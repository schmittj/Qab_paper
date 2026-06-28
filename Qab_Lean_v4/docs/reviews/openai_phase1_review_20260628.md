# OpenAI Phase-1 Review Digest

Review metadata:

- Timestamp: 2026-06-28T14:13:05+02:00
- Response id: `resp_06c8c1492ced2df4006a410d462c14819da27571b1bcd31b45`
- Requested model: `gpt-5.5-pro-2026-04-23`
- Reasoning effort: `xhigh`
- Tools requested: code interpreter, web search

The reviewer inspected the zipped project bundle but did not type-check Lean
inside the review container.  Local `lake build` checks remain authoritative.

Key findings:

- The phase-0 theorem-pack scaffold has the right conditional shape:
  `CoreProof.lean` is pack-parametric, broad assumptions are isolated in
  `Qab.Packs.BroadAxioms`, and `Qab.lean` does not import broad axioms.
- `PackageShare` and `FromShare` are opaque but not vacuous.  They should not
  be used to prove concrete finite-pack assumptions until their intended
  meanings are replaced by definitions/checkers.
- Pair-level definitions should be split out of `Basic.lean` before concrete
  polynomial sharing is introduced, otherwise `Basic.lean` could need to import
  polynomial modules that already depend on `Basic.lean`.
- The primitive coefficient formula should remain separate from the full
  imprimitive orientation polynomial; all full package semantics should go
  through `qOrientZ = g * qPrimZ(A,B)(x^g)`.
- `Polynomial.expand` is an appropriate Mathlib API for the `x ↦ x^g`
  composition layer.
- Before replacing opaque `PackageShare`, harden the polynomial layer with
  general coefficient lemmas, endpoint facts, degree facts, and package product
  definitions over `ℚ[x]`.
- Residual modular artifacts appear to target collision polynomials with forced
  gcd degree `2`; they should not be silently reinterpreted as already-divided
  package-product certificates.

Actions taken after the review:

- Added `Qab.Pairs` and moved `PosPair`, `unequal`, `sameUnordered`, and `swap`
  there.
- Changed `Qab.Polynomials.Primitive` to import `Qab.Pairs`, removing its
  dependency on the opaque phase-0 `PackageShare` layer.
- Added `Qab.Polynomials.Orientation` with primitive reduction, `qOrientZ`,
  `qOrientQ`, package products, and separate concrete sharing predicates.
- Verified `lake build` and `lake build Qab.Packs.BroadAxioms` after the split.

One recommendation was tested and deferred: removing `noncomputable` from
`qPrimZ`/`qPrimQ` fails on Mathlib v4.31.0 because the current polynomial
semiring/map definitions are marked noncomputable.
