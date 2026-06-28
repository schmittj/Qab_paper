import Qab.Certificates.ZModGcd
import Mathlib.Tactic

namespace Qab

open Polynomial

namespace Certificates.CollisionBezout

open Certificates.ZModGcd

/-!
Semantic Bezout certificates for residual collision rows over `ZMod 1009`.

The dense gcd checker in `Qab.Certificates.ZModGcd` is useful as an executable
screen, but its Euclidean loop is not yet proved to compute Mathlib's gcd.
This module supplies a smaller semantic kernel: it checks dense coefficient
identities of the form

`u * collisionH₁ + v * collisionH₂ = (X - 1)^2`

and proves once that this executable identity denotes the corresponding
Mathlib polynomial identity.  Consequently every common divisor of the two
mapped collision polynomials divides the forced double root.
-/

@[simp]
lemma natCast_modMul (a b : Nat) :
    ((modMul a b : Nat) : F1009) = (a : F1009) * (b : F1009) := by
  simp [modMul]

@[simp]
lemma C_natCast_modNeg (a : Nat) :
    Polynomial.C ((modNeg a : Nat) : F1009) = -Polynomial.C (a : F1009) := by
  rw [natCast_modNeg]
  simp

def addDenseRaw : List Nat → List Nat → List Nat
  | [], g => g
  | f, [] => f
  | a :: f, b :: g => modAdd a b :: addDenseRaw f g

def addDense (f g : List Nat) : List Nat := trim (addDenseRaw f g)

def scaleDense (c : Nat) : List Nat → List Nat
  | [] => []
  | a :: f => modMul c a :: scaleDense c f

def shiftDense : Nat → List Nat → List Nat
  | 0, f => f
  | n + 1, f => 0 :: shiftDense n f

def shiftScaleDense (shift c : Nat) (f : List Nat) : List Nat :=
  shiftDense shift (scaleDense c f)

/--
Executable multiplication of a dense polynomial by the sparse residual
collision trinomial.
-/
def collisionMulDense (f : List Nat) (scale low total : Nat) : List Nat :=
  addDense
    (addDense
      (shiftScaleDense (scale * total) low f)
      (shiftScaleDense (scale * low) (modNeg total) f))
    (scaleDense (total - low) f)

lemma denseToPoly_addDenseRaw (f g : List Nat) :
    denseToPoly (addDenseRaw f g) = denseToPoly f + denseToPoly g := by
  induction f generalizing g with
  | nil =>
      simp [addDenseRaw, denseToPoly]
  | cons a f ih =>
      cases g with
      | nil =>
          simp [addDenseRaw, denseToPoly]
      | cons b g =>
          simp [addDenseRaw, denseToPoly, ih]
          ring

lemma denseToPoly_addDense (f g : List Nat) :
    denseToPoly (addDense f g) = denseToPoly f + denseToPoly g := by
  simp [addDense, denseToPoly_trim, denseToPoly_addDenseRaw]

lemma denseToPoly_scaleDense (c : Nat) (f : List Nat) :
    denseToPoly (scaleDense c f) = Polynomial.C (c : F1009) * denseToPoly f := by
  induction f with
  | nil =>
      simp [scaleDense, denseToPoly]
  | cons a f ih =>
      simp [scaleDense, denseToPoly, ih]
      ring_nf

lemma denseToPoly_shiftDense (shift : Nat) (f : List Nat) :
    denseToPoly (shiftDense shift f) = Polynomial.X ^ shift * denseToPoly f := by
  induction shift with
  | zero =>
      simp [shiftDense]
  | succ shift ih =>
      simp [shiftDense, denseToPoly, ih, pow_succ]
      ring_nf

lemma denseToPoly_shiftScaleDense (shift c : Nat) (f : List Nat) :
    denseToPoly (shiftScaleDense shift c f) =
      Polynomial.X ^ shift * (Polynomial.C (c : F1009) * denseToPoly f) := by
  simp [shiftScaleDense, denseToPoly_shiftDense, denseToPoly_scaleDense]

lemma denseToPoly_collisionMulDense (f : List Nat) (scale low total : Nat) :
    denseToPoly (collisionMulDense f scale low total) =
      denseToPoly f * collisionHMod scale low total := by
  rw [collisionMulDense, denseToPoly_addDense, denseToPoly_addDense,
    denseToPoly_shiftScaleDense, denseToPoly_shiftScaleDense, denseToPoly_scaleDense,
    collisionHMod_eq_sparse]
  rw [C_natCast_modNeg]
  ring

def forcedFactorDense : List Nat := [1, modNeg 2, 1]

lemma denseToPoly_forcedFactorDense :
    denseToPoly forcedFactorDense = ((Polynomial.X - 1 : Polynomial F1009) ^ 2) := by
  simp [forcedFactorDense, denseToPoly, sq]
  rw [Polynomial.C_ofNat]
  ring_nf

/-- Dense Bezout data for one residual collision pair. -/
structure CollisionBezoutCertificate where
  scale₁ : Nat
  low₁ : Nat
  total₁ : Nat
  scale₂ : Nat
  low₂ : Nat
  total₂ : Nat
  u : List Nat
  v : List Nat
  deriving Repr

namespace CollisionBezoutCertificate

def bezoutLhs (cert : CollisionBezoutCertificate) : List Nat :=
  addDense
    (collisionMulDense cert.u cert.scale₁ cert.low₁ cert.total₁)
    (collisionMulDense cert.v cert.scale₂ cert.low₂ cert.total₂)

def checks (cert : CollisionBezoutCertificate) : Prop :=
  cert.bezoutLhs = forcedFactorDense

instance checksDecidable (cert : CollisionBezoutCertificate) : Decidable cert.checks := by
  unfold checks
  infer_instance

theorem polynomialIdentity_of_checks {cert : CollisionBezoutCertificate}
    (hcheck : cert.checks) :
    denseToPoly cert.u * collisionHMod cert.scale₁ cert.low₁ cert.total₁ +
      denseToPoly cert.v * collisionHMod cert.scale₂ cert.low₂ cert.total₂ =
        ((Polynomial.X - 1 : Polynomial F1009) ^ 2) := by
  have hdense := congrArg denseToPoly hcheck
  rw [bezoutLhs, denseToPoly_addDense, denseToPoly_collisionMulDense,
    denseToPoly_collisionMulDense, denseToPoly_forcedFactorDense] at hdense
  exact hdense

/--
A checked Bezout identity proves that no common divisor remains outside the
forced double root.
-/
theorem common_dvd_X_sub_one_sq {cert : CollisionBezoutCertificate}
    (hcheck : cert.checks) {d : Polynomial F1009}
    (h₁ : d ∣ collisionHMod cert.scale₁ cert.low₁ cert.total₁)
    (h₂ : d ∣ collisionHMod cert.scale₂ cert.low₂ cert.total₂) :
    d ∣ ((Polynomial.X - 1 : Polynomial F1009) ^ 2) := by
  rcases h₁ with ⟨a, ha⟩
  rcases h₂ with ⟨b, hb⟩
  refine ⟨denseToPoly cert.u * a + denseToPoly cert.v * b, ?_⟩
  have hpoly := polynomialIdentity_of_checks hcheck
  calc
    ((Polynomial.X - 1 : Polynomial F1009) ^ 2) =
        denseToPoly cert.u * collisionHMod cert.scale₁ cert.low₁ cert.total₁ +
          denseToPoly cert.v * collisionHMod cert.scale₂ cert.low₂ cert.total₂ := hpoly.symm
    _ = denseToPoly cert.u * (d * a) + denseToPoly cert.v * (d * b) := by
      simp [ha, hb]
    _ = d * (denseToPoly cert.u * a + denseToPoly cert.v * b) := by
      ring

end CollisionBezoutCertificate

end Certificates.CollisionBezout

end Qab
