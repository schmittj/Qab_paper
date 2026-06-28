#!/usr/bin/env python3
"""Run a read-only Claude Code review for the Qab Lean formalization."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

from openai_review import ARTIFACT_DIR, ROOT, build_bundle, git_value


DEFAULT_MODEL = os.environ.get("CLAUDE_REVIEW_MODEL", "opus")

DEFAULT_PROMPT = """\
Please perform an in-depth read-only review of this repository's conditional
Lean formalization work.

Focus on:

1. Lean theorem-pack boundary quality and assumption isolation.
2. Whether Qab_Lean_v4/CoreProof.lean is a clean assembly proof.
3. Whether broad axioms remain isolated in Qab/Packs/BroadAxioms.lean.
4. Phase-1 risks for qPrimZ, qOrientZ, qPackageProdZ, PackageShare, and
   OrientationShare.
5. Concrete next steps and likely Mathlib APIs to inspect.

Do not edit files.  Give file-specific findings and recommendations.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show the command and create the bundle only")
    parser.add_argument("--task", help="specific review task to append to the prompt")
    parser.add_argument("--prompt-file", type=pathlib.Path, help="custom prompt file")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-budget-usd", help="optional Claude CLI budget cap")
    parser.add_argument("--output-format", default="text", choices=["text", "json", "stream-json"])
    parser.add_argument("--allow-bash", action="store_true", help="allow Bash in addition to Read/Grep/Glob")
    parser.add_argument("--background", action="store_true", help="launch a Claude Code background agent")
    parser.add_argument("--name", help="display name for the Claude session/background agent")
    return parser.parse_args()


def read_prompt(args: argparse.Namespace, bundle_path: pathlib.Path) -> str:
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else DEFAULT_PROMPT
    if args.task:
        prompt += "\n\nSpecific task/request:\n" + args.task.strip() + "\n"
    prompt += (
        "\n\nContext:\n"
        f"- Repository root: {ROOT}\n"
        f"- Current branch: {git_value('branch', '--show-current')}\n"
        f"- Current commit: {git_value('rev-parse', 'HEAD')}\n"
        f"- Review bundle: {bundle_path}\n"
        "You may inspect files directly under the repository root.\n"
    )
    return prompt


def main() -> int:
    args = parse_args()
    if not shutil.which("claude"):
        raise SystemExit("claude CLI was not found on PATH")

    bundle = build_bundle(include_data_csv=False)
    prompt = read_prompt(args, bundle.path)
    tools = "Read,Grep,Glob"
    if args.allow_bash:
        tools += ",Bash"

    name = args.name or f"qab-lean-review-{time.strftime('%Y%m%d-%H%M%S')}"
    command = ["claude"]
    if args.background:
        command.extend(["--bg", "--name", name])
    else:
        command.append("-p")
    command.extend(
        [
            "--effort",
            "max",
            "--model",
            args.model,
            "--add-dir",
            str(ROOT),
            "--tools",
            tools,
        ]
    )
    if not args.background:
        command.extend(["--output-format", args.output_format])
    if args.max_budget_usd:
        command.extend(["--max-budget-usd", args.max_budget_usd])
    command.append(prompt)

    print("bundle:", bundle.path)
    print("bundle_files:", bundle.file_count)
    print("bundle_bytes:", bundle.byte_count)
    print("command:", " ".join(command[:-1] + ["<prompt>"]))
    if args.dry_run:
        return 0

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    suffix = "claude_background.json" if args.background else "claude_review.txt"
    out_path = ARTIFACT_DIR / f"{stamp}_{suffix}"
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if args.background:
        payload = {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "name": name,
            "exit_code": proc.returncode,
            "bundle": str(bundle.path),
            "command": command[:-1] + ["<prompt>"],
            "stdout": proc.stdout,
            "next_steps": ["claude agents"],
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        out_path.write_text(proc.stdout, encoding="utf-8")
    sys.stdout.write(proc.stdout)
    print(f"\nclaude_exit_code: {proc.returncode}")
    print(f"claude_output: {out_path}")
    if args.background:
        print("check_status: claude agents")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
