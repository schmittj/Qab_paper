# Agent Notes

## Project

This repository is a review/proof bundle for the `Q_{a,b}` reciprocal-package
project.  It combines a LaTeX manuscript with deterministic C++/Python
computations and stored verification artifacts.

The manuscript is `Qab.tex`; `Qab.pdf` is the rendered copy.  Current source
code lives in `code/qab12/`, generated proof artifacts live in `data/qab12/`,
and replay logs live in `logs/`.  Those internal directory names are retained
for provenance from the completed computation stage.  Older audited Qab9-Qab11
materials are kept under `archive/`; independent audit reports are in
`docs/audits/`.

## Current Status

The current bundle has eliminated these branches:

- the archived upper range `6,816,242 <= D <= 175,394,637`;
- the lower-box unit-coefficient branch;
- the both-nonunit endpoint-coefficient branch;
- the one-nonunit branch for `D >= 16,584`.

The audit of the previous numbered stage found that the older residual cap
`d <= 224` was not justified for the one-nonunit branch.  The corrected
residual branch uses the safe bound `D <= 16,583`, `|V| = 1`,
`2 <= U <= D`, and `d <= 2601`; it is now handled by
`code/qab12/enumerate_one_nonunit_residual_packages.cpp`,
`code/qab12/pair_one_nonunit_residual.cpp`, and
`code/qab12/verify_one_nonunit_residual.py`.

The residual artifacts are:

- `data/qab12/one_nonunit_residual_packages.csv`
- `data/qab12/one_nonunit_residual_state_pairs.csv`
- `data/qab12/one_nonunit_residual_orientation_pairs.csv`
- `data/qab12/one_nonunit_residual_modular_certificates.csv`
- `data/qab12/one_nonunit_residual_manifest.json`

## Verification Commands

From the repository root:

```bash
make verify-light
make verify-upper
make verify-unit
make one-nonunit-residual THREADS=25
```

The modular and direct irreducibility verifiers require `python-flint`.  The
light verifier rebuilds the main C++ tools and checks the constants,
two-nonunit rows, one-nonunit `D >= 16584` rows, the residual manifest, the
unit-branch manifest, and small regression oracles.

## Lean Formalization

The conditional Lean scaffold lives in `Qab_Lean_v4/`.  Use the central local
Mathlib installation rather than cloning a new copy into this repository.  The
current central dependency is:

```text
/home/jo314/lean/mathlib4-central
```

It is pinned at Mathlib tag `v4.31.0`, commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, with the corresponding
`leanprover/lean4:v4.31.0` toolchain installed through `elan`.
`Qab_Lean_v4/lakefile.lean` points to that package by absolute local path, so
the normal check is:

```bash
cd Qab_Lean_v4
lake build
```

Do not run `lake exe cache get`, `lake update`, or change the Mathlib source
inside `Qab_Lean_v4`; run cache/update commands in `/home/jo314/lean/mathlib4-central`
when the central dependency itself is intentionally refreshed.  If the Lean or
Mathlib version is changed, update `lean-toolchain`, `lakefile.lean`, and
`Qab_Lean_v4/CHANGELOG.md` together.

## AI Review Helpers

To solicit a fresh-perspective review or a targeted question from another model,
use the helpers in `tools/ai_review/` (see `tools/ai_review/README.md`).

For a Claude review, prefer the background + poll flow so you can keep working:

```bash
python3 tools/ai_review/claude_review.py --background \
  --task "<your specific review question>"
# then, until status: done
python3 tools/ai_review/claude_review.py --poll \
  artifacts/ai_reviews/<stamp>_claude_receipt.json
```

The helper drives `claude -p` (read-only Read/Grep/Glob over the repo root),
delivers the prompt via stdin, and self-manages a detached worker — it does not
use the `claude --bg` background-agent daemon.  Use `--dry-run` to preview the
prompt, `--model`/`--effort` to tune cost, and `--cancel <receipt>` to stop a
run.  Review artifacts land in `artifacts/ai_reviews/` (gitignored).

## Development Notes

Prefer preserving the existing proof-artifact style: C++ generators/pair
sieves emit CSV/TXT artifacts under `data/qab12/`, and Python verifiers replay
those artifacts from first principles as much as possible.  Do not remove or
rewrite archived Qab9-Qab11 materials unless specifically asked.
