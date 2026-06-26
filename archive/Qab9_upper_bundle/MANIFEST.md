# Qab9 review bundle manifest

## Principal artifacts

- `Qab9.tex` - integrated mathematical note.
- `Qab9.pdf` - compiled 59-page PDF.
- `README.md` - entry point and reproduction commands.
- `SHA256SUMS` - checksums for all other files in the bundle.

## Exact upper-range proof code

- `code/certify_constants.py` - exact rational/integer constant certificates.
- `code/enumerate_shapes.cpp` - exhaustive primitive-shape generator.
- `code/pair_upper.cpp` - scale-pair and arithmetic sieve.
- `code/same_shape_screen.py` - final same-shape Bezout exclusion.
- `code/verify_upper.py` - independent row verifier.
- `code/test_small.py` - regression and small-box completeness tests.

## Independent and future-facing code

- `code/certify_thresholds.sage` - independent interval check of analytic thresholds.
- `code/factor_through_60.py` - exact parallel factorization through total 60.
- `code/lower_exception_catalog.py` - lower-range endpoint-prime catalogue.
- `code/postfilter_upper.py` - optional stronger factor-degree diagnostic.
- `code/modular_screen.py`, `code/gcd_orientation_worker.py` - optional modular-gcd backend.

## Data and logs

- `data/upper_shapes.csv` - 237,418 generated shapes.
- `data/upper_pair_survivors.csv` - 761 rows before the final same-shape screen.
- `data/upper_residual_candidates.csv` - header-only zero-survivor file.
- `data/upper_pipeline_output.txt` - stage counts and exact constants.
- `data/verification_output.txt` - independent verifier output.
- `data/test_output.txt` - regression-test output.
- `data/reproducibility_checks.txt` - deterministic CSV rerun checks.
- `data/factor60_output.txt` - total-60 factorization result.
- `data/lower_exception_catalog.txt` - exceptional endpoint-prime catalogue.
- `data/resource_usage.txt` - indicative runtime and memory measurements.

## Review documentation

- `docs/MATHEMATICAL_CERTIFICATE.md` - map from propositions to code conditions.
- `docs/COMPUTATIONAL_PIPELINE.md` - implementation details.
- `docs/LOWER_RANGE_PLAN.md` - remaining lower-range program.
- `docs/REVIEW_CHECKLIST.md` - high-priority audit points.
- `docs/REVISION_NOTES.md` - changes from Qab8 and the support-index correction.
