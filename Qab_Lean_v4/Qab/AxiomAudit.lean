import Qab.CoreProof

/-!
Build-time axiom audit for the conditional assembly theorem.

This guard is intentionally narrow: it should fail if
`package_coprimality_from_packs` accidentally starts depending on broad pack
axioms such as `broad_finite_residual_pack`.  The listed axioms are the current
opaque vocabulary plus Lean's standard classical axioms.
-/

/--
info: 'Qab.package_coprimality_from_packs' depends on axioms: [propext,
 Classical.choice,
 Qab.AdmissibleLowerState,
 Qab.AdmissibleResidualState,
 Qab.Encodes,
 Qab.EncodesResidual,
 Qab.FromShare,
 Qab.ReciprocalNormalize,
 Quot.sound]
-/
#guard_msgs in
#print axioms Qab.package_coprimality_from_packs

