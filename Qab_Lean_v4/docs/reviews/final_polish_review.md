## Verdict

Yes. This revised v3 package is **suitable to start a first Lean formalization**, provided the goal is clearly the one stated in the README: a **conditional formalization from theorem packs**, not yet a Lean-certified proof of the theorem packs themselves.

Compared with the previous package, this is a major improvement. The main design hazards from v2 have been addressed:

| v2 concern                                             | v3 status                                                                                |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `FromShare` might be defined as `True`                 | Fixed: now opaque                                                                        |
| `NormCE` too thin                                      | Fixed: includes `hD`, `norm_gcd`, `shape_distinct`                                       |
| Upper branch too broad                                 | Fixed: split into `UpperNormalizationPack` and `UpperRangePack`                          |
| Local p-adic work hidden behind coefficient trichotomy | Fixed: trichotomy is arithmetic; local work is state extraction                          |
| Finite eliminators consumed raw `FromShare`            | Mostly fixed: lower eliminators consume `Encodes ce st` and `AdmissibleLowerState st`    |
| Residual branch envelope hidden                        | Fixed: explicit `ResidualEnvelope` and `ResidualWitness`                                 |
| No project scaffold                                    | Fixed: now has `lakefile.lean`, `lean-toolchain`, module tree, README                    |
| Certificate boundary unclear                           | Improved: schematic interfaces are present and documentation explains the trust boundary |

I would start from this package.

The main remaining caveat is that the package is still a scaffold. It proves the correct **assembly theorem** from named packs, but the hard mathematical and computational proof content remains inside assumptions, opaque predicates, or future certificate checkers.

---

## What I checked

I unpacked the zip and reviewed the Lean files, README, roadmap, and TeX core. The package contains:

```text
Qab_Lean_v3/
  lean-toolchain
  lakefile.lean
  README.md
  Qab.lean
  Qab/
    Constants.lean
    Basic.lean
    Counterexample.lean
    CoreProof.lean
    Packs/
      Collision.lean
      GlobalHeight.lean
      LocalPacket.lean
      FiniteElimination.lean
      BroadAxioms.lean
    Certificates/
      Interfaces.lean
  docs/
    Qab_Lean_Roadmap_v3.md
    Qab_core_v3.tex
    Qab_core_v3.pdf
    audit_v2.md
```

I also checked the original `Qab(1).tex` against the v3 constants and branch structure. The main numerical cutoffs match:

```text
global bound:             D ≤ 175394637
upper range start:        D ≥ 6816242
lower box:                D ≤ 6816241
large one-nonunit start:  D ≥ 16584
residual range:           D ≤ 16583
residual degree bound:    d ≤ 2601
```

I could not run `lake build` because this environment does not have Lean or Lake installed. I did run `pdflatex` on `docs/Qab_core_v3.tex`, and the TeX source compiled successfully.

---

## Mathematical audit

The v3 proof spine is mathematically sound as a conditional argument.

The core theorem now has the right structure:

```lean
theorem package_coprimality_from_packs
    (C  : CollisionPack)
    (G  : GlobalHeightPack)
    (UN : UpperNormalizationPack)
    (UR : UpperRangePack)
    (L  : LocalPacketPack)
    (FL : FiniteLowerPack)
    (FR : FiniteResidualPack) :
    ReciprocalPackageCoprimality
```

The proof proceeds as follows:

```text
PackageShare P Q
  → CollisionPack.share_to_normCE
  → ∃ ce, FromShare P Q ce

FromShare P Q ce
  → GlobalHeightPack.absolute_bound
  → ce.D ≤ 175394637

Then split:

1. Upper case:
   ce.D ≥ 6816242
   → UpperNormalizationPack.upper_unit_normalized
   → ce.UnitCoeff
   → UpperRangePack.no_upper_unit_counterexample
   → False

2. Lower case:
   ce.D ≤ 6816241
   → LocalPacketPack.to_lower_state
   → admissible lower state

   Then arithmetic trichotomy:
   ce.UnitCoeff ∨ ce.BothNonunit ∨ ce.OneNonunit

   Unit:
     → FiniteLowerPack.no_lower_unit

   Both nonunit:
     → FiniteLowerPack.no_both_nonunit

   One nonunit:
     split at 16584 / 16583

     Large:
       ce.D ≥ 16584
       → FiniteLowerPack.no_one_nonunit_large

     Residual:
       ce.D ≤ 16583
       → LocalPacketPack.to_residual_witness
       → ResidualEnvelope after reciprocal normalization
       → FiniteResidualPack.no_residual_state
```

This matches the final branch structure of the original manuscript. I do not see a missing top-level case.

The important distinction is that this is still conditional. The following major mathematical blocks remain inside packs:

```text
CollisionPack:
  package-product sharing → selected off-unit-circle normalized collision

GlobalHeightPack:
  height estimate, degree bound, Mahler/Smyth gap, constant arithmetic

UpperNormalizationPack:
  D ≥ 6816242 → unit leading/constant coefficients

UpperRangePack:
  exact upper-range elimination

LocalPacketPack:
  p-adic/Kummer extraction, endpoint packets, deficient prime control,
  residual reciprocal normalization

FiniteLowerPack:
  lower unit branch, both-nonunit branch, large one-nonunit branch

FiniteResidualPack:
  residual finite-state elimination
```

That is acceptable for the first version, because the README and roadmap are explicit that this is a conditional theorem-pack scaffold.

---

## Lean architecture audit

### 1. `FromShare` is now safe

This is the most important fix.

Current declaration:

```lean
constant FromShare : PosPair → PosPair → NormCE → Prop
```

This avoids the v2 inconsistency risk. Since `FromShare` is opaque, broad eliminators do not automatically apply to arbitrary dummy `NormCE` records.

The guardrails in `BroadAxioms.lean` are also good:

```lean
* `FromShare` must stay opaque here; never define it as `True`.
* No dummy `FromShare` proofs should be axiomatized.
```

This is exactly the right policy.

### 2. `NormCE` is now strong enough for phase 0 and phase 1

The current record is much better:

```lean
structure NormCE where
  m n p q : Nat
  hm_pos : 0 < m
  hm_lt  : m < n
  hp_pos : 0 < p
  hp_lt  : p < q
  D : Nat
  hD : D = max (max m n) (max p q)
  norm_gcd : Nat.gcd (Nat.gcd m n) (Nat.gcd p q) = 1
  shape_distinct : ¬ ((m = p ∧ n = q) ∨ (m = q ∧ n = p))
  d U Vabs : Nat
  hd_pos : 0 < d
  hU_pos : 0 < U
  hV_pos : 0 < Vabs
```

This fixes the earlier problem where `D` and primitive normalization were not part of the counterexample state. It should now be possible to open theorem packs later without changing the core proof signature.

The arithmetic trichotomy is also correctly proved from positivity:

```lean
theorem coeff_trichotomy (ce : NormCE) :
    ce.UnitCoeff ∨ ce.BothNonunit ∨ ce.OneNonunit
```

That is the right place for this lemma. It should not be a local p-adic axiom.

### 3. The upper branch split is right

The split into

```lean
UpperNormalizationPack
UpperRangePack
```

is a clear improvement. It mirrors the original proof better than a single broad upper-range contradiction.

This is now reviewable:

```lean
structure UpperNormalizationPack where
  upper_unit_normalized :
    FromShare P Q ce → upperStart ≤ ce.D → ce.UnitCoeff

structure UpperRangePack where
  no_upper_unit_counterexample :
    FromShare P Q ce → ce.UnitCoeff →
    upperStart ≤ ce.D → ce.D ≤ globalBound → False
```

This is exactly the split I would want before opening the upper computation.

### 4. Lower and residual states are much better

The local/finite interface is now structurally sound:

```lean
structure LowerState where
  rowId : Nat

constant Encodes : NormCE → LowerState → Prop
constant AdmissibleLowerState : LowerState → Prop
```

and the finite lower pack consumes state data:

```lean
no_lower_unit :
  Encodes ce st → AdmissibleLowerState st → ce.UnitCoeff → False
```

This is much better than having the finite eliminators consume raw `FromShare`.

The residual branch is also much improved:

```lean
def ResidualEnvelope (ce : NormCE) : Prop :=
  ce.D ≤ residualMax ∧
  ce.Vabs = 1 ∧
  2 ≤ ce.U ∧ ce.U ≤ ce.D ∧
  ce.d ≤ residualDegreeMax
```

and

```lean
structure ResidualWitness (ce : NormCE) where
  ce' : NormCE
  st : ResidualState
  recnorm : ReciprocalNormalize ce ce'
  envelope : ResidualEnvelope ce'
  encodes : EncodesResidual ce' st
  admissible : AdmissibleResidualState st
```

This exposes exactly the reductions that should not be hidden:

```text
D ≤ 16583
Vabs = 1
2 ≤ U ≤ D
d ≤ 2601
```

That is a strong design improvement.

---

## Likely Lean build status

I could not type-check with Lean, but by static inspection the Lean files look close to buildable.

The imports are plausible:

```lean
import Mathlib.Tactic
```

in `Constants.lean` should make `omega` available downstream.

The core proof is short and well structured. I see no obvious mathematical type mismatch.

There are a few minor things a Lean worker may need to adjust on first build:

### 1. Rename `rw` in `CoreProof.lean`

This is probably accepted by Lean, but it is mildly risky and stylistically unfortunate because `rw` is a tactic name.

Current code:

```lean
let rw := L.to_residual_witness hfs hOne hResidual
exact FR.no_residual_state rw.recnorm rw.envelope rw.encodes rw.admissible
```

I would change it to:

```lean
let rwit := L.to_residual_witness hfs hOne hResidual
exact FR.no_residual_state rwit.recnorm rwit.envelope rwit.encodes rwit.admissible
```

This avoids parser/name confusion.

### 2. `omega` should probably prove the trichotomy, but have a fallback ready

This theorem:

```lean
theorem coeff_trichotomy (ce : NormCE) :
    ce.UnitCoeff ∨ ce.BothNonunit ∨ ce.OneNonunit := by
  have hU := ce.hU_pos
  have hV := ce.hV_pos
  dsimp [UnitCoeff, BothNonunit, OneNonunit]
  omega
```

is mathematically correct. If `omega` does not like the disjunction shape, replace it with a two-step case split:

```lean
have hU' : ce.U = 1 ∨ 2 ≤ ce.U := by omega
have hV' : ce.Vabs = 1 ∨ 2 ≤ ce.Vabs := by omega
rcases hU' with hU1 | hU2
  <;> rcases hV' with hV1 | hV2
  <;> simp [UnitCoeff, BothNonunit, OneNonunit, hU1, hU2, hV1, hV2]
```

The current version is fine to try first.

### 3. Certificate interface should not import `CoreProof`

Currently:

```lean
import Qab.CoreProof
```

in `Qab/Certificates/Interfaces.lean`.

This works now, but it is a future dependency-cycle trap. Eventually, finite-elimination proofs will want to import certificate interfaces. If certificates already import `CoreProof`, and `CoreProof` imports finite elimination, you will get an architectural cycle.

I would change this now to a minimal import, probably:

```lean
import Qab.Packs.LocalPacket
```

or even:

```lean
import Qab.Counterexample
```

depending on what the certificate interfaces need. At the moment, `Interfaces.lean` does not need `CoreProof`.

### 4. Lower finite pack could expose the lower-box hypothesis explicitly

The current lower eliminators rely on `AdmissibleLowerState st` to encode that the state is in the lower box. That is reasonable, but the core proof has the lower-box hypothesis available:

```lean
hLower : ce.D ≤ lowerMax
```

For auditability, I would pass it explicitly to at least the unit and both-nonunit eliminators:

```lean
no_lower_unit :
  Encodes ce st → AdmissibleLowerState st →
  ce.D ≤ lowerMax → ce.UnitCoeff → False

no_both_nonunit :
  Encodes ce st → AdmissibleLowerState st →
  ce.D ≤ lowerMax → ce.BothNonunit → False
```

Then the core proof uses:

```lean
exact FL.no_lower_unit hEnc hAdm hLower hUnit
exact FL.no_both_nonunit hEnc hAdm hLower hBoth
```

This is not strictly necessary, but it makes the theorem-pack boundary more transparent.

---

## Important phase-1 warning: package polynomial semantics need tightening

The v3 roadmap says the first concrete replacement for `PackageShare` should use a coefficient-defined package polynomial. This is the right direction, but there is one point that should be clarified before coding.

The original theorem is about reciprocal package products:

[
P_{a,b}(x)=Q_{a,b}(x)Q_{b,a}(x).
]

Meanwhile the roadmap’s coefficient formula is for the primitive orientation polynomial (Q_{A,B}), essentially the case after primitive reduction.

For nonprimitive pairs,

[
a=gA,\qquad b=gB,\qquad \gcd(A,B)=1,
]

the original manuscript uses

[
Q_{a,b}(x)=gQ_{A,B}(x^g).
]

So phase 1 should not accidentally define `packageQZ P` by the primitive coefficient formula for arbitrary `PosPair`. That would be wrong for imprimitive pairs.

I recommend separating the names:

```lean
qPrimZ        -- primitive orientation polynomial Q_{A,B}
qOrientZ      -- full orientation polynomial Q_{a,b}, using primitive reduction
qPackageProdZ -- reciprocal package product Q_{a,b} * Q_{b,a}
OrientationShare
PackageShare
```

Then choose one of two clean approaches:

```lean
-- Product-level, closest to the paper:
def PackageShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q
```

or:

```lean
-- Orientation-level, useful for the collision dictionary:
def OrientationShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qOrientQ P ∧ h ∣ qOrientQ Q
```

If using the orientation-level version, then prove separately that package-product sharing gives orientation sharing for some choice of reciprocal orientations. The current abstract `PackageShare` hides this distinction, which is fine for phase 0, but it should be resolved before phase 1.

---

## Certificate interface audit

The certificate module is appropriately schematic for now:

```lean
structure TerminalRow where
  rowId : Nat
  m n p q : Nat
  orientationId : Nat

structure CoverageCert where
  name : String
  payloadHash : String

structure ModGcdCert where
  prime : Nat
  expectedGcdDegree : Nat
  forcedCyclotomicDegree : Nat
  payloadHash : String
```

This is acceptable as a placeholder, and the roadmap correctly says that hashes are not Lean certificates.

For the first real certificate milestone, I would strengthen this before doing serious work:

1. Replace `payloadHash` by typed data or generated Lean terms.
2. Add a `TerminalRow.WellFormed` predicate or use a structured row with positivity/order proofs.
3. Rename `expectedGcdDegree` to something like `exactGcdDegree` if the certificate proves exact degree.
4. Decide whether certificates check:

   * divided package polynomials (Q_{a,b}), or
   * undivided collision trinomials (H_{m,n}).

This matters because the residual terminal checks report modular gcd degree `2`, which is accounted for by the forced double root at (x=1). Lean must know exactly where that forced degree lives.

The roadmap correctly identifies the residual terminal certificates over `ZMod 1009` as the right first computational target. I agree.

---

## Axiom policy audit

`BroadAxioms.lean` is well isolated:

```lean
axiom broad_collision_pack : CollisionPack
axiom broad_global_height_pack : GlobalHeightPack
axiom broad_upper_normalization_pack : UpperNormalizationPack
axiom broad_upper_range_pack : UpperRangePack
axiom broad_local_packet_pack : LocalPacketPack
axiom broad_finite_lower_pack : FiniteLowerPack
axiom broad_finite_residual_pack : FiniteResidualPack
```

and the theorem using them is clearly named:

```lean
theorem package_coprimality_with_broad_axioms : ReciprocalPackageCoprimality
```

This is fine as a smoke test. It is not a mathematical proof yet, but the package says that clearly.

Also good: `Qab.lean` does **not** import `BroadAxioms.lean`.

So normal users importing

```lean
import Qab
```

will not automatically import the broad axiom theorem. That is the right default.

---

## Minor packaging issues

The zip contains both the project directory and duplicate top-level copies of:

```text
Qab_Lean_Roadmap_v3.md
Qab_core_v3.tex
Qab_core_v3.pdf
```

This is harmless, but I would remove the top-level duplicates in the repository version to avoid confusion. Keep the canonical copies under:

```text
Qab_Lean_v3/docs/
```

The README is clear and useful. The roadmap is detailed enough for a worker to begin.

---

## Recommended edits before handing this to a Lean worker

I would make these four small changes first:

1. Rename `rw` to `rwit` or `reswit` in `CoreProof.lean`.
2. Change `Qab/Certificates/Interfaces.lean` so it does not import `Qab.CoreProof`.
3. Consider adding `ce.D ≤ lowerMax` explicitly to `FiniteLowerPack.no_lower_unit` and `no_both_nonunit`.
4. Add one paragraph to the phase-1 instructions clarifying the difference between:

   * primitive (Q_{A,B}),
   * full imprimitive (Q_{a,b}=gQ_{A,B}(x^g)),
   * reciprocal package product (Q_{a,b}Q_{b,a}),
   * orientation-level sharing versus package-product sharing.

None of these changes blocks starting phase 0, but they will reduce confusion later.

---

## Suggested first Lean milestone

The first milestone should be very modest:

```text
Milestone 0:
  lake build succeeds
  package_coprimality_from_packs compiles
  BroadAxioms.lean compiles but is not imported by Qab.lean
  no theorem outside BroadAxioms.lean depends on broad temporary axioms
```

Then phase 1 should not jump immediately to certificates. It should first build the polynomial layer carefully:

```text
Milestone 1:
  define primitive orientation polynomial qPrimZ
  define full orientation polynomial qOrientZ using primitive reduction
  define reciprocal package product qPackageProdZ
  prove basic coefficient/support/degree/constant/leading lemmas
  define concrete PackageShare
```

Only after that would I start the residual terminal `ZMod 1009` certificates.

---

## Bottom line

This v3 package is a good starting point. It is much more disciplined than the previous draft, and it now has the right shape for a first conditional Lean formalization.

I would approve it for phase-0 Lean work, with the following understanding:

```text
Suitable now:
  yes, as a conditional theorem-pack scaffold

Not yet:
  a Lean proof of the original theorem

Most urgent next action:
  run lake build and make small API/syntax fixes

Most important phase-1 clarification:
  define the polynomial/package-sharing layer carefully,
  especially primitive vs imprimitive Q_{a,b} and package-product vs orientation sharing
```

The core mathematical logic is intact, the main previous assumption-boundary problems are fixed, and the remaining issues are engineering and interface-refinement issues rather than flaws in the proof spine.
