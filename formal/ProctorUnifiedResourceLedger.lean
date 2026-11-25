/-! F034 candidate: compose the selected checker terminal and
nonterminal ledgers. Eager independent reservations, not a trace
of the unified short-circuit checker or a complete machine cost. -/
namespace ProctorUnifiedResourceLedger
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope Terminal target)
open ProctorXorResourceLedger (Meter both)
open ProctorExecutableReplay (hasEmpty)

def terminalMeter (f : Formula) : Terminal → Meter
  | .empty => (hasEmpty f,0,0)
  | .capacity c => ProctorCapacityResourceLedger.capacityMeter 512 f c
  | .xor bs => ProctorXorResourceLedger.xorMeter 512 f bs

def terminalVisitBudget (f : Formula) : Terminal → Nat
  | .empty => 0
  | .capacity c => ProctorCapacityResourceLedger.visitBudget 512 f c
  | .xor bs => ProctorXorResourceLedger.visitBudget 512 f bs

def terminalGateBudget (f : Formula) : Terminal → Nat
  | .empty => 0
  | .capacity c => ProctorCapacityResourceLedger.gateBudget 512 f c
  | .xor bs => ProctorXorResourceLedger.gateBudget 512 f bs

theorem terminal_value (f : Formula) (t : Terminal) :
    (terminalMeter f t).1=ProctorUnifiedBinary.terminalBinary f t := by
  cases t with
  | empty => rfl
  | capacity c => exact ProctorCapacityResourceLedger.capacity_value 512 f c
  | xor bs => exact ProctorXorResourceLedger.xor_value 512 f bs

theorem terminal_bounds (f : Formula) (t : Terminal) :
    (terminalMeter f t).2.1≤terminalVisitBudget f t ∧
    (terminalMeter f t).2.2≤terminalGateBudget f t := by
  cases t with
  | empty => exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩
  | capacity c => exact ProctorCapacityResourceLedger.capacity_bounds 512 f c
  | xor bs => exact ProctorXorResourceLedger.xor_bounds 512 f bs

def checkerMeter (n : Nat) (f : Formula) (e : Envelope) : Meter :=
  let a := ProctorBinaryInputBinding.bindingMeter 512 n f e
  let b := ProctorBinaryProofRange.proofRange 512 n e.proof
  let c := ProctorBinaryChain.chainMeter 512 f e.proof.batches
  let t := terminalMeter (target f e.proof) e.proof.terminal
  (a.1 && (b.1 && (c.1 && t.1)),c.2.1+t.2.1,a.2+b.2+c.2.2+t.2.2)

def checkerVisitBudget (f : Formula) (e : Envelope) : Nat :=
  ProctorBinaryChain.chainVisitBudget 512 f e.proof.batches+
    terminalVisitBudget (target f e.proof) e.proof.terminal

def checkerGateBudget (f : Formula) (e : Envelope) : Nat :=
  ProctorUnifiedBinary.partialGateBudget f e+
    terminalGateBudget (target f e.proof) e.proof.terminal

theorem checker_value (n : Nat) (f : Formula) (e : Envelope) :
    (checkerMeter n f e).1=ProctorUnifiedBinary.binaryCheck n f e := by
  unfold checkerMeter ProctorUnifiedBinary.binaryCheck ProctorUnifiedBinary.replayBinary
  dsimp only
  rw [terminal_value]

theorem checker_bounds (n : Nat) (f : Formula) (e : Envelope) :
    (checkerMeter n f e).2.1≤checkerVisitBudget f e ∧
    (checkerMeter n f e).2.2≤checkerGateBudget f e := by
  have h := ProctorUnifiedBinary.partial_bounds n f e
  have t := terminal_bounds (target f e.proof) e.proof.terminal
  exact ⟨Nat.add_le_add h.right t.left,Nat.add_le_add h.left t.right⟩

def bytesMeter (a b : List Nat) : Meter :=
  match ProctorFuelFreeDecoder.decodeExpected a, ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (n,f),some e => checkerMeter n f e
  | _,_ => (false,0,0)

def bytesVisitBudget (a b : List Nat) : Nat :=
  match ProctorFuelFreeDecoder.decodeExpected a, ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (_,f),some e => checkerVisitBudget f e
  | _,_ => 0

def bytesGateBudget (a b : List Nat) : Nat :=
  match ProctorFuelFreeDecoder.decodeExpected a, ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (_,f),some e => checkerGateBudget f e
  | _,_ => 0

theorem bytes_binary_value (a b : List Nat) :
    (bytesMeter a b).1=ProctorUnifiedBinary.checkBytes a b := by
  unfold bytesMeter ProctorUnifiedBinary.checkBytes
  cases ProctorFuelFreeDecoder.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases ProctorFuelFreeDecoder.decodeEnvelope b with
      | none => rfl
      | some e => exact checker_value n f e

theorem bytes_value (a b : List Nat) :
    (bytesMeter a b).1=ProctorDataParser.checkBytes a b :=
  (bytes_binary_value a b).trans (ProctorUnifiedBinary.bytes_value a b)

theorem bytes_sound (a b : List Nat) (h : (bytesMeter a b).1=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [bytes_binary_value] at h
  exact ProctorUnifiedBinary.bytes_sound a b h

theorem bytes_bounds (a b : List Nat) :
    (bytesMeter a b).2.1≤bytesVisitBudget a b ∧
    (bytesMeter a b).2.2≤bytesGateBudget a b := by
  unfold bytesMeter bytesVisitBudget bytesGateBudget
  cases ProctorFuelFreeDecoder.decodeExpected a with
  | none => exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩
  | some nf =>
    cases nf with
    | mk n f =>
      cases ProctorFuelFreeDecoder.decodeEnvelope b with
      | none => exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩
      | some e => exact checker_bounds n f e

end ProctorUnifiedResourceLedger

#print axioms ProctorUnifiedResourceLedger.terminal_value
#print axioms ProctorUnifiedResourceLedger.terminal_bounds
#print axioms ProctorUnifiedResourceLedger.checker_value
#print axioms ProctorUnifiedResourceLedger.checker_bounds
#print axioms ProctorUnifiedResourceLedger.bytes_binary_value
#print axioms ProctorUnifiedResourceLedger.bytes_value
#print axioms ProctorUnifiedResourceLedger.bytes_sound
#print axioms ProctorUnifiedResourceLedger.bytes_bounds
