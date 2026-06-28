import Mathlib.Tactic
import Qab.Certificates.CoverageTypes

namespace Qab

/-!
# Decidable coverage certificates for finite searches

The endpoint convention is closed: `CoverageInterval` covers the natural
numbers `x` satisfying `lo ≤ x ∧ x ≤ hi`.

The checker below is intentionally small and pure.  It scans a list of
intervals from left to right while carrying the next target point that has not
yet been covered.  Fully stale intervals are skipped, a listed interval whose
left endpoint is beyond the next target point is a gap, and an interval covering
the next target point advances the scan to one past its right endpoint.
-/

namespace CoverageInterval

/-- Closed-interval membership for a coverage interval. -/
def Contains (I : CoverageInterval) (x : Nat) : Prop :=
  I.lo ≤ x ∧ x ≤ I.hi

/-- A nonempty closed interval.  The checker does not assume this separately. -/
def WellFormed (I : CoverageInterval) : Prop :=
  I.lo ≤ I.hi

end CoverageInterval

namespace Coverage

/-- A target interval is nonempty when its closed endpoints are ordered. -/
def TargetWellFormed (lo hi : Nat) : Prop :=
  lo ≤ hi

/-- The point `x` is covered by some interval in `intervals`. -/
def CoversPoint (intervals : List CoverageInterval) (x : Nat) : Prop :=
  ∃ I, I ∈ intervals ∧ I.Contains x

/-- The point `x` is covered by the interval projected from some typed row. -/
def CoversMappedPoint {α : Type} (rows : List α)
    (toInterval : α → CoverageInterval) (x : Nat) : Prop :=
  ∃ row, row ∈ rows ∧ (toInterval row).Contains x

/-- Every point in the closed target interval `[lo, hi]` is covered. -/
def CoversClosedTarget (intervals : List CoverageInterval) (lo hi : Nat) : Prop :=
  ∀ x, lo ≤ x → x ≤ hi → CoversPoint intervals x

/-- Scan intervals from the next uncovered point through the closed endpoint
`hi`.  The list is expected to be ordered by left endpoint for completeness,
but soundness does not rely on an external sortedness proof. -/
def checkFrom (next hi : Nat) : List CoverageInterval → Bool
  | [] => decide (hi < next)
  | I :: rest =>
      if hi < next then
        true
      else if I.hi < next then
        checkFrom next hi rest
      else if next < I.lo then
        false
      else
        checkFrom (I.hi + 1) hi rest

/-- Check that `intervals` cover the closed target interval `[lo, hi]`.  If
`lo > hi`, the target is empty and the checker succeeds. -/
def checkCoverage (intervals : List CoverageInterval) (lo hi : Nat) : Bool :=
  checkFrom lo hi intervals

/-- Process a list of intervals and return the next point that remains
uncovered, or `none` if a gap is found before the target endpoint.  This is a
resumable version of `checkFrom` for generated chunk certificates. -/
def advanceFrom (next hi : Nat) : List CoverageInterval → Option Nat
  | [] => some next
  | I :: rest =>
      if hi < next then
        some next
      else if I.hi < next then
        advanceFrom next hi rest
      else if next < I.lo then
        none
      else
        advanceFrom (I.hi + 1) hi rest

/-- Boolean checker induced by the resumable `advanceFrom` scan. -/
def checkFromViaAdvance (next hi : Nat) (intervals : List CoverageInterval) : Bool :=
  match advanceFrom next hi intervals with
  | some next' => decide (hi < next')
  | none => false

/-- Public coverage checker induced by the resumable `advanceFrom` scan. -/
def checkCoverageViaAdvance (intervals : List CoverageInterval) (lo hi : Nat) : Bool :=
  checkFromViaAdvance lo hi intervals

theorem advanceFrom_append {xs ys : List CoverageInterval} {next hi : Nat} :
    advanceFrom next hi (xs ++ ys) =
      match advanceFrom next hi xs with
      | none => none
      | some next' => advanceFrom next' hi ys := by
  induction xs generalizing next with
  | nil =>
      simp [advanceFrom]
  | cons I rest ih =>
      by_cases hDone : hi < next
      · have hYs : advanceFrom next hi ys = some next := by
          cases ys <;> simp [advanceFrom, hDone]
        simp [advanceFrom, hDone, hYs]
      · by_cases hStale : I.hi < next
        · simp [advanceFrom, hDone, hStale, ih]
        · by_cases hGap : next < I.lo
          · simp [advanceFrom, hDone, hStale, hGap]
          · simp [advanceFrom, hDone, hStale, hGap, ih]

theorem checkFrom_eq_checkFromViaAdvance {intervals : List CoverageInterval}
    {next hi : Nat} :
    checkFrom next hi intervals = checkFromViaAdvance next hi intervals := by
  induction intervals generalizing next with
  | nil =>
      simp [checkFrom, checkFromViaAdvance, advanceFrom]
  | cons I rest ih =>
      by_cases hDone : hi < next
      · simp [checkFrom, checkFromViaAdvance, advanceFrom, hDone]
      · by_cases hStale : I.hi < next
        · simp [checkFrom, checkFromViaAdvance, advanceFrom, hDone, hStale, ih]
        · by_cases hGap : next < I.lo
          · simp [checkFrom, checkFromViaAdvance, advanceFrom, hDone, hStale, hGap]
          · simp [checkFrom, checkFromViaAdvance, advanceFrom, hDone, hStale, hGap, ih]

theorem checkCoverage_eq_checkCoverageViaAdvance {intervals : List CoverageInterval}
    {lo hi : Nat} :
    checkCoverage intervals lo hi = checkCoverageViaAdvance intervals lo hi := by
  simpa [checkCoverage, checkCoverageViaAdvance] using
    (checkFrom_eq_checkFromViaAdvance (intervals := intervals) (next := lo) (hi := hi))

theorem checkFrom_sound {intervals : List CoverageInterval} {next hi : Nat} :
    checkFrom next hi intervals = true →
      ∀ x, next ≤ x → x ≤ hi → CoversPoint intervals x := by
  induction intervals generalizing next with
  | nil =>
      intro h x hxNext hxHi
      simp [checkFrom] at h
      omega
  | cons I rest ih =>
      intro h x hxNext hxHi
      by_cases hDone : hi < next
      · omega
      · by_cases hStale : I.hi < next
        · have hRest : checkFrom next hi rest = true := by
            simpa [checkFrom, hDone, hStale] using h
          rcases ih hRest x hxNext hxHi with ⟨J, hJMem, hJContains⟩
          exact ⟨J, by simp [hJMem], hJContains⟩
        · by_cases hGap : next < I.lo
          · simp [checkFrom, hDone, hStale, hGap] at h
          · have hRest : checkFrom (I.hi + 1) hi rest = true := by
              simpa [checkFrom, hDone, hStale, hGap] using h
            by_cases hxI : x ≤ I.hi
            · have hLo : I.lo ≤ x := by
                have hLoNext : I.lo ≤ next := Nat.le_of_not_gt hGap
                exact le_trans hLoNext hxNext
              exact ⟨I, by simp, hLo, hxI⟩
            · have hxAfterI : I.hi + 1 ≤ x :=
                Nat.succ_le_of_lt (Nat.lt_of_not_ge hxI)
              rcases ih hRest x hxAfterI hxHi with ⟨J, hJMem, hJContains⟩
              exact ⟨J, by simp [hJMem], hJContains⟩

/-- Soundness of the public checker: a successful run covers every point in
the closed target interval. -/
theorem checkCoverage_sound {intervals : List CoverageInterval} {lo hi : Nat} :
    checkCoverage intervals lo hi = true →
      CoversClosedTarget intervals lo hi := by
  intro h
  exact checkFrom_sound h

/-- Soundness of the resumable-checker public wrapper. -/
theorem checkCoverageViaAdvance_sound {intervals : List CoverageInterval} {lo hi : Nat} :
    checkCoverageViaAdvance intervals lo hi = true →
      CoversClosedTarget intervals lo hi := by
  intro h
  exact checkCoverage_sound (by
    simpa [checkCoverage_eq_checkCoverageViaAdvance] using h)

/-- Soundness for typed rows carrying an interval projection.  This is the
bridge future residual-row certificates need: coverage of `rows.map toInterval`
recovers a row, not just a bare interval. -/
theorem checkCoverage_map_sound {α : Type} {rows : List α}
    {toInterval : α → CoverageInterval} {lo hi : Nat} :
    checkCoverage (rows.map toInterval) lo hi = true →
      ∀ x, lo ≤ x → x ≤ hi → CoversMappedPoint rows toInterval x := by
  intro h x hxLo hxHi
  rcases checkCoverage_sound h x hxLo hxHi with ⟨I, hIMem, hIContains⟩
  rcases List.mem_map.mp hIMem with ⟨row, hRowMem, hRowInterval⟩
  exact ⟨row, hRowMem, by simpa [hRowInterval] using hIContains⟩

/-- Eliminate every point in a checked target interval from local facts on each
listed coverage interval. -/
theorem checkCoverage_elim {P : Nat → Prop}
    {intervals : List CoverageInterval} {lo hi : Nat} :
    checkCoverage intervals lo hi = true →
      (∀ I, I ∈ intervals → ∀ x, I.Contains x → P x) →
      ∀ x, lo ≤ x → x ≤ hi → P x := by
  intro hCoverage hLocal x hxLo hxHi
  rcases checkCoverage_sound hCoverage x hxLo hxHi with ⟨I, hIMem, hIContains⟩
  exact hLocal I hIMem x hIContains

theorem coversPoint_append_left {xs ys : List CoverageInterval} {x : Nat} :
    CoversPoint xs x → CoversPoint (xs ++ ys) x := by
  rintro ⟨I, hIMem, hIContains⟩
  exact ⟨I, List.mem_append_left ys hIMem, hIContains⟩

theorem coversPoint_append_right {xs ys : List CoverageInterval} {x : Nat} :
    CoversPoint ys x → CoversPoint (xs ++ ys) x := by
  rintro ⟨I, hIMem, hIContains⟩
  exact ⟨I, List.mem_append_right xs hIMem, hIContains⟩

/-- Stitch two already-covered adjacent closed target intervals. -/
theorem coversClosedTarget_append {xs ys : List CoverageInterval} {lo mid hi : Nat} :
    CoversClosedTarget xs lo mid →
      CoversClosedTarget ys (mid + 1) hi →
      CoversClosedTarget (xs ++ ys) lo hi := by
  intro hLeft hRight x hxLo hxHi
  by_cases hxMid : x ≤ mid
  · exact coversPoint_append_left (ys := ys) (hLeft x hxLo hxMid)
  · have hxRightLo : mid + 1 ≤ x :=
      Nat.succ_le_of_lt (Nat.lt_of_not_ge hxMid)
    exact coversPoint_append_right (xs := xs) (hRight x hxRightLo hxHi)

section Examples

private def singleton : List CoverageInterval :=
  [{ lo := 4, hi := 4 }]

private def touching : List CoverageInterval :=
  [{ lo := 0, hi := 2 }, { lo := 3, hi := 5 }]

private def overlapping : List CoverageInterval :=
  [{ lo := 0, hi := 3 }, { lo := 2, hi := 5 }]

private def staleOverlap : List CoverageInterval :=
  [{ lo := 0, hi := 3 }, { lo := 1, hi := 2 }, { lo := 4, hi := 4 }]

private def gap : List CoverageInterval :=
  [{ lo := 0, hi := 1 }, { lo := 3, hi := 4 }]

private def startsLate : List CoverageInterval :=
  [{ lo := 1, hi := 2 }]

private def emptyInside : List CoverageInterval :=
  [{ lo := 0, hi := 2 }, { lo := 5, hi := 2 }, { lo := 3, hi := 5 }]

private def unsortedCover : List CoverageInterval :=
  [{ lo := 2, hi := 3 }, { lo := 0, hi := 1 }]

example : checkCoverage ([] : List CoverageInterval) 3 2 = true := by
  decide

example : checkCoverage ([] : List CoverageInterval) 0 0 = false := by
  decide

example : checkCoverage singleton 4 4 = true := by
  decide

example : checkCoverage [{ lo := 0, hi := 10 }] 3 5 = true := by
  decide

example : checkCoverage touching 0 5 = true := by
  decide

example : checkCoverage overlapping 0 5 = true := by
  decide

example : checkCoverage staleOverlap 0 4 = true := by
  decide

example : checkCoverage emptyInside 0 5 = true := by
  decide

example : checkCoverage gap 0 4 = false := by
  decide

example : checkCoverage startsLate 0 2 = false := by
  decide

example : checkCoverage [{ lo := 0, hi := 2 }] 0 3 = false := by
  decide

example : checkCoverage unsortedCover 0 3 = false := by
  decide

example : advanceFrom 0 5 touching = some 6 := by
  decide

example :
    advanceFrom 0 5 (touching ++ [{ lo := 6, hi := 7 }]) = some 6 := by
  decide

end Examples

end Coverage

export Coverage (CoversClosedTarget CoversPoint TargetWellFormed checkCoverage
  checkCoverage_sound checkFrom checkFrom_sound CoversMappedPoint
  checkCoverage_map_sound checkCoverage_elim advanceFrom advanceFrom_append
  checkFromViaAdvance checkCoverageViaAdvance checkCoverageViaAdvance_sound
  coversClosedTarget_append)

end Qab
