# AI Review Helpers

These scripts package the current Lean formalization context and send it to an
external review model.  They are intended for occasional high-level review or
when the formalization gets stuck, not for every small edit.

## OpenAI Responses review

The OpenAI helper uses only the Python standard library.  It reads
`OPENAI_API_KEY` from the environment, or from the repository-local
`secrets.env` file if the variable is not already set.

Dry-run bundle creation:

```bash
python3 tools/ai_review/openai_review.py --dry-run
```

Submit a background review request:

```bash
python3 tools/ai_review/openai_review.py \
  --task "Review the Phase-0 Lean scaffold and identify the next safest Phase-1 definitions."
```

Poll a response:

```bash
python3 tools/ai_review/openai_review.py --poll resp_...
```

Defaults:

- model: `gpt-5.5-pro-2026-04-23`
- reasoning effort: `xhigh`
- `background: true`
- tools: `web_search` and `code_interpreter`
- file handling: upload the generated zip with purpose `user_data` and mount it
  in the code-interpreter container.  The Responses API does not accept `.zip`
  files as direct context-stuffing `input_file` items, so the model is asked to
  inspect the mounted archive with Python.

Useful environment overrides:

```bash
OPENAI_REVIEW_MODEL=gpt-5.5-pro-2026-04-23
OPENAI_REVIEW_EFFORT=xhigh
```

## Claude review

The Claude helper calls the local Claude Code CLI in non-interactive print mode
with max effort.

```bash
python3 tools/ai_review/claude_review.py --dry-run
python3 tools/ai_review/claude_review.py \
  --task "Review the Lean scaffold and theorem-pack boundary."
```

Launch as a Claude Code background agent and continue other work:

```bash
python3 tools/ai_review/claude_review.py --background \
  --task "Review the Lean scaffold and theorem-pack boundary."

claude agents
```

Defaults:

- model: `opus` unless `CLAUDE_REVIEW_MODEL` is set;
- effort: `max`;
- permissions: read-only tool set (`Read,Grep,Glob`);
- output: `artifacts/ai_reviews/*_claude_review.txt`.
- background launch receipts: `artifacts/ai_reviews/*_claude_background.json`.

Set `CLAUDE_REVIEW_MODEL` to a full installed model name if the local CLI
requires one, for example a future Opus snapshot.
