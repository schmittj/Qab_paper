import Qab.Certificates.GoodReduction
import Qab.Certificates.ResidualBezout1009

namespace Qab

open Polynomial

namespace Certificates.ResidualTerminalExclusion

open Certificates.CollisionBezout
open Certificates.ZModGcd

local instance modulus_prime : Fact (Nat.Prime modulus) := ⟨by norm_num [modulus]⟩

/-!
Phase 2 terminal exclusion for the current residual rows.

The theorem layer is deliberately conditional on a simple nonforced predicate:
an integer polynomial factor is nonforced if its reduction modulo `1009` does
not divide the forced double root `(X - 1)^2`.  Later package/orientation
integration can prove this predicate for the factors it extracts, while this
module stays independent of Phase 3 residual-state coverage.
-/

/-- A hidden factor whose reduction is not absorbed by the forced double root. -/
def NonforcedMod1009 (h : Polynomial Int) : Prop :=
  ¬ GoodReduction.reduceZMod modulus h ∣
    ((Polynomial.X - 1 : Polynomial F1009) ^ 2)

/-- The forced double root is nonzero over `ZMod 1009`. -/
theorem forcedSquare_ne_zero :
    ((Polynomial.X - 1 : Polynomial F1009) ^ 2) ≠ 0 := by
  change ((Polynomial.X - Polynomial.C (1 : F1009) : Polynomial F1009) ^ 2) ≠ 0
  exact ((Polynomial.monic_X_sub_C (1 : F1009)).pow 2).ne_zero

/-- The forced double root has degree exactly `2` over `ZMod 1009`. -/
theorem forcedSquare_natDegree :
    (((Polynomial.X - 1 : Polynomial F1009) ^ 2).natDegree) = 2 := by
  change (((Polynomial.X - Polynomial.C (1 : F1009) : Polynomial F1009) ^ 2).natDegree) = 2
  rw [(Polynomial.monic_X_sub_C (1 : F1009)).natDegree_pow, Polynomial.natDegree_X_sub_C]

/--
Degree helper for future package integration: if the hidden factor's leading
coefficient survives modulo `1009` and its integer degree is greater than two,
then it is automatically nonforced.
-/
theorem nonforcedMod1009_of_natDegree_gt_two {h : Polynomial Int}
    (hlc : (h.leadingCoeff : F1009) ≠ 0) (hdeg : 2 < h.natDegree) :
    NonforcedMod1009 h := by
  intro hdvd
  have hred_deg : (GoodReduction.reduceZMod modulus h).natDegree = h.natDegree := by
    simpa [GoodReduction.reduceZMod, GoodReduction.reduceInt] using
      (Polynomial.natDegree_map_of_leadingCoeff_ne_zero
        (p := h) (Int.castRingHom F1009) (by simpa using hlc))
  have hle : (GoodReduction.reduceZMod modulus h).natDegree ≤
      (((Polynomial.X - 1 : Polynomial F1009) ^ 2).natDegree) :=
    Polynomial.natDegree_le_of_dvd hdvd forcedSquare_ne_zero
  rw [hred_deg, forcedSquare_natDegree] at hle
  exact (Nat.not_lt_of_ge hle) hdeg

/-- First integer collision target represented by a Bezout certificate. -/
noncomputable def targetZ₁ (cert : CollisionBezoutCertificate) : Polynomial Int :=
  collisionTriZ cert.scale₁ cert.low₁ cert.total₁

/-- Second integer collision target represented by a Bezout certificate. -/
noncomputable def targetZ₂ (cert : CollisionBezoutCertificate) : Polynomial Int :=
  collisionTriZ cert.scale₂ cert.low₂ cert.total₂

theorem reduceZMod_targetZ₁ (cert : CollisionBezoutCertificate) :
    GoodReduction.reduceZMod modulus (targetZ₁ cert) =
      collisionHMod cert.scale₁ cert.low₁ cert.total₁ := by
  rfl

theorem reduceZMod_targetZ₂ (cert : CollisionBezoutCertificate) :
    GoodReduction.reduceZMod modulus (targetZ₂ cert) =
      collisionHMod cert.scale₂ cert.low₂ cert.total₂ := by
  rfl

/--
Integer-divisibility form of terminal exclusion: a common integer factor of
the two collision trinomials reduces to a divisor of the forced double root.
-/
theorem reduced_common_factor_dvd_forced_of_int_dvd
    {cert : CollisionBezoutCertificate} (hcheck : cert.checks)
    {h : Polynomial Int} (hF : h ∣ targetZ₁ cert) (hG : h ∣ targetZ₂ cert) :
    GoodReduction.reduceZMod modulus h ∣
      ((Polynomial.X - 1 : Polynomial F1009) ^ 2) := by
  have hF_mod : GoodReduction.reduceZMod modulus h ∣
      collisionHMod cert.scale₁ cert.low₁ cert.total₁ := by
    simpa [targetZ₁, GoodReduction.reduceZMod, GoodReduction.reduceInt, collisionHMod]
      using GoodReduction.reduceInt_dvd_of_int_dvd (K := F1009) hF
  have hG_mod : GoodReduction.reduceZMod modulus h ∣
      collisionHMod cert.scale₂ cert.low₂ cert.total₂ := by
    simpa [targetZ₂, GoodReduction.reduceZMod, GoodReduction.reduceInt, collisionHMod]
      using GoodReduction.reduceInt_dvd_of_int_dvd (K := F1009) hG
  exact CollisionBezoutCertificate.common_dvd_X_sub_one_sq hcheck hF_mod hG_mod

/--
Rational-divisibility form used by the package polynomial bridge.  The
primitive hypothesis clears denominators by `GoodReduction.int_dvd_of_rat_dvd`;
the semantic Bezout certificate then accounts for the full modular common
divisor.
-/
theorem reduced_common_factor_dvd_forced_of_rat_dvd
    {cert : CollisionBezoutCertificate} (hcheck : cert.checks)
    {h : Polynomial Int} (hh : h.IsPrimitive)
    (hF : h.map (Int.castRingHom Rat) ∣
      (targetZ₁ cert).map (Int.castRingHom Rat))
    (hG : h.map (Int.castRingHom Rat) ∣
      (targetZ₂ cert).map (Int.castRingHom Rat)) :
    GoodReduction.reduceZMod modulus h ∣
      ((Polynomial.X - 1 : Polynomial F1009) ^ 2) := by
  exact reduced_common_factor_dvd_forced_of_int_dvd hcheck
    (GoodReduction.int_dvd_of_rat_dvd hh hF)
    (GoodReduction.int_dvd_of_rat_dvd hh hG)

/--
A residual terminal certificate excludes every primitive rational common factor
whose modulo-`1009` reduction is not part of the forced double root.
-/
def ExcludesNonforcedRatCommonFactor (cert : CollisionBezoutCertificate) : Prop :=
  ∀ {h : Polynomial Int}, h.IsPrimitive → NonforcedMod1009 h →
    h.map (Int.castRingHom Rat) ∣ (targetZ₁ cert).map (Int.castRingHom Rat) →
    h.map (Int.castRingHom Rat) ∣ (targetZ₂ cert).map (Int.castRingHom Rat) →
    False

theorem excludesNonforcedRatCommonFactor_of_checks
    {cert : CollisionBezoutCertificate} (hcheck : cert.checks) :
    ExcludesNonforcedRatCommonFactor cert := by
  intro h hh hnonforced hF hG
  exact hnonforced (reduced_common_factor_dvd_forced_of_rat_dvd hcheck hh hF hG)

namespace ResidualRows

open Certificates.ResidualBezout1009

def residualTerminalCertificates : List CollisionBezoutCertificate :=
  ResidualBezout1009.residualBezoutCertificates

theorem cert0_excludes : ExcludesNonforcedRatCommonFactor cert0 :=
  excludesNonforcedRatCommonFactor_of_checks cert0_checks

theorem cert1_excludes : ExcludesNonforcedRatCommonFactor cert1 :=
  excludesNonforcedRatCommonFactor_of_checks cert1_checks

theorem cert2_excludes : ExcludesNonforcedRatCommonFactor cert2 :=
  excludesNonforcedRatCommonFactor_of_checks cert2_checks

theorem cert3_excludes : ExcludesNonforcedRatCommonFactor cert3 :=
  excludesNonforcedRatCommonFactor_of_checks cert3_checks

theorem cert4_excludes : ExcludesNonforcedRatCommonFactor cert4 :=
  excludesNonforcedRatCommonFactor_of_checks cert4_checks

theorem cert5_excludes : ExcludesNonforcedRatCommonFactor cert5 :=
  excludesNonforcedRatCommonFactor_of_checks cert5_checks

theorem cert6_excludes : ExcludesNonforcedRatCommonFactor cert6 :=
  excludesNonforcedRatCommonFactor_of_checks cert6_checks

theorem cert7_excludes : ExcludesNonforcedRatCommonFactor cert7 :=
  excludesNonforcedRatCommonFactor_of_checks cert7_checks

/--
Artifact-only audit facts needed by the semantic terminal-exclusion path.  This
intentionally avoids the retained dense-gcd replay check.
-/
def ResidualTerminalSemanticAudit : Prop :=
    ResidualBezout1009.residualBezoutRowsMatch = true ∧
      ResidualZMod1009.allRowsArtifactConsistent = true ∧
      ResidualZMod1009.listedPairOrientationCoverageComplete = true ∧
      ResidualZMod1009.listedCountsMatchManifest = true

theorem residualTerminalSemanticAudit : ResidualTerminalSemanticAudit := by
  exact ⟨ResidualBezout1009.residualBezoutRowsMatch_eq_true,
    ResidualZMod1009.allRowsArtifactConsistent_eq_true,
    ResidualZMod1009.listedPairOrientationCoverageComplete_eq_true,
    ResidualZMod1009.listedCountsMatchManifest_eq_true⟩

/-- List-based API for consumers that find a generated residual certificate. -/
theorem excludes_of_mem_residualTerminalCertificates
    {cert : CollisionBezoutCertificate} (hmem : cert ∈ residualTerminalCertificates) :
    ExcludesNonforcedRatCommonFactor cert := by
  rw [residualTerminalCertificates, ResidualBezout1009.residualBezoutCertificates] at hmem
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hmem
  rcases hmem with h0 | hmem
  · subst cert
    exact cert0_excludes
  rcases hmem with h1 | hmem
  · subst cert
    exact cert1_excludes
  rcases hmem with h2 | hmem
  · subst cert
    exact cert2_excludes
  rcases hmem with h3 | hmem
  · subst cert
    exact cert3_excludes
  rcases hmem with h4 | hmem
  · subst cert
    exact cert4_excludes
  rcases hmem with h5 | hmem
  · subst cert
    exact cert5_excludes
  rcases hmem with h6 | h7
  · subst cert
    exact cert6_excludes
  · subst cert
    exact cert7_excludes

/--
All generated residual terminal certificates are matched to the typed residual
rows and exclude nonforced primitive rational common factors.
-/
theorem residualTerminalExclusionSet :
    ResidualTerminalSemanticAudit ∧
      ExcludesNonforcedRatCommonFactor cert0 ∧
      ExcludesNonforcedRatCommonFactor cert1 ∧
      ExcludesNonforcedRatCommonFactor cert2 ∧
      ExcludesNonforcedRatCommonFactor cert3 ∧
      ExcludesNonforcedRatCommonFactor cert4 ∧
      ExcludesNonforcedRatCommonFactor cert5 ∧
      ExcludesNonforcedRatCommonFactor cert6 ∧
      ExcludesNonforcedRatCommonFactor cert7 := by
  exact ⟨residualTerminalSemanticAudit, cert0_excludes, cert1_excludes,
    cert2_excludes, cert3_excludes, cert4_excludes, cert5_excludes,
    cert6_excludes, cert7_excludes⟩

end ResidualRows

end Certificates.ResidualTerminalExclusion

end Qab
