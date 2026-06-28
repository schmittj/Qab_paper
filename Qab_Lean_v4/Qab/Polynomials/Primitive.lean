import Mathlib.Algebra.Polynomial.Coeff
import Qab.Basic

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

/-- Primitive orientation polynomial mapped to `ℚ[x]`. -/
noncomputable def qPrimQ (P : PosPair) : Polynomial Rat :=
  (qPrimZ P).map (Int.castRingHom Rat)

end Qab
