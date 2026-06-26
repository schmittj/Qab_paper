# Mathematical certificate for the upper-range computation

This document maps each program condition to the relevant statement in `Qab9.tex`. It is intended to make source review possible without reverse-engineering the code.

## Normal form

A normalized counterexample in the upper unit range is written as two primitive package shapes

```
{r A, r B},   {s C, s E},
N=A+B, M=C+E, gcd(r,s)=1,
D=max(rN,sM).
```

The common root is `alpha`, its degree is `d`, and `beta=alpha^r`, `gamma=alpha^s`.

## Exact global bounds

Section 18 proves

```
d > D/140,
r,s <= 139,
d < 4 D^(2/3).
```

The lower degree used in the code is therefore

```
floor(D/140)+1.
```

The upper degree is computed as the largest integer `d` satisfying

```
d^3 < 64 D^2,
```

which is exactly equivalent to `d < 4 D^(2/3)` and avoids floating point.

## Full Kummer degree

Proposition 18.3 proves

```
d = r*s*k,
deg(beta)=s*k,
deg(gamma)=r*k
```

for an integer `k>=1`. This is the key variable used by `pair_upper.cpp`.

## Shape support cap

Corollary 18.5 proves

```
r*rad(A*B*N) < 4398937,
s*rad(C*E*M) < 4398937.
```

The programs use the inclusive cap `<=4398937`; this is deliberately one integer more permissive than necessary.

Because `A,B,N` are pairwise coprime, the product of their three radicals equals `rad(A*B*N)`.

## Exhaustive shape generation

If three positive radicals have product at most `4398937` and are ordered as `rho1<=rho2<=rho3`, then

```
rho1 <= 163,
rho2 <= 2097.
```

`enumerate_shapes.cpp` generates every integer at most `175394637` with radical under each of these bounds, treats the two generated numbers as the two least-radical roles in all three possible role pairs, reconstructs the third member from `A+B=N`, and canonicalizes radical ties. `test_small.py` compares this method with literal brute force on a small box.

## Pair filters

For each coprime scale pair `1<=r<=s<=139`, `pair_upper.cpp` applies:

1. **Prime-support compatibility.** Outside `{2,3}`, a prime present in one primitive triple and absent in the other must divide the opposite scale (Corollary 11.4 applied to the scaled package).
2. **Range and no-three disjointness.** `D` lies in the unit interval and the two scaled additive triples are disjoint.
3. **Degree interval.** The code combines `d>D/140`, `d<4D^(2/3)`, the confluent degree bound `d<=min(N,M)-2`, and proper-factor bounds `s*k<=N-4`, `r*k<=M-4`. The subtraction by four uses the exact residual-class theorem and the rational-root classification: a complementary factor cannot have degree one.
4. **Role-binomial degree bound.** If prime `p` occupies role `R` in one primitive triple, reduction modulo `p` gives a divisor of `X^(rR)-1`; if it appears in both triples, `d<=gcd(rR,sS)`.
5. **Full-radical congruence.** For every prime in the first triple, `s*k` is `0` or `-2 mod p`; for every prime in the second, `r*k` is `0` or `-2 mod p`. The code tests whether the integer `k` interval meets the combined CRT classes.

The resulting file contains 761 rows.

## Final same-shape certificate

All 761 rows have identical primitive shapes. Proposition 18.8 gives

```
d <= 2*r*s.
```

Since the scales are coprime and at most 139,

```
2*r*s <= 2*139*138 = 38364,
```

whereas throughout the unit interval

```
d >= 48688.
```

Thus no row survives.

## Independent verifier

`verify_upper.py` recomputes radicals, all row inequalities, role values, exact degree intervals, support compatibility, and CRT feasibility from the CSV files. It also confirms that every pre-final row is same-shape and violates the final degree bound. It does not independently prove that the C++ pair loop omitted no branch; that source-level coverage is the remaining computational trust boundary.
