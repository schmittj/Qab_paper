# Qab Lean v4 blueprint

This repository is a **conditional formalization from theorem packs**, not a Lean-certified proof of the theorem packs themselves.

The immediate goal is to give a Codex CLI worker a buildable, pack-parametric Lean scaffold and a precise work order. The core theorem is:

```lean
theorem package_coprimality_from_packs
    (C  : CollisionPack)
    (G  : GlobalHeightPack)
    (UN : UpperNormalizationPack)
    (UR : UpperRangePack)
    (L  : LocalPacketPack)
    (FL : FiniteLowerPack)
    (FR : FiniteResidualPack) :
    ReciprocalPackageCoprimality
```

The file `Qab/Packs/BroadAxioms.lean` contains temporary broad axiom instances. It exists only as a smoke-test and assumption-boundary file. Do not import it into mathematical development files unless the resulting theorem is explicitly described as axiom-dependent.

## What changed in v4

The v4 polish pass implements the last review suggestions:

1. `CoreProof.lean` no longer binds a local variable named `rw`; the residual witness is named `reswit`.
2. `Qab/Certificates/Interfaces.lean` imports `Qab.Packs.LocalPacket`, not `Qab.CoreProof`, to avoid future dependency cycles.
3. `FiniteLowerPack.no_lower_unit` and `FiniteLowerPack.no_both_nonunit` explicitly take the lower-box hypothesis `ce.D ≤ lowerMax`.
4. The phase-1 instructions now distinguish primitive orientation polynomials, full imprimitive orientation polynomials, reciprocal package products, orientation-level sharing, and package-product sharing.
5. The certificate interface is more explicit: terminal rows have a `WellFormed` predicate, `exactGcdDegree` replaces `expectedGcdDegree`, and each modular-gcd certificate states the polynomial target it checks.
6. The zip package has no duplicate top-level copies of the docs; canonical documents live under `docs/`.
7. `CODEX_START_HERE.md` is the handoff file for a local Codex CLI worker.

## Safety guardrails

1. `FromShare` is opaque. It must not be defined as `True`.
2. No dummy `FromShare` proofs should be introduced.
3. Temporary assumptions live only in `Qab/Packs/BroadAxioms.lean`.
4. The arithmetic endpoint trichotomy is proved directly in `NormCE.coeff_trichotomy`; the local p-adic/Kummer content is represented by `LocalPacketPack.to_lower_state` and `LocalPacketPack.to_residual_witness`.
5. Lower finite eliminators consume admissible state data and, for the unit and both-nonunit branches, the explicit lower-box hypothesis `ce.D ≤ lowerMax`.
6. The residual branch exposes its envelope explicitly: after reciprocal normalization, `D ≤ 16583`, `Vabs = 1`, `2 ≤ U ≤ D`, and `d ≤ 2601`.
7. `Qab.lean` intentionally does **not** import `Qab/Packs/BroadAxioms.lean`.
8. Certificate hashes or audit identifiers are never Lean proofs; certificate soundness must eventually be reduced to typed Lean data and checked predicates.

## Build

This scaffold pins Lean/mathlib at the version recorded in `lean-toolchain` and `lakefile.lean`. A worker may refresh the pin before starting substantial development, but should record that change.

```bash
lake exe cache get
lake build
```

This package was prepared without a local Lean/Lake installation, so the first worker should run `lake build` immediately and make any small API/syntax adjustments before doing mathematical work.

## Start here

Read `CODEX_START_HERE.md` first. It contains the concrete first-milestone instructions and the non-negotiable assumption-boundary rules.

The canonical design document is `docs/Qab_Lean_Roadmap_v4.md`. The reviewer-facing mathematical summary is `docs/Qab_core_v4.tex` and its compiled PDF.

## Phase-1 polynomial semantics

`PackageShare` is now concrete, but it is deliberately product-level rather
than a naive coefficient polynomial for arbitrary pairs. The primitive
coefficient formula defines `Q_{A,B}` only after primitive reduction. The
formalization separates:

```lean
qPrimZ        -- primitive orientation polynomial Q_{A,B}
qOrientZ      -- full orientation polynomial Q_{a,b}, using primitive reduction
qPackageProdZ -- reciprocal product Q_{a,b} * Q_{b,a}
OrientationShare
PackageShare
```

For nonprimitive pairs, the intended relation is `a = g*A`, `b = g*B`, `gcd A B = 1`, and `Q_{a,b}(x) = g * Q_{A,B}(x^g)`. Product-level `PackageShare` should refer to common nonconstant factors of `qPackageProdQ`; orientation-level sharing, if introduced, should be a separate predicate with a theorem selecting compatible orientations from product-level sharing.
This is implemented through `PackageProductShare`,
`ReciprocalOrientationShare`, and
`packageProductShare_iff_reciprocalOrientationShare`.

## Suggested first tasks

1. Run `lake build` and fix any syntax/API drift.
2. Keep `Qab/CoreProof.lean` short and pack-parametric.
3. Confirm `BroadAxioms.lean` compiles but remains unimported by `Qab.lean`.
4. Continue hardening the polynomial layer as needed, but do not change the
   collision-to-counterexample boundary without review.
5. Add a small residual-terminal certificate checker over `ZMod 1009` only after
   the polynomial constructors are stable.
6. Convert broad pack fields into narrower theorem packs one at a time.

## Included reference files

* `docs/original/Qab_original.tex` is the original manuscript source used for comparison.
* `docs/Qab_core_v4.tex` and `docs/Qab_core_v4.pdf` are the streamlined mathematical companion.
* `docs/Qab_Lean_Roadmap_v4.md` is the detailed implementation contract.
* `docs/reviews/final_polish_review.md` records the final external polish review that motivated v4.
* `CODEX_START_HERE.md` gives the recommended first prompt and task order for a Codex CLI worker.
