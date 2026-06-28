import Qab.CoreProof
import Qab.Certificates.ResidualTerminalExclusion

/-!
Build-time axiom audit for the conditional assembly theorem.

This guard is intentionally narrow: it should fail if
`package_coprimality_from_packs` accidentally starts depending on broad pack
axioms such as `broad_finite_residual_pack`.  The listed axioms are the current
opaque vocabulary plus Lean's standard classical axioms.

It also audits the generic Phase 2 residual terminal-exclusion theorem.  That
certificate bridge should not depend on any project theorem-pack axioms; the
generated row-set theorem separately depends on the expected `native_decide`
certificate checks.
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

/--
info: 'Qab.Certificates.ResidualTerminalExclusion.reduced_common_factor_dvd_forced_of_rat_dvd' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
-/
#guard_msgs in
#print axioms Qab.Certificates.ResidualTerminalExclusion.reduced_common_factor_dvd_forced_of_rat_dvd

/--
info: 'Qab.Certificates.ResidualTerminalExclusion.ResidualRows.residualTerminalExclusionSet' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Qab.Certificates.ResidualBezout1009.cert0_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert1_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert2_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert3_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert4_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert5_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert6_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.cert7_checks._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualBezout1009.residualBezoutRowsMatch_eq_true._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualZMod1009.allRowsArtifactConsistent_eq_true._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualZMod1009.listedCountsMatchManifest_eq_true._native.native_decide.ax_1_1,
 Qab.Certificates.ResidualZMod1009.listedPairOrientationCoverageComplete_eq_true._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Qab.Certificates.ResidualTerminalExclusion.ResidualRows.residualTerminalExclusionSet
