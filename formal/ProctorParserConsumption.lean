/-! F034: successful parser consumption and raw custom-data byte bound.
No changes to the executable checker. -/
namespace ProctorParserConsumption
open ProctorHallDeficiency
open ProctorDataParser
open ProctorWireRoundtrip
open ProctorEnvelopeRoundtrip
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorEncodedSize (size cap globalUnit global_meter)
open ProctorTerminalPolynomial (mul_mono)

def Consumes {α : Type} (p : Parser α) (enc : α → List Nat) : Prop :=
  ∀ ts a rest, p ts=some (a,rest) → ts=enc a++rest

private theorem append_assoc_local {α : Type} (a b c : List α) :
    (a++b)++c=a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_nil_local {α : Type} (a : List α) :
    a++[]=a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem reverseAux_append_local {α : Type} (a b c : List α) :
    a.reverseAux (b++c)=a.reverseAux b++c := by
  induction a generalizing b with
  | nil => rfl
  | cons x xs ih => exact ih (x::b)

private theorem reverse_cons_local {α : Type} (x : α) (xs : List α) :
    (x::xs).reverse=xs.reverse++[x] :=
  reverseAux_append_local xs [] [x]

private theorem len_append {α : Type} (a b : List α) :
    (a++b).length=a.length+b.length := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++b).length+1=(xs.length+1)+b.length
    rw [ih]
    calc
      (xs.length+b.length)+1 = xs.length+(b.length+1) := Nat.add_assoc _ _ _
      _ = xs.length+(1+b.length) := congrArg (fun z => xs.length+z) (Nat.add_comm _ _)
      _ = (xs.length+1)+b.length := (Nat.add_assoc _ _ _).symm

private theorem bind_success {α β : Type} (p : Parser α)
    (q : α → List Nat → Option β) (ts : List Nat) (out : β)
    (h : (do
      let (a,rest) ← p ts
      q a rest)=some out) :
    ∃ a rest, p ts=some (a,rest) ∧ q a rest=some out := by
  cases e : p ts with
  | none =>
    rw [e] at h
    cases h
  | some pair =>
    cases pair with
    | mk a rest =>
      rw [e] at h
      exact ⟨a,rest,rfl,h⟩

theorem nat_converse : Consumes natToken encNat := by
  intro ts a rest h
  cases ts with
  | nil => cases h
  | cons v vs =>
    change some (v,vs)=some (a,rest) at h
    cases h
    rfl

theorem bool_converse : Consumes boolToken encBool := by
  intro ts a rest h
  cases ts with
  | nil => cases h
  | cons v vs =>
    change (if v=0 then some (false,vs)
      else if v=1 then some (true,vs) else none)=some (a,rest) at h
    by_cases z : v=0
    · cases z
      rw [if_pos rfl] at h
      cases h
      rfl
    · rw [if_neg z] at h
      by_cases o : v=1
      · cases o
        rw [if_pos rfl] at h
        cases h
        rfl
      · rw [if_neg o] at h
        cases h

theorem many_converse {α : Type} (p : Parser α) (enc : α → List Nat)
    (hc : Consumes p enc) (k : Nat) (ts : List Nat) (acc out : List α)
    (rest : List Nat) (h : manyAux p k ts acc=some (out,rest)) :
    ∃ xs : List α, xs.length=k ∧ out=acc.reverse++xs ∧
      ts=encItems enc xs++rest := by
  induction k generalizing ts acc out rest with
  | zero =>
    change some (acc.reverse,ts)=some (out,rest) at h
    cases h
    exact ⟨[],rfl,(append_nil_local _).symm,rfl⟩
  | succ k ih =>
    change (do
      let (a,next) ← p ts
      manyAux p k next (a::acc))=some (out,rest) at h
    obtain ⟨a,next,ha,hr⟩ := bind_success p
      (fun a next => manyAux p k next (a::acc)) ts (out,rest) h
    obtain ⟨xs,hl,ho,ht⟩ := ih next (a::acc) out rest hr
    refine ⟨a::xs,congrArg Nat.succ hl,?_,?_⟩
    · rw [ho,reverse_cons_local,append_assoc_local] <;> rfl
    · rw [hc ts a next ha,ht]
      change enc a++(encItems enc xs++rest)=(enc a++encItems enc xs)++rest
      exact (append_assoc_local _ _ _).symm

theorem list_converse {α : Type} (p : Parser α) (enc : α → List Nat)
    (hc : Consumes p enc) : Consumes (listToken p) (encList enc) := by
  intro ts out rest h
  cases ts with
  | nil => cases h
  | cons k vs =>
    change (if k≤listLimit then manyAux p k vs [] else none)=some (out,rest) at h
    by_cases size : k≤listLimit
    · rw [if_pos size] at h
      obtain ⟨xs,hl,ho,ht⟩ := many_converse p enc hc k vs [] out rest h
      change out=xs at ho
      have exactInput : k::vs=xs.length::(encItems enc xs++rest) := by
        rw [hl,ht]
      cases ho
      exact exactInput
    · rw [if_neg size] at h
      cases h

theorem literal_converse : Consumes literalToken encLiteral := by
  intro input out rest h
  unfold literalToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success natToken
    (fun v0 t0 => do
      let (v1,t1) ← boolToken t0
      some ((v0,v1),t1)) input (out,rest) h
  have c0 := nat_converse input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success boolToken
    (fun v1 t1 => do
      some ((v0,v1),t1)) t0 (out,rest) next0
  have c1 := bool_converse t0 v1 t1 h1
  have exactInput : input = encLiteral ((v0,v1)) ++ t1 := by
    calc
      input = encNat v0 ++ (encBool v1 ++ (t1)) := by rw [c0,c1]
      _ = encLiteral ((v0,v1)) ++ t1 := by
        unfold encLiteral
        repeat rw [append_assoc_local]
        all_goals rfl
  change some ((v0,v1),t1)=some (out,rest) at next1
  cases next1
  exact exactInput

theorem clause_converse : Consumes clauseToken encClause :=
  list_converse literalToken encLiteral literal_converse

theorem formula_converse : Consumes formulaToken encFormula :=
  list_converse clauseToken encClause clause_converse

theorem ref_converse : Consumes refToken encRef := by
  intro input out rest h
  unfold refToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success natToken
    (fun v0 t0 => do
      let (v1,t1) ← clauseToken t0
      some (RefRow.mk v0 v1,t1)) input (out,rest) h
  have c0 := nat_converse input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success clauseToken
    (fun v1 t1 => do
      some (RefRow.mk v0 v1,t1)) t0 (out,rest) next0
  have c1 := clause_converse t0 v1 t1 h1
  have exactInput : input = encRef (RefRow.mk v0 v1) ++ t1 := by
    calc
      input = encNat v0 ++ (encClause v1 ++ (t1)) := by rw [c0,c1]
      _ = encRef (RefRow.mk v0 v1) ++ t1 := by
        unfold encRef
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (RefRow.mk v0 v1,t1)=some (out,rest) at next1
  cases next1
  exact exactInput
theorem group_converse : Consumes groupToken encGroup := by
  intro input out rest h
  unfold groupToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success clauseToken
    (fun v0 t0 => do
      let (v1,t1) ← natToken t0
      some (Group.mk v0 v1,t1)) input (out,rest) h
  have c0 := clause_converse input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success natToken
    (fun v1 t1 => do
      some (Group.mk v0 v1,t1)) t0 (out,rest) next0
  have c1 := nat_converse t0 v1 t1 h1
  have exactInput : input = encGroup (Group.mk v0 v1) ++ t1 := by
    calc
      input = encClause v0 ++ (encNat v1 ++ (t1)) := by rw [c0,c1]
      _ = encGroup (Group.mk v0 v1) ++ t1 := by
        unfold encGroup
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (Group.mk v0 v1,t1)=some (out,rest) at next1
  cases next1
  exact exactInput
theorem capacity_converse : Consumes capacityToken encCapacity := by
  intro input out rest h
  unfold capacityToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success (listToken refToken)
    (fun v0 t0 => do
      let (v1,t1) ← (listToken groupToken) t0
      let (v2,t2) ← (listToken refToken) t1
      some (Certificate.mk v0 v1 v2,t2)) input (out,rest) h
  have c0 := (list_converse refToken encRef ref_converse) input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success (listToken groupToken)
    (fun v1 t1 => do
      let (v2,t2) ← (listToken refToken) t1
      some (Certificate.mk v0 v1 v2,t2)) t0 (out,rest) next0
  have c1 := (list_converse groupToken encGroup group_converse) t0 v1 t1 h1
  obtain ⟨v2,t2,h2,next2⟩ := bind_success (listToken refToken)
    (fun v2 t2 => do
      some (Certificate.mk v0 v1 v2,t2)) t1 (out,rest) next1
  have c2 := (list_converse refToken encRef ref_converse) t1 v2 t2 h2
  have exactInput : input = encCapacity (Certificate.mk v0 v1 v2) ++ t2 := by
    calc
      input = (encList encRef) v0 ++ ((encList encGroup) v1 ++ ((encList encRef) v2 ++ (t2))) := by rw [c0,c1,c2]
      _ = encCapacity (Certificate.mk v0 v1 v2) ++ t2 := by
        unfold encCapacity
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (Certificate.mk v0 v1 v2,t2)=some (out,rest) at next2
  cases next2
  exact exactInput
theorem block_converse : Consumes blockToken encBlock := by
  intro input out rest h
  unfold blockToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success (listToken natToken)
    (fun v0 t0 => do
      let (v1,t1) ← boolToken t0
      let (v2,t2) ← (listToken refToken) t1
      some (Block.mk v0 v1 v2,t2)) input (out,rest) h
  have c0 := (list_converse natToken encNat nat_converse) input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success boolToken
    (fun v1 t1 => do
      let (v2,t2) ← (listToken refToken) t1
      some (Block.mk v0 v1 v2,t2)) t0 (out,rest) next0
  have c1 := bool_converse t0 v1 t1 h1
  obtain ⟨v2,t2,h2,next2⟩ := bind_success (listToken refToken)
    (fun v2 t2 => do
      some (Block.mk v0 v1 v2,t2)) t1 (out,rest) next1
  have c2 := (list_converse refToken encRef ref_converse) t1 v2 t2 h2
  have exactInput : input = encBlock (Block.mk v0 v1 v2) ++ t2 := by
    calc
      input = (encList encNat) v0 ++ (encBool v1 ++ ((encList encRef) v2 ++ (t2))) := by rw [c0,c1,c2]
      _ = encBlock (Block.mk v0 v1 v2) ++ t2 := by
        unfold encBlock
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (Block.mk v0 v1 v2,t2)=some (out,rest) at next2
  cases next2
  exact exactInput
theorem step_converse : Consumes stepToken encStep := by
  intro input out rest h
  unfold stepToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success natToken
    (fun v0 t0 => do
      let (v1,t1) ← natToken t0
      let (v2,t2) ← natToken t1
      let (v3,t3) ← clauseToken t2
      some (Step.mk v0 v1 v2 v3,t3)) input (out,rest) h
  have c0 := nat_converse input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success natToken
    (fun v1 t1 => do
      let (v2,t2) ← natToken t1
      let (v3,t3) ← clauseToken t2
      some (Step.mk v0 v1 v2 v3,t3)) t0 (out,rest) next0
  have c1 := nat_converse t0 v1 t1 h1
  obtain ⟨v2,t2,h2,next2⟩ := bind_success natToken
    (fun v2 t2 => do
      let (v3,t3) ← clauseToken t2
      some (Step.mk v0 v1 v2 v3,t3)) t1 (out,rest) next1
  have c2 := nat_converse t1 v2 t2 h2
  obtain ⟨v3,t3,h3,next3⟩ := bind_success clauseToken
    (fun v3 t3 => do
      some (Step.mk v0 v1 v2 v3,t3)) t2 (out,rest) next2
  have c3 := clause_converse t2 v3 t3 h3
  have exactInput : input = encStep (Step.mk v0 v1 v2 v3) ++ t3 := by
    calc
      input = encNat v0 ++ (encNat v1 ++ (encNat v2 ++ (encClause v3 ++ (t3)))) := by rw [c0,c1,c2,c3]
      _ = encStep (Step.mk v0 v1 v2 v3) ++ t3 := by
        unfold encStep
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (Step.mk v0 v1 v2 v3,t3)=some (out,rest) at next3
  cases next3
  exact exactInput

theorem terminal_converse : Consumes terminalToken encTerminal := by
  intro input out rest h
  cases input with
  | nil => cases h
  | cons tag ts =>
    change (if tag=0 then some (Terminal.empty,ts)
      else if tag=1 then (do
        let (c,next) ← capacityToken ts
        some (Terminal.capacity c,next))
      else if tag=2 then (do
        let (bs,next) ← listToken blockToken ts
        some (Terminal.xor bs,next))
      else none)=some (out,rest) at h
    by_cases z : tag=0
    · cases z
      rw [if_pos rfl] at h
      cases h
      rfl
    · rw [if_neg z] at h
      by_cases o : tag=1
      · cases o
        rw [if_pos rfl] at h
        obtain ⟨c,next,hc,hr⟩ := bind_success capacityToken
          (fun c next => some (Terminal.capacity c,next)) ts (out,rest) h
        have eq : 1::ts=encTerminal (.capacity c)++next :=
          congrArg (List.cons 1) (capacity_converse ts c next hc)
        cases hr
        exact eq
      · rw [if_neg o] at h
        by_cases two : tag=2
        · cases two
          rw [if_pos rfl] at h
          obtain ⟨bs,next,hb,hr⟩ := bind_success (listToken blockToken)
            (fun bs next => some (Terminal.xor bs,next)) ts (out,rest) h
          have eq : 2::ts=encTerminal (.xor bs)++next :=
            congrArg (List.cons 2) (list_converse blockToken encBlock block_converse ts bs next hb)
          cases hr
          exact eq
        · rw [if_neg two] at h
          cases h

theorem proof_converse : Consumes proofToken encProof := by
  intro input out rest h
  unfold proofToken at h
  obtain ⟨v0,t0,h0,next0⟩ := bind_success (listToken (listToken stepToken))
    (fun v0 t0 => do
      let (v1,t1) ← boolToken t0
      let (v2,t2) ← terminalToken t1
      some (Proof.mk v0 v1 v2,t2)) input (out,rest) h
  have c0 := (list_converse (listToken stepToken) encBatch (list_converse stepToken encStep step_converse)) input v0 t0 h0
  obtain ⟨v1,t1,h1,next1⟩ := bind_success boolToken
    (fun v1 t1 => do
      let (v2,t2) ← terminalToken t1
      some (Proof.mk v0 v1 v2,t2)) t0 (out,rest) next0
  have c1 := bool_converse t0 v1 t1 h1
  obtain ⟨v2,t2,h2,next2⟩ := bind_success terminalToken
    (fun v2 t2 => do
      some (Proof.mk v0 v1 v2,t2)) t1 (out,rest) next1
  have c2 := terminal_converse t1 v2 t2 h2
  have exactInput : input = encProof (Proof.mk v0 v1 v2) ++ t2 := by
    calc
      input = (encList encBatch) v0 ++ (encBool v1 ++ (encTerminal v2 ++ (t2))) := by rw [c0,c1,c2]
      _ = encProof (Proof.mk v0 v1 v2) ++ t2 := by
        unfold encProof
        repeat rw [append_assoc_local]
        all_goals rfl
  change some (Proof.mk v0 v1 v2,t2)=some (out,rest) at next2
  cases next2
  exact exactInput

theorem expected_converse : Consumes expectedToken (fun nf => encExpected nf.1 nf.2) := by
  intro input out rest h
  cases input with
  | nil => cases h
  | cons tag ts =>
    change (if tag=3401 then (do
      let (v0,t0) ← natToken ts
      let (v1,t1) ← formulaToken t0
      some ((v0,v1),t1)) else none)=some (out,rest) at h
    by_cases e : tag=3401
    · cases e
      rw [if_pos rfl] at h
      obtain ⟨v0,t0,h0,next0⟩ := bind_success natToken
        (fun v0 t0 => do
          let (v1,t1) ← formulaToken t0
          some ((v0,v1),t1)) ts (out,rest) h
      have c0 := nat_converse ts v0 t0 h0
      obtain ⟨v1,t1,h1,next1⟩ := bind_success formulaToken
        (fun v1 t1 => do
          some ((v0,v1),t1)) t0 (out,rest) next0
      have c1 := formula_converse t0 v1 t1 h1
      have exactInput : 3401::ts = encExpected v0 v1 ++ t1 := by
        calc
          3401::ts = 3401::(encNat v0 ++ (encFormula v1 ++ (t1))) := by rw [c0,c1]
          _ = encExpected v0 v1 ++ t1 := by
            unfold encExpected
            repeat rw [append_assoc_local]
            all_goals rfl
      change some ((v0,v1),t1)=some (out,rest) at next1
      cases next1
      exact exactInput
    · rw [if_neg e] at h
      cases h

theorem envelope_converse : Consumes envelopeToken encEnvelope := by
  intro input out rest h
  cases input with
  | nil => cases h
  | cons tag ts =>
    change (if tag=3402 then (do
      let (v0,t0) ← natToken ts
      let (v1,t1) ← formulaToken t0
      let (v2,t2) ← proofToken t1
      some (Envelope.mk v0 v1 v2,t2)) else none)=some (out,rest) at h
    by_cases e : tag=3402
    · cases e
      rw [if_pos rfl] at h
      obtain ⟨v0,t0,h0,next0⟩ := bind_success natToken
        (fun v0 t0 => do
          let (v1,t1) ← formulaToken t0
          let (v2,t2) ← proofToken t1
          some (Envelope.mk v0 v1 v2,t2)) ts (out,rest) h
      have c0 := nat_converse ts v0 t0 h0
      obtain ⟨v1,t1,h1,next1⟩ := bind_success formulaToken
        (fun v1 t1 => do
          let (v2,t2) ← proofToken t1
          some (Envelope.mk v0 v1 v2,t2)) t0 (out,rest) next0
      have c1 := formula_converse t0 v1 t1 h1
      obtain ⟨v2,t2,h2,next2⟩ := bind_success proofToken
        (fun v2 t2 => do
          some (Envelope.mk v0 v1 v2,t2)) t1 (out,rest) next1
      have c2 := proof_converse t1 v2 t2 h2
      have exactInput : 3402::ts = encEnvelope (Envelope.mk v0 v1 v2) ++ t2 := by
        calc
          3402::ts = 3402::(encNat v0 ++ (encFormula v1 ++ (encProof v2 ++ (t2)))) := by rw [c0,c1,c2]
          _ = encEnvelope (Envelope.mk v0 v1 v2) ++ t2 := by
            change 3402::v0::(encFormula v1++(encProof v2++t2)) =
              3402::v0::((encFormula v1++encProof v2)++t2)
            exact congrArg (fun xs => 3402::v0::xs)
              (append_assoc_local (encFormula v1) (encProof v2) t2).symm
      change some (Envelope.mk v0 v1 v2,t2)=some (out,rest) at next2
      cases next2
      exact exactInput
    · rw [if_neg e] at h
      cases h

theorem decode_converse {α : Type} (p : Parser α) (enc : α → List Nat)
    (hc : Consumes p enc) (bytes : List Nat) (a : α)
    (h : decode p bytes=some a) : tokenize bytes=some (enc a) := by
  unfold decode at h
  cases et : tokenize bytes with
  | none =>
    rw [et] at h
    cases h
  | some ts =>
    rw [et] at h
    obtain ⟨v,rest,hp,hr⟩ := bind_success p
      (fun v rest => match rest with | [] => some v | _::_ => none) ts a h
    cases rest with
    | nil =>
      have eq := hc ts v [] hp
      rw [append_nil_local] at eq
      change some v=some a at hr
      cases hr
      rw [eq]
    | cons x xs => cases hr

theorem wire_length (bytes ts : List Nat) (h : Wire bytes ts) :
    ts.length≤bytes.length := by
  induction h with
  | nil => exact Nat.le_refl 0
  | @cons digits bytes v vs word tail ih =>
    change vs.length+1≤(digits++10::bytes).length
    rw [len_append]
    exact Nat.le_trans (Nat.succ_le_succ ih) (Nat.le_add_left _ _)

theorem expected_bytes (bytes : List Nat) (n : Nat) (f : Formula)
    (h : decodeExpected bytes=some (n,f)) :
    tokenize bytes=some (encExpected n f) ∧ (encExpected n f).length≤bytes.length := by
  have e := decode_converse expectedToken (fun nf => encExpected nf.1 nf.2)
    expected_converse bytes (n,f) h
  exact ⟨e,wire_length _ _ (tokenize_converse _ _ e).right⟩

theorem envelope_bytes (bytes : List Nat) (e : Envelope)
    (h : decodeEnvelope bytes=some e) :
    tokenize bytes=some (encEnvelope e) ∧ (encEnvelope e).length≤bytes.length := by
  have he := decode_converse envelopeToken encEnvelope envelope_converse bytes e h
  exact ⟨he,wire_length _ _ (tokenize_converse _ _ he).right⟩

private theorem binary_mono (k a b : Nat) (h : a≤b) :
    ProctorTerminalPolynomial.binaryUnit k a≤ProctorTerminalPolynomial.binaryUnit k b := by
  induction k with
  | zero => exact h
  | succ k ih => exact Nat.add_le_add (Nat.add_le_add ih ih) (Nat.le_refl 1)

theorem global_mono (a b : Nat) (h : a≤b) : globalUnit a≤globalUnit b :=
  (Nat.add_le_add (Nat.le_refl 1) (Nat.add_le_add (mul_mono h (Nat.le_refl 4)) (Nat.add_le_add (mul_mono h (Nat.le_refl 4)) (Nat.add_le_add (mul_mono h (Nat.le_refl 4)) (Nat.add_le_add (mul_mono h (Nat.add_le_add (Nat.add_le_add h (mul_mono h (Nat.add_le_add h (Nat.le_refl 1)))) (Nat.add_le_add h (mul_mono h (Nat.add_le_add h (Nat.le_refl 1)))))) (Nat.add_le_add (Nat.add_le_add h (Nat.add_le_add (mul_mono h (Nat.add_le_add h (Nat.add_le_add h (Nat.le_refl 1)))) (Nat.add_le_add (mul_mono h (Nat.add_le_add h (Nat.add_le_add h (Nat.le_refl 1)))) (Nat.add_le_add (mul_mono h (Nat.add_le_add (Nat.add_le_add h (Nat.add_le_add (mul_mono h (Nat.add_le_add (mul_mono h (Nat.add_le_add (Nat.add_le_add (Nat.le_refl 9) (mul_mono h (Nat.le_refl 7))) (Nat.le_refl 1))) (Nat.le_refl 1))) (Nat.le_refl 1))) (Nat.le_refl 2))) (Nat.add_le_add (mul_mono h (Nat.add_le_add (mul_mono h (Nat.add_le_add (Nat.add_le_add (Nat.add_le_add (Nat.add_le_add h h) (mul_mono h (Nat.add_le_add (mul_mono h (Nat.le_refl 2)) (Nat.le_refl 1)))) (Nat.le_refl 1)) (Nat.le_refl 1))) (Nat.le_refl 1))) (Nat.add_le_add (mul_mono h (Nat.add_le_add h (Nat.le_refl 2))) (Nat.le_refl 1))))))) (Nat.add_le_add (Nat.add_le_add (Nat.add_le_add (mul_mono h (Nat.add_le_add (Nat.add_le_add (Nat.add_le_add (mul_mono h (Nat.add_le_add h (Nat.add_le_add h (Nat.le_refl 1)))) (binary_mono 5 _ _ (Nat.add_le_add (Nat.le_refl 6) (mul_mono h (Nat.le_refl 6))))) (Nat.le_refl 1)) (Nat.le_refl 1))) (mul_mono h h)) h) (Nat.le_refl 1))))))))

def byteCap (a b : List Nat) : Nat :=
  (a.length+b.length)+(a.length+b.length)+1

theorem byte_budget (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : decodeExpected a=some (n,f)) (hb : decodeEnvelope b=some e) :
    (ProctorUnifiedMeter.boundMeter n f e).2≤globalUnit (byteCap a b) := by
  have hs : size n f e≤a.length+b.length :=
    Nat.add_le_add (expected_bytes a n f ha).right (envelope_bytes b e hb).right
  exact Nat.le_trans (global_meter n f e)
    (global_mono _ _ (Nat.succ_le_succ (Nat.add_le_add hs hs)))

theorem accepted_byte_sound (a b : List Nat) (h : checkBytes a b=true) :
    ∃ n f e, decodeExpected a=some (n,f) ∧ decodeEnvelope b=some e ∧
      (¬ ∃ x : Assignment, FormulaSat f x) ∧
      (ProctorUnifiedMeter.boundMeter n f e).2≤globalUnit (byteCap a b) := by
  obtain ⟨n,f,e,ha,hb,hc⟩ := ProctorDataParser.accepted_decoded a b h
  exact ⟨n,f,e,ha,hb,ProctorUnifiedReplay.bound_sound n f e hc,byte_budget a b n f e ha hb⟩

end ProctorParserConsumption

#print axioms ProctorParserConsumption.nat_converse
#print axioms ProctorParserConsumption.bool_converse
#print axioms ProctorParserConsumption.many_converse
#print axioms ProctorParserConsumption.list_converse
#print axioms ProctorParserConsumption.literal_converse
#print axioms ProctorParserConsumption.clause_converse
#print axioms ProctorParserConsumption.formula_converse
#print axioms ProctorParserConsumption.ref_converse
#print axioms ProctorParserConsumption.group_converse
#print axioms ProctorParserConsumption.capacity_converse
#print axioms ProctorParserConsumption.block_converse
#print axioms ProctorParserConsumption.step_converse
#print axioms ProctorParserConsumption.terminal_converse
#print axioms ProctorParserConsumption.proof_converse
#print axioms ProctorParserConsumption.expected_converse
#print axioms ProctorParserConsumption.envelope_converse
#print axioms ProctorParserConsumption.decode_converse
#print axioms ProctorParserConsumption.wire_length
#print axioms ProctorParserConsumption.expected_bytes
#print axioms ProctorParserConsumption.envelope_bytes
#print axioms ProctorParserConsumption.global_mono
#print axioms ProctorParserConsumption.byte_budget
#print axioms ProctorParserConsumption.accepted_byte_sound
