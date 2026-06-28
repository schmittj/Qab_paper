# OpenAI Primitive Identity Review, 2026-06-28

Response id: `resp_08059623444e6ed8006a411a9db8bc819da47cc15d79fef229`

This was a focused proof-guidance request for the primitive closed-form
identity before the local triangular-sum proof was committed.

## Main Advice

- The scaffold boundaries look sound:
  - `Primitive.lean` depends on `Qab.Pairs`, not the opaque `Qab.Basic`
    package-sharing layer.
  - `Orientation.lean` correctly builds the imprimitive polynomial through
    `Polynomial.expand`.
  - broad assumptions remain isolated in `Qab/Packs/BroadAxioms.lean`.
- The main risk is proof/definition bloat in the polynomial layer, not
  assumption leakage.
- Suggested statement shape:
  - introduce a `qNumeratorZ P` trinomial definition;
  - prove a compact `qPrimZ_closed_form`;
  - expose the expanded theorem as a derived statement;
  - do not mark the theorem as `[simp]`.
- Suggested proof route:
  - use coefficient extensionality;
  - prove a private coefficient formula for `((X - 1)^2) * f` using
    `Polynomial.coeff_X_pow_mul'` and `Polynomial.coeff_C_mul_X_pow`;
  - isolate endpoint arithmetic in a private integer-indexed mirror of
    `qPrimCoeffZ`, then transport back to `Nat` coefficients.
- Suggested next imprimitive theorem:
  `((X ^ P.gcd - 1)^2) * qOrientZ P = qNumeratorZ P`, proved from the
  primitive closed form through `Polynomial.expand`.

## Comparison Notes For Follow-Up

- The committed local proof `qPrimZ_mul_X_sub_one_sq` instead uses private
  recursive ascending/descending triangular-sum helpers.
- Before refactoring, compare this OpenAI advice against the pending Claude
  post-implementation review.  The key question is whether the triangular-sum
  proof is maintainable enough, or whether the integer-indexed
  second-difference proof would be shorter and cleaner after all.
