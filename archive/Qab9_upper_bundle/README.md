# Qab9 review bundle

This bundle contains the revised mathematical note and the exact computation used to eliminate the unit-normalized portion of the finite box.

## Mathematical status

The analytic argument in `Qab9.tex` bounds every normalized counterexample by

```
D = max(m,n,p,q) <= 175394637.
```

The new computer-assisted theorem eliminates the complete range

```
6816242 <= D <= 175394637,
```

so any normalized counterexample must satisfy

```
D <= 6816241.
```

This is **not yet a proof of the full conjecture**. In the remaining lower range the common factor may be nonunit, and endpoint internal-power branches must still be classified. The endpoint theorem reduces their exceptional primes to `2,3,5,7`.

The main upper-range computation is exact: it uses integer and rational arithmetic only, constructs no large polynomial, and invokes no irreducibility oracle or finite-field factorization.

## Files

- `Qab9.tex`, `Qab9.pdf`: integrated note and compiled PDF.
- `code/enumerate_shapes.cpp`: exhaustive radical-bounded primitive-shape generator.
- `code/pair_upper.cpp`: exact upper-range pair sieve.
- `code/same_shape_screen.py`: final same-shape Bézout screen.
- `code/certify_constants.py`: exact rational certificates for the new constants.
- `code/verify_upper.py`: independent row-by-row verifier for the recorded CSV data.
- `code/test_small.py`: small-box brute-force and arithmetic regression tests.
- `code/factor_through_60.py`: parallel exact SymPy factorization check for all 870 packages through total 60.
- `code/postfilter_upper.py`, `code/modular_screen.py`, `code/gcd_orientation_worker.py`: optional deeper finite-field and modular-GCD diagnostics; they are not used in the upper proof.
- `data/upper_shapes.csv`: all 237,418 radical-admissible primitive shapes.
- `data/upper_pair_survivors.csv`: the 761 rows surviving all pre-Bézout upper sieves.
- `data/upper_residual_candidates.csv`: header-only output after the final screen.
- `docs/MATHEMATICAL_CERTIFICATE.md`: map from mathematical lemmas to code conditions.
- `docs/COMPUTATIONAL_PIPELINE.md`: implementation and reproducibility details.
- `docs/LOWER_RANGE_PLAN.md`: proposed next attack on the remaining finite range.
- `docs/REVIEW_CHECKLIST.md`: focused review points and trust boundary.
- `docs/REVISION_NOTES.md`: integrated mathematical and computational changes, including the support-index audit correction.
- `MANIFEST.md`, `SHA256SUMS`: package inventory and integrity hashes.

## Reproduce the upper proof

Requirements for the main pipeline:

- a C++20 compiler;
- OpenMP;
- Python 3 using only the standard library.

Run:

```bash
make clean
make upper THREADS=25
make verify
```

The expected terminal counts are recorded in `data/upper_pipeline_output.txt`. The final lines are:

```text
after_full_radical_CRT=761
same_shape_rows=761
eliminated_by_degree_lower_gt_2rs=761
residual_candidates=0
```

For development tests and the independent total-60 factorization, install `requirements-dev.txt` and run:

```bash
make test
make factor60 THREADS=25
```

The optional modular backend requires `requirements-optional.txt`.

## Typical resources

On the current 25-thread environment, the shape generator took about 9 seconds and peaked near 714 MB; the corrected pair sieve took about 30 seconds and peaked near 159 MB; the independent total-60 factorization took about 13 seconds and peaked near 328 MB. Hardware and compiler differences will change these figures. The full proof pipeline is far below a seven-day budget.

## Trust boundary

The supplied Python verifier independently checks every shape row and every one of the 761 pre-final rows. The large-pair **coverage** is presently established by inspection and rerunning of the concise C++ enumeration loop, supported by small-box brute-force regression tests. A Lean-oriented version should replace this source-level trust boundary with branch or interval coverage certificates.
