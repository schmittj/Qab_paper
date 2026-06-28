import Qab.Basic

namespace Qab

/-!
Normalized counterexamples.

The audit warning is implemented here: `FromShare` is an opaque constant, not
`True`.  This prevents broad branch-elimination assumptions from becoming
inconsistent on dummy `NormCE` records.
-/

/--
The normalized four-index counterexample state used by the core proof.

The fields `hD`, `norm_gcd`, and `shape_distinct` are included already in
phase 0 so that later theorem-pack openings do not need to change the core
signature.  `d`, `U`, and `Vabs` represent, respectively, the degree and the
absolute endpoint coefficients of the primitive minimal polynomial selected
by `FromShare`.
-/
structure NormCE where
  m : Nat
  n : Nat
  p : Nat
  q : Nat
  hm_pos : 0 < m
  hm_lt  : m < n
  hp_pos : 0 < p
  hp_lt  : p < q
  D : Nat
  hD : D = max (max m n) (max p q)
  norm_gcd : Nat.gcd (Nat.gcd m n) (Nat.gcd p q) = 1
  shape_distinct : ¬ ((m = p ∧ n = q) ∨ (m = q ∧ n = p))
  d : Nat
  U : Nat
  Vabs : Nat
  hd_pos : 0 < d
  hU_pos : 0 < U
  hV_pos : 0 < Vabs

namespace NormCE

/-- Both endpoint coefficients are units. -/
def UnitCoeff (ce : NormCE) : Prop := ce.U = 1 ∧ ce.Vabs = 1

/-- Both endpoint coefficients are nonunits. -/
def BothNonunit (ce : NormCE) : Prop := 2 ≤ ce.U ∧ 2 ≤ ce.Vabs

/-- Exactly one endpoint coefficient is a nonunit. -/
def OneNonunit (ce : NormCE) : Prop :=
  (ce.U = 1 ∧ 2 ≤ ce.Vabs) ∨ (2 ≤ ce.U ∧ ce.Vabs = 1)

/-- The endpoint-coefficient trichotomy is arithmetic, not a p-adic theorem. -/
theorem coeff_trichotomy (ce : NormCE) :
    ce.UnitCoeff ∨ ce.BothNonunit ∨ ce.OneNonunit := by
  have hUpos : 0 < ce.U := ce.hU_pos
  have hVpos : 0 < ce.Vabs := ce.hV_pos
  have hUcases : ce.U = 1 ∨ 2 ≤ ce.U := by
    omega
  have hVcases : ce.Vabs = 1 ∨ 2 ≤ ce.Vabs := by
    omega
  rcases hUcases with hU1 | hU2
  · rcases hVcases with hV1 | hV2
    · exact Or.inl ⟨hU1, hV1⟩
    · exact Or.inr (Or.inr (Or.inl ⟨hU1, hV2⟩))
  · rcases hVcases with hV1 | hV2
    · exact Or.inr (Or.inr (Or.inr ⟨hU2, hV1⟩))
    · exact Or.inr (Or.inl ⟨hU2, hV2⟩)

end NormCE

/--
Opaque selected-collision predicate.  It should eventually be replaced by a
structure containing: selected orientations, an off-unit-circle common root,
primitive minimal polynomial data, height data, and the link to the package
share.
-/
axiom FromShare : PosPair → PosPair → NormCE → Prop

end Qab
