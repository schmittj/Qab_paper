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
- output token budget: no `max_output_tokens` cap is sent
- web-search return budget: `unlimited`
- file handling: upload the generated zip with purpose `user_data` and mount it
  in the code-interpreter container.  The Responses API does not accept `.zip`
  files as direct context-stuffing `input_file` items, so the model is asked to
  inspect the mounted archive with Python.

Do not add a response-token cap for substantive Lean reviews.  A previous
focused request with `max_output_tokens=12000` ended as `incomplete` before
returning usable guidance.

Useful environment overrides:

```bash
OPENAI_REVIEW_MODEL=gpt-5.5-pro-2026-04-23
OPENAI_REVIEW_EFFORT=xhigh
```

## Claude review

The Claude helper calls the local Claude Code CLI (`claude -p`, non-interactive
print mode) and lets Claude read the repository directly with the read-only
Read/Grep/Glob tools.  The prompt is delivered over **stdin** and the helper
manages its own backgrounding; it does **not** use `claude --bg`.

Preview the prompt and command without calling Claude:

```bash
python3 tools/ai_review/claude_review.py --dry-run \
  --task "Review the Lean scaffold and theorem-pack boundary."
```

Run a synchronous review (blocks, prints, and saves the review):

```bash
python3 tools/ai_review/claude_review.py \
  --task "Review the Lean scaffold and theorem-pack boundary."
```

Run a detached background review and poll for the result:

```bash
# Returns immediately with a receipt path:
python3 tools/ai_review/claude_review.py --background \
  --task "Review the Lean scaffold and theorem-pack boundary."

# Check status / fetch the review when done (re-run until status: done):
python3 tools/ai_review/claude_review.py --poll \
  artifacts/ai_reviews/<stamp>_claude_receipt.json

# Stop a running background review:
python3 tools/ai_review/claude_review.py --cancel \
  artifacts/ai_reviews/<stamp>_claude_receipt.json
```

Defaults:

- model: `opus` (override with `--model` or `CLAUDE_REVIEW_MODEL`);
- effort: `max` (override with `--effort` or `CLAUDE_REVIEW_EFFORT`);
- tools: read-only `Read,Grep,Glob` (`--allow-bash` adds `Bash`);
- output format: `text` (`--output-format json` returns the structured CLI
  result with `result`, `is_error`, and `total_cost_usd`);
- timeout: `3600` s (`--timeout`);
- synchronous output: `artifacts/ai_reviews/<stamp>_claude_review.{txt,json}`;
- background artifacts: `<stamp>_claude_receipt.json` (status + metadata),
  `<stamp>_claude_prompt.txt`, and `<stamp>_claude_review.{txt,json}`.

Optionally pass `--max-budget-usd N` to cap CLI spend.

### Design notes / why not `claude --bg`

Two failure modes in the first iteration are fixed here:

1. **Swallowed prompt.** The CLI's `--tools`/`--add-dir` options are *variadic*
   (`<tools...>`); a positional prompt placed after them is consumed as an extra
   option value, leaving "Input must be provided ...".  This helper always feeds
   the prompt on **stdin**, and keeps `--tools` last in the argv.

2. **Background-agent daemon.** `claude --bg` depends on a background-agent
   daemon whose socket is not guaranteed to be up for a non-interactive caller
   (it returned `ECONNREFUSED` in practice) and provides no built-in way to
   capture the review text.  Instead, `--background` forks a self-managed,
   fully detached worker (the same script, `start_new_session=True`) that runs
   the ordinary synchronous review, writes the review file, and records progress
   in the receipt JSON that `--poll` reads back.  No daemon involved.

Set `CLAUDE_REVIEW_MODEL` to a full installed model name if the local CLI
requires one, for example a future Opus snapshot.
