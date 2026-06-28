import Mathlib.Algebra.Field.ZMod
import Mathlib.RingTheory.Polynomial.GaussLemma

/-!
Reusable good-reduction lemmas for modular-gcd certificates.

This module is intentionally project-data-free.  It only speaks about integer
polynomials, their images in `Rat[X]`, and reductions to an arbitrary field
or to `ZMod p`.

The main contract is:

* a hidden common factor is represented by a primitive `h : Int[X]`;
* rational divisibility hypotheses are stated as divisibility after mapping to
  `Rat[X]`;
* no primitivity hypothesis is imposed on the certificate targets `F` and `G`.
  The proof clears their content by passing through `Polynomial.primPart`;
* for degree lower bounds, the good prime must preserve the leading
  coefficient of `h`, either directly or via a surviving target leading
  coefficient.
-/

namespace Qab
namespace GoodReduction

open Polynomial

noncomputable section

/-- Reduction of an integer polynomial along the canonical map to a ring. -/
def reduceInt (K : Type*) [Ring K] (F : Polynomial Int) : Polynomial K :=
  F.map (Int.castRingHom K)

/-- The modular gcd target for two reduced integer polynomials over a field. -/
def modularGCD (K : Type*) [Field K] [DecidableEq K]
    (F G : Polynomial Int) : Polynomial K :=
  gcd (reduceInt K F) (reduceInt K G)

/--
Gauss-style denominator clearing for the certificate shape used here.

If `h` is primitive over `Int` and divides an integer polynomial after mapping
to `Rat[X]`, then it already divides the integer polynomial.  The target
polynomial need not be primitive; for nonzero targets the proof removes the
content using `primPart`, and the zero target is immediate.
-/
theorem int_dvd_of_rat_dvd {h F : Polynomial Int} (hh : h.IsPrimitive)
    (hdiv : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat)) :
    h ∣ F := by
  by_cases hF : F = 0
  · rw [hF]
    exact dvd_zero h
  · have hcontent_ne_int : F.content ≠ 0 := by
      exact mt Polynomial.content_eq_zero_iff.mp hF
    have hcontent_ne_rat : ((F.content : Int) : Rat) ≠ 0 := by
      exact_mod_cast hcontent_ne_int
    have hdiv_primPart :
        h.map (Int.castRingHom Rat) ∣ F.primPart.map (Int.castRingHom Rat) := by
      rw [F.eq_C_content_mul_primPart, Polynomial.map_mul, Polynomial.map_C] at hdiv
      exact (Polynomial.dvd_C_mul
        (p := h.map (Int.castRingHom Rat))
        (q := F.primPart.map (Int.castRingHom Rat))
        hcontent_ne_rat).mp hdiv
    have hdiv_int : h ∣ F.primPart :=
      (Polynomial.IsPrimitive.Int.dvd_iff_map_cast_dvd_map_cast
        h F.primPart hh F.isPrimitive_primPart).mpr hdiv_primPart
    exact hdiv_int.trans
      ⟨Polynomial.C F.content, by
        rw [mul_comm, ← F.eq_C_content_mul_primPart]⟩

/-- Divisibility survives reduction along the canonical map from `Int`. -/
theorem reduceInt_dvd_of_int_dvd {K : Type*} [Ring K]
    {h F : Polynomial Int} (hF : h ∣ F) :
    reduceInt K h ∣ reduceInt K F := by
  rcases hF with ⟨A, hA⟩
  exact ⟨reduceInt K A, by
    simp [reduceInt, hA, Polynomial.map_mul]⟩

/--
If an integer factor divides both integer targets, its reduction divides the
modular gcd target.  This is the primitive reusable core; the rational
divisibility versions below only add the Gauss-clearing step.
-/
theorem reduceInt_dvd_modularGCD_of_int_dvd {K : Type*} [Field K] [DecidableEq K]
    {h F G : Polynomial Int} (hF : h ∣ F) (hG : h ∣ G) :
    reduceInt K h ∣ modularGCD K F G :=
  dvd_gcd (reduceInt_dvd_of_int_dvd (K := K) hF)
    (reduceInt_dvd_of_int_dvd (K := K) hG)

/--
The reusable good-reduction divisibility statement.

If a primitive integer polynomial `h` divides both `F` and `G` over `Rat[X]`,
then every field reduction of `h` divides the gcd of the corresponding
reductions of `F` and `G`.  This part has no good-prime hypothesis: bad primes
may collapse `h`, but divisibility still survives.
-/
theorem reduceInt_dvd_modularGCD {K : Type*} [Field K] [DecidableEq K]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat)) :
    reduceInt K h ∣ modularGCD K F G := by
  have hF_int : h ∣ F := int_dvd_of_rat_dvd hh hF
  have hG_int : h ∣ G := int_dvd_of_rat_dvd hh hG
  exact reduceInt_dvd_modularGCD_of_int_dvd (K := K) hF_int hG_int

/--
A nonzero reduced leading coefficient makes the reduced polynomial nonzero.
Certificate checkers often prove this directly from a sparse top coefficient.
-/
theorem reduceInt_ne_zero_of_leadingCoeff_ne_zero {K : Type*} [Ring K]
    {F : Polynomial Int} (hF_lc : (Int.castRingHom K) F.leadingCoeff ≠ 0) :
    reduceInt K F ≠ 0 := by
  intro hzero
  apply hF_lc
  change (Int.castRingHom K) (F.coeff F.natDegree) = 0
  rw [← coeff_map]
  change (reduceInt K F).coeff F.natDegree = 0
  rw [hzero]
  simp

/--
If `h ∣ F` over `Int[X]` and the leading coefficient of `F` survives in the
target ring, then the leading coefficient of `h` survives too.
-/
theorem leadingCoeff_map_ne_zero_of_dvd_of_target_lc_ne_zero
    {K : Type*} [Ring K] {h F : Polynomial Int}
    (hF : h ∣ F) (hF_lc : (Int.castRingHom K) F.leadingCoeff ≠ 0) :
    (Int.castRingHom K) h.leadingCoeff ≠ 0 := by
  intro hh_lc
  rcases Polynomial.leadingCoeff_dvd_leadingCoeff hF with ⟨c, hc⟩
  apply hF_lc
  rw [hc, map_mul, hh_lc, zero_mul]

theorem modularGCD_ne_zero_of_left {K : Type*} [Field K] [DecidableEq K]
    {F G : Polynomial Int} (hF : reduceInt K F ≠ 0) :
    modularGCD K F G ≠ 0 := by
  simpa [modularGCD] using
    (gcd_ne_zero_of_left (a := reduceInt K F) (b := reduceInt K G) hF)

theorem modularGCD_ne_zero_of_right {K : Type*} [Field K] [DecidableEq K]
    {F G : Polynomial Int} (hG : reduceInt K G ≠ 0) :
    modularGCD K F G ≠ 0 := by
  simpa [modularGCD] using
    (gcd_ne_zero_of_right (a := reduceInt K F) (b := reduceInt K G) hG)

/--
Degree lower bound form used by modular-gcd certificates.

The extra good-reduction hypotheses are exactly those needed for a degree
obstruction:

* the leading coefficient of `h` survives in the target field, so
  `reduceInt K h` has the same degree as `h`;
* at least one of `F` or `G` has nonzero reduction, so the gcd target is not
  the zero polynomial.
-/
theorem natDegree_le_modularGCD_of_rat_dvd {K : Type*} [Field K] [DecidableEq K]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (h_lc : (Int.castRingHom K) h.leadingCoeff ≠ 0)
    (h_target_ne : reduceInt K F ≠ 0 ∨ reduceInt K G ≠ 0) :
    h.natDegree ≤ (modularGCD K F G).natDegree := by
  have h_dvd : reduceInt K h ∣ modularGCD K F G :=
    reduceInt_dvd_modularGCD (K := K) hh hF hG
  have h_gcd_ne : modularGCD K F G ≠ 0 := by
    rcases h_target_ne with hF_ne | hG_ne
    · exact modularGCD_ne_zero_of_left (K := K) hF_ne
    · exact modularGCD_ne_zero_of_right (K := K) hG_ne
  have h_degree :
      (reduceInt K h).natDegree = h.natDegree := by
    simpa [reduceInt] using
      (Polynomial.natDegree_map_of_leadingCoeff_ne_zero
        (p := h) (Int.castRingHom K) h_lc)
  calc
    h.natDegree = (reduceInt K h).natDegree := h_degree.symm
    _ ≤ (modularGCD K F G).natDegree :=
      Polynomial.natDegree_le_of_dvd h_dvd h_gcd_ne

/--
Certificate-friendly left-target variant.  It derives the hidden factor's
leading-coefficient hypothesis and the gcd target nonvanishing from the single
check that `F.leadingCoeff` survives reduction.
-/
theorem natDegree_le_modularGCD_of_rat_dvd_of_left_lc
    {K : Type*} [Field K] [DecidableEq K]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hF_lc : (Int.castRingHom K) F.leadingCoeff ≠ 0) :
    h.natDegree ≤ (modularGCD K F G).natDegree := by
  have hF_int : h ∣ F := int_dvd_of_rat_dvd hh hF
  exact natDegree_le_modularGCD_of_rat_dvd (K := K) hh hF hG
    (leadingCoeff_map_ne_zero_of_dvd_of_target_lc_ne_zero
      (K := K) hF_int hF_lc)
    (Or.inl (reduceInt_ne_zero_of_leadingCoeff_ne_zero
      (K := K) hF_lc))

/--
Certificate-friendly right-target variant.  It is the same lower bound as
`natDegree_le_modularGCD_of_rat_dvd_of_left_lc`, using `G.leadingCoeff`.
-/
theorem natDegree_le_modularGCD_of_rat_dvd_of_right_lc
    {K : Type*} [Field K] [DecidableEq K]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hG_lc : (Int.castRingHom K) G.leadingCoeff ≠ 0) :
    h.natDegree ≤ (modularGCD K F G).natDegree := by
  have hG_int : h ∣ G := int_dvd_of_rat_dvd hh hG
  exact natDegree_le_modularGCD_of_rat_dvd (K := K) hh hF hG
    (leadingCoeff_map_ne_zero_of_dvd_of_target_lc_ne_zero
      (K := K) hG_int hG_lc)
    (Or.inr (reduceInt_ne_zero_of_leadingCoeff_ne_zero
      (K := K) hG_lc))

/--
Contrapositive-friendly positive-degree form: a nonconstant rational common
factor whose leading coefficient survives reduction forces the modular gcd
target to have positive degree.
-/
theorem modularGCD_natDegree_pos_of_rat_common_factor {K : Type*}
    [Field K] [DecidableEq K] {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (h_lc : (Int.castRingHom K) h.leadingCoeff ≠ 0)
    (h_target_ne : reduceInt K F ≠ 0 ∨ reduceInt K G ≠ 0) :
    0 < (modularGCD K F G).natDegree :=
  h_pos.trans_le
    (natDegree_le_modularGCD_of_rat_dvd
      (K := K) hh hF hG h_lc h_target_ne)

theorem modularGCD_natDegree_pos_of_rat_common_factor_of_left_lc
    {K : Type*} [Field K] [DecidableEq K] {h F G : Polynomial Int}
    (hh : h.IsPrimitive) (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hF_lc : (Int.castRingHom K) F.leadingCoeff ≠ 0) :
    0 < (modularGCD K F G).natDegree :=
  h_pos.trans_le
    (natDegree_le_modularGCD_of_rat_dvd_of_left_lc
      (K := K) hh hF hG hF_lc)

theorem modularGCD_natDegree_pos_of_rat_common_factor_of_right_lc
    {K : Type*} [Field K] [DecidableEq K] {h F G : Polynomial Int}
    (hh : h.IsPrimitive) (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hG_lc : (Int.castRingHom K) G.leadingCoeff ≠ 0) :
    0 < (modularGCD K F G).natDegree :=
  h_pos.trans_le
    (natDegree_le_modularGCD_of_rat_dvd_of_right_lc
      (K := K) hh hF hG hG_lc)

/-- Integer-polynomial reduction modulo `p`. -/
def reduceZMod (p : Nat) (F : Polynomial Int) : Polynomial (ZMod p) :=
  reduceInt (ZMod p) F

/-- The modular gcd target over `ZMod p`, for prime `p`. -/
def modularGCDZMod (p : Nat) [Fact p.Prime]
    (F G : Polynomial Int) : Polynomial (ZMod p) :=
  modularGCD (ZMod p) F G

/-- `ZMod p` specialization of `reduceInt_dvd_modularGCD`. -/
theorem reduceZMod_dvd_modularGCDZMod {p : Nat} [Fact p.Prime]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat)) :
    reduceZMod p h ∣ modularGCDZMod p F G := by
  change reduceInt (ZMod p) h ∣ modularGCD (ZMod p) F G
  exact reduceInt_dvd_modularGCD (K := ZMod p) hh hF hG

/-- `ZMod p` specialization of `reduceInt_dvd_modularGCD_of_int_dvd`. -/
theorem reduceZMod_dvd_modularGCDZMod_of_int_dvd {p : Nat} [Fact p.Prime]
    {h F G : Polynomial Int} (hF : h ∣ F) (hG : h ∣ G) :
    reduceZMod p h ∣ modularGCDZMod p F G := by
  change reduceInt (ZMod p) h ∣ modularGCD (ZMod p) F G
  exact reduceInt_dvd_modularGCD_of_int_dvd (K := ZMod p) hF hG

/-- `ZMod p` specialization of the degree lower bound. -/
theorem natDegree_le_modularGCDZMod_of_rat_dvd {p : Nat} [Fact p.Prime]
    {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (h_lc : (h.leadingCoeff : ZMod p) ≠ 0)
    (h_target_ne : reduceZMod p F ≠ 0 ∨ reduceZMod p G ≠ 0) :
    h.natDegree ≤ (modularGCDZMod p F G).natDegree := by
  change h.natDegree ≤ (modularGCD (ZMod p) F G).natDegree
  exact natDegree_le_modularGCD_of_rat_dvd
    (K := ZMod p) hh hF hG (by simpa using h_lc) h_target_ne

/-- `ZMod p` specialization using the left target's leading coefficient. -/
theorem natDegree_le_modularGCDZMod_of_rat_dvd_of_left_lc
    {p : Nat} [Fact p.Prime] {h F G : Polynomial Int}
    (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hF_lc : (F.leadingCoeff : ZMod p) ≠ 0) :
    h.natDegree ≤ (modularGCDZMod p F G).natDegree := by
  change h.natDegree ≤ (modularGCD (ZMod p) F G).natDegree
  exact natDegree_le_modularGCD_of_rat_dvd_of_left_lc
    (K := ZMod p) hh hF hG (by simpa using hF_lc)

/-- `ZMod p` specialization using the right target's leading coefficient. -/
theorem natDegree_le_modularGCDZMod_of_rat_dvd_of_right_lc
    {p : Nat} [Fact p.Prime] {h F G : Polynomial Int}
    (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hG_lc : (G.leadingCoeff : ZMod p) ≠ 0) :
    h.natDegree ≤ (modularGCDZMod p F G).natDegree := by
  change h.natDegree ≤ (modularGCD (ZMod p) F G).natDegree
  exact natDegree_le_modularGCD_of_rat_dvd_of_right_lc
    (K := ZMod p) hh hF hG (by simpa using hG_lc)

/-- Positive-degree `ZMod p` specialization for exact-gcd-degree certificates. -/
theorem modularGCDZMod_natDegree_pos_of_rat_common_factor
    {p : Nat} [Fact p.Prime] {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (h_lc : (h.leadingCoeff : ZMod p) ≠ 0)
    (h_target_ne : reduceZMod p F ≠ 0 ∨ reduceZMod p G ≠ 0) :
    0 < (modularGCDZMod p F G).natDegree := by
  change 0 < (modularGCD (ZMod p) F G).natDegree
  exact modularGCD_natDegree_pos_of_rat_common_factor
    (K := ZMod p) hh h_pos hF hG (by simpa using h_lc) h_target_ne

theorem modularGCDZMod_natDegree_pos_of_rat_common_factor_of_left_lc
    {p : Nat} [Fact p.Prime] {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hF_lc : (F.leadingCoeff : ZMod p) ≠ 0) :
    0 < (modularGCDZMod p F G).natDegree := by
  change 0 < (modularGCD (ZMod p) F G).natDegree
  exact modularGCD_natDegree_pos_of_rat_common_factor_of_left_lc
    (K := ZMod p) hh h_pos hF hG (by simpa using hF_lc)

theorem modularGCDZMod_natDegree_pos_of_rat_common_factor_of_right_lc
    {p : Nat} [Fact p.Prime] {h F G : Polynomial Int} (hh : h.IsPrimitive)
    (h_pos : 0 < h.natDegree)
    (hF : h.map (Int.castRingHom Rat) ∣ F.map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣ G.map (Int.castRingHom Rat))
    (hG_lc : (G.leadingCoeff : ZMod p) ≠ 0) :
    0 < (modularGCDZMod p F G).natDegree := by
  change 0 < (modularGCD (ZMod p) F G).natDegree
  exact modularGCD_natDegree_pos_of_rat_common_factor_of_right_lc
    (K := ZMod p) hh h_pos hF hG (by simpa using hG_lc)

end

end GoodReduction
end Qab
