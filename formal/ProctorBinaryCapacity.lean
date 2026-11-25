/-! F034 candidate: binary comparisons and indexed lookups in
capacity terminal validation. Retain Nat structural enumeration,
capacity guard and final capacity arithmetic. No whole cost claim. -/
namespace ProctorBinaryCapacity
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group opposite totalCapacity)
open ProctorCapacityReplay (RefRow Certificate test every someCheck refCheck distinctCheck words conflictCheck groupCheck indices demandAt getAt different capacityCheck)
open ProctorBinaryReferences (Fits refMeter ref_value containsMeter contains_value literalMeter literal_value)
open ProctorBinaryLookup (checkedLookup checked_projection checked_bound)
open ProctorCheckerBinaryTests (checkedEq checked_eq_value)
open ProctorCheckedBinaryScanner (cap)
open ProctorBinaryInputBinding (optFalse)
open ProctorIntermediateWidth (index_lt target_fit)
open ProctorWireRoundtrip (encFormula encList encBool)
open ProctorEnvelopeRoundtrip (encEnvelope encProof encBatch encTerminal encCapacity)

def FormulaFit (w : Nat) (f : Formula) : Prop := ∀ c ∈ f, Fits w c
def RefsFit (w : Nat) (rs : List RefRow) : Prop :=
  ∀ r ∈ rs, r.index<cap w ∧ Fits w r.row
def GroupsFit (w : Nat) (gs : List Group) : Prop :=
  ∀ g ∈ gs, Fits w g.literals

theorem every_congr {α : Type} (p q : α → Bool) (xs : List α)
    (h : ∀ a ∈ xs, p a=q a) : every p xs=every q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a && every p as)=(q a && every q as)
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))]

theorem some_congr {α : Type} (p q : α → Bool) (xs : List α)
    (h : ∀ a ∈ xs, p a=q a) : someCheck p xs=someCheck q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a || someCheck p as)=(q a || someCheck q as)
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))]

def refsBinary (w : Nat) (f : Formula) (rs : List RefRow) : Bool :=
  every (fun r => (refMeter w f r).1) rs

theorem refs_value (w : Nat) (f : Formula) (rs : List RefRow)
    (hf : FormulaFit w f) (hr : RefsFit w rs) :
    refsBinary w f rs=every (refCheck f) rs :=
  every_congr _ _ rs (fun r hm => ref_value w f r (hr r hm).left hf (hr r hm).right)

def distinctBinary (w : Nat) : Clause → Bool
  | [] => true
  | a::as => if (containsMeter w a as).1 then false else distinctBinary w as

theorem distinct_value (w : Nat) (xs : Clause) (h : Fits w xs) :
    distinctBinary w xs=distinctCheck xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    have ht : Fits w as := fun l hl => h l (List.Mem.tail _ hl)
    change (if (containsMeter w a as).1 then false else distinctBinary w as)=
      (if ProctorExecutableReplay.contains a as then false else distinctCheck as)
    rw [contains_value w a as (h a (List.Mem.head _)) ht,ih ht]

theorem words_value (w : Nat) (xs : Clause) (k : Nat) (p q : Clause → Bool)
    (hx : Fits w xs) (h : ∀ ys, Fits w ys → p ys=q ys) :
    words xs k p=words xs k q := by
  induction k generalizing p q with
  | zero => exact h [] (fun l hl => by cases hl)
  | succ k ih =>
    change every (fun a => words xs k (fun rest => p (a::rest))) xs=
      every (fun a => words xs k (fun rest => q (a::rest))) xs
    apply every_congr
    intro a ha
    apply ih
    intro ys hy
    apply h
    intro l hl
    cases hl with
    | head => exact hx a ha
    | tail _ hm => exact hy l hm

def conflictBinary (w : Nat) (rs : List RefRow) (ys : Clause) : Bool :=
  someCheck (fun r => every (fun l =>
    someCheck (fun p => (literalMeter w l (opposite p)).1) ys) r.row) rs

theorem conflict_value (w : Nat) (rs : List RefRow) (ys : Clause)
    (hr : RefsFit w rs) (hy : Fits w ys) :
    conflictBinary w rs ys=conflictCheck rs ys := by
  unfold conflictBinary conflictCheck
  apply some_congr
  intro r hm
  apply every_congr
  intro l hl
  apply some_congr
  intro p hp
  exact literal_value w l (opposite p) ((hr r hm).right l hl) (hy p hp)

def groupBinary (w : Nat) (rs : List RefRow) (g : Group) : Bool :=
  test (g.cap≤2) && (distinctBinary w g.literals &&
    words g.literals (g.cap+1) (fun ys =>
      if distinctBinary w ys then conflictBinary w rs ys else true))

theorem group_value (w : Nat) (rs : List RefRow) (g : Group)
    (hr : RefsFit w rs) (hg : Fits w g.literals) :
    groupBinary w rs g=groupCheck rs g := by
  unfold groupBinary groupCheck
  rw [distinct_value w g.literals hg]
  have hw : words g.literals (g.cap+1) (fun ys =>
      if distinctBinary w ys then conflictBinary w rs ys else true)=
      words g.literals (g.cap+1) (fun ys =>
      if distinctCheck ys then conflictCheck rs ys else true) := by
    apply words_value w g.literals (g.cap+1) _ _ hg
    intro ys hy
    rw [distinct_value w ys hy, conflict_value w rs ys hr hy]
  rw [hw]

def demandBinary (w : Nat) (ds : List RefRow) (i : Nat) : Clause :=
  match (checkedLookup w ds i).1 with
  | some r => r.row
  | none => []

theorem demand_value (w : Nat) (ds : List RefRow) (i : Nat)
    (hi : i<cap w) : demandBinary w ds i=demandAt ds i := by
  unfold demandBinary demandAt
  rw [checked_projection w ds i hi]

theorem demand_visits (w : Nat) (ds : List RefRow) (i : Nat) :
    (checkedLookup w ds i).2≤(w+1)*ds.length :=
  checked_bound w ds i

def natEq (w a b : Nat) : Bool := optFalse (checkedEq w a b).1

theorem nat_eq_value (w a b : Nat) (ha : a<cap w) (hb : b<cap w) :
    natEq w a b=test (a=b) := by
  unfold natEq
  rw [checked_eq_value w a b ha hb]
  rfl

theorem nat_ne_value (w a b : Nat) (ha : a<cap w) (hb : b<cap w) :
    (!natEq w a b)=test (a≠b) := by
  rw [nat_eq_value w a b ha hb]
  unfold test
  by_cases e : a=b
  · have hn : ¬ (a≠b) := fun h => h e
    rw [if_pos e,if_neg hn] <;> rfl
  · rw [if_neg e,if_pos e] <;> rfl

def differentBinary (w : Nat) (ds : List RefRow) (i j : Nat) : Bool :=
  if natEq w i j then true else
    every (fun a => every (fun b => !natEq w a.1 b.1)
      (demandBinary w ds j)) (demandBinary w ds i)

theorem different_value (w : Nat) (ds : List RefRow) (i j : Nat)
    (hi : i<cap w) (hj : j<cap w) (hr : RefsFit w ds) :
    differentBinary w ds i j=different ds i j := by
  unfold differentBinary different
  rw [nat_eq_value w i j hi hj,demand_value w ds i hi,demand_value w ds j hj]
  unfold test
  by_cases e : i=j
  · rw [if_pos e,if_pos e] <;> rfl
  · rw [if_neg e,if_neg e]
    have h1 := ProctorIntermediateWidth.demand_fit (cap w) ds i (fun r hm => (hr r hm).right)
    have h2 := ProctorIntermediateWidth.demand_fit (cap w) ds j (fun r hm => (hr r hm).right)
    apply every_congr
    intro a ha
    apply every_congr
    intro b hb
    exact nat_ne_value w a.1 b.1 (h1 a ha) (h2 b hb)

def coverageBinary (w : Nat) (ds : List RefRow) (gs : List Group) : Bool :=
  every (fun r => every (fun l =>
    someCheck (fun g => (containsMeter w l g.literals).1) gs) r.row) ds

theorem coverage_value (w : Nat) (ds : List RefRow) (gs : List Group)
    (hr : RefsFit w ds) (hg : GroupsFit w gs) :
    coverageBinary w ds gs=every (fun r => every (fun l =>
      someCheck (fun g => ProctorExecutableReplay.contains l g.literals) gs) r.row) ds := by
  unfold coverageBinary
  apply every_congr
  intro r hm
  apply every_congr
  intro l hl
  apply some_congr
  intro g hgm
  exact contains_value w l g.literals ((hr r hm).right l hl) (hg g hgm)

def capacityBinary (w : Nat) (f : Formula) (c : Certificate) : Bool :=
  refsBinary w f c.demands &&
  (refsBinary w f c.conflicts &&
  (every (groupBinary w c.conflicts) c.groups &&
  (every (fun i => every (differentBinary w c.demands i) (indices c.demands.length))
      (indices c.demands.length) &&
  (coverageBinary w c.demands c.groups &&
    test (totalCapacity c.groups<c.demands.length)))))

theorem capacity_value (w : Nat) (f : Formula) (c : Certificate)
    (hf : FormulaFit w f) (hd : RefsFit w c.demands)
    (hc : RefsFit w c.conflicts) (hg : GroupsFit w c.groups)
    (hn : c.demands.length<cap w) :
    capacityBinary w f c=capacityCheck f c := by
  unfold capacityBinary capacityCheck
  rw [refs_value w f c.demands hf hd,refs_value w f c.conflicts hf hc,
    every_congr _ _ c.groups (fun g hm => group_value w c.conflicts g hc (hg g hm)),
    coverage_value w c.demands c.groups hd hg]
  have he : every (fun i => every (differentBinary w c.demands i)
      (indices c.demands.length)) (indices c.demands.length)=
      every (fun i => every (different c.demands i)
      (indices c.demands.length)) (indices c.demands.length) := by
    apply every_congr
    intro i hi
    apply every_congr
    intro j hj
    exact different_value w c.demands i j
      (Nat.lt_trans (index_lt _ _ hi) hn) (Nat.lt_trans (index_lt _ _ hj) hn) hd
  rw [he]

theorem capacity_sound (w : Nat) (f : Formula) (c : Certificate)
    (hf : FormulaFit w f) (hd : RefsFit w c.demands)
    (hc : RefsFit w c.conflicts) (hg : GroupsFit w c.groups)
    (hn : c.demands.length<cap w) (h : capacityBinary w f c=true) :
    ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [capacity_value w f c hf hd hc hg hn] at h
  exact ProctorCapacityReplay.capacity_check_sound f c h

-- The serialized demand list count is itself a decoded token.
theorem decoded_demand_count (b : List Nat) (e : ProctorUnifiedReplay.Envelope)
    (c : Certificate) (hb : ProctorDataParser.decodeEnvelope b=some e)
    (ht : e.proof.terminal=ProctorUnifiedReplay.Terminal.capacity c) :
    c.demands.length<cap 512 := by
  have h := ProctorDecodedWidth.token_fit b (encEnvelope e)
    (ProctorParserConsumption.envelope_bytes b e hb).left
  change ProctorDecodedWidth.AllFit
    (3402::e.variableBound::(encFormula e.original++encProof e.proof)) at h
  have hp := ProctorDecodedWidth.append_right (encFormula e.original) (encProof e.proof)
    (fun n hm => h n (List.Mem.tail _ (List.Mem.tail _ hm)))
  change ProctorDecodedWidth.AllFit (encList encBatch e.proof.batches++
    (encBool e.proof.augmented++encTerminal e.proof.terminal)) at hp
  have hc := ProctorDecodedWidth.append_right (encBool e.proof.augmented) _
    (ProctorDecodedWidth.append_right (encList encBatch e.proof.batches) _ hp)
  rw [ht] at hc
  exact hc c.demands.length (List.Mem.tail _ (List.Mem.head _))

theorem decoded_capacity_value (a b : List Nat) (n : Nat) (f : Formula)
    (e : ProctorUnifiedReplay.Envelope) (c : Certificate)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e)
    (ht : e.proof.terminal=ProctorUnifiedReplay.Terminal.capacity c) :
    capacityBinary 512 (ProctorUnifiedReplay.target f e.proof) c=
      capacityCheck (ProctorUnifiedReplay.target f e.proof) c := by
  have h1 := ProctorDecodedWidth.decoded_expected a n f ha
  have h2 := ProctorDecodedWidth.decoded_envelope b e hb
  have hf := target_fit (cap 512) f e.proof h1.right
    (fun batch hm s hs => (h2.right.right.left batch hm s hs).right.right.right)
  have hc := h2.right.right.right
  rw [ht] at hc
  exact capacity_value 512 _ c hf hc.left hc.right.right
    (fun g hm => (hc.right.left g hm).left) (decoded_demand_count b e c hb ht)

end ProctorBinaryCapacity

#print axioms ProctorBinaryCapacity.every_congr
#print axioms ProctorBinaryCapacity.some_congr
#print axioms ProctorBinaryCapacity.refs_value
#print axioms ProctorBinaryCapacity.distinct_value
#print axioms ProctorBinaryCapacity.words_value
#print axioms ProctorBinaryCapacity.conflict_value
#print axioms ProctorBinaryCapacity.group_value
#print axioms ProctorBinaryCapacity.demand_value
#print axioms ProctorBinaryCapacity.demand_visits
#print axioms ProctorBinaryCapacity.nat_eq_value
#print axioms ProctorBinaryCapacity.nat_ne_value
#print axioms ProctorBinaryCapacity.different_value
#print axioms ProctorBinaryCapacity.coverage_value
#print axioms ProctorBinaryCapacity.capacity_value
#print axioms ProctorBinaryCapacity.capacity_sound
#print axioms ProctorBinaryCapacity.decoded_demand_count
#print axioms ProctorBinaryCapacity.decoded_capacity_value
