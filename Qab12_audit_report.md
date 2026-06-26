# Qab12 mathematical and computational audit report

## Executive assessment

Qab12 is a real advance over Qab10.  The upper-range computation remains intact; the unit-coefficient lower branch is now certificate-backed; the both-nonunit branch is eliminated; and the one-nonunit branch for `D >= 16584` is eliminated by a production all-shapes enumeration.  I found no fatal problem in those completed branches.

The package is still not a complete proof, and I found one important correction to the stated residual envelope.  The manuscript and README state that the remaining one-nonunit branch has `d <= 224`.  I do not find a proof of this for the one-nonunit case.  The `224` bound is justified for the both-nonunit comparison, where two independent nonunit coefficients give the logarithmic upper bound used in Proposition 19.  It does not automatically transfer to the residual one-nonunit branch.  From the global degree inequality alone, the safe bound at `D <= 16583` is

\[
 d^3 < 64D^2,\qquad D\le 16583,
\]

which gives

\[
 d\le 2601.
\]

This does not undermine the completed Qab12 branch eliminations, but it means the remaining production computation should be stated and implemented with `d <= 2601`, unless a new lemma proves the sharper `d <= 224` in the one-nonunit setting.

Despite that correction, the remaining work appears very feasible.  As an audit experiment, I wrote a separate prototype for the corrected residual one-nonunit range with `D <= 16583` and `d <= 2601`.  It enumerated 232,866 package states, reduced 29,532 same-key raw state pairs to 4 terminal state pairs, and a simple independent modular-gcd screen at `p = 1009` eliminated all terminal orientations.  This prototype is not a formal replacement for a production proof artifact, but it is strong evidence that the remaining computation is small enough for a laptop or ordinary compute server.

## Files and integrity

Bundle inspected: `/mnt/data/Qab12_review_bundle(1).zip`.

Root hashes recorded during audit:

```text
Qab12 zip SHA-256: 6090c58aee99e65a71d62c40fef57da94f244d22e982a0bd551c4b2f7d92805a
Qab12.tex SHA-256: 5755de844b12cd7cfdd660e90ce706511fca70b0f5643c03f2fd8a2ebb536146
Qab12.pdf SHA-256: 4c291a99d65c16089e543124b267ca7fbdcd3013a18c35e91a708428825b37d9
```

The bundle manifest `SHA256SUMS` validates all 1,416 listed files.  The PDF is a 65-page LaTeX document with embedded fonts, no encryption, no form fields, and no attachments.  I rendered the PDF to page images for layout inspection and used the TeX source for mathematical cross-reference checking.

## Reproduction checks performed

### Manifest and light verification

`make q12-verify-light` passed in my environment.  It rebuilt the C++ tools, checked the constants, verified the both-nonunit catalog, verified the one-nonunit `D >= 16584` catalog, and ran the small regression oracles.

Observed result:

```text
verified_two_nonunit_package_states=1054
verified_unique_common_factor_keys=1054
verified_two_nonunit_state_pairs=0
status=PASS

verified_one_nonunit_package_states=608490
aggregate_package_records=608490
aggregate_groups=514280
aggregate_raw_state_pairs=137530
aggregate_after_coprime_scales=10636
aggregate_after_range=7916
aggregate_after_extraction=7916
aggregate_after_disjoint=5430
aggregate_after_support=483
aggregate_after_degree=76
aggregate_after_role=0
aggregate_after_correspondence=0
aggregate_unique_state_pairs=0
aggregate_unique_orientation_pairs=0
verified_one_nonunit_survivors=0
status=PASS
```

The run took about 30 seconds and 395 MB peak RSS in this environment.

### Upper-range verification

`make q12-verify-upper` passed:

```text
verified_shapes=237418
verified_prefinal_pairs=761
verified_residual_candidates=0
status=PASS
```

This confirms the archived Qab9 upper computation remains replayable in Qab12.

### Modular certificate replay

The bundled logs report successful replay of the unit-branch modular certificates:

```text
unit large: verified_package_pairs=7, verified_orientation_certificates=28, status=PASS
unit small: verified_package_pairs=3, verified_orientation_certificates=12, status=PASS
unit defect: verified_shapes=46, verified_modular_factorizations=106, status=PASS
```

I could not independently rerun those two optional Make targets in this container because `python-flint` is not installed.  The scripts fail immediately with `ModuleNotFoundError: No module named 'flint'`.  This is an environmental reproducibility issue rather than a mathematical objection, but the final package should either pin `python-flint` in a reproducible environment or include a fallback verifier.

## Mathematical review

### Extraction degrees and reduced correspondence

The revised extraction identities are sound.  If `alpha` is a common root and `beta = alpha^r`, `gamma = alpha^s`, then the tower-law identities

\[
 d = t e_1 = u e_2
\]

are correct, and the field-degree inequality

\[
 d \le e_1 e_2
\]

is a necessary condition.  The reduced correspondence bound

\[
 d\leq
 \frac{rs(ae+bc)}{\gcd(rb,se)\gcd(ra,sc)}
\]

is also correctly derived from the two binomial correspondences in \(\mathbf P^1\times\mathbf P^1\).  The Qab10 ambiguity about ordered versus unordered orientations is fixed: Qab12 distinguishes equal selected ordered orientations from the opposite-orientation same-shape case, where the same-shape Bezout bound is used.

### Norm transfer and endpoint arithmetic

The norm-transfer identities are correct.  If the minimal polynomial of `alpha` has coefficients `(U,V)`, then the primitive factor coefficients on the `beta` side satisfy the expected valuation identities.  In the one-nonunit normalization, `U > 1`, `|V| = 1`, and `U | a` after choosing the leading endpoint.  The endpoint packet occupancy formula

\[
 w_p = \frac{b\lambda}{\kappa},\qquad
 \lambda = \frac r t v_p(U),
\]

with

\[
 1\le w_p\le \min\{b,e_1\},
 \qquad e_1-w_p\equiv 0\text{ or }-2\pmod p
\]

matches the code’s signature construction.  The signature key used by the one-nonunit code, `(U,d,sigma)`, is mathematically meaningful: for fixed `U`, equality of the signature records equality of the endpoint slopes for every coefficient prime.

### Capelli exceptional branch

The Qab10 gap around the exceptional `-4K^4` branch is substantially repaired.  The new lemma observes that if `beta = -4 eta^4`, then `-beta` is a square.  In the total-role and unit endpoint packets, the 2-adic root-of-unity approximation has valuation `1/ell < 1`, and the same valuation is inherited by `-beta - zeta`; the Newton-edge obstruction therefore excludes the exceptional branch there.  The remaining case is localized to a nonunit endpoint block, giving

\[
 e_1\le b,
 \qquad 2b\mid e_1\kappa
\]

or the reciprocal assertion.  This is the needed repair for Proposition 19’s Kummer-defect localization.  I would still recommend citing the precise Newton-edge square-obstruction statement at this point, because this is one of the densest local arguments in the manuscript.

### Unit-coefficient branch

The unit branch is now much stronger than in Qab10.  It is divided into full-Kummer large, full-Kummer small, and Kummer-defect cases.  The use of modular gcd certificates for terminal package pairs is sound: if the two trinomials have modular gcd of degree exactly two at a good prime, then only the forced `(x-1)^2` factor remains, so no noncyclotomic common factor over `Q` can exist in that orientation.

The unit-defect branch uses modular subset-degree certificates to prove irreducibility of 46 primitive shapes.  The certificate logic is sound: if a primitive polynomial has no rational factor degree except `0` and its full degree, then it is irreducible; the global isolation theorem then excludes every lift of those shapes.

### Both-nonunit branch

The both-nonunit reduction is coherent.  With primes dividing the two nonunit endpoint coefficients, the reduced correspondence and valuation bounds give the logarithmic upper bound on `d`; comparing this to the plastic-number lower bound excludes `D >= 16584`.  For `D <= 16583`, the `d <= 224` bound is valid in this branch, and the C++ enumeration plus Python row verifier find 1,054 one-package states with distinct common-factor keys.  Since no two states share a key, the empty state-pair file is a legitimate certificate for this branch, subject to generator coverage.

### One-nonunit branch above 16,583

The coefficient trichotomy for `D >= 16584` is sound: at most one endpoint coefficient is nonunit, and the nonunit coefficient is at most 26.  The production code enumerates `U = 2,...,26`, using coefficient-specific `D` caps and linear `D < C(U)d` bounds.  The pair sieve eliminates all 137,530 raw same-key state pairs before terminal polynomial gcd construction.  This branch appears complete.

### Residual one-nonunit branch

This is where the manuscript needs correction.  The stated remaining branch is

```text
D <= 16583, |V| = 1, 2 <= U <= D, d <= 224.
```

The first three conditions are justified.  The `d <= 224` condition is not justified for the one-nonunit branch as written.  It comes from the two-nonunit logarithmic comparison and should not be imported into the one-nonunit residual range without an additional proof.

The safe general bound available from Qab12’s inequalities is

```text
D <= 16583, |V| = 1, 2 <= U <= D, d <= 2601.
```

This matters for implementation: the current one-nonunit production code is hardwired to `U <= 26` and to three signature columns, while the residual branch allows `U` with up to five distinct prime factors below 16,583.  A final residual enumerator needs dynamic signature vectors, or at least five coefficient-prime slots.

## Additional residual-branch experiment

Because the stated residual range is the main remaining work, I wrote an independent prototype to estimate the corrected workload.  This is not part of the submitted proof package and should not be cited as a formal certificate, but it is useful for feasibility.

I ran two versions:

1. A narrow prototype with the manuscript’s stated `d <= 224` cap.
2. A corrected prototype with the safer `d <= 2601` cap.

The corrected `d <= 2601` prototype produced:

```text
smooth_totals=215358
shape_tests=4485172
core_tests=23467736
coefficient_choices=232866
raw_states=232866
unique_states=232866
groups=211994
raw_state_pairs=29532
after_coprime_scales=5657
after_range=5657
after_extraction=5656
after_disjoint=2331
after_support=426
after_degree=232
after_role=4
after_correspondence=4
unique_state_pairs=4
seconds=23.7078
maxrss=156924 KB
```

The four terminal state pairs collapse to two unique package pairs:

```text
U=8,  d=99:  (3; 440,1,441)  vs  (4; 3024,1,3025)
U=32, d=123: (1; 6560,1,6561) vs (2; 1024,1,1025)
U=32, d=205: same package pair
U=32, d=285: same package pair
```

A separate simple modular-gcd program checked all orientations of these terminal package pairs at `p = 1009`; every orientation had modular gcd degree exactly 2.  The modular screen took about 0.1 seconds.

Again, this is audit evidence, not a replacement for a production certificate.  It strongly suggests the final residual computation is small.

## Code review

### Strengths

The Qab12 code is much better organized than Qab10.  The light verifier recomputes arithmetic row conditions rather than merely trusting row counts.  The modular certificate verifiers reconstruct polynomials and recompute gcd/factorization data.  The branch manifest records counts and SHA-256 hashes for important artifacts.

The one-nonunit large run is deliberately conservative: it keeps shapes even when known irreducibility tests could discard them.  This is good proof engineering, because it avoids making correctness depend on too many theorem-specific early exits.

The both-nonunit verifier uses five signature columns and is closer to what the residual one-nonunit verifier will need.

### Issues and recommendations

1. **Correct the residual degree bound.**  Replace `d <= 224` by `d <= 2601`, or add and prove a one-nonunit-specific lemma giving `d <= 224`.

2. **Extend the one-nonunit code beyond `U <= 26`.**  The current generator rejects `U > 26`, and the package/pair CSV format has only three signature columns.  The residual branch allows `2 <= U <= 16583`; numbers in this interval can have up to five distinct prime factors.  The final code should use dynamic signatures or a five-column format.

3. **Make terminal modular checks replayable without environmental ambiguity.**  The optional unit certificate verifiers require `python-flint`.  Provide a pinned environment, container, or C++/FLINT-free fallback.

4. **Add an independent coverage verifier for the final residual branch.**  The current nonunit verifiers validate emitted rows and counts.  For the last branch, add a structurally different small-box oracle or a coverage proof over `(e,r,t,n,a,U)` / endpoint-divisor choices.

5. **Clean stale documentation and scripts.**  The manuscript still references `code/lower/endpoint_state.schema.json`, which is not present in the bundle.  It also refers to Sage/Arb scripts whose names do not match the Qab12 code.  `code/qab12/run_all_one_nonunit.sh` appears stale; it points to old executable and data paths.  The Makefile uses the working `run_all_one_nonunit_unfiltered.sh` script instead.

6. **Fix compiler warnings.**  The build emits several misleading-indentation warnings and `__int128` pedantic warnings.  The `__int128` use is reasonable under GCC, but the misleading-indentation warnings should be cleaned up before final submission.

## Progress assessment

| Branch | Qab12 status | Audit assessment |
|---|---:|---|
| Upper range `6816242 <= D <= 175394637` | Eliminated | Replayed successfully |
| Unit coefficients in lower box | Eliminated | Mathematically sound; bundled logs pass; local replay needs `python-flint` |
| Both endpoint coefficients nonunit | Eliminated | Light verifier replayed successfully |
| One endpoint coefficient nonunit, `D >= 16584` | Eliminated | Light verifier replayed successfully |
| One endpoint coefficient nonunit, `D <= 16583` | Remaining | Statement should use `d <= 2601` unless a sharper proof is added |

## Feasibility of the remaining work

Yes: the remaining work looks very reasonable for a separate laptop or compute server.  With the corrected `d <= 2601` cap, my independent prototype ran in under half a minute and found only four terminal state pairs.  A production-quality implementation with manifests, independent verification, and modular certificates may take longer to engineer and run, but the computational scale appears small, not weeks-scale.

A prudent final plan is:

1. Correct the residual theorem statement.
2. Implement a dynamic one-nonunit small enumerator over endpoint divisors `U | a`, not a naive loop over all `U`.
3. Emit package rows, state-pair rows, terminal orientation rows, counts, and SHA-256 manifests.
4. Verify rows with a separate checker that recomputes norm transfer, endpoint occupancy, deficient-prime conditions, radical signatures, role bounds, correspondence bounds, and terminal row coverage.
5. Certify any remaining terminal package pairs by modular gcd degree exactly 2 at good primes.
6. Add reproducible dependency instructions or a container for FLINT-based checks.

If implemented along those lines, the remaining computation should plausibly run on a normal multicore laptop or modest server in minutes to hours.  Even allowing for a more cautious independent verifier and certificate generation, it appears reasonable to complete outside the execution window of a single GPT call.
