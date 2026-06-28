import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Polynomial.Degree.Lemmas
import Qab.Pairs

namespace Qab

open Polynomial
open scoped BigOperators

/-!
Primitive orientation polynomials.

This module starts Phase 1 without changing the phase-0 theorem statement.
The coefficient formula here is only the primitive orientation formula from
the roadmap.  It must not be used directly as the full imprimitive
`Q_{a,b}` when `gcd a b > 1`; the later `qOrientZ` layer will perform
primitive reduction and composition with `x ↦ x^g`.
-/

namespace PosPair

/-- Primitive-pair predicate for the orientation polynomial formula. -/
def Primitive (P : PosPair) : Prop := Nat.Coprime P.a P.b

end PosPair

/-- Coefficient of the primitive orientation polynomial `Q_{A,B}`. -/
def qPrimCoeffZ (P : PosPair) (j : Nat) : Int :=
  if j < P.a then
    (P.b : Int) * ((j + 1 : Nat) : Int)
  else if j ≤ P.a + P.b - 2 then
    (P.a : Int) * ((P.a + P.b - j - 1 : Nat) : Int)
  else
    0

@[simp]
lemma qPrimCoeffZ_of_lt {P : PosPair} {j : Nat} (hj : j < P.a) :
    qPrimCoeffZ P j = (P.b : Int) * ((j + 1 : Nat) : Int) := by
  simp [qPrimCoeffZ, hj]

lemma qPrimCoeffZ_of_not_lt_of_le {P : PosPair} {j : Nat}
    (hjA : ¬ j < P.a) (hjTop : j ≤ P.a + P.b - 2) :
    qPrimCoeffZ P j =
      (P.a : Int) * ((P.a + P.b - j - 1 : Nat) : Int) := by
  simp [qPrimCoeffZ, hjA, hjTop]

lemma qPrimCoeffZ_of_top_lt {P : PosPair} {j : Nat}
    (hjTop : P.a + P.b - 2 < j) :
    qPrimCoeffZ P j = 0 := by
  have hjTop' : ¬ j ≤ P.a + P.b - 2 := Nat.not_le_of_gt hjTop
  by_cases hjA : j < P.a
  · have hb : 0 < P.b := P.hb_pos
    omega
  · simp [qPrimCoeffZ, hjA, hjTop']

@[simp]
lemma qPrimCoeffZ_top (P : PosPair) :
    qPrimCoeffZ P (P.a + P.b - 2) = (P.a : Int) := by
  have hA : 0 < P.a := P.ha_pos
  have hB : 0 < P.b := P.hb_pos
  by_cases hb : P.b = 1
  · have hlt : P.a + P.b - 2 < P.a := by
      omega
    have hidxInt : ((P.a - 1 : Nat) : Int) + 1 = (P.a : Int) := by
      omega
    calc
      qPrimCoeffZ P (P.a + P.b - 2)
          = (P.b : Int) * (((P.a + P.b - 2) + 1 : Nat) : Int) := by
              simpa using
                qPrimCoeffZ_of_lt (P := P) (j := P.a + P.b - 2) hlt
      _ = (P.a : Int) := by
              simp [hb, hidxInt]
  · have hb2 : 2 ≤ P.b := by
      omega
    have hnotlt : ¬ P.a + P.b - 2 < P.a := by
      omega
    have hidx : P.a + P.b - (P.a + P.b - 2) - 1 = 1 := by
      omega
    calc
      qPrimCoeffZ P (P.a + P.b - 2)
          =
            (P.a : Int) *
              ((P.a + P.b - (P.a + P.b - 2) - 1 : Nat) : Int) := by
              simpa using
                qPrimCoeffZ_of_not_lt_of_le (P := P) (j := P.a + P.b - 2)
                  hnotlt le_rfl
      _ = (P.a : Int) := by
              simp [hidx]

/--
Primitive orientation polynomial over `ℤ`.

For primitive positive `A,B`, this is
`Σ_{0 ≤ j < A} B(j+1)x^j + Σ_{A ≤ j ≤ A+B-2} A(A+B-j-1)x^j`.
The finite range is `0, …, A+B-2`.
-/
noncomputable def qPrimZ (P : PosPair) : Polynomial Int :=
  (Finset.range (P.a + P.b - 1)).sum fun j =>
    Polynomial.monomial j (qPrimCoeffZ P j)

@[simp]
lemma qPrimZ_coeff_zero (P : PosPair) :
    (qPrimZ P).coeff 0 = (P.b : Int) := by
  have hA : 0 < P.a := P.ha_pos
  have hB : 0 < P.b := P.hb_pos
  have hRange : 0 < P.a + P.b - 1 := by
    omega
  rw [qPrimZ, finsetSum_coeff]
  simp only [coeff_monomial]
  rw [Finset.sum_eq_single 0]
  · simp [qPrimCoeffZ, hA]
  · intro j _ hj
    simp [hj]
  · intro hnot
    simp [hRange] at hnot

lemma qPrimZ_coeff_eq_zero_of_top_lt {P : PosPair} {j : Nat}
    (hjTop : P.a + P.b - 2 < j) :
    (qPrimZ P).coeff j = 0 := by
  have hA : 0 < P.a := P.ha_pos
  have hB : 0 < P.b := P.hb_pos
  rw [qPrimZ, finsetSum_coeff]
  refine Finset.sum_eq_zero ?_
  intro k hk
  have hkRange : k < P.a + P.b - 1 := Finset.mem_range.mp hk
  have hne : k ≠ j := by
    omega
  simp [coeff_monomial, hne]

lemma qPrimZ_coeff (P : PosPair) (j : Nat) :
    (qPrimZ P).coeff j = qPrimCoeffZ P j := by
  by_cases hjRange : j < P.a + P.b - 1
  · rw [qPrimZ, finsetSum_coeff]
    simp only [coeff_monomial]
    rw [Finset.sum_eq_single j]
    · simp
    · intro k _ hkj
      simp [hkj]
    · intro hnot
      exact False.elim (hnot (Finset.mem_range.mpr hjRange))
  · have hA : 0 < P.a := P.ha_pos
    have hB : 0 < P.b := P.hb_pos
    have hjTop : P.a + P.b - 2 < j := by
      omega
    rw [qPrimZ_coeff_eq_zero_of_top_lt hjTop, qPrimCoeffZ_of_top_lt hjTop]

lemma qPrimZ_natDegree_le (P : PosPair) :
    (qPrimZ P).natDegree ≤ P.a + P.b - 2 := by
  rw [natDegree_le_iff_coeff_eq_zero]
  intro j hj
  exact qPrimZ_coeff_eq_zero_of_top_lt (P := P) (j := j) hj

@[simp]
lemma qPrimZ_coeff_top (P : PosPair) :
    (qPrimZ P).coeff (P.a + P.b - 2) = (P.a : Int) := by
  have hA : 0 < P.a := P.ha_pos
  have hB : 0 < P.b := P.hb_pos
  have hRange : P.a + P.b - 2 < P.a + P.b - 1 := by
    omega
  rw [qPrimZ, finsetSum_coeff]
  simp only [coeff_monomial]
  rw [Finset.sum_eq_single (P.a + P.b - 2)]
  · simp
  · intro j _ hj
    simp [hj]
  · intro hnot
    simp [hRange] at hnot

lemma qPrimZ_coeff_zero_ne_zero (P : PosPair) :
    (qPrimZ P).coeff 0 ≠ 0 := by
  rw [qPrimZ_coeff_zero]
  exact_mod_cast (Nat.ne_of_gt P.hb_pos)

lemma qPrimZ_coeff_top_ne_zero (P : PosPair) :
    (qPrimZ P).coeff (P.a + P.b - 2) ≠ 0 := by
  rw [qPrimZ_coeff_top]
  exact_mod_cast (Nat.ne_of_gt P.ha_pos)

@[simp]
lemma qPrimZ_natDegree (P : PosPair) :
    (qPrimZ P).natDegree = P.a + P.b - 2 := by
  exact natDegree_eq_of_le_of_coeff_ne_zero
    (qPrimZ_natDegree_le P) (qPrimZ_coeff_top_ne_zero P)

/-- Primitive orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qPrimQ (P : PosPair) : Polynomial Rat :=
  (qPrimZ P).map (Int.castRingHom Rat)

@[simp]
lemma qPrimQ_coeff (P : PosPair) (j : Nat) :
    (qPrimQ P).coeff j = (qPrimCoeffZ P j : Rat) := by
  simp [qPrimQ, qPrimZ_coeff]

end Qab
