/-! F034 candidate: pointwise nested certificate parser substitution.
Abstract the list implementation, specialize to the verified checked
17-bit list parser, and compose the verified binary tokenizer.
The concrete list implementation retains explicit Nat structural fuel.
The original checker remains unchanged. -/
namespace ProctorNestedParser
open ProctorHallDeficiency
open ProctorDataParser (Parser natToken boolToken literalToken manyAux listToken listLimit)
open ProctorExecutableReplay (Step)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Proof Terminal Envelope boundCheck)

abbrev ListBuilder := (α : Type) → Parser α → Parser (List α)
def ListContract (L : ListBuilder) : Prop :=
  ∀ (α : Type) (p : Parser α) (ts : List Nat), L α p ts=listToken p ts

private theorem many_congr {α : Type} (p q : Parser α)
    (h : ∀ ts, p ts=q ts) (k : Nat) (ts : List Nat) (acc : List α) :
    manyAux p k ts acc=manyAux q k ts acc := by
  induction k generalizing ts acc with
  | zero => rfl
  | succ k ih =>
    change (do
      let (a,rest) ← p ts
      manyAux p k rest (a::acc))=(do
      let (a,rest) ← q ts
      manyAux q k rest (a::acc))
    rw [h ts]
    cases e : q ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => exact ih rest (a::acc)

theorem list_congr (L : ListBuilder) (hL : ListContract L)
    {α : Type} (p q : Parser α) (h : ∀ ts, p ts=q ts) (ts : List Nat) :
    L α p ts=listToken q ts := by
  rw [hL α p ts]
  cases ts with
  | nil => rfl
  | cons k xs =>
    change (if k≤listLimit then manyAux p k xs [] else none)=
      (if k≤listLimit then manyAux q k xs [] else none)
    rw [many_congr p q h k xs []]

private theorem bind_congr {α β : Type} (p q : Parser α)
    (f g : α → List Nat → Option β) (ts : List Nat)
    (hp : p ts=q ts) (hf : ∀ a rest, f a rest=g a rest) :
    (do
      let (a,rest) ← p ts
      f a rest)=(do
      let (a,rest) ← q ts
      g a rest) := by
  rw [hp]
  cases e : q ts with
  | none => rfl
  | some pair =>
    cases pair with
    | mk a rest => exact hf a rest

def clause (L : ListBuilder) : Parser Clause := L Literal literalToken
def formula (L : ListBuilder) : Parser Formula := L Clause (clause L)

theorem clause_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    clause L ts=ProctorDataParser.clauseToken ts := hL Literal literalToken ts

theorem formula_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    formula L ts=ProctorDataParser.formulaToken ts :=
  list_congr L hL _ _ (clause_refines L hL) ts

def ref (L : ListBuilder) : Parser RefRow := fun ts => do
  let (i,ts) ← (natToken) ts
  let (row,ts) ← (clause L) ts
  some (⟨i,row⟩,ts)

theorem ref_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    ref L ts=ProctorDataParser.refToken ts := by
  unfold ref ProctorDataParser.refToken
  apply bind_congr
  · exact rfl
  · intro i ts
    apply bind_congr
    · exact clause_refines L hL _
    · intro row ts
      rfl

def group (L : ListBuilder) : Parser ProctorCapacityDeficiency.Group := fun ts => do
  let (vs,ts) ← (clause L) ts
  let (cap,ts) ← (natToken) ts
  some (⟨vs,cap⟩,ts)

theorem group_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    group L ts=ProctorDataParser.groupToken ts := by
  unfold group ProctorDataParser.groupToken
  apply bind_congr
  · exact clause_refines L hL _
  · intro vs ts
    apply bind_congr
    · exact rfl
    · intro cap ts
      rfl

def capacity (L : ListBuilder) : Parser Certificate := fun ts => do
  let (ds,ts) ← (L RefRow (ref L)) ts
  let (gs,ts) ← (L ProctorCapacityDeficiency.Group (group L)) ts
  let (rs,ts) ← (L RefRow (ref L)) ts
  some (⟨ds,gs,rs⟩,ts)

theorem capacity_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    capacity L ts=ProctorDataParser.capacityToken ts := by
  unfold capacity ProctorDataParser.capacityToken
  apply bind_congr
  · exact list_congr L hL _ _ (ref_refines L hL) _
  · intro ds ts
    apply bind_congr
    · exact list_congr L hL _ _ (group_refines L hL) _
    · intro gs ts
      apply bind_congr
      · exact list_congr L hL _ _ (ref_refines L hL) _
      · intro rs ts
        rfl

def block (L : ListBuilder) : Parser ProctorXorReplay.Block := fun ts => do
  let (vs,ts) ← (L Nat natToken) ts
  let (rhs,ts) ← (boolToken) ts
  let (rs,ts) ← (L RefRow (ref L)) ts
  some (⟨vs,rhs,rs⟩,ts)

theorem block_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    block L ts=ProctorDataParser.blockToken ts := by
  unfold block ProctorDataParser.blockToken
  apply bind_congr
  · exact hL Nat natToken _
  · intro vs ts
    apply bind_congr
    · exact rfl
    · intro rhs ts
      apply bind_congr
      · exact list_congr L hL _ _ (ref_refines L hL) _
      · intro rs ts
        rfl

def step (L : ListBuilder) : Parser Step := fun ts => do
  let (a,ts) ← (natToken) ts
  let (b,ts) ← (natToken) ts
  let (p,ts) ← (natToken) ts
  let (tail,ts) ← (clause L) ts
  some (⟨a,b,p,tail⟩,ts)

theorem step_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    step L ts=ProctorDataParser.stepToken ts := by
  unfold step ProctorDataParser.stepToken
  apply bind_congr
  · exact rfl
  · intro a ts
    apply bind_congr
    · exact rfl
    · intro b ts
      apply bind_congr
      · exact rfl
      · intro p ts
        apply bind_congr
        · exact clause_refines L hL _
        · intro tail ts
          rfl

def terminal (L : ListBuilder) : Parser Terminal := fun ts => do
  let (tag,ts) ← natToken ts
  if tag=0 then some (.empty,ts)
  else if tag=1 then do
    let (c,ts) ← capacity L ts
    some (.capacity c,ts)
  else if tag=2 then do
    let (bs,ts) ← L ProctorXorReplay.Block (block L) ts
    some (.xor bs,ts)
  else none

theorem terminal_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    terminal L ts=ProctorDataParser.terminalToken ts := by
  unfold terminal ProctorDataParser.terminalToken
  apply bind_congr
  · rfl
  · intro tag ts
    by_cases h0 : tag=0
    · rw [if_pos h0] <;> try rw [if_pos h0]
    · rw [if_neg h0] <;> try rw [if_neg h0]
      by_cases h1 : tag=1
      · rw [if_pos h1] <;> try rw [if_pos h1]
        apply bind_congr
        · exact capacity_refines L hL _
        · intro c rest; rfl
      · rw [if_neg h1] <;> try rw [if_neg h1]
        by_cases h2 : tag=2
        · rw [if_pos h2] <;> try rw [if_pos h2]
          apply bind_congr
          · exact list_congr L hL _ _ (block_refines L hL) _
          · intro bs rest; rfl
        · rw [if_neg h2] <;> try rw [if_neg h2]

def proof (L : ListBuilder) : Parser Proof := fun ts => do
  let (bs,ts) ← (L (List Step) (L Step (step L))) ts
  let (aug,ts) ← (boolToken) ts
  let (t,ts) ← (terminal L) ts
  some (⟨bs,aug,t⟩,ts)

theorem proof_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    proof L ts=ProctorDataParser.proofToken ts := by
  unfold proof ProctorDataParser.proofToken
  apply bind_congr
  · exact list_congr L hL _ _ (fun xs => list_congr L hL _ _ (step_refines L hL) xs) _
  · intro bs ts
    apply bind_congr
    · exact rfl
    · intro aug ts
      apply bind_congr
      · exact terminal_refines L hL _
      · intro t ts
        rfl

def expected (L : ListBuilder) : Parser (Nat × Formula) := fun ts => do
  let (magic,ts) ← natToken ts
  if magic=3401 then do
    let (n,ts) ← natToken ts
    let (f,ts) ← formula L ts
    some ((n,f),ts)
  else none

theorem expected_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    expected L ts=ProctorDataParser.expectedToken ts := by
  unfold expected ProctorDataParser.expectedToken
  apply bind_congr
  · rfl
  · intro magic ts
    by_cases h : magic=3401
    · rw [if_pos h] <;> try rw [if_pos h]
      apply bind_congr
      · rfl
      · intro n rest
        apply bind_congr
        · exact formula_refines L hL _
        · intro f tail; rfl
    · rw [if_neg h] <;> try rw [if_neg h]

def envelope (L : ListBuilder) : Parser Envelope := fun ts => do
  let (magic,ts) ← natToken ts
  if magic=3402 then do
    let (n,ts) ← natToken ts
    let (f,ts) ← formula L ts
    let (p,ts) ← proof L ts
    some (⟨n,f,p⟩,ts)
  else none

theorem envelope_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    envelope L ts=ProctorDataParser.envelopeToken ts := by
  unfold envelope ProctorDataParser.envelopeToken
  apply bind_congr
  · rfl
  · intro magic ts
    by_cases h : magic=3402
    · rw [if_pos h] <;> try rw [if_pos h]
      apply bind_congr
      · rfl
      · intro n rest
        apply bind_congr
        · exact formula_refines L hL _
        · intro f tail
          apply bind_congr
          · exact proof_refines L hL _
          · intro p endTokens; rfl
    · rw [if_neg h] <;> try rw [if_neg h]

def checkedLists : ListBuilder := fun _ p => ProctorParserCounters.listBits p

theorem checked_contract : ListContract checkedLists :=
  fun _ p ts => ProctorParserCounters.list_refines p ts

def decode {α : Type} (p : Parser α) (bytes : List Nat) : Option α := do
  let ts ← ProctorBytePrepass.tokenizeBounded bytes
  let (a,rest) ← p ts
  match rest with
  | [] => some a
  | _::_ => none

theorem decode_refines {α : Type} (p q : Parser α) (h : ∀ ts, p ts=q ts)
    (bytes : List Nat) : decode p bytes=ProctorDataParser.decode q bytes := by
  unfold decode ProctorDataParser.decode
  rw [ProctorBytePrepass.tokenize_refines bytes]
  cases ProctorDataParser.tokenize bytes with
  | none => rfl
  | some ts =>
    change (do
      let (a,rest) ← p ts
      match rest with
      | [] => some a
      | _::_ => none)=(do
      let (a,rest) ← q ts
      match rest with
      | [] => some a
      | _::_ => none)
    rw [h ts]

def decodeExpected := decode (expected checkedLists)
def decodeEnvelope := decode (envelope checkedLists)

theorem expected_bytes_refines (bytes : List Nat) :
    decodeExpected bytes=ProctorDataParser.decodeExpected bytes :=
  decode_refines _ _ (expected_refines checkedLists checked_contract) bytes

theorem envelope_bytes_refines (bytes : List Nat) :
    decodeEnvelope bytes=ProctorDataParser.decodeEnvelope bytes :=
  decode_refines _ _ (envelope_refines checkedLists checked_contract) bytes

def checkBytes (expectedBytes proofBytes : List Nat) : Bool :=
  match decodeExpected expectedBytes,decodeEnvelope proofBytes with
  | some (n,f),some e => boundCheck n f e
  | _,_ => false

theorem check_refines (expectedBytes proofBytes : List Nat) :
    checkBytes expectedBytes proofBytes=ProctorDataParser.checkBytes expectedBytes proofBytes := by
  unfold checkBytes ProctorDataParser.checkBytes
  rw [expected_bytes_refines,envelope_bytes_refines]

theorem check_sound (expectedBytes proofBytes : List Nat)
    (h : checkBytes expectedBytes proofBytes=true) :
    ∃ n f, ProctorDataParser.decodeExpected expectedBytes=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [check_refines] at h
  exact ProctorDataParser.accepted_unsat expectedBytes proofBytes h

end ProctorNestedParser

#print axioms ProctorNestedParser.list_congr
#print axioms ProctorNestedParser.clause_refines
#print axioms ProctorNestedParser.formula_refines
#print axioms ProctorNestedParser.ref_refines
#print axioms ProctorNestedParser.group_refines
#print axioms ProctorNestedParser.capacity_refines
#print axioms ProctorNestedParser.block_refines
#print axioms ProctorNestedParser.step_refines
#print axioms ProctorNestedParser.terminal_refines
#print axioms ProctorNestedParser.proof_refines
#print axioms ProctorNestedParser.expected_refines
#print axioms ProctorNestedParser.envelope_refines
#print axioms ProctorNestedParser.checked_contract
#print axioms ProctorNestedParser.decode_refines
#print axioms ProctorNestedParser.expected_bytes_refines
#print axioms ProctorNestedParser.envelope_bytes_refines
#print axioms ProctorNestedParser.check_refines
#print axioms ProctorNestedParser.check_sound
