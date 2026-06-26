## Executive verdict

I did **not** find a fatal mathematical error in the proof chain or in the decisive finite eliminations represented by the current artifacts. The repository looks like a serious, coherent computer-assisted proof bundle, not merely a sketch. In particular, the corrected residual one-nonunit branch now appears aligned with the manuscript: (D\le 16583), (2\le U\le D), (d\le2601), four terminal state pairs, two terminal package pairs, and eight modular gcd certificates.

That said, I would **not publish the repository exactly as-is**. The main remaining risks are not that I found a false theorem, but that an expert referee will have difficulty locating the proof obligations, distinguishing generator trust from verifier trust, and reproducing the computational branches cleanly. The paper is close to being reviewable, but the public version needs a sharper certificate contract, cleaner reproducibility story, and a few expansions of the most compressed mathematical reductions.

My recommended publication status is:

> **Mathematical core: provisionally pass, subject to specialist review of the p-adic/Kummer packet arguments and the sparse-polynomial degree bound.
> Repository/public release: not quite ready; fix the reproducibility and exposition blockers below first.**

## What I inspected and replayed

I inspected the top-level manuscript and PDF, the README/MANIFEST/AGENTS files, current code under `code/qab12/`, proof artifacts under `data/qab12/`, archived upper-range material, logs, and historical audit files.

The checksum file verified cleanly: `sha256sum -c SHA256SUMS` reported all 1,433 listed entries as OK.

The bundled PDF is 67 pages, with embedded fonts and no obvious rendering/clipping problems in the pages I spot-checked. The final LaTeX log `logs/qab_pdflatex_final3.log` did not show unresolved references/citations or overfull-box warnings in my grep pass.

I replayed the main non-FLINT verification pieces individually. The following passed in this environment:

```text
certify_qab12_constants.py
verify_two_nonunit.py
verify_one_nonunit.py --data-dir data/qab12
verify_one_nonunit_all_manifest.py
verify_one_nonunit_residual.py --manifest data/qab12/one_nonunit_residual_manifest.json
test_one_nonunit_small.py
test_one_nonunit_residual_small.py
test_two_nonunit_small.py
verify_upper_safe.py
```

Important counts I confirmed from the replayed scripts and manifests include:

```text
two-nonunit package states:             1,054
two-nonunit state pairs:                    0

one-nonunit D >= 16,584 package states: 608,490
raw same-key state pairs:              137,530
after role/correspondence:                   0

residual package states:               233,278
residual raw state pairs:               29,611
after role/correspondence:                   4
terminal orientation package pairs:          2
residual modular certificates:               8

archived upper verifier:
verified_shapes:                       237,418
verified_prefinal_pairs:                   761
verified_residual_candidates:                0
```

I could not run the FLINT-dependent modular/irreducibility replays in this container because `python-flint` is not installed. The repo pins `python-flint==0.8.0` in `requirements-optional.txt`, and the bundled logs record successful runs for the unit large/small modular gcd certificates and the direct irreducibility verifier. For public release, this should be containerized or placed in CI, because a referee should not have to reconstruct a compatible FLINT environment manually.

## Mathematical audit

### 1. Main collision dictionary and normalization

The reduction from package common factors to collisions among selected ordered trinomials looks internally consistent. I checked the reciprocal normalization, the unit-circle exclusion, the squarefreeness/double-root handling at (x=1), and the “no three” mechanism. I did not find a counterexample to the stated collision dictionary.

The no-three theorem, as written, is one of the cleanest parts of the paper. The triangle-equality/unit-circle argument and the divided-difference/sign-law style reasoning appear sound. This is important because several later arguments use it to rule out complementary or overdetermined edge configurations.

The proper-divisibility rigidity argument also looks substantially correct. The diagonal-denominator comparison, endpoint coefficient comparison, and boundary use of Eneström–Kakeya/no-three logic are doing real work, and I did not see an unhandled orientation case. I would still add a brief “orientation audit” paragraph after that proposition, because this is exactly the kind of place where a referee will worry about swapped (a,b) or reciprocal orientations.

### 2. Finite support/local finiteness/S-unit sections

The point-finite and local-finiteness arguments are credible. The inequality controlling (k/m) for (|z|<1), and the finite-support consequence, look correct. The S-unit finiteness material is useful but not always obviously part of the shortest route to the final theorem. For readability, I would mark which sections are logically necessary for the final proof and which are structural context.

### 3. Schinzel fibre and self-power/Kummer reduction

This is one of the proof’s highest-risk zones for expert review. I did not find a definite mathematical error, but the current exposition is dense enough that a specialist reader may have to reconstruct too much.

The “Schinzel fibre” lemma and the valuation case split should be expanded. In particular, I would add a small appendix giving the cyclotomic valuation table explicitly: what happens at primes dividing (a), (b), (a+b), at endpoint packets, at the center-(1) packet, and in the exceptional (p=2) branch. That appendix would make the later Kummer-defect enumeration much easier to trust.

The use of Borisov’s local packet lemmas and reducibility/factor-degree information is a genuine external dependency, not just background. The bibliography points to Borisov’s Acta Arithmetica paper, which is indeed the relevant abc-polynomial source. For publication, quote the exact lemma numbers/statements being imported, including hypotheses and convention translations. ([eudml.org][1])

### 4. Exceptional (-4K^4) branch

The current treatment of Capelli’s exceptional branch is much improved over what the historical audits describe. I checked the logic around replacing (\beta) by (-\beta), especially the (2)-adic unit-packet issue. The ultrametric step is plausible: in characteristic-zero (2)-adic valuation, a root close to an odd-order root of unity remains in the right obstruction regime after the sign change because the (2\zeta) term has valuation (1), while the packet distance is (<1).

I would still expand this proof slightly. It is short, but it carries a lot of weight: it justifies that the enumeration does not miss the exceptional fourth-power branch. A referee will likely ask for more explicit links between Capelli’s criterion, the unit packet obstruction, and the endpoint-only survivor condition.

### 5. Sparse Wronskians/direct degree bound

The field-degree/sparse-polynomial bound in Section 17 is elegant, but it is another high-load section. The lattice determinant estimate, rank-two subtorus reduction, toric degree estimate, and lower Mahler bound all fit together plausibly. I did not find a numerical contradiction.

However, this should be made more modular. State the imported sparse-polynomial theorem in the exact form used, then state a standalone “specialization to this four-term family” proposition with all constants. The paper cites Amoroso–Sombra–Zannier, whose structure theorem for multiple non-cyclotomic irreducible factors of sparse polynomials is the relevant external input. ([arXiv][2])

If higher Newton polygon language is part of the local packet justification, the paper should also make the exact dependency clear; Guàrdia–Montes–Nart is a standard source for higher Newton polygon methods in (p)-adic factorization, but the manuscript should specify whether it is using a theorem from that work or only background terminology. ([arXiv][3])

### 6. Unit-coefficient branch

The three-way split in Section 20 is mathematically reasonable:

1. full Kummer, (50,000\le D\le6,816,241);
2. full Kummer, (D<50,000);
3. deficient scale prime.

The terminal modular-gcd logic is sound in principle: after accounting for the forced double root at (x=1), modular gcd degree exactly (2) at a good prime rules out an additional noncyclotomic common factor.

The main issue is presentation/certification. The manuscript states in Section 20 that in the large full-Kummer branch
[
r,\operatorname{rad}(ab(a+b))<1,612,000.
]
This is plausible from the preceding support envelope (C(D)) at the endpoint (D=50,000), but the earlier printed exact support cap is (4,398,937), and the active C++ comment in `pair_unit_large.cpp` mentions the (4,398,937) Qab9 cap while the code uses `SUPPORT_PRODUCT_CAP = 1612000`. This is not necessarily wrong, but it is a public-review hazard. Add an explicit exact certificate line proving the (1,612,000) cap for (D\ge50,000), and change the code comment so the mathematical and computational constants are visibly identical.

The active Makefile also does not give a clean full replay target for the whole unit large/small enumeration path. It verifies the terminal modular certificates, but it does not make the unit full-Kummer enumeration as self-contained as the residual nonunit branch. Before dissemination, add a unit-branch manifest verifier analogous to the residual verifier.

### 7. Nonunit branches

The nonunit part is the most convincing computational portion of the current repository.

The both-nonunit branch is small and well controlled: the cutoff (D\le16583), (d\le224), endpoint valuation bound, and distinct common-factor keys are all consistent with the verifier.

The one-nonunit (D\ge16584) branch now has a clear coefficient table (U=2,\ldots,26), and the row/count verifier confirms that the pair sieve reaches zero after the local role-binomial bound. The verifier is explicit that it is a row/count verifier, not an independent production enumerator; that honesty is good, but the manuscript should state the same trust boundary.

The corrected residual branch is a strong part of the repository. The verifier recomputes row conditions, reruns the pair sieve, compares the terminal state/orientation CSVs exactly, and recomputes the eight residual modular gcds over (\mathbf F_{1009}) using pure Python polynomial arithmetic. This is the right model for the rest of the computational proof.

## Computational and reproducibility issues

### Blocker 1: verifier should not mutate proof artifacts

`verify_one_nonunit_residual.py --manifest data/qab12/one_nonunit_residual_manifest.json` currently writes the manifest. The content is deterministic and matched the bundled artifact in my runs, but a command named “verify” should not silently overwrite tracked proof data.

Change this to two modes:

```text
--check-manifest path     read and compare
--write-manifest path     regenerate intentionally
```

Then make `make verify-light` use `--check-manifest`.

### Blocker 2: unit branch needs the same manifest discipline as residual branch

The residual branch has a good verifier contract. The unit branch is less clean. The repo includes terminal modular certificates and logs, but the large/small full-Kummer enumeration path is not wrapped in a comparable current manifest verifier.

For public release, add a `unit_branch_manifest.json` containing at least:

```text
shape list hashes
package list hashes
pair-sieve output hashes
stage counts
terminal package-pair hashes
terminal orientation-pair hashes
modular certificate hashes
script/compiler hashes or versions
```

Then add a verifier that checks those hashes, recomputes row-level conditions, and reruns the pair sieve or at least independently checks the logged terminal rows.

### Blocker 3: reproducible environment

The README says optional dependencies are pinned, but a public proof bundle should include a Dockerfile, Nix flake, conda environment, or CI workflow. The current situation is:

```text
python-flint==0.8.0 pinned
sympy==1.14.0 pinned
jsonschema==4.23.0 pinned
C++ requires GCC/Clang, OpenMP, GNU __int128
```

That is a good start, but not enough for a referee. I could not run the FLINT-dependent scripts in this container because `flint` was absent. The bundled PASS logs help, but public dissemination should make these checks one-command reproducible.

### Blocker 4: Makefile target names overstate coverage

`q12-build` builds only a subset of `code/qab12/*.cpp`. It does not build every active or archived tool in the repository. This is fine if intentional, but then call it something like `build-nonunit-light`, or add separate targets:

```text
make build-all-current
make verify-nonunit
make verify-unit
make verify-upper
make verify-full
```

A public referee should not have to infer which tools are proof-critical.

### Blocker 5: generator/verifier trust boundary should be formalized

Some verifiers are genuinely independent recomputers; others are row/count checkers. For example, `verify_one_nonunit.py` explicitly says it is “not an independent production enumerator.” That is acceptable, but the paper needs a computational certificate appendix with a table like:

```text
artifact                  generator obligation       verifier obligation       remaining trust
one_nonunit_all_*.csv      exhaustive enumeration      row checks/counts         generator coverage
residual_packages.csv      exhaustive enumeration      row + pair recompute      generator coverage
residual certs             terminal gcd search         gcd recompute             none beyond arithmetic
unit_large certs           terminal gcd search         FLINT gcd recompute       unit enumeration coverage
```

This would make the proof much easier to audit.

## Presentation and writing

The paper is much more readable than a raw computation dump, and the proof map is useful. Still, the manuscript is trying to do three jobs at once:

1. introduce a new mathematical reduction;
2. prove many structural lemmas;
3. document a large proof-producing computation.

That makes the current 67-page paper cognitively heavy. I would restructure for expert dissemination as follows.

First, add a one-page dependency diagram after the introduction. It should show the path:

```text
collision dictionary
→ structural reductions
→ upper-range computation
→ lower state object
→ unit branch
→ nonunit branches
→ residual certificates
→ main theorem
```

Second, label optional/contextual sections. Some of the phase localization, Schur deformation, rational-root, and density-isolation material may be mathematically interesting, but the reader needs to know whether it is part of the shortest proof path.

Third, add a “computer-assisted proof contract” appendix. This is the single highest-value readability improvement. Include the exact CSV schemas, field meanings, allowed ranges, and the lemma that maps every hypothetical counterexample to one row in one generator output.

Fourth, make the external dependencies easier to verify. For Borisov, ASZ, and any Newton-polygon reference, quote the exact theorem/lemma used and state the substitution into this notation. Do not force a referee to reverse-engineer how a cited theorem applies.

Fifth, revise the AI disclosure. The current “Use of AI tools” section says a fuller account will be added in a later revision. That is not public-ready. Either give the fuller account now or shorten the section to a final, self-contained disclosure explaining which parts were AI-assisted and which parts are certified by deterministic artifacts/human review.

## Repository hygiene

Remove or rewrite `AGENTS.md` before publication. It contains the private backup remote:

```text
[private remote redacted]
```

That is not mathematically harmful, but it should not be in a public release.

The historical audits in `docs/audits/` are valuable, but they currently contain statements that are now superseded, including claims about stale manifests and incomplete residual branches. The README says these are historical, which helps. I would still add `docs/audits/README.md` with a chronology:

```text
Qab9: upper-range partial proof
Qab10: lower-state infrastructure, incomplete
Qab12: found residual d<=224 issue
Qab12 revised/current: residual d<=2601 completed
Qab13 audit: some findings superseded by current tree
```

Several logs contain absolute old working paths such as `/mnt/data/Qab12_work`. This is acceptable as provenance, but I would move resource-usage logs into a clearly marked provenance subdirectory or normalize paths in regenerated logs.

The file `docs/WRITING_GUIDANCE_V2.md` is not a proof artifact. It is harmless, but for an expert public release it may distract from the mathematical archive. Consider moving it out of the release bundle or into a clearly non-proof `meta/` directory.

## Priority fix list before making the repository public

**Must fix before public release:**

1. Add a computational-certificate appendix with CSV schemas, verifier contracts, and branch coverage statements.
2. Make all verification commands non-mutating; split manifest writing from manifest checking.
3. Add a reproducible environment: Docker/Nix/CI with `python-flint`, compiler, and exact command transcript.
4. Add a current unit-branch manifest verifier, not only terminal modular certificate checks.
5. Remove the private GitHub remote from `AGENTS.md`.
6. Replace the “fuller account later” AI disclosure with final text.
7. Add an exact printed certificate for the (1,612,000) unit-large support cap and align the C++ comment with the manuscript.

**Strongly recommended before sending to experts:**

1. Expand the Schinzel/Kummer/local packet section with an explicit valuation-case appendix.
2. Quote exact Borisov and ASZ statements used, including notation translation.
3. Add a one-page proof dependency graph.
4. Mark historical audits as superseded where appropriate.
5. Add runtime expectations for each verifier target.
6. Refactor the most compressed C++ verifiers for readability: braces, named predicates, fewer one-line compound conditions.
7. Add a top-level `PUBLICATION_CHECKLIST.md` recording the exact commands and expected outputs.

## Bottom line

The current repository appears to contain a coherent proof package, and I did not find a mathematical or computational defect that invalidates the claimed theorem. The decisive residual correction to (d\le2601) is now represented consistently in the manuscript, README, manifests, and verifier outputs.

The main danger is **reviewability**. The mathematical proof is dense, and the computation is strong but not yet packaged in the cleanest possible way for independent referees. With a formal verifier contract, non-mutating manifests, a reproducible FLINT environment, and a clearer exposition of the p-adic/Kummer and sparse-polynomial inputs, this would be much better positioned for public dissemination.

[1]: https://eudml.org/doc/207137?utm_source=chatgpt.com "On some polynomials allegedly related to the abc conjecture"
[2]: https://arxiv.org/abs/1412.8059?utm_source=chatgpt.com "Unlikely intersections and multiple roots of sparse polynomials"
[3]: https://arxiv.org/abs/0807.4065?utm_source=chatgpt.com "Higher Newton polygons in the computation of discriminants and prime ideal decomposition in number fields"
