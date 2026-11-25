/-! F034 candidate: compose verified fuel-free list iteration with
the verified nested parser and binary tokenizer. No new checker logic,
no complete cost claim, no production substitution. -/
namespace ProctorFuelFreeDecoder
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorNestedParser (ListBuilder ListContract expected envelope decode decode_refines)

def wordLists : ListBuilder := fun _ p => ProctorFuelFreeParser.listWord p

theorem word_contract : ListContract wordLists :=
  fun _ p ts => ProctorFuelFreeParser.list_word_refines p ts

def decodeExpected := decode (expected wordLists)
def decodeEnvelope := decode (envelope wordLists)

theorem expected_bytes_refines (bytes : List Nat) :
    decodeExpected bytes=ProctorDataParser.decodeExpected bytes :=
  decode_refines _ _ (ProctorNestedParser.expected_refines wordLists word_contract) bytes

theorem envelope_bytes_refines (bytes : List Nat) :
    decodeEnvelope bytes=ProctorDataParser.decodeEnvelope bytes :=
  decode_refines _ _ (ProctorNestedParser.envelope_refines wordLists word_contract) bytes

def checkBytes (expectedBytes proofBytes : List Nat) : Bool :=
  match decodeExpected expectedBytes,decodeEnvelope proofBytes with
  | some (n,f),some e => boundCheck n f e
  | _,_ => false

theorem check_refines (expectedBytes proofBytes : List Nat) :
    checkBytes expectedBytes proofBytes=ProctorDataParser.checkBytes expectedBytes proofBytes := by
  unfold checkBytes ProctorDataParser.checkBytes
  rw [expected_bytes_refines,envelope_bytes_refines]

theorem checked_decoder_agrees (expectedBytes proofBytes : List Nat) :
    checkBytes expectedBytes proofBytes=ProctorNestedParser.checkBytes expectedBytes proofBytes :=
  (check_refines expectedBytes proofBytes).trans
    (ProctorNestedParser.check_refines expectedBytes proofBytes).symm

theorem check_sound (expectedBytes proofBytes : List Nat)
    (h : checkBytes expectedBytes proofBytes=true) :
    ∃ n f, ProctorDataParser.decodeExpected expectedBytes=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [check_refines] at h
  exact ProctorDataParser.accepted_unsat expectedBytes proofBytes h

end ProctorFuelFreeDecoder

#print axioms ProctorFuelFreeDecoder.word_contract
#print axioms ProctorFuelFreeDecoder.expected_bytes_refines
#print axioms ProctorFuelFreeDecoder.envelope_bytes_refines
#print axioms ProctorFuelFreeDecoder.check_refines
#print axioms ProctorFuelFreeDecoder.checked_decoder_agrees
#print axioms ProctorFuelFreeDecoder.check_sound
