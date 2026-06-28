import Qab.Packs.LocalPacket

namespace Qab

/-!
Finite elimination packs.

The lower eliminators consume `Encodes ce st` and `AdmissibleLowerState st`,
not raw `FromShare` alone.  The unit and both-nonunit eliminators also receive
the explicit lower-box hypothesis `ce.D ≤ lowerMax`, even though this is
expected to be encoded in `AdmissibleLowerState`; passing it separately keeps
the trust boundary audit-friendly.

The residual eliminator consumes the explicit reciprocal-normalized residual
envelope and the residual-state predicate.
-/

/-- Unit, both-nonunit, and large one-nonunit lower-box eliminations.

Original manuscript role: lower-box finite branch eliminations after local
packet/Kummer state extraction.  The unit and both-nonunit branches are given
the lower-box bound explicitly for auditability. -/
structure FiniteLowerPack where
  no_lower_unit :
    ∀ {ce : NormCE} {st : LowerState},
      Encodes ce st → AdmissibleLowerState st →
      ce.D ≤ lowerMax → ce.UnitCoeff → False

  no_both_nonunit :
    ∀ {ce : NormCE} {st : LowerState},
      Encodes ce st → AdmissibleLowerState st →
      ce.D ≤ lowerMax → ce.BothNonunit → False

  no_one_nonunit_large :
    ∀ {ce : NormCE} {st : LowerState},
      Encodes ce st → AdmissibleLowerState st → ce.OneNonunit →
      largeOneNonunitStart ≤ ce.D → ce.D ≤ lowerMax → False

/-- Residual one-nonunit elimination after reciprocal normalization.

Original manuscript role: residual finite-state elimination after the envelope
`D ≤ 16583`, `Vabs = 1`, `2 ≤ U ≤ D`, and `d ≤ 2601` has been exposed by
`LocalPacketPack.to_residual_witness`. -/
structure FiniteResidualPack where
  no_residual_state :
    ∀ {ce ce' : NormCE} {st : ResidualState},
      ReciprocalNormalize ce ce' →
      ResidualEnvelope ce' →
      EncodesResidual ce' st →
      AdmissibleResidualState st →
      False

end Qab
