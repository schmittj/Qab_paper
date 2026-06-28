import Qab.Constants
import Qab.Pairs
import Qab.Polynomials.Orientation

namespace Qab

/-!
Basic package-level objects.

`PackageShare` is now the concrete product-level sharing predicate: existence
of a nonconstant common factor of the canonical reciprocal package products
over `ℚ[x]`.  The collision-to-counterexample bridge remains conditional and
is represented by the `CollisionPack` interface.

Phase-1 warning: the primitive coefficient formula defines only the primitive
orientation polynomial `qPrimZ`.  The full orientation polynomial for an
imprimitive pair must use the manuscript convention
`Q_{a,b}(x) = g * Q_{A,B}(x^g)`.  Keep the later names separate:
`qPrimZ`, `qOrientZ`, `qPackageProdZ`, `OrientationShare`, `PackageShare`.
-/

/--
Concrete product-level package sharing:

```
∃ h : Polynomial ℚ,
  0 < h.natDegree ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q
```
-/
def PackageShare (P Q : PosPair) : Prop :=
  PackageProductShare P Q

lemma PackageShare_iff_packageProductShare (P Q : PosPair) :
    PackageShare P Q ↔ PackageProductShare P Q := by
  rfl

lemma PackageShare_iff_reciprocalOrientationShare (P Q : PosPair) :
    PackageShare P Q ↔ ReciprocalOrientationShare P Q := by
  simpa [PackageShare] using packageProductShare_iff_reciprocalOrientationShare P Q

lemma PackageShare_iff_gcd_natDegree_pos (P Q : PosPair) :
    PackageShare P Q ↔ 0 < (packageGcdQ P Q).natDegree := by
  simpa [PackageShare] using PackageProductShare_iff_gcd_natDegree_pos P Q

lemma PackageShare_iff_not_isCoprime (P Q : PosPair) :
    PackageShare P Q ↔ ¬ IsCoprime (qPackageProdQ P) (qPackageProdQ Q) := by
  simpa [PackageShare] using PackageProductShare_iff_not_isCoprime P Q

lemma PackageShare_comm (P Q : PosPair) :
    PackageShare P Q ↔ PackageShare Q P := by
  simpa [PackageShare] using PackageProductShare_comm P Q

@[simp]
lemma PackageShare_swap_left (P Q : PosPair) :
    PackageShare P.swap Q ↔ PackageShare P Q := by
  simp [PackageShare]

@[simp]
lemma PackageShare_swap_right (P Q : PosPair) :
    PackageShare P Q.swap ↔ PackageShare P Q := by
  simp [PackageShare]

/-- Final theorem target at package level. -/
def ReciprocalPackageCoprimality : Prop :=
  ∀ {P Q : PosPair},
    P.unequal → Q.unequal → ¬ P.sameUnordered Q → ¬ PackageShare P Q

end Qab
