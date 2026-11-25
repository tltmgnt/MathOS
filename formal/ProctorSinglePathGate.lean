/-! Single-path witness construction. The universal preservation premise
is open, not assumed as an established property of any heuristic.
This is a constructive logical equivalence, not a machine-cost theorem. -/
namespace ProctorSinglePathGate
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (update variables variable_mem)
open ProctorGeneralBranching (Satisfiable Covered restrict restrict_cover restriction_correct shannon)

abbrev Selector := Formula → Nat → Bool

def Preserves (pick : Selector) : Prop :=
  ∀ f v, Satisfiable f → Satisfiable (restrict v (pick f v) f)

def follow (pick : Selector) : List Nat → Formula → Assignment
  | [],_ => fun _ => false
  | v::vs,f => update (follow pick vs (restrict v (pick f v) f)) v (pick f v)

theorem empty_covered_model (f : Formula) (h : Covered [] f)
    (hs : Satisfiable f) (x : Assignment) : FormulaSat f x := by
  obtain ⟨y,hy⟩ := hs
  intro c hc
  obtain ⟨l,hl,_⟩ := hy c hc
  have hm := h c hc l hl
  cases hm

theorem follow_complete (pick : Selector) (hp : Preserves pick)
    (vs : List Nat) (f : Formula) (hc : Covered vs f) (hs : Satisfiable f) :
    FormulaSat f (follow pick vs f) := by
  induction vs generalizing f with
  | nil => exact empty_covered_model f hc hs _
  | cons v vs ih =>
    have hr := hp f v hs
    have hx := ih (restrict v (pick f v) f) (restrict_cover v (pick f v) vs f hc) hr
    exact (restriction_correct v (pick f v) f (follow pick vs (restrict v (pick f v) f))).1 hx

theorem check_iff (pick : Selector) (hp : Preserves pick)
    (vs : List Nat) (f : Formula) (hc : Covered vs f) :
    Satisfiable f ↔ FormulaSat f (follow pick vs f) :=
  ⟨follow_complete pick hp vs f hc,fun h => ⟨follow pick vs f,h⟩⟩

theorem preservation_iff (pick : Selector) :
    Preserves pick ↔
      ∀ vs f, Covered vs f → Satisfiable f → FormulaSat f (follow pick vs f) := by
  constructor
  · intro hp vs f hc hs
    exact follow_complete pick hp vs f hc hs
  · intro h f v hs
    have hc : Covered (v::variables f) f := by
      intro c hc l hl
      exact List.Mem.tail _ (variable_mem f c l hc hl)
    have hm := h (v::variables f) f hc hs
    change FormulaSat f (update (follow pick (variables f) (restrict v (pick f v) f)) v (pick f v)) at hm
    exact ⟨_,(restriction_correct v (pick f v) f _).2 hm⟩

def fromDecision (d : Formula → Bool) : Selector :=
  fun f v => if d (restrict v false f) then false else true

theorem decision_preserves (d : Formula → Bool)
    (hd : ∀ f, d f=true ↔ Satisfiable f) : Preserves (fromDecision d) := by
  intro f v hs
  unfold fromDecision
  cases he : d (restrict v false f) with
  | true =>
    change Satisfiable (restrict v false f)
    exact (hd _).1 he
  | false =>
    change Satisfiable (restrict v true f)
    cases (shannon v f).1 hs with
    | inl h =>
      have ht := (hd _).2 h
      rw [he] at ht
      cases ht
    | inr h => exact h

theorem failure_refutes_preservation (pick : Selector) (vs : List Nat)
    (f : Formula) (hc : Covered vs f) (hs : Satisfiable f)
    (bad : ¬ FormulaSat f (follow pick vs f)) : ¬ Preserves pick :=
  fun hp => bad (follow_complete pick hp vs f hc hs)

end ProctorSinglePathGate

#print axioms ProctorSinglePathGate.empty_covered_model
#print axioms ProctorSinglePathGate.follow_complete
#print axioms ProctorSinglePathGate.check_iff
#print axioms ProctorSinglePathGate.preservation_iff
#print axioms ProctorSinglePathGate.decision_preserves
#print axioms ProctorSinglePathGate.failure_refutes_preservation
