/-! F034 candidate: compositional selected parser charges.
A list meter includes the child parser's selected charges in the base
transition, plus dispatch, word traversal, wrapper construction and
one list header attempt. Sequential composition sums child charges
and short-circuits. This is not a complete machine cost semantics. -/
namespace ProctorParserMeterCompose
open ProctorDataParser (Parser natToken boolToken listToken listLimit)
open ProctorFuelFreeParser (State advance finish manyWord listWord)
open ProctorIteratorDispatch (Metered word_projection)
open ProctorIteratorOverhead (ledger selectedTotal dispatch_projection total_bound)
open ProctorCheckedBinaryScanner (encode encode_sound)
open ProctorTerminalPolynomial (mul_mono)

abbrev ParserMeter (α : Type) := List Nat → Option (α × List Nat) × Nat
def project {α : Type} (p : ParserMeter α) : Parser α := fun ts => (p ts).1

def seqMeter {α β : Type} (p : ParserMeter α) (q : α → ParserMeter β)
    (ts : List Nat) : Option (β × List Nat) × Nat :=
  let r := p ts
  match r.1 with
  | none => (none,r.2)
  | some (a,rest) =>
    let v := q a rest
    (v.1,r.2+v.2)

theorem seq_projection {α β : Type} (p : ParserMeter α) (q : α → ParserMeter β)
    (ts : List Nat) :
    (seqMeter p q ts).1=(do
      let (a,rest) ← project p ts
      project (q a) rest) := by
  change (match (p ts).1 with
    | none => (none,(p ts).2)
    | some (a,rest) => ((q a rest).1,(p ts).2+(q a rest).2)).1=_
  unfold project
  cases e : (p ts).1 with
  | none => rfl
  | some pair => cases pair; rfl

theorem seq_bound {α β : Type} (p : ParserMeter α) (q : α → ParserMeter β)
    (A B : Nat) (hp : ∀ ts, (p ts).2≤A)
    (hq : ∀ a ts, (q a ts).2≤B) (ts : List Nat) :
    (seqMeter p q ts).2≤A+B := by
  change (match (p ts).1 with
    | none => (none,(p ts).2)
    | some (a,rest) => ((q a rest).1,(p ts).2+(q a rest).2)).2≤_
  cases e : (p ts).1 with
  | none => exact Nat.le_trans (hp ts) (Nat.le_add_right _ _)
  | some pair =>
    cases pair with
    | mk a rest => exact Nat.add_le_add (hp ts) (hq a rest)

def advanceMeter {α : Type} (p : ParserMeter α) (s : State α) :
    Option (State α) × Nat :=
  let r := p s.2
  match r.1 with
  | none => (none,r.2+1)
  | some (a,rest) => (some (a::s.1,rest),r.2+1)

theorem advance_projection {α : Type} (p : ParserMeter α) (s : State α) :
    (advanceMeter p s).1=advance (project p) s := by
  cases s with
  | mk acc ts =>
    change (match (p ts).1 with
      | none => (none,(p ts).2+1)
      | some (a,rest) => (some (a::acc,rest),(p ts).2+1)).1=
      (match (p ts).1 with
        | none => none
        | some (a,rest) => some (a::acc,rest))
    cases e : (p ts).1 with
    | none => rfl
    | some pair => cases pair; rfl

theorem advance_potential {α : Type} (p : ParserMeter α) (B : Nat)
    (h : ∀ ts, (p ts).2≤B) (s : State α) :
    (advanceMeter p s).2+1≤B+2 := by
  cases s with
  | mk acc ts =>
    change (match (p ts).1 with
      | none => (none,(p ts).2+1)
      | some (a,rest) => (some (a::acc,rest),(p ts).2+1)).2+1≤B+2
    cases e : (p ts).1 with
    | none => exact Nat.succ_le_succ (Nat.succ_le_succ (h ts))
    | some pair => cases pair; exact Nat.succ_le_succ (Nat.succ_le_succ (h ts))

def wordRun {α : Type} (p : ParserMeter α) (c : List Bool) (ts : List Nat) :
    Option (List α × List Nat) × Nat :=
  let r := ledger c (advanceMeter p) ([],ts)
  (finish r.1.1,r.1.2+r.2)

theorem word_run_projection {α : Type} (p : ParserMeter α) (c : List Bool)
    (ts : List Nat) :
    (wordRun p c ts).1=manyWord (project p) c ts [] := by
  change finish (ledger c (advanceMeter p) ([],ts)).1.1=
    finish (ProctorFuelFreeParser.iterWord c (advance (project p)) ([],ts))
  rw [dispatch_projection]
  exact congrArg finish (word_projection c (advanceMeter p)
    (advance (project p)) (advance_projection p) ([],ts))

theorem word_run_bound {α : Type} (p : ParserMeter α) (B : Nat)
    (h : ∀ ts, (p ts).2≤B) (c : List Bool) (ts : List Nat) :
    (wordRun p c ts).2≤(B+2)*ProctorDecimalBitWidth.bitsValue c+(2*c.length+1) :=
  total_bound c (advanceMeter p) (B+2) (advance_potential p B h) ([],ts)

def listMeter {α : Type} (p : ParserMeter α) : ParserMeter (List α)
  | [] => (none,1)
  | k::ts =>
    if k≤listLimit then
      match encode 17 k with
      | none => (none,1)
      | some c =>
        let r := wordRun p c ts
        (r.1,r.2+1)
    else (none,1)

theorem list_projection {α : Type} (p : ParserMeter α) (ts : List Nat) :
    (listMeter p ts).1=listWord (project p) ts := by
  cases ts with
  | nil => rfl
  | cons k ts =>
    change (if k≤listLimit then
      match encode 17 k with
      | none => (none,1)
      | some c => ((wordRun p c ts).1,(wordRun p c ts).2+1)
      else (none,1)).1=(if k≤listLimit then
      match encode 17 k with
      | none => none
      | some c => manyWord (project p) c ts []
      else none)
    by_cases h : k≤listLimit
    · rw [if_pos h,if_pos h]
      cases e : encode 17 k with
      | none => rfl
      | some c => exact word_run_projection p c ts
    · rw [if_neg h,if_neg h]

theorem list_refines {α : Type} (p : ParserMeter α) (ts : List Nat) :
    (listMeter p ts).1=listToken (project p) ts :=
  (list_projection p ts).trans (ProctorFuelFreeParser.list_word_refines (project p) ts)

def listBudget (B : Nat) : Nat := (B+2)*listLimit+36

theorem list_bound {α : Type} (p : ParserMeter α) (B : Nat)
    (h : ∀ ts, (p ts).2≤B) (ts : List Nat) :
    (listMeter p ts).2≤listBudget B := by
  cases ts with
  | nil =>
    change 1≤(B+2)*listLimit+36
    exact Nat.succ_le_succ (Nat.zero_le _)
  | cons k ts =>
    change (if k≤listLimit then
      match encode 17 k with
      | none => (none,1)
      | some c => ((wordRun p c ts).1,(wordRun p c ts).2+1)
      else (none,1)).2≤(B+2)*listLimit+36
    by_cases hk : k≤listLimit
    · rw [if_pos hk]
      cases e : encode 17 k with
      | none => exact Nat.succ_le_succ (Nat.zero_le _)
      | some c =>
        have hs := encode_sound 17 k c e
        have hb := word_run_bound p B h c ts
        rw [hs.left,hs.right] at hb
        change (wordRun p c ts).2+1≤(B+2)*listLimit+36
        exact Nat.succ_le_succ (Nat.le_trans hb
          (Nat.add_le_add (mul_mono (Nat.le_refl (B+2)) hk) (Nat.le_refl 35)))
    · rw [if_neg hk]
      exact Nat.succ_le_succ (Nat.zero_le _)

def natMeter : ParserMeter Nat := fun ts => (natToken ts,1)
def boolMeter : ParserMeter Bool := fun ts => (boolToken ts,1)

theorem nested_nat_refines (ts : List Nat) :
    (listMeter (listMeter natMeter) ts).1=listToken (listToken natToken) ts := by
  rw [list_projection]
  exact ProctorFuelFreeParser.list_congr_pointwise
    (project (listMeter natMeter)) (listToken natToken)
    (fun xs => list_refines natMeter xs) ts

theorem nested_nat_bound (ts : List Nat) :
    (listMeter (listMeter natMeter) ts).2≤listBudget (listBudget 1) :=
  list_bound (listMeter natMeter) (listBudget 1)
    (list_bound natMeter 1 (fun _ => Nat.le_refl 1)) ts

end ProctorParserMeterCompose

#print axioms ProctorParserMeterCompose.seq_projection
#print axioms ProctorParserMeterCompose.seq_bound
#print axioms ProctorParserMeterCompose.advance_projection
#print axioms ProctorParserMeterCompose.advance_potential
#print axioms ProctorParserMeterCompose.word_run_projection
#print axioms ProctorParserMeterCompose.word_run_bound
#print axioms ProctorParserMeterCompose.list_projection
#print axioms ProctorParserMeterCompose.list_refines
#print axioms ProctorParserMeterCompose.list_bound
#print axioms ProctorParserMeterCompose.nested_nat_refines
#print axioms ProctorParserMeterCompose.nested_nat_bound
