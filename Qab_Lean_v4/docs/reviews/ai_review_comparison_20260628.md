# AI Review Comparison, 2026-06-28

Inputs:

- OpenAI focused primitive-identity review:
  `openai_primitive_identity_review_20260628.md`.
- Claude full post-implementation review:
  `claude_full_review_20260628.md`.

## Agreement

- The current scaffold keeps the theorem-pack boundary clean.
- Broad axioms remain isolated.
- The primitive closed-form identity is the right mathematical direction.
- The RHS trinomial should be named as a reusable object.
- The next substantive Lean work should move from the primitive identity to the
  imprimitive `qOrientZ` identity and rational/product API.
- The closed-form theorem should not be a `[simp]` lemma.

## Difference In Proof-Style Advice

- OpenAI suggested a coefficient-extensional proof using an integer-indexed
  mirror of `qPrimCoeffZ`.
- The committed proof uses private recursive triangular-sum helpers.
- Claude reviewed the committed triangular-sum proof and recommended not
  rewriting it now; the proof is sound and the alternative would be lateral.

## Strategic Decision

Keep `qPrimZ_mul_X_sub_one_sq` as currently proved, but introduce a named
trinomial numerator before building the imprimitive layer.  Defer any
`PackageShare` concretization until the real collision-to-counterexample bridge
is being developed.

## Proposed Next Step

1. Add `qNumeratorZ` or `qCollisionZ` in the polynomial layer.
2. Restate the primitive identity through that definition.
3. Prove endpoint/degree/double-root facts for the numerator.
4. Prove the imprimitive `qOrientZ` numerator identity using
   `Polynomial.expand`.
