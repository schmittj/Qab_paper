# Qab Lean Changelog

## 2026-06-28

- Created a central reusable Mathlib checkout at `/home/jo314/lean/mathlib4-central`.
- Pinned the scaffold to `leanprover/lean4:v4.31.0` and local Mathlib commit
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (`v4.31.0`).
- Replaced the GitHub Mathlib dependency with the central local path so this
  repository does not clone its own Mathlib copy.
- Adjusted Lean declarations for `v4.31.0`: replaced old `constant`
  declarations by `axiom` declarations for opaque predicates and expanded
  grouped structure fields used by dependent later fields.
- Verified `lake build` and `lake build Qab.Packs.BroadAxioms`.
- Added `Qab.Polynomials.Primitive` with the primitive-pair predicate,
  primitive coefficient function, `qPrimZ`, `qPrimQ`, and the constant
  coefficient lemma for `qPrimZ`.
- Extended the primitive polynomial layer with the top coefficient, support
  bound, nonzero endpoint coefficients, general `qPrimZ`/`qPrimQ` coefficient
  lemmas, and exact `natDegree` for `qPrimZ`.
- Split pair-level definitions into `Qab.Pairs` so polynomial modules no longer
  depend on the opaque phase-0 `PackageShare` layer.
- Added `Qab.Polynomials.Orientation` with primitive reduction, the full
  imprimitive orientation polynomial `qOrientZ`, package products over `ℤ` and
  `ℚ`, separate concrete sharing predicates, and `qOrientZ_coeff_zero`.
- Added orientation and package-product endpoint infrastructure: coefficient
  transport through `Polynomial.expand`, exact `natDegree`, leading
  coefficient, nonzero, and swap-invariance lemmas.
- Added basic product-sharing predicate lemmas for symmetry and reciprocal-swap
  invariance.
- Recorded the first OpenAI background review digest in
  `docs/reviews/openai_phase1_review_20260628.md`.
- Fixed and documented the Claude review helper: stdin prompts, self-managed
  background reviews, polling/cancellation receipts, and captured review
  artifacts.
- Removed OpenAI review response-token caps from the helper and made web-search
  return budget unlimited by default for long review/guidance runs.
- Proved the primitive closed-form identity
  `qPrimZ_mul_X_sub_one_sq`, clearing the double root at `1`.
- Added the named primitive trinomial numerator `qNumeratorZ`, with endpoint,
  degree, leading-coefficient, evaluation, and derivative-evaluation lemmas.
- Proved the imprimitive orientation closed form `qOrientZ_closed_form` as
  `C (gcd a b) * expand (gcd a b) (qNumeratorZ primitivePart)`.
- Added the product-sharing comparison API:
  `qPackageProdQ_eq_orient_mul`, orientation-factor divisibility into package
  products, `OrientationShare.toPackageProductShare`,
  `ReciprocalOrientationShare`, and
  `packageProductShare_iff_reciprocalOrientationShare`.
- Replaced the opaque `Basic.PackageShare` axiom by the concrete
  product-level predicate `PackageProductShare`, with bridge lemmas to
  `PackageProductShare` and `ReciprocalOrientationShare`.
- Added the first residual Phase 2 modular-gcd checker over `ZMod 1009`:
  `Qab.Certificates.ZModGcd` defines the executable dense collision-gcd
  checker and forced double-root accounting, and
  `Qab.Certificates.ResidualZMod1009` checks the two residual terminal
  orientation rows and eight orientation certificates from the bundled CSV
  artifacts.
