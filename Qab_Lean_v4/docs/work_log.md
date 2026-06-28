# Lean Formalization Work Log

## 2026-06-28T13:24:04+02:00

- Added root `.gitignore` entry for `secrets.env`.
- Unpacked `Qab_Lean_v4_Package.zip` into `Qab_Lean_v4/`.
- Located local Mathlib installs and selected the built `v4.29.1` package at
  `/mnt/c/Users/jo314/Desktop/mathagents/test_run_problems/erdos539_gcd_quotients/lean/.lake/packages/mathlib`.
- Temporarily tested retargeting `Qab_Lean_v4` to the installed Lean/Mathlib
  version instead of cloning or fetching a fresh Mathlib copy.

## 2026-06-28T13:34:47+02:00

- Created central reusable Mathlib checkout `/home/jo314/lean/mathlib4-central`
  at tag `v4.31.0`, commit `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
- Installed Lean toolchain `leanprover/lean4:v4.31.0` through `elan`.
- Ran `lake exe cache get` in the central Mathlib checkout.  The cache command
  decompressed 8516 files and warned that a small number of cache files were
  unavailable.
- Repointed `Qab_Lean_v4/lakefile.lean` to the central local Mathlib checkout.

## 2026-06-28T13:39:45+02:00

- Fixed Lean `v4.31.0` syntax/API drift:
  - replaced opaque predicate declarations using `constant` with `axiom`;
  - expanded grouped structure fields in `NormCE`, `TerminalRow`, and
    `CoverageInterval`.
- Verified `cd Qab_Lean_v4 && lake build`.
- Verified `cd Qab_Lean_v4 && lake build Qab.Packs.BroadAxioms`.

## 2026-06-28T13:53:49+02:00

- Added AI review helpers under `tools/ai_review/`.
- Verified dry-run bundle creation for OpenAI and Claude review helpers; the
  default bundle currently contains 78 files and is about 1.5 MB.
- Reworked Claude reviews to launch as background agents instead of blocking
  the main development session.
- Launched Claude background review:
  - agent id: `0d872b98`;
  - name: `qab-lean-review-20260628-135309`;
  - status/log commands: `claude agents`, `claude logs 0d872b98`.
- Submitted OpenAI background Responses review:
  - model: `gpt-5.5-pro-2026-04-23`;
  - reasoning effort: `xhigh`;
  - response id: `resp_0b52a9a0c6658cab006a410b4282b081a19778c01751af0e7d`;
  - uploaded bundle file id: `file-ERrPYPJY9xKmNLCMRavobZ`.

## 2026-06-28T14:02:21+02:00

- Added `Qab.Polynomials.Primitive` and imported it from `Qab.lean`.
- Defined:
  - `PosPair.Primitive`;
  - `qPrimCoeffZ`;
  - `qPrimZ`;
  - `qPrimQ`.
- Proved `qPrimCoeffZ` branch simp lemmas and `qPrimZ_coeff_zero`.
- Verified `cd Qab_Lean_v4 && lake build`.
- Polled OpenAI response
  `resp_0b52a9a0c6658cab006a410b4282b081a19778c01751af0e7d`; it failed
  because `.zip` is not a supported direct `input_file` context format.
- Updated `tools/ai_review/openai_review.py` to mount zip bundles in the
  code-interpreter container instead of attaching them as direct `input_file`
  items.
- Submitted corrected OpenAI background Responses review:
  - response id: `resp_06c8c1492ced2df4006a410d462c14819da27571b1bcd31b45`;
  - uploaded bundle file id: `file-XR6yWVmTkTJSgPh4GRWwKg`.

## 2026-06-28T14:09:24+02:00

- Extended `Qab.Polynomials.Primitive` with the initial support and endpoint
  facts from the phase-1 checklist:
  - top primitive coefficient `qPrimCoeffZ_top`;
  - coefficient vanishing above `A+B-2`;
  - `natDegree` upper bound and exact `natDegree`;
  - nonzero constant and top coefficients.
- Verified:
  - `cd Qab_Lean_v4 && lake build`;
  - `cd Qab_Lean_v4 && lake build Qab.Polynomials.Primitive`;
  - `cd Qab_Lean_v4 && lake build Qab.Packs.BroadAxioms`.
- Polled corrected OpenAI background response
  `resp_06c8c1492ced2df4006a410d462c14819da27571b1bcd31b45`; status was
  still `in_progress`.
- Attempted to read Claude background-agent logs for `0d872b98`; the local
  Claude daemon socket returned `ECONNREFUSED`, so the Claude review is not
  currently recoverable from this shell session.

## 2026-06-28T14:15:15+02:00

- OpenAI background response
  `resp_06c8c1492ced2df4006a410d462c14819da27571b1bcd31b45` completed.
- Added a concise review digest at
  `Qab_Lean_v4/docs/reviews/openai_phase1_review_20260628.md`.
- Acted on the main structural recommendation:
  - added `Qab.Pairs`;
  - moved `PosPair`, `PosPair.unequal`, `PosPair.sameUnordered`, and
    `PosPair.swap` out of `Qab.Basic`;
  - changed `Qab.Polynomials.Primitive` to import `Qab.Pairs` instead of
    `Qab.Basic`, avoiding a future cycle when concrete product sharing is
    wired into `Basic.lean`.
- Added `Qab.Polynomials.Orientation` with primitive reduction, `qOrientZ`,
  `qOrientQ`, `qPackageProdZ`, `qPackageProdQ`, `OrientationShare`, and
  `PackageProductShare`.
- Proved `qOrientZ_coeff_zero`.
- Added general coefficient lemmas `qPrimZ_coeff` and `qPrimQ_coeff`.
- Tested the review suggestion to remove `noncomputable` from `qPrimZ` and
  `qPrimQ`; Lean v4.31.0 rejected this because the current polynomial
  semiring/map API is noncomputable, so the annotations were restored.
- Verified:
  - `cd Qab_Lean_v4 && lake build`;
  - `cd Qab_Lean_v4 && lake build Qab.Packs.BroadAxioms`.

## 2026-06-28T14:29:57+02:00

- Extended `Qab.Pairs` with simp lemmas for `swap.a`, `swap.b`, and
  `swap.swap`.
- Extended `Qab.Polynomials.Primitive` with `qPrimZ_ne_zero` and
  `qPrimZ_leadingCoeff`.
- Extended `Qab.Polynomials.Orientation` with:
  - coefficient transport for exponents divisible by `gcd a b`;
  - coefficient vanishing for exponents not divisible by `gcd a b`;
  - nonzero, exact `natDegree`, leading coefficient, and top-coefficient facts
    for `qOrientZ`;
  - rational constant coefficient for `qOrientQ`;
  - nonzero, exact `natDegree`, leading coefficient, and swap invariance for
    `qPackageProdZ`;
  - swap invariance for `qPackageProdQ`.
- Verified:
  - `cd Qab_Lean_v4 && lake build`;
  - `cd Qab_Lean_v4 && lake build Qab.Packs.BroadAxioms`.

## 2026-06-28T14:32:30+02:00

- Submitted a focused OpenAI background request for proof guidance on the
  primitive closed-form identity:
  - response id: `resp_0a1c8e51b793fdee006a41142a9c88819cbd8c73ddcc56b622`;
  - uploaded bundle file id: `file-WCscFS1uwETcV57fUQEeuC`;
  - first poll status: `in_progress`.
- Added product-sharing predicate lemmas:
  - `PackageProductShare_comm`;
  - `PackageProductShare_swap_left`;
  - `PackageProductShare_swap_right`.
- Verified:
  - `cd Qab_Lean_v4 && lake build`;
  - `cd Qab_Lean_v4 && lake build Qab.Packs.BroadAxioms`.

## 2026-06-28T14:49:26+02:00

- Validated the repaired Claude review helper after the external Claude Code
  session rewrote `tools/ai_review/claude_review.py`.
- Added a small robustness patch before committing:
  - poll/cancel receipts now print `python3 tools/ai_review/claude_review.py`
    instead of the ambiguous bare script name;
  - `--poll` no longer reports a fresh running receipt as crashed merely
    because PID liveness is unreliable from this shell context.
- Verified:
  - `python3 -m py_compile tools/ai_review/claude_review.py`;
  - `python3 tools/ai_review/claude_review.py --dry-run --model haiku --effort low --task ...`;
  - synchronous `haiku`/`low` smoke review with captured output;
  - detached background `haiku`/`low` smoke review, including an immediate
    `running` poll and later `done` poll for receipt
    `artifacts/ai_reviews/20260628_144748_claude_receipt.json`.
- The helper now supports stdin prompts, self-managed background workers,
  `--poll`, `--cancel`, and review capture under `artifacts/ai_reviews/`.

## 2026-06-28T14:57:50+02:00

- Tightened the OpenAI review helper after the focused primitive-identity
  request returned `status: incomplete` with
  `incomplete_details.reason = "max_output_tokens"`.
- Removed the `max_output_tokens` request field from
  `tools/ai_review/openai_review.py`; substantive review calls are now
  uncapped by this helper.
- Made the web-search tool request `return_token_budget = "unlimited"` by
  default and documented this in `AGENTS.md` and `tools/ai_review/README.md`.
