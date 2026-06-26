# Qab12 runbook

## Build C++ tools

```bash
make q12-build
```

## Light verification

```bash
make q12-verify-light
```

This reruns exact constant checks, the two-nonunit row verifier, the one-nonunit row/count verifier, and the small brute-force oracles.

## Modular certificate verification

```bash
make q12-verify-modular
```

Requires `python-flint`. It recomputes the modular gcd certificates for the unit large and small terminal pairs.

## Direct irreducibility verification

```bash
make q12-verify-irreducibility-direct
```

Requires `python-flint`. It recomputes the modular factorization degrees for the unit-defect irreducibility certificates.

## Reproduce the all-shapes one-nonunit run

```bash
make q12-one-nonunit-all THREADS=25
```

This reruns the `U=2,...,26` branch for `D >= 16,584`. It is not the remaining small branch.
