import Qab.Certificates.Coverage
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

/-- Which polynomial family a terminal modular-gcd certificate is checking. -/
inductive PolynomialCheckTarget where
  /-- Undivided collision trinomials `H_{m,n}`.  Forced cyclotomic factors must
  be accounted for explicitly, especially the double root at `x = 1`. -/
  | collisionH
  /-- Divided orientation/package polynomial `Q_{a,b}`. -/
  | orientationQ
  /-- Reciprocal package product `Q_{a,b} * Q_{b,a}`. -/
  | packageProduct
  deriving DecidableEq, Repr

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

/-- Schematic coverage certificate for finite searches.

`auditId` may record an external filename/hash for reproducibility, but it is
not a proof.  The proof-relevant part must eventually be typed Lean data such
as intervals, child certificates, and verified exclusion reasons. -/
structure CoverageCert where
  name : String
  targetLo : Nat
  targetHi : Nat
  intervals : List CoverageInterval
  auditId : String

/-- Concrete coverage claim represented by a `CoverageCert`.

`auditId` remains metadata only; the proof-relevant content is the target
interval and the typed interval list. -/
def ChecksCoverageCert (cert : CoverageCert) : Prop :=
  CoversClosedTarget cert.intervals cert.targetLo cert.targetHi

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
