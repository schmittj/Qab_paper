# Computational pipeline

## Main proof path

The proof path is:

```text
certify_constants.py
        |
enumerate_shapes.cpp -> upper_shapes.csv
        |
pair_upper.cpp       -> upper_pair_survivors.csv
        |
same_shape_screen.py -> upper_residual_candidates.csv (empty)
        |
verify_upper.py
```

No stage on this path uses floating-point arithmetic for a mathematical decision.

## Build and run

```bash
make clean
make upper THREADS=25
make verify
```

`make upper` rebuilds both C++ executables and overwrites the three principal CSV files. Output ordering is deterministic after the parallel workers are merged and sorted.

## Recorded counts

See `data/upper_pipeline_output.txt`. The main counts are:

| Stage | Count |
|---|---:|
| Primitive radical-admissible shapes | 237,418 |
| Scaled records | 2,450,291 |
| Coprime scale pairs | 5,952 |
| Pairs after range/support/disjointness | 67,730,966 |
| After degree interval | 2,124,295 |
| After role-binomial interval | 139,640 |
| After full-radical CRT | 761 |
| After same-shape Bézout | 0 |

The C++ pair loop considers about 1.84 billion shape pairs, but almost all work consists of small integer operations and support-indexed lookups.

## Exact constants

`certify_constants.py` uses only `int` and `fractions.Fraction`. It certifies:

- the exact reduction of the 70th plastic-number power;
- `theta_0^70 > 2*175394637`;
- `d>D/140` and `r,s<=139`;
- monotonicity of the support envelope;
- a rational upper bound below `4398937` at the endpoint;
- the final uniform gap `48688>38364`.

## Testing

`make test` performs:

- support-target generation for every scale through 139, including scales with hidden factors after removing powers of 2 and 3;
- shape enumeration versus literal brute force in a small box;
- finite-field factor-degree reachability versus SymPy for small `(p,g)` pairs (diagnostic code only);
- exact cube-bound regression;
- rerun of all rational constant assertions.

## Optional diagnostics

`postfilter_upper.py` computes stronger finite-field factor-degree feasibility. It is no longer needed for the upper theorem because the simpler role-binomial bound already leaves only same-shape rows.

`modular_screen.py` and `gcd_orientation_worker.py` implement adaptive modular gcd certificates using `python-flint`. They are retained for the lower range. They require good auxiliary primes and explicitly verify preservation of degree.

## Memory profile

The radical sieve stores one 32-bit radical per integer up to `175394637`, accounting for most of the shape generator's memory. The pair sieve stores the 237,418 shapes and scale/support indices and is much lighter. Recorded measurements are in `data/resource_usage.txt`.


## Independent total-60 factorization

```bash
make factor60 THREADS=25
```

This parallel SymPy check is logically separate from the upper-range elimination.
