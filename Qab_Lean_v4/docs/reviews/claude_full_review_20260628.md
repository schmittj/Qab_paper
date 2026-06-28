# Claude Full Review, 2026-06-28

Receipt: `artifacts/ai_reviews/20260628_151301_claude_receipt.json`

Review file: `artifacts/ai_reviews/20260628_151301_claude_review.txt`

Model/effort: `opus` / `max`

Scope: full current-state review after commit `79f81bf`, with special focus on
`qPrimZ_mul_X_sub_one_sq`, the private triangular-sum helper design, and the
safest next implementation step.

## Main Findings

- The Lean scaffold is structurally sound:
  - `CoreProof.lean` remains a clean assembly proof.
  - broad pack axioms remain isolated in `Qab/Packs/BroadAxioms.lean`;
  - the polynomial layer is correctly separate from the opaque
    `PackageShare`/`FromShare` layer.
- The new primitive identity `qPrimZ_mul_X_sub_one_sq` is mathematically
  correct and soundly proved.
- The private ascending/descending triangular-sum helper design is
  maintainable and not worth rewriting now.
- The best small refactor is to name the trinomial numerator, for example
  `qNumeratorZ` or `qCollisionZ`, and restate the primitive identity through
  it.
- The safest next implementation step is the imprimitive numerator identity
  for `qOrientZ`, then rational/map/product API support.
- Do **not** flip the opaque `PackageShare` axiom to the concrete
  `PackageProductShare` predicate yet.  Claude's strategic concern is that this
  would not remove a theorem-pack axiom and would make the broad-axiom smoke
  test's consistency effectively depend on the target theorem unless the real
  collision-to-counterexample bridge is opened at the same time.

## Concrete Recommendations

- Add a named numerator/trinomial definition and basic API:
  - `natDegree`;
  - leading coefficient;
  - constant coefficient;
  - evaluation and derivative facts at `1` to record the forced double root.
- Prove an imprimitive identity in `Orientation.lean` from the primitive
  identity through `Polynomial.expand`:
  `((X ^ P.gcd - 1)^2) * qOrientZ P = ...`.
- Prove rational image/product facts for `qPackageProdQ`.
- Add a regression check around `#print axioms package_coprimality_from_packs`
  so accidental imports of broad axioms into the conditional theorem are caught.
- Keep the triangular helper island private and stop investing in it unless a
  future Mathlib bump breaks the current proof.

## Notes For Planning

- Claude explicitly compared the committed triangular-sum proof with the
  OpenAI-suggested integer-indexed second-difference route and recommended not
  rewriting now.
- The next work should be demand-driven by the numerator/imprimitive/certificate
  path, not by prematurely replacing `PackageShare`.
