namespace Qab

/-!
Leaf coverage-certificate datatypes.

This module intentionally has no project imports.  Pure coverage checkers can
depend on these datatypes without pulling in theorem packs, polynomial code, or
schematic certificate axioms.
-/

/-- A closed natural-number interval used by generated coverage certificates. -/
structure CoverageInterval where
  lo : Nat
  hi : Nat
  deriving DecidableEq, Repr

end Qab
