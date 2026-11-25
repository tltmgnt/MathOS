/-! A checked counterexample to extending the width-two conflict
criterion to unrestricted CNF. This is not a lower bound against SAT
algorithms or against resolution; it identifies a specific missing
generality premise. -/
namespace ProctorWidthThreeBarrier
open ProctorHallDeficiency
open ProctorResolutionBridge (Unsat)
open ProctorImplicationPathDiscovery (arcs candidate)
open ProctorTwoCNFModel (NoConflict findConflict noConflict_of_none)
open ProctorOrdinaryCompleteness (variables)
open ProctorUnifiedReplay (validFormula)
open ProctorTotalTwoCNF (supported solve)
open ProctorExecutableReplay (hasEmpty)

def cube : Formula :=
  [[(1,false),(2,false),(3,false)],
   [(1,false),(2,false),(3,true)],
   [(1,false),(2,true),(3,false)],
   [(1,false),(2,true),(3,true)],
   [(1,true),(2,false),(3,false)],
   [(1,true),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],
   [(1,true),(2,true),(3,true)]]

def single : Formula := [[(1,true),(2,true),(3,true)]]

theorem cube_row (a b c : Bool) : [(1,a),(2,b),(3,c)]∈cube := by
  cases a <;> cases b <;> cases c
  · exact List.Mem.head _
  · exact List.Mem.tail _ (List.Mem.head _)
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _))
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _)))
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _))))
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _)))))
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _))))))
  · exact List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _)))))))

theorem cube_unsat : Unsat cube := by
  intro h
  obtain ⟨x,hx⟩ := h
  have hc := hx _ (cube_row (!(x 1)) (!(x 2)) (!(x 3)))
  obtain ⟨l,hl,he⟩ := hc
  cases hl with
  | head =>
    change x 1= !(x 1) at he
    cases e : x 1 <;> rw [e] at he <;> cases he
  | tail _ hm =>
    cases hm with
    | head =>
      change x 2= !(x 2) at he
      cases e : x 2 <;> rw [e] at he <;> cases he
    | tail _ ht =>
      cases ht with
      | head =>
        change x 3= !(x 3) at he
        cases e : x 3 <;> rw [e] at he <;> cases he
      | tail _ hz => cases hz

theorem single_sat : ∃ x, FormulaSat single x := by
  refine ⟨fun _ => true,?_⟩
  intro c hc
  cases hc with
  | head => exact ⟨(1,true),List.Mem.head _,rfl⟩
  | tail _ hm => cases hm

theorem cube_valid : validFormula 3 cube=true := by decide
theorem single_valid : validFormula 3 single=true := by decide

theorem cube_width_three : ∀ c∈cube, c.length=3 := by
  intro c hc
  unfold cube at hc
  cases hc with
  | head => rfl
  | tail _ h =>
    cases h with
    | head => rfl
    | tail _ h =>
      cases h with
      | head => rfl
      | tail _ h =>
        cases h with
        | head => rfl
        | tail _ h =>
          cases h with
          | head => rfl
          | tail _ h =>
            cases h with
            | head => rfl
            | tail _ h =>
              cases h with
              | head => rfl
              | tail _ h =>
                cases h with
                | head => rfl
                | tail _ h => cases h

theorem same_graph : arcs cube=arcs single := rfl
theorem cube_no_empty : hasEmpty cube=false := rfl
theorem cube_no_conflict : findConflict cube (variables cube)=none := by decide
theorem cube_no_conflict_semantic : NoConflict cube :=
  noConflict_of_none cube cube_no_conflict
theorem cube_candidate_none : candidate cube=none := rfl
theorem cube_unsupported : solve 3 cube=.unsupported := rfl

-- No Boolean function of this extracted graph alone can decide
-- satisfiability for both inputs, even with the same declared bound.
theorem graph_only_impossible (d : List ProctorImplicationPathDiscovery.Arc → Bool)
    (hu : d (arcs cube)=false) (hs : d (arcs single)=true) : False := by
  rw [same_graph] at hu
  exact Bool.noConfusion (hu.symm.trans hs)

theorem width_hypothesis_essential :
    ∃ f : Formula, validFormula 3 f=true ∧ NoConflict f ∧ Unsat f :=
  ⟨cube,cube_valid,cube_no_conflict_semantic,cube_unsat⟩

end ProctorWidthThreeBarrier

#print axioms ProctorWidthThreeBarrier.cube_row
#print axioms ProctorWidthThreeBarrier.cube_unsat
#print axioms ProctorWidthThreeBarrier.single_sat
#print axioms ProctorWidthThreeBarrier.cube_valid
#print axioms ProctorWidthThreeBarrier.single_valid
#print axioms ProctorWidthThreeBarrier.cube_width_three
#print axioms ProctorWidthThreeBarrier.same_graph
#print axioms ProctorWidthThreeBarrier.cube_no_empty
#print axioms ProctorWidthThreeBarrier.cube_no_conflict
#print axioms ProctorWidthThreeBarrier.cube_no_conflict_semantic
#print axioms ProctorWidthThreeBarrier.cube_candidate_none
#print axioms ProctorWidthThreeBarrier.cube_unsupported
#print axioms ProctorWidthThreeBarrier.graph_only_impossible
#print axioms ProctorWidthThreeBarrier.width_hypothesis_essential
