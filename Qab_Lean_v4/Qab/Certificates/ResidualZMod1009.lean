import Qab.Certificates.ZModGcd
import Qab.Constants

namespace Qab

namespace Certificates.ResidualZMod1009

open Certificates.ZModGcd

/-!
Typed residual one-nonunit modular-gcd data for `ZMod 1009`.

Source artifacts:

* `data/qab12/one_nonunit_residual_orientation_pairs.csv`
* `data/qab12/one_nonunit_residual_modular_certificates.csv`

The CSV currently has two residual orientation-pair rows and four orientations
per pair.  This module checks all eight rows against the executable
`collisionH` checker in `Qab.Certificates.ZModGcd`.
-/

structure ResidualPair where
  U : Nat
  r : Nat
  a : Nat
  b : Nat
  n : Nat
  s : Nat
  c : Nat
  f : Nat
  m : Nat
  deriving BEq, DecidableEq, Repr

structure ResidualCertificateRow where
  pairIndex : Nat
  orientation : Nat
  U : Nat
  r : Nat
  a : Nat
  b : Nat
  n : Nat
  s : Nat
  c : Nat
  f : Nat
  m : Nat
  low1 : Nat
  low2 : Nat
  prime : Nat
  gcdDegree : Nat
  deriving BEq, DecidableEq, Repr

namespace ResidualCertificateRow

def pair (row : ResidualCertificateRow) : ResidualPair where
  U := row.U
  r := row.r
  a := row.a
  b := row.b
  n := row.n
  s := row.s
  c := row.c
  f := row.f
  m := row.m

def expectedLow1 (row : ResidualCertificateRow) : Nat :=
  if row.orientation / 2 = 0 then row.a else row.b

def expectedLow2 (row : ResidualCertificateRow) : Nat :=
  if row.orientation % 2 = 0 then row.c else row.f

def toCollisionCertificate (row : ResidualCertificateRow) : CollisionCertificate where
  scale₁ := row.r
  low₁ := row.low1
  total₁ := row.n
  scale₂ := row.s
  low₂ := row.low2
  total₂ := row.m
  prime := row.prime
  target := PolynomialCheckTarget.collisionH
  exactGcdDegree := row.gcdDegree
  forcedCyclotomicDegree := forcedDoubleRootDegree

def matchesPair (pairs : List ResidualPair) (row : ResidualCertificateRow) : Bool :=
  pairs[row.pairIndex]? = some row.pair

def artifactConsistent (pairs : List ResidualPair) (row : ResidualCertificateRow) : Bool :=
  row.matchesPair pairs &&
    row.orientation < 4 &&
    row.a + row.b = row.n &&
    row.c + row.f = row.m &&
    Nat.gcd row.a row.b = 1 &&
    Nat.gcd row.c row.f = 1 &&
    Nat.gcd row.r row.s = 1 &&
    max (row.r * row.n) (row.s * row.m) ≤ residualMax &&
    row.low1 = row.expectedLow1 &&
    row.low2 = row.expectedLow2 &&
    row.prime = modulus &&
    !([row.r, row.a, row.b, row.n, row.s, row.c, row.f, row.m].any
      fun x => x % modulus = 0)

def checks (pairs : List ResidualPair) (row : ResidualCertificateRow) : Bool :=
  row.artifactConsistent pairs && row.toCollisionCertificate.checks

end ResidualCertificateRow

/-- Orientation-pair rows from `one_nonunit_residual_orientation_pairs.csv`. -/
def residualPairs : List ResidualPair :=
  [ { U := 8, r := 3, a := 440, b := 1, n := 441,
      s := 4, c := 3024, f := 1, m := 3025 },
    { U := 32, r := 1, a := 6560, b := 1, n := 6561,
      s := 2, c := 1024, f := 1, m := 1025 } ]

/-- Modular-gcd rows from `one_nonunit_residual_modular_certificates.csv`. -/
def residualCertificateRows : List ResidualCertificateRow :=
  [ { pairIndex := 0, orientation := 0, U := 8,
      r := 3, a := 440, b := 1, n := 441,
      s := 4, c := 3024, f := 1, m := 3025,
      low1 := 440, low2 := 3024, prime := 1009, gcdDegree := 2 },
    { pairIndex := 0, orientation := 1, U := 8,
      r := 3, a := 440, b := 1, n := 441,
      s := 4, c := 3024, f := 1, m := 3025,
      low1 := 440, low2 := 1, prime := 1009, gcdDegree := 2 },
    { pairIndex := 0, orientation := 2, U := 8,
      r := 3, a := 440, b := 1, n := 441,
      s := 4, c := 3024, f := 1, m := 3025,
      low1 := 1, low2 := 3024, prime := 1009, gcdDegree := 2 },
    { pairIndex := 0, orientation := 3, U := 8,
      r := 3, a := 440, b := 1, n := 441,
      s := 4, c := 3024, f := 1, m := 3025,
      low1 := 1, low2 := 1, prime := 1009, gcdDegree := 2 },
    { pairIndex := 1, orientation := 0, U := 32,
      r := 1, a := 6560, b := 1, n := 6561,
      s := 2, c := 1024, f := 1, m := 1025,
      low1 := 6560, low2 := 1024, prime := 1009, gcdDegree := 2 },
    { pairIndex := 1, orientation := 1, U := 32,
      r := 1, a := 6560, b := 1, n := 6561,
      s := 2, c := 1024, f := 1, m := 1025,
      low1 := 6560, low2 := 1, prime := 1009, gcdDegree := 2 },
    { pairIndex := 1, orientation := 2, U := 32,
      r := 1, a := 6560, b := 1, n := 6561,
      s := 2, c := 1024, f := 1, m := 1025,
      low1 := 1, low2 := 1024, prime := 1009, gcdDegree := 2 },
    { pairIndex := 1, orientation := 3, U := 32,
      r := 1, a := 6560, b := 1, n := 6561,
      s := 2, c := 1024, f := 1, m := 1025,
      low1 := 1, low2 := 1, prime := 1009, gcdDegree := 2 } ]

def taskCount (pairIndex orientation : Nat) : Nat :=
  (residualCertificateRows.filter fun row =>
    row.pairIndex = pairIndex && row.orientation = orientation).length

def listedPairOrientationCoverageComplete : Bool :=
  (List.range residualPairs.length).all fun pairIndex =>
    (List.range 4).all fun orientation =>
      taskCount pairIndex orientation = 1

def listedCountsMatchManifest : Bool :=
  residualPairs.length = 2 && residualCertificateRows.length = 8

def allRowsCheck : Bool :=
  residualCertificateRows.all fun row => row.checks residualPairs

/-- All residual `ZMod 1009` certificate rows pass the executable checker. -/
theorem allRowsCheck_eq_true : allRowsCheck = true := by
  native_decide

/-- The typed residual rows cover every listed pair/orientation task exactly once. -/
theorem listedPairOrientationCoverageComplete_eq_true :
    listedPairOrientationCoverageComplete = true := by
  native_decide

/-- The typed residual data has the current manifest-level residual task counts. -/
theorem listedCountsMatchManifest_eq_true : listedCountsMatchManifest = true := by
  native_decide

/-- Combined theorem used by the branch-level build target. -/
theorem residualZMod1009CertificateSetChecks :
    allRowsCheck = true ∧
      listedPairOrientationCoverageComplete = true ∧
      listedCountsMatchManifest = true := by
  exact ⟨allRowsCheck_eq_true, listedPairOrientationCoverageComplete_eq_true,
    listedCountsMatchManifest_eq_true⟩

end Certificates.ResidualZMod1009

end Qab
