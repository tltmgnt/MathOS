import F038Formal.Bridge

/-! FV-05: scoped resource model for D7I projection and its certificate.
    The hypotheses are per-execution graph/count invariants, not a verified
    operational semantics of the JavaScript engine. -/
namespace MathOS.F038.Resources

structure Counts where
  starts : Nat
  edgeScans : Nat
  pairTests : Nat
  pathSteps : Nat
  emitted : Nat
  peakQueue : Nat
  peakPredecessors : Nat

def work (c : Counts) : Nat := c.edgeScans + c.pairTests + c.pathSteps

def bound (v e : Nat) : Nat := v * e + v * v + v * v * v

structure ValidCounts (v e : Nat) (c : Counts) : Prop where
  starts : c.starts ≤ v
  scans : c.edgeScans ≤ c.starts * e
  pairs : c.pairTests ≤ c.starts * v
  steps : c.pathSteps ≤ c.pairTests * v
  paths : c.emitted ≤ c.pairTests
  queue : c.peakQueue ≤ v
  predecessors : c.peakPredecessors ≤ v

theorem scans_bound {v e : Nat} {c : Counts} (h : ValidCounts v e c) :
    c.edgeScans ≤ v * e :=
  h.scans.trans (Nat.mul_le_mul_right e h.starts)

theorem pairs_bound {v e : Nat} {c : Counts} (h : ValidCounts v e c) :
    c.pairTests ≤ v * v :=
  h.pairs.trans (Nat.mul_le_mul_right v h.starts)

theorem steps_bound {v e : Nat} {c : Counts} (h : ValidCounts v e c) :
    c.pathSteps ≤ v * v * v :=
  h.steps.trans (Nat.mul_le_mul_right v (pairs_bound h))

theorem charged_work_bound {v e : Nat} {c : Counts} (h : ValidCounts v e c) :
    work c ≤ bound v e := by
  unfold work bound
  exact Nat.add_le_add (Nat.add_le_add (scans_bound h) (pairs_bound h)) (steps_bound h)

theorem path_count_bound {v e : Nat} {c : Counts} (h : ValidCounts v e c) :
    c.emitted ≤ v * v :=
  h.paths.trans (pairs_bound h)

-- A simple path stores distinct literal vertices. This proves the cardinality
-- premise for an individually validated path over v vertex IDs.
theorem simple_path_vertices {v : Nat} (xs : List (Fin v)) (h : xs.Nodup) :
    xs.length ≤ v := by
  classical
  have hc : xs.toFinset.card = xs.length := List.toFinset_card_of_nodup h
  rw [← hc]
  simpa using (Finset.card_le_univ xs.toFinset)

-- Prefix of the actual budget discipline: a successful charge costs one unit.
-- A failed charge leaves the counter unchanged and returns no successful result.
def charge (limit used : Nat) : Option Nat :=
  if used < limit then some (used + 1) else none

theorem charge_safe (limit used next : Nat) (h : charge limit used = some next) :
    next ≤ limit ∧ next = used + 1 := by
  by_cases ht : used < limit
  · have he : used + 1 = next := by simpa [charge, ht] using h
    omega
  · simp [charge, ht] at h

theorem charge_cutoff (limit used : Nat) (h : used ≤ limit)
    (stop : charge limit used = none) : used = limit := by
  by_cases ht : used < limit
  · simp [charge, ht] at stop
  · omega

-- Logical word model: two header counts, retained factor IDs, three
-- words per path, three words per edge. No object or JSON overhead included.
def payloadWords (retained paths edges : Nat) : Nat :=
  2 + retained + 3 * paths + 3 * edges

def payloadBits (width retained paths edges : Nat) : Nat :=
  width * payloadWords retained paths edges

theorem payload_word_bound {v e f retained edges : Nat} {c : Counts}
    (h : ValidCounts v e c) (hr : retained ≤ f) (he : edges ≤ c.pathSteps) :
    payloadWords retained c.emitted edges ≤ 2 + f + 3 * (v*v) + 3 * (v*v*v) := by
  unfold payloadWords
  have hp := Nat.mul_le_mul_left 3 (path_count_bound h)
  have hs := Nat.mul_le_mul_left 3 (he.trans (steps_bound h))
  omega

theorem payload_bit_bound {v e f retained edges width : Nat} {c : Counts}
    (h : ValidCounts v e c) (hr : retained ≤ f) (he : edges ≤ c.pathSteps) :
    payloadBits width retained c.emitted edges ≤
      width * (2 + f + 3 * (v*v) + 3 * (v*v*v)) :=
  Nat.mul_le_mul_left width (payload_word_bound h hr he)

-- Bounded-arity input has at most four forbidden rows per binary factor,
-- each contributing at most two directed edges. Deduplication only shrinks it.
theorem coordinate_work_bound {k f e : Nat} {c : Counts}
    (h : ValidCounts (2*k) e c) (he : e ≤ 8*f) :
    work c ≤ (2*k)*(8*f) + (2*k)*(2*k) + (2*k)*(2*k)*(2*k) := by
  apply (charged_work_bound h).trans
  unfold bound
  have hs := Nat.mul_le_mul_left (2*k) he
  omega

-- Structural reference checker accounting. These are counted opportunities
-- for comparisons, not CPU instructions, proof elaboration, or bit costs.
def checkerBound (options conflicts : Nat) : Nat := options * options * conflicts

theorem checker_comparison_bound (options conflicts pairs probes : Nat)
    (hp : pairs ≤ options * options) (hc : probes ≤ pairs * conflicts) :
    probes ≤ checkerBound options conflicts :=
  hc.trans (Nat.mul_le_mul_right conflicts hp)

-- Executable validation of an instrumented count summary. The theorem
-- validates the arithmetic obligations, not the truth of a reported trace.
def countsCheck (v e : Nat) (c : Counts) : Bool :=
  decide (c.starts ≤ v ∧ c.edgeScans ≤ c.starts * e ∧
    c.pairTests ≤ c.starts * v ∧ c.pathSteps ≤ c.pairTests * v ∧
    c.emitted ≤ c.pairTests ∧ c.peakQueue ≤ v ∧ c.peakPredecessors ≤ v)

theorem countsCheck_sound {v e : Nat} {c : Counts}
    (h : countsCheck v e c = true) : ValidCounts v e c := by
  have hc : c.starts ≤ v ∧ c.edgeScans ≤ c.starts * e ∧
      c.pairTests ≤ c.starts * v ∧ c.pathSteps ≤ c.pairTests * v ∧
      c.emitted ≤ c.pairTests ∧ c.peakQueue ≤ v ∧ c.peakPredecessors ≤ v :=
    of_decide_eq_true h
  rcases hc with ⟨a,b,d,f,g,i,j⟩
  exact ⟨a,b,d,f,g,i,j⟩

theorem checked_work_bound {v e : Nat} {c : Counts}
    (h : countsCheck v e c = true) : work c ≤ bound v e :=
  charged_work_bound (countsCheck_sound h)

-- An explicit abstract array representation: adjacency triples + dense
-- offsets, option list, queue, predecessor triples, current path scratch
-- and saved certificate. Excludes original factors and projected tables.
def liveWords (v e retained edges : Nat) (c : Counts) : Nat :=
  3*e + (v+1) + v + c.peakQueue + 3*c.peakPredecessors +
    3*v + payloadWords retained c.emitted edges

theorem live_word_bound {v e f retained edges : Nat} {c : Counts}
    (h : ValidCounts v e c) (hr : retained ≤ f) (he : edges ≤ c.pathSteps) :
    liveWords v e retained edges c ≤
      3*e + 9*v + 1 + (2 + f + 3*(v*v) + 3*(v*v*v)) := by
  unfold liveWords
  have hp := Nat.mul_le_mul_left 3 h.predecessors
  have hq := h.queue
  have hb := payload_word_bound h hr he
  omega

theorem projected_factor_bound {v e f retained : Nat} {c : Counts}
    (h : ValidCounts v e c) (hr : retained ≤ f) :
    retained + c.emitted ≤ f + v*v :=
  Nat.add_le_add hr (path_count_bound h)

#print axioms countsCheck_sound
#print axioms checked_work_bound
#print axioms live_word_bound
#print axioms projected_factor_bound
#print axioms charged_work_bound
#print axioms simple_path_vertices
#print axioms charge_safe
#print axioms charge_cutoff
#print axioms payload_bit_bound
#print axioms coordinate_work_bound
#print axioms checker_comparison_bound

end MathOS.F038.Resources
