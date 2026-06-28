# Parallel Phase 2 Worktrees

This directory contains branch briefs for three independent Lean subprocesses:

- `residual_zmod_checker.md`
- `good_reduction.md`
- `coverage_kernel.md`

Each subprocess should work in its own git worktree.  Do not run several agents
in the same checkout.

## Worktree Setup

Run these commands from the main checkout after the shared prelude commit is
present on `lean-formalization`:

```bash
git worktree add ../Qab_paper_phase2_zmod -b lean-phase2-zmod lean-formalization
git worktree add ../Qab_paper_good_reduction -b lean-good-reduction lean-formalization
git worktree add ../Qab_paper_coverage -b lean-coverage-kernel lean-formalization
```

The review helpers need repository-local secrets in each worktree.  `secrets.env`
is intentionally ignored by git, so copy it explicitly:

```bash
cp secrets.env ../Qab_paper_phase2_zmod/secrets.env
cp secrets.env ../Qab_paper_good_reduction/secrets.env
cp secrets.env ../Qab_paper_coverage/secrets.env
```

Inside each worktree, start by running:

```bash
cd Qab_Lean_v4
lake build
```

If `.lake` must be rebuilt, use the central Mathlib installation noted in the
repository `AGENTS.md`; do not clone a new Mathlib into the project.

## Review Helpers

Launch reviews from the root of the worktree, not from the main checkout, so
the uploaded archive and Claude read tools see the branch-local files.

OpenAI:

```bash
python3 tools/ai_review/openai_review.py \
  --task "<branch-specific review question>"
```

Poll with the response id printed by the helper:

```bash
python3 tools/ai_review/openai_review.py --poll resp_...
```

Claude:

```bash
python3 tools/ai_review/claude_review.py --background \
  --task "<branch-specific review question>"
```

Poll with the receipt path printed by the helper:

```bash
python3 tools/ai_review/claude_review.py --poll \
  artifacts/ai_reviews/<stamp>_claude_receipt.json
```

`artifacts/ai_reviews/` is ignored.  The worker should record response ids,
receipt paths, and any completed review summaries in its final message or in a
small committed note if that is useful.

## Shared Prelude

The common Phase 2 prelude is `Qab.Polynomials.Collision`.  It defines:

- `collisionTriZ`, the scale-normalized collision trinomial;
- `collisionQuotZ`, the forced-factor quotient;
- `collisionTriZ_eq_expand_qNumeratorZ`;
- `collisionQuotZ_closed_form`;
- divisibility of `collisionTriZ` by the forced cyclotomic square and by
  `(X - 1)^2`.

The prelude also exports nonvanishing at `X = 1` for `qPrimZ`, `qOrientZ`, and
`qOrientQ`.  Certificate branches should reuse these facts rather than
reproving polynomial identities ad hoc.

