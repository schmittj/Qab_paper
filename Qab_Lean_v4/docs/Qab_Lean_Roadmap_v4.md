# Qab Lean formalization roadmap, v4

**Status.** This is the handoff blueprint for a Codex CLI worker. It incorporates the final polish review of the v3 scaffold. The goal is a **conditional formalization from theorem packs** first, followed by a staged replacement of broad packs by Mathlib proofs and Lean-checkable certificates.

The accompanying mathematical summary is `docs/Qab_core_v4.tex` / `docs/Qab_core_v4.pdf`. The original manuscript source is included as `docs/original/Qab_original.tex` for traceability. Start the worker from `CODEX_START_HERE.md`.

## 0. What changed since v3

The v3 review approved the overall architecture and suggested small polish changes before handing the repository to a Lean worker. Version 4 implements those changes.

1. **Residual witness variable renamed.** `CoreProof.lean` uses `reswit`, not `rw`, to avoid conflict with the `rw` tactic.
2. **Certificate interfaces no longer import `CoreProof`.** `Qab/Certificates/Interfaces.lean` imports only the local-packet layer, avoiding a future dependency cycle when finite-elimination proof files start importing certificate modules.
3. **Lower-box bound is explicit in lower eliminators.** `FiniteLowerPack.no_lower_unit` and `FiniteLowerPack.no_both_nonunit` take `ce.D ≤ lowerMax` as an argument. The core proof already has this hypothesis, and passing it explicitly makes the finite-pack boundary more auditable.
4. **Phase-1 polynomial semantics are clarified.** The roadmap, README, and `Basic.lean` distinguish `qPrimZ`, `qOrientZ`, `qPackageProdZ`, `OrientationShare`, and product-level `PackageShare`.
5. **Certificate placeholders are slightly more typed.** `TerminalRow.WellFormed` is present, `expectedGcdDegree` has been renamed to `exactGcdDegree`, and certificates record an explicit `PolynomialCheckTarget` (`collisionH`, `orientationQ`, or `packageProduct`).
6. **Repository handoff is cleaner.** The zip contains only the project directory, with canonical documents under `docs/`; no duplicate top-level roadmap/TeX/PDF files are included.

The prior v2-to-v3 safety decisions remain in force:

- `FromShare` is opaque, never `True`.
- `NormCE` contains `hD`, `norm_gcd`, and `shape_distinct` from phase 0.
- The upper range is split into `UpperNormalizationPack` and `UpperRangePack`.
- Endpoint coefficient trichotomy is an arithmetic lemma, not a local theorem.
- Local p-adic/Kummer work is represented by state extraction: `to_lower_state` and `to_residual_witness`.
- The residual envelope is explicit.

## 1. Target theorem and proof spine

The final target at the current abstraction level is:

```lean
def ReciprocalPackageCoprimality : Prop :=
  ∀ {P Q : PosPair},
    P.unequal → Q.unequal → ¬ P.sameUnordered Q → ¬ PackageShare P Q
```

The conditional assembly theorem is:

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

The proof spine is:

```text
PackageShare P Q
  → CollisionPack.share_to_normCE
  → ∃ ce, FromShare P Q ce
  → GlobalHeightPack.absolute_bound gives ce.D ≤ 175394637
  → either ce.D ≥ 6816242 or ce.D ≤ 6816241

Upper case:
  ce.D ≥ 6816242
  → UpperNormalizationPack.upper_unit_normalized gives ce.UnitCoeff
  → UpperRangePack.no_upper_unit_counterexample gives False

Lower case:
  ce.D ≤ 6816241
  → LocalPacketPack.to_lower_state gives an admissible lower state st
  → arithmetic trichotomy: UnitCoeff ∨ BothNonunit ∨ OneNonunit
  → unit: FiniteLowerPack.no_lower_unit, with explicit ce.D ≤ lowerMax
  → both-nonunit: FiniteLowerPack.no_both_nonunit, with explicit ce.D ≤ lowerMax
  → one-nonunit:
       either ce.D ≥ 16584 or ce.D ≤ 16583
       large: FiniteLowerPack.no_one_nonunit_large
       residual: LocalPacketPack.to_residual_witness
                 then FiniteResidualPack.no_residual_state
```

The core proof should remain a short assembly theorem. It should not contain polynomial definitions, height estimates, p-adic facts, or search/certificate logic.

## 2. Repository layout

```text
Qab_Lean_v4/
  lean-toolchain
  lakefile.lean
  README.md
  CODEX_START_HERE.md
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
    Qab_Lean_Roadmap_v4.md
    Qab_core_v4.tex
    Qab_core_v4.pdf
    reviews/
      audit_v2.md
    original/
      Qab_original.tex
```

The worker's first command should be:

```bash
lake exe cache get
lake build
```

This package was written without a local Lean installation, so small syntax/API fixes may be necessary. The intended math/logic content of the theorem-pack interfaces should not be changed during the first build-fix pass.

## 3. Constants

The constants are defined as reducible abbreviations in `Qab/Constants.lean`:

```lean
abbrev globalBound : Nat := 175394637
abbrev upperStart : Nat := 6816242
abbrev lowerMax : Nat := 6816241
abbrev largeOneNonunitStart : Nat := 16584
abbrev residualMax : Nat := 16583
abbrev residualDegreeMax : Nat := 2601
```

They correspond to the streamlined completion path:

- global height-degree-Mahler bound: `D ≤ 175394637`;
- upper-range start: `D ≥ 6816242`;
- lower box: `D ≤ 6816241`;
- large one-nonunit branch: `D ≥ 16584`;
- residual one-nonunit branch: `D ≤ 16583`;
- residual degree envelope: `d ≤ 2601`.

The boundary lemmas in `Constants.lean` should remain the only arithmetic needed in `CoreProof.lean`.

## 4. Basic objects

`PosPair` is a positive ordered pair. `PosPair.sameUnordered` tracks equality up to reciprocal swap. `PackageShare` is opaque in phase 0.

Important phase-1 warning: the theorem is about reciprocal package products, but the coefficient formula is for primitive orientation polynomials only. Keep the names separate:

```lean
qPrimZ         -- primitive orientation polynomial Q_{A,B}
qOrientZ       -- full orientation polynomial Q_{a,b}, using primitive reduction
qPackageProdZ  -- reciprocal package product Q_{a,b} * Q_{b,a}
OrientationShare
PackageShare   -- product-level sharing
```

The eventual product-level definition should be close to:

```lean
def PackageShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qPackageProdQ P ∧ h ∣ qPackageProdQ Q
```

Orientation-level sharing is useful for the collision dictionary:

```lean
def OrientationShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    0 < h.natDegree ∧ h ∣ qOrientQ P ∧ h ∣ qOrientQ Q
```

If the theorem uses product-level `PackageShare`, prove a separate bridge from product sharing to orientation sharing for some choice of reciprocal orientations.

## 5. Canonical package polynomials: phase-1 target

For positive primitive `A,B`, define `qPrimZ` by coefficients:

```text
Qprim_{A,B}(x)
 = Σ_{0 ≤ j < A} B(j+1)x^j
   + Σ_{A ≤ j ≤ A+B-2} A(A+B-j-1)x^j.
```

For an arbitrary positive pair `a,b`, let `g = gcd a b`, `a = g A`, `b = g B`. The full orientation polynomial must implement:

```text
Q_{a,b}(x) = g * Q_{A,B}(x^g).
```

Do not define `qOrientZ` by applying the primitive coefficient formula directly to `a,b` when `g > 1`.

Implementation sketch:

```lean
def qCoeff (P : PosPair) (j : Nat) : Int :=
  if h1 : j < P.a then
    (P.b : Int) * ((j + 1 : Nat) : Int)
  else if h2 : j ≤ P.a + P.b - 2 then
    (P.a : Int) * ((P.a + P.b - j - 1 : Nat) : Int)
  else
    0

noncomputable def qPrimZ (P : PosPair) : Polynomial Int :=
  -- choose a Mathlib-friendly constructor
  ...

noncomputable def qOrientZ (P : PosPair) : Polynomial Int :=
  -- use primitive reduction and composition with x^g
  ...

noncomputable def qPackageProdZ (P : PosPair) : Polynomial Int :=
  qOrientZ P * qOrientZ P.swap
```

A worker should not copy this pseudo-code literally. Choose the Mathlib-friendly polynomial constructor after checking current APIs.

Initial lemmas:

1. support bound for `qPrimZ`;
2. constant coefficient of `qPrimZ` is `B`;
3. leading coefficient of `qPrimZ` at `A+B-2` is `A`;
4. nonzero constant and leading coefficients;
5. degree formula for `qPrimZ`;
6. primitive-reduction and imprimitive-composition lemmas for `qOrientZ`;
7. map-to-`ℚ[x]` lemmas;
8. product-level divisibility lemmas for `qPackageProdZ`.

Only after these definitions and lemmas are stable should opaque `PackageShare` be replaced.

## 6. Normalized counterexamples and `FromShare`

`NormCE` contains:

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

The endpoint predicates are `UnitCoeff`, `BothNonunit`, and `OneNonunit`. The trichotomy is proved arithmetically from `hU_pos` and `hV_pos`; it is not a p-adic theorem.

`FromShare : PosPair → PosPair → NormCE → Prop` is opaque. Do not define it as `True`. Later it should become a structure containing selected orientations, an off-unit-circle common root, minimal-polynomial data, endpoint-coefficient data, and the link to package sharing.

## 7. The theorem packs

### 7.1 `CollisionPack`

```lean
structure CollisionPack where
  share_to_normCE :
    ∀ {P Q : PosPair},
      P.unequal → Q.unequal → ¬ P.sameUnordered Q →
      PackageShare P Q → ∃ ce : NormCE, FromShare P Q ce
```

This is the bridge from package sharing to a selected normalized counterexample. It should eventually be opened after the polynomial layer is concrete.

### 7.2 `GlobalHeightPack`

```lean
structure GlobalHeightPack where
  absolute_bound :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.D ≤ globalBound
```

This pack contains the height estimate, the rank-two torus/isolation degree bound, Mahler/Smyth or equivalent nonreciprocal gap, and exact constant arithmetic. It is the part that makes the infinite family finite.

### 7.3 `UpperNormalizationPack` and `UpperRangePack`

```lean
structure UpperNormalizationPack where
  upper_unit_normalized :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → upperStart ≤ ce.D → ce.UnitCoeff

structure UpperRangePack where
  no_upper_unit_counterexample :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.UnitCoeff →
      upperStart ≤ ce.D → ce.D ≤ globalBound → False
```

This split mirrors the manuscript more faithfully than a single broad upper-range contradiction.

### 7.4 `LocalPacketPack`

```lean
structure LowerState where
  rowId : Nat

constant Encodes : NormCE → LowerState → Prop
constant AdmissibleLowerState : LowerState → Prop

structure LocalPacketPack where
  to_lower_state :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.D ≤ lowerMax →
      ∃ st : LowerState, Encodes ce st ∧ AdmissibleLowerState st

  to_residual_witness :
    ∀ {P Q : PosPair} {ce : NormCE},
      FromShare P Q ce → ce.OneNonunit → ce.D ≤ residualMax →
      ResidualWitness ce
```

Open `LowerState` later by adding primitive shapes, scales, extraction degrees, endpoint coefficients, slope signatures, packet occupancies, deficient-prime flags, total-radical data, and row identifiers.

### 7.5 Residual envelope

The residual envelope is explicit:

```lean
def ResidualEnvelope (ce : NormCE) : Prop :=
  ce.D ≤ residualMax ∧
  ce.Vabs = 1 ∧
  2 ≤ ce.U ∧ ce.U ≤ ce.D ∧
  ce.d ≤ residualDegreeMax
```

The local pack returns a `ResidualWitness` containing reciprocal normalization, the envelope, a residual state, and admissibility.

### 7.6 `FiniteLowerPack`

```lean
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
```

The unit and both-nonunit eliminators explicitly take the lower-box hypothesis. The Kummer-defect unit subbranch remains an explicit review decision: keep a narrow isolation theorem pack for the 46 irreducible primitive shapes, or replace it by finite certificates.

### 7.7 `FiniteResidualPack`

```lean
structure FiniteResidualPack where
  no_residual_state :
    ∀ {ce ce' : NormCE} {st : ResidualState},
      ReciprocalNormalize ce ce' →
      ResidualEnvelope ce' →
      EncodesResidual ce' st →
      AdmissibleResidualState st →
      False
```

This should be the first finite pack opened concretely.

## 8. Certificate architecture

`Qab/Certificates/Interfaces.lean` is schematic but now makes the certificate target and row sanity checks explicit. The current declarations are:

```lean
inductive PolynomialCheckTarget where
  | collisionH
  | orientationQ
  | packageProduct

structure TerminalRow where
  rowId : Nat
  m n p q : Nat
  orientationId : Nat

namespace TerminalRow

def WellFormed (row : TerminalRow) : Prop :=
  0 < row.m ∧ row.m < row.n ∧ 0 < row.p ∧ row.p < row.q

end TerminalRow

structure CoverageInterval where
  lo hi : Nat

structure CoverageCert where
  name : String
  intervals : List CoverageInterval
  auditId : String

structure ModGcdCert (row : TerminalRow) where
  prime : Nat
  target : PolynomialCheckTarget
  exactGcdDegree : Nat
  forcedCyclotomicDegree : Nat
  row_wellformed : row.WellFormed
  auditId : String
```

`auditId` is metadata, not a proof. The proof-relevant content must be typed interval/branch data, explicit Euclidean/Bezout certificates, or generated Lean terms.

For terminal modular gcd certificates, prove a good-reduction theorem of this shape:

```lean
if h ∈ ℤ[x] is primitive and nonconstant,
h ∣ F and h ∣ G over ℚ[x],
and p is a good reduction prime,
then h mod p divides gcd(F mod p, G mod p).
```

Good-reduction hypotheses should include primality of `p`, leading coefficient/content checks, preservation of positive degree after reduction, and explicit handling of forced cyclotomic factors. If certificates use undivided collision trinomials, the forced double root at `x = 1` must be accounted for explicitly. If certificates use divided package polynomials, the proof should say where the forced factor has already been removed.

## 9. Implementation phases

### Phase 0: compile the conditional scaffold

Acceptance criteria:

1. `lake build` succeeds.
2. `package_coprimality_from_packs` compiles.
3. `FromShare` is opaque or a real structure, not `True`.
4. No theorem is advertised as unconditional unless it imports `BroadAxioms.lean` and is clearly marked axiom-dependent.
5. `NormCE` includes `hD`, `norm_gcd`, and shape distinctness.
6. README states the conditional status.

Expected work: 1--3 days for a Lean worker, mostly build/API fixes.

### Phase 1: concrete package polynomials and `PackageShare`

Tasks:

1. Implement `qPrimZ` by coefficients.
2. Implement primitive-reduction data for a positive pair.
3. Implement full imprimitive `qOrientZ` using composition `x ↦ x^g`.
4. Implement reciprocal `qPackageProdZ`.
5. Define and compare `OrientationShare` and product-level `PackageShare`.
6. Map these polynomials to `ℚ[x]`.
7. Prove support, degree, constant coefficient, leading coefficient, imprimitive-composition, and primitive/content facts.
8. Define `PackageShare` concretely.
9. Prove package-level gcd/coprimality equivalences.

Expected work: 1--3 weeks depending on Mathlib polynomial API familiarity.

### Phase 2: first residual terminal certificates

Tasks:

1. Encode the residual terminal package pairs and orientations.
2. Implement the selected polynomial constructor used by the terminal checks.
3. Check the modular gcd certificates over `ZMod 1009`.
4. Prove the good-reduction-to-no-common-noncyclotomic-factor theorem for these terminal rows.

Expected work: 2--5 weeks. This is the highest-value first certificate milestone.

### Phase 3: residual state coverage

Tasks:

1. Expand `ResidualState` fields.
2. Define `AdmissibleResidualState` from exact integer predicates.
3. Generate typed coverage certificates for the residual generator and pair sieve.
4. Replace the broad `FiniteResidualPack` axiom by a theorem from coverage plus terminal certificates.

Expected work: 1--3 months depending on data size and certificate format.

### Phase 4: lower nonunit branches

Tasks:

1. Expand `LowerState` enough to support both-nonunit and one-nonunit-large computations.
2. Formalize row predicates and exact filters.
3. Prove no survivors for both-nonunit and one-nonunit-large branches from certificates.
4. Open corresponding fields of `FiniteLowerPack`.

Expected work: 2--4 months.

### Phase 5: unit branch

Tasks:

1. Formalize full-Kummer search row/certificate formats.
2. Verify terminal modular gcd certificates for full-Kummer branches.
3. Decide the Kummer-defect strategy: keep a narrow isolation axiom for the 46 irreducible shapes, or generate direct finite package-orientation certificates and avoid global isolation.
4. Open `FiniteLowerPack.no_lower_unit`.

Expected work: 2--5 months, heavily dependent on the Kummer-defect decision.

### Phase 6: collision pack and selected-root data

Tasks:

1. Replace `FromShare` by a real structure.
2. Formalize the collision dictionary and reciprocal orientations.
3. Prove unit-circle/cyclotomic removal.
4. Prove no-three orientation compatibility.
5. Prove primitive normalization and imprimitive composition handling.
6. Open `CollisionPack`.

Expected work: 2--6 months.

### Phase 7: global height and local theorem packs

These are the hardest mathematical openings.

Global height pack:

- height of collision roots;
- degree bound from rank-two torus/isolation;
- Smyth/Mahler nonreciprocal gap;
- constant arithmetic.

Local packet pack:

- Borisov/Newton polygon consequences in exactly the forms consumed by states;
- p-adic local-field ramification/packet facts;
- Capelli/Kummer extraction-degree control;
- endpoint divisibility, support, and slope-signature constraints.

Expected work: several months to multi-year depending on how much is axiomatized versus formalized.

## 10. Axiom policy

Use three categories.

### Category A: broad temporary packs

Located only in `Qab/Packs/BroadAxioms.lean`. These are acceptable for smoke tests but not for reviewable mathematical claims.

### Category B: narrow literature theorem packs

Examples:

```lean
structure BorisovNewtonPack where ...
structure CapelliKummerPack where ...
structure HeightMahlerPack where ...
structure ToricBezoutPack where ...
```

These should have theorem statements close to the literature and should not mention the final theorem.

### Category C: Lean-checked certificates

Computational eliminations should eventually be Category C, not Category B. The finite branches are part of the novel proof and should not remain broad axioms if the project aims at genuine validation.

## 11. Mathematical simplifications retained

The Lean core intentionally omits the following from the top-level theorem:

- ASZ-style unlikely-intersection boundedness;
- Beukers--Schlickewei/S-unit finiteness;
- density-one/global-isolation side results except possibly as a narrow unit-defect axiom;
- most sign/phase/Schur discovery scaffolding.

The retained core is:

- collision extraction;
- explicit height-degree bound;
- upper unit-normalized elimination;
- lower finite-state extraction;
- finite branch eliminations.

## 12. Open review questions

1. **Unit Kummer-defect branch.** Should the 46 irreducible-shape branch use a narrow global-isolation theorem pack, or should it be replaced by direct finite certificates?
2. **Terminal polynomial choice.** Should modular gcd certificates be stated for divided package polynomials or undivided collision trinomials? The forced `x=1` double root must be accounted for explicitly either way.
3. **Upper range final rows.** Should the 761 same-shape rows be excluded by a formal same-shape degree contradiction, or should modular certificates be attached to the terminal rows?
4. **Shape of `FromShare`.** Should selected roots be represented via explicit algebraic extensions, minimal polynomials, or divisibility-only data? Defer until package polynomial API is stable.
5. **Data format.** Should certificates live as generated Lean files, JSON/CSV read by an external generator, or compact binary-to-Lean translations? For Lean trust, the final checked objects must be typed Lean data or reduced to typed Lean data.

## 13. Immediate instructions to the Codex CLI worker

Start by reading `CODEX_START_HERE.md`, then run:

```bash
cd Qab_Lean_v4
lake exe cache get
lake build
```

Then:

1. Fix build errors without changing theorem-pack intent.
2. Keep a changelog of API adjustments.
3. Confirm `Qab/CoreProof.lean` stays short and pack-parametric.
4. Do not import `BroadAxioms.lean` into core files.
5. Add tests/examples only in separate files.
6. Report back if any pack interface needs to change to make the core proof compile.

Once phase 0 compiles, begin phase 1 with the polynomial layer in this order: `qPrimZ`, primitive-reduction data, `qOrientZ`, `qPackageProdZ`, `OrientationShare`, then product-level `PackageShare`.
