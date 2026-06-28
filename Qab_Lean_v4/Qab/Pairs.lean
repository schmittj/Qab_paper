namespace Qab

/-!
Pair-level package objects.

These definitions are kept below `Qab.Basic` in the import graph so the
polynomial layer can use positive pairs without depending on the temporary
opaque `PackageShare` predicate.
-/

/-- A positive ordered pair `(a,b)`.  The mathematical package also contains
both reciprocal orientations, so unordered equality is tracked separately. -/
structure PosPair where
  a : Nat
  b : Nat
  ha_pos : 0 < a
  hb_pos : 0 < b

namespace PosPair

/-- The nontrivial package condition used in the theorem statement. -/
def unequal (P : PosPair) : Prop := P.a ≠ P.b

/-- Equality after allowing the reciprocal swap. -/
def sameUnordered (P Q : PosPair) : Prop :=
  (P.a = Q.a ∧ P.b = Q.b) ∨ (P.a = Q.b ∧ P.b = Q.a)

/-- Swapped orientation helper. -/
def swap (P : PosPair) : PosPair where
  a := P.b
  b := P.a
  ha_pos := P.hb_pos
  hb_pos := P.ha_pos

@[simp]
theorem swap_a (P : PosPair) : P.swap.a = P.b := rfl

@[simp]
theorem swap_b (P : PosPair) : P.swap.b = P.a := rfl

@[simp]
theorem swap_swap (P : PosPair) : P.swap.swap = P := by
  cases P
  rfl

end PosPair

end Qab
