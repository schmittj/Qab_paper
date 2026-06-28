import Qab.Counterexample

namespace Qab

/-!
Collision theorem pack.

This pack is the only top-level bridge from package sharing to a normalized
counterexample.  It is intentionally narrow: it does not eliminate any branch
and it does not contain height, p-adic, or computational facts.

Eventually this pack should be opened by formalizing:
* the coefficient-defined primitive orientation polynomial;
* the full imprimitive orientation polynomial `Q_{a,b}(x)=g Q_{A,B}(x^g)`;
* the reciprocal package product and product-to-orientation sharing bridge;
* the collision dictionary for selected orientations;
* removal of the forced cyclotomic double roots;
* the no-three-equal-values lemma needed to choose compatible orientations;
* primitive normalization.
-/
structure CollisionPack where
  share_to_normCE :
    ∀ {P Q : PosPair},
      P.unequal → Q.unequal → ¬ P.sameUnordered Q →
      PackageShare P Q → ∃ ce : NormCE, FromShare P Q ce

end Qab
