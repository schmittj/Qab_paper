# Lean Certificate Generators

## `coverage_csv_to_lean.py`

`coverage_csv_to_lean.py` is the Phase 3 interval-coverage emitter.  It reads a
CSV with closed natural-number interval endpoints and emits typed Lean terms
against `Qab.Certificates.Coverage`.

Minimal use:

```bash
python3 Qab_Lean_v4/scripts/coverage_csv_to_lean.py intervals.csv \
  --name residualD \
  --target-lo 0 \
  --target-hi 16583 \
  --lo-column lo \
  --hi-column hi \
  --output Qab_Lean_v4/Qab/Generated/ResidualD.lean
```

The generated file defines:

- `<name>Intervals : List Qab.CoverageInterval`;
- `<name>Cert : Qab.CoverageCert`, with `auditId` as metadata only;
- `<name>Covers : Qab.CoversClosedTarget <name>Intervals lo hi`, proved by
  `Qab.checkCoverage_sound (by native_decide)`.

Rows are sorted by `(lo, hi)` before emission unless `--preserve-order` is
passed.  Large files are emitted as chunks of 1000 intervals by default; use
`--chunk-size 0` for a single list.  The proof-relevant check is always the
Lean checker, not the CSV order, filename, hash, or audit id.
