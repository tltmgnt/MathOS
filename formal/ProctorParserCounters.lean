/-! F034 candidate: checked binary remaining-item counter for the
generic list parser. A separate Nat structural fuel is deliberately
retained to make recursion constructive; this is not a complete
binary control-machine refinement. -/
namespace ProctorParserCounters
open ProctorDataParser (Parser manyAux listToken listLimit)
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedBinaryScanner (encode encode_sound encode_complete zeroBits zero_complete)
open ProctorStructuralCounters (list_capacity)
open ProctorCheckedDecrement (decMeter dec_sound dec_complete dec_reject_iff dec_visit_bound)

-- Fuel is an explicit executable recursion safeguard, not a ghost.
-- On reachable states it is at least the value of the binary word.
def manyBits {α : Type} (p : Parser α) :
    Nat → List Bool → List Nat → List α → Option (List α × List Nat)
  | 0,c,ts,acc => if zeroBits c=true then some (acc.reverse,ts) else none
  | f+1,c,ts,acc =>
    match (decMeter c).1 with
    | none => some (acc.reverse,ts)
    | some d => do
      let (a,rest) ← p ts
      manyBits p f d rest (a::acc)

theorem many_refines {α : Type} (p : Parser α) (f : Nat)
    (c : List Bool) (ts : List Nat) (acc : List α)
    (h : bitsValue c≤f) :
    manyBits p f c ts acc=manyAux p (bitsValue c) ts acc := by
  induction f generalizing c ts acc with
  | zero =>
    have hz : bitsValue c=0 := Nat.eq_zero_of_le_zero h
    rw [manyBits,if_pos (zero_complete c hz),hz]
    rfl
  | succ f ih =>
    cases e : bitsValue c with
    | zero =>
      have hd : (decMeter c).1=none := (dec_reject_iff c).mpr e
      rw [manyBits,hd]
      rfl
    | succ k =>
      have hp : 0<bitsValue c := by
        rw [e]
        exact Nat.succ_le_succ (Nat.zero_le k)
      obtain ⟨d,ed⟩ := dec_complete c hp
      have hs := (dec_sound c d ed).right
      rw [e] at hs
      have hv : bitsValue d=k := Nat.succ.inj hs
      have hk : k≤f := by
        rw [e] at h
        exact Nat.le_of_succ_le_succ h
      have hf : bitsValue d≤f := by
        rw [hv]
        exact hk
      rw [manyBits,ed]
      change (do
        let (a,rest) ← p ts
        manyBits p f d rest (a::acc))=(do
        let (a,rest) ← p ts
        manyAux p k rest (a::acc))
      cases ep : p ts with
      | none => rfl
      | some pair =>
        cases pair with
        | mk a rest =>
          change manyBits p f d rest (a::acc)=manyAux p k rest (a::acc)
          have he := ih d rest (a::acc) hf
          rw [hv] at he
          exact he

-- The list length token remains a Nat boundary; checked encoding
-- after the original limit guard cannot truncate it.
def listBits {α : Type} (p : Parser α) : Parser (List α)
  | [] => none
  | k::ts =>
    if k≤listLimit then
      match encode 17 k with
      | none => none
      | some c => manyBits p listLimit c ts []
    else none

theorem list_refines {α : Type} (p : Parser α) (ts : List Nat) :
    listBits p ts=listToken p ts := by
  cases ts with
  | nil => rfl
  | cons k ts =>
    change (if k≤listLimit then
      match encode 17 k with
      | none => none
      | some c => manyBits p listLimit c ts []
      else none)=(if k≤listLimit then manyAux p k ts [] else none)
    by_cases h : k≤listLimit
    · rw [if_pos h,if_pos h]
      obtain ⟨c,e⟩ := encode_complete 17 k (Nat.lt_of_le_of_lt h list_capacity)
      have hv := (encode_sound 17 k c e).right
      rw [e]
      change manyBits p listLimit c ts []=manyAux p k ts []
      have hf : bitsValue c≤listLimit := by
        rw [hv]
        exact h
      have he := many_refines p listLimit c ts [] hf
      rw [hv] at he
      exact he
    · rw [if_neg h,if_neg h]

theorem list_function_refines {α : Type} (p : Parser α) :
    ∀ ts, listBits p ts=listToken p ts := list_refines p

theorem counter_width (k : Nat) (c : List Bool)
    (h : encode 17 k=some c) : c.length=17 :=
  (encode_sound 17 k c h).left

theorem step_width (c d : List Bool) (hc : c.length=17)
    (h : (decMeter c).1=some d) : d.length=17 :=
  (dec_sound c d h).left.trans hc

theorem step_visits (c : List Bool) (hc : c.length=17) :
    (decMeter c).2≤17 := by
  have h := dec_visit_bound c
  rw [hc] at h
  exact h

end ProctorParserCounters

#print axioms ProctorParserCounters.many_refines
#print axioms ProctorParserCounters.list_refines
#print axioms ProctorParserCounters.list_function_refines
#print axioms ProctorParserCounters.counter_width
#print axioms ProctorParserCounters.step_width
#print axioms ProctorParserCounters.step_visits
