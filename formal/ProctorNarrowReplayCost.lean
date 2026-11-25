/-! F035: extend F034's verified local meters to bounded-width
resolution replay. Counts are lookup row visits and literal comparisons,
not native time. Both parents and all steps are conservatively charged. -/
namespace ProctorNarrowReplayCost
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch lookup stepCheck batchCheck chainCheck tails)
open ProctorCheckerCost (lookupMeter lookup_value lookup_bound shapeMeter shape_value shape_bound shapeBudget)
open ProctorTotalTwoCNF (WidthTwo solve solve_size)
open ProctorWireTokenBounds (NarrowSteps NarrowBatches solve_narrow variables_length)
open ProctorTokenMagnitude (tails_length)
open ProctorPathResourceBounds (steps occurrences)
open ProctorFiniteModel (readValue materialize materialize_length)
open ProctorOrdinaryCompleteness (variables)

private theorem mul_add' (a b c : Nat) : a*(b+c)=a*b+a*c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change a*(b+c+1)=a*b+a*(c+1)
    rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]

private theorem add_mul' (a b c : Nat) : (a+b)*c=a*c+b*c := by
  rw [Nat.mul_comm (a+b) c,mul_add',Nat.mul_comm c a,Nat.mul_comm c b]

theorem shape_budget_length (tail row : Clause) :
    shapeBudget tail row=row.length*(tail.length+1) := by
  induction row with
  | nil => exact (Nat.zero_mul _).symm
  | cons l ls ih =>
    change shapeBudget tail ls+(tail.length+1)=(ls.length+1)*(tail.length+1)
    rw [ih,add_mul',Nat.one_mul]

theorem shape_narrow (pivot : Literal) (tail row : Clause)
    (ht : tail.length≤2) (hr : row.length≤2) :
    (shapeMeter pivot tail row).2≤6 := by
  have h := shape_bound pivot tail row
  rw [shape_budget_length] at h
  exact Nat.le_trans h (Nat.mul_le_mul hr (Nat.succ_le_succ ht))

def stepMeter (f : Formula) (s : Step) : Bool × Nat :=
  let a := lookupMeter f s.left
  let b := lookupMeter f s.right
  match a.1,b.1 with
  | some c,some d =>
    let l := shapeMeter (s.pivot,true) s.tail c
    let r := shapeMeter (s.pivot,false) s.tail d
    (l.1 && r.1,a.2+b.2+(l.2+r.2))
  | _,_ => (false,a.2+b.2)

theorem step_value (f : Formula) (s : Step) :
    (stepMeter f s).1=stepCheck f s := by
  unfold stepMeter stepCheck
  dsimp only
  rw [lookup_value,lookup_value]
  cases ha : lookup f s.left with
  | none => rfl
  | some a =>
    cases hb : lookup f s.right with
    | none => rfl
    | some b =>
      change ((shapeMeter (s.pivot,true) s.tail a).1 &&
        (shapeMeter (s.pivot,false) s.tail b).1)=_
      rw [shape_value,shape_value]

theorem step_bound (f : Formula) (s : Step) (hf : WidthTwo f) (hs : s.tail.length≤2) :
    (stepMeter f s).2≤f.length+f.length+12 := by
  unfold stepMeter
  dsimp only
  rw [lookup_value,lookup_value]
  have h := Nat.add_le_add (lookup_bound f s.left) (lookup_bound f s.right)
  cases ha : lookup f s.left with
  | none => exact Nat.le_trans h (Nat.le_add_right _ _)
  | some a =>
    cases hb : lookup f s.right with
    | none => exact Nat.le_trans h (Nat.le_add_right _ _)
    | some b =>
      exact Nat.add_le_add h (Nat.add_le_add
        (shape_narrow _ _ _ hs (hf a (ProctorExecutableReplay.lookup_mem f s.left a ha)))
        (shape_narrow _ _ _ hs (hf b (ProctorExecutableReplay.lookup_mem f s.right b hb))))

def batchMeter (f : Formula) : Batch → Bool × Nat
  | [] => (true,0)
  | s::ss =>
    let a := stepMeter f s
    let b := batchMeter f ss
    (a.1 && b.1,a.2+b.2)

theorem batch_value (f : Formula) (b : Batch) :
    (batchMeter f b).1=batchCheck f b := by
  induction b with
  | nil => rfl
  | cons s ss ih =>
    change ((stepMeter f s).1 && (batchMeter f ss).1)=(stepCheck f s && batchCheck f ss)
    rw [step_value,ih]

theorem batch_bound (f : Formula) (b : Batch) (hf : WidthTwo f) (hb : NarrowSteps b)
    (cap : Nat) (hc : f.length≤cap) :
    (batchMeter f b).2≤b.length*(cap+cap+12) := by
  induction b with
  | nil => exact Nat.zero_le _
  | cons s ss ih =>
    change (stepMeter f s).2+(batchMeter f ss).2≤(ss.length+1)*(cap+cap+12)
    rw [add_mul',Nat.one_mul,Nat.add_comm (ss.length*(cap+cap+12))]
    exact Nat.add_le_add
      (Nat.le_trans (step_bound f s hf (hb s (List.Mem.head _)))
        (Nat.add_le_add_right (Nat.add_le_add hc hc) 12))
      (ih (fun t ht => hb t (List.Mem.tail _ ht)))

theorem tails_narrow (b : Batch) (hb : NarrowSteps b) : WidthTwo (tails b) := by
  induction b with
  | nil => intro c hc; cases hc
  | cons s ss ih =>
    intro c hc
    cases hc with
    | head => exact hb s (List.Mem.head _)
    | tail _ hm => exact ih (fun t ht => hb t (List.Mem.tail _ ht)) c hm

def chainMeter (f : Formula) : List Batch → Bool × Nat
  | [] => (true,0)
  | b::bs =>
    let a := batchMeter f b
    let r := chainMeter (tails b) bs
    (a.1 && r.1,a.2+r.2)

theorem chain_value (f : Formula) (bs : List Batch) :
    (chainMeter f bs).1=chainCheck f bs := by
  induction bs generalizing f with
  | nil => rfl
  | cons b bs ih =>
    change ((batchMeter f b).1 && (chainMeter (tails b) bs).1)=
      (batchCheck f b && chainCheck (tails b) bs)
    rw [batch_value,ih]

theorem chain_bound (f : Formula) (bs : List Batch) (hf : WidthTwo f)
    (hb : NarrowBatches bs) (cap : Nat) (hc : f.length+steps bs≤cap) :
    (chainMeter f bs).2≤steps bs*(cap+cap+12) := by
  induction bs generalizing f with
  | nil => exact Nat.zero_le _
  | cons b bs ih =>
    have hbn := hb b (List.Mem.head _)
    have hcap : f.length≤cap := Nat.le_trans (Nat.le_add_right _ _) hc
    have ht : (tails b).length+steps bs≤cap := by
      rw [tails_length]
      exact Nat.le_trans (Nat.le_add_left (steps (b::bs)) f.length) hc
    change (batchMeter f b).2+(chainMeter (tails b) bs).2≤(b.length+steps bs)*(cap+cap+12)
    rw [add_mul']
    exact Nat.add_le_add (batch_bound f b hf hbn cap hcap)
      (ih _ (tails_narrow b hbn) (fun d hd => hb d (List.Mem.tail _ hd)) ht)

theorem solver_replay_bound (n : Nat) (f : Formula) (p : ProctorUnifiedReplay.Proof)
    (h : solve n f=.unsat p) :
    let K := 2*occurrences f+1
    let S := (f.length+K)*K
    let C := f.length+S
    (chainMeter f p.batches).2≤S*(C+C+12) := by
  have hv := ProctorTotalTwoCNF.solve_spec n f
  rw [h] at hv
  have hn := solve_narrow n f p h
  have hz := solve_size n f p h
  let K := 2*occurrences f+1
  let S := (f.length+K)*K
  let C := f.length+S
  have hc : f.length+steps p.batches≤C := Nat.add_le_add_left hz.right _
  exact Nat.le_trans (chain_bound f p.batches hv.2.1 hn.right C hc)
    (Nat.mul_le_mul_right _ hz.right)

-- SAT checker meter: one identifier equality per visited row,
-- one Boolean equality per visited literal, all clauses conservatively.
def readMeter (v : Nat) : Clause → Bool × Nat
  | [] => (false,0)
  | (w,b)::rs =>
    if v=w then (b,1)
    else let r := readMeter v rs; (r.1,r.2+1)

theorem read_value (v : Nat) (rs : Clause) : (readMeter v rs).1=readValue rs v := by
  induction rs with
  | nil => rfl
  | cons l ls ih =>
    cases l with
    | mk w b =>
      change (if v=w then (b,1) else ((readMeter v ls).1,(readMeter v ls).2+1)).1=
        (if v=w then b else readValue ls v)
      by_cases h : v=w
      · rw [if_pos h,if_pos h]
      · rw [if_neg h,if_neg h]
        exact ih

theorem read_bound (v : Nat) (rs : Clause) : (readMeter v rs).2≤rs.length := by
  induction rs with
  | nil => exact Nat.le_refl _
  | cons l ls ih =>
    cases l with
    | mk w b =>
      change (if v=w then (b,1) else ((readMeter v ls).1,(readMeter v ls).2+1)).2≤ls.length+1
      by_cases h : v=w
      · rw [if_pos h]
        exact Nat.succ_le_succ (Nat.zero_le _)
      · rw [if_neg h]
        exact Nat.succ_le_succ ih

def evalMeter (rs : Clause) : Clause → Bool × Nat
  | [] => (false,0)
  | l::ls =>
    let a := readMeter l.1 rs
    if a.1=l.2 then (true,a.2+1)
    else let r := evalMeter rs ls; (r.1,a.2+1+r.2)

theorem eval_value (rs row : Clause) :
    (evalMeter rs row).1=ProctorFiniteModel.evalRow rs row := by
  induction row with
  | nil => rfl
  | cons l ls ih =>
    change (if (readMeter l.1 rs).1=l.2 then (true,(readMeter l.1 rs).2+1)
      else ((evalMeter rs ls).1,(readMeter l.1 rs).2+1+(evalMeter rs ls).2)).1=
      (if readValue rs l.1=l.2 then true else ProctorFiniteModel.evalRow rs ls)
    rw [read_value]
    by_cases h : readValue rs l.1=l.2
    · rw [if_pos h,if_pos h]
    · rw [if_neg h,if_neg h]
      exact ih

theorem eval_bound (rs row : Clause) : (evalMeter rs row).2≤row.length*(rs.length+1) := by
  induction row with
  | nil => exact Nat.zero_le _
  | cons l ls ih =>
    change (if (readMeter l.1 rs).1=l.2 then (true,(readMeter l.1 rs).2+1)
      else ((evalMeter rs ls).1,(readMeter l.1 rs).2+1+(evalMeter rs ls).2)).2≤
      (ls.length+1)*(rs.length+1)
    rw [add_mul',Nat.one_mul,Nat.add_comm (ls.length*(rs.length+1))]
    have h := Nat.add_le_add_right (read_bound l.1 rs) 1
    by_cases e : (readMeter l.1 rs).1=l.2
    · rw [if_pos e]
      exact Nat.le_trans h (Nat.le_add_right _ _)
    · rw [if_neg e]
      exact Nat.add_le_add h ih

def modelMeter (rs : Clause) : Formula → Bool × Nat
  | [] => (true,0)
  | c::cs =>
    let a := evalMeter rs c
    let b := modelMeter rs cs
    (a.1 && b.1,a.2+b.2)

theorem model_value (rs : Clause) (f : Formula) :
    (modelMeter rs f).1=ProctorFiniteModel.checkModel f rs := by
  induction f with
  | nil => rfl
  | cons c cs ih =>
    change ((evalMeter rs c).1 && (modelMeter rs cs).1)=
      (ProctorFiniteModel.evalRow rs c && ProctorFiniteModel.checkModel cs rs)
    rw [eval_value,ih]

theorem model_bound (rs : Clause) (f : Formula) :
    (modelMeter rs f).2≤occurrences f*(rs.length+1) := by
  induction f with
  | nil => exact Nat.zero_le _
  | cons c cs ih =>
    change (evalMeter rs c).2+(modelMeter rs cs).2≤(c.length+occurrences cs)*(rs.length+1)
    rw [add_mul']
    exact Nat.add_le_add (eval_bound rs c) ih

theorem materialized_model_bound (f : Formula) (x : Assignment) :
    (modelMeter (materialize x (variables f)) f).2≤occurrences f*(occurrences f+1) := by
  have h := model_bound (materialize x (variables f)) f
  rw [materialize_length,variables_length] at h
  exact h

end ProctorNarrowReplayCost

#print axioms ProctorNarrowReplayCost.shape_budget_length
#print axioms ProctorNarrowReplayCost.shape_narrow
#print axioms ProctorNarrowReplayCost.step_value
#print axioms ProctorNarrowReplayCost.step_bound
#print axioms ProctorNarrowReplayCost.batch_value
#print axioms ProctorNarrowReplayCost.batch_bound
#print axioms ProctorNarrowReplayCost.tails_narrow
#print axioms ProctorNarrowReplayCost.chain_value
#print axioms ProctorNarrowReplayCost.chain_bound
#print axioms ProctorNarrowReplayCost.solver_replay_bound
#print axioms ProctorNarrowReplayCost.read_value
#print axioms ProctorNarrowReplayCost.read_bound
#print axioms ProctorNarrowReplayCost.eval_value
#print axioms ProctorNarrowReplayCost.eval_bound
#print axioms ProctorNarrowReplayCost.model_value
#print axioms ProctorNarrowReplayCost.model_bound
#print axioms ProctorNarrowReplayCost.materialized_model_bound
