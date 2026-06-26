# Independent mathematical and code audit of the Qab9 review bundle

**Audit date:** 25 June 2026  
**Bundle reviewed:** `Qab9_review_bundle(1).zip`  
**Bundle SHA-256:** `1e848565904158290a832e0a5c3f1faf26be0ccf09f9e34da909e021d3c92a4a`

## 1. Executive conclusion

The bundle supports a substantial but **strictly partial** computer-assisted result.

My overall conclusions are:

| Question | Audit conclusion |
|---|---|
| Does the package prove the full reciprocal-package coprimality conjecture? | **No.** It explicitly leaves the normalized range `D <= 6,816,241`, where nonunit factors and endpoint internal-power branches can occur. |
| Does the mathematical paper give a credible finite reduction? | **Yes, with reservations described below.** I found no contradiction or invalid inference in the reduction to `D <= 175,394,637`, and the numerical endpoint checks are consistent. |
| Does the supplied main computation eliminate the claimed upper range `6,816,242 <= D <= 175,394,637`? | **Yes, subject to the ordinary source-code coverage trust boundary.** The filters match the paper, the full run reproduced the published outputs exactly, and independent small-domain oracles found no missing branch. |
| Is the upper computation feasible and reproducible? | **Yes.** On the audit machine, the full main pipeline took 32.97 seconds wall time and at most 734,260 kB resident memory. |
| Is the remaining lower computation shown to be feasible? | **Not yet.** The paper narrows exceptional endpoint primes to `{2,3,5,7}` and retains small scales, which is encouraging, but there is no complete lower-range classifier, enumeration, branch count, or runtime estimate. |
| Did the audit find a substantive mathematical or implementation error invalidating the stated upper theorem? | **No.** The most important remaining concerns are assurance and completeness, not a demonstrated false step. |

Accordingly, my verdict is:

> **Upper-range theorem: pass with assurance reservations. Full conjecture: incomplete by design.**

The package would be reasonable evidence for the stated upper-range theorem after expert review of the densest local arguments, but it is not yet a complete computer-assisted proof of the conjecture advertised in the motivating problem.

---

## 2. What the package actually claims

For

\[
Q_{a,b}(x)=\frac{a x^{a+b}-(a+b)x^a+b}{(x^{\gcd(a,b)}-1)^2},
\qquad
P_{a,b}(x)=Q_{a,b}(x)Q_{b,a}(x),
\]

the target conjecture is that reciprocal packages attached to distinct unordered pairs are coprime.

The paper does **not** claim to finish this conjecture. Its computationally relevant conclusions are:

1. Every normalized counterexample has
   \[
   D=\max\{m,n,p,q\}\le 175{,}394{,}637.
   \]
2. Every counterexample in
   \[
   6{,}816{,}242\le D\le175{,}394{,}637
   \]
   is unit-normalized and satisfies a collection of exact arithmetic filters.
3. The supplied computation exhausts those filters and leaves 761 pre-final rows.
4. All 761 rows have the same primitive shape on both sides and are contradicted by
   \[
   d\le 2rs\le 38{,}364
   \quad\text{and}\quad
   d\ge48{,}688.
   \]
5. Consequently, any normalized counterexample must satisfy
   \[
   D\le6{,}816{,}241.
   \]
6. In that lower range, endpoint internal-power branches can involve only the primes
   \[
   p\in\{2,3,5,7\}.
   \]

The last range is not enumerated or eliminated by this package.

---

## 3. Audit methodology

I used four complementary methods.

### 3.1 Proof audit

I read the integrated 59-page paper and traced the dependencies of the summary theorem, with particular attention to:

- normalization and removal of cyclotomic roots;
- the graph reformulation and no-three theorem;
- the p-adic packet and prime-support arguments;
- proper-divisibility, Schinzel-fibre, self-power, and Kummer steps;
- the merged 2-adic residual-polynomial argument;
- the torus-intersection and explicit height-degree bound;
- the exact unit-range reductions used by the code;
- the final same-shape Bézout bound.

I also checked the paper's use of the relevant primary external results against the source statements: Borisov's p-adic root packets and cluster divisibility, the quantitative sparse-polynomial theorem of Amoroso–Sombra–Zannier, and the residual-polynomial factorization theorem of Guàrdia–Montes–Nart.

### 3.2 Independent symbolic and numerical checks

I independently checked representative algebra and all load-bearing numerical transitions, including:

- the reciprocal resultant identity for several primitive pairs in exact symbolic arithmetic;
- the plastic-number power certificate;
- the endpoint signs defining `175,394,637` and `6,816,241`;
- the support cap `4,398,937`;
- the scale bound `139`;
- the final degree gap `48,688 > 38,364`.

### 3.3 Source review and dynamic testing

I reviewed every supplied source file, compiled the C++ code with warnings, ran sanitizer builds on reduced domains, ran all supplied tests, and inspected integer widths, strict versus non-strict inequalities, ordering, concurrency, and CSV semantics.

### 3.4 Independent enumeration oracle

The package's verifier checks every recorded row but does not independently prove that the C++ pair scan omitted no row. To test that boundary, I wrote a separate Python oracle that:

- generates primitive shapes by literal loops rather than the package's least-radical construction;
- loops directly over every scale and shape pair rather than using the package's support index;
- checks each possible `k` literally rather than using the C++ CRT construction;
- compares every stage count and every surviving row.

This oracle matched the package on 20 shape-enumerator test boxes, full pair scans through `D=70` and `D=90`, and a constructed 80-shape test with a nonzero pre-final survivor.

This is strong regression evidence, though it is not a formal coverage proof for the production-scale run.

---

# Part I. Mathematical audit

## 4. Normalization, reciprocal packages, and roots on the unit circle

### 4.1 Polynomial identities

The identities

\[
H_{m,n}(x)=mx^n-nx^m+(n-m),
\qquad
Q_{a,b}(x)=\frac{H_{a,a+b}(x)}{(x^{\gcd(a,b)}-1)^2},
\]

and

\[
x^{a+b-2g}Q_{a,b}(1/x)=Q_{b,a}(x)
\]

are correct. The composition identity

\[
Q_{rA,rB}(x)=rQ_{A,B}(x^r)
\]

also follows directly.

### 4.2 Unit-circle lemma

The proof that a unit-modulus zero of `H_{m,n}` must satisfy `z^m=z^n=1` is sound. The equation writes `z^m` as a strict convex combination of `1` and `z^n`; equality of modulus forces equality in the triangle inequality. The second-derivative calculation correctly gives multiplicity exactly two at every `gcd(m,n)`-th root of unity.

The derivative

\[
H'_{m,n}(x)=mnx^{m-1}(x^{n-m}-1)
\]

then shows that these are all multiple roots. It follows correctly that every `Q_{a,b}` is square-free and has no root on the unit circle.

**Audit status:** sound.

### 4.3 Primitive normalization

Dividing the four edge indices by their common gcd and replacing the root by the corresponding power is legitimate. The normalization

\[
\gcd(m,n,p,q)=1
\]

implies coprimality of the two edge gcds, as used later.

**Audit status:** sound.

---

## 5. No-three theorem and collision dictionary

The no-three theorem is one of the cleanest parts of the paper. If three positive indices share a value `L_r(z)=A`, then

\[
F(t)=|1-tA|^2-|z|^{2t}
\]

has four distinct real zeros at `0,i,j,k`, while

\[
F'''(t)=-(\log |z|^2)^3|z|^{2t}
\]

never vanishes when `|z| != 1`. Three applications of Rolle's theorem give the stated contradiction.

The consequences are correctly propagated:

- the collision graph at a fixed off-unit root is a matching;
- the two complementary orientations of one reciprocal package cannot both occur;
- common factors between package products correspond exactly to two distinct graph edges;
- the propagation identity derived from
  \[
  (u+v)L_{u+v}=uL_u+vz^uL_v
  \]
  rules out endpoint-gap overlaps;
- the two additive triples in a counterexample are disjoint.

I checked the endpoint/endpoint, gap/gap, and endpoint/gap cases separately; the proof covers all of them.

**Audit status:** sound and load-bearing.

---

## 6. Local finiteness, sign, tail, phase, Schur, and second-jet sections

These sections contain both structural results and auxiliary identities. Most do not directly enter the upper-range program, but they support the broader paper.

### 6.1 Finite collision support and local finiteness

The reduction of repeated collisions at a fixed algebraic point to an `S`-unit equation is logically consistent. Once the multiplicative group generated by the algebraic point and the relevant coefficients is fixed, the cited finiteness theorem applies. The transition from pointwise finite collision support to finite support for a fixed irreducible factor is valid by choosing a root of that factor.

This result is qualitative and does not provide the explicit finite endpoint used later; the paper does not conflate those two roles.

**Audit status:** sound, conditional on the cited standard `S`-unit theorem.

### 6.2 Sign and exact tail identities

I checked the divided-difference formulas and the exact tail-conjugacy identity algebraically. The one-crossing and chord consequences preserve the required strictness because unit-circle roots have already been removed.

**Audit status:** no issue found.

### 6.3 Phase localization and positive-cone decomposition

The phase inequalities follow from the collision equation and triangle geometry. The positive-cone decomposition is an exact rearrangement rather than an asymptotic assertion. The negative-real ordering proposition correctly treats the parity cases.

**Audit status:** no issue found.

### 6.4 Schur/Casoratian and second jet

The Schur, determinant, and contraction forms are algebraically equivalent to the original collision equations. The second-order branch expansion has the correct vanishing first derivative and the stated second-order coefficient.

These arguments are not used to justify the production enumeration, so an error here would not by itself invalidate the upper computational theorem; I nevertheless found no algebraic discrepancy.

**Audit status:** no issue found.

---

## 7. Rational-root classification

The rational-root theorem is used later to strengthen a proper-factor complement from degree at least one to degree at least two. I checked the cases arising from the rational-root theorem, signs, and reciprocal symmetry.

The important computational consequence is valid: in the relevant unequal primitive cases, a proper complementary factor cannot have degree one. Hence, if a selected factor of `Q_{A,B}` has degree `e`, then

\[
e\le (A+B-2)-2=A+B-4.
\]

This is exactly the source of the code's `N-4` and `M-4` bounds.

**Audit status:** sound and correctly transferred to code.

---

## 8. Additive-triple prime separation and finite primitive shapes

### 8.1 Mapping to Borisov's notation

The paper's local arguments use Borisov's `abc` polynomial with the three pairwise-coprime entries corresponding to the two endpoints and their total. I checked the role mapping and reciprocal endpoint cases.

Borisov's local statements supply:

- the factorization modulo a prime occupying one additive-triple role;
- clusters around prime-to-`p` roots of unity;
- the center-1 packets;
- nonunit blocks at endpoint roles;
- divisibility by `p` of the number of roots of a rational factor in each nontrivial cluster.

The paper's prime-separation theorem applies these statements in the correct role and does not silently use a unit conclusion at an endpoint where a nonunit block might occur.

### 8.2 Support compatibility

For two colliding primitive shapes, a prime appearing in only one additive triple must be supplied by the opposite scale, except for the separately treated small primes in the computational support index. The direction of the divisibility is correct:

- `p` in shape 1 but not shape 2 implies `p | s`;
- `p` in shape 2 but not shape 1 implies `p | r`.

The paper's revised support-index correction is reflected in the code: powers of 2 and 3 are fully removed before extracting scale support at primes at least 5.

### 8.3 Finite primitive-shape theorem

Once the six entries are restricted to a finite prime set, the additive equation `A+B=N` becomes an `S`-unit equation, giving finitely many primitive shapes. The subsequent finite-scaling statement is compatible with the support separation.

**Audit status:** sound. The local packet material is one of the paper's densest external-dependency zones and merits specialist p-adic review, but I found no mismatch with Borisov's stated lemmas.

---

## 9. Proper-divisibility rigidity

The theorem

\[
Q_{A,B}\mid Q_{C,D}\Longrightarrow (C,D)=(A,B)
\]

for primitive unequal pairs is checked through the diagonal denominator, boundary cases, and root-location arguments.

The proof correctly separates:

- interior primitive pairs;
- boundary pairs where one endpoint is 1;
- reciprocal orientations;
- the possibility of equal totals.

The use of the Eneström–Kakeya-type boundary control is consistent with the coefficient signs in the normalized polynomial.

This theorem is then used correctly: if a primitive base is irreducible, any occurrence inside a distinct package would force forbidden divisibility, so the base is globally isolated after the self-power and Kummer steps.

**Audit status:** no flaw found.

---

## 10. Schinzel-fibre bound, internal powers, and Kummer reduction

This is another load-bearing block.

### 10.1 Elementary binomial-fibre lemma

I checked the valuation split and the resulting degree divisibility case by case. The lemma properly distinguishes ordinary extraction from the exceptional fourth-power case in Capelli's theorem.

### 10.2 Confluent Schinzel degree bound

The application to two power-composed primitive polynomials gives the bound

\[
d\le \min(N,M)-2.
\]

The multiplicity-two cyclotomic denominator has already been removed, so the degree subtraction is consistent.

### 10.3 Newton-edge and Frobenius obstructions

The Newton-edge obstruction and the good-prime Frobenius bound correctly translate local packet lengths into restrictions on the degree of a factor whose root is an internal `p`-th power. I checked the arithmetic transition to `e <= p-2` in the good-prime case.

### 10.4 Self-power rigidity

For an irreducible primitive `Q_{A,B}`, the paper eliminates internal `p`-th powers for all primes. The odd-prime role analysis and the special `p=2` treatment are coherent. The fourth-power exception is not ignored.

### 10.5 Exact Kummer reduction

The field-degree formula under extraction is used in the correct direction. Once internal powers are excluded, the degree multiplies by the expected prime factors, yielding isolation of every lift of an irreducible primitive base.

### 10.6 Density estimate

The paper combines this isolation theorem with Borisov's count of exceptional primitive triples. The exponent

\[
O(X^{20/11}\log X)
\]

matches the cited source's quantitative estimate, and the summation over scales does not change the stated order improperly.

**Audit status:** no logical break found. This chain is intricate but internally consistent.

---

## 11. Factor-level radical sieves and the merged 2-adic block

### 11.1 Primitive total-radical sieve

The degree congruence

\[
\operatorname{rad}(A+B)\mid e(e+2)
\]

follows from the factor partition into the center-1 packet and the other clusters. The exact factor-partition signatures for odd total primes are compatible with the packet lengths.

### 11.2 Merged 2-adic residual polynomial

The paper repairs an important potential gap: at `p=2`, Newton sides that are distinct for odd primes merge, so packet length alone is insufficient. The proposed residual polynomial is computed for the merged side and shown to be residual-separable; the Guàrdia–Montes–Nart residual-polynomial theorem then splits the corresponding factor block.

I checked:

- the coefficients lying on the merged side;
- the normalization used to form the residual polynomial;
- the derivative/separability calculation over the residue field;
- the way residual factors translate back to polynomial factors;
- the parity conclusion used in later moment and power arguments.

I did not find an algebraic error. Nevertheless, this is the **least externally standardized, most review-sensitive proof in the bundle**. The general residual-polynomial theorem is standard, but the specialized merged-side computation is new to this paper and is not accompanied by an independently generated local certificate or proof-assistant formalization.

**Audit status:** plausible and algebraically checked, but recommended for independent specialist verification before treating the broader theorem chain as publication-final.

---

## 12. Endpoint and good-prime power sieves; exact signatures

The endpoint theorem correctly isolates the only possible endpoint internal-power situation:

\[
e\le A,\qquad pA\mid e\kappa
\]

or the reciprocal version, where `p^kappa` exactly divides the endpoint. In particular, `kappa >= p` is a necessary condition.

The good-prime sieve, prime-by-prime Kummer trigger, role signatures, and factor partitions are mutually consistent. The prime and twice-prime total irreducibility corollary follows from those partitions.

The large-prime endpoint-role rigidity is also used in the correct direction: it narrows possible matching roles rather than claiming full irreducibility from insufficient local data.

**Audit status:** no issue found.

---

## 13. Reciprocal resultant

The stated formula is

\[
\left|\operatorname{Res}(Q_{a,b},Q_{b,a})\right|
 =a^{a-2}b^{b-2}(a+b)^{a+b-2}
\]

for primitive pairs, with the natural interpretation in boundary cases.

I independently constructed the exact polynomials and checked the formula with symbolic resultants on several small and medium primitive pairs. All tests agreed.

The resultant is presented as a supplementary sieve, not as a hidden assumption in the upper computation.

**Audit status:** verified on representative exact cases; derivation appears sound.

---

## 14. Sparse Wronskian and torus-intersection rigidity

### 14.1 Wronskian square divisor

If two sparse collision polynomials share a factor, the standard Wronskian combination has the square of that factor as a divisor. The sparse expression in the paper follows from direct differentiation and cancellation. I checked the exponents and coefficients.

### 14.2 Four-unit divisor rigidity

The function-field argument using divisors of `u`, `u-1`, `v`, and `v-1` correctly forces degeneracy when their divisor span has rank at most two. The proof treats constants and nonconstant maps separately.

### 14.3 Rank-two torus intersections

The paper uses four-unit rigidity to rule out a positive-dimensional component of the intersection of the product-of-lines variety with a rank-two subtorus under the normalized gcd hypothesis. I checked the passage from monomial relations to divisor relations and the treatment of mixed relations.

**Audit status:** no flaw found; this is important for proving that the relevant toric intersection is zero-dimensional before applying Bézout.

---

## 15. Amoroso–Sombra–Zannier route to effective boundedness

The paper specializes the quantitative sparse-polynomial theorem with four exponents. The source theorem supplies, when

\[
D^{1/6}>B_4(1+h_0),
\]

an injective torus homomorphism of bounded size, a factorization of the exponent map, and a gcd/proper-subsupport dichotomy. Here `h_0 <= log(2D)`, yielding the stated threshold.

The paper then analyzes the possible codimension parameter `k`:

- `k=3`: normalization forces the remaining scalar exponent to have absolute value one, bounding `D` by the torus-map size;
- `k=0`: an injective same-dimensional torus map is an automorphism, so it cannot create a gcd between coprime Laurent linear forms;
- `k=1`: the full product of two punctured lines cannot lie in a proper subtorus, including a mixed monomial relation;
- `k=2`: rank-two torus-intersection rigidity excludes a curve through the point.

The proper-subsupport alternatives are eliminated using the sparsity and no-three structure before this case split.

The source theorem's constant is effective but not numerically supplied. The paper states this limitation correctly and does not use this symbolic constant for the production endpoint.

**Audit status:** correct specialization as far as I can determine; not the practical source of the numerical bound.

---

## 16. Direct explicit endpoint `175,394,637`

This is the key analytic reduction used by the computation.

### 16.1 Height estimate

From a collision equation `H_{u,v}(alpha)=0`, standard height inequalities give

\[
(v-u)h(\alpha)\le\log(2v),
\qquad
u h(\alpha)\le\log(2v),
\]

hence

\[
v h(\alpha)\le2\log(2v).
\]

Applying this at the maximum endpoint gives the required bound in terms of `D`.

### 16.2 Short rank-two subtorus

The lattice of integral relations among the four exponents has rank three. A geometry-of-numbers argument chooses two short independent relations. The resulting rank-two subtorus has degree below

\[
4D^{2/3}.
\]

I checked the determinant estimate and the conversion between the lattice norm and the toric degree.

### 16.3 Bézout and field degree

Because the rank-two intersection has no positive-dimensional component, Bézout bounds the number of conjugate points, giving

\[
d=[\mathbb Q(\alpha):\mathbb Q]<4D^{2/3}.
\]

The conjugate injection is valid: every conjugate of the common root gives a distinct point in the torus parameterization.

### 16.4 Mahler-measure gap

Combining the height and degree bounds gives an upper bound for the Mahler measure of the primitive minimal polynomial. The paper correctly proves that this minimal polynomial is nonreciprocal. Thus:

- if it is monic, Smyth's lower bound gives `M(h) >= theta_0`, where `theta_0` is the plastic number;
- if it is nonmonic, `M(h) >= 2 > theta_0`.

This yields the numerical comparison that fails beyond `D=175,394,637`.

### 16.5 Independent endpoint check

Using high-precision arithmetic, I obtained the following signed margins for the relevant decreasing envelope `F(D)`:

| Check | Signed margin |
|---|---:|
| `F(175394637) - log(theta_0)` | approximately `+4.138e-10` |
| `F(175394638) - log(theta_0)` | approximately `-3.911e-11` |
| `F(6816241) - log(2)` | approximately `+9.329e-9` |
| `F(6816242) - log(2)` | approximately `-1.838e-8` |

Thus the integer transition points stated in the paper are consistent and are not off by one.

The Sage/Arb script supplied for these two real-number comparisons was not runnable in the base audit environment because Sage and Arb were not installed. This does not affect the main C++ computation, and I independently checked the signs at high precision, but a fully pinned release should include a container or lockfile for that auxiliary certificate.

**Audit status:** no error found; endpoint independently corroborated.

---

## 17. Unit transition and exact upper-range reduction

For `D >= 6,816,242`, the Mahler upper bound is below `2`, so a primitive minimal polynomial cannot be nonmonic. The constant coefficient is then also a unit by reciprocity/norm considerations. The endpoint `6,816,242` is numerically correct as noted above.

The exact plastic-number certificate proves

\[
\theta_0^{70}>2D_{\max}.
\]

Consequently, throughout the finite box,

\[
d>\frac{D}{140}.
\]

The script reduces `theta_0^70` modulo `X^3-X-1` to an expression with positive coefficients and substitutes the rational lower bound `theta_0>33/25`; this is an exact proof, not a floating-point approximation.

The same estimates yield `r,s <= 139`. Because the scales are coprime, their maximum product in the same-shape case is `139*138`.

**Audit status:** exact constants and strict inequalities are handled correctly.

---

## 18. Full Kummer degree in the unit range

Writing the two packages as primitive shapes at coprime scales `r,s`, with `beta=alpha^r` and `gamma=alpha^s`, the paper proves

\[
d=rsk,
\qquad
[\mathbb Q(\beta):\mathbb Q]=sk,
\qquad
[\mathbb Q(\gamma):\mathbb Q]=rk
\]

for an integer `k >= 1`.

I audited the prime-by-prime argument:

- total-role primes are excluded by the total-prime internal-power theorem;
- good primes are excluded by `e <= p-2` together with the degree lower bound;
- endpoint primes have no nonunit packet in the unit-normalized range;
- the `4 | r` Capelli exception is handled separately by ruling out the relevant negative square via the 2-adic packets.

The use of `gcd(r,s)=1` to combine the separate degree multipliers is correct.

This proposition is essential: the program's single integer `k` and all its congruences would not be justified without it.

**Audit status:** no gap found in the unit range. It is intentionally unavailable in the remaining nonunit lower range.

---

## 19. One-package support cap and congruences

The one-package support estimate combines the factor-level radical bound, the field-degree estimates, and the height/Mahler envelope. Its endpoint maximum is correctly shown to be below `4,398,937`.

The code deliberately uses the weaker inclusive condition

\[
r\,\operatorname{rad}(AB(A+B))\le4{,}398{,}937,
\]

whereas the theorem gives a strict upper bound. This can add candidates but cannot delete a genuine one.

For a primitive shape, `A`, `B`, and `A+B` are pairwise coprime, so

\[
\operatorname{rad}(AB(A+B))=
\operatorname{rad}(A)\operatorname{rad}(B)\operatorname{rad}(A+B).
\]

The full-radical degree signatures

\[
sk\equiv0,-2\pmod p,
\qquad
rk\equiv0,-2\pmod p
\]

are applied to every prime in the corresponding primitive triple. The code's treatment when the coefficient is divisible by `p` is correct: the congruence is then automatically satisfied because the left side is zero modulo `p`.

**Audit status:** sound and faithfully implemented.

---

## 20. Role-binomial bound

Reduction modulo a prime occupying a unique primitive role places the reduction of the common minimal polynomial inside a divisor of a binomial `X^E-1`. Therefore:

- when the prime occurs only on one side, `d <= E`;
- when it occurs on both sides, `d <= gcd(E_1,E_2)`.

The role value is uniquely defined because a primitive additive triple has pairwise-coprime entries. The code checks this invariant and throws if it fails.

The program converts the degree bound to a bound on `k` by integer division by `rs`; this is exact because `d=rsk`.

**Audit status:** correct.

---

## 21. Same-shape Bézout bound

For two coprime scales applied to the same primitive shape, the paper considers the two power-correspondence curves in `P^1 x P^1`. Their bidegrees give intersection number `2rs`. Four-unit rigidity rules out a common component unless the packages coincide. Distinct conjugates of the common root inject into the intersection, yielding

\[
d\le2rs.
\]

I checked the bidegrees, the common-component exclusion, and the conjugate injection. The program applies this bound only when the primitive triples are exactly equal.

In the upper interval,

\[
d\ge\left\lfloor\frac{6{,}816{,}242}{140}\right\rfloor+1=48{,}688,
\]

while

\[
2rs\le2\cdot139\cdot138=38{,}364.
\]

The strict contradiction is valid. The minimum actual margin in the 761 recorded rows was 48,539.

**Audit status:** sound and decisive.

---

## 22. Remaining mathematical class

The paper correctly identifies the unresolved class:

- both primitive bases are reducible;
- `D <= 6,816,241`;
- nonunit leading or constant coefficients may occur;
- full Kummer degree and the one-package unit support cap may fail at endpoint primes.

The endpoint internal-power theorem gives `p^p <= 6,816,241`, hence only

\[
p\in\{2,3,5,7\}.
\]

This is a useful finite branching reduction, but it is not an elimination. The residual four-index statement remains a conjecture in the paper.

**Audit status:** accurately disclosed incompleteness.

---

# Part II. Code audit

## 23. `code/enumerate_shapes.cpp`

### 23.1 Intended task

The program must list every primitive triple

\[
1\le A<B,\quad N=A+B,\quad \gcd(A,B)=1,
\]

with

\[
N\le D_{\max},
\qquad
\operatorname{rad}(A)\operatorname{rad}(B)\operatorname{rad}(N)
\le4{,}398{,}937.
\]

### 23.2 Exhaustiveness argument

Order the three radicals as `rho_1 <= rho_2 <= rho_3`. Their product bound implies

\[
rho_1\le\lfloor B^{1/3}\rfloor=163,
\qquad
rho_2\le\lfloor B^{1/2}\rfloor=2097.
\]

The code recursively generates every integer up to `D_MAX` whose radical is at most each of these two limits. It then treats the generated pair as the two least-radical roles in all three possible role pairs:

1. endpoint/endpoint;
2. endpoint/total;
3. total/endpoint.

`canonical_witness` orders `(radical, role)` pairs, so ties are assigned to exactly one branch. The reconstructed third entry is checked against the full radical cap and gcd condition.

This is a valid exhaustive scheme.

### 23.3 Independent checks

A literal enumerator matched this code exactly on 20 deterministic and seeded-random boxes with varying endpoint and radical limits.

### 23.4 Arithmetic and implementation

- The full radical sieve uses one 32-bit word per integer, explaining the roughly 700 MB memory peak.
- `rad(n) <= n <= 175,394,637`, so the sieve values fit in `uint32_t`.
- Products used for cap comparisons are promoted to 64 or 128 bits.
- Floating-point `sqrt` and `cbrt` are corrected by exact integer loops before use; therefore they do not create a mathematical cutoff risk.
- Parallel workers have private result vectors and are merged, sorted, and deduplicated deterministically.

### 23.5 Minor robustness issues

- Generic command-line values larger than `uint32_t` are silently narrowed after parsing.
- There is no explicit check that `rad-cap` itself fits the downstream 32-bit helper arguments.
- The program assumes nonadversarial generated input and does not provide a formal branch certificate.

None affects the official command line.

**Code verdict:** correct for the stated production domain.

---

## 24. `code/pair_upper.cpp`

### 24.1 Scale enumeration

The code enumerates

\[
1\le r\le s\le139,
\qquad
\gcd(r,s)=1.
\]

This is exhaustive up to swapping the two packages. The only equal-scale case is `r=s=1`; there, `j>i` prevents duplicate and self-pairs.

The recorded count `5,952` agrees with an independent enumeration.

### 24.2 Support index

Shapes are grouped by scale and prime support outside `{2,3}`. For a support `S_1`, the target support generator permits exactly:

- dropping primes of `S_1` that divide `s`;
- adding primes that divide `r`.

This is equivalent to the support-compatibility theorem at primes at least 5. The code now fully removes powers of 2 and 3 from scales before factor extraction; this correctly fixes the earlier composite-atom risk mentioned in the revision notes.

The built-in support self-test checks all scales through 139 and many support combinations. My direct pair oracle, which does not use the support index, found the same pair universe on reduced domains.

### 24.3 Range, cap, and disjointness

The code computes

\[
D=\max(rN,sM)
\]

in 64 bits, enforces the exact requested interval, verifies disjointness of all six scaled additive-triple entries, and rechecks both support caps.

The groups already enforce `scale * total <= dmax`, so narrowing `D` to 32 bits is safe in the official domain.

### 24.4 Degree interval

The lower bound is

```text
floor(D/140)+1
```

which exactly implements the strict inequality `d>D/140`.

The upper bound is the largest integer satisfying

\[
d^3<64D^2,
\]

computed using 128-bit products. This is exactly `d<4D^(2/3)` without floating point.

The program also imposes:

\[
d\le\min(N,M)-2,
\qquad
sk\le N-4,
\qquad
rk\le M-4.
\]

The conversion to the interval for `k` is correct.

The binary-search upper limit `2,000,000` is safely above the true maximum in the official box, although this is a hard-coded domain assumption rather than a checked invariant.

### 24.5 Role-binomial interval

For every prime in the union of primitive supports, the code finds the unique divisible role and computes the correct one-sided exponent or two-sided gcd. The minimum is divided by `rs` to bound `k`.

An aggressive warning build reported one conversion warning at the expression `role_bound / rs`. The quotient is below `uint32_t` in the official domain, so this is not an overflow defect, but an explicit checked cast would improve the code.

### 24.6 CRT feasibility

For each prime, the allowed residues are the solutions to

\[
ck\equiv0\text{ or }-2\pmod p.
\]

The code intersects the two sides when necessary and incrementally combines the result by CRT. It finally tests whether any resulting class meets `[k_lo,k_hi]`.

I compared this implementation to literal iteration over every `k` on reduced domains; all rows and stage counts agreed. The product of distinct moduli is safely below 64-bit capacity under the support caps.

### 24.7 Parallelism and determinism

Each OpenMP thread owns its counters and survivor vector. There is no shared mutation inside the pair loop. Survivors are globally sorted before CSV output, making the three principal CSV files deterministic across thread schedules.

### 24.8 Input validation

`read_shapes` trusts the input CSV's mathematical invariants and does not recompute radicals or gcds. In the official pipeline this file is generated immediately by the audited enumerator and later checked by Python, so this is acceptable but not hardened against adversarial inputs.

**Code verdict:** the implementation matches the paper's upper-range filters; no missing or reversed condition was found.

---

## 25. `code/same_shape_screen.py`

The script reads each pre-final row, compares the two primitive triples, computes

\[
\text{degree lower}=\lfloor D/140\rfloor+1,
\qquad
\text{same-shape bound}=2rs,
\]

and discards a row only if the shapes agree and the lower bound exceeds `2rs`.

This is conservative and exactly implements the final proposition. It does not infer same shape from partial data. The production output is a header-only residual CSV.

**Code verdict:** correct.

---

## 26. `code/verify_upper.py`

The verifier independently recomputes for every recorded row:

- additive and gcd conditions;
- radicals and radical products;
- ordering and uniqueness;
- scales and range;
- disjointness;
- support compatibility;
- exact degree bounds;
- role-binomial bounds;
- CRT feasibility;
- same-shape status and final degree contradiction.

This is valuable protection against corrupted or malformed result rows.

However, it does **not** independently enumerate all possible shapes or pairs. It can prove that every listed row is valid, but not that no valid row was omitted. The docstring and paper state this limitation accurately.

A further low-severity issue is that almost all checks use Python `assert`. Running the verifier under `python -O` would remove them and still print `status=PASS`. The supplied Makefile invokes ordinary `python3`, so the recorded run is valid. For proof infrastructure, assertions should be replaced by explicit exceptions or checked predicates.

**Code verdict:** good row validator; not a coverage certificate.

---

## 27. `code/test_small.py` and independent coverage testing

The supplied test suite covers:

- support-target generation;
- the shape enumerator versus brute force in a small box;
- exact cube-bound regressions;
- optional finite-field factor-degree reachability versus SymPy;
- exact rational constants.

Its principal gap is that it does not independently brute-force the entire pair loop.

The separate audit oracle filled part of that gap:

| Test | Result |
|---|---|
| 20 shape boxes versus literal enumeration | exact match |
| Complete pair oracle, `D <= 70`, 746 shapes | every stage count and survivor set matched; 0 survivors |
| Complete pair oracle, `D <= 90`, 1,239 shapes | every stage count and survivor set matched; 0 survivors |
| 80-shape subset through `D=220` with a known survivor | every stage count and exact row matched; 1 survivor |

The nonzero case is important because it exercises CSV survivor construction, not merely a vacuous zero output.

**Testing verdict:** strong regression evidence, but still not a formal production-coverage proof.

---

## 28. Exact constants and threshold scripts

`certify_constants.py` uses only integers and `Fraction`. Its logarithm and exponential helpers have explicit tail bounds. I checked the signs and monotonicity argument.

It certifies:

```text
plastic_power_coefficients=62608681,109870576,82938844
theta70_rational_lower=220094051941/625
twice_D_max=350789274
uniform_degree_bound=d>D/140
scale_max=139
same_shape_max=38364
unit_degree_integer_min=48688
support_endpoint_upper_floor=4398936
support_product_cap=4398937
```

The separate Sage/Arb threshold script is sensible but was not run in this environment because its dependencies were absent. The two endpoint signs were independently checked as described above.

**Code verdict:** exact main constants are well certified.

---

## 29. Factorization through total 60

`factor_through_60.py` constructs `Q_{a,b}` exactly over `QQ`, factors one orientation, canonicalizes each factor together with its reciprocal, and checks orbit collisions between packages.

For totals through 60 there are 870 unordered unequal pairs. The rerun returned:

```text
870 [] [] 870
```

meaning no reducible package, no reciprocal-orbit collision, and all 870 packages globally certified by an irreducible primitive base.

This is a useful independent sanity check, but it is logically separate from the large upper-range sieve and does not extend the proof beyond total 60 by itself.

**Code verdict:** correct exact diagnostic.

---

## 30. Optional finite-field and modular-gcd code

### 30.1 `postfilter_upper.py`

The factor-degree reachability calculation for divisors of `X^g-1` over `F_p` correctly accounts for the `p`-power multiplicity and the degrees `ord_t(p)` of cyclotomic factors. The bounded subset-sum implementation is appropriate.

This script is not used in the main proof.

### 30.2 `modular_screen.py` and `gcd_orientation_worker.py`

The intended certificate is valid: choose a good prime preserving degree, reduce both package polynomials, and compute a modular gcd. Since every package has the known cyclotomic square before division, a modular gcd of exactly the expected trivial degree excludes an additional characteristic-zero common factor when the leading data are preserved.

The worker explicitly verifies the relevant degree preservation and records its auxiliary prime. The sparse modular remainder implementation was consistent with direct checks on reduced examples.

The optional `python-flint` dependency was not available in the base environment, so I did not run this backend. It is not invoked by `make upper` or needed for the stated upper theorem.

**Code verdict:** design appears sound; optional path not fully dynamically audited.

---

## 31. Static and sanitizer results

- The normal C++ build with `-Wall -Wextra -Wpedantic` was clean.
- An additional `-Wconversion -Wsign-conversion -Wshadow` build produced only the harmless quotient-conversion warning discussed above.
- AddressSanitizer and UndefinedBehaviorSanitizer runs completed without findings for:
  - the shape enumerator at limit 1,000;
  - the pair sieve at `D <= 1,000`, producing 12 pre-final rows;
  - the support self-test.
- All Python files compiled successfully with `compileall`.

Sanitizer tests on reduced domains do not prove absence of all production bugs, but no memory, overflow, or undefined-behavior symptom was observed.

---

# Part III. Reproduction results

## 32. Audit environment

The full run was performed on:

```text
Debian 13.3, Linux x86_64
g++ 14.2.0
Python 3.13.5
GNU Make 4.4.1
```

The core commands were:

```bash
make clean
/usr/bin/time -v make upper THREADS=25
make verify
make test
make factor60 THREADS=8
make lower-catalog
```

All completed successfully.

## 33. Full production counts

The clean rerun produced:

| Stage | Count |
|---|---:|
| Primitive shapes | 237,418 |
| Scaled records | 2,450,291 |
| Coprime scale pairs | 5,952 |
| Support-group pairs | 18,118,166 |
| Shape pairs considered | 1,836,842,744 |
| After range, cap, and disjointness | 67,730,966 |
| After degree interval | 2,124,295 |
| After role-binomial interval | 139,640 |
| After full-radical CRT | 761 |
| Same-shape rows | 761 |
| Residual candidates | 0 |

## 34. Hash reproduction

The three mathematical data files reproduced byte-for-byte:

```text
ead8e791b2f5b5e04122c606d51575f20836255c232ed58f9aab10f4afd7fe99  upper_shapes.csv
f4ff36cf9a766eefc14a73565dbf036674ffd95dc381c253bad352ca1f7a789a  upper_pair_survivors.csv
69bac3fef15bcd6f3fc64a62a8c7f057e5ce6060b22dc39cf28c8e4cb9a80369  upper_residual_candidates.csv
```

The original bundle also passes its complete `SHA256SUMS` file.

The timing-containing text log naturally changes on a clean rerun. This is a minor packaging issue: timing output should not be included in a bit-for-bit mathematical-output hash, or the checksum documentation should distinguish deterministic data from environment-dependent logs.

## 35. Resource use

The complete `make upper` run used:

```text
Elapsed wall time: 32.97 seconds
Maximum resident set size: 734,260 kB
CPU utilization: 1061%
```

The dominant memory cost is the radical sieve, not polynomial arithmetic. The upper-range computation is therefore plainly feasible on an ordinary multicore workstation.

---

# Part IV. Findings and risk assessment

## 36. Findings by severity

### Finding 1 — Blocking for the full conjecture: the lower range is not proved

**Status:** acknowledged by the authors; not a hidden defect.

The package proves only that a normalized counterexample must have

\[
D\le6{,}816{,}241.
\]

It contains a plan, not an implementation, for the nonunit endpoint-power branches. Therefore the package is not a computer-assisted proof of the full conjecture.

### Finding 2 — Moderate assurance risk: pair-scan coverage remains source-level

The production scan considers approximately 1.84 billion shape pairs. The Python verifier validates all output rows but cannot detect an omitted input branch. Completeness rests on inspection and execution of the C++ loop.

The independent reduced-domain oracle materially increases confidence and found no mismatch, but it does not constitute a formal certificate for the full production universe.

### Finding 3 — Moderate mathematical-review risk: specialized local 2-adic argument

The merged 2-adic residual-polynomial computation is central to several broad claims and is the least routine new local argument. I found it algebraically consistent and compatible with the general residual-polynomial theorem, but it lacks an independent machine-generated local certificate or a second derivation.

This is a recommendation for concentrated expert review, not a discovered counterexample.

### Finding 4 — Low: symbolic ASZ bound is not practical

The Amoroso–Sombra–Zannier constant is effective but nonnumeric in the cited source. The paper clearly says so and supplies a separate direct numerical argument, so this does not affect the endpoint `175,394,637`.

### Finding 5 — Low: verifier can be disabled by `python -O`

`verify_upper.py` uses assertions for proof checks. The official command does not optimize Python, but robust certificate software should use explicit failures.

### Finding 6 — Low: deterministic and nondeterministic artifacts are mixed

The principal CSVs are deterministic. The pipeline text file includes timings, so its hash varies by run. Separate mathematical manifests from benchmark logs.

### Finding 7 — Low: generic input hardening

The C++ programs have limited range validation and trust generated CSV invariants. Some narrowing casts and the fixed `degree_upper` binary-search ceiling are safe only under the documented official bounds.

### Finding 8 — Low: optional dependency reproducibility

Sage/Arb and `python-flint` were not installed in the base environment, and the package does not provide a pinned container image. These paths are auxiliary for the present upper theorem but will matter more for a lower-range release.

---

## 37. What was not found

The audit found no evidence of:

- an off-by-one error in either analytic endpoint;
- a missing radical tie case in the shape enumerator;
- a reversed support-scale divisibility condition;
- omission of scales with hidden prime factors after powers of 2 or 3;
- incorrect strictness in the degree cube bound;
- a CRT residue error at `p=2` or when a scale is divisible by `p`;
- a race condition in the OpenMP output;
- nondeterminism in the principal CSVs;
- integer overflow in the official production domain;
- a mismatch between any of the 761 recorded rows and the stated filters;
- a surviving upper-range row after the same-shape theorem.

---

# Part V. Completeness and feasibility

## 38. Completeness of the upper-range theorem

Conditional on the mathematical propositions proved in the paper and ordinary trust in the compiled C++ source, the upper-range theorem is complete:

1. every unit-range counterexample is mapped to a primitive-shape/scale pair;
2. every such shape satisfies the support cap and is generated;
3. every scale pair is enumerated up to symmetry;
4. every necessary filter is conservative;
5. every pre-final row is recorded;
6. the final theorem excludes every recorded row.

The independent oracle supports steps 2–5 on reduced domains. I found no filter that is stronger than its mathematical justification.

## 39. Completeness for the full conjecture

The package is incomplete in precisely the way it states. In the lower range, a selected factor may be nonmonic or have nonunit constant term. Then:

- the full Kummer degree `d=rsk` can fail;
- endpoint nonunit packets can absorb conjugates;
- the one-package unit support bound can fail;
- the current single `k` congruence model is not exhaustive.

A lower computation cannot safely be obtained merely by changing `--dmin` to 1 in `pair_upper.cpp`. Doing so would apply unit-range conclusions outside their hypotheses.

## 40. Feasibility of the remaining work

There are favorable structural constraints:

- `D` is reduced from 175 million to about 6.8 million;
- scales remain at most 139;
- only endpoint primes `{2,3,5,7}` can support internal-power exceptions;
- exact factor partitions, norm divisibilities, and slope matching offer strong pre-polynomial filters;
- modular gcd and sparse-Wronskian certificates are already sketched.

However, feasibility has not been demonstrated because the package gives no:

- complete endpoint packet state space;
- proof that the proposed branches are exhaustive and disjoint;
- number of branch records or shape pairs after each lower filter;
- memory or runtime projection;
- residual modular-gcd workload;
- completed certificate verifier.

A naive lower scan could still be enormous despite the smaller endpoint. The main difficulty is not the numeric size of `D`; it is the loss of the unit hypotheses that make the upper sieve one-dimensional in `k`.

My assessment is therefore:

> **A full computation looks plausible, but the current package does not establish its feasibility.**

---

# Part VI. Recommendations for a proof-grade release

## 41. Mathematical recommendations

1. Obtain an independent specialist review of the merged 2-adic residual polynomial, endpoint-power theorem, and the fourth-power Capelli branch.
2. State every external theorem in the exact notation needed at first use, including all hypotheses on monicity, residual irreducibility, injectivity, and proper subsums.
3. Separate theorems needed for the upper computation from broader structural claims, so that the computer-assisted theorem has a minimal auditable dependency graph.
4. For the lower range, define a finite endpoint-packet state object and prove a formal exhaustiveness theorem before implementing it.

## 42. Computational recommendations

1. Replace `assert`-based verification with explicit checked failures.
2. Emit a branch-coverage certificate. A practical format would record, for each scale pair and support-group pair, the input interval or shape-index ranges, counts before and after each filter, and a hash accumulator over rejected and surviving records.
3. Write a second, structurally different implementation of the production pair scan. The audit oracle is a prototype but does not scale to the full domain.
4. Add production tests with known nonzero survivors at several stages, not only zero final outputs.
5. Add checked casts and explicit domain assertions for every fixed-width conversion.
6. Make the cube-bound search ceiling derive from `D` rather than use `2,000,000`.
7. Validate CSV schemas and recompute shape invariants on input, or cryptographically bind the pair run to the exact shape-file hash.
8. Separate deterministic certificate files from timing logs in `SHA256SUMS`.
9. Provide a pinned container or reproducible environment for compiler, Python, SymPy, Sage/Arb, and `python-flint`.
10. For modular gcds, emit compact certificates containing the auxiliary prime, reduced leading data, gcd degree, and a checker independent of `python-flint`.

## 43. Lower-range implementation milestones

A credible path to a complete package would be:

1. Enumerate endpoint valuations only for `p=2,3,5,7` and prove the state list exhaustive.
2. Attach to each state the permitted factor degrees, packet occupancies, norm valuations, and Kummer degree multipliers.
3. Apply support, role, partition, endpoint norm, and slope filters before constructing any large polynomial.
4. Produce deterministic residual rows with full branch provenance.
5. Eliminate each residual row by an independently checkable modular gcd, sparse-Wronskian square-freeness certificate, or a new exact theorem.
6. Run an independent branch enumerator and compare hashes/counts.
7. Integrate all certificates into a verifier that does not reuse the search implementation's indexing or CRT code.

---

## 44. Final assessment

The bundle is unusually transparent about what it has and has not proved. Its main strengths are:

- a coherent mathematical path from collisions to a finite exact search;
- an explicit rather than merely effective endpoint;
- integer-only production decisions;
- a concise and fast computation;
- deterministic core data;
- clear mapping from propositions to code filters;
- successful full reproduction and reduced-domain independent oracle checks.

Its principal limitation is decisive: it does not finish the lower nonunit range. The upper theorem also retains a conventional source-code coverage trust boundary, and the specialized 2-adic local argument deserves independent expert scrutiny.

Subject to those reservations, I regard the claimed statement

\[
\text{“there is no normalized counterexample with }
6{,}816{,}242\le D\le175{,}394{,}637\text{”}
\]

as well supported by the paper and code. I do **not** regard the bundle, in its present form, as a complete computer-assisted proof of the full conjecture.

---

# Appendix A. Reproduction artifacts

The audit produced the following additional artifacts:

- `Qab9_reproduction_run.log` — full upper-pipeline counts;
- `Qab9_reproduction_time.log` — `/usr/bin/time -v` resource record;
- `Qab9_independent_oracle.py` — independent reduced-domain shape and pair oracle;
- `Qab9_independent_oracle_output.txt` — oracle results.

# Appendix B. Audit limitations

This was a detailed independent mathematical and implementation audit, not a formal proof-assistant verification. In particular:

- standard external theorems were checked against their published statements but not reproved;
- the complete 1.84-billion-pair universe was rerun through the supplied C++ code, not separately enumerated by the slower Python oracle;
- the Sage/Arb and optional `python-flint` paths were not dynamically run in the base environment;
- sanitizer testing used reduced domains;
- no hardware fault model or malicious compiler model was considered.

These limitations are compatible with the “source-verification” form of a computer-assisted proof, but they should be addressed if a higher-assurance certificate is desired.
