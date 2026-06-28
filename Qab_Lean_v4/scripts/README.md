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
- `<name>AuditId : String`, with `auditId` as metadata only;
- `<name>Check`, a Lean-checked Boolean coverage computation;
- `<name>Covers : Qab.CoversClosedTarget <name>Intervals lo hi`, proved from
  the checker soundness theorem.

Rows are sorted by `(lo, hi)` before emission unless `--preserve-order` is
passed.  Large files are emitted as chunks of 1000 intervals by default; use
`--chunk-size 0` for a single list.  For chunked output, the generator emits
per-chunk `Qab.advanceFrom` checks and then stitches them with
`Qab.checkCoverageViaAdvance_sound`, so each expensive computation is local to
one chunk.

Before writing Lean, the script runs a non-trusted Python sweep that mirrors the
Lean checker and reports the first uncovered target point.  This is only a
diagnostic; the proof-relevant check is always the Lean checker, not the Python
preflight, CSV order, filename, hash, or audit id.  Use `--skip-preflight` only
when deliberately emitting a file that may fail to build.
