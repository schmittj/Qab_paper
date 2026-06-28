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

lemma primitivePart_degree_mul_gcd (P : PosPair) :
    (P.primitivePart.a + P.primitivePart.b - 2) * P.gcd =
      P.a + P.b - 2 * P.gcd := by
  rw [Nat.sub_mul, Nat.add_mul, P.primitivePart_a_mul_gcd, P.primitivePart_b_mul_gcd]

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

lemma qOrientZ_coeff_zero_ne_zero (P : PosPair) :
    (qOrientZ P).coeff 0 ≠ 0 := by
  rw [qOrientZ_coeff_zero]
  exact_mod_cast (Nat.ne_of_gt P.hb_pos)

lemma qOrientZ_coeff_mul_gcd (P : PosPair) (n : Nat) :
    (qOrientZ P).coeff (n * P.gcd) =
      (P.gcd : Int) * qPrimCoeffZ P.primitivePart n := by
  rw [qOrientZ, coeff_C_mul, coeff_expand P.gcd_pos, if_pos (dvd_mul_left P.gcd n),
    Nat.mul_div_left n P.gcd_pos, qPrimZ_coeff]

lemma qOrientZ_coeff_of_not_dvd_gcd {P : PosPair} {j : Nat} (hj : ¬ P.gcd ∣ j) :
    (qOrientZ P).coeff j = 0 := by
  rw [qOrientZ, coeff_C_mul, coeff_expand P.gcd_pos, if_neg hj, mul_zero]

lemma qOrientZ_ne_zero (P : PosPair) : qOrientZ P ≠ 0 := by
  intro h
  exact qOrientZ_coeff_zero_ne_zero P (by simp [h])

@[simp]
lemma qOrientZ_natDegree (P : PosPair) :
    (qOrientZ P).natDegree = P.a + P.b - 2 * P.gcd := by
  have hg_ne : (P.gcd : Int) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt P.gcd_pos)
  calc
    (qOrientZ P).natDegree
        =
          (Polynomial.expand Int P.gcd (qPrimZ P.primitivePart)).natDegree := by
            rw [qOrientZ, natDegree_C_mul hg_ne]
    _ = (P.primitivePart.a + P.primitivePart.b - 2) * P.gcd := by
            rw [natDegree_expand, qPrimZ_natDegree]
    _ = P.a + P.b - 2 * P.gcd := P.primitivePart_degree_mul_gcd

@[simp]
lemma qOrientZ_leadingCoeff (P : PosPair) :
    (qOrientZ P).leadingCoeff = (P.a : Int) := by
  have hg_ne : (P.gcd : Int) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt P.gcd_pos)
  let E : Polynomial Int := Polynomial.expand Int P.gcd (qPrimZ P.primitivePart)
  have hleadE : E.leadingCoeff = (P.primitivePart.a : Int) := by
    dsimp [E]
    rw [leadingCoeff_expand P.gcd_pos]
    exact qPrimZ_leadingCoeff P.primitivePart
  have hmul : (P.gcd : Int) * E.leadingCoeff ≠ 0 := by
    rw [hleadE]
    exact mul_ne_zero hg_ne (by exact_mod_cast (Nat.ne_of_gt P.primitivePart.ha_pos))
  rw [qOrientZ]
  change (Polynomial.C (P.gcd : Int) * E).leadingCoeff = (P.a : Int)
  rw [leadingCoeff, natDegree_C_mul_of_mul_ne_zero hmul, coeff_C_mul, ← leadingCoeff,
    hleadE]
  exact_mod_cast P.gcd_mul_primitivePart_a

@[simp]
lemma qOrientZ_coeff_natDegree (P : PosPair) :
    (qOrientZ P).coeff (P.a + P.b - 2 * P.gcd) = (P.a : Int) := by
  rw [← qOrientZ_natDegree, ← leadingCoeff, qOrientZ_leadingCoeff]

/-- Full orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qOrientQ (P : PosPair) : Polynomial Rat :=
  (qOrientZ P).map (Int.castRingHom Rat)

@[simp]
lemma qOrientQ_coeff_zero (P : PosPair) :
    (qOrientQ P).coeff 0 = (P.b : Rat) := by
  simp [qOrientQ]

/-- Reciprocal package product over `ℤ`. -/
noncomputable def qPackageProdZ (P : PosPair) : Polynomial Int :=
  qOrientZ P * qOrientZ P.swap

lemma qPackageProdZ_ne_zero (P : PosPair) : qPackageProdZ P ≠ 0 := by
  rw [qPackageProdZ]
  exact mul_ne_zero (qOrientZ_ne_zero P) (qOrientZ_ne_zero P.swap)

@[simp]
lemma qPackageProdZ_natDegree (P : PosPair) :
    (qPackageProdZ P).natDegree = 2 * (P.a + P.b - 2 * P.gcd) := by
  rw [qPackageProdZ, natDegree_mul (qOrientZ_ne_zero P) (qOrientZ_ne_zero P.swap)]
  simp
  omega

@[simp]
lemma qPackageProdZ_leadingCoeff (P : PosPair) :
    (qPackageProdZ P).leadingCoeff = (P.a : Int) * (P.b : Int) := by
  rw [qPackageProdZ, leadingCoeff_mul]
  simp [PosPair.swap]

@[simp]
lemma qPackageProdZ_swap (P : PosPair) :
    qPackageProdZ P.swap = qPackageProdZ P := by
  simp [qPackageProdZ, mul_comm]

/-- Reciprocal package product over `ℚ[x]`. -/
noncomputable def qPackageProdQ (P : PosPair) : Polynomial Rat :=
  (qPackageProdZ P).map (Int.castRingHom Rat)

@[simp]
lemma qPackageProdQ_swap (P : PosPair) :
    qPackageProdQ P.swap = qPackageProdQ P := by
  simp [qPackageProdQ]

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
