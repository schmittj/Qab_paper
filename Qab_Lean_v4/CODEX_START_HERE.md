# Codex CLI handoff: Qab Lean v4

You are starting a conditional Lean formalization of the `Q_{a,b}` package-coprimality proof. The first milestone is not to prove the external theorem packs. The first milestone is to make the theorem-pack assembly compile cleanly, with the assumption boundary explicit and stable.

## Inputs in this repository

```text
README.md
Qab.lean
Qab/
  Constants.lean
  Basic.lean
  Counterexample.lean
  CoreProof.lean
  Packs/
  Certificates/
docs/
  Qab_Lean_Roadmap_v4.md
  Qab_core_v4.tex
  Qab_core_v4.pdf
  original/Qab_original.tex
  reviews/audit_v2.md
  reviews/final_polish_review.md
```

The original manuscript is included at `docs/original/Qab_original.tex`. The roadmap is the implementation contract; the TeX file is the human-review mathematical core.

## First command

Run this from the repository root:

```bash
lake exe cache get
lake build
```

If the pinned Lean/mathlib version is stale or unavailable, update `lean-toolchain` and `lakefile.lean` together, then record the change in a short changelog. Do not change theorem-pack semantics merely to fix a build issue.

## Phase-0 acceptance criteria

Phase 0 is complete when:

1. `lake build` succeeds.
2. `package_coprimality_from_packs` compiles.
3. `FromShare` is opaque or a genuine structure, not `True`.
4. No theorem outside `Qab/Packs/BroadAxioms.lean` depends on the broad temporary axiom instances.
5. `Qab.lean` does not import `Qab/Packs/BroadAxioms.lean`.
6. `Qab/CoreProof.lean` stays a short assembly proof from theorem packs.
7. Any syntax/API adjustments are documented.

## Do not do these in phase 0

* Do not define `FromShare := True`.
* Do not add dummy proofs of `FromShare`.
* Do not move broad axioms out of `Qab/Packs/BroadAxioms.lean`.
* Do not import `Qab.CoreProof` from certificate interface files.
* Do not start large certificate work before the polynomial semantics are fixed.

## Phase-1 polynomial semantics

`PackageShare` is concrete and product-level.  Keep these objects distinct.

```lean
qPrimZ         -- primitive orientation polynomial Q_{A,B}
qOrientZ       -- full orientation polynomial Q_{a,b}, using primitive reduction
qPackageProdZ  -- reciprocal package product Q_{a,b} * Q_{b,a}
OrientationShare
PackageShare
```

For primitive coprime positive `A,B`, the coefficient-defined polynomial is:

```text
Qprim_{A,B}(x)
 = sum_{0 <= j < A} B(j+1)x^j
   + sum_{A <= j <= A+B-2} A(A+B-j-1)x^j.
```

For nonprimitive pairs `a = g A`, `b = g B`, with `g = gcd(a,b)`, the full orientation polynomial must use:

```text
Q_{a,b}(x) = g * Q_{A,B}(x^g).
```

Do not define a full `packageQZ` for an arbitrary `PosPair` by the primitive formula alone; that formula is only correct after primitive reduction.

Product-level sharing is closest to the theorem statement:

```lean
def PackageShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q
```

Orientation-level sharing is useful for the collision dictionary:

```lean
def OrientationShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qOrientQ P ∧ h ∣ qOrientQ Q
```

If `OrientationShare` is used, prove a separate bridge that package-product sharing gives orientation sharing for some reciprocal-orientation choice.
The current API provides this bridge as
`packageProductShare_iff_reciprocalOrientationShare`.

## Suggested phase-1 proof order

1. Define `qPrimZ` on positive primitive pairs, or on `PosPair` plus a primitive hypothesis.
2. Prove coefficient support, constant coefficient, leading coefficient, and degree lemmas.
3. Define `qOrientZ` using primitive reduction and composition `x |-> x^g`.
4. Define `qPackageProdZ` as `qOrientZ P * qOrientZ P.swap` after adding a `PosPair.swap` helper.
5. Use `PackageShare_iff_packageProductShare` and
   `PackageShare_iff_reciprocalOrientationShare` for theorem-boundary work.
6. Only then begin the residual `ZMod 1009` certificate checker.

## Certificate trust boundary

The current certificate interface is schematic. Audit identifiers or hashes are not proof. The first real certificate milestone should produce typed Lean data or generated Lean terms checking:

* the terminal row is well-formed;
* the certificate target is explicit: divided package polynomial or undivided collision trinomial;
* the prime is actually prime;
* good-reduction side conditions hold;
* a Bezout/Euclidean gcd certificate proves the claimed exact gcd degree;
* forced cyclotomic degree accounts for all modular gcd degree.

For residual terminal certificates over `ZMod 1009`, decide explicitly whether the modular computation is on undivided collision trinomials or divided package polynomials. If using collision trinomials, account for the forced double root at `x = 1`.

## When to check back

Check back before changing any theorem-pack signature in a mathematically meaningful way, before choosing the final `FromShare` representation, or before deciding the Kummer-defect strategy for the 46 irreducible-shape branch.
