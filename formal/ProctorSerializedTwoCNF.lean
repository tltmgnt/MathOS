/-! F035: tagged SAT/UNSAT witness token interface. The independent
checker uses the expected typed input, not a producer-supplied digest.
The unconditional decimal encoder is a separate research module. -/
namespace ProctorSerializedTwoCNF
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope Proof boundCheck validFormula)
open ProctorTotalTwoCNF (solve Spec WidthTwo solve_spec solve_sat_complete solve_unsat_complete)
open ProctorFiniteModel (materialize readValue checkModel checkModel_sound materialized_accepts modelTokens model_roundtrip)
open ProctorOrdinaryCompleteness (variables)
open ProctorResolutionBridge (Unsat)
open ProctorWireRoundtrip (RoundTrip encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)
open ProctorDataParser (Parser)
open ProctorUnboundedCodec (clauseToken envelopeToken decode)

inductive Witness where
  | sat (rows : Clause)
  | unsat (e : Envelope)

def tokens : Witness → List Nat
  | .sat rows => 0::modelTokens rows
  | .unsat e => 1::encEnvelope e

def witnessToken : Parser Witness
  | 0::ts => do
    let (rows,rest) ← clauseToken ts
    some (.sat rows,rest)
  | 1::ts => do
    let (e,rest) ← envelopeToken ts
    some (.unsat e,rest)
  | _ => none

theorem witness_roundtrip (w : Witness) : RoundTrip witnessToken w (tokens w) := by
  intro rest
  cases w with
  | sat rows =>
    change (do
      let (rs,ts) ← clauseToken (modelTokens rows++rest)
      some (Witness.sat rs,ts))=some (Witness.sat rows,rest)
    rw [model_roundtrip rows rest]
    rfl
  | unsat e =>
    change (do
      let (q,ts) ← envelopeToken (encEnvelope e++rest)
      some (Witness.unsat q,ts))=some (Witness.unsat e,rest)
    rw [ProctorUnboundedRoundtrip.envelope_roundtrip e rest]
    rfl

theorem witness_decode (w : Witness) (bytes : List Nat)
    (h : ProctorUnboundedCodec.tokenize bytes=some (tokens w)) :
    decode witnessToken bytes=some w :=
  ProctorUnboundedRoundtrip.decode_exact _ _ _ _ (witness_roundtrip w) h

def check (n : Nat) (f : Formula) : Witness → Bool
  | .sat rows => validFormula n f && checkModel f rows
  | .unsat e => boundCheck n f e

def Meaning (f : Formula) : Witness → Prop
  | .sat rows => FormulaSat f (readValue rows)
  | .unsat _ => Unsat f

theorem check_sound (n : Nat) (f : Formula) (w : Witness)
    (h : check n f w=true) : Meaning f w := by
  cases w with
  | sat rows =>
    change (validFormula n f && checkModel f rows)=true at h
    cases hv : validFormula n f with
    | false => rw [hv] at h; cases h
    | true =>
      rw [hv] at h
      exact checkModel_sound f rows h
  | unsat e => exact ProctorUnifiedReplay.bound_sound n f e h

def produce (n : Nat) (f : Formula) : Option Witness :=
  match solve n f with
  | .sat x => some (.sat (materialize x (variables f)))
  | .unsat p => some (.unsat ⟨n,f,p⟩)
  | _ => none

theorem produce_accepts (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w) : check n f w=true := by
  have hs := solve_spec n f
  unfold produce at h
  cases e : solve n f with
  | invalid => rw [e] at h; cases h
  | unsupported => rw [e] at h; cases h
  | internalError => rw [e] at h; cases h
  | sat x =>
    rw [e] at h
    cases h
    rw [e] at hs
    change (validFormula n f && checkModel f (materialize x (variables f)))=true
    rw [hs.1,materialized_accepts f x hs.2.2]
    rfl
  | unsat p =>
    rw [e] at h
    cases h
    rw [e] at hs
    exact hs.2.2.1

theorem produce_sat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f)
    (h : ∃ x, FormulaSat f x) :
    ∃ rows, produce n f=some (.sat rows) := by
  obtain ⟨x,hx⟩ := solve_sat_complete n f hf hw h
  refine ⟨materialize x (variables f),?_⟩
  unfold produce
  rw [hx]

theorem produce_unsat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) (h : Unsat f) :
    ∃ p, produce n f=some (.unsat ⟨n,f,p⟩) := by
  obtain ⟨p,hp⟩ := solve_unsat_complete n f hf hw h
  refine ⟨p,?_⟩
  unfold produce
  rw [hp]

theorem produce_total (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) :
    ∃ w, produce n f=some w ∧ check n f w=true := by
  have hs := solve_spec n f
  cases e : solve n f with
  | invalid =>
    rw [e] at hs
    change validFormula n f=false at hs
    rw [hf] at hs
    cases hs
  | unsupported =>
    rw [e] at hs
    have hh := hs.2
    rw [(ProctorTotalTwoCNF.supported_iff f).2 hw] at hh
    cases hh
  | internalError => exact (ProctorTotalTwoCNF.solve_no_internal_error n f e).elim
  | sat x =>
    let w := Witness.sat (materialize x (variables f))
    have h : produce n f=some w := by unfold produce; rw [e]
    exact ⟨w,h,produce_accepts n f w h⟩
  | unsat p =>
    let w := Witness.unsat ⟨n,f,p⟩
    have h : produce n f=some w := by unfold produce; rw [e]
    exact ⟨w,h,produce_accepts n f w h⟩

def checkBytes (expected witness : List Nat) : Bool :=
  match ProctorUnboundedCodec.decodeExpected expected, decode witnessToken witness with
  | some (n,f), some w => check n f w
  | _,_ => false

theorem bytes_accept (n : Nat) (f : Formula) (w : Witness) (expected witness : List Nat)
    (he : ProctorUnboundedCodec.tokenize expected=some (encExpected n f))
    (hw : ProctorUnboundedCodec.tokenize witness=some (tokens w))
    (h : check n f w=true) : checkBytes expected witness=true := by
  unfold checkBytes
  rw [ProctorUnboundedRoundtrip.expected_exact n f expected he,witness_decode w witness hw]
  exact h

theorem bytes_sound (expected witness : List Nat) (h : checkBytes expected witness=true) :
    ∃ n f w, ProctorUnboundedCodec.decodeExpected expected=some (n,f) ∧
      decode witnessToken witness=some w ∧ Meaning f w := by
  unfold checkBytes at h
  cases he : ProctorUnboundedCodec.decodeExpected expected with
  | none => rw [he] at h; cases h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [he] at h
      cases hw : decode witnessToken witness with
      | none => rw [hw] at h; cases h
      | some w =>
        rw [hw] at h
        exact ⟨n,f,w,rfl,rfl,check_sound n f w h⟩

theorem sat_unsat_exclusive (n : Nat) (f : Formula) (rows : Clause) (e : Envelope)
    (hs : check n f (.sat rows)=true) (hu : check n f (.unsat e)=true) : False :=
  check_sound n f (.unsat e) hu ⟨readValue rows,check_sound n f (.sat rows) hs⟩

end ProctorSerializedTwoCNF

#print axioms ProctorSerializedTwoCNF.witness_roundtrip
#print axioms ProctorSerializedTwoCNF.witness_decode
#print axioms ProctorSerializedTwoCNF.check_sound
#print axioms ProctorSerializedTwoCNF.produce_accepts
#print axioms ProctorSerializedTwoCNF.produce_sat
#print axioms ProctorSerializedTwoCNF.produce_unsat
#print axioms ProctorSerializedTwoCNF.produce_total
#print axioms ProctorSerializedTwoCNF.bytes_accept
#print axioms ProctorSerializedTwoCNF.bytes_sound
#print axioms ProctorSerializedTwoCNF.sat_unsat_exclusive
