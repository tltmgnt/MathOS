/-! F035: integrate the verified explicit Boolean-list comparator
into the canonical byte producer. The new producer never constructs
the numeric score for its SAT branch. Equality is on finite witnesses,
not functions (no functional extensionality). -/
namespace ProctorBinaryByteSolver
open ProctorHallDeficiency
open ProctorUnifiedReplay (validFormula)
open ProctorExecutableReplay (hasEmpty)
open ProctorTotalTwoCNF (supported WidthTwo emptyProof solve)
open ProctorTwoCNFModel (findConflict model)
open ProctorImplicationPathDiscovery (arcs tryVar)
open ProctorBinarySquareDiscovery (checked)
open ProctorOrdinaryCompleteness (variables)
open ProctorFiniteModel (materialize)
open ProctorRankBitBounds (bitModel bit_model_eq)
open ProctorSerializedTwoCNF (Witness produce tokens checkBytes)
open ProctorEndToEndBytes (witnessBytes produceBytes)
open ProctorDecimalEncoder (encode)
open ProctorWireRoundtrip (encExpected)
open ProctorUnboundedCodec (decodeExpected)
open ProctorPolynomialWireSize (inputSize outputBudget)
open ProctorResolutionBridge (Unsat)

theorem materialize_congr (x y : Assignment) (vs : List Nat)
    (h : ∀ v, x v=y v) : materialize x vs=materialize y vs := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change (v,x v)::materialize x vs=(v,y v)::materialize y vs
    rw [h v,ih]

theorem bit_materialize_eq (f : Formula) :
    materialize (bitModel f) (variables f)=materialize (model f) (variables f) :=
  materialize_congr _ _ _ (bit_model_eq f)

def produceBits (n : Nat) (f : Formula) : Option Witness :=
  if validFormula n f then
    if supported f then
      if hasEmpty f then some (.unsat ⟨n,f,emptyProof⟩)
      else match findConflict f (variables f) with
        | none => some (.sat (materialize (bitModel f) (variables f)))
        | some v =>
          match checked n f (tryVar f (arcs f) v) with
          | none => none
          | some p => some (.unsat ⟨n,f,p⟩)
    else none
  else none

theorem producer_eq (n : Nat) (f : Formula) :
    produceBits n f=produce n f := by
  unfold produceBits produce solve
  cases hv : validFormula n f with
  | false => rfl
  | true =>
    cases hw : supported f with
    | false => rfl
    | true =>
      cases he : hasEmpty f with
      | true => rfl
      | false =>
        cases hc : findConflict f (variables f) with
        | none =>
          change some (Witness.sat (materialize (bitModel f) (variables f)))=
            some (Witness.sat (materialize (model f) (variables f)))
          rw [bit_materialize_eq]
        | some v =>
          change (match checked n f (tryVar f (arcs f) v) with
            | none => none
            | some p => some (Witness.unsat ⟨n,f,p⟩))=
            (match (match checked n f (tryVar f (arcs f) v) with
              | none => ProctorTotalTwoCNF.Result.internalError
              | some p => ProctorTotalTwoCNF.Result.unsat p) with
            | .sat x => some (.sat (materialize x (variables f)))
            | .unsat p => some (.unsat ⟨n,f,p⟩)
            | _ => none)
          cases hp : checked n f (tryVar f (arcs f) v) <;> rfl

def produceBitsBytes (expected : List Nat) : Option (List Nat) := do
  let (n,f) ← decodeExpected expected
  let w ← produceBits n f
  some (witnessBytes w)

theorem byte_producer_eq (expected : List Nat) :
    produceBitsBytes expected=produceBytes expected := by
  unfold produceBitsBytes produceBytes
  cases he : decodeExpected expected with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      change (do
        let w ← produceBits n f
        some (witnessBytes w))=(do
        let w ← produce n f
        some (witnessBytes w))
      rw [producer_eq]

theorem byte_sound (expected out : List Nat)
    (h : produceBitsBytes expected=some out) : checkBytes expected out=true := by
  rw [byte_producer_eq] at h
  exact ProctorEndToEndBytes.produce_bytes_sound expected out h

theorem byte_total (expected : List Nat) (n : Nat) (f : Formula)
    (he : decodeExpected expected=some (n,f))
    (hf : validFormula n f=true) (hw : WidthTwo f) :
    ∃ out, produceBitsBytes expected=some out ∧ checkBytes expected out=true := by
  rw [byte_producer_eq]
  exact ProctorEndToEndBytes.produce_bytes_total expected n f he hf hw

theorem byte_sat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f)
    (hm : ∃ x, FormulaSat f x) :
    ∃ rows, produceBitsBytes (encode (encExpected n f))=some (witnessBytes (.sat rows)) ∧
      checkBytes (encode (encExpected n f)) (witnessBytes (.sat rows))=true := by
  rw [byte_producer_eq]
  exact ProctorEndToEndBytes.encoded_sat n f hf hw hm

theorem byte_unsat (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hw : WidthTwo f) (hu : Unsat f) :
    ∃ p : ProctorUnifiedReplay.Proof,
      produceBitsBytes (encode (encExpected n f))=some (witnessBytes (.unsat ⟨n,f,p⟩)) ∧
      checkBytes (encode (encExpected n f)) (witnessBytes (.unsat ⟨n,f,p⟩))=true := by
  rw [byte_producer_eq]
  exact ProctorEndToEndBytes.encoded_unsat n f hf hw hu

theorem byte_size (n : Nat) (f : Formula) (out : List Nat)
    (h : produceBitsBytes (encode (encExpected n f))=some out) :
    out.length≤outputBudget (inputSize n f) := by
  rw [byte_producer_eq] at h
  exact ProctorPolynomialWireSize.canonical_byte_budget n f out h

theorem malformed_rejected (expected : List Nat) (h : decodeExpected expected=none) :
    produceBitsBytes expected=none := by
  rw [byte_producer_eq]
  exact ProctorEndToEndBytes.malformed_rejected expected h

end ProctorBinaryByteSolver

#print axioms ProctorBinaryByteSolver.materialize_congr
#print axioms ProctorBinaryByteSolver.bit_materialize_eq
#print axioms ProctorBinaryByteSolver.producer_eq
#print axioms ProctorBinaryByteSolver.byte_producer_eq
#print axioms ProctorBinaryByteSolver.byte_sound
#print axioms ProctorBinaryByteSolver.byte_total
#print axioms ProctorBinaryByteSolver.byte_sat
#print axioms ProctorBinaryByteSolver.byte_unsat
#print axioms ProctorBinaryByteSolver.byte_size
#print axioms ProctorBinaryByteSolver.malformed_rejected
