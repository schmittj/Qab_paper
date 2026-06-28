import Qab.Packs.FiniteElimination

namespace Qab

/-!
Core assembly proof.

This file should remain short.  Its purpose is to verify that the theorem-pack
interfaces compose to the desired package-coprimality theorem.
-/

/-- No normalized counterexample can survive the theorem packs. -/
theorem no_normCE_from_packs
    (G : GlobalHeightPack)
    (UN : UpperNormalizationPack)
    (UR : UpperRangePack)
    (L : LocalPacketPack)
    (FL : FiniteLowerPack)
    (FR : FiniteResidualPack)
    {P Q : PosPair} {ce : NormCE}
    (hfs : FromShare P Q ce) : False := by
  have hGlobal : ce.D ≤ globalBound := G.absolute_bound hfs
  by_cases hUpper : upperStart ≤ ce.D
  · have hUnit : ce.UnitCoeff := UN.upper_unit_normalized hfs hUpper
    exact UR.no_upper_unit_counterexample hfs hUnit hUpper hGlobal
  · have hLower : ce.D ≤ lowerMax := le_lowerMax_of_not_ge_upperStart hUpper
    rcases L.to_lower_state hfs hLower with ⟨st, hEnc, hAdm⟩
    rcases ce.coeff_trichotomy with hUnit | hRest
    · exact FL.no_lower_unit hEnc hAdm hLower hUnit
    · rcases hRest with hBoth | hOne
      · exact FL.no_both_nonunit hEnc hAdm hLower hBoth
      · by_cases hLarge : largeOneNonunitStart ≤ ce.D
        · exact FL.no_one_nonunit_large hEnc hAdm hOne hLarge hLower
        · have hResidual : ce.D ≤ residualMax :=
            le_residualMax_of_not_ge_largeOneNonunitStart hLarge
          let reswit := L.to_residual_witness hfs hOne hResidual
          exact FR.no_residual_state
            reswit.recnorm reswit.envelope reswit.encodes reswit.admissible

/-- Conditional package-coprimality theorem from named theorem packs. -/
theorem package_coprimality_from_packs
    (C : CollisionPack)
    (G : GlobalHeightPack)
    (UN : UpperNormalizationPack)
    (UR : UpperRangePack)
    (L : LocalPacketPack)
    (FL : FiniteLowerPack)
    (FR : FiniteResidualPack) :
    ReciprocalPackageCoprimality := by
  intro P Q hP hQ hNotSame hShare
  rcases C.share_to_normCE hP hQ hNotSame hShare with ⟨ce, hfs⟩
  exact no_normCE_from_packs G UN UR L FL FR hfs

end Qab
