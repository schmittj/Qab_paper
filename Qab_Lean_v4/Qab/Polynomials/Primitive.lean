import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Polynomial.Degree.Lemmas
import Mathlib.Algebra.Polynomial.Derivative
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

lemma qPrimZ_ne_zero (P : PosPair) : qPrimZ P ≠ 0 := by
  intro h
  exact qPrimZ_coeff_zero_ne_zero P (by simp [h])

lemma qPrimZ_coeff_top_ne_zero (P : PosPair) :
    (qPrimZ P).coeff (P.a + P.b - 2) ≠ 0 := by
  rw [qPrimZ_coeff_top]
  exact_mod_cast (Nat.ne_of_gt P.ha_pos)

@[simp]
lemma qPrimZ_natDegree (P : PosPair) :
    (qPrimZ P).natDegree = P.a + P.b - 2 := by
  exact natDegree_eq_of_le_of_coeff_ne_zero
    (qPrimZ_natDegree_le P) (qPrimZ_coeff_top_ne_zero P)

@[simp]
lemma qPrimZ_leadingCoeff (P : PosPair) :
    (qPrimZ P).leadingCoeff = (P.a : Int) := by
  rw [leadingCoeff, qPrimZ_natDegree, qPrimZ_coeff_top]

/-- Primitive orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qPrimQ (P : PosPair) : Polynomial Rat :=
  (qPrimZ P).map (Int.castRingHom Rat)

@[simp]
lemma qPrimQ_coeff (P : PosPair) (j : Nat) :
    (qPrimQ P).coeff j = (qPrimCoeffZ P j : Rat) := by
  simp [qPrimQ, qPrimZ_coeff]

/--
The trinomial numerator obtained from the primitive orientation polynomial
after clearing the double root at `1`.
-/
noncomputable def qNumeratorZ (P : PosPair) : Polynomial Int :=
  Polynomial.C (P.a : Int) * Polynomial.X ^ (P.a + P.b) -
    Polynomial.C (((P.a + P.b : Nat) : Int)) * Polynomial.X ^ P.a +
    Polynomial.C (P.b : Int)

@[simp]
lemma qNumeratorZ_coeff_zero (P : PosPair) :
    (qNumeratorZ P).coeff 0 = (P.b : Int) := by
  have hA : 0 ≠ P.a := (Nat.ne_of_gt P.ha_pos).symm
  have hTop : 0 ≠ P.a + P.b := (Nat.ne_of_gt (Nat.add_pos_left P.ha_pos P.b)).symm
  rw [qNumeratorZ, coeff_add, coeff_sub, coeff_C_mul_X_pow,
    coeff_C_mul_X_pow, coeff_C]
  simp [hA, hTop]

@[simp]
lemma qNumeratorZ_coeff_top (P : PosPair) :
    (qNumeratorZ P).coeff (P.a + P.b) = (P.a : Int) := by
  have hA : P.a ≠ 0 := Nat.ne_of_gt P.ha_pos
  have hB : P.b ≠ 0 := Nat.ne_of_gt P.hb_pos
  rw [qNumeratorZ, coeff_add, coeff_sub, coeff_C_mul_X_pow,
    coeff_C_mul_X_pow, coeff_C]
  simp [hA, hB]

lemma qNumeratorZ_natDegree_le (P : PosPair) :
    (qNumeratorZ P).natDegree ≤ P.a + P.b := by
  rw [natDegree_le_iff_coeff_eq_zero]
  intro j hj
  have hTop : j ≠ P.a + P.b := by omega
  have hMid : j ≠ P.a := by omega
  have hZero : j ≠ 0 := by omega
  rw [qNumeratorZ, coeff_add, coeff_sub, coeff_C_mul_X_pow,
    coeff_C_mul_X_pow, coeff_C]
  simp [hTop, hMid, hZero]

lemma qNumeratorZ_coeff_top_ne_zero (P : PosPair) :
    (qNumeratorZ P).coeff (P.a + P.b) ≠ 0 := by
  rw [qNumeratorZ_coeff_top]
  exact_mod_cast (Nat.ne_of_gt P.ha_pos)

@[simp]
lemma qNumeratorZ_natDegree (P : PosPair) :
    (qNumeratorZ P).natDegree = P.a + P.b := by
  exact natDegree_eq_of_le_of_coeff_ne_zero
    (qNumeratorZ_natDegree_le P) (qNumeratorZ_coeff_top_ne_zero P)

@[simp]
lemma qNumeratorZ_leadingCoeff (P : PosPair) :
    (qNumeratorZ P).leadingCoeff = (P.a : Int) := by
  rw [leadingCoeff, qNumeratorZ_natDegree, qNumeratorZ_coeff_top]

@[simp]
lemma qNumeratorZ_eval_one (P : PosPair) :
    Polynomial.eval (1 : Int) (qNumeratorZ P) = 0 := by
  simp [qNumeratorZ, Nat.cast_add]

@[simp]
lemma qNumeratorZ_derivative_eval_one (P : PosPair) :
    Polynomial.eval (1 : Int) (Polynomial.derivative (qNumeratorZ P)) = 0 := by
  simp only [qNumeratorZ, derivative_add, derivative_sub, derivative_C_mul_X_pow,
    derivative_C, eval_add, eval_sub, eval_mul, eval_C, eval_X_pow, one_pow,
    mul_one, eval_zero]
  norm_num [Nat.cast_add]
  ring

/-
Triangular-sum helpers for the closed form of the primitive orientation
polynomial.  They are kept private because the exported object is the final
identity for `qPrimZ`.
-/
private noncomputable def qPrimAscZ : Nat → Polynomial Int
  | 0 => 0
  | n + 1 => qPrimAscZ n + Polynomial.C (((n + 1 : Nat) : Int)) * Polynomial.X ^ n

@[simp]
private lemma qPrimAscZ_zero : qPrimAscZ 0 = 0 := rfl

@[simp]
private lemma qPrimAscZ_succ (n : Nat) :
    qPrimAscZ (n + 1) =
      qPrimAscZ n + Polynomial.C (((n + 1 : Nat) : Int)) * Polynomial.X ^ n := rfl

private noncomputable def qPrimDescZ : Nat → Polynomial Int
  | 0 => 0
  | n + 1 => Polynomial.C (((n + 1 : Nat) : Int)) + Polynomial.X * qPrimDescZ n

@[simp]
private lemma qPrimDescZ_zero : qPrimDescZ 0 = 0 := rfl

@[simp]
private lemma qPrimDescZ_succ (n : Nat) :
    qPrimDescZ (n + 1) =
      Polynomial.C (((n + 1 : Nat) : Int)) + Polynomial.X * qPrimDescZ n := rfl

private lemma qPrimAscZ_closed (n : Nat) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimAscZ n =
      1 - Polynomial.C (((n + 1 : Nat) : Int)) * Polynomial.X ^ n +
        Polynomial.C ((n : Int)) * Polynomial.X ^ (n + 1) := by
  induction n with
  | zero =>
      simp
  | succ n ih =>
      rw [qPrimAscZ_succ, mul_add, ih]
      norm_num [Nat.cast_add, Nat.cast_one]
      ring_nf

private lemma qPrimDescZ_closed (n : Nat) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimDescZ n =
      Polynomial.C ((n : Int)) -
        Polynomial.C (((n + 1 : Nat) : Int)) * Polynomial.X +
        Polynomial.X ^ (n + 1) := by
  induction n with
  | zero =>
      simp
  | succ n ih =>
      rw [qPrimDescZ_succ, mul_add]
      rw [show ((Polynomial.X - 1 : Polynomial Int) ^ 2) * (Polynomial.X * qPrimDescZ n) =
          Polynomial.X * (((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimDescZ n) by
        ring]
      rw [ih]
      norm_num [Nat.cast_add, Nat.cast_one]
      ring_nf

private lemma qPrimAscZ_coeff (n j : Nat) :
    (qPrimAscZ n).coeff j = if j < n then ((j + 1 : Nat) : Int) else 0 := by
  induction n generalizing j with
  | zero =>
      simp
  | succ n ih =>
      rw [qPrimAscZ_succ, coeff_add]
      by_cases hjn : j = n
      · subst j
        rw [coeff_C_mul_X_pow]
        simp [ih]
      · have hcoeff :
            (Polynomial.C (((n + 1 : Nat) : Int)) * Polynomial.X ^ n).coeff j = 0 := by
          rw [coeff_C_mul_X_pow]
          simp [hjn]
        rw [hcoeff, add_zero, ih]
        by_cases hj : j < n
        · have hjs : j < n + 1 := by omega
          simp [hj, hjs]
        · have hnot : ¬ j < n + 1 := by omega
          simp [hj, hnot]

private lemma qPrimDescZ_coeff (n j : Nat) :
    (qPrimDescZ n).coeff j = if j < n then ((n - j : Nat) : Int) else 0 := by
  induction n generalizing j with
  | zero =>
      simp
  | succ n ih =>
      cases j with
      | zero =>
          simp [qPrimDescZ_succ]
      | succ j =>
          rw [qPrimDescZ_succ, coeff_add]
          have hC :
              (Polynomial.C (((n + 1 : Nat) : Int))).coeff (j + 1) = 0 := by
            rw [coeff_C]
            simp
          rw [hC, zero_add]
          have hx : (Polynomial.X * qPrimDescZ n).coeff (j + 1) =
              (qPrimDescZ n).coeff j :=
            coeff_X_mul (qPrimDescZ n) j
          rw [hx, ih]
          by_cases hj : j < n
          · have hjs : j + 1 < n + 1 := by omega
            have hsub : n + 1 - (j + 1) = n - j := by omega
            simp [hj, hjs, hsub]
          · have hnot : ¬ j + 1 < n + 1 := by omega
            simp [hj, hnot]

private lemma qPrimZ_eq_triangles (P : PosPair) :
    qPrimZ P =
      Polynomial.C (P.b : Int) * qPrimAscZ P.a +
        Polynomial.C (P.a : Int) * (Polynomial.X ^ P.a * qPrimDescZ (P.b - 1)) := by
  ext j
  rw [qPrimZ_coeff, coeff_add, coeff_C_mul, coeff_C_mul, coeff_X_pow_mul',
    qPrimAscZ_coeff, qPrimDescZ_coeff]
  by_cases hjA : j < P.a
  · have hnotAle : ¬ P.a ≤ j := by omega
    simp [qPrimCoeffZ, hjA, hnotAle]
  · have hAle : P.a ≤ j := by omega
    simp [qPrimCoeffZ, hjA, hAle]
    by_cases hdesc : j - P.a < P.b - 1
    · have hTop : j ≤ P.a + P.b - 2 := by omega
      have hidx : P.b - 1 - (j - P.a) = P.a + P.b - j - 1 := by omega
      simp [hdesc, hTop, hidx]
    · have hTopLt : P.a + P.b - 2 < j := by
        have hApos : 0 < P.a := P.ha_pos
        have hBpos : 0 < P.b := P.hb_pos
        by_cases hb1 : P.b = 1
        · omega
        · have hdesc_le : P.b - 1 ≤ j - P.a := by omega
          omega
      have hnotTop : ¬ j ≤ P.a + P.b - 2 := by omega
      simp [hdesc, hnotTop]

/-- Closed form for the primitive orientation polynomial after clearing
the double root at `1`. -/
lemma qPrimZ_mul_X_sub_one_sq (P : PosPair) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimZ P =
      Polynomial.C (P.a : Int) * Polynomial.X ^ (P.a + P.b) -
        Polynomial.C (((P.a + P.b : Nat) : Int)) * Polynomial.X ^ P.a +
        Polynomial.C (P.b : Int) := by
  have hBpos : 0 < P.b := P.hb_pos
  have hBpred : P.b - 1 + 1 = P.b := by omega
  have hBpredCast : ((P.b - 1 : Nat) : Int) = (P.b : Int) - 1 := by omega
  rw [qPrimZ_eq_triangles]
  calc
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) *
        (Polynomial.C (P.b : Int) * qPrimAscZ P.a +
          Polynomial.C (P.a : Int) * (Polynomial.X ^ P.a * qPrimDescZ (P.b - 1)))
        =
          Polynomial.C (P.b : Int) *
              (((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimAscZ P.a) +
            Polynomial.C (P.a : Int) * Polynomial.X ^ P.a *
              (((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimDescZ (P.b - 1)) := by
            ring
    _ =
          Polynomial.C (P.b : Int) *
              (1 - Polynomial.C (((P.a + 1 : Nat) : Int)) * Polynomial.X ^ P.a +
                Polynomial.C (P.a : Int) * Polynomial.X ^ (P.a + 1)) +
            Polynomial.C (P.a : Int) * Polynomial.X ^ P.a *
              (Polynomial.C (((P.b - 1 : Nat) : Int)) -
                Polynomial.C (((P.b - 1 + 1 : Nat) : Int)) * Polynomial.X +
                Polynomial.X ^ (P.b - 1 + 1)) := by
            rw [qPrimAscZ_closed, qPrimDescZ_closed]
    _ =
      Polynomial.C (P.a : Int) * Polynomial.X ^ (P.a + P.b) -
        Polynomial.C (((P.a + P.b : Nat) : Int)) * Polynomial.X ^ P.a +
        Polynomial.C (P.b : Int) := by
            rw [hBpred, hBpredCast]
            norm_num [Nat.cast_add, Nat.cast_one]
            ring_nf

/-- Closed form for the primitive orientation polynomial using the named
trinomial numerator. -/
lemma qPrimZ_closed_form (P : PosPair) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) * qPrimZ P = qNumeratorZ P := by
  simpa [qNumeratorZ] using qPrimZ_mul_X_sub_one_sq P

end Qab
