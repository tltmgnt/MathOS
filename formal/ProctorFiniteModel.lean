/-! F035: finite assignment witnesses and token-level serialization.
A finite model contains one row per occurring variable occurrence;
repeated rows agree by construction. No scan of [1..n] is necessary.
The independent checker uses the original formula, not a producer
digest. Token roundtrip is distinct from byte encoder completeness. -/
namespace ProctorFiniteModel
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (variables variable_mem)
open ProctorTwoCNFModel (TwoCNF model findConflict noConflict_of_none model_satisfies)
open ProctorDataParser (Parser)
open ProctorWireRoundtrip (RoundTrip encClause encExpected encNat)
open ProctorUnboundedCodec (clauseToken expectedToken decode)
open ProctorUnboundedRoundtrip (clause_roundtrip)

def materialize (x : Assignment) : List Nat → Clause
  | [] => []
  | v::vs => (v,x v)::materialize x vs

def readValue (rows : Clause) (v : Nat) : Bool :=
  match rows with
  | [] => false
  | (w,b)::rs => if v=w then b else readValue rs v

theorem materialize_length (x : Assignment) (vs : List Nat) :
    (materialize x vs).length=vs.length := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change (materialize x vs).length+1=vs.length+1
    rw [ih]

theorem materialize_member (x : Assignment) (vs : List Nat) (l : Literal)
    (h : l∈materialize x vs) : l.1∈vs ∧ l.2=x l.1 := by
  induction vs with
  | nil => cases h
  | cons v vs ih =>
    cases h with
    | head => exact ⟨List.Mem.head _,rfl⟩
    | tail _ hm =>
      have hh := ih hm
      exact ⟨List.Mem.tail _ hh.left,hh.right⟩

theorem read_materialized (x : Assignment) (vs : List Nat) (v : Nat)
    (h : v∈vs) : readValue (materialize x vs) v=x v := by
  induction vs with
  | nil => cases h
  | cons w ws ih =>
    change (if v=w then x w else readValue (materialize x ws) v)=x v
    by_cases e : v=w
    · cases e
      rw [if_pos rfl]
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact ih hm

def evalRow (rows : Clause) : Clause → Bool
  | [] => false
  | l::ls => if readValue rows l.1=l.2 then true else evalRow rows ls

def checkModel (f : Formula) (rows : Clause) : Bool :=
  match f with
  | [] => true
  | c::cs => evalRow rows c && checkModel cs rows

theorem evalRow_sound (rows c : Clause) (h : evalRow rows c=true) :
    ClauseSat c (readValue rows) := by
  induction c with
  | nil => cases h
  | cons l ls ih =>
    change (if readValue rows l.1=l.2 then true else evalRow rows ls)=true at h
    by_cases e : readValue rows l.1=l.2
    · exact ⟨l,List.Mem.head _,e⟩
    · rw [if_neg e] at h
      obtain ⟨a,ha,ht⟩ := ih h
      exact ⟨a,List.Mem.tail _ ha,ht⟩

theorem evalRow_complete (rows c : Clause) (h : ClauseSat c (readValue rows)) :
    evalRow rows c=true := by
  induction c with
  | nil =>
    obtain ⟨l,hl,_⟩ := h
    cases hl
  | cons l ls ih =>
    change (if readValue rows l.1=l.2 then true else evalRow rows ls)=true
    by_cases e : readValue rows l.1=l.2
    · rw [if_pos e]
    · rw [if_neg e]
      obtain ⟨a,ha,ht⟩ := h
      cases ha with
      | head => exact (e ht).elim
      | tail _ hm => exact ih ⟨a,hm,ht⟩

theorem checkModel_sound (f : Formula) (rows : Clause)
    (h : checkModel f rows=true) : FormulaSat f (readValue rows) := by
  induction f with
  | nil => intro c hc; cases hc
  | cons c cs ih =>
    change (evalRow rows c && checkModel cs rows)=true at h
    have he : evalRow rows c=true := by
      cases e : evalRow rows c with
      | false => rw [e] at h; cases h
      | true => rfl
    have ht : checkModel cs rows=true := by rw [he] at h; exact h
    intro d hd
    cases hd with
    | head => exact evalRow_sound rows c he
    | tail _ hm => exact ih ht d hm

theorem checkModel_complete (f : Formula) (rows : Clause)
    (h : FormulaSat f (readValue rows)) : checkModel f rows=true := by
  induction f with
  | nil => rfl
  | cons c cs ih =>
    change (evalRow rows c && checkModel cs rows)=true
    rw [evalRow_complete rows c (h c (List.Mem.head _)),
      ih (fun d hd => h d (List.Mem.tail _ hd))]
    rfl

theorem materialized_satisfies (f : Formula) (x : Assignment)
    (h : FormulaSat f x) : FormulaSat f (readValue (materialize x (variables f))) := by
  intro c hc
  obtain ⟨l,hl,ht⟩ := h c hc
  exact ⟨l,hl,(read_materialized x (variables f) l.1
    (variable_mem f c l hc hl)).trans ht⟩

theorem materialized_accepts (f : Formula) (x : Assignment)
    (h : FormulaSat f x) : checkModel f (materialize x (variables f))=true :=
  checkModel_complete f _ (materialized_satisfies f x h)

def finiteModel (f : Formula) : Clause := materialize (model f) (variables f)

theorem finiteModel_accepts (f : Formula) (hf : TwoCNF f)
    (h : findConflict f (variables f)=none) : checkModel f (finiteModel f)=true :=
  materialized_accepts f (model f) (model_satisfies f hf (noConflict_of_none f h))

-- Reuse the existing unbounded literal-list codec. These are tokens,
-- not decimal bytes; exact byte decoding is conditional on tokenization.
def modelTokens (rows : Clause) : List Nat := encClause rows

theorem model_roundtrip (rows : Clause) : RoundTrip clauseToken rows (modelTokens rows) :=
  clause_roundtrip rows

theorem model_decode (rows : Clause) (bytes : List Nat)
    (h : ProctorUnboundedCodec.tokenize bytes=some (modelTokens rows)) :
    decode clauseToken bytes=some rows :=
  ProctorUnboundedRoundtrip.decode_exact _ _ _ _ (model_roundtrip rows) h

def checkModelBytes (expected witness : List Nat) : Bool :=
  match ProctorUnboundedCodec.decodeExpected expected, decode clauseToken witness with
  | some (n,f), some rows => ProctorUnifiedReplay.validFormula n f && checkModel f rows
  | _,_ => false

theorem bytes_model_accepts (n : Nat) (f : Formula) (rows : Clause)
    (expected witness : List Nat)
    (he : ProctorUnboundedCodec.tokenize expected=some (encExpected n f))
    (hw : ProctorUnboundedCodec.tokenize witness=some (modelTokens rows))
    (hf : ProctorUnifiedReplay.validFormula n f=true)
    (hs : checkModel f rows=true) : checkModelBytes expected witness=true := by
  unfold checkModelBytes
  rw [ProctorUnboundedRoundtrip.expected_exact n f expected he,model_decode rows witness hw]
  change (ProctorUnifiedReplay.validFormula n f && checkModel f rows)=true
  rw [hf,hs]
  rfl

theorem bytes_model_sound (expected witness : List Nat)
    (h : checkModelBytes expected witness=true) :
    ∃ n f rows, ProctorUnboundedCodec.decodeExpected expected=some (n,f) ∧
      decode clauseToken witness=some rows ∧ FormulaSat f (readValue rows) := by
  unfold checkModelBytes at h
  cases he : ProctorUnboundedCodec.decodeExpected expected with
  | none => rw [he] at h; cases h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [he] at h
      cases hw : decode clauseToken witness with
      | none => rw [hw] at h; cases h
      | some rows =>
        rw [hw] at h
        change (ProctorUnifiedReplay.validFormula n f && checkModel f rows)=true at h
        have hs : checkModel f rows=true := by
          cases hv : ProctorUnifiedReplay.validFormula n f with
          | false => rw [hv] at h; cases h
          | true => rw [hv] at h; exact h
        exact ⟨n,f,rows,rfl,rfl,checkModel_sound f rows hs⟩

end ProctorFiniteModel

#print axioms ProctorFiniteModel.materialize_length
#print axioms ProctorFiniteModel.materialize_member
#print axioms ProctorFiniteModel.read_materialized
#print axioms ProctorFiniteModel.evalRow_sound
#print axioms ProctorFiniteModel.evalRow_complete
#print axioms ProctorFiniteModel.checkModel_sound
#print axioms ProctorFiniteModel.checkModel_complete
#print axioms ProctorFiniteModel.materialized_satisfies
#print axioms ProctorFiniteModel.materialized_accepts
#print axioms ProctorFiniteModel.finiteModel_accepts
#print axioms ProctorFiniteModel.model_roundtrip
#print axioms ProctorFiniteModel.model_decode
#print axioms ProctorFiniteModel.bytes_model_accepts
#print axioms ProctorFiniteModel.bytes_model_sound
