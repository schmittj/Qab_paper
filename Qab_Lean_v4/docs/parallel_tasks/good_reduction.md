# Branch Brief: Good-Reduction Lemma

Suggested worktree:

```bash
git worktree add ../Qab_paper_good_reduction -b lean-good-reduction lean-formalization
cp secrets.env ../Qab_paper_good_reduction/secrets.env
```

Start in `../Qab_paper_good_reduction`.

## Slash Goal

```text
/goal In branch lean-good-reduction, formalize a reusable good-reduction lemma for Phase 2 certificates: if h in Z[x] is primitive and nonconstant, h divides F and G over Q[x], and p is a good prime satisfying the necessary content/leading-coefficient/nonvanishing hypotheses, then the reduction of h modulo p divides the modular gcd target for reductions of F and G.  Keep the theorem Mathlib-shaped and reusable by the residual ZMod 1009 branch, document the exact hypotheses chosen, and avoid project-specific data.  Before declaring ready, commit the branch, push it, and launch both review helpers from this worktree asking OpenAI and Claude to audit the statement, hypotheses, and proof usefulness for the residual certificates; record the response id / Claude receipt path for later inspection.  You may interrupt and mark the goal blocked if you encounter a serious mathematical or Mathlib API issue that needs external input to resolve, such as uncertainty about the right primitive/content hypothesis, denominator-clearing contract, or an unavoidable mismatch between rational divisibility and modular reduction.
```

## Scope

This branch should be independent of residual CSV data.  Its output is a
general theorem and a short explanation of how certificate checkers should
instantiate it.

Primary files to inspect:

- `Qab_Lean_v4/Qab/Polynomials/Primitive.lean`
- `Qab_Lean_v4/Qab/Polynomials/Orientation.lean`
- `Qab_Lean_v4/Qab/Polynomials/Collision.lean`
- `Qab_Lean_v4/Qab/Certificates/Interfaces.lean`
- Mathlib polynomial content, primitive, map, and gcd APIs.

Likely new file:

- `Qab_Lean_v4/Qab/Certificates/GoodReduction.lean`

## Suggested Shape

The exact theorem statement is part of the task.  A useful end state may split
the work into smaller lemmas:

- clearing rational divisibility to an integral divisibility statement under
  primitive/content hypotheses;
- reduction modulo `p` preserving nonzero positive degree under leading
  coefficient and content conditions;
- if a reduced nonconstant factor divides both reduced polynomials, then the
  modular gcd has degree at least that factor degree;
- the contrapositive form used by certificates: an exact modular gcd degree
  bound excludes a rational common noncyclotomic factor after forced factors are
  accounted for.

It is acceptable to land a narrower but compiled theorem if the final general
statement proves too large, provided the limitation is documented precisely.

## Acceptance Criteria

- The new module builds directly and under full `lake build`.
- The theorem hypotheses are explicit enough for `ZMod 1009` certificates:
  prime/nonzero characteristic, content or primitive hypotheses, leading
  coefficient not vanishing mod `p`, and positive-degree preservation.
- The statement is reusable and does not mention residual row ids or artifact
  filenames.
- Any remaining gap is recorded as a concrete theorem contract rather than a
  vague TODO.
- OpenAI and Claude review processes are launched before the branch is marked
  ready.

## Review Questions

OpenAI / Claude should be asked to review:

- whether the good-prime hypotheses are sufficient and not bloated;
- whether the rational-to-integral divisibility bridge is sound;
- how Track 1 should instantiate the theorem for collision trinomials;
- whether the proof should use Mathlib gcd directly or a degree-lower-bound
  formulation for modular certificates.

