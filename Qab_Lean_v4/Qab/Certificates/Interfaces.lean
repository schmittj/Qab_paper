import Qab.Certificates.Targets
import Qab.Packs.LocalPacket

namespace Qab

/-!
Preliminary certificate interfaces.

This module deliberately does **not** import `Qab.CoreProof`; finite-elimination
proofs will eventually import certificate interfaces, and importing the core
assembly theorem here would create a dependency-cycle trap.

These structures are still schematic, but v4 makes the intended trust boundary
more explicit than v3:
* terminal rows have a `WellFormed` predicate;
* modular-gcd certificates have an explicit polynomial target;
* `exactGcdDegree` is named as an exact certificate claim, not an expectation;
* identifiers such as `auditId`, where present, are metadata only and are not
  Lean certificates.
-/

/-- A terminal package-orientation row from a finite search. -/
structure TerminalRow where
  rowId : Nat
  m : Nat
  n : Nat
  p : Nat
  q : Nat
  orientationId : Nat

namespace TerminalRow

/-- Minimal well-formedness for terminal rows.  Later versions may replace this
by a row structure carrying these proofs as fields. -/
def WellFormed (row : TerminalRow) : Prop :=
  0 < row.m ∧ row.m < row.n ∧ 0 < row.p ∧ row.p < row.q

end TerminalRow

/-- A typed interval used by coverage certificates.

This is intentionally modest.  Phase 2 should replace broad coverage axioms by
generated Lean terms built out of intervals, child-coverage proofs, and exact
integer exclusions. -/
structure CoverageInterval where
  lo : Nat
  hi : Nat

/-- Schematic coverage certificate for finite searches.

`auditId` may record an external filename/hash for reproducibility, but it is
not a proof.  The proof-relevant part must eventually be typed Lean data such
as intervals, child certificates, and verified exclusion reasons. -/
structure CoverageCert where
  name : String
  intervals : List CoverageInterval
  auditId : String

axiom ChecksCoverageCert : CoverageCert → Prop

/-- Schematic modular-gcd certificate attached to a terminal row.

The eventual concrete checker should include:
* primality of `prime`;
* explicit reduced polynomials or reproducible constructors;
* good-reduction hypotheses, including leading coefficient and content checks;
* a Bezout or Euclidean certificate for the claimed gcd degree;
* an accounting of forced cyclotomic factors, especially the double root at
  `x = 1` when the target is `PolynomialCheckTarget.collisionH`.
-/
structure ModGcdCert (row : TerminalRow) where
  prime : Nat
  target : PolynomialCheckTarget
  exactGcdDegree : Nat
  forcedCyclotomicDegree : Nat
  row_wellformed : row.WellFormed
  auditId : String

axiom ChecksModGcdCert : (row : TerminalRow) → ModGcdCert row → Prop

/-- A row is excluded if the verified modular gcd has no noncyclotomic room. -/
def ModGcdExcludes (row : TerminalRow) (cert : ModGcdCert row) : Prop :=
  ChecksModGcdCert row cert ∧ cert.exactGcdDegree ≤ cert.forcedCyclotomicDegree

end Qab
