# Residual ZMod 1009 Checker

This branch adds the first Phase 2 residual modular-gcd checker:

- `Qab.Certificates.ZModGcd`
- `Qab.Certificates.ResidualZMod1009`

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

## Forced Factor Accounting

The checker does not treat an undivided gcd degree of `2` as an exclusion by
itself.  It records `forcedDoubleRootDegree = 2`, and
`CollisionCertificate.checks` requires

```text
exactGcdDegree <= forcedCyclotomicDegree.
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
- the reduction prime is `1009` and is not a bad-reduction prime for row data;
- the executable collision-gcd degree is exactly `2`;
- the forced degree is exactly `2`, so there is no noncyclotomic room.

`ResidualZMod1009.coverageComplete_eq_true` separately checks that the typed
data covers each listed pair/orientation task exactly once.

## Scaling Notes

This is intentionally a first useful kernel-checked certificate, not the final
large-scale format.  The dense Euclidean checker is simple and transparent but
would become expensive if the residual artifact grows by orders of magnitude.
For larger data, the likely next step is generated Euclidean or Bezout
certificates with a checker that verifies division identities, rather than
recomputing long dense gcds from scratch.
