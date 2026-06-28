#!/usr/bin/env python3
"""Solicit a read-only Claude Code review for the Qab Lean formalization.

This helper lets the lead author (Codex) ask Claude for a fresh-perspective
review or a targeted question about the conditional Lean formalization.  It
drives the local ``claude`` CLI in non-interactive print mode (``claude -p``)
and lets Claude read the repository directly with the read-only Read/Grep/Glob
tools.

Design notes (why it looks the way it does)
-------------------------------------------
* The prompt is delivered over **stdin**, never as a positional argument.  The
  ``claude`` CLI exposes ``--tools`` and ``--add-dir`` as *variadic* options
  (``<tools...>``); a positional prompt placed after them is silently swallowed
  as an extra option value, leaving the CLI with no prompt ("Input must be
  provided ...").  Feeding the prompt on stdin sidesteps that entirely and also
  handles arbitrarily large prompts and shell-special characters.

* Background mode uses a **self-managed detached worker** (this same script
  re-invoked with ``--worker-receipt``), not ``claude --bg``.  The CLI's
  background-agent daemon is not guaranteed to be running for a non-interactive
  caller and its socket returned ``ECONNREFUSED`` in practice; it also offers no
  built-in way to capture the review *text* to a file.  The detached worker has
  no such dependency: it runs the ordinary synchronous review, writes the review
  to a file, and records progress in a receipt JSON that ``--poll`` reads back.

Usage
-----
Preview the prompt/command without calling Claude::

    python3 tools/ai_review/claude_review.py --dry-run --task "..."

Synchronous review (blocks, prints, and saves the review)::

    python3 tools/ai_review/claude_review.py --task "Review the Phase-1 layer."

Detached background review + poll (no Claude daemon involved)::

    python3 tools/ai_review/claude_review.py --background --task "..."
    python3 tools/ai_review/claude_review.py --poll artifacts/ai_reviews/<stamp>_claude_receipt.json

Cancel a running background review::

    python3 tools/ai_review/claude_review.py --cancel artifacts/ai_reviews/<stamp>_claude_receipt.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import time

from openai_review import ARTIFACT_DIR, ROOT, git_value, iter_bundle_files


DEFAULT_MODEL = os.environ.get("CLAUDE_REVIEW_MODEL", "opus")
DEFAULT_EFFORT = os.environ.get("CLAUDE_REVIEW_EFFORT", "max")
DEFAULT_TOOLS = "Read,Grep,Glob"
# Generous ceiling for a max-effort review; overridable with --timeout.
DEFAULT_TIMEOUT_S = 3600
# Cap on how many focus-file paths to inline into the prompt.
MAX_FOCUS_FILES = 160
SCRIPT_PATH = pathlib.Path(__file__).resolve()
try:
    SCRIPT_DISPLAY = SCRIPT_PATH.relative_to(ROOT).as_posix()
except ValueError:
    SCRIPT_DISPLAY = str(SCRIPT_PATH)

DEFAULT_PROMPT = """\
Please perform an in-depth, read-only review of this repository's conditional
Lean formalization work.

Focus on:

1. Lean theorem-pack boundary quality and assumption isolation.
2. Whether Qab_Lean_v4/CoreProof.lean is a clean assembly proof.
3. Whether broad axioms remain isolated in Qab/Packs/BroadAxioms.lean.
4. Phase-1 risks for qPrimZ, qOrientZ, qPackageProdZ, PackageShare, and
   OrientationShare.
5. Concrete next steps and likely Mathlib APIs to inspect.

Do not edit files.  Give file-specific findings (file:line where possible) and
concrete recommendations.
"""


# --------------------------------------------------------------------------- #
# Prompt + command construction
# --------------------------------------------------------------------------- #
def focus_file_list() -> list[str]:
    """Curated, relative paths Claude should prioritise reading."""
    try:
        files = iter_bundle_files(include_data_csv=False)
    except Exception:
        return []
    return [path.relative_to(ROOT).as_posix() for path in files]


def build_prompt(args: argparse.Namespace) -> str:
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else DEFAULT_PROMPT
    if args.task:
        prompt += "\n\nSpecific task/request:\n" + args.task.strip() + "\n"

    focus = focus_file_list()
    if focus:
        shown = focus[:MAX_FOCUS_FILES]
        listing = "\n".join(f"- {rel}" for rel in shown)
        if len(focus) > len(shown):
            listing += f"\n- ... ({len(focus) - len(shown)} more)"
        prompt += (
            "\n\nRelevant files (read these directly with Read/Grep/Glob; you have "
            "read-only access to the repository root):\n" + listing + "\n"
        )

    prompt += (
        "\n\nContext:\n"
        f"- Repository root: {ROOT}\n"
        f"- Current branch: {git_value('branch', '--show-current')}\n"
        f"- Current commit: {git_value('rev-parse', 'HEAD')}\n"
        "You may inspect files directly under the repository root.\n"
    )
    return prompt


def build_command(args: argparse.Namespace) -> list[str]:
    """Build the ``claude -p`` argv.  The prompt is supplied via stdin."""
    tools = args.tools
    if args.allow_bash and "Bash" not in tools.split(","):
        tools = tools + ",Bash"

    command = [
        "claude",
        "-p",
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--add-dir",
        str(ROOT),
        "--output-format",
        args.output_format,
    ]
    if args.max_budget_usd:
        command.extend(["--max-budget-usd", args.max_budget_usd])
    # --tools is variadic and MUST stay last so it cannot swallow another value.
    # The prompt is delivered via stdin, never as a positional argument.
    command.extend(["--tools", tools])
    return command


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def review_suffix(output_format: str) -> str:
    return "json" if output_format == "json" else "txt"


def parse_json_result(raw: str) -> dict | None:
    """Best-effort parse of a ``--output-format json`` result object."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # stream-json or trailing noise: try the last line.
        try:
            return json.loads(raw.splitlines()[-1])
        except Exception:
            return None


def summarise(output_format: str, raw: str) -> dict:
    """Extract a small status summary from a completed review's stdout."""
    summary: dict = {"is_error": None, "cost_usd": None, "permission_denials": None}
    if output_format != "json":
        return summary
    data = parse_json_result(raw)
    if not isinstance(data, dict):
        return summary
    summary["is_error"] = data.get("is_error")
    summary["cost_usd"] = data.get("total_cost_usd")
    denials = data.get("permission_denials")
    if isinstance(denials, list):
        summary["permission_denials"] = len(denials)
    return summary


def write_receipt(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_receipt(path: pathlib.Path, **changes) -> dict:
    """Read-modify-write a receipt, preserving fields set by another process."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data.update(changes)
    write_receipt(path, data)
    return data


# --------------------------------------------------------------------------- #
# Core runner (shared by synchronous and worker paths)
# --------------------------------------------------------------------------- #
def run_claude(command: list[str], prompt: str, timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return 124, partial + f"\n[claude_review] timed out after {timeout}s\n"


# --------------------------------------------------------------------------- #
# Modes
# --------------------------------------------------------------------------- #
def run_synchronous(args: argparse.Namespace, command: list[str], prompt: str) -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    review_path = ARTIFACT_DIR / f"{stamp}_claude_review.{review_suffix(args.output_format)}"

    print(f"model: {args.model}  effort: {args.effort}  tools: {command[command.index('--tools') + 1]}")
    print(f"review_file: {review_path}")
    print("running claude (synchronous) ...", flush=True)

    returncode, output = run_claude(command, prompt, args.timeout)
    review_path.write_text(output, encoding="utf-8")

    summary = summarise(args.output_format, output)
    if args.output_format == "json":
        data = parse_json_result(output)
        result_text = data.get("result") if isinstance(data, dict) else None
        if result_text:
            print("\n--- review ---\n")
            print(result_text)
    else:
        sys.stdout.write(output if output.endswith("\n") else output + "\n")

    print(f"\nclaude_exit_code: {returncode}")
    if summary["is_error"] is not None:
        print(f"is_error: {summary['is_error']}")
    if summary["cost_usd"] is not None:
        print(f"cost_usd: {summary['cost_usd']}")
    if summary["permission_denials"]:
        print(f"permission_denials: {summary['permission_denials']} (some tools were blocked)")
    print(f"review_file: {review_path}")
    return returncode


def run_background(args: argparse.Namespace, command: list[str], prompt: str) -> int:
    """Fork a detached worker that runs the review and updates a receipt JSON."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    receipt_path = ARTIFACT_DIR / f"{stamp}_claude_receipt.json"
    prompt_path = ARTIFACT_DIR / f"{stamp}_claude_prompt.txt"
    review_path = ARTIFACT_DIR / f"{stamp}_claude_review.{review_suffix(args.output_format)}"

    prompt_path.write_text(prompt, encoding="utf-8")
    write_receipt(
        receipt_path,
        {
            "kind": "claude_review_receipt",
            "status": "starting",
            "created_at": now_iso(),
            "started_at": None,
            "finished_at": None,
            "worker_pid": None,
            "exit_code": None,
            "is_error": None,
            "cost_usd": None,
            "model": args.model,
            "effort": args.effort,
            "output_format": args.output_format,
            "timeout_s": args.timeout,
            "command": command,
            "prompt_file": str(prompt_path),
            "review_file": str(review_path),
            "git_branch": git_value("branch", "--show-current"),
            "git_commit": git_value("rev-parse", "HEAD"),
            "poll_cmd": f"python3 {SCRIPT_DISPLAY} --poll {receipt_path}",
            "cancel_cmd": f"python3 {SCRIPT_DISPLAY} --cancel {receipt_path}",
        },
    )

    # Detach: own session/process group, no controlling terminal, no inherited fds.
    subprocess.Popen(
        [sys.executable, str(pathlib.Path(__file__).resolve()), "--worker-receipt", str(receipt_path)],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )

    print(f"status: launched detached worker (no claude background daemon used)")
    print(f"receipt: {receipt_path}")
    print(f"review_file (when done): {review_path}")
    print(f"poll:   python3 {SCRIPT_DISPLAY} --poll {receipt_path}")
    print(f"cancel: python3 {SCRIPT_DISPLAY} --cancel {receipt_path}")
    return 0


def run_worker(receipt_path: pathlib.Path) -> int:
    """Detached worker: run the review synchronously and record results."""
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception:
        return 1

    command = receipt["command"]
    prompt = pathlib.Path(receipt["prompt_file"]).read_text(encoding="utf-8")
    review_path = pathlib.Path(receipt["review_file"])
    output_format = receipt.get("output_format", "text")
    timeout = int(receipt.get("timeout_s", DEFAULT_TIMEOUT_S))

    update_receipt(receipt_path, status="running", started_at=now_iso(), worker_pid=os.getpid())

    returncode, output = run_claude(command, prompt, timeout)
    review_path.write_text(output, encoding="utf-8")

    summary = summarise(output_format, output)
    status = "done" if returncode == 0 and summary["is_error"] in (None, False) else "failed"
    update_receipt(
        receipt_path,
        status=status,
        finished_at=now_iso(),
        exit_code=returncode,
        is_error=summary["is_error"],
        cost_usd=summary["cost_usd"],
        permission_denials=summary["permission_denials"],
    )
    return returncode


def poll(receipt_path: pathlib.Path) -> int:
    if not receipt_path.exists():
        raise SystemExit(f"receipt not found: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    status = receipt.get("status", "unknown")
    pid = receipt.get("worker_pid")

    # If the receipt still says running but the worker is gone, report a crash.
    if status in {"starting", "running"} and pid and not _pid_alive(pid):
        # The worker may have exited just before its final receipt write became
        # visible to this process.  Re-read once, then only declare a crash if
        # the receipt is stale.  PID checks can be unreliable across caller
        # contexts, so freshness is the safer signal.
        time.sleep(0.25)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        status = receipt.get("status", "unknown")
        pid = receipt.get("worker_pid")
        if (
            status in {"starting", "running"}
            and pid
            and not _pid_alive(pid)
            and _receipt_is_stale(receipt)
        ):
            status = "crashed"

    print(f"status: {status}")
    print(f"model: {receipt.get('model')}  effort: {receipt.get('effort')}")
    if receipt.get("started_at"):
        print(f"started_at: {receipt['started_at']}")
    if receipt.get("finished_at"):
        print(f"finished_at: {receipt['finished_at']}")
    if receipt.get("exit_code") is not None:
        print(f"exit_code: {receipt['exit_code']}")
    if receipt.get("cost_usd") is not None:
        print(f"cost_usd: {receipt['cost_usd']}")
    if receipt.get("permission_denials"):
        print(f"permission_denials: {receipt['permission_denials']} (some tools were blocked)")

    review_path = pathlib.Path(receipt.get("review_file", ""))
    if status in {"done", "failed", "crashed"} and review_path.exists():
        raw = review_path.read_text(encoding="utf-8")
        if receipt.get("output_format") == "json":
            data = parse_json_result(raw)
            raw = data.get("result", raw) if isinstance(data, dict) else raw
        print(f"review_file: {review_path}")
        print("\n--- review ---\n")
        print(raw)
    else:
        print(f"review_file (pending): {review_path}")
        print("not finished yet; poll again later.")
    return 0


def cancel(receipt_path: pathlib.Path) -> int:
    if not receipt_path.exists():
        raise SystemExit(f"receipt not found: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    pid = receipt.get("worker_pid")
    if not pid:
        print("no worker_pid recorded; nothing to cancel (worker may not have started)")
        return 0
    try:
        # Worker is a session leader, so its pgid == pid; kill the whole group
        # to take the claude child down with it.
        os.killpg(pid, signal.SIGTERM)
        print(f"sent SIGTERM to worker process group {pid}")
    except ProcessLookupError:
        print(f"worker {pid} is not running (already finished?)")
    update_receipt(receipt_path, status="cancelled", finished_at=now_iso())
    return 0


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _receipt_is_stale(receipt: dict) -> bool:
    timestamp = receipt.get("started_at") or receipt.get("created_at")
    if not timestamp:
        return False
    try:
        started = dt.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    except (TypeError, ValueError):
        return False
    timeout = int(receipt.get("timeout_s", DEFAULT_TIMEOUT_S))
    return time.time() - started.timestamp() > timeout + 30


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print the resolved command + prompt and exit")
    parser.add_argument("--task", help="specific review task/question appended to the prompt")
    parser.add_argument("--prompt-file", type=pathlib.Path, help="custom prompt file (replaces the default prompt)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"claude model (default: {DEFAULT_MODEL})")
    parser.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--tools", default=DEFAULT_TOOLS, help=f"allowed tools (default: {DEFAULT_TOOLS})")
    parser.add_argument("--allow-bash", action="store_true", help="add Bash to the tool set")
    parser.add_argument("--output-format", default="text", choices=["text", "json"])
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S, help="seconds before the review is aborted")
    parser.add_argument("--max-budget-usd", help="optional Claude CLI spend cap (passed through to --max-budget-usd)")
    parser.add_argument("--background", action="store_true", help="run detached; poll the receipt for the result")
    parser.add_argument("--poll", metavar="RECEIPT_JSON", type=pathlib.Path, help="print the status/result of a receipt")
    parser.add_argument("--cancel", metavar="RECEIPT_JSON", type=pathlib.Path, help="cancel a running background review")
    # Internal: detached worker entry point.
    parser.add_argument("--worker-receipt", metavar="RECEIPT_JSON", type=pathlib.Path, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.worker_receipt:
        return run_worker(args.worker_receipt)
    if args.poll:
        return poll(args.poll)
    if args.cancel:
        return cancel(args.cancel)

    if not shutil.which("claude"):
        raise SystemExit("claude CLI was not found on PATH")

    prompt = build_prompt(args)
    command = build_command(args)

    if args.dry_run:
        tools_val = command[command.index("--tools") + 1]
        print("command:", " ".join(command), "  # prompt delivered via stdin")
        print(f"model: {args.model}  effort: {args.effort}  tools: {tools_val}  output: {args.output_format}")
        print(f"prompt_chars: {len(prompt)}")
        print("\n--- prompt ---\n")
        print(prompt)
        return 0

    if args.background:
        return run_background(args, command, prompt)
    return run_synchronous(args, command, prompt)


if __name__ == "__main__":
    raise SystemExit(main())
