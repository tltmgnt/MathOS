/-! F035: unconditional byte-level completeness of the tagged width-two
solver, using the verified universal decimal encoder. No machine-cost
or unrestricted SAT complexity claim. -/
namespace ProctorEndToEndBytes
open ProctorHallDeficiency
open ProctorUnifiedReplay (validFormula)
open ProctorResolutionBridge (Unsat)
open ProctorTotalTwoCNF (WidthTwo)
open ProctorSerializedTwoCNF (Witness Meaning tokens witnessToken produce check checkBytes)
open ProctorDecimalEncoder (encode tokenize_encode expected_bytes)
open ProctorWireRoundtrip (encExpected)
open ProctorUnboundedCodec (decode decodeExpected)

def witnessBytes (w : Witness) : List Nat := encode (tokens w)

theorem witness_bytes (w : Witness) :
    decode witnessToken (witnessBytes w)=some w :=
  ProctorSerializedTwoCNF.witness_decode w _ (tokenize_encode _)

theorem check_encoded (n : Nat) (f : Formula) (w : Witness) :
    checkBytes (encode (encExpected n f)) (witnessBytes w)=check n f w := by
  unfold checkBytes
  rw [expected_bytes,witness_bytes]
  rfl

def produceBytes (expected : List Nat) : Option (List Nat) := do
  let (n,f) ← decodeExpected expected
  let w ← produce n f
  some (witnessBytes w)

theorem produce_encoded (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w) :
    produceBytes (encode (encExpected n f))=some (witnessBytes w) := by
  unfold produceBytes
  rw [expected_bytes]
  change (do
    let q ← produce n f
    some (witnessBytes q))=_
  rw [h]
  rfl

theorem produce_bytes_sound (expected out : List Nat)
    (h : produceBytes expected=some out) : checkBytes expected out=true := by
  unfold produceBytes at h
  cases he : decodeExpected expected with
  | none => rw [he] at h; cases h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [he] at h
      change (do
        let w ← produce n f
        some (witnessBytes w))=some out at h
      cases hw : produce n f with
      | none => rw [hw] at h; cases h
      | some w =>
        rw [hw] at h
        change some (witnessBytes w)=some out at h
        cases h
        unfold checkBytes
        rw [he,witness_bytes]
        exact ProctorSerializedTwoCNF.produce_accepts n f w hw

theorem produce_bytes_total (expected : List Nat) (n : Nat) (f : Formula)
    (he : decodeExpected expected=some (n,f))
    (hf : validFormula n f=true) (hw : WidthTwo f) :
    ∃ out, produceBytes expected=some out ∧ checkBytes expected out=true := by
  obtain ⟨w,hp,_⟩ := ProctorSerializedTwoCNF.produce_total n f hf hw
  have h : produceBytes expected=some (witnessBytes w) := by
    unfold produceBytes
    rw [he]
    change (do
      let q ← produce n f
      some (witnessBytes q))=_
    rw [hp]
    rfl
  exact ⟨_,h,produce_bytes_sound expected _ h⟩

theorem encoded_total (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) :
    ∃ out, produceBytes (encode (encExpected n f))=some out ∧
      checkBytes (encode (encExpected n f)) out=true :=
  produce_bytes_total _ n f (expected_bytes n f) hf hw

theorem encoded_sat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f)
    (hm : ∃ x, FormulaSat f x) :
    ∃ rows, produceBytes (encode (encExpected n f))=some (witnessBytes (.sat rows)) ∧
      checkBytes (encode (encExpected n f)) (witnessBytes (.sat rows))=true := by
  obtain ⟨rows,hr⟩ := ProctorSerializedTwoCNF.produce_sat n f hf hw hm
  have h := produce_encoded n f (.sat rows) hr
  exact ⟨rows,h,produce_bytes_sound _ _ h⟩

theorem encoded_unsat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) (hu : Unsat f) :
    ∃ p : ProctorUnifiedReplay.Proof,
      produceBytes (encode (encExpected n f))=some (witnessBytes (.unsat ⟨n,f,p⟩)) ∧
      checkBytes (encode (encExpected n f)) (witnessBytes (.unsat ⟨n,f,p⟩))=true := by
  obtain ⟨p,hp⟩ := ProctorSerializedTwoCNF.produce_unsat n f hf hw hu
  have h := produce_encoded n f (.unsat ⟨n,f,p⟩) hp
  exact ⟨p,h,produce_bytes_sound _ _ h⟩

theorem encoded_sound (n : Nat) (f : Formula) (out : List Nat)
    (h : checkBytes (encode (encExpected n f)) out=true) :
    ∃ w, decode witnessToken out=some w ∧ Meaning f w := by
  obtain ⟨n',f',w,he,hw,hm⟩ := ProctorSerializedTwoCNF.bytes_sound _ out h
  rw [expected_bytes] at he
  cases he
  exact ⟨w,hw,hm⟩

theorem malformed_rejected (expected : List Nat) (h : decodeExpected expected=none) :
    produceBytes expected=none := by
  unfold produceBytes
  rw [h]
  rfl

theorem byte_tags_exclusive (n : Nat) (f : Formula) (rows : Clause)
    (e : ProctorUnifiedReplay.Envelope)
    (hs : checkBytes (encode (encExpected n f)) (witnessBytes (.sat rows))=true)
    (hu : checkBytes (encode (encExpected n f)) (witnessBytes (.unsat e))=true) : False := by
  rw [check_encoded] at hs hu
  exact ProctorSerializedTwoCNF.sat_unsat_exclusive n f rows e hs hu

end ProctorEndToEndBytes

#print axioms ProctorEndToEndBytes.witness_bytes
#print axioms ProctorEndToEndBytes.check_encoded
#print axioms ProctorEndToEndBytes.produce_encoded
#print axioms ProctorEndToEndBytes.produce_bytes_sound
#print axioms ProctorEndToEndBytes.produce_bytes_total
#print axioms ProctorEndToEndBytes.encoded_total
#print axioms ProctorEndToEndBytes.encoded_sat
#print axioms ProctorEndToEndBytes.encoded_unsat
#print axioms ProctorEndToEndBytes.encoded_sound
#print axioms ProctorEndToEndBytes.malformed_rejected
#print axioms ProctorEndToEndBytes.byte_tags_exclusive
