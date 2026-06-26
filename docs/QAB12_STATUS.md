# Qab12 status and branch boundary

## Eliminated in this bundle

### Unit branch

- Large full-Kummer branch: terminal package pairs verified by modular gcd certificates.
- Small full-Kummer branch: terminal package pairs verified by modular gcd certificates.
- Unit Kummer-defect branch: 46 primitive shapes certified irreducible by modular factor-degree subset-sum certificates.

### Both nonunit endpoint coefficients

The strengthened constants give `D <= 16,583`, `d <= 224`, and endpoint valuation at most 14. The generator enumerates 1,054 one-package states. The verifier confirms all common-factor keys are unique, so no pair can share one.

### One nonunit endpoint coefficient, D >= 16,584

After reciprocal normalization, the coefficient is `2 <= U <= 26`. The conservative all-shapes enumeration produces:

```text
package_records=608490
groups=514280
raw_state_pairs=137530
after_coprime_scales=10636
after_range=7916
after_extraction=7916
after_disjoint=5430
after_support=483
after_degree=76
after_role=0
unique_state_pairs=0
```

The row/count verifier recomputes these totals and confirms all survivor CSVs are empty.

### Residual one nonunit endpoint coefficient, D <= 16,583

The corrected residual branch uses the safe degree bound from `d^3 < 64D^2`:

```text
D <= 16,583, |V| = 1, 2 <= U <= D, d <= 2601.
```

The production residual run produces:

```text
package_records=233278
groups=212369
raw_state_pairs=29611
after_coprime_scales=5680
after_range=5680
after_extraction=5679
after_disjoint=2345
after_support=428
after_degree=234
after_role=4
after_correspondence=4
unique_state_pairs=4
unique_orientation_pairs=2
```

The two terminal package pairs are eliminated by eight modular gcd
certificates at `p = 1009`, replayed by `verify_one_nonunit_residual.py`.

## Current proof status

All branches isolated in Qab12 are now eliminated by the bundled mathematical
reductions and computational artifacts.
