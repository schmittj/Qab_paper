import Qab.Packs.GlobalHeight

namespace Qab

/-!
Local packet/state extraction.

The audit recommended not hiding the local p-adic/Kummer work behind a mere
coefficient trichotomy.  The trichotomy is proved arithmetically in
`NormCE.coeff_trichotomy`; the serious local theorem is represented here by
`to_lower_state` and `to_residual_witness`.
-/

/-- Placeholder for a lower-box state record.

Open this structure by adding fields for primitive shapes, scales, extraction
degrees, endpoint coefficients, slope signatures, packet occupancies,
deficient-prime flags, total-radical data, and any row identifiers needed by
certificate files.
-/
structure LowerState where
  rowId : Nat

/-- A lower state encodes the normalized counterexample. -/
axiom Encodes : NormCE → LowerState → Prop

/-- All local p-adic/Kummer predicates consumed by the finite lower searches. -/
axiom AdmissibleLowerState : LowerState → Prop

/-- Reciprocal normalization used to orient the residual one-nonunit branch. -/
axiom ReciprocalNormalize : NormCE → NormCE → Prop

/-- Residual states are deliberately separate from general lower states. -/
structure ResidualState where
  rowId : Nat

/-- The explicit residual envelope after reciprocal normalization. -/
def ResidualEnvelope (ce : NormCE) : Prop :=
  ce.D ≤ residualMax ∧
  ce.Vabs = 1 ∧
  2 ≤ ce.U ∧ ce.U ≤ ce.D ∧
  ce.d ≤ residualDegreeMax

/-- A residual row encodes a reciprocally normalized counterexample. -/
axiom EncodesResidual : NormCE → ResidualState → Prop

/-- Residual finite-state predicates consumed by the residual verifier. -/
axiom AdmissibleResidualState : ResidualState → Prop

/-- Packaged residual witness. -/
structure ResidualWitness (ce : NormCE) where
  ce' : NormCE
  st : ResidualState
  recnorm : ReciprocalNormalize ce ce'
  envelope : ResidualEnvelope ce'
  encodes : EncodesResidual ce' st
  admissible : AdmissibleResidualState st

/-- Local packet theorem pack. -/
structure LocalPacketPack where
  /-- Every lower-box counterexample yields an admissible lower state. -/
  to_lower_state :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.D ≤ lowerMax →
      ∃ st : LowerState, Encodes ce st ∧ AdmissibleLowerState st

  /-- Every residual one-nonunit counterexample yields a normalized residual state. -/
  to_residual_witness :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.OneNonunit → ce.D ≤ residualMax →
      ResidualWitness ce

end Qab
