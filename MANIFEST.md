# Qab bundle manifest overview

The main byte-level checksum list is `SHA256SUMS`; the broader JSON inventory
is `ARTIFACT_MANIFEST.json`.  The checksum list intentionally excludes itself,
`ARTIFACT_MANIFEST.json`, and the nested archived
`archive/Qab9_upper_bundle/SHA256SUMS`.

Key deterministic outputs:

- `data/qab12/qab12_branch_summary.json`
- `data/qab12/qab12_constants_output.txt`
- `data/qab12/two_nonunit_packages.csv`
- `data/qab12/two_nonunit_state_pairs.csv`
- `data/qab12/one_nonunit_all_packages_U*.csv`
- `data/qab12/one_nonunit_all_state_pairs_U*.csv`
- `data/qab12/one_nonunit_residual_packages.csv`
- `data/qab12/one_nonunit_residual_state_pairs.csv`
- `data/qab12/one_nonunit_residual_orientation_pairs.csv`
- `data/qab12/one_nonunit_residual_modular_certificates.csv`
- `data/qab12/one_nonunit_residual_manifest.json`
- `data/qab12/unit_branch_manifest.json`
- `data/qab12/unit_large_modular_certificates.csv`
- `data/qab12/unit_small_modular_certificates.csv`
- `data/qab12/unit_defect_irreducibility_certificates.jsonl`
- `logs/qab_verify_light_final.txt`
- `logs/qab_verify_unit_final.txt`
- `logs/qab_verify_upper_final.txt`

The one-nonunit `D >= 16,584` branch is intentionally represented by per-coefficient files `U=2,...,26`; all state-pair and orientation-pair CSVs are header-only.
The corrected residual one-nonunit branch is represented by a single
five-signature-slot package catalogue, four terminal state pairs, two terminal
package pairs, and eight modular gcd certificates.
The unit branch is represented by `unit_branch_manifest.json`, terminal
modular gcd certificates for the full-Kummer large/small cases, and 46 direct
irreducibility certificates for the deficient-scale-prime case.
