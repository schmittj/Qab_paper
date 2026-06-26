# Independent mathematical and code audit of the Qab10 review bundle

**Audit date:** 25 June 2026  
**Bundle reviewed:** `Qab10_review_bundle(1).zip`  
**Bundle SHA-256:** `472bcd93e42fc8bd251b1226ee0eafefdd908749ac311f05883eb84af4ba5880`  
**Manuscript:** `Qab10.tex`, SHA-256 `9db095ddd30af75dbed30f3fca25b7f2b7f58028af6ee75d1a6acdf33a322c31`  
**Bundled PDF:** SHA-256 `adf0ebb1a7cb1cd1bde4b997a043b8e9eabeb921be70a26198c29565208a6454`

## 1. Executive conclusion

Qab10 is a meaningful and substantially more explicit revision of Qab9. It preserves the previously audited upper-range computation unchanged and adds a mathematically useful lower-range state reduction. Most of the new algebra is correct. The revision is also commendably explicit that it does **not** yet prove the full conjecture.

My conclusions are:

| Question | Audit conclusion |
|---|---|
| Does Qab10 prove the full reciprocal-package coprimality conjecture? | **No.** No production lower-state enumeration or terminal-certificate set is supplied. |
| Does the unchanged upper-range theorem remain supported? | **Yes.** The upper source files and three principal CSV artifacts are byte-for-byte identical to the audited Qab9 release. The safe verifier again reports 237,418 shapes, 761 pre-final pairs, and zero residual candidates. |
| Are the new extraction-degree, reduced-correspondence, norm-transfer, endpoint, and numerical-cutoff arguments sound? | **Yes, apart from minor exposition issues identified below.** I independently checked the identities and exact numerical transitions. |
| Is the new Kummer-defect proposition fully proved as written? | **Not yet.** Its treatment of Capelli's exceptional `-4 K^4` branch invokes earlier theorems that were stated only for ordinary internal `p`-th powers. This is a real proof omission, although a short repair appears available. |
| Does the supplied lower code exhaust or eliminate the remaining state space? | **No.** It is reference infrastructure only. It checks a subset of necessary conditions on tiny test boxes and deliberately is not a production generator. |
| Is feasibility of a complete lower computation established? | **No.** The reductions make such a computation plausible, but the package provides no auditable production counts, coverage manifest, runtime model, or complete certificate workload. |

The overall verdict is therefore:

> **The unchanged upper-range theorem passes. The new lower-range architecture is promising but not proof-complete. Proposition 19's exceptional fourth-power branch should be repaired before the new defect-localization and unit-defect cutoffs are cited as established theorems. Even after that repair, a production enumeration and independent certificate verification remain necessary.**

The package should not presently be represented as a computer-assisted proof of the full conjecture. It is best described as a credible finite-reduction program with one repairable mathematical gap and a substantial unimplemented computational obligation.

---

## 2. Scope and methodology

This audit covered the manuscript, all supplied source files, deterministic data, schema, reference states, build scripts, documentation, archive hashes, and PDF presentation.

The work comprised:

1. a differential audit against the archived Qab9 source;
2. a proof review of every new statement in Section 19 and its dependencies;
3. independent arithmetic checks of all new numerical cutoffs;
4. source review and dynamic testing of every new lower-range script;
5. schema validation and negative tests of the verifier boundary;
6. recompilation with warnings and rerunning the supplied upper and lower regression tests;
7. inspection of the modular-certificate architecture;
8. recompilation and visual rendering of the 62-page PDF.

The upper mathematics and production code are unchanged from Qab9. Rather than pretend that identical material was independently novel, I verified the hashes and re-applied the earlier audit conclusions. The prior Qab9 audit included a complete production rerun and a structurally independent reduced-domain enumeration oracle. Those results remain directly applicable to the identical upper sources and data in this bundle.

A fresh full upper pair scan was attempted in the present session but did not complete within the environment's current execution quota. This does not create a new evidentiary gap: the exact program and exact data were already fully reproduced in the preceding audit, and their cryptographic hashes are unchanged. The current warning-enabled build, regression suite, safe row verifier, and hash checks all passed.

---

# Part I. Revision integrity and unchanged upper theorem

## 3. What changed from Qab9

The substantive manuscript change is the replacement of the former residual-proof discussion by the new Section 19, “Lower-range extraction degrees and endpoint states.” The new section introduces:

- extraction degrees `t=[Q(alpha):Q(alpha^r)]` and `u=[Q(alpha):Q(alpha^s)]`;
- the general reduced power-correspondence bound;
- exact norm transfer to the primitive factors of `Q_{a,b}` and `Q_{c,e}`;
- scaled endpoint divisibilities and slope matching;
- the two-nonunit cutoff `D<=37,799`;
- the coefficient trichotomy above `D=50,000`;
- localization of deficient scale primes;
- an abstract finite lower-state object;
- an explicit statement of the remaining computational assurance boundary.

The bundle also adds lower-range Python scripts, a JSON schema, four tiny reference-state rows, a safe wrapper around the upper verifier, and a deterministic-manifest builder.

## 4. Hash identity of the upper proof artifacts

The following load-bearing files are exactly identical to Qab9:

| Artifact | SHA-256 | Qab9 match |
|---|---|---|
| `code/enumerate_shapes.cpp` | `5f53a0946265ad5dc951a2404ca3c69ef88bc8b8c1d9980891b2c6d8c682881d` | yes |
| `code/pair_upper.cpp` | `f9859a955cdaa8ea2932b5f428d850e17505583b4f6b066afd408bf6ea81e112` | yes |
| `code/verify_upper.py` | `82bb828e7f31839801d836e328d38b87f78f423ae8e6efb2e0957a5c94b263b3` | yes |
| `data/upper_shapes.csv` | `ead8e791b2f5b5e04122c606d51575f20836255c232ed58f9aab10f4afd7fe99` | yes |
| `data/upper_pair_survivors.csv` | `f4ff36cf9a766eefc14a73565dbf036674ffd95dc381c253bad352ca1f7a789a` | yes |
| `data/upper_residual_candidates.csv` | `69bac3fef15bcd6f3fc64a62a8c7f057e5ce6060b22dc39cf28c8e4cb9a80369` | yes |

The archived `Qab9.tex`, `Qab9.pdf`, and original checksum file also match their recorded hashes. Only the root documentation and Makefile differ as expected for the revision.

## 5. Current upper regression results

A clean warning-enabled build succeeded with:

```text
g++ -O3 -std=c++20 -fopenmp -Wall -Wextra -Wpedantic
```

The supplied tests reported:

```text
support_target_generation=PASS
small_enumerator_vs_bruteforce=PASS
factor_degree_reachability_vs_sympy=PASS
exact_degree_upper=PASS
constant_certificates=PASS
```

The new safe verifier wrapper reported:

```text
verified_shapes=237418
verified_prefinal_pairs=761
verified_residual_candidates=0
status=PASS
```

Because all upper sources and outputs are identical, the earlier full reproduction remains applicable: the upper scan considered 1,836,842,744 nominal shape pairs, retained 761 rows after all arithmetic filters, found all 761 to have the same primitive shape, and eliminated all of them by the incompatible degree bounds.

**Upper theorem audit conclusion:** unchanged and still supported, subject to the same conventional source-level coverage boundary documented in the Qab9 audit.

---

# Part II. Mathematical audit of the new lower-range section

## 6. Extraction-degree identities

The new notation is

\[
E=\mathbf Q(\alpha),\qquad K=\mathbf Q(\alpha^r),\qquad
L=\mathbf Q(\alpha^s),
\]

with

\[
d=[E:\mathbf Q],\quad e_1=[K:\mathbf Q],\quad e_2=[L:\mathbf Q],
\quad t=[E:K],\quad u=[E:L].
\]

The asserted identities

\[
1\le t\le r,\qquad 1\le u\le s,\qquad d=te_1=ue_2
\]

are immediate from the tower law and the equations

\[
\alpha^r\in K,\qquad \alpha^s\in L.
\]

The assertion `E=KL` is also correct. Since `gcd(r,s)=1`, choose integers `i,j` with `ir+js=1`. The common root is nonzero, so

\[
\alpha=(\alpha^r)^i(\alpha^s)^j\in KL.
\]

The reverse containment is automatic. Hence

\[
d=[KL:\mathbf Q]\le [K:\mathbf Q][L:\mathbf Q]=e_1e_2.
\]

No linear-disjointness assumption is made. This is exactly the right replacement for the unavailable full Kummer identity in the lower range.

**Audit status:** sound.

## 7. General reduced power-correspondence bound

For roots

\[
x=\alpha^r,\qquad y=\alpha^s
\]

of selected ordered primitive orientations `Q_{a,b}` and `Q_{c,e}`, the manuscript defines

\[
U_0=\frac a{a+b}x^b,
\qquad 1-U_0=\frac b{a+b}x^{-a},
\]

and similarly `V_0` from `y`. The relation `x^s=y^r` gives two binomial curves in `P^1 x P^1`:

\[
U_0^{E_0}=\lambda_0V_0^{B_0},
\qquad
(1-U_0)^{C_0}=\lambda_1(1-V_0)^{A_0},
\]

where

\[
B_0=\frac{rb}{\gcd(rb,se)},\quad
E_0=\frac{se}{\gcd(rb,se)},
\]

\[
A_0=\frac{ra}{\gcd(ra,sc)},\quad
C_0=\frac{sc}{\gcd(ra,sc)}.
\]

Their divisor classes have bidegrees `(E_0,B_0)` and `(C_0,A_0)`, so their intersection number is

\[
E_0A_0+B_0C_0
=
\frac{rs(ae+bc)}{\gcd(rb,se)\gcd(ra,sc)}.
\]

The common-component argument is valid. On the normalization of a hypothetical component, the two binomial identities force the four divisors of `U_0`, `1-U_0`, `V_0`, and `1-V_0` into a two-dimensional span. The earlier four-unit lemma restricts `V_0` to the six Möbius transforms of `U_0`. Substitution in the displayed divisor table leaves only `V_0=U_0` with `se=rb` and `sc=ra`, which, by primitivity, forces the same selected ordered shape and the same scale. That is the excluded identical-package case.

The injectivity argument is also correct: `U_0` determines both `x^b` and `x^{-a}`; Bézout for `gcd(a,b)=1` recovers `x`. The pair `(U_0,V_0)` therefore recovers `alpha^r` and `alpha^s`, and coprimality of `r,s` recovers `alpha`. Thus the `d` conjugates give `d` distinct intersection points.

### 7.1 Orientation qualification omitted in the manuscript

The sentence

> “For equal primitive shapes, `g_0=b` and `g_1=a`, so (19.2) recovers `d<=2rs`”

is correct only for equal **selected ordered orientations**, `(c,e)=(a,b)`. It is false as written if “equal primitive shape” is read in the package's usual unordered sense and the selected orientations are opposite.

For example, with `(a,b)=(1,8)`, `(c,e)=(8,1)`, `r=1`, and `s=2`, formula (19.2) gives `65`, whereas the earlier same-unordered-shape theorem gives `2rs=4`.

This does not invalidate (19.2). It means only that the new formula does not literally subsume the stronger old theorem in the opposite-orientation case. The manuscript should say “equal selected ordered orientations,” and a production checker should apply the old `2rs` bound whenever the unordered shapes agree.

**Audit status:** proposition sound; one imprecise specialization claim.

## 8. Norm transfer

Let

\[
h_\alpha(X)=UX^d+\cdots+V
\]

be the primitive minimal polynomial of `alpha`, and let the primitive minimal polynomial of `beta=alpha^r` have leading and constant coefficients `(u_1,v_1)`. The norm identity gives

\[
\left|\frac VU\right|^r
=
\left|\frac{v_1}{u_1}\right|^t.
\]

In the present context the fractions are reduced: `h_alpha` divides the primitive polynomial `Q_{a,b}(X^r)`, whose leading and constant coefficients divide the coprime integers `a` and `b`; similarly for the primitive factor of `Q_{a,b}`. Gauss's lemma therefore gives

\[
\gcd(U,V)=\gcd(u_1,v_1)=1.
\]

Prime-by-prime valuation comparison yields

\[
u_1^t=U^r,
\qquad |v_1|^t=|V|^r,
\]

and the analogous identities for the second package.

The proof in Qab10 says merely that “both fractions are in lowest terms.” That fact is valid here, but it should be justified explicitly; primitiveness of a polynomial alone does not imply that its leading and constant coefficients are coprime.

**Audit status:** correct with a minor omitted justification.

## 9. Scaled endpoint divisibilities and slope matching

Applying the earlier endpoint-divisibility proposition to the primitive factor of `Q_{a,b}` gives

\[
|v_1|^a\mid b^{e_1},
\qquad u_1^b\mid a^{e_1}.
\]

Raising to the extraction degree `t`, substituting the norm-transfer identities, and using `te_1=d` gives

\[
|V|^{ra}\mid b^d,
\qquad U^{rb}\mid a^d.
\]

The second package is identical. This derivation is exact and loses no prime-adic information.

If a prime divides `U`, the norm of `alpha` has negative valuation at that prime, so some conjugate embedding has `v_p(alpha)<0`. The endpoint Newton polygons then give

\[
v_p(\alpha)=-\frac{v_p(a)}{rb}
=-\frac{v_p(c)}{se}.
\]

The analogous positive-valuation argument for a prime dividing `V` gives the constant-endpoint slope equality.

**Audit status:** sound.

## 10. Two-nonunit cutoff

Suppose `U>1` and `|V|>1`. Since `gcd(U,V)=1`, choose distinct primes

\[
p\mid U,\qquad q\mid V.
\]

The slope equations imply the divisibilities

\[
B_0\mid v_p(a),\quad E_0\mid v_p(c),
\qquad
A_0\mid v_q(b),\quad C_0\mid v_q(e).
\]

Combining these with the correspondence bound gives

\[
d\le v_p(c)v_q(b)+v_p(a)v_q(e)
\le 2\lfloor\log_2D\rfloor\lfloor\log_3D\rfloor.
\]

Together with the previously proved strict lower bound `d>D/140`, this fails for every `D>=37,800`.

I independently checked the exact transition:

```text
D=37,799:  floor(D/140)+1 = 270, logarithmic upper bound = 270
D=37,800:  floor(D/140)+1 = 271, logarithmic upper bound = 270
```

Thus `37,799` is the exact last value not excluded by this coarse inequality.

The script `certify_lower_constants.py` checks all intervals on which the two logarithmic floors are constant, so it is not relying on a floating-point sample.

**Audit status:** sound and exactly certified.

## 11. Mahler-measure coefficient trichotomy

The paper uses

\[
\log M(h_\alpha)<\frac{8\log(2D)}{D^{1/3}}.
\]

The right side is decreasing for `D>=50,000`. At `D=50,000`, its actual value is approximately

\[
2.50007101605<\log 13\approx2.56494935746.
\]

The supplied rational certificate uses the safe inequalities

\[
50,000^{1/3}>36,
\qquad
\frac{8\log(100,000)}{36}<\log 13.
\]

The `log_interval` routine uses the convergent atanh series with an explicit positive tail bound; its interval arithmetic is correct for the arguments used here.

For a primitive polynomial, both the absolute leading coefficient and the absolute constant coefficient are bounded by its Mahler measure. Hence, when `D>=50,000`, each is at most `12`; the two-nonunit theorem leaves at most one nonunit endpoint coefficient.

**Audit status:** sound.

## 12. Localization of deficient scale primes

Let `p^a || r` and suppose `v_p(t)<a`. Put `delta=alpha^(r/p^a)`, so `delta^(p^a)=beta`. The composite-degree form of Capelli's binomial criterion says that, unless

\[
\beta\in K^p
\]

or, for `p=2` and `a>=2`,

\[
\beta\in -4K^4,
\]

the polynomial `X^(p^a)-beta` is irreducible over `K`. In that case `K(delta)/K` has degree `p^a`, forcing `p^a|t`, contrary to the assumed defect. This first paragraph of the proposition is correct.

The ordinary internal-power branch `beta in K^p` is then handled correctly:

- an odd good prime gives `e_1<=p-2`;
- a total-role prime is excluded;
- an endpoint-role prime is excluded from unit root packets;
- a factor supported in the nonunit endpoint block satisfies the endpoint degree and norm divisibilities;
- `kappa>=p` and `p^kappa<=D` leave only `p in {2,3,5,7}`.

### 12.1 Material proof omission: the exceptional `-4K^4` branch

The proof then says that the earlier total and endpoint theorems handle the exceptional fourth-power branch as well. They do not, as stated. Those theorems assume an ordinary internal `p`-th power

\[
\beta=w^p,
\]

whereas Capelli's exceptional alternative is

\[
\beta=-4\eta^4.
\]

The manuscript's earlier full-Kummer proposition contains a separate argument excluding this branch in the globally unit case, but Proposition 19 does not reproduce or extend that argument to nonunit endpoint factors. Consequently, the sentence

> “Theorem [endpoint power] ... gives (19.11) for the nonunit packet, including the exceptional fourth-power branch at `p=2`”

is not justified by the cited theorem.

This is a genuine gap in the proof of Proposition 19's exhaustive alternatives. It propagates to the stated unit-defect cutoff and to admissibility condition (vi) of the finite-state theorem.

### 12.2 A plausible short repair

The gap appears repairable without changing the numerical conclusions. A separate lemma can argue as follows.

Suppose

\[
\beta=-4\eta^4.
\]

Then

\[
-\beta=(2\eta^2)^2
\]

is a square in `K`.

For a root in a 2-adic unit packet, the existing local packet analysis gives, after an unramified extension,

\[
v_2(\beta-\zeta)=1/\ell<1
\]

with `zeta` of odd order and local degree at most `ell`. Since `v_2(2zeta)=1`,

\[
v_2(-\beta-\zeta)
=v_2((\beta-\zeta)+2\zeta)
=1/\ell.
\]

The Newton-edge power obstruction applied to `-beta` rules out its being a square. Thus the exceptional branch cannot occur in a total packet or in a unit endpoint packet.

If it survives at an endpoint, every conjugate of the factor must therefore lie in the nonunit endpoint block. This gives the same degree bound `e_1<=b` (or the reciprocal version). Moreover

\[
N_{K/\mathbf Q}(\beta)=(-4)^{e_1}N_{K/\mathbf Q}(\eta)^4
\]

has even 2-adic valuation. Comparing with the endpoint Newton valuation shows that `e_1 kappa/b` is even, hence

\[
2b\mid e_1\kappa.
\]

This is exactly (19.11) for `p=2`.

That repair should be written out and checked against both endpoint orientations. Until it is incorporated, I would not cite Proposition 19's defect localization as fully proved.

### 12.3 Local terminology issue

The phrase “`f_beta` is a unit polynomial” should be replaced by “`f_beta` is a `p`-adic unit factor” or equivalent. A factor can be globally nonunit because of another prime while still having `p`-unit leading and constant coefficients at the deficient prime. The local packet exclusion depends only on the latter condition.

**Audit status:** ordinary internal-power analysis sound; exceptional branch has a material but apparently repairable proof omission.

## 13. Unit-defect cutoff

Assuming the preceding proposition is repaired, the stated unit-defect cutoff follows correctly. For a globally unit common factor, every endpoint and total deficient prime is excluded, so any deficient prime is good. Then

\[
e_1\le p-2\le137,
\qquad d=te_1\le re_1\le139\cdot137.
\]

Together with `d>D/140`, this yields

\[
D<140\cdot139\cdot137=2,666,020.
\]

The strictness is handled correctly.

**Audit status:** numerically and logically correct once the exceptional branch is supplied.

## 14. Finite lower-state envelope

The theorem that every remaining counterexample maps to a finite, effectively enumerable integer state is fundamentally correct. Finiteness follows from:

- the explicit bound `D<=6,816,241`;
- `r,s<=139`;
- bounded primitive totals and shapes;
- bounded extraction and factor degrees;
- endpoint divisibilities, which bound the possible endpoint coefficients;
- finitely many role and factor-partition assignments.

Therefore an exhaustive elimination of a conservative superset of all such states would indeed prove the conjecture.

There are, however, several differences between the mathematical state claimed in the paper and what is currently encoded or checked:

1. The extraction lemma's necessary condition `d<=e_1e_2` is omitted from the admissibility list and from the checker.
2. The coefficient trichotomy is omitted.
3. Exact role assignments and factor-partition signatures are mentioned but are not represented as required state fields.
4. The orientation symbol `epsilon` appears in the mathematical tuple but not in the schema. Ordered `(a,b)` values may encode it redundantly, but the two descriptions should agree.
5. The state theorem depends on the unpatched exceptional fourth-power branch.
6. No theorem connects the abstract admissibility definition to a concrete production enumeration algorithm.

The first four omissions only enlarge the state superset, so they do not make the abstract finite reduction false. They do, however, weaken the claimed correspondence between the theorem, schema, and checker, and they matter for computational feasibility.

**Audit status:** basic finiteness theorem sound; advertised executable certificate object is not yet fully specified.

---

# Part III. Audit of the new lower-range code

## 15. `certify_lower_constants.py`

The following checks are correctly implemented with exact integer or rational arithmetic:

- the two-nonunit transition at `37,800`;
- the Mahler-measure comparison with `log 13`;
- the multiplication `140*139*137=2,666,020`.

The script works under Python optimization mode because it uses explicit exceptions rather than assertions.

One small discrepancy is that it merely prints

```text
endpoint_defect_primes=2,3,5,7
```

without recomputing that list. The older `code/lower_exception_catalog.py` does independently certify it by checking `p^p<=6,816,241`, and its result is correct. For a self-contained Qab10 preflight, the new script should compute or call that check rather than print a hard-coded line.

**Audit status:** correct for the constants it actually checks.

## 16. `lower_state_reference.py`

The checker correctly recomputes the following conditions for a supplied pair of package records:

- primitive ordered shape;
- extraction range and `d=t e_1`;
- proper-factor degree interval;
- coprimality of endpoint coefficients;
- valuation integrality implied by norm transfer;
- scaled endpoint divisibilities;
- the basic radical degree congruence `e_1=0 or -2 mod p`;
- common `(d,U,V)`;
- coprime scales;
- global degree bounds;
- disjoint scaled additive triples;
- the general reduced-correspondence bound;
- endpoint slope matching.

Those checks are implemented with unbounded Python integers and are not vulnerable to fixed-width overflow.

It does **not** verify the full admissibility definition in the paper. In particular, it does not check:

- `d<=e_1e_2`;
- the coefficient trichotomy;
- the detailed good/total/endpoint alternatives for deficient scale primes;
- the exceptional fourth-power branch;
- exact role assignments or partition signatures;
- orientation/provenance semantics;
- a production upper bound on `D`;
- terminal modular certificates;
- schema conformance.

It also coerces JSON values through `int(...)`, so strings and nonintegral numeric inputs may be silently converted rather than rejected by type. The unused line number in the reader is not included in error messages.

The manuscript's description that this checker recomputes “all global arithmetic constraints” is therefore too broad. It is a useful conservative reference checker for a subset of conditions, not a proof-grade verifier of the lower-state theorem.

**Audit status:** internally correct for its implemented subset; materially incomplete relative to the paper's state definition.

## 17. `enumerate_endpoint_states_reference.py`

The literal enumerator is honestly documented as a tiny-box coverage oracle rather than a production program. It reproduced the bundled `D=20`, coefficient-bound `2` output byte for byte:

```text
package_states=26
pair_states=4
validated_pair_states=4
```

The enumeration delegates filtering to the reference checker, so its correctness is limited by the same omitted conditions. It groups by common `(d,U,V)` and tests all unordered pairs in each group.

Points requiring clarification:

- It enumerates only positive `V`. This appears safe because `Q_{a,b}` has positive coefficients and no positive real root, so any real irreducible factor with positive leading coefficient must have positive constant coefficient. That argument should be stated; otherwise the sign restriction looks unexplained.
- It does not emit the mathematical orientation field `epsilon`.
- It emits the branch label `small_domain_reference`, which the supplied schema rejects.
- Its brute-force loop structure is not remotely a production implementation. In my scaling probe with coefficient bound `3`, it took about 8.8 seconds at `D=80` and did not finish `D=100` within a five-minute cap in this environment. This says nothing adverse about a future optimized generator, but it confirms that the reference enumerator itself supplies no production feasibility evidence.

**Audit status:** valid as a small regression toy; not a lower proof computation.

## 18. Schema inconsistency

`endpoint_state.schema.json` is syntactically valid Draft 2020-12 JSON Schema. However, every one of the four bundled reference rows fails it because the rows use

```json
"branch": "small_domain_reference"
```

while the schema permits only:

```text
unit_full_kummer
unit_good_prime_defect
one_nonunit_endpoint
two_nonunit_small_box
```

Independent validation gave:

```text
reference_rows=4
schema_valid=0
schema_invalid=4
```

The checker does not load the schema, so this inconsistency is not detected by `make q10-preflight`.

The schema is also too weak for a proof-grade exchange format:

- all integer fields lack lower and upper bounds;
- `additionalProperties` is true at both levels;
- orientation is absent;
- detailed role, defect-prime, valuation, partition, and certificate fields are absent;
- provenance is merely an arbitrary string;
- no canonical ordering constraint is expressible or checked.

This is a concrete package defect, though not a mathematical counterexample.

**Audit status:** schema file is valid, but the bundled data are nonconforming and the schema is not yet adequate for production proof states.

## 19. Upper verifier safety wrapper

`verify_upper_safe.py` correctly refuses to run when Python assertions are disabled. This addresses a finding from the prior audit.

However, the Makefile's official `verify` target still calls the old assertion-based script directly:

```make
python3 code/verify_upper.py
```

Under `PYTHONOPTIMIZE=1`, that script reports `PASS` while performing almost none of its proof checks. I confirmed this by corrupting a radical entry in a copy of `upper_shapes.csv`:

- normal verifier: failed with `AssertionError`;
- optimized direct verifier: printed `status=PASS` and exited zero;
- safe wrapper: refused to run.

The fix exists but is not wired into the documented command. The Makefile should call the safe wrapper, or, preferably, all proof checks in `verify_upper.py` should be changed from `assert` to explicit checked failures.

**Audit status:** useful partial fix; integration incomplete.

## 20. Modular-GCD certificate tooling

The mathematical logic of the worker is sound for a chosen orientation and good auxiliary prime:

- it constructs the two collision trinomials over `F_p`;
- it checks that `p` divides none of the scales or additive-triple entries, preserving displayed degree and exact multiplicity two at `x=1`;
- it computes the exact modular gcd using FLINT;
- gcd degree two then certifies that only the unavoidable `(x-1)^2` is common modulo `p`.

The sparse-remainder mode computes the larger trinomial modulo the smaller one without materializing the full dense polynomial. This is a reasonable implementation.

The Qab10 manuscript says that “a separate checker recomputes” terminal certificates. No such certificate checker is present. `modular_screen.py` is the search driver and `gcd_orientation_worker.py` is the computational backend. Neither reads a completed certificate file and independently revalidates every row. In fact, resumable operation trusts any existing `(pair_index,orientation)` entry and skips it without recomputation.

The certificate CSV also records only input parameters, a prime, and the asserted gcd degree; that is sufficient for a recomputing checker, but no such checker is supplied. There is no lower-state-to-worker adapter or production certificate set.

**Audit status:** plausible backend, not an independently verified certificate system.

## 21. Artifact manifest and reproducibility

The manifest builder is deterministic for a fixed directory tree. Rebuilding it over the audited tree reproduced all 54 entries, and every recorded hash and size matched.

There are nevertheless reproducibility-design issues:

1. Its docstring says benchmark logs are excluded, but it includes `data/resource_usage.txt` and the timing-bearing `data/upper_pipeline_output.txt` because neither resides in a path component literally named `benchmark`.
2. It includes `Qab10.pdf`. A fresh copy of the source compiled at a different timestamp produced a PDF with identical mathematical content but a different hash because PDF creation metadata changed. Reproducible builds therefore require a fixed `SOURCE_DATE_EPOCH` or explicit suppression of PDF timestamps.
3. The zip contains Python `__pycache__` bytecode files, but the manifest excludes them. Executable cached artifacts should be removed from the distribution rather than left unhashed.
4. Dependency requirements use open-ended minimum versions and do not provide a pinned container or lockfile.

These do not alter the mathematical outputs, but they should be fixed for a proof-grade archival release.

## 22. Build, PDF, and presentation

The manuscript compiled twice without LaTeX errors or substantive warnings. The rendered PDF has 62 pages. I visually inspected the new pages and found no clipping, missing equations, overlap, or unreadable code blocks.

The source and bundled PDF are consistent. The title, abstract, conclusion, and proof-boundary documents accurately state that the full conjecture is not yet proved.

Minor editorial issues include:

- `docs/REVISION_NOTES.md` is still titled “Revision notes from Qab8 to Qab9” and does not document the Qab10 changes;
- `docs/LOWER_RANGE_PLAN.md` is partly inherited from Qab9 and does not map exactly to the new state schema;
- the Makefile preflight does not run the reference enumerator or schema validation;
- `jsonschema` is not declared as a development dependency even though the package advertises a schema.

---

# Part IV. Findings by severity

## 23. Blocking finding: no complete lower proof computation

The package contains no production state generator, no exhaustive branch counts, no canonical state hash, no independent coverage implementation, no terminal certificate set, and no independent terminal-certificate verifier.

This is acknowledged by the authors, but it remains decisive. Qab10 is not a proof of the full conjecture.

## 24. Material mathematical finding: exceptional Capelli branch is not proved

Proposition 19's exhaustive defect alternatives use an earlier theorem outside its stated hypothesis. The `-4K^4` case must be handled separately. A concise repair appears available, but it is not currently in the manuscript.

Until repaired, the following new claims are not fully established as written:

- exhaustive deficient-prime localization;
- inclusion of the exceptional 2-adic branch in (19.11);
- the unit-defect cutoff insofar as it relies on all endpoint/total deficient branches being excluded;
- admissibility condition (vi) in the finite-state theorem.

The basic finite reduction can survive by temporarily omitting the unproved filter, but the stronger numerical architecture should not be treated as final without the patch.

## 25. Moderate assurance finding: theorem, schema, and checker do not coincide

The reference checker validates only a subset of the mathematical state conditions, the schema omits essential fields, and every bundled row violates the schema's branch enum. This prevents the current files from functioning as a coherent proof-certificate interface.

## 26. Moderate assurance finding: no independent modular certificate verifier

The manuscript describes one, but the bundle supplies only the search driver and worker. Existing certificate rows are trusted on resume. A proof-grade release requires an independent reader that reconstructs the polynomials and recomputes every claimed modular gcd.

## 27. Moderate feasibility finding: production scale is unsubstantiated

The mathematical constraints are encouraging, but the statement that the program is “realistically sized” is not supported by auditable evidence. The package gives no production generator, branch counts, asymptotic or empirical workload model, or canonical development logs. The reported exploratory zero-survivor runs cannot be reviewed.

## 28. Low-to-moderate implementation finding: safe verifier is not the official target

The wrapper correctly prevents optimized execution, but `make verify` bypasses it. This is easily fixed and should be fixed before release.

## 29. Minor mathematical/expository findings

- The equal-shape specialization of the correspondence formula needs an ordered-orientation qualification.
- Norm transfer should explicitly justify coprimality of leading and constant coefficients via Gauss's lemma and the coprime endpoints of `Q_{a,b}`.
- “Unit polynomial” should be made local at the deficient prime.
- The admissibility list should include `d<=e_1e_2` and the coefficient trichotomy for efficiency and fidelity.

## 30. Minor packaging findings

- reference data fail the schema;
- preflight does not validate schema or rerun the reference enumeration;
- endpoint-prime output is hard-coded in the new constants script;
- timing files and PDFs are mixed into the purported deterministic manifest;
- unmanifested `.pyc` files are distributed;
- Qab10-specific revision notes are missing.

---

# Part V. Completeness and feasibility assessment

## 31. Completeness of the unchanged upper theorem

The upper theorem remains complete under the same assumptions as the Qab9 audit:

1. every upper unit-range counterexample satisfies the enumerated primitive-shape and scale conditions;
2. the shape generator is exhaustive for the support cap;
3. the pair program enumerates the required scale and shape combinations;
4. every implemented filter is a necessary condition;
5. all 761 recorded pre-final rows satisfy those conditions;
6. the same-shape theorem eliminates all 761.

The prior independent reduced-domain oracle found no missing branch in the optimized indexing or CRT logic. The exact current hashes confirm that no upper regression was introduced.

**Conclusion:** the package still credibly proves

\[
6,816,242\le D\le175,394,637
\]

contains no normalized counterexample.

## 32. Completeness of the lower mathematical reduction

At a basic level, Qab10 does establish a finite lower problem: all indices, shapes, scales, extraction degrees, factor degrees, and endpoint coefficients lie in finite explicit ranges. The reduced-correspondence and endpoint identities are genuinely useful and should substantially shrink a production state space.

The stronger state definition is not fully certified until the exceptional fourth-power lemma is added. Even after that, the paper gives a mathematical superset description, not a verified correspondence between a concrete program's loops and every admissible branch.

## 33. Computational feasibility

### Favorable evidence

- The absolute range is reduced to `D<=6,816,241`.
- Scales remain at most `139`.
- Above `50,000`, at most one endpoint coefficient is nonunit and it is at most `12`.
- Both-nonunit factors are confined to `D<=37,799`.
- Assuming the defect lemma is repaired, endpoint defect primes are only `2,3,5,7`.
- Unit Kummer defects are confined below `2,666,020`.
- Exact slope and endpoint divisibility conditions are strong and cheap.
- Modular gcds can provide compact terminal eliminations.

### Missing evidence

- No count of primitive shapes or package states in each lower branch.
- No count after each factor-degree, partition, norm, slope, or correspondence filter.
- No demonstration that the branch tree is exhaustive and nonoverlapping in code.
- No estimate of terminal polynomial degrees or number of modular attempts.
- No production runtime or peak-memory measurement.
- No independent coverage hash.
- No certificate verifier.

The tiny reference enumerator cannot be extrapolated to the full domain. It is intentionally simple and becomes slow almost immediately.

**Feasibility conclusion:** a complete computation is plausible, and Qab10 improves the prospects materially, but the package does not establish that it fits the stated 25-core, seven-day budget.

---

# Part VI. Required changes for a proof-grade Qab11 release

## 34. Mathematical repairs

1. Add a formal lemma for the `beta in -4K^4` endpoint and total branches, including the square obstruction for `-beta` and the parity-of-norm argument.
2. Qualify the correspondence specialization by ordered orientation and retain the old `2rs` bound for opposite orientations of the same unordered shape.
3. Add the Gauss-lemma coprimality sentence to norm transfer.
4. Replace global “unit polynomial” language by local `p`-adic unit language.
5. Put `d<=e_1e_2`, the coefficient trichotomy, and all intended branch fields into the formal admissibility definition.

## 35. Computational repairs

1. Implement one deterministic production lower-state generator.
2. Implement a structurally different coverage generator or interval/branch certificate checker.
3. Define canonical ordering and hashing of every state.
4. Emit branch counts before and after every filter.
5. Make the JSON schema strict and make every output validate it.
6. Integrate schema validation and the tiny enumerator into preflight tests.
7. Write an independent modular-certificate verifier that does not trust the search driver's completed-file index.
8. Wire `make verify` to the safe wrapper or remove all assertion-based proof checks.
9. Separate deterministic mathematical artifacts from benchmark logs.
10. Remove cached bytecode and pin the compiler/Python/dependency environment.

## 36. Suggested certificate design

A robust production record should minimally contain:

- canonical first and second package states;
- selected orientation or an unambiguous ordered shape;
- `r,t,e_1,s,u,e_2,d,U,V`;
- the precise branch tag;
- every deficient scale prime, its valuation in the scale, and its role;
- endpoint valuation exponent `kappa` where applicable;
- exact role/partition signature identifiers;
- the rejection reason or terminal certificate identifier;
- a canonical record hash.

A small independent verifier should recompute all integer conditions, verify branch coverage metadata, reconstruct each terminal finite-field calculation, and reject unknown or extra fields rather than silently accepting them.

---

## 37. Final assessment

Qab10 successfully preserves the strongest verified result from Qab9 and adds several correct and valuable lower-range reductions. In particular, the extraction-degree framework, generalized correspondence geometry, scaled endpoint arithmetic, two-nonunit cutoff, and coefficient trichotomy are substantive progress.

The revision also improves transparency: it explicitly separates proved upper evidence from exploratory lower development. That is the correct scientific boundary.

The remaining concerns are not cosmetic. One new local branch is not actually proved by the theorem cited for it, and the lower software does not yet implement or certify the finite universe described in the paper. The schema/checker mismatch and absent modular verifier show that the certificate layer is still at the design-prototype stage.

My final classification is:

> **Upper-range computer-assisted theorem: PASS, with the previous source-coverage reservations.**  
> **New lower mathematical architecture: PASS except for one material, apparently repairable exceptional-branch gap.**  
> **Full conjecture: NOT PROVED.**  
> **Production feasibility: PLAUSIBLE BUT NOT DEMONSTRATED.**

---

## Appendix A. Reproduced lower outputs

```text
two_nonunit_max_D=37799
coefficient_trichotomy_start_D=50000
coefficient_mahler_upper_integer=13
unit_defect_strict_upper_D=2666020
endpoint_defect_primes=2,3,5,7
lower_state_reference_self_test=PASS
```

Reference enumerator at the bundled parameters:

```text
package_states=26
pair_states=4
validated_pair_states=4
byte_identical_to_bundle=yes
```

Schema result:

```text
schema_meta_validation=PASS
schema_valid_reference_rows=0
schema_invalid_reference_rows=4
```

## Appendix B. Upper verifier negative test

After altering one recorded radical in a temporary copy of the shape CSV:

```text
normal verify_upper.py: AssertionError, exit 1
PYTHONOPTIMIZE=1 verify_upper.py: status=PASS, exit 0
PYTHONOPTIMIZE=1 verify_upper_safe.py: refuses to run, exit 1
```

This confirms both the old verifier weakness and the correctness of the new wrapper.
