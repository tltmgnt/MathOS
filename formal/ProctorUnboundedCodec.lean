/-! F035 candidate: unbounded typed token grammar and decimal scanner.
No fixed byte, digit, list or operand-width cap. Nat costs and decoder
complexity remain open. Original bounded decoder is unchanged. -/
namespace ProctorUnboundedCodec
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Proof Terminal Envelope boundCheck)
open ProctorDataParser (Parser natToken boolToken manyAux)

def scan : List Nat → Nat → Nat → List Nat → Option (List Nat)
  | [], _, digits, acc => if digits=0 then some acc.reverse else none
  | b::bs, v, digits, acc =>
    if b=10 then
      if digits=0 then none else scan bs 0 0 (v::acc)
    else if 48≤b ∧ b≤57 then
      if digits>0 ∧ v=0 then none
      else scan bs (10*v+(b-48)) (digits+1) acc
    else none

def tokenize (bytes : List Nat) : Option (List Nat) :=
  scan bytes 0 0 []

def listToken {α : Type} (p : Parser α) : Parser (List α)
  | [] => none
  | k::ts => manyAux p k ts []

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


theorem scan_legacy_success (bytes : List Nat) (v k : Nat) (acc out : List Nat)
    (h : ProctorDataParser.scan bytes v k acc=some out) :
    scan bytes v k acc=some out := by
  induction bytes generalizing v k acc with
  | nil => exact h
  | cons b bs ih =>
    rw [ProctorDataParser.scan] at h
    rw [scan]
    by_cases sep : b=10
    · rw [if_pos sep] at h
      rw [if_pos sep]
      by_cases z : k=0
      · rw [if_pos z] at h
        cases h
      · rw [if_neg z] at h
        rw [if_neg z]
        exact ih 0 0 (v::acc) h
    · rw [if_neg sep] at h
      rw [if_neg sep]
      by_cases d : 48≤b ∧ b≤57
      · rw [if_pos d] at h
        rw [if_pos d]
        by_cases bad : k≥ProctorDataParser.digitLimit ∨ (k>0 ∧ v=0)
        · rw [if_pos bad] at h
          cases h
        · rw [if_neg bad] at h
          rw [if_neg (fun z => bad (Or.inr z))]
          exact ih (10*v+(b-48)) (k+1) acc h
      · rw [if_neg d] at h
        cases h

theorem tokenize_legacy_success (bytes ts : List Nat)
    (h : ProctorDataParser.tokenize bytes=some ts) :
    tokenize bytes=some ts := by
  unfold ProctorDataParser.tokenize at h
  by_cases hb : bytes.length≤ProctorDataParser.byteLimit
  · rw [if_pos hb] at h
    exact scan_legacy_success bytes 0 0 [] ts h
  · rw [if_neg hb] at h
    cases h

theorem bounded_expected_reject (a b : List Nat)
    (h : ProctorDataParser.byteLimit<a.length) :
    ProctorDataParser.checkBytes a b=false := by
  have ht : ProctorDataParser.tokenize a=none := by
    unfold ProctorDataParser.tokenize
    rw [if_neg (Nat.not_le_of_gt h)]
  unfold ProctorDataParser.checkBytes ProctorDataParser.decodeExpected ProctorDataParser.decode
  rw [ht]
  rfl

theorem bytes_sound (a b : List Nat) (h : checkBytes a b=true) :
    ∃ n f, decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  unfold checkBytes at h
  cases ha : decodeExpected a with
  | none => rw [ha] at h; cases h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [ha] at h
      cases hb : decodeEnvelope b with
      | none => rw [hb] at h; cases h
      | some e =>
        rw [hb] at h
        exact ⟨n,f,rfl,ProctorUnifiedReplay.bound_sound n f e h⟩

end ProctorUnboundedCodec

#print axioms ProctorUnboundedCodec.scan_legacy_success
#print axioms ProctorUnboundedCodec.tokenize_legacy_success
#print axioms ProctorUnboundedCodec.bounded_expected_reject
#print axioms ProctorUnboundedCodec.bytes_sound
