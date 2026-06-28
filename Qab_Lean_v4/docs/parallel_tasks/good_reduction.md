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

## Implemented Contract

This branch records the reusable lemmas in
`Qab.Certificates.GoodReduction`.  The theorem family is deliberately
project-data-free: it only mentions `h F G : Polynomial Int`, rational
divisibility after mapping to `Rat[X]`, and reductions to an arbitrary field or
to `ZMod p`.

Chosen hypotheses:

- `h.IsPrimitive`, plus `0 < h.natDegree` for the positive-degree
  certificate corollary.
- `h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat)` and the same for
  `G`.
- No primitivity or content hypothesis on `F` or `G`; the denominator-clearing
  lemma passes through `Polynomial.primPart`, so target content is handled
  internally.
- For degree bounds after reduction, `(Int.castRingHom K) h.leadingCoeff ≠ 0`
  (or `(h.leadingCoeff : ZMod p) ≠ 0`) preserves the degree of `h`.
- For degree bounds, at least one reduced target is nonzero:
  `reduceInt K F ≠ 0 ∨ reduceInt K G ≠ 0`.  Certificate checkers may prove
  this from content or leading-coefficient checks, but the lemma takes the
  Mathlib-shaped nonvanishing condition directly.

The main divisibility lemma has no good-prime hypothesis: if a bad prime
collapses the factor, divisibility of the collapsed reduction still holds.  The
good-prime assumptions enter exactly where a modular gcd degree obstruction is
claimed.

## Post-Review Revision

The review follow-up keeps `GoodReduction.lean` data-free and adds two
certificate-facing refinements:

- `reduceInt_dvd_modularGCD_of_int_dvd` splits the pure integral-divisibility
  core from the Gauss-clearing wrapper.  Callers that already know `h ∣ F` and
  `h ∣ G` no longer need to route through rational divisibility.
- `natDegree_le_modularGCD_of_rat_dvd_of_left_lc` and
  `natDegree_le_modularGCD_of_rat_dvd_of_right_lc`, plus the positive-degree
  and `ZMod p` wrappers, derive the hidden factor's leading-coefficient
  hypothesis and target nonvanishing from one surviving target leading
  coefficient.  This matches the sparse-collision-certificate workflow where a
  top coefficient is checked nonzero modulo `1009`.

Remaining bridge contracts for downstream certificate branches:

1. A rational-factor normalization bridge should turn a common
   `hQ : Polynomial Rat` of integer targets into a primitive
   `hZ : Polynomial Int` with `0 < hZ.natDegree` and
   `hZ.map (Int.castRingHom Rat)` dividing the same rational targets.  This is
   the contract needed to connect `PackageShare`/`OrientationShare` witnesses to
   this module without adding project-specific assumptions.
2. The undivided collision-trinomial checker still needs forced-factor
   accounting outside this module.  For
   `C = (Polynomial.X - 1 : Polynomial Int) ^ 2`, a collision-specific bridge
   should show that an extra noncyclotomic common factor `h` forces
   `(C * h)` (or an equivalent divided-target factor) into the modular gcd
   target, yielding a lower bound `2 + h.natDegree ≤ gcdDegree` under the
   appropriate coprimality/nonvanishing hypotheses.

Those bridges should live in a module importing both
`Qab.Certificates.GoodReduction` and the relevant polynomial constructors, not
in `GoodReduction.lean` itself.
