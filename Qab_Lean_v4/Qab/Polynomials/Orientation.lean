import Mathlib.Algebra.Polynomial.Expand
import Qab.Polynomials.Primitive

namespace Qab

open Polynomial

namespace PosPair

/-- Common divisor used to pass from an arbitrary positive pair to a primitive pair. -/
def gcd (P : PosPair) : Nat := Nat.gcd P.a P.b

lemma gcd_pos (P : PosPair) : 0 < P.gcd := by
  simpa [gcd] using Nat.gcd_pos_of_pos_left P.b P.ha_pos

/--
The primitive pair `(a/g,b/g)`, where `g = gcd a b`.

This is the only input on which the primitive coefficient formula should be
used when building the full orientation polynomial.
-/
def primitivePart (P : PosPair) : PosPair where
  a := P.a / P.gcd
  b := P.b / P.gcd
  ha_pos := by
    simpa [gcd] using Nat.div_gcd_pos_of_pos_left P.b P.ha_pos
  hb_pos := by
    simpa [gcd] using Nat.div_gcd_pos_of_pos_right P.a P.hb_pos

@[simp]
lemma primitivePart_a (P : PosPair) : P.primitivePart.a = P.a / P.gcd := rfl

@[simp]
lemma primitivePart_b (P : PosPair) : P.primitivePart.b = P.b / P.gcd := rfl

lemma primitivePart_primitive (P : PosPair) : P.primitivePart.Primitive := by
  simpa [primitivePart, Primitive, gcd] using
    Nat.coprime_div_gcd_div_gcd (Nat.gcd_pos_of_pos_left P.b P.ha_pos)

lemma primitivePart_a_mul_gcd (P : PosPair) : P.primitivePart.a * P.gcd = P.a := by
  simpa [primitivePart, gcd] using Nat.div_mul_cancel (Nat.gcd_dvd_left P.a P.b)

lemma primitivePart_b_mul_gcd (P : PosPair) : P.primitivePart.b * P.gcd = P.b := by
  simpa [primitivePart, gcd] using Nat.div_mul_cancel (Nat.gcd_dvd_right P.a P.b)

lemma gcd_mul_primitivePart_a (P : PosPair) : P.gcd * P.primitivePart.a = P.a := by
  rw [Nat.mul_comm]
  exact P.primitivePart_a_mul_gcd

lemma gcd_mul_primitivePart_b (P : PosPair) : P.gcd * P.primitivePart.b = P.b := by
  rw [Nat.mul_comm]
  exact P.primitivePart_b_mul_gcd

@[simp]
lemma swap_gcd (P : PosPair) : P.swap.gcd = P.gcd := by
  simp [gcd, swap, Nat.gcd_comm]

end PosPair

/--
Full orientation polynomial over `ℤ`.

For `g = gcd a b` and primitive part `(A,B) = (a/g,b/g)`, this is
`g * Q_{A,B}(x^g)`.  The `Polynomial.expand` operation implements
composition with `x ↦ x^g`.
-/
noncomputable def qOrientZ (P : PosPair) : Polynomial Int :=
  Polynomial.C (P.gcd : Int) * Polynomial.expand Int P.gcd (qPrimZ P.primitivePart)

@[simp]
lemma qOrientZ_coeff_zero (P : PosPair) :
    (qOrientZ P).coeff 0 = (P.b : Int) := by
  have hg : 0 < P.gcd := P.gcd_pos
  have hb : P.gcd * P.primitivePart.b = P.b := P.gcd_mul_primitivePart_b
  rw [qOrientZ, coeff_C_mul, coeff_expand hg, if_pos (Nat.dvd_zero P.gcd), Nat.zero_div,
    qPrimZ_coeff_zero]
  exact_mod_cast hb

/-- Full orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qOrientQ (P : PosPair) : Polynomial Rat :=
  (qOrientZ P).map (Int.castRingHom Rat)

/-- Reciprocal package product over `ℤ`. -/
noncomputable def qPackageProdZ (P : PosPair) : Polynomial Int :=
  qOrientZ P * qOrientZ P.swap

/-- Reciprocal package product over `ℚ[x]`. -/
noncomputable def qPackageProdQ (P : PosPair) : Polynomial Rat :=
  (qPackageProdZ P).map (Int.castRingHom Rat)

/-- A nonconstant rational polynomial factor. -/
def NonconstantFactorQ (h : Polynomial Rat) : Prop :=
  0 < h.natDegree

/-- Orientation-level common-factor predicate, kept separate from product-level sharing. -/
def OrientationShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ qOrientQ P ∧ h ∣ qOrientQ Q

/--
Concrete product-level sharing predicate for the eventual replacement of the
opaque phase-0 `PackageShare`.
-/
def PackageProductShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q

end Qab
