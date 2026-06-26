# Qab12 runbook

## Build C++ tools

```bash
make q12-build
```

The default build expects GCC or Clang with OpenMP and GNU `__int128`
support (`-std=gnu++20`).

## Light verification

```bash
make q12-verify-light
```

This reruns exact constant checks, the two-nonunit row verifier, the
one-nonunit row/count verifier, the residual one-nonunit verifier, and the
small brute-force oracles.

## Modular certificate verification

```bash
make q12-verify-modular
```

Requires `python-flint`. It recomputes the modular gcd certificates for the unit large and small terminal pairs.
Install the pinned optional environment with:

```bash
python3 -m pip install -r requirements-optional.txt
```

## Direct irreducibility verification

```bash
make q12-verify-irreducibility-direct
```

Requires `python-flint`. It recomputes the modular factorization degrees for the unit-defect irreducibility certificates.

## Reproduce the all-shapes one-nonunit run

```bash
make q12-one-nonunit-all THREADS=25
```

This reruns the `U=2,...,26` branch for `D >= 16,584`. The corrected small
branch is reproduced by the residual target below.

## Reproduce the residual one-nonunit run

```bash
make q12-one-nonunit-residual THREADS=25
```

This reruns the corrected residual branch
`D <= 16,583`, `|V| = 1`, `2 <= U <= D`, `d <= 2601`,
builds the terminal modular certificates, and verifies the resulting manifest.
