/-! F035: bound every token of the actual generated SAT/UNSAT witnesses.
The cap separates numerical identifiers from structural counts; this
does not assert a bit-cost model. -/
namespace ProctorTokenMagnitude
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch lookup stepCheck batchCheck chainCheck tails and_true_local)
open ProctorUnifiedReplay (Proof Envelope validId validClause validFormula validProof boundCheck)
open ProctorCapacityReplay (every every_sound test_sound)
open ProctorEnvelopeCompleteness (RowOK FormulaOK formula_ok variables_ok)
open ProctorWireRoundtrip (encNat encBool encLiteral encItems encList encClause encFormula encExpected)
open ProctorEnvelopeRoundtrip (encStep encBatch encProof encEnvelope)
open ProctorPathResourceBounds (occurrences steps)
open ProctorWireTokenBounds (NarrowSteps NarrowBatches variables_length solve_narrow)
open ProctorOrdinaryCompleteness (variables)
open ProctorFiniteModel (materialize materialize_member materialize_length)
open ProctorTotalTwoCNF (WidthTwo solve solve_spec solve_size)
open ProctorSerializedTwoCNF (Witness tokens produce)

def Bounded (cap : Nat) (ts : List Nat) : Prop := ∀ t∈ts, t≤cap

private theorem cons_bound (cap a : Nat) (as : List Nat)
    (ha : a≤cap) (hs : Bounded cap as) : Bounded cap (a::as) := by
  intro t ht
  cases ht with
  | head => exact ha
  | tail _ hm => exact hs t hm

private theorem nil_bound (cap : Nat) : Bounded cap [] := by
  intro t ht
  cases ht

private theorem append_bound (cap : Nat) (as bs : List Nat)
    (ha : Bounded cap as) (hb : Bounded cap bs) : Bounded cap (as++bs) := by
  induction as with
  | nil => exact hb
  | cons a as ih =>
    exact cons_bound cap a _ (ha a (List.Mem.head _))
      (ih (fun t ht => ha t (List.Mem.tail _ ht)))

theorem list_bound {α : Type} (enc : α → List Nat) (cap : Nat) (xs : List α)
    (hl : xs.length≤cap) (h : ∀ x∈xs, Bounded cap (enc x)) :
    Bounded cap (encList enc xs) := by
  apply cons_bound cap xs.length _ hl
  induction xs with
  | nil => exact nil_bound cap
  | cons x xs ih =>
    exact append_bound cap _ _ (h x (List.Mem.head _))
      (ih (Nat.le_trans (Nat.le_succ _) hl) (fun y hy => h y (List.Mem.tail _ hy)))

theorem id_bound (n v : Nat) (h : validId n v=true) : v≤n :=
  test_sound _ (and_true_local _ _ h).right

theorem literal_bound (cap : Nat) (l : Literal) (hv : l.1≤cap) (h1 : 1≤cap) :
    Bounded cap (encLiteral l) := by
  change Bounded cap (l.1::(if l.2 then 1 else 0)::[])
  apply cons_bound cap _ _ hv
  apply cons_bound cap _ _ _ (nil_bound cap)
  cases l.2 with
  | false => exact Nat.zero_le _
  | true => exact h1

theorem clause_bound (n cap : Nat) (c : Clause) (hn : n≤cap) (h1 : 1≤cap)
    (hl : c.length≤cap) (h : RowOK n c) : Bounded cap (encClause c) :=
  list_bound encLiteral cap c hl
    (fun l hm => literal_bound cap l (Nat.le_trans (id_bound n l.1 (h l hm)) hn) h1)

theorem formula_bound (n cap : Nat) (f : Formula) (hn : n≤cap)
    (h2 : 2≤cap) (hm : f.length≤cap) (hw : WidthTwo f) (hf : FormulaOK n f) :
    Bounded cap (encFormula f) :=
  list_bound encClause cap f hm (fun c hc =>
    clause_bound n cap c hn (Nat.le_trans (by decide : 1≤2) h2)
      (Nat.le_trans (hw c hc) h2) (hf c hc))

theorem lookup_index (f : Formula) (i : Nat) (c : Clause)
    (h : lookup f i=some c) : i<f.length := by
  induction f generalizing i with
  | nil => cases h
  | cons a as ih =>
    cases i with
    | zero => exact Nat.zero_lt_succ _
    | succ i => exact Nat.succ_lt_succ (ih i h)

theorem step_indices (f : Formula) (s : Step) (h : stepCheck f s=true) :
    s.left<f.length ∧ s.right<f.length := by
  unfold stepCheck at h
  cases ha : lookup f s.left with
  | none => rw [ha] at h; cases h
  | some a =>
    rw [ha] at h
    cases hb : lookup f s.right with
    | none => rw [hb] at h; cases h
    | some b => exact ⟨lookup_index f s.left a ha,lookup_index f s.right b hb⟩

theorem batch_indices (f : Formula) (b : Batch) (h : batchCheck f b=true) :
    ∀ s∈b, s.left<f.length ∧ s.right<f.length := by
  induction b with
  | nil => intro s hs; cases hs
  | cons s ss ih =>
    have hh := and_true_local _ _ h
    intro t ht
    cases ht with
    | head => exact step_indices f s hh.left
    | tail _ hm => exact ih hh.right t hm

theorem tails_length (b : Batch) : (tails b).length=b.length := by
  induction b with
  | nil => rfl
  | cons s ss ih => exact congrArg Nat.succ ih

theorem chain_indices (cap : Nat) (f : Formula) (bs : List Batch)
    (hc : chainCheck f bs=true) (h : f.length+steps bs≤cap) :
    ∀ b∈bs, ∀ s∈b, s.left≤cap ∧ s.right≤cap := by
  induction bs generalizing f with
  | nil => intro b hb; cases hb
  | cons b bs ih =>
    have hh := and_true_local _ _ hc
    intro d hd
    cases hd with
    | head =>
      intro s hs
      have hi := batch_indices f b hh.left s hs
      have hf := Nat.le_trans (Nat.le_add_right f.length (steps (b::bs))) h
      exact ⟨Nat.le_trans (Nat.le_of_lt hi.left) hf,Nat.le_trans (Nat.le_of_lt hi.right) hf⟩
    | tail _ hm =>
      have ht : (tails b).length+steps bs≤cap := by
        rw [tails_length]
        exact Nat.le_trans (Nat.le_add_left (steps (b::bs)) f.length) h
      exact ih (tails b) hh.right ht d hm

theorem batch_count (bs : List Batch) (b : Batch) (h : b∈bs) : b.length≤steps bs := by
  induction bs with
  | nil => cases h
  | cons c cs ih =>
    cases h with
    | head => exact Nat.le_add_right _ _
    | tail _ hm => exact Nat.le_trans (ih hm) (Nat.le_add_left _ _)

theorem step_bound (n cap : Nat) (s : Step)
    (hn : n≤cap) (h2 : 2≤cap) (hl : s.left≤cap) (hr : s.right≤cap)
    (hp : validId n s.pivot=true) (ht : RowOK n s.tail) (hw : s.tail.length≤2) :
    Bounded cap (encStep s) := by
  apply cons_bound cap _ _ hl
  apply cons_bound cap _ _ hr
  apply cons_bound cap _ _ (Nat.le_trans (id_bound n s.pivot hp) hn)
  exact clause_bound n cap s.tail hn (Nat.le_trans (by decide : 1≤2) h2)
    (Nat.le_trans hw h2) ht

theorem proof_bound (n cap : Nat) (f : Formula) (p : Proof)
    (hn : n≤cap) (h2 : 2≤cap) (hb : p.batches.length≤cap)
    (hs : f.length+steps p.batches≤cap)
    (hv : validProof n p=true) (hc : chainCheck f p.batches=true)
    (ht : p.terminal=.empty) (hw : NarrowBatches p.batches) :
    Bounded cap (encProof p) := by
  have hvalid := (and_true_local _ _ hv).left
  have hsteps := Nat.le_trans (Nat.le_add_left (steps p.batches) f.length) hs
  have hbatch : Bounded cap (encList encBatch p.batches) := by
    apply list_bound encBatch cap p.batches hb
    intro b hm
    apply list_bound encStep cap b (Nat.le_trans (batch_count p.batches b hm) hsteps)
    intro s hsm
    have hi := chain_indices cap f p.batches hc hs b hm s hsm
    have hh := and_true_local _ _ (every_sound _ b (every_sound _ p.batches hvalid b hm) s hsm)
    exact step_bound n cap s hn h2 hi.left hi.right hh.left
      (every_sound _ s.tail hh.right) (hw b hm s hsm)
  unfold encProof
  apply append_bound cap _ _ hbatch
  rw [ht]
  change Bounded cap ((if p.augmented then 1 else 0)::[0])
  apply cons_bound cap _ _ _ (cons_bound cap 0 [] (Nat.zero_le _) (nil_bound cap))
  cases p.augmented with
  | false => exact Nat.zero_le _
  | true => exact Nat.le_trans (by decide : 1≤2) h2

theorem accepted_components (n : Nat) (f : Formula) (p : Proof)
    (h : boundCheck n f ⟨n,f,p⟩=true) :
    validFormula n f=true ∧ validProof n p=true ∧ chainCheck f p.batches=true := by
  unfold boundCheck at h
  have h1 := and_true_local _ _ h
  have h2 := and_true_local _ _ h1.right
  have h3 := and_true_local _ _ h2.right
  have h4 := and_true_local _ _ h3.right
  exact ⟨h3.left,h4.left,(and_true_local _ _ h4.right).left⟩

theorem sat_bound (n cap : Nat) (f : Formula) (x : Assignment)
    (hn : n≤cap) (h1 : 1≤cap) (hl : occurrences f≤cap)
    (hf : validFormula n f=true) :
    Bounded cap (tokens (.sat (materialize x (variables f)))) := by
  apply cons_bound cap 0 _ (Nat.zero_le _)
  apply clause_bound n cap _ hn h1
  · rw [materialize_length,variables_length]
    exact hl
  · intro l hm
    exact variables_ok n f (formula_ok n f hf) l.1 (materialize_member x _ l hm).left

theorem unsat_bound (n cap : Nat) (f : Formula) (p : Proof)
    (hn : n≤cap) (hconst : 3402≤cap) (hb : p.batches.length≤cap)
    (hs : f.length+steps p.batches≤cap) (hw : WidthTwo f)
    (ht : p.terminal=.empty) (hnarrow : NarrowBatches p.batches)
    (hc : boundCheck n f ⟨n,f,p⟩=true) :
    Bounded cap (tokens (.unsat ⟨n,f,p⟩)) := by
  have hv := accepted_components n f p hc
  have h2 := Nat.le_trans (by decide : 2≤3402) hconst
  apply cons_bound cap 1 _ (Nat.le_trans (by decide : 1≤2) h2)
  apply cons_bound cap 3402 _ hconst
  apply cons_bound cap n _ hn
  apply append_bound cap _ _
  · exact formula_bound n cap f hn h2
      (Nat.le_trans (Nat.le_add_right f.length (steps p.batches)) hs) hw (formula_ok n f hv.left)
  · exact proof_bound n cap f p hn h2 hb hs hv.right.left hv.right.right ht hnarrow

-- Uniform cap for actual outputs, with separate numerical and
-- structural assumptions so the next decimal-size proof need not
-- charge the numerical identifier as unary input size.
theorem producer_bound (n cap : Nat) (f : Formula) (w : Witness)
    (hn : n≤cap) (hconst : 3402≤cap)
    (hl : occurrences f≤cap)
    (hb : 2*occurrences f+1≤cap)
    (hs : f.length+(f.length+(2*occurrences f+1))*(2*occurrences f+1)≤cap)
    (h : produce n f=some w) : Bounded cap (tokens w) := by
  have hv := solve_spec n f
  unfold produce at h
  cases he : solve n f with
  | invalid => rw [he] at h; cases h
  | unsupported => rw [he] at h; cases h
  | internalError => rw [he] at h; cases h
  | sat x =>
    rw [he] at h
    cases h
    rw [he] at hv
    exact sat_bound n cap f x hn (Nat.le_trans (by decide : 1≤3402) hconst) hl hv.1
  | unsat p =>
    rw [he] at h
    cases h
    rw [he] at hv
    have hsize := solve_size n f p he
    have hnarrow := solve_narrow n f p he
    exact unsat_bound n cap f p hn hconst (Nat.le_trans hsize.left hb)
      (Nat.le_trans (Nat.add_le_add_left hsize.right f.length) hs)
      hv.2.1 hnarrow.left hnarrow.right hv.2.2.1

end ProctorTokenMagnitude

#print axioms ProctorTokenMagnitude.list_bound
#print axioms ProctorTokenMagnitude.id_bound
#print axioms ProctorTokenMagnitude.literal_bound
#print axioms ProctorTokenMagnitude.clause_bound
#print axioms ProctorTokenMagnitude.formula_bound
#print axioms ProctorTokenMagnitude.lookup_index
#print axioms ProctorTokenMagnitude.step_indices
#print axioms ProctorTokenMagnitude.batch_indices
#print axioms ProctorTokenMagnitude.tails_length
#print axioms ProctorTokenMagnitude.chain_indices
#print axioms ProctorTokenMagnitude.batch_count
#print axioms ProctorTokenMagnitude.step_bound
#print axioms ProctorTokenMagnitude.proof_bound
#print axioms ProctorTokenMagnitude.accepted_components
#print axioms ProctorTokenMagnitude.sat_bound
#print axioms ProctorTokenMagnitude.unsat_bound
#print axioms ProctorTokenMagnitude.producer_bound
