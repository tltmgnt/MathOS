/-! F035: total typed 2-CNF interface, including empty clauses.
The invalid and unsupported cases are not labeled SAT. Successful
UNSAT results retain the original-input-bound certificate checker.
Resource bounds count inference steps, not serialized bit operations. -/
namespace ProctorTotalTwoCNF
open ProctorHallDeficiency
open ProctorExecutableReplay (hasEmpty)
open ProctorUnifiedReplay (Proof validFormula boundCheck)
open ProctorOrdinaryCompleteness (variables empty_complete)
open ProctorResolutionBridge (Unsat)
open ProctorTwoCNFModel (TwoCNF model findConflict noConflict_of_none model_satisfies conflict_routes findConflict_some)
open ProctorPathResourceBounds (occurrences steps tryVar_size)
open ProctorImplicationPathDiscovery (tryVar arcs)
open ProctorBinarySquareDiscovery (checked checked_sound)
open ProctorPathCompilerCompleteness (checked_tryVar_complete)

def rowWidth : Clause → Bool
  | [] => true
  | [_] => true
  | [_,_] => true
  | _ => false

def supported : Formula → Bool
  | [] => true
  | c::cs => rowWidth c && supported cs

def WidthTwo (f : Formula) : Prop :=
  ∀ c∈f, c.length≤2

theorem rowWidth_iff (c : Clause) : rowWidth c=true ↔ c.length≤2 := by
  cases c with
  | nil => exact ⟨fun _ => Nat.zero_le _,fun _ => rfl⟩
  | cons a cs =>
    cases cs with
    | nil => exact ⟨fun _ => Nat.le_succ _,fun _ => rfl⟩
    | cons b bs =>
      cases bs with
      | nil => exact ⟨fun _ => Nat.le_refl _,fun _ => rfl⟩
      | cons d ds =>
        constructor
        · intro h; cases h
        · intro h
          have hh : ds.length+3≤2 := h
          have hk : 3≤ds.length+3 := Nat.le_add_left _ _
          exact (Nat.not_succ_le_self 2 (Nat.le_trans hk hh)).elim

theorem supported_iff (f : Formula) : supported f=true ↔ WidthTwo f := by
  induction f with
  | nil =>
    constructor
    · intro _ c h
      cases h
    · intro _
      rfl
  | cons c cs ih =>
    constructor
    · intro h d hd
      change (rowWidth c && supported cs)=true at h
      have hc : rowWidth c=true := by
        cases e : rowWidth c with
        | true => rfl
        | false => rw [e] at h; cases h
      have ht : supported cs=true := by rw [hc] at h; exact h
      cases hd with
      | head => exact (rowWidth_iff c).1 hc
      | tail _ hm => exact ih.1 ht d hm
    · intro h
      change (rowWidth c && supported cs)=true
      rw [(rowWidth_iff c).2 (h c (List.Mem.head _)),
        ih.2 (fun d hd => h d (List.Mem.tail _ hd))]
      rfl

theorem no_empty_two (f : Formula) (hw : WidthTwo f) (he : hasEmpty f=false) :
    TwoCNF f := by
  intro c hc
  have h := hw c hc
  cases c with
  | nil =>
    have hh := empty_complete f hc
    rw [he] at hh
    cases hh
  | cons a cs =>
    cases cs with
    | nil => exact Or.inl ⟨a,rfl⟩
    | cons b bs =>
      cases bs with
      | nil => exact Or.inr ⟨a,b,rfl⟩
      | cons d ds =>
        have hh : ds.length+3≤2 := h
        exact (Nat.not_succ_le_self 2 (Nat.le_trans (Nat.le_add_left _ _) hh)).elim

def emptyProof : Proof := ⟨[],false,.empty⟩

theorem empty_accepts (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (he : hasEmpty f=true) : boundCheck n f ⟨n,f,emptyProof⟩=true := by
  apply ProctorEnvelopeCompleteness.envelope_of_proof n f emptyProof hf rfl
  change (true && hasEmpty f)=true
  rw [he]
  rfl

-- Return a distinct status for outside-fragment or invalid input.
-- SAT assignments are the already verified constructive model.
inductive Result where
  | invalid
  | unsupported
  | sat (x : Assignment)
  | unsat (p : Proof)
  | internalError

def solve (n : Nat) (f : Formula) : Result :=
  if validFormula n f then
    if supported f then
      if hasEmpty f then .unsat emptyProof
      else
        match findConflict f (variables f) with
        | none => .sat (model f)
        | some v =>
          match checked n f (tryVar f (arcs f) v) with
          | none => .internalError
          | some p => .unsat p
    else .unsupported
  else .invalid

def Spec (n : Nat) (f : Formula) : Result → Prop
  | .invalid => validFormula n f=false
  | .unsupported => validFormula n f=true ∧ supported f=false
  | .sat x => validFormula n f=true ∧ WidthTwo f ∧ FormulaSat f x
  | .unsat p => validFormula n f=true ∧ WidthTwo f ∧
      boundCheck n f ⟨n,f,p⟩=true ∧
      p.batches.length≤2*occurrences f+1 ∧
      steps p.batches≤(f.length+(2*occurrences f+1))*(2*occurrences f+1)
  | .internalError => False

theorem checked_eq (n : Nat) (f : Formula) (o : Option Proof) (p : Proof)
    (h : checked n f o=some p) : o=some p := by
  cases o with
  | none => cases h
  | some q =>
    change (if boundCheck n f ⟨n,f,q⟩ then some q else none)=some p at h
    by_cases e : boundCheck n f ⟨n,f,q⟩=true
    · rw [if_pos e] at h
      exact h
    · rw [if_neg e] at h
      cases h

theorem solve_spec (n : Nat) (f : Formula) : Spec n f (solve n f) := by
  unfold solve
  cases hf : validFormula n f with
  | false => exact hf
  | true =>
    cases hw : supported f with
    | false => exact ⟨hf,hw⟩
    | true =>
      have width := (supported_iff f).1 hw
      cases he : hasEmpty f with
      | true =>
        exact ⟨hf,width,empty_accepts n f hf he,Nat.zero_le _,Nat.zero_le _⟩
      | false =>
        cases hc : findConflict f (variables f) with
        | none =>
          exact ⟨hf,width,model_satisfies f (no_empty_two f width he) (noConflict_of_none f hc)⟩
        | some v =>
          change Spec n f (match checked n f (tryVar f (arcs f) v) with
            | none => Result.internalError
            | some p => Result.unsat p)
          cases hp : checked n f (tryVar f (arcs f) v) with
          | none =>
            obtain ⟨ps,qs,hps,hqs⟩ := conflict_routes f v (findConflict_some f _ v hc)
            obtain ⟨p,hp'⟩ := checked_tryVar_complete n v f ps qs hf hps hqs
            rw [hp] at hp'
            cases hp'
          | some p =>
            have hs := tryVar_size f v p (checked_eq n f _ p hp)
            exact ⟨hf,width,checked_sound n f _ p hp,hs.left,hs.right⟩

theorem solve_no_internal_error (n : Nat) (f : Formula) :
    solve n f≠.internalError := by
  intro h
  have hs := solve_spec n f
  rw [h] at hs
  exact hs

theorem solve_sat_sound (n : Nat) (f : Formula) (x : Assignment)
    (h : solve n f=.sat x) : FormulaSat f x := by
  have hs := solve_spec n f
  rw [h] at hs
  exact hs.2.2

theorem solve_unsat_sound (n : Nat) (f : Formula) (p : Proof)
    (h : solve n f=.unsat p) : Unsat f := by
  have hs := solve_spec n f
  rw [h] at hs
  exact ProctorUnifiedReplay.bound_sound n f _ hs.2.2.1

theorem solve_unsat_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) (hu : Unsat f) :
    ∃ p, solve n f=.unsat p := by
  have hs := solve_spec n f
  cases h : solve n f with
  | invalid =>
    rw [h] at hs
    change validFormula n f=false at hs
    rw [hf] at hs
    cases hs
  | unsupported =>
    rw [h] at hs
    have hh := hs.2
    rw [(supported_iff f).2 hw] at hh
    cases hh
  | sat x => exact (hu ⟨x,solve_sat_sound n f x h⟩).elim
  | unsat p => exact ⟨p,rfl⟩
  | internalError => exact (solve_no_internal_error n f h).elim

theorem solve_sat_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) (hm : ∃ x, FormulaSat f x) :
    ∃ x, solve n f=.sat x := by
  have hs := solve_spec n f
  cases h : solve n f with
  | invalid =>
    rw [h] at hs
    change validFormula n f=false at hs
    rw [hf] at hs
    cases hs
  | unsupported =>
    rw [h] at hs
    have hh := hs.2
    rw [(supported_iff f).2 hw] at hh
    cases hh
  | sat x => exact ⟨x,rfl⟩
  | unsat p => exact (solve_unsat_sound n f p h hm).elim
  | internalError => exact (solve_no_internal_error n f h).elim

theorem solve_size (n : Nat) (f : Formula) (p : Proof)
    (h : solve n f=.unsat p) :
    p.batches.length≤2*occurrences f+1 ∧
      steps p.batches≤(f.length+(2*occurrences f+1))*(2*occurrences f+1) := by
  have hs := solve_spec n f
  rw [h] at hs
  exact hs.2.2.2

end ProctorTotalTwoCNF

#print axioms ProctorTotalTwoCNF.rowWidth_iff
#print axioms ProctorTotalTwoCNF.supported_iff
#print axioms ProctorTotalTwoCNF.no_empty_two
#print axioms ProctorTotalTwoCNF.empty_accepts
#print axioms ProctorTotalTwoCNF.checked_eq
#print axioms ProctorTotalTwoCNF.solve_spec
#print axioms ProctorTotalTwoCNF.solve_no_internal_error
#print axioms ProctorTotalTwoCNF.solve_sat_sound
#print axioms ProctorTotalTwoCNF.solve_unsat_sound
#print axioms ProctorTotalTwoCNF.solve_unsat_complete
#print axioms ProctorTotalTwoCNF.solve_sat_complete
#print axioms ProctorTotalTwoCNF.solve_size
