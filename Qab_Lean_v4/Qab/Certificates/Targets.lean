namespace Qab

/-!
Certificate targets that are shared by schematic interfaces and concrete
checkers.

This file intentionally has no theorem-pack or certificate-checking axioms.
-/

/-- Which polynomial family a terminal modular-gcd certificate is checking. -/
inductive PolynomialCheckTarget where
  /-- Undivided collision trinomials `H_{m,n}`.  Forced cyclotomic factors must
  be accounted for explicitly, especially the double root at `x = 1`. -/
  | collisionH
  /-- Divided orientation/package polynomial `Q_{a,b}`. -/
  | orientationQ
  /-- Reciprocal package product `Q_{a,b} * Q_{b,a}`. -/
  | packageProduct
  deriving DecidableEq, Repr

end Qab
