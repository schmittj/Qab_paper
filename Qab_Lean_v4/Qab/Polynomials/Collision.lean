import Qab.Polynomials.Orientation

namespace Qab

open Polynomial

/-!
Normalized collision trinomials.

The residual modular-gcd verifier checks the orientation-level trinomials

`low * X^(scale * total) - total * X^(scale * low) + (total - low)`.

For `total = a + b` and `low = a`, this is exactly
`expand scale (qNumeratorZ ⟨a,b⟩)`.  It is the numerator target used before
dividing by the forced cyclotomic square, not the reciprocal package product.
-/

/-- The scale-normalized collision trinomial used by the residual verifier. -/
noncomputable def collisionTriZ (scale low total : Nat) : Polynomial Int :=
  Polynomial.C (low : Int) * Polynomial.X ^ (scale * total) -
    Polynomial.C (total : Int) * Polynomial.X ^ (scale * low) +
    Polynomial.C ((total - low : Nat) : Int)

/-- The orientation quotient whose forced numerator is `collisionTriZ`. -/
noncomputable def collisionQuotZ (scale : Nat) (P : PosPair) : Polynomial Int :=
  Polynomial.expand Int scale (qPrimZ P)

lemma collisionTriZ_eq_expand_qNumeratorZ (scale : Nat) (P : PosPair) :
    collisionTriZ scale P.a (P.a + P.b) =
      Polynomial.expand Int scale (qNumeratorZ P) := by
  have hpow_total :
      (Polynomial.X : Polynomial Int) ^ (scale * (P.a + P.b)) =
        (Polynomial.X ^ scale : Polynomial Int) ^ (P.a + P.b) := by
    rw [pow_mul]
  have hpow_low :
      (Polynomial.X : Polynomial Int) ^ (scale * P.a) =
        (Polynomial.X ^ scale : Polynomial Int) ^ P.a := by
    rw [pow_mul]
  simp [collisionTriZ, qNumeratorZ, hpow_total, hpow_low]

lemma collisionTriZ_natDegree_of_low_lt_total
    {scale low total : Nat} (hlo : 0 < low) (hlt : low < total) :
    (collisionTriZ scale low total).natDegree = scale * total := by
  let P : PosPair :=
    { a := low
      b := total - low
      ha_pos := hlo
      hb_pos := Nat.sub_pos_of_lt hlt }
  have hsum : P.a + P.b = total := by
    dsimp [P]
    omega
  have htri :
      collisionTriZ scale low total =
        Polynomial.expand Int scale (qNumeratorZ P) := by
    simpa [P, hsum] using collisionTriZ_eq_expand_qNumeratorZ scale P
  calc
    (collisionTriZ scale low total).natDegree
        = (Polynomial.expand Int scale (qNumeratorZ P)).natDegree := by
          rw [htri]
    _ = (qNumeratorZ P).natDegree * scale := by
          rw [natDegree_expand]
    _ = total * scale := by
          rw [qNumeratorZ_natDegree, hsum]
    _ = scale * total := by
          rw [Nat.mul_comm]

lemma collisionTriZ_leadingCoeff_of_low_lt_total
    {scale low total : Nat} (hscale : 0 < scale) (hlo : 0 < low)
    (hlt : low < total) :
    (collisionTriZ scale low total).leadingCoeff = (low : Int) := by
  let P : PosPair :=
    { a := low
      b := total - low
      ha_pos := hlo
      hb_pos := Nat.sub_pos_of_lt hlt }
  have hsum : P.a + P.b = total := by
    dsimp [P]
    omega
  have htri :
      collisionTriZ scale low total =
        Polynomial.expand Int scale (qNumeratorZ P) := by
    simpa [P, hsum] using collisionTriZ_eq_expand_qNumeratorZ scale P
  rw [htri, leadingCoeff_expand hscale, qNumeratorZ_leadingCoeff]

lemma collisionTriZ_ne_zero_of_low_lt_total
    {scale low total : Nat} (hscale : 0 < scale) (hlo : 0 < low)
    (hlt : low < total) :
    collisionTriZ scale low total ≠ 0 := by
  intro hzero
  have hlead :=
    collisionTriZ_leadingCoeff_of_low_lt_total
      (scale := scale) (low := low) (total := total) hscale hlo hlt
  have hlow_ne : (low : Int) ≠ 0 := by
    exact_mod_cast Nat.ne_of_gt hlo
  have hzero_lc : (0 : Int) = low := by
    simpa [hzero] using hlead
  exact hlow_ne hzero_lc.symm

lemma collisionQuotZ_closed_form (scale : Nat) (P : PosPair) :
    ((Polynomial.X ^ scale - 1 : Polynomial Int) ^ 2) *
        collisionQuotZ scale P =
      collisionTriZ scale P.a (P.a + P.b) := by
  rw [collisionQuotZ, collisionTriZ_eq_expand_qNumeratorZ]
  rw [← qPrimZ_closed_form P]
  simp only [map_mul, map_pow, map_sub, expand_X, map_one]

lemma collisionTriZ_cyclotomic_sq_dvd (scale : Nat) (P : PosPair) :
    ((Polynomial.X ^ scale - 1 : Polynomial Int) ^ 2) ∣
      collisionTriZ scale P.a (P.a + P.b) :=
  ⟨collisionQuotZ scale P, (collisionQuotZ_closed_form scale P).symm⟩

/--
Residual rows have coprime scales, so the common forced factor is the square
at `X = 1`.  This lemma records the easy individual divisibility
`(X - 1)^2 ∣ collisionTriZ ...`.
-/
lemma collisionTriZ_X_sub_one_sq_dvd (scale : Nat) (P : PosPair) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) ∣
      collisionTriZ scale P.a (P.a + P.b) := by
  have hX : (Polynomial.X - 1 : Polynomial Int) ∣ Polynomial.X ^ scale - 1 := by
    have h := Polynomial.X_sub_C_dvd_sub_C_eval
      (p := (Polynomial.X ^ scale : Polynomial Int)) (a := (1 : Int))
    simpa using h
  exact (pow_dvd_pow_of_dvd hX 2).trans
    (collisionTriZ_cyclotomic_sq_dvd scale P)

/-- Version of `collisionTriZ_X_sub_one_sq_dvd` expressed only with
`0 < low` and `low < total`. -/
lemma collisionTriZ_X_sub_one_sq_dvd_of_low_lt_total
    {scale low total : Nat} (hlo : 0 < low) (hlt : low < total) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) ∣
      collisionTriZ scale low total := by
  let P : PosPair :=
    { a := low
      b := total - low
      ha_pos := hlo
      hb_pos := Nat.sub_pos_of_lt hlt }
  have hsum : P.a + P.b = total := by
    dsimp [P]
    omega
  simpa [P, hsum] using collisionTriZ_X_sub_one_sq_dvd scale P

end Qab
