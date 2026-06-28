import Qab.Constants
import Qab.Pairs

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
