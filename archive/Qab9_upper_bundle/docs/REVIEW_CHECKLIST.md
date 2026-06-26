# Review checklist

The following points deserve the closest independent review.

## Mathematics

1. **Full Kummer proposition (Section 18).** Check the three prime roles, the numerical contradiction in the good-prime case, and the exclusion of Capelli's exceptional `-4 K^4` case via the 2-adic packet for `-beta`.
2. **One-package support bound.** Confirm that the all-moment proof genuinely uses only the package containing the prime and that unit endpoints remove the nonunit block.
3. **Support-envelope certificate.** Check monotonicity and the rational log/exp bounds in `certify_constants.py`.
4. **Full-radical endpoint signature.** Verify that every unit-cluster factor contribution is `0` or `-2 mod p` in each endpoint role.
5. **Role-binomial lemma.** Note that the reduction is applied to the collision trinomial `H=(X-1)^2Q`, not to `Q` itself.
6. **Same-shape Bézout bound.** Check the two orientation cases, the six Möbius divisor table, absence of a common component, and injectivity of conjugates into the intersection.

## Code

1. `enumerate_shapes.cpp`: verify the two-smallest-radicals completeness argument and tie canonicalization.
2. `pair_upper.cpp`: verify support-target generation, especially removal of all powers of 2 and 3 before extracting scale primes >=5; then check scale canonicalization, exact `k` bounds, role-binomial bounds, and CRT construction. The targeted self-test covers every scale through 139.
3. `verify_upper.py`: compare its independently implemented formulas with the C++ formulas.
4. Confirm that the CSV hashes in `SHA256SUMS` match a clean rerun.

## Scope

The upper unit range is complete subject to source review. The lower range is not enumerated exhaustively in this bundle. Optional modular code is a backend, not evidence that the remaining cases have been checked.
