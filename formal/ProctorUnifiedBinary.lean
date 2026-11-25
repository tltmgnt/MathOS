/-! F034 candidate: unified selected binary checker substitution.
Exact byte-level acceptance projection, not full bit-machine refinement.
Separate partial gate and lookup ledger excludes terminal checking. -/
namespace ProctorUnifiedBinary
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope Proof Terminal target terminalCheck check)
open ProctorBinaryInputBinding (bindingMeter literalCount idBudget)
open ProctorBinaryReferences (literalBudget)
open ProctorExecutableReplay (hasEmpty)

def terminalBinary (f : Formula) : Terminal → Bool
  | .empty => hasEmpty f
  | .capacity c => ProctorBinaryCapacity.capacityBinary 512 f c
  | .xor bs => ProctorBinaryXor.xorBinary 512 f bs

def replayBinary (f : Formula) (p : Proof) : Bool :=
  (ProctorBinaryChain.chainMeter 512 f p.batches).1 &&
    terminalBinary (target f p) p.terminal

def binaryCheck (n : Nat) (f : Formula) (e : Envelope) : Bool :=
  (bindingMeter 512 n f e).1 &&
    ((ProctorBinaryProofRange.proofRange 512 n e.proof).1 && replayBinary f e.proof)

def checkBytes (a b : List Nat) : Bool :=
  match ProctorFuelFreeDecoder.decodeExpected a,ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (n,f),some e => binaryCheck n f e
  | _,_ => false

theorem decoded_terminal_value (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    terminalBinary (target f e.proof) e.proof.terminal=
      terminalCheck (target f e.proof) e.proof.terminal := by
  cases ht : e.proof.terminal with
  | empty => rfl
  | capacity c => exact ProctorBinaryCapacity.decoded_capacity_value a b n f e c ha hb ht
  | xor bs => exact ProctorBinaryXor.decoded_xor_value a b n f e bs ha hb ht

theorem decoded_replay_value (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    replayBinary f e.proof=check f e.proof := by
  unfold replayBinary check
  rw [ProctorBinaryChain.decoded_chain_value a b n f e ha hb,
    decoded_terminal_value a b n f e ha hb]

theorem decoded_bound_value (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    binaryCheck n f e=ProctorBinaryProofRange.binaryCheck n f e := by
  unfold binaryCheck ProctorBinaryProofRange.binaryCheck
  rw [decoded_replay_value a b n f e ha hb]

theorem bytes_value (a b : List Nat) :
    checkBytes a b=ProctorDataParser.checkBytes a b := by
  rw [← ProctorBinaryProofRange.decoded_check_value a b]
  unfold checkBytes ProctorBinaryProofRange.checkBytes
  rw [ProctorFuelFreeDecoder.expected_bytes_refines,ProctorFuelFreeDecoder.envelope_bytes_refines]
  cases ha : ProctorDataParser.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases hb : ProctorDataParser.decodeEnvelope b with
      | none => rfl
      | some e => exact decoded_bound_value a b n f e ha hb

theorem bytes_sound (a b : List Nat) (h : checkBytes a b=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [bytes_value] at h
  exact ProctorDataParser.accepted_unsat a b h

-- Independent conservative reservations, not a short-circuit trace.
-- Terminal resources are NOT included.
def partialLedger (n : Nat) (f : Formula) (e : Envelope) : Nat × Nat :=
  let a := bindingMeter 512 n f e
  let b := ProctorBinaryProofRange.proofRange 512 n e.proof
  let c := ProctorBinaryChain.chainMeter 512 f e.proof.batches
  (a.2+b.2+c.2.2,c.2.1)

def bindingBudget (f : Formula) : Nat :=
  ((5*512+5*512)+3)+literalBudget 512*literalCount f+
    idBudget 512*literalCount f

def partialGateBudget (f : Formula) (e : Envelope) : Nat :=
  bindingBudget f+ProctorBinaryProofRange.proofBudget 512 e.proof+
    ProctorBinaryChain.chainGateBudget 512 f e.proof.batches

theorem partial_gates (n : Nat) (f : Formula) (e : Envelope) :
    (partialLedger n f e).1≤partialGateBudget f e :=
  Nat.add_le_add (Nat.add_le_add (ProctorBinaryInputBinding.binding_bound 512 n f e)
    (ProctorBinaryProofRange.proof_bound 512 n e.proof))
    (ProctorBinaryChain.chain_gates 512 f e.proof.batches)

theorem partial_visits (n : Nat) (f : Formula) (e : Envelope) :
    (partialLedger n f e).2≤ProctorBinaryChain.chainVisitBudget 512 f e.proof.batches :=
  ProctorBinaryChain.chain_visits 512 f e.proof.batches

theorem partial_bounds (n : Nat) (f : Formula) (e : Envelope) :
    (partialLedger n f e).1≤partialGateBudget f e ∧
    (partialLedger n f e).2≤ProctorBinaryChain.chainVisitBudget 512 f e.proof.batches :=
  ⟨partial_gates n f e,partial_visits n f e⟩

end ProctorUnifiedBinary

#print axioms ProctorUnifiedBinary.decoded_terminal_value
#print axioms ProctorUnifiedBinary.decoded_replay_value
#print axioms ProctorUnifiedBinary.decoded_bound_value
#print axioms ProctorUnifiedBinary.bytes_value
#print axioms ProctorUnifiedBinary.bytes_sound
#print axioms ProctorUnifiedBinary.partial_gates
#print axioms ProctorUnifiedBinary.partial_visits
#print axioms ProctorUnifiedBinary.partial_bounds
