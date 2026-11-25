/-! F034 candidate: reusable amortization with a bounded extra
list-header charge. Use the unchanged iterator and parser semantics.
512 units per token pay for every nested header independently.
Selected events, not bit-machine cost. -/
namespace ProctorNestedEncoderAmortization
open ProctorParserMeterCompose (ParserMeter advanceMeter wordRun listMeter natMeter boolMeter)
open ProctorInputSensitiveIterator (Safe word_success joint_bound)
open ProctorIteratorOverhead (ledger selectedTotal dispatch_projection overhead_bound)
open ProctorIteratorDispatch (wordMeter)
open ProctorFuelFreeParser (State finish)
open ProctorDataParser (listLimit)
open ProctorCheckedBinaryScanner (encode encode_sound)

def potential (ts : List Nat) : Nat := 512*ts.length

def Amortized {α : Type} (p : ParserMeter α) : Prop :=
  (∀ ts a rest, (p ts).1=some (a,rest) →
    ((p ts).2+2)+potential rest≤potential ts) ∧
  (∀ ts, (p ts).1=none → (p ts).2+2≤potential ts+3)

def statePotential {α : Type} (s : State α) : Nat := potential s.2

theorem advance_safe {α : Type} (p : ParserMeter α) (hp : Amortized p) :
    Safe (advanceMeter p) statePotential 3 := by
  constructor
  · intro s out hs
    cases s with
    | mk acc ts =>
      have he : advanceMeter p (acc,ts)=
          (match (p ts).1 with
          | none => (none,(p ts).2+1)
          | some (a,rest) => (some (a::acc,rest),(p ts).2+1)) := rfl
      cases e : (p ts).1 with
      | none =>
        rw [he,e] at hs
        cases hs
      | some pair =>
        cases pair with
        | mk a rest =>
          rw [he,e] at hs
          change some (a::acc,rest)=some out at hs
          cases hs
          rw [he,e]
          exact hp.1 ts a rest e
  · intro s hs
    cases s with
    | mk acc ts =>
      have he : advanceMeter p (acc,ts)=
          (match (p ts).1 with
          | none => (none,(p ts).2+1)
          | some (a,rest) => (some (a::acc,rest),(p ts).2+1)) := rfl
      cases e : (p ts).1 with
      | none =>
        rw [he,e]
        exact hp.2 ts e
      | some pair =>
        cases pair with
        | mk a rest =>
          rw [he,e] at hs
          cases hs

private theorem swap_middle (a b c : Nat) : (a+b)+c=(a+c)+b := by
  calc
    (a+b)+c = a+(b+c) := Nat.add_assoc _ _ _
    _ = a+(c+b) := congrArg (fun n => a+n) (Nat.add_comm _ _)
    _ = (a+c)+b := (Nat.add_assoc _ _ _).symm

theorem word_run_success {α : Type} (p : ParserMeter α)
    (hp : Amortized p) (c : List Bool) (ts : List Nat)
    (out : List α) (rest : List Nat)
    (hs : (wordRun p c ts).1=some (out,rest)) :
    (wordRun p c ts).2+potential rest≤potential ts+(2*c.length+1) := by
  cases e : (ledger c (advanceMeter p) ([],ts)).1.1 with
  | none =>
    have hf : (wordRun p c ts).1=none := by
      change finish (ledger c (advanceMeter p) ([],ts)).1.1=none
      rw [e] <;> rfl
    rw [hf] at hs
    cases hs
  | some pair =>
    cases pair with
    | mk acc next =>
      have hf : (wordRun p c ts).1=some (acc.reverse,next) := by
        change finish (ledger c (advanceMeter p) ([],ts)).1.1=_
        rw [e] <;> rfl
      rw [hf] at hs
      have hr : next=rest := congrArg Prod.snd (Option.some.inj hs)
      rw [← hr]
      have hw := e
      rw [dispatch_projection c (advanceMeter p) ([],ts)] at hw
      have hd := word_success c (advanceMeter p) statePotential 3
        (advance_safe p hp) ([],ts) (acc,next) hw
      have ho := overhead_bound c (advanceMeter p) ([],ts)
      change (wordMeter c (advanceMeter p) ([],ts)).2+potential next≤potential ts at hd
      change ((ledger c (advanceMeter p) ([],ts)).1.2+
        (ledger c (advanceMeter p) ([],ts)).2)+potential next≤_
      rw [dispatch_projection c (advanceMeter p) ([],ts),swap_middle]
      exact Nat.add_le_add hd ho

theorem word_run_all {α : Type} (p : ParserMeter α)
    (hp : Amortized p) (c : List Bool) (ts : List Nat) :
    (wordRun p c ts).2≤(potential ts+(3+c.length))+(2*c.length+1) :=
  joint_bound c (advanceMeter p) statePotential 3 (advance_safe p hp) ([],ts)

private theorem list_bad {α : Type} (p : ParserMeter α) (k : Nat)
    (ts : List Nat) (h : ¬ k≤listLimit) :
    listMeter p (k::ts)=(none,1) := by
  change (if k≤listLimit then
    match encode 17 k with
    | none => (none,1)
    | some c => ((wordRun p c ts).1,(wordRun p c ts).2+1)
    else (none,1))=_
  rw [if_neg h]

private theorem list_no_word {α : Type} (p : ParserMeter α) (k : Nat)
    (ts : List Nat) (h : k≤listLimit) (e : encode 17 k=none) :
    listMeter p (k::ts)=(none,1) := by
  change (if k≤listLimit then
    match encode 17 k with
    | none => (none,1)
    | some c => ((wordRun p c ts).1,(wordRun p c ts).2+1)
    else (none,1))=_
  rw [if_pos h,e]

private theorem list_word {α : Type} (p : ParserMeter α) (k : Nat)
    (ts : List Nat) (h : k≤listLimit) (c : List Bool) (e : encode 17 k=some c) :
    listMeter p (k::ts)=((wordRun p c ts).1,(wordRun p c ts).2+1) := by
  change (if k≤listLimit then
    match encode 17 k with
    | none => (none,1)
    | some c => ((wordRun p c ts).1,(wordRun p c ts).2+1)
    else (none,1))=_
  rw [if_pos h,e]

open ProctorEncodeVisits (encodeMeter seventeen_bound)

def headerCharge : List Nat → Nat
  | [] => 0
  | k::_ => if k≤listLimit then (encodeMeter 17 k).2 else 0

theorem header_bound (ts : List Nat) : headerCharge ts≤307 := by
  cases ts with
  | nil => exact Nat.zero_le _
  | cons k rest =>
    change (if k≤listLimit then (encodeMeter 17 k).2 else 0)≤307
    by_cases h : k≤listLimit
    · rw [if_pos h]
      exact seventeen_bound k
    · rw [if_neg h]
      exact Nat.zero_le _

def chargedList {α : Type} (p : ParserMeter α) (ts : List Nat) :
    Option (List α × List Nat) × Nat :=
  let r := listMeter p ts
  (r.1,r.2+headerCharge ts)

theorem charged_projection {α : Type} (p : ParserMeter α) (ts : List Nat) :
    (chargedList p ts).1=(listMeter p ts).1 := rfl

theorem list_amortized {α : Type} (p : ParserMeter α) (hp : Amortized p) :
    Amortized (chargedList p) := by
  constructor
  · intro input out rest hs
    cases input with
    | nil => cases hs
    | cons k ts =>
      change (listMeter p (k::ts)).1=some (out,rest) at hs
      change (((listMeter p (k::ts)).2+headerCharge (k::ts))+2)+
        potential rest≤potential ts+512
      by_cases hk : k≤listLimit
      · cases e : encode 17 k with
        | none =>
          rw [list_no_word p k ts hk e] at hs
          cases hs
        | some c =>
          rw [list_word p k ts hk c e] at hs ⊢
          change (wordRun p c ts).1=some (out,rest) at hs
          have hb := word_run_success p hp c ts out rest hs
          rw [(encode_sound 17 k c e).left] at hb
          have hh := header_bound (k::ts)
          change ((((wordRun p c ts).2+1)+headerCharge (k::ts))+2)+
            potential rest≤potential ts+512
          rw [swap_middle ((wordRun p c ts).2+1) (headerCharge (k::ts)) 2]
          change (((wordRun p c ts).2+3)+headerCharge (k::ts))+potential rest≤_
          rw [swap_middle ((wordRun p c ts).2+3) (headerCharge (k::ts)) (potential rest),
            swap_middle (wordRun p c ts).2 3 (potential rest)]
          calc
            (((wordRun p c ts).2+potential rest)+3)+headerCharge (k::ts)
                ≤ ((potential ts+35)+3)+307 :=
              Nat.add_le_add (Nat.add_le_add hb (Nat.le_refl 3)) hh
            _ ≤ potential ts+512 := by
              rw [Nat.add_assoc (potential ts) 35 3,
                Nat.add_assoc (potential ts) (35+3) 307]
              exact Nat.add_le_add (Nat.le_refl _) (by decide : 345≤512)
      · rw [list_bad p k ts hk] at hs
        cases hs
  · intro input hs
    cases input with
    | nil => exact Nat.le_refl 3
    | cons k ts =>
      change ((listMeter p (k::ts)).2+headerCharge (k::ts))+2≤(potential ts+512)+3
      have hh := header_bound (k::ts)
      by_cases hk : k≤listLimit
      · cases e : encode 17 k with
        | none =>
          rw [list_no_word p k ts hk e]
          exact Nat.le_trans (Nat.add_le_add (Nat.add_le_add (Nat.le_refl 1) hh)
            (Nat.le_refl 2)) (Nat.le_trans (by decide : 310≤515) (by
              change 515≤potential ts+515
              exact Nat.le_add_left _ _))
        | some c =>
          rw [list_word p k ts hk c e]
          have hb := word_run_all p hp c ts
          rw [(encode_sound 17 k c e).left] at hb
          change (wordRun p c ts).2≤(potential ts+20)+35 at hb
          rw [Nat.add_assoc] at hb
          change (((wordRun p c ts).2+1)+headerCharge (k::ts))+2≤_
          calc
            (((wordRun p c ts).2+1)+headerCharge (k::ts))+2
                ≤ (((potential ts+55)+1)+307)+2 :=
              Nat.add_le_add (Nat.add_le_add (Nat.add_le_add hb (Nat.le_refl 1)) hh)
                (Nat.le_refl 2)
            _ ≤ (potential ts+512)+3 := by
              change (((potential ts+55)+1)+307)+2≤(potential ts+512)+3
              rw [Nat.add_assoc (potential ts) 55 1,
                Nat.add_assoc (potential ts) (55+1) 307,
                Nat.add_assoc (potential ts) ((55+1)+307) 2,
                Nat.add_assoc (potential ts) 512 3]
              exact Nat.add_le_add (Nat.le_refl _) (by decide : 365≤515)
      · rw [list_bad p k ts hk]
        exact Nat.le_trans (Nat.add_le_add (Nat.add_le_add (Nat.le_refl 1) hh)
          (Nat.le_refl 2)) (Nat.le_trans (by decide : 310≤515) (by
            change 515≤potential ts+515
            exact Nat.le_add_left _ _))

theorem nat_amortized : Amortized natMeter := by
  constructor
  · intro ts a rest hs
    cases ts with
    | nil => cases hs
    | cons v vs =>
      change some (v,vs)=some (a,rest) at hs
      have hr : vs=rest := congrArg Prod.snd (Option.some.inj hs)
      rw [← hr]
      change 3+potential vs≤potential vs+512
      rw [Nat.add_comm 3 (potential vs)]
      exact Nat.add_le_add (Nat.le_refl _) (by decide : 3≤512)
  · intro ts hs
    cases ts with
    | nil => exact Nat.le_refl 3
    | cons v vs => cases hs

theorem all_bound {α : Type} (p : ParserMeter α) (hp : Amortized p)
    (ts : List Nat) : (p ts).2≤potential ts+3 := by
  cases e : (p ts).1 with
  | none =>
    exact Nat.le_trans (Nat.le_add_right _ _) (hp.2 ts e)
  | some pair =>
    cases pair with
    | mk a rest =>
      have h := hp.1 ts a rest e
      exact Nat.le_trans (Nat.le_trans (Nat.le_add_right _ _)
        (Nat.le_trans (Nat.le_add_right _ _) h)) (Nat.le_add_right _ _)

theorem nested_nat_amortized : Amortized (chargedList (chargedList natMeter)) :=
  list_amortized _ (list_amortized _ nat_amortized)

theorem nested_nat_bound (ts : List Nat) :
    (chargedList (chargedList natMeter) ts).2≤512*ts.length+3 :=
  all_bound _ nested_nat_amortized ts

theorem nested_nat_refines (ts : List Nat) :
    (chargedList (chargedList natMeter) ts).1=
      ProctorDataParser.listToken (ProctorDataParser.listToken ProctorDataParser.natToken) ts := by
  rw [charged_projection,ProctorParserMeterCompose.list_projection]
  exact ProctorFuelFreeParser.list_congr_pointwise
    (ProctorParserMeterCompose.project (chargedList natMeter))
    (ProctorDataParser.listToken ProctorDataParser.natToken)
    (fun xs => (charged_projection natMeter xs).trans
      (ProctorParserMeterCompose.list_refines natMeter xs)) ts

end ProctorNestedEncoderAmortization

#print axioms ProctorNestedEncoderAmortization.advance_safe
#print axioms ProctorNestedEncoderAmortization.word_run_success
#print axioms ProctorNestedEncoderAmortization.word_run_all
#print axioms ProctorNestedEncoderAmortization.header_bound
#print axioms ProctorNestedEncoderAmortization.charged_projection
#print axioms ProctorNestedEncoderAmortization.list_amortized
#print axioms ProctorNestedEncoderAmortization.nat_amortized
#print axioms ProctorNestedEncoderAmortization.all_bound
#print axioms ProctorNestedEncoderAmortization.nested_nat_amortized
#print axioms ProctorNestedEncoderAmortization.nested_nat_bound
#print axioms ProctorNestedEncoderAmortization.nested_nat_refines
