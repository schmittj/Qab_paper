# Publication Checklist

Run these commands from a clean checkout before public release.

## Environment

Use either the host system with the pinned optional Python packages:

```bash
python3 -m pip install -r requirements-optional.txt
```

or the included container:

```bash
docker build -t qab-proof .
docker run --rm qab-proof
```

The C++ tools require GCC or Clang with OpenMP and GNU `__int128` support.

## Required Checks

```bash
make paper
sha256sum -c SHA256SUMS --quiet
make verify-light
make verify-upper
make verify-unit
```

`make verify-light` is non-FLINT and non-mutating.  It rebuilds the
proof-critical nonunit C++ tools, checks the constants, verifies the nonunit
branches, checks the unit-branch manifest, and runs small coverage oracles.

`make verify-unit` requires `python-flint`; it first checks the stored
unit-branch manifest and then recomputes the modular gcd and direct
irreducibility certificates.

## Expected Terminal Counts

- Upper verifier: `verified_shapes=237418`, `verified_prefinal_pairs=761`,
  `verified_residual_candidates=0`.
- One-nonunit residual verifier: `residual_unique_state_pairs=4`,
  `residual_unique_orientation_pairs=2`,
  `verified_residual_orientation_certificates=8`.
- Unit manifest verifier: `large_terminal_package_pairs=7`,
  `small_terminal_package_pairs=3`, `defect_irreducibility_shapes=46`.

All verification commands should end with `status=PASS`.
