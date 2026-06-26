# Agent Notes

## Project

This repository is a review/proof bundle for the `Q_{a,b}` reciprocal-package
project.  It combines a LaTeX manuscript with deterministic C++/Python
computations and stored verification artifacts.

The manuscript is `Qab.tex`; `Qab.pdf` is the rendered copy.  Current source
code lives in `code/qab12/`, generated proof artifacts live in `data/qab12/`,
and replay logs live in `logs/`.  Those internal directory names are retained
for provenance from the completed computation stage.  Older audited Qab9-Qab11
materials are kept under `archive/`; independent audit reports are in
`docs/audits/`.

## Current Status

The current bundle has eliminated these branches:

- the archived upper range `6,816,242 <= D <= 175,394,637`;
- the lower-box unit-coefficient branch;
- the both-nonunit endpoint-coefficient branch;
- the one-nonunit branch for `D >= 16,584`.

The audit of the previous numbered stage found that the older residual cap
`d <= 224` was not justified for the one-nonunit branch.  The corrected
residual branch uses the safe bound `D <= 16,583`, `|V| = 1`,
`2 <= U <= D`, and `d <= 2601`; it is now handled by
`code/qab12/enumerate_one_nonunit_residual_packages.cpp`,
`code/qab12/pair_one_nonunit_residual.cpp`, and
`code/qab12/verify_one_nonunit_residual.py`.

The residual artifacts are:

- `data/qab12/one_nonunit_residual_packages.csv`
- `data/qab12/one_nonunit_residual_state_pairs.csv`
- `data/qab12/one_nonunit_residual_orientation_pairs.csv`
- `data/qab12/one_nonunit_residual_modular_certificates.csv`
- `data/qab12/one_nonunit_residual_manifest.json`

## Verification Commands

From the repository root:

```bash
make verify-light
make verify-upper
make verify-modular
make verify-irreducibility-direct
make one-nonunit-residual THREADS=25
```

The modular and direct irreducibility verifiers require `python-flint`.  The
light verifier rebuilds the main C++ tools and checks the constants,
two-nonunit rows, one-nonunit `D >= 16584` rows, and small regression oracles.

## Development Notes

Prefer preserving the existing proof-artifact style: C++ generators/pair
sieves emit CSV/TXT artifacts under `data/qab12/`, and Python verifiers replay
those artifacts from first principles as much as possible.  Do not remove or
rewrite archived Qab9-Qab11 materials unless specifically asked.

The private GitHub backup remote is `origin` at
`git@github.com:schmittj/Qab_paper.git`.
