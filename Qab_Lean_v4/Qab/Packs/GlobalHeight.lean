import Qab.Packs.Collision

namespace Qab

/-!
Global height and upper-normalization theorem packs.

These are separated so that the height--degree--Mahler bound can later be
opened independently from the upper-range unit-normalization computation.
-/

/-- The explicit global bound `D ≤ 175394637`. -/
structure GlobalHeightPack where
  absolute_bound :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.D ≤ globalBound

/-- The theorem that every counterexample in the upper range is unit-normalized. -/
structure UpperNormalizationPack where
  upper_unit_normalized :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → upperStart ≤ ce.D → ce.UnitCoeff

/-- The exact upper computation after unit normalization. -/
structure UpperRangePack where
  no_upper_unit_counterexample :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.UnitCoeff →
      upperStart ≤ ce.D → ce.D ≤ globalBound → False

end Qab
