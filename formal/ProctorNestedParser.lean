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
  refine bind_congr (β := RefRow × List Nat) (natToken) (natToken)
    (fun i ts => do
      let (row,ts) ← (clause L) ts
      some (⟨i,row⟩,ts))
    (fun i ts => do
      let (row,ts) ← (ProctorDataParser.clauseToken) ts
      some (⟨i,row⟩,ts))
    ts (rfl) ?_
  intro i ts
  dsimp only
  rw [clause_refines L hL ts]

def group (L : ListBuilder) : Parser ProctorCapacityDeficiency.Group := fun ts => do
  let (vs,ts) ← (clause L) ts
  let (cap,ts) ← (natToken) ts
  some (⟨vs,cap⟩,ts)

theorem group_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    group L ts=ProctorDataParser.groupToken ts := by
  unfold group ProctorDataParser.groupToken
  refine bind_congr (β := ProctorCapacityDeficiency.Group × List Nat) (clause L) (ProctorDataParser.clauseToken)
    (fun vs ts => do
      let (cap,ts) ← (natToken) ts
      some (⟨vs,cap⟩,ts))
    (fun vs ts => do
      let (cap,ts) ← (natToken) ts
      some (⟨vs,cap⟩,ts))
    ts (clause_refines L hL ts) ?_
  intro vs ts
  rfl

def capacity (L : ListBuilder) : Parser Certificate := fun ts => do
  let (ds,ts) ← (L RefRow (ref L)) ts
  let (gs,ts) ← (L ProctorCapacityDeficiency.Group (group L)) ts
  let (rs,ts) ← (L RefRow (ref L)) ts
  some (⟨ds,gs,rs⟩,ts)

theorem capacity_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    capacity L ts=ProctorDataParser.capacityToken ts := by
  unfold capacity ProctorDataParser.capacityToken
  refine bind_congr (β := Certificate × List Nat) (L RefRow (ref L)) (listToken ProctorDataParser.refToken)
    (fun ds ts => do
      let (gs,ts) ← (L ProctorCapacityDeficiency.Group (group L)) ts
      let (rs,ts) ← (L RefRow (ref L)) ts
      some (⟨ds,gs,rs⟩,ts))
    (fun ds ts => do
      let (gs,ts) ← (listToken ProctorDataParser.groupToken) ts
      let (rs,ts) ← (listToken ProctorDataParser.refToken) ts
      some (⟨ds,gs,rs⟩,ts))
    ts (list_congr L hL _ _ (ref_refines L hL) ts) ?_
  intro ds ts
  refine bind_congr (β := Certificate × List Nat) (L ProctorCapacityDeficiency.Group (group L)) (listToken ProctorDataParser.groupToken)
    (fun gs ts => do
      let (rs,ts) ← (L RefRow (ref L)) ts
      some (⟨ds,gs,rs⟩,ts))
    (fun gs ts => do
      let (rs,ts) ← (listToken ProctorDataParser.refToken) ts
      some (⟨ds,gs,rs⟩,ts))
    ts (list_congr L hL _ _ (group_refines L hL) ts) ?_
  intro gs ts
  dsimp only
  rw [list_congr L hL _ _ (ref_refines L hL) ts]

def block (L : ListBuilder) : Parser ProctorXorReplay.Block := fun ts => do
  let (vs,ts) ← (L Nat natToken) ts
  let (rhs,ts) ← (boolToken) ts
  let (rs,ts) ← (L RefRow (ref L)) ts
  some (⟨vs,rhs,rs⟩,ts)

theorem block_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    block L ts=ProctorDataParser.blockToken ts := by
  unfold block ProctorDataParser.blockToken
  refine bind_congr (β := ProctorXorReplay.Block × List Nat) (L Nat natToken) (listToken natToken)
    (fun vs ts => do
      let (rhs,ts) ← (boolToken) ts
      let (rs,ts) ← (L RefRow (ref L)) ts
      some (⟨vs,rhs,rs⟩,ts))
    (fun vs ts => do
      let (rhs,ts) ← (boolToken) ts
      let (rs,ts) ← (listToken ProctorDataParser.refToken) ts
      some (⟨vs,rhs,rs⟩,ts))
    ts (hL Nat natToken ts) ?_
  intro vs ts
  refine bind_congr (β := ProctorXorReplay.Block × List Nat) (boolToken) (boolToken)
    (fun rhs ts => do
      let (rs,ts) ← (L RefRow (ref L)) ts
      some (⟨vs,rhs,rs⟩,ts))
    (fun rhs ts => do
      let (rs,ts) ← (listToken ProctorDataParser.refToken) ts
      some (⟨vs,rhs,rs⟩,ts))
    ts (rfl) ?_
  intro rhs ts
  dsimp only
  rw [list_congr L hL _ _ (ref_refines L hL) ts]

def step (L : ListBuilder) : Parser Step := fun ts => do
  let (a,ts) ← (natToken) ts
  let (b,ts) ← (natToken) ts
  let (p,ts) ← (natToken) ts
  let (tail,ts) ← (clause L) ts
  some (⟨a,b,p,tail⟩,ts)

theorem step_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    step L ts=ProctorDataParser.stepToken ts := by
  unfold step ProctorDataParser.stepToken
  refine bind_congr (β := Step × List Nat) (natToken) (natToken)
    (fun a ts => do
      let (b,ts) ← (natToken) ts
      let (p,ts) ← (natToken) ts
      let (tail,ts) ← (clause L) ts
      some (⟨a,b,p,tail⟩,ts))
    (fun a ts => do
      let (b,ts) ← (natToken) ts
      let (p,ts) ← (natToken) ts
      let (tail,ts) ← (ProctorDataParser.clauseToken) ts
      some (⟨a,b,p,tail⟩,ts))
    ts (rfl) ?_
  intro a ts
  refine bind_congr (β := Step × List Nat) (natToken) (natToken)
    (fun b ts => do
      let (p,ts) ← (natToken) ts
      let (tail,ts) ← (clause L) ts
      some (⟨a,b,p,tail⟩,ts))
    (fun b ts => do
      let (p,ts) ← (natToken) ts
      let (tail,ts) ← (ProctorDataParser.clauseToken) ts
      some (⟨a,b,p,tail⟩,ts))
    ts (rfl) ?_
  intro b ts
  refine bind_congr (β := Step × List Nat) (natToken) (natToken)
    (fun p ts => do
      let (tail,ts) ← (clause L) ts
      some (⟨a,b,p,tail⟩,ts))
    (fun p ts => do
      let (tail,ts) ← (ProctorDataParser.clauseToken) ts
      some (⟨a,b,p,tail⟩,ts))
    ts (rfl) ?_
  intro p ts
  dsimp only
  rw [clause_refines L hL ts]

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
  refine bind_congr (β := Terminal × List Nat) natToken natToken
    (fun tag ts =>
      if tag=0 then some (.empty,ts)
      else if tag=1 then do
        let (c,ts) ← capacity L ts
        some (.capacity c,ts)
      else if tag=2 then do
        let (bs,ts) ← L ProctorXorReplay.Block (block L) ts
        some (.xor bs,ts)
      else none)
    (fun tag ts =>
      if tag=0 then some (.empty,ts)
      else if tag=1 then do
        let (c,ts) ← ProctorDataParser.capacityToken ts
        some (.capacity c,ts)
      else if tag=2 then do
        let (bs,ts) ← listToken ProctorDataParser.blockToken ts
        some (.xor bs,ts)
      else none)
    ts rfl ?_
  intro tag ts
  dsimp only
  by_cases h0 : tag=0
  · rw [if_pos h0] <;> try rw [if_pos h0]
  · rw [if_neg h0] <;> try rw [if_neg h0]
    by_cases h1 : tag=1
    · rw [if_pos h1] <;> try rw [if_pos h1]
      rw [capacity_refines L hL ts]
    · rw [if_neg h1] <;> try rw [if_neg h1]
      by_cases h2 : tag=2
      · rw [if_pos h2] <;> try rw [if_pos h2]
        rw [list_congr L hL _ _ (block_refines L hL) ts]
      · rw [if_neg h2] <;> try rw [if_neg h2]

def proof (L : ListBuilder) : Parser Proof := fun ts => do
  let (bs,ts) ← (L (List Step) (L Step (step L))) ts
  let (aug,ts) ← (boolToken) ts
  let (t,ts) ← (terminal L) ts
  some (⟨bs,aug,t⟩,ts)

theorem proof_refines (L : ListBuilder) (hL : ListContract L) (ts : List Nat) :
    proof L ts=ProctorDataParser.proofToken ts := by
  unfold proof ProctorDataParser.proofToken
  refine bind_congr (β := Proof × List Nat) (L (List Step) (L Step (step L))) (listToken (listToken ProctorDataParser.stepToken))
    (fun bs ts => do
      let (aug,ts) ← (boolToken) ts
      let (t,ts) ← (terminal L) ts
      some (⟨bs,aug,t⟩,ts))
    (fun bs ts => do
      let (aug,ts) ← (boolToken) ts
      let (t,ts) ← (ProctorDataParser.terminalToken) ts
      some (⟨bs,aug,t⟩,ts))
    ts (list_congr L hL _ _ (fun xs => list_congr L hL _ _ (step_refines L hL) xs) ts) ?_
  intro bs ts
  refine bind_congr (β := Proof × List Nat) (boolToken) (boolToken)
    (fun aug ts => do
      let (t,ts) ← (terminal L) ts
      some (⟨bs,aug,t⟩,ts))
    (fun aug ts => do
      let (t,ts) ← (ProctorDataParser.terminalToken) ts
      some (⟨bs,aug,t⟩,ts))
    ts (rfl) ?_
  intro aug ts
  dsimp only
  rw [terminal_refines L hL ts]

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
  refine bind_congr (β := (Nat × Formula) × List Nat) natToken natToken
    (fun magic ts =>
      if magic=3401 then do
        let (n,ts) ← (natToken) ts
        let (f,ts) ← (formula L) ts
        some ((n,f),ts)
      else none)
    (fun magic ts =>
      if magic=3401 then do
        let (n,ts) ← (natToken) ts
        let (f,ts) ← (ProctorDataParser.formulaToken) ts
        some ((n,f),ts)
      else none)
    ts rfl ?_
  intro magic ts
  dsimp only
  by_cases h : magic=3401
  · rw [if_pos h] <;> try rw [if_pos h]
    refine bind_congr (β := (Nat × Formula) × List Nat) (natToken) (natToken)
      (fun n ts => do
        let (f,ts) ← (formula L) ts
        some ((n,f),ts))
      (fun n ts => do
        let (f,ts) ← (ProctorDataParser.formulaToken) ts
        some ((n,f),ts))
      ts (rfl) ?_
    intro n ts
    dsimp only
    rw [formula_refines L hL ts]
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
  refine bind_congr (β := Envelope × List Nat) natToken natToken
    (fun magic ts =>
      if magic=3402 then do
        let (n,ts) ← (natToken) ts
        let (f,ts) ← (formula L) ts
        let (p,ts) ← (proof L) ts
        some (⟨n,f,p⟩,ts)
      else none)
    (fun magic ts =>
      if magic=3402 then do
        let (n,ts) ← (natToken) ts
        let (f,ts) ← (ProctorDataParser.formulaToken) ts
        let (p,ts) ← (ProctorDataParser.proofToken) ts
        some (⟨n,f,p⟩,ts)
      else none)
    ts rfl ?_
  intro magic ts
  dsimp only
  by_cases h : magic=3402
  · rw [if_pos h] <;> try rw [if_pos h]
    refine bind_congr (β := Envelope × List Nat) (natToken) (natToken)
      (fun n ts => do
        let (f,ts) ← (formula L) ts
        let (p,ts) ← (proof L) ts
        some (⟨n,f,p⟩,ts))
      (fun n ts => do
        let (f,ts) ← (ProctorDataParser.formulaToken) ts
        let (p,ts) ← (ProctorDataParser.proofToken) ts
        some (⟨n,f,p⟩,ts))
      ts (rfl) ?_
    intro n ts
    refine bind_congr (β := Envelope × List Nat) (formula L) (ProctorDataParser.formulaToken)
      (fun f ts => do
        let (p,ts) ← (proof L) ts
        some (⟨n,f,p⟩,ts))
      (fun f ts => do
        let (p,ts) ← (ProctorDataParser.proofToken) ts
        some (⟨n,f,p⟩,ts))
      ts (formula_refines L hL ts) ?_
    intro f ts
    dsimp only
    rw [proof_refines L hL ts]
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
