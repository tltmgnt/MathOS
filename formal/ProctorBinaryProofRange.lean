/-! F034 candidate: binary identifier range validation for all proof
fields checked by validProof. Reference and step indices, group
capacities, structural lengths and semantic replay retain their
original validation roles. Selected identifier comparison gates only. -/
namespace ProctorBinaryProofRange
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow every)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope validId validClause validRefs validTerminal validProof check)
open ProctorBinaryReferences (Fits)
open ProctorBinaryInputBinding (idGate idBudget id_gate_value allGate all_value all_bound
  weight clauseRange clause_range_value clause_range_bound bindingMeter)
open ProctorCheckedBinaryScanner (cap)
open ProctorCheckerBinaryTests (checked_id_bound)

def both (a b : Bool × Nat) : Bool × Nat := (a.1 && b.1,a.2+b.2)
def RefFit (w : Nat) (r : RefRow) : Prop := Fits w r.row
def RefsFit (w : Nat) (rs : List RefRow) : Prop := ∀ r ∈ rs, RefFit w r
def StepFit (w : Nat) (s : Step) : Prop := s.pivot<cap w ∧ Fits w s.tail
def BatchFit (w : Nat) (b : Batch) : Prop := ∀ s ∈ b, StepFit w s
def TerminalFit (w : Nat) : Terminal → Prop
  | .empty => True
  | .capacity c => RefsFit w c.demands ∧ RefsFit w c.conflicts ∧
      (∀ g ∈ c.groups, Fits w g.literals)
  | .xor bs => ∀ b ∈ bs, (∀ v ∈ b.support, v<cap w) ∧ RefsFit w b.refs

def refsRange (w n : Nat) (rs : List RefRow) : Bool × Nat :=
  allGate (fun r : RefRow => clauseRange w n r.row) rs

theorem refs_value (w n : Nat) (rs : List RefRow) (hn : n<cap w)
    (hr : RefsFit w rs) : (refsRange w n rs).1=validRefs n rs :=
  all_value _ _ rs (fun r hm => clause_range_value w n r.row hn (hr r hm))

def refsBudget (w : Nat) (rs : List RefRow) : Nat :=
  weight (fun r : RefRow => idBudget w*r.row.length) rs

theorem refs_bound (w n : Nat) (rs : List RefRow) :
    (refsRange w n rs).2≤refsBudget w rs :=
  all_bound _ _ (fun r : RefRow => clause_range_bound w n r.row) rs

def stepRange (w n : Nat) (s : Step) : Bool × Nat :=
  both (idGate w n s.pivot) (clauseRange w n s.tail)

def stepBudget (w : Nat) (s : Step) : Nat :=
  idBudget w+idBudget w*s.tail.length

theorem step_value (w n : Nat) (s : Step) (hn : n<cap w)
    (hs : StepFit w s) :
    (stepRange w n s).1=(validId n s.pivot && validClause n s.tail) := by
  unfold stepRange both
  rw [id_gate_value w n s.pivot hn hs.left,clause_range_value w n s.tail hn hs.right]

theorem step_bound (w n : Nat) (s : Step) :
    (stepRange w n s).2≤stepBudget w s :=
  Nat.add_le_add (checked_id_bound w n s.pivot) (clause_range_bound w n s.tail)

def batchRange (w n : Nat) (b : Batch) : Bool × Nat :=
  allGate (stepRange w n) b

def batchBudget (w : Nat) (b : Batch) : Nat := weight (stepBudget w) b

theorem batch_value (w n : Nat) (b : Batch) (hn : n<cap w)
    (hb : BatchFit w b) :
    (batchRange w n b).1=every (fun s : Step =>
      validId n s.pivot && validClause n s.tail) b :=
  all_value _ _ b (fun s hm => step_value w n s hn (hb s hm))

theorem batch_bound (w n : Nat) (b : Batch) :
    (batchRange w n b).2≤batchBudget w b :=
  all_bound _ _ (step_bound w n) b

def supportRange (w n : Nat) (vs : List Nat) : Bool × Nat :=
  allGate (idGate w n) vs

theorem support_value (w n : Nat) (vs : List Nat) (hn : n<cap w)
    (hv : ∀ v ∈ vs, v<cap w) :
    (supportRange w n vs).1=every (validId n) vs :=
  all_value _ _ vs (fun v hm => id_gate_value w n v hn (hv v hm))

theorem support_bound (w n : Nat) (vs : List Nat) :
    (supportRange w n vs).2≤weight (fun _ : Nat => idBudget w) vs :=
  all_bound _ _ (checked_id_bound w n) vs

def groupsRange (w n : Nat) (gs : List Group) : Bool × Nat :=
  allGate (fun g : Group => clauseRange w n g.literals) gs

theorem groups_value (w n : Nat) (gs : List Group) (hn : n<cap w)
    (hg : ∀ g ∈ gs, Fits w g.literals) :
    (groupsRange w n gs).1=every (fun g : Group => validClause n g.literals) gs :=
  all_value _ _ gs (fun g hm => clause_range_value w n g.literals hn (hg g hm))

theorem groups_bound (w n : Nat) (gs : List Group) :
    (groupsRange w n gs).2≤weight (fun g : Group => idBudget w*g.literals.length) gs :=
  all_bound _ _ (fun g : Group => clause_range_bound w n g.literals) gs

def blockRange (w n : Nat) (b : Block) : Bool × Nat :=
  both (supportRange w n b.support) (refsRange w n b.refs)

def blockBudget (w : Nat) (b : Block) : Nat :=
  weight (fun _ : Nat => idBudget w) b.support+refsBudget w b.refs

theorem block_value (w n : Nat) (b : Block) (hn : n<cap w)
    (hb : (∀ v ∈ b.support, v<cap w) ∧ RefsFit w b.refs) :
    (blockRange w n b).1=(every (validId n) b.support && validRefs n b.refs) := by
  unfold blockRange both
  rw [support_value w n b.support hn hb.left,refs_value w n b.refs hn hb.right]

theorem block_bound (w n : Nat) (b : Block) :
    (blockRange w n b).2≤blockBudget w b :=
  Nat.add_le_add (support_bound w n b.support) (refs_bound w n b.refs)

def terminalRange (w n : Nat) : Terminal → Bool × Nat
  | .empty => (true,0)
  | .capacity c => both (refsRange w n c.demands)
      (both (refsRange w n c.conflicts) (groupsRange w n c.groups))
  | .xor bs => allGate (blockRange w n) bs

def terminalBudget (w : Nat) : Terminal → Nat
  | .empty => 0
  | .capacity c => refsBudget w c.demands+
      (refsBudget w c.conflicts+weight (fun g : Group => idBudget w*g.literals.length) c.groups)
  | .xor bs => weight (blockBudget w) bs

theorem terminal_value (w n : Nat) (t : Terminal) (hn : n<cap w)
    (ht : TerminalFit w t) : (terminalRange w n t).1=validTerminal n t := by
  cases t with
  | empty => rfl
  | capacity c =>
    change ((refsRange w n c.demands).1 &&
      ((refsRange w n c.conflicts).1 && (groupsRange w n c.groups).1))=_
    rw [refs_value w n c.demands hn ht.left,refs_value w n c.conflicts hn ht.right.left,
      groups_value w n c.groups hn ht.right.right]
    rfl
  | xor bs =>
    exact all_value _ _ bs (fun b hm => block_value w n b hn (ht b hm))

theorem terminal_bound (w n : Nat) (t : Terminal) :
    (terminalRange w n t).2≤terminalBudget w t := by
  cases t with
  | empty => exact Nat.le_refl 0
  | capacity c =>
    exact Nat.add_le_add (refs_bound w n c.demands)
      (Nat.add_le_add (refs_bound w n c.conflicts) (groups_bound w n c.groups))
  | xor bs => exact all_bound _ _ (block_bound w n) bs

def proofRange (w n : Nat) (p : Proof) : Bool × Nat :=
  both (allGate (batchRange w n) p.batches) (terminalRange w n p.terminal)

def proofBudget (w : Nat) (p : Proof) : Nat :=
  weight (batchBudget w) p.batches+terminalBudget w p.terminal

theorem proof_value (w n : Nat) (p : Proof) (hn : n<cap w)
    (hb : ∀ b ∈ p.batches, BatchFit w b) (ht : TerminalFit w p.terminal) :
    (proofRange w n p).1=validProof n p := by
  unfold proofRange both validProof
  rw [terminal_value w n p.terminal hn ht]
  have h := all_value (batchRange w n) (fun b : Batch => every (fun s : Step =>
    validId n s.pivot && validClause n s.tail) b) p.batches
    (fun b hm => batch_value w n b hn (hb b hm))
  rw [h]

theorem proof_bound (w n : Nat) (p : Proof) :
    (proofRange w n p).2≤proofBudget w p :=
  Nat.add_le_add (all_bound _ _ (batch_bound w n) p.batches)
    (terminal_bound w n p.terminal)

theorem decoded_proof_fit (p : Proof) (h : ProctorDecodedWidth.ProofFit p) :
    (∀ b ∈ p.batches, BatchFit 512 b) ∧ TerminalFit 512 p.terminal := by
  refine ⟨fun b hm s hs => (h.left b hm s hs).right.right, ?_⟩
  have ht := h.right
  cases e : p.terminal with
  | empty => exact True.intro
  | capacity c =>
    rw [e] at ht
    exact ⟨fun r hm => (ht.left r hm).right,
      fun r hm => (ht.right.right r hm).right,
      fun g hm => (ht.right.left g hm).left⟩
  | xor bs =>
    rw [e] at ht
    exact fun b hm => ⟨(ht b hm).left,fun r hr => ((ht b hm).right r hr).right⟩

theorem decoded_proof_value (a b : List Nat) (n : Nat) (f : Formula)
    (e : Envelope) (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    (proofRange 512 n e.proof).1=validProof n e.proof := by
  have h1 := ProctorDecodedWidth.decoded_expected a n f ha
  have h2 := ProctorDecodedWidth.decoded_envelope b e hb
  have hp := decoded_proof_fit e.proof h2.right.right
  exact proof_value 512 n e.proof h1.left hp.left hp.right

def binaryCheck (n : Nat) (f : Formula) (e : Envelope) : Bool :=
  (bindingMeter 512 n f e).1 && ((proofRange 512 n e.proof).1 && check f e.proof)

def checkBytes (a b : List Nat) : Bool :=
  match ProctorFuelFreeDecoder.decodeExpected a,ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (n,f),some e => binaryCheck n f e
  | _,_ => false

theorem decoded_check_value (a b : List Nat) :
    checkBytes a b=ProctorDataParser.checkBytes a b := by
  unfold checkBytes
  rw [ProctorFuelFreeDecoder.expected_bytes_refines,ProctorFuelFreeDecoder.envelope_bytes_refines]
  rw [← ProctorBinaryInputBinding.decoded_check_value a b]
  unfold ProctorBinaryInputBinding.checkBytes
  rw [ProctorFuelFreeDecoder.expected_bytes_refines,ProctorFuelFreeDecoder.envelope_bytes_refines]
  cases ha : ProctorDataParser.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases hb : ProctorDataParser.decodeEnvelope b with
      | none => rfl
      | some e =>
        unfold binaryCheck ProctorBinaryInputBinding.binaryCheck
        rw [decoded_proof_value a b n f e ha hb]

theorem decoded_check_sound (a b : List Nat) (h : checkBytes a b=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [decoded_check_value] at h
  exact ProctorDataParser.accepted_unsat a b h

end ProctorBinaryProofRange

#print axioms ProctorBinaryProofRange.refs_value
#print axioms ProctorBinaryProofRange.refs_bound
#print axioms ProctorBinaryProofRange.step_value
#print axioms ProctorBinaryProofRange.step_bound
#print axioms ProctorBinaryProofRange.batch_value
#print axioms ProctorBinaryProofRange.batch_bound
#print axioms ProctorBinaryProofRange.support_value
#print axioms ProctorBinaryProofRange.support_bound
#print axioms ProctorBinaryProofRange.groups_value
#print axioms ProctorBinaryProofRange.groups_bound
#print axioms ProctorBinaryProofRange.block_value
#print axioms ProctorBinaryProofRange.block_bound
#print axioms ProctorBinaryProofRange.terminal_value
#print axioms ProctorBinaryProofRange.terminal_bound
#print axioms ProctorBinaryProofRange.proof_value
#print axioms ProctorBinaryProofRange.proof_bound
#print axioms ProctorBinaryProofRange.decoded_proof_fit
#print axioms ProctorBinaryProofRange.decoded_proof_value
#print axioms ProctorBinaryProofRange.decoded_check_value
#print axioms ProctorBinaryProofRange.decoded_check_sound
