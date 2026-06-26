# Lower-range research and computation plan

## Remaining box

After the upper elimination, a normalized counterexample must satisfy

```text
D <= 6816241,
r,s <= 139.
```

The upper proof cannot simply be rerun because the common minimal polynomial may have a nonunit leading or constant coefficient. At an endpoint prime this can permit an internal power and destroy the full Kummer identity `d=r*s*k`.

## Exceptional endpoint primes

The endpoint theorem requires `v_p(endpoint)>=p`. Hence `p^p<=6816241`, leaving exactly

```text
p in {2,3,5,7}.
```

`code/lower_exception_catalog.py` certifies this and records the possible exponent ranges.

## Proposed branch architecture

For every prime divisor of a scale, classify its role in the associated primitive additive triple:

1. **Total role:** internal powers are impossible for every prime.
2. **Good role:** the Frobenius theorem gives the sharp factor-degree bound `e<=p-2`.
3. **Endpoint role, unit packet:** internal powers are impossible by the local packet obstruction.
4. **Endpoint role, nonunit packet:** only `p=2,3,5,7` survives, with the exact constraints
   `e<=endpoint_complement` and `p*endpoint_complement | e*kappa`.

A branch certificate should record the role assignment, valuation exponent, degree interval, norm divisibilities, and slope matching. Branches should be split by intervals of totals and scales so that a small verifier can check coverage.

## Recommended terminal certificates

For rows surviving the arithmetic branch classifier:

- a modular gcd of degree exactly two for each reciprocal orientation;
- a modular square-free certificate for the primitive sparse Wronskian quotient;
- an exact Bézout identity modulo an auxiliary prime;
- or an exact factor-degree incompatibility in a role binomial.

The modular backend in this bundle already supports the first option. Good reduction must be checked explicitly.

## Lean-friendly direction

Rather than formalizing a monolithic enumeration, emit:

- interval/branch coverage nodes;
- per-node arithmetic exclusion reasons;
- compact terminal finite-field certificates.

Lean would then verify the branch tree and exact certificates. The expensive search could remain external.

## Possible theoretical refinements

The most valuable improvements would be:

- a nonunit analogue of the one-package support bound that tracks endpoint coefficients sharply;
- a classification of endpoint internal powers for `p=2,3,5,7` using residual polynomials;
- a better constant in the toric degree bound or the height inequality;
- a same-shape-style correspondence bound for a small number of related but unequal shapes.
