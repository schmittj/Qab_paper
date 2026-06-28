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
