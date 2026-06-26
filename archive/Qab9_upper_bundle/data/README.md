# Data files

- `upper_shapes.csv`: 237,418 primitive shape rows plus header.
- `upper_pair_survivors.csv`: 761 pre-final package-pair rows plus header.
- `upper_residual_candidates.csv`: header only; zero rows survive.
- `upper_pipeline_output.txt`: deterministic stage counts (timing fields are machine-dependent).
- `verification_output.txt`: independent verifier result.
- `reproducibility_checks.txt`: byte-for-byte rerun checks for the two principal CSV outputs.
- `test_output.txt`: development regression tests.
- `factor60_output.txt`: exact factorization summary `870 [] [] 870`.
- `factor60_resource_usage.txt`: resource measurement for the parallel total-60 rerun.
- `lower_exception_catalog.txt`: exact exceptional endpoint-prime catalogue.
- `resource_usage.txt`: measurements from the current environment.

The old experimental `v2` and intermediate diagnostic files have intentionally been omitted from the review package. Optional diagnostics can be regenerated with the Makefile targets.
