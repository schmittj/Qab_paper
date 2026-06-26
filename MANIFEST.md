# Qab12 bundle manifest overview

The authoritative byte-level manifest is `SHA256SUMS`.

Key deterministic outputs:

- `data/qab12/qab12_branch_summary.json`
- `data/qab12/qab12_constants_output.txt`
- `data/qab12/two_nonunit_packages.csv`
- `data/qab12/two_nonunit_state_pairs.csv`
- `data/qab12/one_nonunit_all_packages_U*.csv`
- `data/qab12/one_nonunit_all_state_pairs_U*.csv`
- `data/qab12/unit_large_modular_certificates.csv`
- `data/qab12/unit_small_modular_certificates.csv`
- `data/qab12/unit_defect_irreducibility_certificates.jsonl`

The one-nonunit `D >= 16,584` branch is intentionally represented by per-coefficient files `U=2,...,26`; all state-pair and orientation-pair CSVs are header-only.
