## Audit verdict

The package is **mathematically coherent as a conditional Lean formalization plan**, and the proposed proof spine does preserve the decisive logic of `Qab(1).tex`: package sharing is converted to a normalized counterexample; a global height–degree–Mahler bound makes the search finite; the upper range is eliminated; the lower range is split by endpoint-coefficient type; and the unit, both-nonunit, one-nonunit-large, and residual one-nonunit branches are eliminated.

However, the current Lean blueprint is **not yet a faithful “first conditional formalization” unless the assumption boundary is tightened**. The skeleton proves the intended theorem from four packs, but several packs are currently so broad that they could accidentally hide nearly all of the theorem. This is acceptable for a toy phase-0 assembly theorem, but it should be revised before serious Lean work begins.

The most important concrete warning is this:

> The roadmap says `FromShare` may be defined as `True` in phase 0. Do **not** do this if you also add broad axiom instances of the finite-elimination packs. With `FromShare := True`, the finite-elimination fields become inconsistent, because one can construct a dummy `NormCE` with `D = 1`, `U = 1`, `Vabs = 1`, and immediately derive `False` from `no_lower_unit`.

The skeleton avoids this by making `FromShare` an opaque constant rather than `True`. That is the right direction. Keep it opaque, or make it a real structure with normalized-counterexample content.

I could not run Lean type-checking because Lean/Lake are not installed in this container. I did, however, unpack the package, review the Lean syntax/API by inspection, and compile both TeX files with `pdflatex`; the TeX sources compile successfully after reruns.

---

## Files reviewed

The zip contains exactly three files:

1. `Qab_Lean_Roadmap.md`
2. `Qab_core_v2.tex`
3. `Qab_Phase0_Skeleton.lean`

The original source file `Qab(1).tex` is a 5164-line manuscript. The streamlined `Qab_core_v2.tex` is an 8-page Lean-oriented extraction of the proof architecture. The Lean file is a single 125-line phase-0 skeleton, not yet a Lake project.

---

## Mathematical audit

### 1. The streamlined proof spine is logically valid

The core theorem in `Qab_core_v2.tex` and `Qab_Phase0_Skeleton.lean` follows this structure:

```lean
PackageShare P Q
  → ∃ ce, FromShare P Q ce
  → ce.D ≤ 175394637
  → not (6816242 ≤ ce.D)
  → ce.D ≤ 6816241
  → UnitCoeff ∨ BothNonunit ∨ OneNonunit
  → contradiction by finite branch eliminations
```

This is a valid contradiction proof. The branch split covers all endpoint possibilities for positive `U,Vabs`, and the finite-elimination pack rules out every branch. Therefore, as a **conditional theorem from packs**, the proof is complete.

The corresponding original-paper branches are preserved:

| Original proof component                                                                    | Lean pack / field                               |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Collision dictionary, unit-circle removal, reciprocal orientations, primitive normalization | `CollisionPack.share_to_normCE`                 |
| Explicit bound `D ≤ 175394637`                                                              | `GlobalHeightPack.absolute_bound`               |
| Upper range `6816242 ≤ D ≤ 175394637` eliminated                                            | `FiniteEliminationPack.no_upper_counterexample` |
| Unit branch eliminated                                                                      | `FiniteEliminationPack.no_lower_unit`           |
| Both-nonunit branch eliminated                                                              | `FiniteEliminationPack.no_both_nonunit`         |
| One-nonunit, `D ≥ 16584`, eliminated                                                        | `FiniteEliminationPack.no_one_nonunit_large`    |
| Residual one-nonunit, `D ≤ 16583`, eliminated                                               | `FiniteEliminationPack.no_one_nonunit_residual` |

So the math has not been made invalid by the simplification. The proof has been compressed into theorem packs.

### 2. The streamlined core is not a proof of the hard mathematics

The Lean skeleton is an assembly theorem. It does not formalize the hard steps:

* collision extraction from actual polynomial gcds;
* construction of `Q_{a,b}`;
* equivalence between package sharing and selected orientation collisions;
* the height estimate;
* the rank-two torus degree argument;
* Smyth/Mahler gap or nonreciprocity;
* upper-range coverage;
* local p-adic/Kummer extraction;
* finite-state coverage;
* modular gcd certificate soundness.

That is fine if the milestone is explicitly “conditional formalization from named packs.” It would be misleading only if the generated theorem were presented as an unconditional formal proof.

### 3. The proof spine correctly removes ASZ/S-unit material from the Lean core

The original manuscript contains ASZ-style boundedness, S-unit finiteness, density-one isolation, sign/phase/Schur material, and other discovery/structural scaffolding. The core blueprint correctly identifies that the final contradiction can avoid most of this in the Lean top-level theorem.

The direct path retained by the core is:

1. collision normalization;
2. direct height–degree–Mahler bound;
3. upper finite elimination;
4. lower finite-state extraction;
5. finite branch eliminations.

That is a legitimate reduction of the proof dependency graph.

One caveat: the original unit Kummer-defect branch still uses global isolation of irreducible primitive bases for 46 certified shapes. If the Lean plan wants to avoid “global isolation” entirely, that branch needs to be replaced by a finite certificate route. The roadmap notices this as a review question, but it is not yet resolved.

---

## Lean skeleton audit

### 1. The core theorem is well shaped

The main Lean theorem:

```lean
theorem package_coprimality_from_packs
    (C : CollisionPack)
    (G : GlobalHeightPack)
    (L : LocalPacketPack)
    (F : FiniteEliminationPack) :
    ReciprocalPackageCoprimality
```

is the right target for phase 0.

The proof of `no_normCE_from_packs` is also structurally correct. It uses only:

* `G.absolute_bound`;
* `F.no_upper_counterexample`;
* `L.coeff_trichotomy`;
* the four lower finite eliminators;
* elementary natural-number case splitting at `6816241/6816242` and `16583/16584`.

This is exactly what a first conditional formalization should do.

### 2. Likely Lean syntax status

I could not type-check the file, but the syntax is mostly standard Lean 4 / Mathlib style.

The only places that may need minor API adjustment are these arithmetic steps:

```lean
have hlt : 6816241 < ce.D := lt_of_not_ge hnot
have hge : 6816242 ≤ ce.D := Nat.succ_le_of_lt hlt
```

and similarly for `16583/16584`.

These are likely fine, but if Mathlib API changes or elaboration struggles, replacing them by `omega` would be safer:

```lean
have hge : 6816242 ≤ ce.D := by omega
```

The roadmap’s pseudo-Lean already suggests `omega`; the skeleton uses `lt_of_not_ge` and `Nat.succ_le_of_lt`. Both approaches are reasonable.

### 3. The package is not yet a Lean project

The zip contains no:

* `lakefile.lean`;
* `lean-toolchain`;
* `Qab/` module tree;
* `README`;
* Mathlib version pin.

So the package is a blueprint plus a skeleton file, not yet a buildable repository. That is fine for a design draft, but the first implementation task should be to create a Lake project and split the skeleton into modules.

Minimum phase-0 repository:

```text
lean-toolchain
lakefile.lean
Qab/
  Basic.lean
  Counterexample.lean
  Packs/
    Collision.lean
    GlobalHeight.lean
    LocalPacket.lean
    FiniteElimination.lean
  CoreProof.lean
README.md
```

### 4. `FromShare` must not be `True`

This is the single most serious Lean-design issue.

The roadmap says:

```lean
def FromShare (P Q : PosPair) (ce : NormCE) : Prop := True
```

That is dangerous. If `FromShare := True`, then a broad finite-elimination axiom such as

```lean
no_lower_unit :
  ∀ {P Q ce},
    FromShare P Q ce → ce.D ≤ 6816241 → ce.UnitCoeff → False
```

becomes, effectively:

```lean
∀ ce, ce.D ≤ 6816241 → ce.UnitCoeff → False
```

But such `ce` are constructible. For example, one can make a dummy normalized counterexample with `D = 1`, `d = 1`, `U = 1`, `Vabs = 1`. Then `no_lower_unit` proves `False`.

So there are three safe options:

1. Keep `FromShare` opaque, as the skeleton currently does.
2. Define `FromShare` as a real structure containing actual root/collision data.
3. Do not instantiate the packs at all in phase 0; prove only the theorem parametrized by pack variables.

The safest phase-0 choice is:

```lean
constant FromShare : PosPair → PosPair → NormCE → Prop
```

Then later replace it with a structure.

### 5. `NormCE` is too thin for opening packs

The skeleton’s `NormCE` stores:

```lean
m n p q : Nat
D d U Vabs : Nat
hm_pos : 0 < m
hm_lt  : m < n
hp_pos : 0 < p
hp_lt  : p < q
hd_pos : 0 < d
hU_pos : 0 < U
hV_pos : 0 < Vabs
```

This is enough for the phase-0 assembly proof, but not enough for the next stage.

The roadmap correctly suggests adding:

```lean
hD : D = max (max m n) (max p q)
norm_gcd : Nat.gcd (Nat.gcd m n) (Nat.gcd p q) = 1
distinct_packages : Prop
```

I would add these earlier rather than later. The global height pack and field-degree proof need `D` to be tied to `m,n,p,q`, and the rank-two torus argument needs the primitive normalization.

A better phase-1 shape is:

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

  d U Vabs : Nat
  hd_pos : 0 < d
  hU_pos : 0 < U
  hV_pos : 0 < Vabs
```

Then `FromShare` should assert that these numbers come from a selected off-unit-circle noncyclotomic common root.

---

## Pack-boundary audit

### 1. `CollisionPack` is appropriate but should become concrete early

Current field:

```lean
share_to_normCE :
  ∀ {P Q : PosPair},
    P.unequal → Q.unequal → ¬ P.sameUnordered Q →
    PackageShare P Q → ∃ ce : NormCE, FromShare P Q ce
```

This is the right phase-0 abstraction. It corresponds to:

* defining package polynomials;
* proving unit-circle roots are exactly the removed cyclotomic roots;
* selecting one orientation from each package;
* using no-three to avoid complementary orientation confusion;
* normalizing common-root data.

The roadmap’s plan to define `primQZ` by positive coefficients is good. It avoids making polynomial division part of the computational kernel.

One implementation warning: avoid defining

```lean
def QabZ (a b : ℕ) : Polynomial ℤ := ...
```

without handling `a = 0` or `b = 0`. The theorem only uses positive pairs, so either define `QabZ` on `PosPair`, or make the zero cases explicit.

### 2. `GlobalHeightPack` is slightly inconsistent between files

`Qab_core_v2.tex` says the global height–degree pack includes both:

```text
D ≤ 175394637
```

and

```text
D ≥ 6816242 → U = 1, V0 = 1
```

The Lean skeleton’s `GlobalHeightPack` contains only:

```lean
absolute_bound :
  FromShare P Q ce → ce.D ≤ 175394637
```

This is not logically wrong, because the skeleton’s `FiniteEliminationPack.no_upper_counterexample` eliminates the entire upper range directly. But it changes the responsibility boundary.

There are two coherent designs:

Design A, broad upper finite pack:

```lean
GlobalHeightPack.absolute_bound :
  FromShare P Q ce → ce.D ≤ 175394637

FiniteEliminationPack.no_upper_counterexample :
  FromShare P Q ce →
  6816242 ≤ ce.D → ce.D ≤ 175394637 → False
```

Design B, narrower and closer to the paper:

```lean
GlobalHeightPack.absolute_bound :
  FromShare P Q ce → ce.D ≤ 175394637

GlobalHeightPack.upper_unit_normalized :
  FromShare P Q ce → 6816242 ≤ ce.D → ce.UnitCoeff

UpperRangePack.no_upper_unit_counterexample :
  FromShare P Q ce →
  ce.UnitCoeff →
  6816242 ≤ ce.D → ce.D ≤ 175394637 → False
```

Design B is better for later opening of packs, because the upper-range computation in the paper relies on unit normalization.

### 3. `LocalPacketPack.coeff_trichotomy` is too weak to represent the local theory

Current field:

```lean
coeff_trichotomy :
  FromShare P Q ce → ce.D ≤ 6816241 →
    ce.UnitCoeff ∨ ce.BothNonunit ∨ ce.OneNonunit
```

But this trichotomy is essentially arithmetic once `U,Vabs ≥ 1`. It does not encode the local p-adic/Kummer finite-state extraction. The real local theorem is not “one of three coefficient cases occurs”; it is “every counterexample maps to an admissible lower state satisfying all predicates consumed by the finite searches.”

For phase 0, this is harmless. For a meaningful conditional formalization, replace or extend it with something like:

```lean
structure LowerState where
  -- scales, primitive shapes, extraction degrees,
  -- endpoint coefficients, slope signatures, packet data, etc.

structure LocalPacketPack where
  to_lower_state :
    ∀ {P Q ce},
      FromShare P Q ce →
      ce.D ≤ 6816241 →
      ∃ st : LowerState, Encodes ce st ∧ AdmissibleLowerState st
```

Then the finite eliminators should consume `AdmissibleLowerState`, not just `FromShare`.

### 4. `FiniteEliminationPack` is logically valid but too broad for review

The current finite pack says, for example:

```lean
no_one_nonunit_residual :
  FromShare P Q ce → ce.OneNonunit → ce.D ≤ 16583 → False
```

The original residual computation is narrower: after reciprocal normalization, it enumerates

```text
D ≤ 16583,
|V| = 1,
2 ≤ U ≤ D,
d ≤ 2601,
```

plus endpoint valuations, deficient-prime restrictions, extraction-degree data, slope signatures, total-radical constraints, and finite-state predicates.

The broad field is mathematically valid if it is understood as bundling all those reductions. But it is not ideal for auditing. A reviewer cannot see whether the residual computation is being applied only inside its certified envelope.

A better eventual split is:

```lean
LocalPacketPack.residual_envelope :
  FromShare P Q ce →
  ce.OneNonunit →
  ce.D ≤ 16583 →
  ∃ ce', ReciprocalNormalize ce ce' ∧
    ce'.U > 1 ∧ ce'.Vabs = 1 ∧
    2 ≤ ce'.U ∧ ce'.U ≤ ce'.D ∧
    ce'.d ≤ 2601 ∧
    ∃ st, Encodes ce' st ∧ ResidualState st

FiniteResidualPack.no_residual_state :
  ResidualState st → False
```

This would make the residual computation visibly certificate-based rather than axiomatically branch-based.

---

## Certificate and computation audit

The original paper’s computational proof is reproducible-source based, not Lean-certified. The roadmap correctly recognizes that a Lean version must not trust C++ or Python loops as proof.

The key certificate requirements are:

### 1. Coverage certificates are more important than terminal gcds

Terminal modular gcd certificates are relatively easy to check in Lean. The harder part is proving that every possible counterexample reaches one of the terminal rows.

The roadmap’s proposed `IntervalCert`, `ExclusionReason`, and coverage soundness theorems are the right direction. For upper-range and large branch computations, Lean should verify coverage by explicit interval/branch certificates, not by replaying an external loop.

### 2. Modular gcd certificates need explicit good-reduction hypotheses

For a terminal certificate over `ZMod p`, Lean must prove a statement of this shape:

```lean
if h ∈ ℤ[x] is primitive and nonconstant,
h ∣ F and h ∣ G over ℚ[x],
and p is a good reduction prime,
then h mod p divides gcd(F mod p, G mod p).
```

The “good reduction” hypotheses must include at least:

* `p` is prime;
* relevant leading coefficients do not vanish modulo `p`;
* the primitive common factor does not reduce to zero or lose all positive degree;
* contents are controlled;
* the forced cyclotomic part is identified and removed or separately accounted for.

This matters especially because the manuscript’s residual certificates compute modular gcd degree `2` for collision trinomials, with degree `2` accounted for by the forced double root at `x = 1`. In Lean, the certificate must say precisely whether it is checking `H_{m,n}` or the divided `Q_{a,b}`, and why a degree-2 forced factor leaves no noncyclotomic common factor.

### 3. The residual branch is the right first certificate target

The roadmap proposes starting with the residual terminal certificates over `𝔽_1009`. That is sensible. The residual branch is small enough to exercise all key infrastructure:

* reconstruct package polynomials;
* reduce modulo `1009`;
* verify gcd or Bezout identities;
* handle the forced cyclotomic factor;
* prove terminal row exclusion.

After that, expand to residual row coverage, then larger branches.

---

## Specific Lean engineering recommendations

### 1. Add a real project scaffold immediately

The package should include:

```text
lean-toolchain
lakefile.lean
Qab/Basic.lean
Qab/Counterexample.lean
Qab/Packs/*.lean
Qab/CoreProof.lean
```

Pinning Mathlib is important. Otherwise even a correct skeleton can rot quickly.

### 2. Keep all temporary assumptions visible

The roadmap says temporary axioms should live in `Qab/Packs/BroadAxioms.lean`. I agree, but with one restriction: do not define impossible broad pack instances over `FromShare := True`.

A safe pattern is:

```lean
axiom temporary_collision_pack : CollisionPack
axiom temporary_global_height_pack : GlobalHeightPack
axiom temporary_local_packet_pack : LocalPacketPack
axiom temporary_finite_elimination_pack : FiniteEliminationPack
```

only if `FromShare` is opaque and no dummy `FromShare` proofs are constructible.

### 3. Make `PackageShare` concrete soon

The phase-0 theorem can use an opaque `PackageShare`, but the next milestone should define it as:

```lean
def NonconstantFactor (h : Polynomial ℚ) : Prop :=
  0 < h.natDegree

def PackageShare (P Q : PosPair) : Prop :=
  ∃ h : Polynomial ℚ,
    NonconstantFactor h ∧ h ∣ packageQ P ∧ h ∣ packageQ Q
```

Then later prove the equivalence with gcd-coprimality over `ℚ[x]`.

### 4. Define the polynomial by coefficients, not division

The roadmap’s coefficient formula is the right Lean choice:

[
Q^{\rm prim}*{A,B}(x)=
\sum*{0\le j<A}B(j+1)x^j+
\sum_{A\le j\le A+B-2}A(A+B-j-1)x^j.
]

This should be implemented before certificate work begins, because all row and modular-gcd certificates need canonical polynomial constructors.

### 5. Add arithmetic lemmas for the boundary cuts

The proof uses two natural-number dichotomies:

```lean
¬ ce.D ≤ 6816241 → 6816242 ≤ ce.D
¬ ce.D ≤ 16583 → 16584 ≤ ce.D
```

These can be handled by `omega`, but it may be useful to add named lemmas for readability:

```lean
lemma ge_6816242_of_not_le_6816241 {D : Nat} :
    ¬ D ≤ 6816241 → 6816242 ≤ D := by omega

lemma ge_16584_of_not_le_16583 {D : Nat} :
    ¬ D ≤ 16583 → 16584 ≤ D := by omega
```

### 6. Rename the “local trichotomy” field

Since the current `coeff_trichotomy` is almost arithmetic, I would not let it stand as the main local p-adic theorem. Either prove it directly from `hU_pos` and `hV_pos`, or rename the serious local theorem to something like:

```lean
to_admissible_lower_state
```

This makes the true mathematical content visible.

---

## Completeness relative to the original proof

The compressed proof package covers the final contradiction. I do not see a missing branch in the high-level logic. In particular:

* upper range is eliminated;
* lower unit branch is eliminated;
* lower both-nonunit branch is eliminated;
* one-nonunit branch above `16583` is eliminated;
* residual one-nonunit branch at `D ≤ 16583` is eliminated;
* reciprocal normalization handles the orientation choice for the one-nonunit residual case.

The places that need explicit traceability before heavy Lean work are:

1. `CollisionPack.share_to_normCE` must cover all common factors of reciprocal package products, including the swapped orientation and imprimitive composition `Q_{rA,rB}(x)=rQ_{A,B}(x^r)`.
2. The upper-range finite pack must either include or depend on the upper unit-normalization theorem.
3. The residual one-nonunit eliminator must document the reciprocal normalization step and the reductions to `|V|=1`, `2 ≤ U ≤ D`, and `d ≤ 2601`.
4. The Kummer-defect unit branch must be assigned either to a theorem pack using the original global-isolation argument or to a new finite certificate pack.
5. Modular gcd certificates must include good-reduction soundness, not just computed gcd degrees.

---

## Recommended revised phase-0 acceptance criterion

I would adjust the phase-0 definition of done as follows:

A phase-0 repository is acceptable when:

1. `package_coprimality_from_packs` compiles in Lake.
2. `FromShare` is opaque or a real structure, not `True`.
3. No global theorem is named as unconditional unless it takes packs as parameters.
4. All temporary axioms live in `BroadAxioms.lean`.
5. `NormCE` includes at least `hD` and `norm_gcd`, or `FromShare` includes them.
6. `GlobalHeightPack`, `UpperRangePack`, `LocalPacketPack`, and `FiniteEliminationPack` have comments mapping each field to the relevant theorem/section of `Qab(1).tex`.
7. The README explicitly states: “This is a conditional formalization from theorem packs, not a Lean-certified proof of the packs.”

---

## Bottom line

The package is a **sound and useful blueprint** for a first conditional Lean formalization. The core theorem is the right theorem, the proof skeleton is the right proof, and the high-level mathematical reduction has not lost any decisive branch of the original argument.

But before using this as the basis for serious Lean work, I would make three changes:

1. **Do not define `FromShare := True`.** Keep it opaque or make it a real normalized-counterexample predicate.
2. **Strengthen the local/finite interface.** The current finite pack is logically valid but too broad for long-term trust; introduce `LowerState`, `Encodes`, and `AdmissibleLowerState`.
3. **Split the upper and residual packs more faithfully.** The upper elimination should expose unit normalization, and the residual eliminator should expose the residual envelope and reciprocal normalization.

With those changes, this is a realistic work package for obtaining a first conditional Lean formalization, and it gives a credible path toward replacing the broad packs by Mathlib proofs and Lean-checkable finite certificates.
