/-! F034 candidate: nine selected front-end and checker resource
coordinates with exact byte-level result projection. Independent
reservations, not a single execution trace or full machine cost. -/
namespace ProctorEndToEndSelectedLedger
open ProctorHallDeficiency
open ProctorFrontendResourceLedger (Resources Below pairMeter pairBudget)
open ProctorUnifiedResourceLedger (checkerMeter checkerVisitBudget checkerGateBudget)

structure Ledger where
  accepted : Bool
  frontend : Resources
  lookupVisits : Nat
  comparisonGates : Nat

def meter (a b : List Nat) : Ledger :=
  let r := pairMeter a b
  match r.1.1,r.1.2 with
  | some (n,f),some e =>
    let c := checkerMeter n f e
    ⟨c.1,r.2,c.2.1,c.2.2⟩
  | _,_ => ⟨false,r.2,0,0⟩

set_option maxRecDepth 4096 in
theorem checker_projection (a b : List Nat) :
    ((meter a b).accepted,(meter a b).lookupVisits,(meter a b).comparisonGates)=
      ProctorUnifiedResourceLedger.bytesMeter a b := by
  unfold meter ProctorUnifiedResourceLedger.bytesMeter
  dsimp only
  rw [ProctorFrontendResourceLedger.pair_value a b]
  cases ProctorFuelFreeDecoder.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases ProctorFuelFreeDecoder.decodeEnvelope b <;> rfl

theorem frontend_projection (a b : List Nat) :
    (meter a b).frontend=(pairMeter a b).2 := by
  unfold meter
  dsimp only
  cases (pairMeter a b).1.1 with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases (pairMeter a b).1.2 <;> rfl

theorem bytes_value (a b : List Nat) :
    (meter a b).accepted=ProctorDataParser.checkBytes a b := by
  have h := congrArg Prod.fst (checker_projection a b)
  exact h.trans (ProctorUnifiedResourceLedger.bytes_value a b)

theorem bytes_sound (a b : List Nat) (h : (meter a b).accepted=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [bytes_value] at h
  exact ProctorDataParser.accepted_unsat a b h

theorem frontend_bounds (a b : List Nat) :
    Below (meter a b).frontend (pairBudget (a.length+b.length)) := by
  rw [frontend_projection]
  exact ProctorFrontendResourceLedger.pair_bounds a b

theorem checker_bounds (a b : List Nat) :
    (meter a b).lookupVisits≤ProctorUnifiedResourceLedger.bytesVisitBudget a b ∧
    (meter a b).comparisonGates≤ProctorUnifiedResourceLedger.bytesGateBudget a b := by
  have h := checker_projection a b
  have hv := congrArg (fun r : Bool × Nat × Nat => r.2.1) h
  have hg := congrArg (fun r : Bool × Nat × Nat => r.2.2) h
  change (meter a b).lookupVisits=(ProctorUnifiedResourceLedger.bytesMeter a b).2.1 at hv
  change (meter a b).comparisonGates=(ProctorUnifiedResourceLedger.bytesMeter a b).2.2 at hg
  rw [hv,hg]
  exact ProctorUnifiedResourceLedger.bytes_bounds a b

theorem resource_bounds (a b : List Nat) :
    Below (meter a b).frontend (pairBudget (a.length+b.length)) ∧
    (meter a b).lookupVisits≤ProctorUnifiedResourceLedger.bytesVisitBudget a b ∧
    (meter a b).comparisonGates≤ProctorUnifiedResourceLedger.bytesGateBudget a b :=
  ⟨frontend_bounds a b,checker_bounds a b⟩

-- A failed decoder reserves no checker resources; the front-end
-- reservation is retained, including work on rejected inputs.
theorem rejected_expected (a b : List Nat)
    (h : ProctorFuelFreeDecoder.decodeExpected a=none) :
    (meter a b).accepted=false ∧ (meter a b).lookupVisits=0 ∧
      (meter a b).comparisonGates=0 := by
  have e := checker_projection a b
  unfold ProctorUnifiedResourceLedger.bytesMeter at e
  rw [h] at e
  exact ⟨congrArg Prod.fst e,congrArg (fun r : Bool × Nat × Nat => r.2.1) e,
    congrArg (fun r : Bool × Nat × Nat => r.2.2) e⟩

end ProctorEndToEndSelectedLedger

#print axioms ProctorEndToEndSelectedLedger.checker_projection
#print axioms ProctorEndToEndSelectedLedger.frontend_projection
#print axioms ProctorEndToEndSelectedLedger.bytes_value
#print axioms ProctorEndToEndSelectedLedger.bytes_sound
#print axioms ProctorEndToEndSelectedLedger.frontend_bounds
#print axioms ProctorEndToEndSelectedLedger.checker_bounds
#print axioms ProctorEndToEndSelectedLedger.resource_bounds
#print axioms ProctorEndToEndSelectedLedger.rejected_expected
