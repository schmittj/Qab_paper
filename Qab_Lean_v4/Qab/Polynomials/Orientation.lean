import Mathlib.Algebra.Polynomial.Expand
import Mathlib.Algebra.Polynomial.FieldDivision
import Mathlib.RingTheory.PrincipalIdealDomain
import Mathlib.RingTheory.Polynomial.UniqueFactorization
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

lemma qPrimZ_primitivePart_isPrimitive (P : PosPair) :
    (qPrimZ P.primitivePart).IsPrimitive :=
  qPrimZ_isPrimitive P.primitivePart P.primitivePart_primitive

lemma qPrimZ_primitivePart_content_eq_one (P : PosPair) :
    (qPrimZ P.primitivePart).content = 1 :=
  qPrimZ_content_eq_one P.primitivePart P.primitivePart_primitive

lemma primitivePart_a_mul_gcd (P : PosPair) : P.primitivePart.a * P.gcd = P.a := by
  simpa [primitivePart, gcd] using Nat.div_mul_cancel (Nat.gcd_dvd_left P.a P.b)

lemma primitivePart_b_mul_gcd (P : PosPair) : P.primitivePart.b * P.gcd = P.b := by
  simpa [primitivePart, gcd] using Nat.div_mul_cancel (Nat.gcd_dvd_right P.a P.b)

lemma primitivePart_sum_mul_gcd (P : PosPair) :
    (P.primitivePart.a + P.primitivePart.b) * P.gcd = P.a + P.b := by
  rw [Nat.add_mul, P.primitivePart_a_mul_gcd, P.primitivePart_b_mul_gcd]

lemma gcd_mul_primitivePart_a (P : PosPair) : P.gcd * P.primitivePart.a = P.a := by
  rw [Nat.mul_comm]
  exact P.primitivePart_a_mul_gcd

lemma gcd_mul_primitivePart_b (P : PosPair) : P.gcd * P.primitivePart.b = P.b := by
  rw [Nat.mul_comm]
  exact P.primitivePart_b_mul_gcd

lemma gcd_mul_primitivePart_sum (P : PosPair) :
    P.gcd * (P.primitivePart.a + P.primitivePart.b) = P.a + P.b := by
  rw [Nat.mul_comm, P.primitivePart_sum_mul_gcd]

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

noncomputable def qOrientNumeratorZ (P : PosPair) : Polynomial Int :=
  Polynomial.C (P.gcd : Int) *
    Polynomial.expand Int P.gcd (qNumeratorZ P.primitivePart)

lemma qOrientNumeratorZ_eq_qNumeratorZ (P : PosPair) :
    qOrientNumeratorZ P = qNumeratorZ P := by
  let A : Int := ((P.a / P.gcd : Nat) : Int)
  let B : Int := ((P.b / P.gcd : Nat) : Int)
  have haNat : P.gcd * (P.a / P.gcd) = P.a := by
    simpa [PosPair.primitivePart] using P.gcd_mul_primitivePart_a
  have hbNat : P.gcd * (P.b / P.gcd) = P.b := by
    simpa [PosPair.primitivePart] using P.gcd_mul_primitivePart_b
  have hsumNat : P.gcd * (P.a / P.gcd + P.b / P.gcd) = P.a + P.b := by
    simpa [PosPair.primitivePart] using P.gcd_mul_primitivePart_sum
  have hpow_total :
      (Polynomial.X ^ P.gcd : Polynomial Int) ^
          (P.a / P.gcd + P.b / P.gcd) =
        Polynomial.X ^ (P.a + P.b) := by
    rw [← pow_mul, hsumNat]
  have hpow_a :
      (Polynomial.X ^ P.gcd : Polynomial Int) ^ (P.a / P.gcd) =
        Polynomial.X ^ P.a := by
    rw [← pow_mul, haNat]
  have ha : (P.gcd : Int) * A = (P.a : Int) := by
    dsimp [A]
    exact_mod_cast haNat
  have hb : (P.gcd : Int) * B = (P.b : Int) := by
    dsimp [B]
    exact_mod_cast hbNat
  simp [qOrientNumeratorZ, qNumeratorZ, hpow_total, hpow_a, Nat.cast_add]
  calc
    ((P.gcd : Int) : Polynomial Int) *
        (((A : Int) : Polynomial Int) *
            (Polynomial.X : Polynomial Int) ^ (P.a + P.b) -
          (((A : Int) : Polynomial Int) + ((B : Int) : Polynomial Int)) *
            Polynomial.X ^ P.a +
          ((B : Int) : Polynomial Int))
        = (((P.gcd : Int) * A : Int) : Polynomial Int) *
            Polynomial.X ^ (P.a + P.b) -
            ((((P.gcd : Int) * A + (P.gcd : Int) * B : Int) : Polynomial Int)) *
            Polynomial.X ^ P.a +
            (((P.gcd : Int) * B : Int) : Polynomial Int) := by
          simp [Int.cast_mul, Int.cast_add]
          ring_nf
    _ = ((P.a : Int) : Polynomial Int) * Polynomial.X ^ (P.a + P.b) -
          (((P.a : Int) + (P.b : Int) : Int) : Polynomial Int) *
            Polynomial.X ^ P.a +
          ((P.b : Int) : Polynomial Int) := by
          rw [ha, hb]
    _ = ((P.a : Int) : Polynomial Int) * Polynomial.X ^ (P.a + P.b) -
          (((P.a : Int) : Polynomial Int) + ((P.b : Int) : Polynomial Int)) *
            Polynomial.X ^ P.a +
          ((P.b : Int) : Polynomial Int) := by
          simp [Int.cast_add]

@[simp]
lemma qOrientNumeratorZ_natDegree (P : PosPair) :
    (qOrientNumeratorZ P).natDegree = P.a + P.b := by
  rw [qOrientNumeratorZ_eq_qNumeratorZ, qNumeratorZ_natDegree]

@[simp]
lemma qOrientNumeratorZ_leadingCoeff (P : PosPair) :
    (qOrientNumeratorZ P).leadingCoeff = (P.a : Int) := by
  rw [qOrientNumeratorZ_eq_qNumeratorZ, qNumeratorZ_leadingCoeff]

/--
Closed form for the full orientation polynomial after clearing the
imprimitive double root at every `gcd a b`-th root of unity.
-/
lemma qOrientZ_closed_form (P : PosPair) :
    ((Polynomial.X ^ P.gcd - 1 : Polynomial Int) ^ 2) * qOrientZ P =
      Polynomial.C (P.gcd : Int) *
        Polynomial.expand Int P.gcd (qNumeratorZ P.primitivePart) := by
  rw [qOrientZ, ← qPrimZ_closed_form P.primitivePart]
  simp only [map_mul, map_pow, map_sub, expand_X, map_one]
  ring

lemma qOrientZ_closed_form_numerator (P : PosPair) :
    ((Polynomial.X ^ P.gcd - 1 : Polynomial Int) ^ 2) * qOrientZ P =
      qOrientNumeratorZ P := by
  simpa [qOrientNumeratorZ] using qOrientZ_closed_form P

lemma qOrientNumeratorZ_cyclotomic_sq_dvd (P : PosPair) :
    ((Polynomial.X ^ P.gcd - 1 : Polynomial Int) ^ 2) ∣ qOrientNumeratorZ P :=
  ⟨qOrientZ P, (qOrientZ_closed_form_numerator P).symm⟩

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

lemma qOrientZ_eval_one_pos (P : PosPair) :
    0 < (qOrientZ P).eval (1 : Int) := by
  have hg_pos : (0 : Int) < (P.gcd : Int) := by
    exact_mod_cast P.gcd_pos
  rw [qOrientZ, eval_C_mul, expand_eval]
  simpa using mul_pos hg_pos (qPrimZ_eval_one_pos P.primitivePart)

lemma qOrientZ_eval_one_ne_zero (P : PosPair) :
    (qOrientZ P).eval (1 : Int) ≠ 0 :=
  ne_of_gt (qOrientZ_eval_one_pos P)

/-- Full orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qOrientQ (P : PosPair) : Polynomial Rat :=
  (qOrientZ P).map (Int.castRingHom Rat)

noncomputable def qOrientNumeratorQ (P : PosPair) : Polynomial Rat :=
  (qOrientNumeratorZ P).map (Int.castRingHom Rat)

@[simp]
lemma qOrientQ_coeff_zero (P : PosPair) :
    (qOrientQ P).coeff 0 = (P.b : Rat) := by
  simp [qOrientQ]

lemma qOrientQ_ne_zero (P : PosPair) : qOrientQ P ≠ 0 := by
  intro h
  have hcoeff := congrArg (fun f : Polynomial Rat => f.coeff 0) h
  have hb_ne : (P.b : Rat) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt P.hb_pos)
  exact hb_ne (by simpa using hcoeff)

lemma qOrientQ_eval_one_ne_zero (P : PosPair) :
    (qOrientQ P).eval (1 : Rat) ≠ 0 := by
  have hInt : (Polynomial.eval (1 : Int) (qOrientZ P) : Int) ≠ 0 := by
    simpa using qOrientZ_eval_one_ne_zero P
  have hRat : ((Polynomial.eval (1 : Int) (qOrientZ P) : Int) : Rat) ≠ 0 := by
    exact Int.cast_ne_zero.mpr hInt
  rw [qOrientQ]
  change ((qOrientZ P).map (Int.castRingHom Rat)).eval
      ((Int.castRingHom Rat) (1 : Int)) ≠ 0
  rw [Polynomial.eval_map_apply]
  exact hRat

lemma qOrientQ_closed_form_numerator (P : PosPair) :
    ((Polynomial.X ^ P.gcd - 1 : Polynomial Rat) ^ 2) * qOrientQ P =
      qOrientNumeratorQ P := by
  have h := congrArg
    (fun f : Polynomial Int => f.map (Int.castRingHom Rat))
    (qOrientZ_closed_form_numerator P)
  simpa [qOrientQ, qOrientNumeratorQ] using h

lemma qOrientNumeratorQ_cyclotomic_sq_dvd (P : PosPair) :
    ((Polynomial.X ^ P.gcd - 1 : Polynomial Rat) ^ 2) ∣ qOrientNumeratorQ P :=
  ⟨qOrientQ P, (qOrientQ_closed_form_numerator P).symm⟩

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

lemma qPackageProdQ_eq_orient_mul (P : PosPair) :
    qPackageProdQ P = qOrientQ P * qOrientQ P.swap := by
  simp [qPackageProdQ, qPackageProdZ, qOrientQ]

lemma qPackageProdQ_ne_zero (P : PosPair) : qPackageProdQ P ≠ 0 := by
  rw [qPackageProdQ_eq_orient_mul]
  exact mul_ne_zero (qOrientQ_ne_zero P) (qOrientQ_ne_zero P.swap)

lemma qOrientQ_dvd_qPackageProdQ (P : PosPair) :
    qOrientQ P ∣ qPackageProdQ P := by
  rw [qPackageProdQ_eq_orient_mul]
  exact ⟨qOrientQ P.swap, rfl⟩

lemma qOrientQ_swap_dvd_qPackageProdQ (P : PosPair) :
    qOrientQ P.swap ∣ qPackageProdQ P := by
  rw [qPackageProdQ_eq_orient_mul]
  exact ⟨qOrientQ P, by rw [mul_comm]⟩

@[simp]
lemma qPackageProdQ_swap (P : PosPair) :
    qPackageProdQ P.swap = qPackageProdQ P := by
  simp [qPackageProdQ]

/-- A nonconstant rational polynomial factor. -/
def NonconstantFactorQ (h : Polynomial Rat) : Prop :=
  0 < h.natDegree

noncomputable def orientGcdQ (P Q : PosPair) : Polynomial Rat :=
  gcd (qOrientQ P) (qOrientQ Q)

noncomputable def packageGcdQ (P Q : PosPair) : Polynomial Rat :=
  gcd (qPackageProdQ P) (qPackageProdQ Q)

lemma NonconstantFactorQ_iff_not_isUnit_of_ne_zero {h : Polynomial Rat}
    (hh : h ≠ 0) : NonconstantFactorQ h ↔ ¬ IsUnit h := by
  constructor
  · intro hdeg
    exact not_isUnit_of_natDegree_pos h hdeg
  · intro hnot
    by_contra hdeg
    have hdeg0 : h.natDegree = 0 := Nat.eq_zero_of_not_pos hdeg
    obtain ⟨c, hc⟩ := Polynomial.natDegree_eq_zero.mp hdeg0
    have hc_ne : c ≠ 0 := by
      intro hc0
      apply hh
      rw [← hc, hc0, map_zero]
    exact hnot (hc ▸ (isUnit_C.mpr (isUnit_iff_ne_zero.mpr hc_ne)))

lemma commonFactor_iff_gcd_natDegree_pos {f g : Polynomial Rat}
    (hfg : f ≠ 0 ∨ g ≠ 0) :
    (∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ f ∧ h ∣ g) ↔
      NonconstantFactorQ (gcd f g) := by
  have hgcd_ne : gcd f g ≠ 0 := by
    intro hg
    have hzero := (gcd_eq_zero_iff f g).mp hg
    rcases hfg with hf | hg'
    · exact hf hzero.1
    · exact hg' hzero.2
  constructor
  · rintro ⟨h, hnc, hfdiv, hgdiv⟩
    have hdvd : h ∣ gcd f g := dvd_gcd hfdiv hgdiv
    exact lt_of_lt_of_le hnc (natDegree_le_of_dvd hdvd hgcd_ne)
  · intro hgpos
    exact ⟨gcd f g, hgpos, gcd_dvd_left f g, gcd_dvd_right f g⟩

lemma commonFactor_iff_not_isCoprime {f g : Polynomial Rat}
    (hfg : f ≠ 0 ∨ g ≠ 0) :
    (∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ f ∧ h ∣ g) ↔
      ¬ IsCoprime f g := by
  have hgcd_ne : gcd f g ≠ 0 := by
    intro hg
    have hzero := (gcd_eq_zero_iff f g).mp hg
    rcases hfg with hf | hg'
    · exact hf hzero.1
    · exact hg' hzero.2
  rw [commonFactor_iff_gcd_natDegree_pos hfg,
    NonconstantFactorQ_iff_not_isUnit_of_ne_zero hgcd_ne]
  constructor
  · intro hnot hcop
    exact hnot ((gcd_isUnit_iff f g).mpr hcop)
  · intro hnot hunit
    exact hnot ((gcd_isUnit_iff f g).mp hunit)

lemma orientGcdQ_ne_zero (P Q : PosPair) : orientGcdQ P Q ≠ 0 := by
  intro h
  have hzero := (gcd_eq_zero_iff (qOrientQ P) (qOrientQ Q)).mp
    (by simpa [orientGcdQ] using h)
  exact qOrientQ_ne_zero P hzero.1

lemma packageGcdQ_ne_zero (P Q : PosPair) : packageGcdQ P Q ≠ 0 := by
  intro h
  have hzero := (gcd_eq_zero_iff (qPackageProdQ P) (qPackageProdQ Q)).mp
    (by simpa [packageGcdQ] using h)
  exact qPackageProdQ_ne_zero P hzero.1

/-- Orientation-level common-factor predicate, kept separate from product-level sharing. -/
def OrientationShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ qOrientQ P ∧ h ∣ qOrientQ Q

lemma OrientationShare_iff_gcd_natDegree_pos (P Q : PosPair) :
    OrientationShare P Q ↔ 0 < (orientGcdQ P Q).natDegree := by
  simpa [OrientationShare, orientGcdQ, NonconstantFactorQ] using
    (commonFactor_iff_gcd_natDegree_pos
      (f := qOrientQ P) (g := qOrientQ Q) (Or.inl (qOrientQ_ne_zero P)))

lemma OrientationShare_iff_not_isCoprime (P Q : PosPair) :
    OrientationShare P Q ↔ ¬ IsCoprime (qOrientQ P) (qOrientQ Q) := by
  simpa [OrientationShare] using
    (commonFactor_iff_not_isCoprime
      (f := qOrientQ P) (g := qOrientQ Q) (Or.inl (qOrientQ_ne_zero P)))

lemma OrientationShare_comm (P Q : PosPair) :
    OrientationShare P Q ↔ OrientationShare Q P := by
  constructor
  · rintro ⟨h, hnc, hP, hQ⟩
    exact ⟨h, hnc, hQ, hP⟩
  · rintro ⟨h, hnc, hQ, hP⟩
    exact ⟨h, hnc, hP, hQ⟩

/--
Underlying product-level sharing predicate used by the package-level
`PackageShare` definition.
-/
def PackageProductShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial Rat, NonconstantFactorQ h ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q

lemma PackageProductShare_iff_gcd_natDegree_pos (P Q : PosPair) :
    PackageProductShare P Q ↔ 0 < (packageGcdQ P Q).natDegree := by
  simpa [PackageProductShare, packageGcdQ, NonconstantFactorQ] using
    (commonFactor_iff_gcd_natDegree_pos
      (f := qPackageProdQ P) (g := qPackageProdQ Q)
      (Or.inl (qPackageProdQ_ne_zero P)))

lemma PackageProductShare_iff_not_isCoprime (P Q : PosPair) :
    PackageProductShare P Q ↔ ¬ IsCoprime (qPackageProdQ P) (qPackageProdQ Q) := by
  simpa [PackageProductShare] using
    (commonFactor_iff_not_isCoprime
      (f := qPackageProdQ P) (g := qPackageProdQ Q)
      (Or.inl (qPackageProdQ_ne_zero P)))

lemma OrientationShare.toPackageProductShare {P Q : PosPair}
    (hPQ : OrientationShare P Q) : PackageProductShare P Q := by
  rcases hPQ with ⟨h, hnc, hP, hQ⟩
  exact ⟨h, hnc, dvd_trans hP (qOrientQ_dvd_qPackageProdQ P),
    dvd_trans hQ (qOrientQ_dvd_qPackageProdQ Q)⟩

lemma PackageProductShare_comm (P Q : PosPair) :
    PackageProductShare P Q ↔ PackageProductShare Q P := by
  constructor
  · rintro ⟨h, hnc, hP, hQ⟩
    exact ⟨h, hnc, hQ, hP⟩
  · rintro ⟨h, hnc, hQ, hP⟩
    exact ⟨h, hnc, hP, hQ⟩

@[simp]
lemma PackageProductShare_swap_left (P Q : PosPair) :
    PackageProductShare P.swap Q ↔ PackageProductShare P Q := by
  simp [PackageProductShare]

@[simp]
lemma PackageProductShare_swap_right (P Q : PosPair) :
    PackageProductShare P Q.swap ↔ PackageProductShare P Q := by
  simp [PackageProductShare]

/--
Product-level sharing decomposes through one of the four reciprocal
orientation choices.  This is the comparison theorem that keeps reducible
common factors honest: the product-level witness is first replaced by an
irreducible factor, then primality splits divisibility across the two product
factors.
-/
def ReciprocalOrientationShare (P Q : PosPair) : Prop :=
  OrientationShare P Q ∨ OrientationShare P.swap Q ∨
    OrientationShare P Q.swap ∨ OrientationShare P.swap Q.swap

lemma ReciprocalOrientationShare.toPackageProductShare {P Q : PosPair}
    (hPQ : ReciprocalOrientationShare P Q) : PackageProductShare P Q := by
  rcases hPQ with hPQ | hPQ | hPQ | hPQ
  · exact hPQ.toPackageProductShare
  · simpa using hPQ.toPackageProductShare
  · simpa using hPQ.toPackageProductShare
  · simpa using hPQ.toPackageProductShare

lemma PackageProductShare.toReciprocalOrientationShare {P Q : PosPair}
    (hPQ : PackageProductShare P Q) : ReciprocalOrientationShare P Q := by
  rcases hPQ with ⟨h, hnc, hPprod, hQprod⟩
  obtain ⟨r, hrIrred, hrh⟩ := Polynomial.exists_irreducible_of_natDegree_pos
    (f := h) hnc
  have hrNc : NonconstantFactorQ r := hrIrred.natDegree_pos
  have hrPrime : Prime r := UniqueFactorizationMonoid.irreducible_iff_prime.mp hrIrred
  have hrPprod : r ∣ qPackageProdQ P := dvd_trans hrh hPprod
  have hrQprod : r ∣ qPackageProdQ Q := dvd_trans hrh hQprod
  rw [qPackageProdQ_eq_orient_mul] at hrPprod hrQprod
  rcases hrPrime.dvd_or_dvd hrPprod with hP | hPswap
  · rcases hrPrime.dvd_or_dvd hrQprod with hQ | hQswap
    · exact Or.inl ⟨r, hrNc, hP, hQ⟩
    · exact Or.inr (Or.inr (Or.inl ⟨r, hrNc, hP, hQswap⟩))
  · rcases hrPrime.dvd_or_dvd hrQprod with hQ | hQswap
    · exact Or.inr (Or.inl ⟨r, hrNc, hPswap, hQ⟩)
    · exact Or.inr (Or.inr (Or.inr ⟨r, hrNc, hPswap, hQswap⟩))

lemma packageProductShare_iff_reciprocalOrientationShare (P Q : PosPair) :
    PackageProductShare P Q ↔ ReciprocalOrientationShare P Q := by
  exact ⟨PackageProductShare.toReciprocalOrientationShare,
    ReciprocalOrientationShare.toPackageProductShare⟩

end Qab
