# Qab12 review bundle

This bundle is a reviewable proof package for the `Q_{a,b}` reciprocal-package project.

## Current proof status

The bundle contains artifacts supporting the following eliminations:

1. the previously audited upper range `6,816,242 <= D <= 175,394,637`;
2. the complete unit-coefficient lower branch;
3. the both-coefficients-nonunit branch;
4. the one-nonunit branch with `D >= 16,584`;
5. the corrected residual one-nonunit branch
   `D <= 16,583`, `|V| = 1`, `2 <= U <= D`, `d <= 2601`.

The residual run enumerates 233,278 conservative package states, leaves four
terminal state pairs, and eliminates the two terminal package pairs by eight
modular gcd certificates at `p = 1009`.

## Main files

- `Qab12.tex`, `Qab12.pdf`: integrated manuscript.
- `code/qab12/`: current Qab12 source code and verification scripts.
- `data/qab12/`: deterministic outputs and proof artifacts from the current work round.
- `archive/Qab9_upper_bundle/`: audited upper-range code/data retained for self-containment.
- `Qab12_audit_report.md`, `Qab13_audit.md`: current-stage external audit reports.
- `docs/audits/`: earlier independent audit reports supplied by the user.
- `SHA256SUMS`: hashes of every file in this bundle, excluding itself.

## Quick verification commands

From the bundle root:

```bash
make q12-verify-light
make q12-verify-modular     # requires python-flint
make q12-verify-upper       # verifies archived upper rows
```

The C++ tools are intended for GCC or Clang with OpenMP and GNU `__int128`
support; the default Makefile uses `-std=gnu++20`. Optional Python
dependencies for the modular and irreducibility replays are pinned in
`requirements-optional.txt`.

The corrected residual branch can be regenerated with

```bash
make q12-one-nonunit-residual THREADS=25
```

The long direct modular irreducibility verifier can be run with

```bash
make q12-verify-irreducibility-direct
```

This last command may take longer depending on the local FLINT build.
