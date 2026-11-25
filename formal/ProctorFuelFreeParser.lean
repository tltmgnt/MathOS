/-! F034 candidate: fuel-free binary iteration by composition.
The iterator recurses structurally on the word, doubling an optional
state transition at each bit. No executable Nat recursion fuel or
decoded counter is used in this loop. Closure and call costs are not
yet metered. -/
namespace ProctorFuelFreeParser
open ProctorDecimalBitWidth (bitsValue)
open ProctorDataParser (Parser manyAux listToken listLimit)
open ProctorCheckedBinaryScanner (encode encode_complete encode_sound)
open ProctorStructuralCounters (list_capacity)

def doubleStep {σ : Type} (step : σ → Option σ) (s : σ) : Option σ :=
  match step s with
  | none => none
  | some t => step t

-- Nat specification, not used in the executable word iterator.
def iterNat {σ : Type} (step : σ → Option σ) : Nat → σ → Option σ
  | 0,s => some s
  | n+1,s =>
    match step s with
    | none => none
    | some t => iterNat step n t

def iterWord {σ : Type} : List Bool → (σ → Option σ) → σ → Option σ
  | [],_,s => some s
  | false::bs,step,s => iterWord bs (doubleStep step) s
  | true::bs,step,s =>
    match step s with
    | none => none
    | some t => iterWord bs (doubleStep step) t

theorem double_refines {σ : Type} (step : σ → Option σ) (n : Nat) (s : σ) :
    iterNat (doubleStep step) n s=iterNat step (2*n) s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    change (match doubleStep step s with
      | none => none
      | some t => iterNat (doubleStep step) n t)=iterNat step (2*n+2) s
    change (match (match step s with
      | none => none
      | some t => step t) with
      | none => none
      | some u => iterNat (doubleStep step) n u)=
      (match step s with
      | none => none
      | some t => match step t with
        | none => none
        | some u => iterNat step (2*n) u)
    cases e : step s with
    | none => rfl
    | some t =>
      change (match step t with
        | none => none
        | some u => iterNat (doubleStep step) n u)=
        (match step t with
        | none => none
        | some u => iterNat step (2*n) u)
      cases step t with
      | none => rfl
      | some u => exact ih u

theorem word_refines {σ : Type} (bs : List Bool) (step : σ → Option σ) (s : σ) :
    iterWord bs step s=iterNat step (bitsValue bs) s := by
  induction bs generalizing step s with
  | nil => rfl
  | cons b bs ih =>
    cases b with
    | false =>
      change iterWord bs (doubleStep step) s=iterNat step (0+2*bitsValue bs) s
      rw [Nat.zero_add]
      exact (ih (doubleStep step) s).trans (double_refines step (bitsValue bs) s)
    | true =>
      change (match step s with
        | none => none
        | some t => iterWord bs (doubleStep step) t)=iterNat step (1+2*bitsValue bs) s
      rw [Nat.add_comm 1 (2*bitsValue bs)]
      change (match step s with
        | none => none
        | some t => iterWord bs (doubleStep step) t)=
        (match step s with
        | none => none
        | some t => iterNat step (2*bitsValue bs) t)
      cases e : step s with
      | none => rfl
      | some t => exact (ih (doubleStep step) t).trans (double_refines step (bitsValue bs) t)

abbrev State (α : Type) := List α × List Nat

def advance {α : Type} (p : Parser α) (s : State α) : Option (State α) :=
  match p s.2 with
  | none => none
  | some (a,rest) => some (a::s.1,rest)

def finish {α : Type} : Option (State α) → Option (List α × List Nat)
  | none => none
  | some (acc,ts) => some (acc.reverse,ts)

private theorem nat_parser {α : Type} (p : Parser α) (n : Nat)
    (ts : List Nat) (acc : List α) :
    finish (iterNat (advance p) n (acc,ts))=manyAux p n ts acc := by
  induction n generalizing ts acc with
  | zero => rfl
  | succ n ih =>
    rw [iterNat, manyAux]
    unfold advance
    change finish (match (match p ts with
      | none => none
      | some (a,rest) => some (a::acc,rest)) with
      | none => none
      | some s => iterNat (advance p) n s)=_
    cases e : p ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => exact ih rest (a::acc)

def manyWord {α : Type} (p : Parser α) (c : List Bool)
    (ts : List Nat) (acc : List α) : Option (List α × List Nat) :=
  finish (iterWord c (advance p) (acc,ts))

theorem many_word_refines {α : Type} (p : Parser α) (c : List Bool)
    (ts : List Nat) (acc : List α) :
    manyWord p c ts acc=manyAux p (bitsValue c) ts acc := by
  unfold manyWord
  rw [word_refines]
  exact nat_parser p (bitsValue c) ts acc

-- The existing Nat list-limit guard and checked conversion remain.
def listWord {α : Type} (p : Parser α) : Parser (List α)
  | [] => none
  | k::ts =>
    if k≤listLimit then
      match encode 17 k with
      | none => none
      | some c => manyWord p c ts []
    else none

theorem list_word_refines {α : Type} (p : Parser α) (ts : List Nat) :
    listWord p ts=listToken p ts := by
  cases ts with
  | nil => rfl
  | cons k ts =>
    change (if k≤listLimit then
      match encode 17 k with
      | none => none
      | some c => manyWord p c ts []
      else none)=(if k≤listLimit then manyAux p k ts [] else none)
    by_cases h : k≤listLimit
    · rw [if_pos h,if_pos h]
      obtain ⟨c,e⟩ := encode_complete 17 k (Nat.lt_of_le_of_lt h list_capacity)
      have hv := (encode_sound 17 k c e).right
      rw [e]
      change manyWord p c ts []=manyAux p k ts []
      rw [many_word_refines,hv]
    · rw [if_neg h,if_neg h]

-- Pointwise substitution for nested parsers, without funext.
theorem list_congr_pointwise {α : Type} (p q : Parser α)
    (h : ∀ ts, p ts=q ts) (ts : List Nat) :
    listWord p ts=listToken q ts := by
  rw [list_word_refines]
  have hm : ∀ (k : Nat) (xs : List Nat) (acc : List α),
      manyAux p k xs acc=manyAux q k xs acc := by
    intro k
    induction k with
    | zero => intro xs acc; rfl
    | succ k ih =>
      intro xs acc
      change (do
        let (a,rest) ← p xs
        manyAux p k rest (a::acc))=(do
        let (a,rest) ← q xs
        manyAux q k rest (a::acc))
      rw [h xs]
      cases e : q xs with
      | none => rfl
      | some pair =>
        cases pair with
        | mk a rest => exact ih rest (a::acc)
  cases ts with
  | nil => rfl
  | cons k xs =>
    change (if k≤listLimit then manyAux p k xs [] else none)=
      (if k≤listLimit then manyAux q k xs [] else none)
    rw [hm k xs []]

end ProctorFuelFreeParser

#print axioms ProctorFuelFreeParser.double_refines
#print axioms ProctorFuelFreeParser.word_refines
#print axioms ProctorFuelFreeParser.many_word_refines
#print axioms ProctorFuelFreeParser.list_word_refines
#print axioms ProctorFuelFreeParser.list_congr_pointwise
