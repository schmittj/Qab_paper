import Qab.Certificates.Interfaces
import Qab.Polynomials.Collision
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

namespace Qab

open Polynomial

namespace Certificates.ZModGcd

/-!
A small executable modular-gcd checker for collision trinomials.

The checker uses dense coefficient lists over the prime field with 1009
elements.  Its target constructor is the same trinomial as
`Qab.Polynomials.Collision.collisionTriZ`, reduced modulo 1009.
-/

/-- The Phase 2 residual checker currently uses the prime 1009. -/
def modulus : Nat := 1009

/-- Coefficient field used by the mathematical target statements. -/
abbrev F1009 := ZMod modulus

local instance modulus_prime : Fact (Nat.Prime modulus) := ⟨by norm_num [modulus]⟩

/-- The collision trinomial reduced modulo 1009 as a Mathlib polynomial. -/
noncomputable def collisionHMod (scale low total : Nat) : Polynomial F1009 :=
  (collisionTriZ scale low total).map (Int.castRingHom F1009)

/-- The mapped target is the sparse trinomial used by the executable checker. -/
lemma collisionHMod_eq_sparse (scale low total : Nat) :
    collisionHMod scale low total =
      Polynomial.C (low : F1009) * Polynomial.X ^ (scale * total) -
        Polynomial.C (total : F1009) * Polynomial.X ^ (scale * low) +
        Polynomial.C ((total - low : Nat) : F1009) := by
  simp [collisionHMod, collisionTriZ]

/-- Version of the shared forced-factor lemma expressed only with `low < total`. -/
lemma collisionTriZ_X_sub_one_sq_dvd_of_low_lt_total
    {scale low total : Nat} (hlo : 0 < low) (hlt : low < total) :
    ((Polynomial.X - 1 : Polynomial Int) ^ 2) ∣
      collisionTriZ scale low total := by
  let P : PosPair :=
    { a := low
      b := total - low
      ha_pos := hlo
      hb_pos := Nat.sub_pos_of_lt hlt }
  have hsum : P.a + P.b = total := by
    dsimp [P]
    omega
  simpa [P, hsum] using collisionTriZ_X_sub_one_sq_dvd scale P

/--
The forced double root at `X = 1` survives reduction modulo 1009.

Residual rows have coprime scales, so this degree-2 factor is the common
forced factor that must be subtracted from the undivided collision gcd.
-/
lemma collisionHMod_X_sub_one_sq_dvd_of_low_lt_total
    {scale low total : Nat} (hlo : 0 < low) (hlt : low < total) :
    ((Polynomial.X - 1 : Polynomial F1009) ^ 2) ∣
      collisionHMod scale low total := by
  rcases collisionTriZ_X_sub_one_sq_dvd_of_low_lt_total
    (scale := scale) (low := low) (total := total) hlo hlt with ⟨q, hq⟩
  refine ⟨q.map (Int.castRingHom F1009), ?_⟩
  simpa [collisionHMod] using
    congrArg (fun f : Polynomial Int => f.map (Int.castRingHom F1009)) hq

/-- The residual undivided collision target always has a forced degree-2 part. -/
def forcedDoubleRootDegree : Nat := 2

def modReduce (a : Nat) : Nat := a % modulus

def modAdd (a b : Nat) : Nat := (a + b) % modulus

def modNeg (a : Nat) : Nat := (modulus - a % modulus) % modulus

def modSub (a b : Nat) : Nat := (a + modNeg b) % modulus

def modMul (a b : Nat) : Nat := (a * b) % modulus

def invMod (a : Nat) : Nat :=
  ((List.range modulus).find? fun b => (a % modulus * b) % modulus = 1).getD 0

def trim (f : List Nat) : List Nat :=
  match (f.reverse.dropWhile fun a => a = 0).reverse with
  | [] => [0]
  | g => g

def lastD : List Nat → Nat
  | [] => 0
  | [a] => a
  | _ :: rest => lastD rest

def degree (f : List Nat) : Nat := (trim f).length - 1

def addCoeff : List Nat → Nat → Nat → List Nat
  | [], 0, c => [modReduce c]
  | [], i + 1, c => 0 :: addCoeff [] i c
  | a :: rest, 0, c => modAdd a c :: rest
  | a :: rest, i + 1, c => a :: addCoeff rest i c

def subScaledPrefix : List Nat → Nat → List Nat → List Nat
  | f, _, [] => f
  | [], scale, b :: rest => modNeg (modMul scale b) :: subScaledPrefix [] scale rest
  | a :: f, scale, b :: rest =>
      modSub a (modMul scale b) :: subScaledPrefix f scale rest

def subScaledAt : List Nat → Nat → Nat → List Nat → List Nat
  | f, 0, scale, g => subScaledPrefix f scale g
  | [], shift + 1, scale, g => 0 :: subScaledAt [] shift scale g
  | a :: f, shift + 1, scale, g => a :: subScaledAt f shift scale g

def polyModFuel : Nat → List Nat → List Nat → List Nat
  | 0, f, _ => trim f
  | fuel + 1, f, g =>
      let f := trim f
      let g := trim g
      if g = [0] then
        f
      else if f = [0] then
        f
      else if f.length < g.length then
        f
      else
        let scale := modMul (lastD f) (invMod (lastD g))
        let shift := f.length - g.length
        polyModFuel fuel (trim (subScaledAt f shift scale g)) g

def polyMod (f g : List Nat) : List Nat :=
  polyModFuel (trim f).length f g

def polyGcdFuel : Nat → List Nat → List Nat → List Nat
  | 0, f, _ => trim f
  | fuel + 1, f, g =>
      let f := trim f
      let g := trim g
      if g = [0] then
        f
      else
        polyGcdFuel fuel g (polyMod f g)

def polyGcd (f g : List Nat) : List Nat :=
  polyGcdFuel ((trim f).length + (trim g).length + 1) f g

/-- Dense coefficient list for `collisionTriZ scale low total` modulo 1009. -/
def collisionDense (scale low total : Nat) : List Nat :=
  trim <|
    addCoeff
      (addCoeff
        (addCoeff [] (scale * total) low)
        (scale * low) (modNeg total))
      0 (total - low)

def collisionGcdDegree
    (scale₁ low₁ total₁ scale₂ low₂ total₂ : Nat) : Nat :=
  degree <| polyGcd
    (collisionDense scale₁ low₁ total₁)
    (collisionDense scale₂ low₂ total₂)

/-- A row-level executable collision-gcd task over `ZMod 1009`. -/
structure CollisionCertificate where
  scale₁ : Nat
  low₁ : Nat
  total₁ : Nat
  scale₂ : Nat
  low₂ : Nat
  total₂ : Nat
  prime : Nat
  target : PolynomialCheckTarget
  exactGcdDegree : Nat
  forcedCyclotomicDegree : Nat
  deriving DecidableEq, Repr

namespace CollisionCertificate

def wellFormed (cert : CollisionCertificate) : Bool :=
  cert.prime = modulus &&
    decide (cert.target = PolynomialCheckTarget.collisionH) &&
    0 < cert.scale₁ && 0 < cert.scale₂ &&
    0 < cert.low₁ && cert.low₁ < cert.total₁ &&
    0 < cert.low₂ && cert.low₂ < cert.total₂

def computedGcdDegree (cert : CollisionCertificate) : Nat :=
  collisionGcdDegree
    cert.scale₁ cert.low₁ cert.total₁
    cert.scale₂ cert.low₂ cert.total₂

/--
Executable check for an undivided collision-gcd certificate.

The final inequality is the forced-factor accounting: an exact degree equal to
the forced degree leaves no noncyclotomic common factor.
-/
def checks (cert : CollisionCertificate) : Bool :=
  cert.wellFormed &&
    cert.computedGcdDegree = cert.exactGcdDegree &&
    cert.forcedCyclotomicDegree = forcedDoubleRootDegree &&
    cert.exactGcdDegree ≤ cert.forcedCyclotomicDegree

end CollisionCertificate

end Certificates.ZModGcd

end Qab
