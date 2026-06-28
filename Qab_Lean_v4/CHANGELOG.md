# Qab Lean Changelog

## 2026-06-28

- Created a central reusable Mathlib checkout at `/home/jo314/lean/mathlib4-central`.
- Pinned the scaffold to `leanprover/lean4:v4.31.0` and local Mathlib commit
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (`v4.31.0`).
- Replaced the GitHub Mathlib dependency with the central local path so this
  repository does not clone its own Mathlib copy.
- Adjusted Lean declarations for `v4.31.0`: replaced old `constant`
  declarations by `axiom` declarations for opaque predicates and expanded
  grouped structure fields used by dependent later fields.
- Verified `lake build` and `lake build Qab.Packs.BroadAxioms`.
- Added `Qab.Polynomials.Primitive` with the primitive-pair predicate,
  primitive coefficient function, `qPrimZ`, `qPrimQ`, and the constant
  coefficient lemma for `qPrimZ`.
