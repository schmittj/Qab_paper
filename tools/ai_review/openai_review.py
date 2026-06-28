#!/usr/bin/env python3
"""Submit Qab Lean review bundles to the OpenAI Responses API.

The script intentionally avoids an SDK dependency.  It builds a zip containing
the Lean scaffold, blueprint docs, manuscript TeX/PDF, and deterministic
verification source code; uploads that zip with purpose ``user_data``; mounts
it in a code-interpreter container; and starts a background Responses request
with web search and code interpreter.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import mimetypes
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from dataclasses import dataclass
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts" / "ai_reviews"
OPENAI_BASE_URL = "https://api.openai.com/v1"

DEFAULT_MODEL = "gpt-5.5-pro-2026-04-23"
DEFAULT_EFFORT = "xhigh"

DEFAULT_FILE_GLOBS = [
    "AGENTS.md",
    "README.md",
    "MANIFEST.md",
    "PUBLICATION_CHECKLIST.md",
    "Makefile",
    "Qab.tex",
    "Qab.pdf",
    "requirements-optional.txt",
    "Qab_Lean_v4/**/*.lean",
    "Qab_Lean_v4/lakefile.lean",
    "Qab_Lean_v4/lean-toolchain",
    "Qab_Lean_v4/lake-manifest.json",
    "Qab_Lean_v4/README.md",
    "Qab_Lean_v4/CODEX_START_HERE.md",
    "Qab_Lean_v4/CHANGELOG.md",
    "Qab_Lean_v4/docs/**/*.md",
    "Qab_Lean_v4/docs/**/*.tex",
    "Qab_Lean_v4/docs/**/*.pdf",
    "code/qab12/**/*",
    "data/qab12/*manifest*.json",
    "docs/audits/**/*.md",
]

EXCLUDED_PARTS = {
    ".git",
    ".lake",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".claude",
    ".codex",
    ".agents",
}

EXCLUDED_GLOBS = [
    "secrets.env",
    "artifacts/ai_reviews/**",
    "*.olean",
    "*.ilean",
    "*.c",
    "*.o",
    "*.out",
]

DEFAULT_PROMPT = """\
You are reviewing a conditional Lean formalization for the Q_{a,b}
reciprocal-package project.

Use the attached zip as the source of truth.  It contains the Lean scaffold,
the v4 roadmap, the mathematical core TeX/PDF, the original manuscript TeX,
and the deterministic verification source code/manifests.

Please produce an engineering-grade review focused on:

1. Lean code quality and theorem-pack boundary hygiene.
2. Whether the current scaffold keeps broad assumptions isolated.
3. The safest next steps for Phase 1 polynomial semantics.
4. Places where definitions risk bloat, circular dependencies, or premature
   commitments.
5. Concrete Lean/Mathlib implementation guidance, with file-specific
   references where possible.

Do not propose replacing the theorem packs by unverified axioms outside
Qab/Packs/BroadAxioms.lean.  Do not suggest defining FromShare or PackageShare
as True.  Prefer narrow, auditable changes.
"""


@dataclass(frozen=True)
class Bundle:
    path: pathlib.Path
    file_count: int
    byte_count: int


def load_dotenv(path: pathlib.Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def git_value(*args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return proc.stdout.strip()
    except Exception:
        return "unknown"


def should_exclude(path: pathlib.Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts):
        return True
    return any(fnmatch.fnmatch(rel, pattern) for pattern in EXCLUDED_GLOBS)


def iter_bundle_files(include_data_csv: bool) -> list[pathlib.Path]:
    patterns = list(DEFAULT_FILE_GLOBS)
    if include_data_csv:
        patterns.append("data/qab12/**/*.csv")
        patterns.append("data/qab12/**/*.txt")

    found: dict[str, pathlib.Path] = {}
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file() and not should_exclude(path):
                found[path.relative_to(ROOT).as_posix()] = path
    return [found[key] for key in sorted(found)]


def build_bundle(include_data_csv: bool = False) -> Bundle:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    bundle_path = ARTIFACT_DIR / f"qab_review_bundle_{stamp}.zip"
    files = iter_bundle_files(include_data_csv)

    manifest = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_status_short": git_value("status", "--short"),
        "include_data_csv": include_data_csv,
        "file_count": len(files),
        "files": [path.relative_to(ROOT).as_posix() for path in files],
    }

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("AI_REVIEW_BUNDLE_MANIFEST.json", json.dumps(manifest, indent=2))
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())

    return Bundle(bundle_path, len(files), bundle_path.stat().st_size)


def read_prompt(path: pathlib.Path | None, task: str | None) -> str:
    prompt = path.read_text(encoding="utf-8") if path else DEFAULT_PROMPT
    if task:
        prompt += "\n\nSpecific task/request:\n" + task.strip() + "\n"
    return prompt


def require_api_key() -> str:
    load_dotenv(ROOT / "secrets.env")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set and was not found in secrets.env")
    return api_key


def openai_json_request(api_key: str, method: str, path: str, payload: Any | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_BASE_URL + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    return parse_response(request)


def multipart_request(api_key: str, path: str, fields: dict[str, str], files: dict[str, pathlib.Path]) -> Any:
    boundary = "----qab-review-" + uuid.uuid4().hex
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode(),
                b"\r\n",
            ]
        )

    for name, file_path in files.items():
        mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{name}"; '
                    f'filename="{file_path.name}"\r\n'
                ).encode(),
                f"Content-Type: {mime_type}\r\n\r\n".encode(),
                file_path.read_bytes(),
                b"\r\n",
            ]
        )

    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    request = urllib.request.Request(
        OPENAI_BASE_URL + path,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    return parse_response(request)


def parse_response(request: urllib.request.Request) -> Any:
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI API error {exc.code}: {body}") from exc
    return json.loads(raw)


def response_output_text(response: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in response.get("output", []) or []:
        if item.get("type") != "message":
            continue
        for part in item.get("content", []) or []:
            if part.get("type") == "output_text" and part.get("text"):
                chunks.append(part["text"])
    return "\n".join(chunks)


def write_json(path: pathlib.Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def submit(args: argparse.Namespace) -> int:
    prompt = read_prompt(args.prompt_file, args.task)
    bundle = build_bundle(include_data_csv=args.include_data_csv)
    print(f"bundle: {bundle.path}")
    print(f"bundle_files: {bundle.file_count}")
    print(f"bundle_bytes: {bundle.byte_count}")

    if args.dry_run:
        return 0
    if args.no_code_interpreter:
        raise SystemExit(
            "--no-code-interpreter is incompatible with zip review bundles; "
            "the Responses API does not accept .zip as a direct input_file."
        )

    api_key = require_api_key()
    uploaded = multipart_request(
        api_key,
        "/files",
        fields={"purpose": "user_data"},
        files={"file": bundle.path},
    )
    file_id = uploaded["id"]

    tools: list[dict[str, Any]] = []
    include: list[str] = []
    if not args.no_web_search:
        web_tool: dict[str, Any] = {
            "type": "web_search",
            "search_context_size": args.search_context_size,
            "return_token_budget": "unlimited",
        }
        tools.append(web_tool)
        include.append("web_search_call.action.sources")
    if not args.no_code_interpreter:
        tools.append(
            {
                "type": "code_interpreter",
                "container": {
                    "type": "auto",
                    "memory_limit": args.container_memory,
                    "file_ids": [file_id],
                },
            }
        )
        include.append("code_interpreter_call.outputs")

    mounted_prompt = (
        f"The review bundle `{bundle.path.name}` has been uploaded as `{file_id}` "
        "and mounted in the code-interpreter container.  Use Python's zipfile "
        "module to inspect the archive before reviewing the Lean/materials.\n\n"
        + prompt
    )

    payload: dict[str, Any] = {
        "model": args.model,
        "background": not args.foreground,
        "reasoning": {"effort": args.reasoning_effort},
        "prompt_cache_retention": "24h",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": mounted_prompt},
                ],
            }
        ],
        "metadata": {
            "project": "Qab_paper",
            "kind": "lean_formalization_review",
            "git_commit": git_value("rev-parse", "HEAD")[:40],
        },
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    if include:
        payload["include"] = include
    response = openai_json_request(api_key, "POST", "/responses", payload)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    result_path = ARTIFACT_DIR / f"{stamp}_openai_response.json"
    write_json(
        result_path,
        {
            "bundle": str(bundle.path.relative_to(ROOT)),
            "uploaded_file": uploaded,
            "request": {k: v for k, v in payload.items() if k != "input"},
            "response": response,
        },
    )
    print(f"file_id: {file_id}")
    print(f"response_id: {response.get('id')}")
    print(f"status: {response.get('status')}")
    print(f"result_json: {result_path}")
    text = response_output_text(response)
    if text:
        print("\n--- output_text ---\n")
        print(text)
    return 0


def poll(response_id: str) -> int:
    api_key = require_api_key()
    response = openai_json_request(api_key, "GET", f"/responses/{response_id}")
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    result_path = ARTIFACT_DIR / f"{response_id}_poll.json"
    write_json(result_path, response)
    print(f"response_id: {response.get('id')}")
    print(f"status: {response.get('status')}")
    print(f"result_json: {result_path}")
    text = response_output_text(response)
    if text:
        print("\n--- output_text ---\n")
        print(text)
    return 0


def cancel(response_id: str) -> int:
    api_key = require_api_key()
    response = openai_json_request(api_key, "POST", f"/responses/{response_id}/cancel", {})
    print(json.dumps(response, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="build the review bundle but do not call the API")
    parser.add_argument("--task", help="specific review task to append to the default prompt")
    parser.add_argument("--prompt-file", type=pathlib.Path, help="custom prompt file")
    parser.add_argument("--include-data-csv", action="store_true", help="include data/qab12 CSV/TXT artifacts")
    parser.add_argument("--model", default=os.environ.get("OPENAI_REVIEW_MODEL", DEFAULT_MODEL))
    parser.add_argument("--reasoning-effort", default=os.environ.get("OPENAI_REVIEW_EFFORT", DEFAULT_EFFORT))
    parser.add_argument("--foreground", action="store_true", help="set background=false")
    parser.add_argument("--no-web-search", action="store_true")
    parser.add_argument("--no-code-interpreter", action="store_true")
    parser.add_argument(
        "--unlimited-web",
        action="store_true",
        help="deprecated no-op; web_search return_token_budget is always unlimited",
    )
    parser.add_argument("--search-context-size", default="high", choices=["low", "medium", "high"])
    parser.add_argument("--container-memory", default="4g", choices=["1g", "4g", "16g", "64g"])
    parser.add_argument("--poll", metavar="RESPONSE_ID", help="retrieve an existing response")
    parser.add_argument("--cancel", metavar="RESPONSE_ID", help="cancel an existing background response")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.poll:
        return poll(args.poll)
    if args.cancel:
        return cancel(args.cancel)
    return submit(args)


if __name__ == "__main__":
    raise SystemExit(main())
