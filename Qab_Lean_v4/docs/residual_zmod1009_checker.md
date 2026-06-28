# Residual ZMod 1009 Checker

This branch adds the first Phase 2 residual modular-gcd checker and its
semantic terminal-exclusion bridge:

- `Qab.Certificates.ZModGcd`
- `Qab.Certificates.ResidualZMod1009`
- `Qab.Certificates.CollisionBezout`
- `Qab.Certificates.ResidualBezout1009`
- `Qab.Certificates.ResidualTerminalExclusion`

`Qab.Certificates.Targets` contains the shared `PolynomialCheckTarget` enum, so
the concrete checker does not import the schematic certificate axioms from
`Qab.Certificates.Interfaces`.

## Target

The checked target is `PolynomialCheckTarget.collisionH`, the undivided
orientation-level collision trinomial

```text
low * X^(scale * total) - total * X^(scale * low) + (total - low).
```

`Qab.Certificates.ZModGcd.collisionHMod` is defined by mapping
`Qab.Polynomials.Collision.collisionTriZ` into `ZMod 1009`; the lemma
`collisionHMod_eq_sparse` records that this is the sparse trinomial used by the
executable dense checker.

The dense executable representation is also connected to this polynomial target
by `denseToPoly_collisionDense_eq_collisionHMod`, which proves that
`denseToPoly (collisionDense scale low total)` denotes the mapped
`collisionTriZ` target.

## Forced Factor Accounting

The checker does not treat an undivided gcd degree of `2` as an exclusion by
itself.  It records `forcedDoubleRootDegree = 2`, checks coprime residual
scales both in the generic `CollisionCertificate.wellFormed` predicate and in
the typed row data, and
`CollisionCertificate.checks` requires

```text
exactGcdDegree = forcedCyclotomicDegree.
```

The forced factor is linked back to the shared prelude by
`collisionTriZ_X_sub_one_sq_dvd_of_low_lt_total`, a wrapper around
`collisionTriZ_X_sub_one_sq_dvd`, and
`collisionHMod_X_sub_one_sq_dvd_of_low_lt_total`, its reduction modulo `1009`.
For these residual rows the scales in each pair are coprime, so the common
forced factor is the double root `(X - 1)^2`, of degree `2`.

## Executable Checker

The gcd computation uses a small dense coefficient-list implementation over
residues modulo `1009`, with the same Euclidean loop as the Python verifier.
It constructs dense lists from the collision-trinomial formula and checks the
computed gcd degree against the typed certificate row.

The current residual artifact set is small enough to type directly: two
orientation-pair rows and eight orientation certificates from
`data/qab12/one_nonunit_residual_orientation_pairs.csv` and
`data/qab12/one_nonunit_residual_modular_certificates.csv`.

`ResidualZMod1009.allRowsCheck_eq_true` checks:

- every certificate row matches its indexed orientation-pair row;
- the orientation low terms agree with the CSV convention;
- the additive triples hold;
- the primitive additive triples and residual degree bound hold;
- the two residual scales are coprime;
- the reduction prime is `1009` and is not a bad-reduction prime for row data;
- the executable collision-gcd degree is exactly `2`;
- the forced degree is exactly `2`, so there is no noncyclotomic room.

`ResidualZMod1009.listedPairOrientationCoverageComplete_eq_true` separately
checks that the typed data covers each listed pair/orientation task exactly
once.  `ResidualZMod1009.listedCountsMatchManifest_eq_true` records the current
manifest-level counts: two listed residual orientation pairs and eight listed
orientation certificates.

## Semantic Bezout Bridge

The executable dense gcd checker is retained as a useful audit/replay path, but
the mathematical terminal-exclusion path now uses generated Bezout identities.
`Qab.Certificates.CollisionBezout` proves a dense-arithmetic kernel sound
against Mathlib polynomials: a checked identity

```text
u * collisionH₁ + v * collisionH₂ = (X - 1)^2
```

implies that every common divisor of the two mapped collision trinomials
divides the forced double root.  `Qab.Certificates.ResidualBezout1009` contains
the generated witnesses for the eight current residual terminal rows and checks
them by `native_decide`; it is regenerated from the CSV artifact by
`Qab_Lean_v4/scripts/residual_bezout_to_lean.py`.

`Qab.Certificates.ResidualTerminalExclusion` is the Phase 2 theorem layer.  It
defines the conditional predicate

```text
NonforcedMod1009 h := ¬ reduceZMod 1009 h ∣ (X - 1)^2
```

for primitive integer representatives of rational factors.  Using
`GoodReduction.int_dvd_of_rat_dvd`, it proves that any primitive rational common
factor of a checked residual collision pair reduces modulo `1009` to a divisor
of `(X - 1)^2`; hence every factor satisfying `NonforcedMod1009` is excluded.
The theorem `ResidualRows.residualTerminalExclusionSet` packages this exclusion
for all eight generated residual certificates and records that they match the
typed residual rows.

## Scaling Notes

The dense Euclidean checker is intentionally still present because it mirrors
the original verifier and is useful for row auditing.  It is no longer the
mathematical trust boundary for the current eight residual terminal rows; the
semantic path is the generated Bezout identity plus
`ResidualTerminalExclusion`.

The remaining contracts now sit outside Phase 2 terminal certificates:

- later package/orientation integration must produce a primitive integer
  representative `h` of the rational common factor and prove divisibility of
  `h.map ℚ` into both relevant `collisionTriZ` targets;
- the same integration layer must prove `NonforcedMod1009 h` for that factor
  (for example via the degree helper
  `nonforcedMod1009_of_natDegree_gt_two`, or a later low-degree forced-factor
  classifier);
- Phase 3 residual-state coverage must prove that every residual counterexample
  reaches one of the terminal rows.
