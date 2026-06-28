import Qab.Constants

namespace Qab

/-!
Basic package-level objects.

This phase deliberately keeps `PackageShare` opaque.  The first concrete
opening should replace it by the existence of a nonconstant common factor of
the canonical reciprocal package products over `ℚ[x]`.  Until then, no theorem
in this repository should manufacture a `PackageShare` proof except via
explicit assumptions.

Phase-1 warning: the primitive coefficient formula defines only the primitive
orientation polynomial `qPrimZ`.  The full orientation polynomial for an
imprimitive pair must use the manuscript convention
`Q_{a,b}(x) = g * Q_{A,B}(x^g)`.  Keep the later names separate:
`qPrimZ`, `qOrientZ`, `qPackageProdZ`, `OrientationShare`, `PackageShare`.
-/

/-- A positive ordered pair `(a,b)`.  The mathematical package also contains
both reciprocal orientations, so unordered equality is tracked separately. -/
structure PosPair where
  a : Nat
  b : Nat
  ha_pos : 0 < a
  hb_pos : 0 < b

namespace PosPair

/-- The nontrivial package condition used in the theorem statement. -/
def unequal (P : PosPair) : Prop := P.a ≠ P.b

/-- Equality after allowing the reciprocal swap. -/
def sameUnordered (P Q : PosPair) : Prop :=
  (P.a = Q.a ∧ P.b = Q.b) ∨ (P.a = Q.b ∧ P.b = Q.a)

/-- Swapped orientation helper, useful when the polynomial layer is opened. -/
def swap (P : PosPair) : PosPair where
  a := P.b
  b := P.a
  ha_pos := P.hb_pos
  hb_pos := P.ha_pos

end PosPair

/--
Opaque phase-0 sharing predicate.  Phase 1 should replace this by something
like

```
∃ h : Polynomial ℚ,
  0 < h.natDegree ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q
```

after `qPrimZ`, `qOrientZ`, and `qPackageProdZ` have been added.
-/
axiom PackageShare : PosPair → PosPair → Prop

/-- Final theorem target at package level. -/
def ReciprocalPackageCoprimality : Prop :=
  ∀ {P Q : PosPair},
    P.unequal → Q.unequal → ¬ P.sameUnordered Q → ¬ PackageShare P Q

end Qab
