# Verification runbook

## Build C++ tools

```bash
make build-nonunit-light
```

This builds the proof-critical nonunit C++ tools used by the light verifier.
The default build expects GCC or Clang with OpenMP and GNU `__int128` support
(`-std=gnu++20`).

## Light verification

```bash
make verify-light
```

This reruns exact constant checks, the two-nonunit row verifier, the
one-nonunit row/count verifier, the residual one-nonunit verifier in
non-mutating manifest-check mode, the unit-branch manifest verifier, and the
small brute-force oracles.

## Full unit-branch verification

```bash
make verify-unit
```

Requires `python-flint`. It checks the stored unit-branch manifest, recomputes
the modular gcd certificates for the unit large and small terminal pairs, and
recomputes the modular factorization degrees for the unit-defect
irreducibility certificates.

## Modular certificate verification

```bash
make verify-modular
```

Requires `python-flint`. It recomputes the modular gcd certificates for the unit large and small terminal pairs.
Install the pinned optional environment with:

```bash
python3 -m pip install -r requirements-optional.txt
```

## Direct irreducibility verification

```bash
make verify-irreducibility-direct
```

Requires `python-flint`. It recomputes the modular factorization degrees for the unit-defect irreducibility certificates.

## Reproduce the all-shapes one-nonunit run

```bash
make one-nonunit-all THREADS=25
```

This reruns the `U=2,...,26` branch for `D >= 16,584`. The corrected small
branch is reproduced by the residual target below.

## Reproduce the residual one-nonunit run

```bash
make one-nonunit-residual THREADS=25
```

This reruns the corrected residual branch
`D <= 16,583`, `|V| = 1`, `2 <= U <= D`, `d <= 2601`,
builds the terminal modular certificates, and verifies the resulting manifest.
