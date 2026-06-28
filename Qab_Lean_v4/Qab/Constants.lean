import Mathlib.Tactic

namespace Qab

/-!
Numerical cutoffs from the streamlined completion path.

`globalBound` is the explicit height--degree--Mahler bound.
`upperStart` is the first value in the upper unit-normalized range.
`lowerMax` is the complementary lower box.
`largeOneNonunitStart` and `residualMax` split the one-nonunit branch.
`residualDegreeMax` is the safe degree bound in the residual envelope.
-/

abbrev globalBound : Nat := 175394637
abbrev upperStart : Nat := 6816242
abbrev lowerMax : Nat := 6816241
abbrev largeOneNonunitStart : Nat := 16584
abbrev residualMax : Nat := 16583
abbrev residualDegreeMax : Nat := 2601

lemma le_lowerMax_of_not_ge_upperStart {D : Nat} :
    ¬ upperStart ≤ D → D ≤ lowerMax := by
  dsimp [upperStart, lowerMax]
  omega

lemma ge_upperStart_of_not_le_lowerMax {D : Nat} :
    ¬ D ≤ lowerMax → upperStart ≤ D := by
  dsimp [upperStart, lowerMax]
  omega

lemma le_residualMax_of_not_ge_largeOneNonunitStart {D : Nat} :
    ¬ largeOneNonunitStart ≤ D → D ≤ residualMax := by
  dsimp [largeOneNonunitStart, residualMax]
  omega

lemma ge_largeOneNonunitStart_of_not_le_residualMax {D : Nat} :
    ¬ D ≤ residualMax → largeOneNonunitStart ≤ D := by
  dsimp [largeOneNonunitStart, residualMax]
  omega

/-- Audit-friendly alias for the lower/upper boundary cut. -/
lemma ge_6816242_of_not_le_6816241 {D : Nat} :
    ¬ D ≤ lowerMax → upperStart ≤ D :=
  ge_upperStart_of_not_le_lowerMax

/-- Audit-friendly alias for the residual/large-one-nonunit boundary cut. -/
lemma ge_16584_of_not_le_16583 {D : Nat} :
    ¬ D ≤ residualMax → largeOneNonunitStart ≤ D :=
  ge_largeOneNonunitStart_of_not_le_residualMax

end Qab
