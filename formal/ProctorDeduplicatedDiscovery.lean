/-! F035: remove repeated-variable splits, plus a checked fast path
for contradictory unit clauses. No polynomial worst-case claim. -/
namespace ProctorDeduplicatedDiscovery
open ProctorHallDeficiency
open ProctorExecutableReplay (Step lookup stepCheck hasEmpty)
open ProctorUnifiedReplay (Proof validFormula validProof validId boundCheck check)
open ProctorResolutionBridge (Unsat compile compile_refutation step_complete)
open ProctorOrdinaryCompleteness (variables)
open ProctorEnvelopeCompleteness (formula_ok variables_ok compile_range envelope_of_proof batchRange)
open ProctorExecutableDiscovery (build build_complete trace_check trace_frontier trace_range findRow find_sound)

def member (v : Nat) : List Nat → Bool
  | [] => false
  | a::as => if v=a then true else member v as

theorem member_complete (v : Nat) (vs : List Nat) (h : v∈vs) : member v vs=true := by
  induction vs with
  | nil => cases h
  | cons a as ih =>
    unfold member
    by_cases e : v=a
    · rw [if_pos e]
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact ih hm

theorem member_sound (v : Nat) (vs : List Nat) (h : member v vs=true) : v∈vs := by
  induction vs with
  | nil => cases h
  | cons a as ih =>
    unfold member at h
    by_cases e : v=a
    · cases e
      exact List.Mem.head _
    · rw [if_neg e] at h
      exact List.Mem.tail _ (ih h)

def unique : List Nat → List Nat
  | [] => []
  | v::vs => let us := unique vs; if member v us then us else v::us

theorem unique_forward (vs : List Nat) (v : Nat) (h : v∈vs) : v∈unique vs := by
  induction vs with
  | nil => cases h
  | cons a as ih =>
    unfold unique
    dsimp only
    cases e : member a (unique as) with
    | true =>
      rw [e]
      cases h with
      | head => exact member_sound _ _ e
      | tail _ hm => exact ih hm
    | false =>
      rw [e]
      cases h with
      | head => exact List.Mem.head _
      | tail _ hm => exact List.Mem.tail _ (ih hm)

theorem unique_backward (vs : List Nat) (v : Nat) (h : v∈unique vs) : v∈vs := by
  induction vs with
  | nil => cases h
  | cons a as ih =>
    unfold unique at h
    dsimp only at h
    cases e : member a (unique as) with
    | true =>
      rw [e] at h
      exact List.Mem.tail _ (ih h)
    | false =>
      rw [e] at h
      cases h with
      | head => exact List.Mem.head _
      | tail _ hm => exact List.Mem.tail _ (ih hm)

def Distinct : List Nat → Prop
  | [] => True
  | v::vs => (v∉vs) ∧ Distinct vs

theorem unique_distinct (vs : List Nat) : Distinct (unique vs) := by
  induction vs with
  | nil => exact True.intro
  | cons v vs ih =>
    unfold unique
    dsimp only
    cases e : member v (unique vs) with
    | true => rw [e]; exact ih
    | false =>
      rw [e]
      exact ⟨fun h => Bool.noConfusion (e.symm.trans (member_complete _ _ h)),ih⟩

theorem unique_ok (n : Nat) (vs : List Nat) (h : ∀ v∈vs, validId n v=true) :
    ∀ v∈unique vs, validId n v=true :=
  fun v hv => h v (unique_backward vs v hv)

def generate (n : Nat) (f : Formula) : Option Proof :=
  if n=0 then some ⟨[],false,.empty⟩
  else (build 1 (unique (variables f)) f []).map (fun r => ⟨compile 1 f r.1,false,.empty⟩)

theorem generate_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p, generate n f=some p ∧ boundCheck n f ⟨n,f,p⟩=true := by
  by_cases hn : n=0
  · cases hn
    obtain ⟨p,hp,hc⟩ := ProctorExecutableDiscovery.generate_complete 0 f hf hu
    exact ⟨p,hp,hc⟩
  · have hq : validId n 1=true := by
      unfold validId ProctorCapacityReplay.test
      rw [if_pos (Nat.zero_lt_succ 0),if_pos (Nat.succ_le_of_lt (Nat.pos_of_ne_zero hn))] <;> rfl
    have ho := formula_ok n f hf
    obtain ⟨ss,g,hb,ht,he⟩ := build_complete n 1 hq f (unique (variables f)) [] (fun _ => false) hu
      (fun c hc l hl => Or.inl (unique_forward _ _ (ProctorOrdinaryCompleteness.variable_mem f c l hc hl)))
      (unique_ok n _ (variables_ok n f ho)) (fun _ hl => nomatch hl) f (fun _ hc => hc)
    let p : Proof := ⟨compile 1 f ss,false,.empty⟩
    have hp : validProof n p=true := by
      change (ProctorCapacityReplay.every (batchRange n) (compile 1 f ss) && true)=true
      rw [compile_range n 1 f ss hq ho (trace_range ht)] <;> rfl
    have hc : check f p=true :=
      compile_refutation 1 f ss (trace_check ht) ((trace_frontier ht).symm ▸ ProctorOrdinaryCompleteness.empty_complete g he)
    refine ⟨p,?_,envelope_of_proof n f p hf hp hc⟩
    unfold generate
    rw [if_neg hn,hb] <;> rfl

def decide (n : Nat) (f : Formula) : Bool :=
  match generate n f with | none => false | some p => boundCheck n f ⟨n,f,p⟩

theorem decide_sound (n : Nat) (f : Formula) (h : decide n f=true) : Unsat f := by
  unfold decide at h
  cases e : generate n f with
  | none => rw [e] at h; cases h
  | some p => rw [e] at h; exact ProctorUnifiedReplay.bound_sound n f _ h

theorem decide_complete (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (h : Unsat f) : decide n f=true := by
  obtain ⟨p,hp,hc⟩ := generate_complete n f hf h
  unfold decide
  rw [hp]
  exact hc

theorem decide_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    decide n f=true ↔ Unsat f :=
  ⟨decide_sound n f,decide_complete n f hf⟩

-- Try all occurring variable identifiers for a one-step contradiction.
-- Validate any proposed proof with the original bound checker.
def unitCandidate (f : Formula) : List Nat → Option Proof
  | [] => none
  | v::vs =>
    match findRow (fun c => ProctorCapacityReplay.test (c=[(v,true)])) f,
          findRow (fun c => ProctorCapacityReplay.test (c=[(v,false)])) f with
    | some i,some j => some ⟨[[⟨i,j,v,[]⟩]],false,.empty⟩
    | _,_ => unitCandidate f vs

theorem unit_pair (n v i j : Nat) (f : Formula)
    (hf : validFormula n f=true) (hv : validId n v=true)
    (hi : lookup f i=some [(v,true)]) (hj : lookup f j=some [(v,false)]) :
    boundCheck n f ⟨n,f,⟨[[⟨i,j,v,[]⟩]],false,.empty⟩⟩=true := by
  let s : Step := ⟨i,j,v,[]⟩
  have hs : stepCheck f s=true := step_complete f s _ _ hi hj
    (fun l hl => by cases hl with | head => exact Or.inl rfl | tail _ hm => cases hm)
    (fun l hl => by cases hl with | head => exact Or.inl rfl | tail _ hm => cases hm)
  let p : Proof := ⟨[[s]],false,.empty⟩
  have hp : validProof n p=true := by
    change (((validId n v && true) && true) && true) && true = true
    rw [hv] <;> rfl
  have hc : check f p=true := by
    change ((stepCheck f s && true) && true) && true=true
    rw [hs] <;> rfl
  exact envelope_of_proof n f p hf hp hc

def fast (n : Nat) (f : Formula) : Bool :=
  match unitCandidate f (unique (variables f)) with
  | none => decide n f
  | some p => if boundCheck n f ⟨n,f,p⟩ then true else decide n f

theorem fast_sound (n : Nat) (f : Formula) (h : fast n f=true) : Unsat f := by
  unfold fast at h
  cases e : unitCandidate f (unique (variables f)) with
  | none => rw [e] at h; exact decide_sound n f h
  | some p =>
    rw [e] at h
    cases b : boundCheck n f ⟨n,f,p⟩ with
    | true => exact ProctorUnifiedReplay.bound_sound n f _ b
    | false => rw [b] at h; exact decide_sound n f h

theorem fast_complete (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (hu : Unsat f) : fast n f=true := by
  unfold fast
  cases e : unitCandidate f (unique (variables f)) with
  | none => rw [e]; exact decide_complete n f hf hu
  | some p =>
    rw [e]
    cases b : boundCheck n f ⟨n,f,p⟩ with
    | true => rw [b]; rfl
    | false => rw [b]; exact decide_complete n f hf hu

theorem fast_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    fast n f=true ↔ Unsat f :=
  ⟨fast_sound n f,fast_complete n f hf⟩

end ProctorDeduplicatedDiscovery

#print axioms ProctorDeduplicatedDiscovery.member_complete
#print axioms ProctorDeduplicatedDiscovery.member_sound
#print axioms ProctorDeduplicatedDiscovery.unique_forward
#print axioms ProctorDeduplicatedDiscovery.unique_backward
#print axioms ProctorDeduplicatedDiscovery.unique_distinct
#print axioms ProctorDeduplicatedDiscovery.unique_ok
#print axioms ProctorDeduplicatedDiscovery.generate_complete
#print axioms ProctorDeduplicatedDiscovery.decide_sound
#print axioms ProctorDeduplicatedDiscovery.decide_complete
#print axioms ProctorDeduplicatedDiscovery.decide_iff
#print axioms ProctorDeduplicatedDiscovery.unit_pair
#print axioms ProctorDeduplicatedDiscovery.fast_sound
#print axioms ProctorDeduplicatedDiscovery.fast_complete
#print axioms ProctorDeduplicatedDiscovery.fast_iff
