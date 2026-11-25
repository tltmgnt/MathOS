/-! F034 candidate: binary comparison and lookup substitution in
resolution-chain replay. Preserve the existing weakening semantics.
Separate selected comparison gates and lookup visits; no full cost claim.
Independent of the intermediate-width and input-binding PRs. -/
namespace ProctorBinaryChain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch lookup lookup_mem contains shapeCheck stepCheck batchCheck chainCheck tails frontier)
open ProctorCapacityReplay (test)
open ProctorBinaryReferences (Fits literalMeter literal_value literal_bound containsMeter contains_value contains_bound literalBudget)
open ProctorBinaryLookup (checkedLookup checked_formula_projection checked_bound)
open ProctorCheckedBinaryScanner (cap)

def FormulaFit (w : Nat) (f : Formula) : Prop := ∀ c ∈ f, Fits w c
def StepFit (w : Nat) (s : Step) : Prop :=
  s.left<cap w ∧ s.right<cap w ∧ s.pivot<cap w ∧ Fits w s.tail
def BatchFit (w : Nat) (b : Batch) : Prop := ∀ s ∈ b, StepFit w s

def shapeMeter (w : Nat) (p : Literal) (t : Clause) : Clause → Bool × Nat
  | [] => (true,0)
  | l::ls =>
    let e := literalMeter w l p
    if e.1 then
      let r := shapeMeter w p t ls
      (r.1,r.2+e.2)
    else
      let m := containsMeter w l t
      if m.1 then
        let r := shapeMeter w p t ls
        (r.1,r.2+(e.2+m.2))
      else (false,e.2+m.2)

theorem shape_value (w : Nat) (p : Literal) (t row : Clause)
    (hp : p.1<cap w) (ht : Fits w t) (hr : Fits w row) :
    (shapeMeter w p t row).1=shapeCheck p t row := by
  induction row with
  | nil => rfl
  | cons l ls ih =>
    have hl := hr l (List.Mem.head _)
    have hrest := ih (fun a ha => hr a (List.Mem.tail _ ha))
    unfold shapeMeter shapeCheck
    dsimp only
    rw [literal_value w l p hl hp]
    unfold test
    by_cases e : l=p
    · rw [if_pos e,if_pos e]
      exact hrest
    · rw [if_neg e,if_neg e,contains_value w l t hl ht]
      cases h : contains l t with
      | false => rfl
      | true => exact hrest

def shapeBudget (w : Nat) (t row : Clause) : Nat :=
  (literalBudget w+literalBudget w*t.length)*row.length

theorem shape_bound (w : Nat) (p : Literal) (t row : Clause) :
    (shapeMeter w p t row).2≤shapeBudget w t row := by
  induction row with
  | nil => exact Nat.le_refl 0
  | cons l ls ih =>
    unfold shapeMeter
    dsimp only
    change (if (literalMeter w l p).1 then
      ((shapeMeter w p t ls).1,(shapeMeter w p t ls).2+(literalMeter w l p).2)
      else if (containsMeter w l t).1 then
        ((shapeMeter w p t ls).1,(shapeMeter w p t ls).2+
          ((literalMeter w l p).2+(containsMeter w l t).2))
      else (false,(literalMeter w l p).2+(containsMeter w l t).2)).2≤
        shapeBudget w t ls+(literalBudget w+literalBudget w*t.length)
    cases e : (literalMeter w l p).1 with
    | true =>
      exact Nat.add_le_add ih
        (Nat.le_trans (literal_bound w l p) (Nat.le_add_right _ _))
    | false =>
      cases m : (containsMeter w l t).1 with
      | true =>
        exact Nat.add_le_add ih (Nat.add_le_add (literal_bound w l p) (contains_bound w l t))
      | false =>
        exact Nat.le_trans (Nat.add_le_add (literal_bound w l p) (contains_bound w l t))
          (Nat.le_add_left _ _)

-- Coordinates: Boolean result, lookup visits, selected literal gates.
abbrev Meter := Bool × Nat × Nat
def both (a b : Meter) : Meter := (a.1 && b.1,a.2.1+b.2.1,a.2.2+b.2.2)

def parentMeter (w : Nat) (f : Formula) (i : Nat) (p : Literal) (t : Clause) : Meter :=
  let a := checkedLookup w f i
  match a.1 with
  | none => (false,a.2,0)
  | some row => let b := shapeMeter w p t row; (b.1,a.2,b.2)

def parentGateBudget (w : Nat) (f : Formula) (i : Nat) (t : Clause) : Nat :=
  match (checkedLookup w f i).1 with
  | none => 0
  | some row => shapeBudget w t row

theorem parent_value (w : Nat) (f : Formula) (i : Nat) (p : Literal) (t : Clause)
    (hi : i<cap w) (hf : FormulaFit w f) (hp : p.1<cap w) (ht : Fits w t) :
    (parentMeter w f i p t).1=ProctorChainMeter.parentCheck f i p t := by
  unfold parentMeter ProctorChainMeter.parentCheck
  dsimp only
  rw [checked_formula_projection w f i hi]
  cases e : lookup f i with
  | none => rfl
  | some row => exact shape_value w p t row hp ht (hf row (lookup_mem f i row e))

theorem parent_visits (w : Nat) (f : Formula) (i : Nat) (p : Literal) (t : Clause) :
    (parentMeter w f i p t).2.1≤(w+1)*f.length := by
  unfold parentMeter
  dsimp only
  cases (checkedLookup w f i).1 <;> exact checked_bound w f i

theorem parent_gates (w : Nat) (f : Formula) (i : Nat) (p : Literal) (t : Clause) :
    (parentMeter w f i p t).2.2≤parentGateBudget w f i t := by
  unfold parentMeter parentGateBudget
  dsimp only
  cases (checkedLookup w f i).1 with
  | none => exact Nat.le_refl 0
  | some row => exact shape_bound w p t row

def stepMeter (w : Nat) (f : Formula) (s : Step) : Meter :=
  both (parentMeter w f s.left (s.pivot,true) s.tail)
       (parentMeter w f s.right (s.pivot,false) s.tail)

def stepGateBudget (w : Nat) (f : Formula) (s : Step) : Nat :=
  parentGateBudget w f s.left s.tail+parentGateBudget w f s.right s.tail

def stepVisitBudget (w : Nat) (f : Formula) : Nat :=
  (w+1)*f.length+(w+1)*f.length

theorem step_value (w : Nat) (f : Formula) (s : Step)
    (hf : FormulaFit w f) (hs : StepFit w s) :
    (stepMeter w f s).1=stepCheck f s := by
  unfold stepMeter both
  rw [parent_value w f s.left (s.pivot,true) s.tail hs.left hf hs.right.right.left hs.right.right.right,
      parent_value w f s.right (s.pivot,false) s.tail hs.right.left hf hs.right.right.left hs.right.right.right]
  unfold ProctorChainMeter.parentCheck stepCheck
  cases lookup f s.left with
  | none => rfl
  | some a =>
    cases lookup f s.right with
    | none => exact Bool.and_false _
    | some b => rfl

theorem step_visits (w : Nat) (f : Formula) (s : Step) :
    (stepMeter w f s).2.1≤stepVisitBudget w f :=
  Nat.add_le_add (parent_visits w f s.left (s.pivot,true) s.tail)
    (parent_visits w f s.right (s.pivot,false) s.tail)

theorem step_gates (w : Nat) (f : Formula) (s : Step) :
    (stepMeter w f s).2.2≤stepGateBudget w f s :=
  Nat.add_le_add (parent_gates w f s.left (s.pivot,true) s.tail)
    (parent_gates w f s.right (s.pivot,false) s.tail)

def batchMeter (w : Nat) (f : Formula) : Batch → Meter
  | [] => (true,0,0)
  | s::ss => both (stepMeter w f s) (batchMeter w f ss)

def batchGateBudget (w : Nat) (f : Formula) : Batch → Nat
  | [] => 0
  | s::ss => stepGateBudget w f s+batchGateBudget w f ss

theorem batch_value (w : Nat) (f : Formula) (ss : Batch)
    (hf : FormulaFit w f) (hs : BatchFit w ss) :
    (batchMeter w f ss).1=batchCheck f ss := by
  induction ss with
  | nil => rfl
  | cons s ss ih =>
    change ((stepMeter w f s).1 && (batchMeter w f ss).1)=
      (stepCheck f s && batchCheck f ss)
    rw [step_value w f s hf (hs s (List.Mem.head _)),
      ih (fun t ht => hs t (List.Mem.tail _ ht))]

theorem batch_visits (w : Nat) (f : Formula) (ss : Batch) :
    (batchMeter w f ss).2.1≤stepVisitBudget w f*ss.length := by
  induction ss with
  | nil => exact Nat.le_refl 0
  | cons s ss ih =>
    change (stepMeter w f s).2.1+(batchMeter w f ss).2.1≤
      stepVisitBudget w f*ss.length+stepVisitBudget w f
    rw [Nat.add_comm (stepMeter w f s).2.1 (batchMeter w f ss).2.1]
    exact Nat.add_le_add ih (step_visits w f s)

theorem batch_gates (w : Nat) (f : Formula) (ss : Batch) :
    (batchMeter w f ss).2.2≤batchGateBudget w f ss := by
  induction ss with
  | nil => exact Nat.le_refl 0
  | cons s ss ih => exact Nat.add_le_add (step_gates w f s) ih

theorem tails_fit (w : Nat) (ss : Batch) (hs : BatchFit w ss) :
    FormulaFit w (tails ss) := by
  induction ss with
  | nil => intro c hc; cases hc
  | cons s ss ih =>
    intro c hc
    change c ∈ s.tail::tails ss at hc
    cases hc with
    | head => exact (hs s (List.Mem.head _)).right.right.right
    | tail _ hm => exact ih (fun t ht => hs t (List.Mem.tail _ ht)) c hm

def chainMeter (w : Nat) (f : Formula) : List Batch → Meter
  | [] => (true,0,0)
  | ss::rest => both (batchMeter w f ss) (chainMeter w (tails ss) rest)

def chainGateBudget (w : Nat) (f : Formula) : List Batch → Nat
  | [] => 0
  | ss::rest => batchGateBudget w f ss+chainGateBudget w (tails ss) rest

def chainVisitBudget (w : Nat) (f : Formula) : List Batch → Nat
  | [] => 0
  | ss::rest => stepVisitBudget w f*ss.length+chainVisitBudget w (tails ss) rest

theorem chain_value (w : Nat) (f : Formula) (bs : List Batch)
    (hf : FormulaFit w f) (hb : ∀ b ∈ bs, BatchFit w b) :
    (chainMeter w f bs).1=chainCheck f bs := by
  induction bs generalizing f with
  | nil => rfl
  | cons ss rest ih =>
    change ((batchMeter w f ss).1 && (chainMeter w (tails ss) rest).1)=
      (batchCheck f ss && chainCheck (tails ss) rest)
    have h := hb ss (List.Mem.head _)
    rw [batch_value w f ss hf h,
      ih (tails ss) (tails_fit w ss h) (fun b hb' => hb b (List.Mem.tail _ hb'))]

theorem chain_visits (w : Nat) (f : Formula) (bs : List Batch) :
    (chainMeter w f bs).2.1≤chainVisitBudget w f bs := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl 0
  | cons ss rest ih => exact Nat.add_le_add (batch_visits w f ss) (ih (tails ss))

theorem chain_gates (w : Nat) (f : Formula) (bs : List Batch) :
    (chainMeter w f bs).2.2≤chainGateBudget w f bs := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl 0
  | cons ss rest ih => exact Nat.add_le_add (batch_gates w f ss) (ih (tails ss))

-- Discharge the representation premises on successfully decoded bytes.
theorem decoded_chain_value (a b : List Nat) (n : Nat) (f : Formula)
    (e : ProctorUnifiedReplay.Envelope)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    (chainMeter 512 f e.proof.batches).1=chainCheck f e.proof.batches := by
  have h1 := ProctorDecodedWidth.decoded_expected a n f ha
  have h2 := ProctorDecodedWidth.decoded_envelope b e hb
  exact chain_value 512 f e.proof.batches h1.right h2.right.right.left

theorem decoded_chain_sound (a b : List Nat) (n : Nat) (f : Formula)
    (e : ProctorUnifiedReplay.Envelope)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e)
    (h : (chainMeter 512 f e.proof.batches).1=true) :
    ProctorMixedInference.Entails f (frontier f e.proof.batches) := by
  rw [decoded_chain_value a b n f e ha hb] at h
  exact ProctorExecutableReplay.chain_sound f e.proof.batches h

end ProctorBinaryChain

#print axioms ProctorBinaryChain.shape_value
#print axioms ProctorBinaryChain.shape_bound
#print axioms ProctorBinaryChain.parent_value
#print axioms ProctorBinaryChain.parent_visits
#print axioms ProctorBinaryChain.parent_gates
#print axioms ProctorBinaryChain.step_value
#print axioms ProctorBinaryChain.step_visits
#print axioms ProctorBinaryChain.step_gates
#print axioms ProctorBinaryChain.batch_value
#print axioms ProctorBinaryChain.batch_visits
#print axioms ProctorBinaryChain.batch_gates
#print axioms ProctorBinaryChain.tails_fit
#print axioms ProctorBinaryChain.chain_value
#print axioms ProctorBinaryChain.chain_visits
#print axioms ProctorBinaryChain.chain_gates
#print axioms ProctorBinaryChain.decoded_chain_value
#print axioms ProctorBinaryChain.decoded_chain_sound
