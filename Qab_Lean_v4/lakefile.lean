import Lake
open Lake DSL

package «qab» where
  -- Conditional formalization scaffold for the Q_{a,b} package-coprimality proof.
  -- Keep this project small and pack-parametric until theorem packs are opened.

require mathlib from
  "/home" / "jo314" / "lean" / "mathlib4-central"

@[default_target]
lean_lib «Qab» where
