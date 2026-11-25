/-! F034: compositional metering of attempted natural-token reads.
A failed read at EOF costs one. Guard comparisons, constructors,
reversal, calls and integer operations are outside this charge model. -/
namespace ProctorTypedParserMeter
open ProctorHallDeficiency
open ProctorDataParser
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Terminal Envelope)

abbrev MeterParser (α : Type) := List Nat → Option (α × List Nat) × Nat

def Value {α : Type} (m : MeterParser α) (p : Parser α) : Prop :=
  ∀ ts, (m ts).1=p ts

def Good {α : Type} (m : MeterParser α) : Prop :=
  ∀ ts, match m ts with
  | (none,k) => k≤ts.length+1
  | (some (_,rest),k) => k+rest.length=ts.length

def pureMeter {α : Type} (a : α) : MeterParser α :=
  fun ts => (some (a,ts),0)

def failMeter {α : Type} : MeterParser α := fun _ => (none,0)

def bindMeter {α β : Type} (p : MeterParser α)
    (q : α → MeterParser β) : MeterParser β := fun ts =>
  let r := p ts
  match r.1 with
  | none => (none,r.2)
  | some (a,rest) =>
    let s := q a rest
    (s.1,r.2+s.2)

def chooseMeter {α : Type} (c : Prop) [Decidable c]
    (p q : MeterParser α) : MeterParser α :=
  if c then p else q

theorem bind_value {α β : Type} (p : MeterParser α) (q : α → MeterParser β)
    (P : Parser α) (Q : α → Parser β)
    (hp : Value p P) (hq : ∀ a, Value (q a) (Q a)) :
    Value (bindMeter p q) (fun ts => do
      let (a,rest) ← P ts
      Q a rest) := by
  intro ts
  change (match (p ts).1 with
    | none => (none,(p ts).2)
    | some (a,rest) => ((q a rest).1,(p ts).2+(q a rest).2)).1 =
    (do
      let (a,rest) ← P ts
      Q a rest)
  rw [← hp ts]
  cases (p ts).1 with
  | none => rfl
  | some ar =>
    cases ar with
    | mk a rest => exact hq a rest

theorem bind_good {α β : Type} (p : MeterParser α) (q : α → MeterParser β)
    (hp : Good p) (hq : ∀ a, Good (q a)) : Good (bindMeter p q) := by
  intro ts
  have h := hp ts
  unfold bindMeter
  cases e : p ts with
  | mk r k =>
    rw [e] at h
    cases r with
    | none => exact h
    | some ar =>
      cases ar with
      | mk a rest =>
        change k+rest.length=ts.length at h
        change (match ((q a rest).1,k+(q a rest).2) with
          | (none,j) => j≤ts.length+1
          | (some (_,tail),j) => j+tail.length=ts.length)
        have hh := hq a rest
        cases ee : q a rest with
        | mk s j =>
          rw [ee] at hh
          cases s with
          | none =>
            change j≤rest.length+1 at hh
            change k+j≤ts.length+1
            calc
              k+j ≤ k+(rest.length+1) := Nat.add_le_add (Nat.le_refl _) hh
              _ = ts.length+1 := by rw [← Nat.add_assoc,h]
          | some ar =>
            cases ar with
            | mk b tail =>
              change j+tail.length=rest.length at hh
              change (k+j)+tail.length=ts.length
              rw [Nat.add_assoc,hh,h]

theorem choose_value {α : Type} (c : Prop) [Decidable c]
    (p q : MeterParser α) (P Q : Parser α)
    (hp : Value p P) (hq : Value q Q) :
    Value (chooseMeter c p q) (fun ts => if c then P ts else Q ts) := by
  intro ts
  change ((if c then p else q) ts).1 = (if c then P ts else Q ts)
  by_cases h : c
  · rw [if_pos h,if_pos h] <;> exact hp ts
  · rw [if_neg h,if_neg h] <;> exact hq ts

theorem choose_good {α : Type} (c : Prop) [Decidable c]
    (p q : MeterParser α) (hp : Good p) (hq : Good q) :
    Good (chooseMeter c p q) := by
  unfold chooseMeter
  by_cases h : c
  · rw [if_pos h]
    exact hp
  · rw [if_neg h]
    exact hq

private theorem pure_value {α : Type} (a : α) :
    Value (pureMeter a) (fun ts => some (a,ts)) := fun _ => rfl

private theorem pure_good {α : Type} (a : α) : Good (pureMeter a) := by
  intro ts
  change 0+ts.length=ts.length
  exact Nat.zero_add _

private theorem fail_value {α : Type} :
    Value (failMeter : MeterParser α) (fun _ => none) := fun _ => rfl

private theorem fail_good {α : Type} : Good (failMeter : MeterParser α) :=
  fun ts => Nat.zero_le (ts.length+1)

def natMeter : MeterParser Nat
  | [] => (none,1)
  | v::vs => (some (v,vs),1)

theorem nat_value : Value natMeter natToken := by
  intro ts
  cases ts <;> rfl

theorem nat_good : Good natMeter := by
  intro ts
  cases ts with
  | nil => exact Nat.le_refl 1
  | cons v vs => exact Nat.add_comm 1 vs.length

-- The specification uses bindMeter. The executable accumulator
-- implementation is supplied below, to avoid deferred charge adds
-- for long lists.
def manySpec {α : Type} (p : MeterParser α) :
    Nat → List α → MeterParser (List α)
  | 0,acc => pureMeter acc.reverse
  | k+1,acc => bindMeter p (fun a => manySpec p k (a::acc))

theorem many_value {α : Type} (p : MeterParser α) (P : Parser α)
    (hp : Value p P) (k : Nat) (acc : List α) :
    Value (manySpec p k acc) (fun ts => manyAux P k ts acc) := by
  induction k generalizing acc with
  | zero => exact pure_value _
  | succ k ih =>
    exact bind_value p (fun a => manySpec p k (a::acc)) P
      (fun a ts => manyAux P k ts (a::acc)) hp (fun a => ih (a::acc))

theorem many_good {α : Type} (p : MeterParser α) (hp : Good p)
    (k : Nat) (acc : List α) : Good (manySpec p k acc) := by
  induction k generalizing acc with
  | zero => exact pure_good _
  | succ k ih => exact bind_good p _ hp (fun a => ih (a::acc))

def manyRun {α : Type} (p : MeterParser α) :
    Nat → List Nat → List α → Nat → Option (List α × List Nat) × Nat
  | 0,ts,acc,c => (some (acc.reverse,ts),c)
  | k+1,ts,acc,c =>
    let r := p ts
    match r.1 with
    | none => (none,c+r.2)
    | some (a,rest) => manyRun p k rest (a::acc) (c+r.2)

private theorem many_run_spec {α : Type} (p : MeterParser α)
    (k : Nat) (ts : List Nat) (acc : List α) (c : Nat) :
    manyRun p k ts acc c =
      ((manySpec p k acc ts).1,c+(manySpec p k acc ts).2) := by
  induction k generalizing ts acc c with
  | zero => rfl
  | succ k ih =>
    change (match (p ts).1 with
      | none => (none,c+(p ts).2)
      | some (a,rest) => manyRun p k rest (a::acc) (c+(p ts).2)) =
      ((bindMeter p (fun a => manySpec p k (a::acc)) ts).1,
        c+(bindMeter p (fun a => manySpec p k (a::acc)) ts).2)
    unfold bindMeter
    cases e : p ts with
    | mk r j =>
      cases r with
      | none => rfl
      | some ar =>
        cases ar with
        | mk a rest =>
          change manyRun p k rest (a::acc) (c+j) =
            ((manySpec p k (a::acc) rest).1,c+(j+(manySpec p k (a::acc) rest).2))
          rw [ih]
          change ((manySpec p k (a::acc) rest).1,(c+j)+(manySpec p k (a::acc) rest).2) =
            ((manySpec p k (a::acc) rest).1,c+(j+(manySpec p k (a::acc) rest).2))
          rw [Nat.add_assoc]

def manyMeter {α : Type} (p : MeterParser α) (k : Nat) (acc : List α) :
    MeterParser (List α) := fun ts => manyRun p k ts acc 0

theorem many_meter_spec {α : Type} (p : MeterParser α)
    (k : Nat) (acc : List α) (ts : List Nat) :
    manyMeter p k acc ts=manySpec p k acc ts := by
  unfold manyMeter
  rw [many_run_spec,Nat.zero_add]

private theorem many_exec_value {α : Type} (p : MeterParser α) (P : Parser α)
    (hp : Value p P) (k : Nat) (acc : List α) :
    Value (manyMeter p k acc) (fun ts => manyAux P k ts acc) := by
  intro ts
  rw [many_meter_spec]
  exact many_value p P hp k acc ts

private theorem many_exec_good {α : Type} (p : MeterParser α) (hp : Good p)
    (k : Nat) (acc : List α) : Good (manyMeter p k acc) := by
  intro ts
  rw [many_meter_spec]
  exact many_good p hp k acc ts

def listMeter {α : Type} (p : MeterParser α) : MeterParser (List α) :=
  bindMeter natMeter (fun k => chooseMeter (k≤listLimit)
    (manyMeter p k []) failMeter)

theorem list_value {α : Type} (p : MeterParser α) (P : Parser α)
    (hp : Value p P) : Value (listMeter p) (listToken P) := by
  unfold listMeter listToken
  exact bind_value natMeter
    (fun k => chooseMeter (k≤listLimit) (manyMeter p k []) failMeter)
    natToken (fun k ts => if k≤listLimit then manyAux P k ts [] else none)
    nat_value (fun k => choose_value (k≤listLimit) _ _ _ _
      (many_exec_value p P hp k []) fail_value)

theorem list_good {α : Type} (p : MeterParser α) (hp : Good p) :
    Good (listMeter p) := by
  unfold listMeter
  apply bind_good _ _ nat_good
  intro k
  exact choose_good _ _ _ (many_exec_good p hp k []) fail_good


def boolMeter : MeterParser Bool :=
  (bindMeter natMeter (fun v => (chooseMeter (v=0) (pureMeter false) (chooseMeter (v=1) (pureMeter true) failMeter))))

theorem bool_value : Value boolMeter boolToken :=
  (bind_value _ _ _ _ nat_value (fun _v => (choose_value _ _ _ _ _ (pure_value _) (choose_value _ _ _ _ _ (pure_value _) fail_value))))

theorem bool_good : Good boolMeter :=
  (bind_good _ _ nat_good (fun _v => (choose_good _ _ _ (pure_good _) (choose_good _ _ _ (pure_good _) fail_good))))

def literalMeter : MeterParser Literal :=
  (bindMeter natMeter (fun v => (bindMeter boolMeter (fun sign => (pureMeter (v,sign))))))

theorem literal_value : Value literalMeter literalToken :=
  (bind_value _ _ _ _ nat_value (fun _v => (bind_value _ _ _ _ bool_value (fun _sign => (pure_value _)))))

theorem literal_good : Good literalMeter :=
  (bind_good _ _ nat_good (fun _v => (bind_good _ _ bool_good (fun _sign => (pure_good _)))))

def clauseMeter : MeterParser Clause :=
  (listMeter literalMeter)

theorem clause_value : Value clauseMeter clauseToken :=
  (list_value _ _ literal_value)

theorem clause_good : Good clauseMeter :=
  (list_good _ literal_good)

def formulaMeter : MeterParser Formula :=
  (listMeter clauseMeter)

theorem formula_value : Value formulaMeter formulaToken :=
  (list_value _ _ clause_value)

theorem formula_good : Good formulaMeter :=
  (list_good _ clause_good)

def refMeter : MeterParser RefRow :=
  (bindMeter natMeter (fun i => (bindMeter clauseMeter (fun row => (pureMeter (RefRow.mk i row))))))

theorem ref_value : Value refMeter refToken :=
  (bind_value _ _ _ _ nat_value (fun _i => (bind_value _ _ _ _ clause_value (fun _row => (pure_value _)))))

theorem ref_good : Good refMeter :=
  (bind_good _ _ nat_good (fun _i => (bind_good _ _ clause_good (fun _row => (pure_good _)))))

def groupMeter : MeterParser Group :=
  (bindMeter clauseMeter (fun vs => (bindMeter natMeter (fun k => (pureMeter (Group.mk vs k))))))

theorem group_value : Value groupMeter groupToken :=
  (bind_value _ _ _ _ clause_value (fun _vs => (bind_value _ _ _ _ nat_value (fun _k => (pure_value _)))))

theorem group_good : Good groupMeter :=
  (bind_good _ _ clause_good (fun _vs => (bind_good _ _ nat_good (fun _k => (pure_good _)))))

def capacityMeter : MeterParser Certificate :=
  (bindMeter (listMeter refMeter) (fun ds => (bindMeter (listMeter groupMeter) (fun gs => (bindMeter (listMeter refMeter) (fun rs => (pureMeter (Certificate.mk ds gs rs))))))))

theorem capacity_value : Value capacityMeter capacityToken :=
  (bind_value _ _ _ _ (list_value _ _ ref_value) (fun _ds => (bind_value _ _ _ _ (list_value _ _ group_value) (fun _gs => (bind_value _ _ _ _ (list_value _ _ ref_value) (fun _rs => (pure_value _)))))))

theorem capacity_good : Good capacityMeter :=
  (bind_good _ _ (list_good _ ref_good) (fun _ds => (bind_good _ _ (list_good _ group_good) (fun _gs => (bind_good _ _ (list_good _ ref_good) (fun _rs => (pure_good _)))))))

def blockMeter : MeterParser Block :=
  (bindMeter (listMeter natMeter) (fun vs => (bindMeter boolMeter (fun rhs => (bindMeter (listMeter refMeter) (fun rs => (pureMeter (Block.mk vs rhs rs))))))))

theorem block_value : Value blockMeter blockToken :=
  (bind_value _ _ _ _ (list_value _ _ nat_value) (fun _vs => (bind_value _ _ _ _ bool_value (fun _rhs => (bind_value _ _ _ _ (list_value _ _ ref_value) (fun _rs => (pure_value _)))))))

theorem block_good : Good blockMeter :=
  (bind_good _ _ (list_good _ nat_good) (fun _vs => (bind_good _ _ bool_good (fun _rhs => (bind_good _ _ (list_good _ ref_good) (fun _rs => (pure_good _)))))))

def stepMeter : MeterParser Step :=
  (bindMeter natMeter (fun a => (bindMeter natMeter (fun b => (bindMeter natMeter (fun pivot => (bindMeter clauseMeter (fun tail => (pureMeter (Step.mk a b pivot tail))))))))))

theorem step_value : Value stepMeter stepToken :=
  (bind_value _ _ _ _ nat_value (fun _a => (bind_value _ _ _ _ nat_value (fun _b => (bind_value _ _ _ _ nat_value (fun _pivot => (bind_value _ _ _ _ clause_value (fun _tail => (pure_value _)))))))))

theorem step_good : Good stepMeter :=
  (bind_good _ _ nat_good (fun _a => (bind_good _ _ nat_good (fun _b => (bind_good _ _ nat_good (fun _pivot => (bind_good _ _ clause_good (fun _tail => (pure_good _)))))))))

def terminalMeter : MeterParser Terminal :=
  (bindMeter natMeter (fun tag => (chooseMeter (tag=0) (pureMeter Terminal.empty) (chooseMeter (tag=1) (bindMeter capacityMeter (fun cert => (pureMeter (Terminal.capacity cert)))) (chooseMeter (tag=2) (bindMeter (listMeter blockMeter) (fun bs => (pureMeter (Terminal.xor bs)))) failMeter)))))

theorem terminal_value : Value terminalMeter terminalToken :=
  (bind_value _ _ _ _ nat_value (fun _tag => (choose_value _ _ _ _ _ (pure_value _) (choose_value _ _ _ _ _ (bind_value _ _ _ _ capacity_value (fun _cert => (pure_value _))) (choose_value _ _ _ _ _ (bind_value _ _ _ _ (list_value _ _ block_value) (fun _bs => (pure_value _))) fail_value)))))

theorem terminal_good : Good terminalMeter :=
  (bind_good _ _ nat_good (fun _tag => (choose_good _ _ _ (pure_good _) (choose_good _ _ _ (bind_good _ _ capacity_good (fun _cert => (pure_good _))) (choose_good _ _ _ (bind_good _ _ (list_good _ block_good) (fun _bs => (pure_good _))) fail_good)))))

def proofMeter : MeterParser Proof :=
  (bindMeter (listMeter (listMeter stepMeter)) (fun bs => (bindMeter boolMeter (fun aug => (bindMeter terminalMeter (fun terminal => (pureMeter (Proof.mk bs aug terminal))))))))

theorem proof_value : Value proofMeter proofToken :=
  (bind_value _ _ _ _ (list_value _ _ (list_value _ _ step_value)) (fun _bs => (bind_value _ _ _ _ bool_value (fun _aug => (bind_value _ _ _ _ terminal_value (fun _terminal => (pure_value _)))))))

theorem proof_good : Good proofMeter :=
  (bind_good _ _ (list_good _ (list_good _ step_good)) (fun _bs => (bind_good _ _ bool_good (fun _aug => (bind_good _ _ terminal_good (fun _terminal => (pure_good _)))))))

def expectedMeter : MeterParser (Nat × Formula) :=
  (bindMeter natMeter (fun magic => (chooseMeter (magic=3401) (bindMeter natMeter (fun n => (bindMeter formulaMeter (fun f => (pureMeter (n,f)))))) failMeter)))

theorem expected_value : Value expectedMeter expectedToken :=
  (bind_value _ _ _ _ nat_value (fun _magic => (choose_value _ _ _ _ _ (bind_value _ _ _ _ nat_value (fun _n => (bind_value _ _ _ _ formula_value (fun _f => (pure_value _))))) fail_value)))

theorem expected_good : Good expectedMeter :=
  (bind_good _ _ nat_good (fun _magic => (choose_good _ _ _ (bind_good _ _ nat_good (fun _n => (bind_good _ _ formula_good (fun _f => (pure_good _))))) fail_good)))

def envelopeMeter : MeterParser Envelope :=
  (bindMeter natMeter (fun magic => (chooseMeter (magic=3402) (bindMeter natMeter (fun n => (bindMeter formulaMeter (fun f => (bindMeter proofMeter (fun proof => (pureMeter (Envelope.mk n f proof)))))))) failMeter)))

theorem envelope_value : Value envelopeMeter envelopeToken :=
  (bind_value _ _ _ _ nat_value (fun _magic => (choose_value _ _ _ _ _ (bind_value _ _ _ _ nat_value (fun _n => (bind_value _ _ _ _ formula_value (fun _f => (bind_value _ _ _ _ proof_value (fun _proof => (pure_value _))))))) fail_value)))

theorem envelope_good : Good envelopeMeter :=
  (bind_good _ _ nat_good (fun _magic => (choose_good _ _ _ (bind_good _ _ nat_good (fun _n => (bind_good _ _ formula_good (fun _f => (bind_good _ _ proof_good (fun _proof => (pure_good _))))))) fail_good)))

theorem read_bound {α : Type} (m : MeterParser α) (h : Good m)
    (ts : List Nat) : (m ts).2≤ts.length+1 := by
  have hg := h ts
  cases e : m ts with
  | mk r k =>
    rw [e] at hg
    cases r with
    | none => exact hg
    | some ar =>
      cases ar with
      | mk a rest =>
        change k+rest.length=ts.length at hg
        change k≤ts.length+1
        rw [← hg]
        exact Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _)

theorem successful_reads {α : Type} (m : MeterParser α) (h : Good m)
    (ts : List Nat) (a : α) (rest : List Nat)
    (e : (m ts).1=some (a,rest)) :
    (m ts).2+rest.length=ts.length := by
  have hg := h ts
  revert e
  cases em : m ts with
  | mk r k =>
    rw [em] at hg
    intro he
    change r=some (a,rest) at he
    cases he
    exact hg

def decodeMeter {α : Type} (m : MeterParser α) (bytes : List Nat) :
    Option α × Nat :=
  let s := ProctorScannerMeter.tokenizeMeter bytes
  match s.1 with
  | none => (none,s.2)
  | some ts =>
    let r := m ts
    let out := match r.1 with
      | some (a,[]) => some a
      | _ => none
    (out,s.2+r.2+1)

theorem decode_value {α : Type} (m : MeterParser α) (p : Parser α)
    (h : Value m p) (bytes : List Nat) :
    (decodeMeter m bytes).1=decode p bytes := by
  unfold decodeMeter decode
  change (match (ProctorScannerMeter.tokenizeMeter bytes).1 with
    | none => (none,(ProctorScannerMeter.tokenizeMeter bytes).2)
    | some ts =>
      (match (m ts).1 with
       | some (a,[]) => some a
       | _ => none,
       (ProctorScannerMeter.tokenizeMeter bytes).2+(m ts).2+1)).1 =
    (do
      let ts ← tokenize bytes
      let (a,rest) ← p ts
      match rest with | [] => some a | _::_ => none)
  rw [ProctorScannerMeter.tokenize_value]
  cases e : tokenize bytes with
  | none => rfl
  | some ts =>
    change (match (m ts).1 with
      | some (a,[]) => some a
      | _ => none) = (do
        let (a,rest) ← p ts
        match rest with | [] => some a | _::_ => none)
    rw [h ts]
    cases p ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => cases rest <;> rfl

def decodeBudget (bytes : List Nat) : Nat :=
  ProctorScannerMeter.tokenBudget bytes+(bytes.length+1)+1

theorem decode_bound {α : Type} (m : MeterParser α) (h : Good m)
    (bytes : List Nat) : (decodeMeter m bytes).2≤decodeBudget bytes := by
  unfold decodeMeter decodeBudget
  have hs := ProctorScannerMeter.tokenize_bound bytes
  cases e : ProctorScannerMeter.tokenizeMeter bytes with
  | mk r k =>
    rw [e] at hs
    cases r with
    | none =>
      exact Nat.le_trans hs (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _))
    | some ts =>
      have hv := ProctorScannerMeter.tokenize_value bytes
      rw [e] at hv
      have he : tokenize bytes=some ts := hv.symm
      have ht := ProctorParserConsumption.wire_length bytes ts
        (ProctorEnvelopeRoundtrip.tokenize_converse bytes ts he).right
      change k+(m ts).2+1≤ProctorScannerMeter.tokenBudget bytes+(bytes.length+1)+1
      exact Nat.add_le_add (Nat.add_le_add hs
        (Nat.le_trans (read_bound m h ts) (Nat.succ_le_succ ht))) (Nat.le_refl 1)

end ProctorTypedParserMeter

#print axioms ProctorTypedParserMeter.bind_value
#print axioms ProctorTypedParserMeter.bind_good
#print axioms ProctorTypedParserMeter.choose_value
#print axioms ProctorTypedParserMeter.choose_good
#print axioms ProctorTypedParserMeter.nat_value
#print axioms ProctorTypedParserMeter.nat_good
#print axioms ProctorTypedParserMeter.many_value
#print axioms ProctorTypedParserMeter.many_good
#print axioms ProctorTypedParserMeter.list_value
#print axioms ProctorTypedParserMeter.list_good
#print axioms ProctorTypedParserMeter.bool_value
#print axioms ProctorTypedParserMeter.bool_good
#print axioms ProctorTypedParserMeter.literal_value
#print axioms ProctorTypedParserMeter.literal_good
#print axioms ProctorTypedParserMeter.clause_value
#print axioms ProctorTypedParserMeter.clause_good
#print axioms ProctorTypedParserMeter.formula_value
#print axioms ProctorTypedParserMeter.formula_good
#print axioms ProctorTypedParserMeter.ref_value
#print axioms ProctorTypedParserMeter.ref_good
#print axioms ProctorTypedParserMeter.group_value
#print axioms ProctorTypedParserMeter.group_good
#print axioms ProctorTypedParserMeter.capacity_value
#print axioms ProctorTypedParserMeter.capacity_good
#print axioms ProctorTypedParserMeter.block_value
#print axioms ProctorTypedParserMeter.block_good
#print axioms ProctorTypedParserMeter.step_value
#print axioms ProctorTypedParserMeter.step_good
#print axioms ProctorTypedParserMeter.terminal_value
#print axioms ProctorTypedParserMeter.terminal_good
#print axioms ProctorTypedParserMeter.proof_value
#print axioms ProctorTypedParserMeter.proof_good
#print axioms ProctorTypedParserMeter.expected_value
#print axioms ProctorTypedParserMeter.expected_good
#print axioms ProctorTypedParserMeter.envelope_value
#print axioms ProctorTypedParserMeter.envelope_good
#print axioms ProctorTypedParserMeter.many_meter_spec
#print axioms ProctorTypedParserMeter.read_bound
#print axioms ProctorTypedParserMeter.successful_reads
#print axioms ProctorTypedParserMeter.decode_value
#print axioms ProctorTypedParserMeter.decode_bound
