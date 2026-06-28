import Qab.CoreProof

namespace Qab

/-!
Temporary broad axioms.

This file is intentionally separate.  Importing it turns the conditional core
into an axiom-dependent theorem.  Do not move these axioms into the core files.

Soundness guardrails:
* `FromShare` must stay opaque here; never define it as `True`.
* No dummy `FromShare` proofs should be axiomatized.
* Replacement work should proceed by deleting one axiom at a time and proving
  the corresponding pack value from narrower theorem packs or certificates.
-/

axiom broad_collision_pack : CollisionPack
axiom broad_global_height_pack : GlobalHeightPack
axiom broad_upper_normalization_pack : UpperNormalizationPack
axiom broad_upper_range_pack : UpperRangePack
axiom broad_local_packet_pack : LocalPacketPack
axiom broad_finite_lower_pack : FiniteLowerPack
axiom broad_finite_residual_pack : FiniteResidualPack

/-- Axiom-dependent top-level theorem, useful only as a smoke test. -/
theorem package_coprimality_with_broad_axioms : ReciprocalPackageCoprimality :=
  package_coprimality_from_packs
    broad_collision_pack
    broad_global_height_pack
    broad_upper_normalization_pack
    broad_upper_range_pack
    broad_local_packet_pack
    broad_finite_lower_pack
    broad_finite_residual_pack

end Qab
