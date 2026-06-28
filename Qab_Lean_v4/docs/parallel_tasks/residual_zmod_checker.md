# Branch Brief: Residual ZMod 1009 Checker

Suggested worktree:

```bash
git worktree add ../Qab_paper_phase2_zmod -b lean-phase2-zmod lean-formalization
cp secrets.env ../Qab_paper_phase2_zmod/secrets.env
```

Start in `../Qab_paper_phase2_zmod`.

## Slash Goal

```text
/goal In branch lean-phase2-zmod, build the first residual Phase 2 modular-gcd certificate checker over ZMod 1009.  Use the shared prelude Qab.Polynomials.Collision, especially collisionTriZ, to match the orientation-level residual trinomials and account explicitly for the forced cyclotomic square / double root at X = 1.  Aim for a checked Lean kernel plus generated or typed data for an initial useful set of residual terminal rows, with lake build passing and the design documented.  Before declaring ready, commit the branch, push it, and launch both review helpers from this worktree with branch-specific questions for OpenAI and Claude; record the response id / Claude receipt path for later inspection.  You may interrupt and mark the goal blocked if you encounter a serious mathematical, data-format, or infrastructure issue that needs external input to resolve, such as an ambiguity in which rows/orientations the Python verifier certifies, a mismatch between collisionTriZ and the artifact data, or prototype evidence that the intended decidable checker is computationally infeasible without changing certificate format.
```

## Scope

This branch is the highest-value Phase 2 certificate milestone.  It should be
self-contained and avoid changing theorem-pack boundaries unless the need is
documented.

Primary files to inspect:

- `Qab_Lean_v4/Qab/Polynomials/Collision.lean`
- `Qab_Lean_v4/Qab/Certificates/Interfaces.lean`
- `data/qab12/one_nonunit_residual_orientation_pairs.csv`
- `data/qab12/one_nonunit_residual_modular_certificates.csv`
- `code/qab12/verify_one_nonunit_residual.py`

Likely new files:

- `Qab_Lean_v4/Qab/Certificates/ZModGcd.lean`
- `Qab_Lean_v4/Qab/Certificates/ResidualZMod1009.lean`
- a generator under `tools/` or `Qab_Lean_v4/scripts/` if generated Lean terms
  are needed.

## Acceptance Criteria

- `lake build Qab.Certificates.ZModGcd` passes, or the chosen module name is
  documented if different.
- `lake build` passes for the full Lean package.
- The checker verifies real typed certificate content, not metadata hashes.
- The target is clearly `PolynomialCheckTarget.collisionH` unless the branch
  deliberately switches to a divided target and documents that change.
- Forced factors are accounted for explicitly; do not report an undivided
  collision gcd as excluding noncyclotomic sharing without subtracting the
  forced degree.
- A short design note explains whether the checker uses Mathlib `Polynomial`
  directly, a computable sparse representation, or generated Euclidean/Bezout
  certificates.
- OpenAI and Claude review processes are launched before the branch is marked
  ready.

## Review Questions

OpenAI / Claude should be asked to review:

- whether the encoded polynomials match the residual Python verifier;
- whether the certificate format is likely to scale;
- whether the forced-factor accounting is mathematically sound;
- whether the trust boundary is genuine typed Lean checking rather than replay
  of artifact metadata.

