/-! F034: data-only decimal token format. No generated Lean terms are
needed for the byte-input path. Append after ProctorUnifiedReplay. -/
namespace ProctorDataParser
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Proof Terminal Envelope boundCheck)

def byteLimit : Nat := 1000000
def digitLimit : Nat := 128
def listLimit : Nat := 100000

-- Exactly one LF terminator per natural token; no sign, whitespace,
-- blank token or redundant leading zero. EOF must be at a boundary.
def scan : List Nat → Nat → Nat → List Nat → Option (List Nat)
  | [], _, digits, acc => if digits=0 then some acc.reverse else none
  | b::bs, v, digits, acc =>
    if b=10 then
      if digits=0 then none else scan bs 0 0 (v::acc)
    else if 48 ≤ b ∧ b ≤ 57 then
      if digits ≥ digitLimit ∨ (digits > 0 ∧ v=0) then none
      else scan bs (10*v+(b-48)) (digits+1) acc
    else none

def tokenize (bytes : List Nat) : Option (List Nat) :=
  if bytes.length ≤ byteLimit then scan bytes 0 0 [] else none

abbrev Parser (α : Type) := List Nat → Option (α × List Nat)

def natToken : Parser Nat
  | [] => none
  | v::vs => some (v,vs)

def boolToken : Parser Bool := fun ts => do
  let (v,rest) ← natToken ts
  if v=0 then some (false,rest)
  else if v=1 then some (true,rest) else none

def manyAux {α : Type} (p : Parser α) :
    Nat → List Nat → List α → Option (List α × List Nat)
  | 0, ts, acc => some (acc.reverse,ts)
  | k+1, ts, acc => do
    let (a,rest) ← p ts
    manyAux p k rest (a::acc)

def listToken {α : Type} (p : Parser α) : Parser (List α) := fun ts => do
  let (k,rest) ← natToken ts
  if k ≤ listLimit then manyAux p k rest [] else none

def literalToken : Parser Literal := fun ts => do
  let (v,ts) ← natToken ts
  let (b,ts) ← boolToken ts
  some ((v,b),ts)

def clauseToken : Parser Clause := listToken literalToken
def formulaToken : Parser Formula := listToken clauseToken

def refToken : Parser RefRow := fun ts => do
  let (i,ts) ← natToken ts
  let (row,ts) ← clauseToken ts
  some (⟨i,row⟩,ts)

def groupToken : Parser ProctorCapacityDeficiency.Group := fun ts => do
  let (vs,ts) ← clauseToken ts
  let (cap,ts) ← natToken ts
  some (⟨vs,cap⟩,ts)

def capacityToken : Parser Certificate := fun ts => do
  let (ds,ts) ← listToken refToken ts
  let (gs,ts) ← listToken groupToken ts
  let (rs,ts) ← listToken refToken ts
  some (⟨ds,gs,rs⟩,ts)

def blockToken : Parser ProctorXorReplay.Block := fun ts => do
  let (vs,ts) ← listToken natToken ts
  let (rhs,ts) ← boolToken ts
  let (rs,ts) ← listToken refToken ts
  some (⟨vs,rhs,rs⟩,ts)

def stepToken : Parser Step := fun ts => do
  let (a,ts) ← natToken ts
  let (b,ts) ← natToken ts
  let (p,ts) ← natToken ts
  let (tail,ts) ← clauseToken ts
  some (⟨a,b,p,tail⟩,ts)

def terminalToken : Parser Terminal := fun ts => do
  let (tag,ts) ← natToken ts
  if tag=0 then some (.empty,ts)
  else if tag=1 then do
    let (c,ts) ← capacityToken ts
    some (.capacity c,ts)
  else if tag=2 then do
    let (bs,ts) ← listToken blockToken ts
    some (.xor bs,ts)
  else none

def proofToken : Parser Proof := fun ts => do
  let (bs,ts) ← listToken (listToken stepToken) ts
  let (aug,ts) ← boolToken ts
  let (terminal,ts) ← terminalToken ts
  some (⟨bs,aug,terminal⟩,ts)

def expectedToken : Parser (Nat × Formula) := fun ts => do
  let (magic,ts) ← natToken ts
  if magic=3401 then do
    let (n,ts) ← natToken ts
    let (f,ts) ← formulaToken ts
    some ((n,f),ts)
  else none

def envelopeToken : Parser Envelope := fun ts => do
  let (magic,ts) ← natToken ts
  if magic=3402 then do
    let (n,ts) ← natToken ts
    let (f,ts) ← formulaToken ts
    let (p,ts) ← proofToken ts
    some (⟨n,f,p⟩,ts)
  else none

def decode {α : Type} (p : Parser α) (bytes : List Nat) : Option α := do
  let ts ← tokenize bytes
  let (a,rest) ← p ts
  match rest with
  | [] => some a
  | _::_ => none

def decodeExpected := decode expectedToken
def decodeEnvelope := decode envelopeToken

def checkBytes (expected proof : List Nat) : Bool :=
  match decodeExpected expected, decodeEnvelope proof with
  | some (n,f), some e => boundCheck n f e
  | _, _ => false

theorem accepted_decoded (expected proof : List Nat)
    (h : checkBytes expected proof = true) :
    ∃ n f e, decodeExpected expected = some (n,f) ∧
      decodeEnvelope proof = some e ∧ boundCheck n f e = true := by
  unfold checkBytes at h
  cases he : decodeExpected expected with
  | none =>
    rw [he] at h
    exact Bool.noConfusion h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [he] at h
      cases hp : decodeEnvelope proof with
      | none =>
        rw [hp] at h
        exact Bool.noConfusion h
      | some e =>
        rw [hp] at h
        exact ⟨n,f,e,rfl,rfl,h⟩

theorem accepted_unsat (expected proof : List Nat)
    (h : checkBytes expected proof = true) :
    ∃ n f, decodeExpected expected = some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  obtain ⟨n,f,e,he,_,hc⟩ := accepted_decoded expected proof h
  exact ⟨n,f,he,ProctorUnifiedReplay.bound_sound n f e hc⟩

theorem accepted_binding (expected proof : List Nat)
    (h : checkBytes expected proof = true) :
    ∃ n f e, decodeExpected expected = some (n,f) ∧
      decodeEnvelope proof = some e ∧ n=e.variableBound ∧ f=e.original := by
  obtain ⟨n,f,e,he,hp,hc⟩ := accepted_decoded expected proof h
  have hb := ProctorUnifiedReplay.binding_exact n f e hc
  exact ⟨n,f,e,he,hp,hb.left,hb.right⟩

end ProctorDataParser

#print axioms ProctorDataParser.accepted_decoded
#print axioms ProctorDataParser.accepted_unsat
#print axioms ProctorDataParser.accepted_binding
