import Qab.Certificates.Interfaces

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

/-- Every point in the closed target interval `[lo, hi]` is covered. -/
def CoversClosedTarget (intervals : List CoverageInterval) (lo hi : Nat) : Prop :=
  ∀ x, lo ≤ x → x ≤ hi → CoversPoint intervals x

/-- Scan intervals from the next uncovered point through the closed endpoint
`hi`.  The list is expected to be ordered by left endpoint for completeness,
but soundness does not rely on an external sortedness proof. -/
def checkFrom (next hi : Nat) : List CoverageInterval → Bool
  | [] => hi < next
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

example : checkCoverage ([] : List CoverageInterval) 3 2 = true := by
  native_decide

example : checkCoverage singleton 4 4 = true := by
  native_decide

example : checkCoverage touching 0 5 = true := by
  native_decide

example : checkCoverage overlapping 0 5 = true := by
  native_decide

example : checkCoverage staleOverlap 0 4 = true := by
  native_decide

example : checkCoverage gap 0 4 = false := by
  native_decide

example : checkCoverage startsLate 0 2 = false := by
  native_decide

end Examples

end Coverage

export Coverage (CoversClosedTarget CoversPoint TargetWellFormed checkCoverage
  checkCoverage_sound checkFrom checkFrom_sound)

end Qab
