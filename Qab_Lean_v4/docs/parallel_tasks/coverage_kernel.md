# Branch Brief: Decidable Coverage Kernel

Suggested worktree:

```bash
git worktree add ../Qab_paper_coverage -b lean-coverage-kernel lean-formalization
cp secrets.env ../Qab_paper_coverage/secrets.env
```

Start in `../Qab_paper_coverage`.

## Slash Goal

```text
/goal In branch lean-coverage-kernel, implement the Phase 3 decidable interval-coverage kernel for residual finite searches.  Define a pure Lean checker showing that a sorted list of CoverageInterval values covers a target Nat interval [lo, hi] with no gaps, prove the checker sound, and add a small CSV-to-Lean-term generator or generator design that can emit typed coverage certificates later.  Keep this branch independent from polynomial/gcd certificate work except for using the existing CoverageInterval interface.  Before declaring ready, commit the branch, push it, and launch both review helpers from this worktree asking OpenAI and Claude to audit the kernel, edge cases, and generator interface; record the response id / Claude receipt path for later inspection.  You may interrupt and mark the goal blocked if you encounter a serious issue that needs external input to resolve, such as uncertainty about interval endpoint conventions, missing residual CSV semantics, or a generator format decision that would constrain later certificate branches.
```

## Scope

This branch is intentionally independent of Phase 2 polynomial work.  It should
produce deterministic, testable infrastructure for replacing the schematic
coverage part of `FiniteResidualPack`.

Primary files to inspect:

- `Qab_Lean_v4/Qab/Certificates/Interfaces.lean`
- `Qab_Lean_v4/Qab/Packs/FiniteElimination.lean`
- `Qab_Lean_v4/docs/Qab_Lean_Roadmap_v4.md`
- residual data files under `data/qab12/`

Likely new files:

- `Qab_Lean_v4/Qab/Certificates/Coverage.lean`
- a small generator under `tools/` or `Qab_Lean_v4/scripts/`
- optional focused tests/examples in a Lean module if they do not slow the
  build.

## Suggested Kernel

Useful definitions and theorems may include:

- a closed Nat interval predicate, e.g. `i ∈ [lo, hi]`;
- interval well-formedness `lo ≤ hi`;
- a recursive checker that consumes the next uncovered point and a sorted list;
- a theorem that checker success implies every `x` with `lo ≤ x ≤ hi` lies in
  some listed interval;
- edge-case tests for empty intervals, singleton intervals, touching intervals,
  overlaps, and gaps.

Endpoint convention matters.  Prefer closed intervals because the existing
`CoverageInterval` fields are named `lo` and `hi`; document any different
choice before using it.

## Acceptance Criteria

- `lake build Qab.Certificates.Coverage` passes, or the chosen module name is
  documented if different.
- Full `lake build` passes.
- The kernel is pure Lean and decidable; no certificate hash is treated as a
  proof.
- The generator emits or is documented to emit typed Lean terms that call the
  checker, not informal proof comments.
- The branch does not require Phase 2 modular-gcd code.
- OpenAI and Claude review processes are launched before the branch is marked
  ready.

## Review Questions

OpenAI / Claude should be asked to review:

- whether the endpoint convention and no-gap condition are correct;
- whether the checker theorem is strong enough to feed future residual coverage;
- whether the generator interface is stable for large CSV files;
- whether the proof design will scale without excessive generated term size.

