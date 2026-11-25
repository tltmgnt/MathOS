/-! F034: selected DIMACS lexical primitive charges.
Header traversal uses a tail accumulator. Splitting uses structural
charges for full scans and reversals. Decimal words reuse the verified
custom scanner. This is not a complete lexer runtime model. -/
namespace ProctorDimacsLexMeter
open ProctorHallDeficiency
open ProctorDimacsInput (takeHeader splitWords white naturalWord signedWord)
open ProctorDimacsLexical (Header Split flush header_sound split_sound)
open ProctorScannerMeter (tokenizeMeter tokenize_value tokenize_bound tokenBudget)

private theorem len_append {α : Type} (a b : List α) :
    (a++b).length=a.length+b.length := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++b).length+1=(xs.length+1)+b.length
    rw [ih]
    exact (Nat.succ_add xs.length b.length).symm

private theorem revAux_len {α : Type} (a b : List α) :
    (a.reverseAux b).length=a.length+b.length := by
  induction a generalizing b with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs.reverseAux (x::b)).length=(xs.length+1)+b.length
    rw [ih (x::b)]
    exact (Nat.succ_add xs.length b.length).symm

private theorem rev_len {α : Type} (a : List α) :
    a.reverse.length=a.length := revAux_len a []

def headerAux : List Nat → List Nat → Nat →
    Option (List Nat × List Nat) × Nat
  | [],_,k => (none,k+1)
  | b::bs,acc,k =>
    if b=10 then (some (acc.reverse,bs),k+1)
    else headerAux bs (b::acc) (k+1)

theorem header_aux_value (bytes acc : List Nat) (k : Nat) :
    (headerAux bytes acc k).1=takeHeader bytes acc := by
  induction bytes generalizing acc k with
  | nil => rfl
  | cons b bs ih =>
    change (if b=10 then (some (acc.reverse,bs),k+1)
      else headerAux bs (b::acc) (k+1)).1 =
      (if b=10 then some (acc.reverse,bs) else takeHeader bs (b::acc))
    by_cases h : b=10
    · rw [if_pos h,if_pos h]
    · rw [if_neg h,if_neg h]
      exact ih (b::acc) (k+1)

theorem header_aux_bound (bytes acc : List Nat) (k : Nat) :
    (headerAux bytes acc k).2≤(k+bytes.length)+1 := by
  induction bytes generalizing acc k with
  | nil => exact Nat.le_refl _
  | cons b bs ih =>
    change (if b=10 then (some (acc.reverse,bs),k+1)
      else headerAux bs (b::acc) (k+1)).2≤k+(bs.length+1)+1
    by_cases h : b=10
    · rw [if_pos h]
      exact Nat.succ_le_succ (Nat.le_add_right _ _)
    · rw [if_neg h]
      have hh := ih (b::acc) (k+1)
      rw [Nat.succ_add k bs.length] at hh
      exact hh

theorem header_length (bytes acc head body : List Nat)
    (h : Header bytes acc head body) :
    head.length≤bytes.length+acc.length := by
  induction h with
  | endLine rest acc =>
    rw [rev_len]
    exact Nat.le_add_left _ _
  | @next b bs acc head body ne sub ih =>
    change head.length≤(bs.length+1)+acc.length
    rw [Nat.succ_add bs.length acc.length]
    exact ih

def headerReverseCharge : Option (List Nat × List Nat) → Nat
  | none => 0
  | some (h,_) => h.length

def headerMeter (bytes : List Nat) : Option (List Nat × List Nat) × Nat :=
  let r := headerAux bytes [] 0
  (r.1,r.2+headerReverseCharge r.1)

theorem header_value (bytes : List Nat) :
    (headerMeter bytes).1=takeHeader bytes [] :=
  header_aux_value bytes [] 0

theorem header_bound (bytes : List Nat) :
    (headerMeter bytes).2≤(bytes.length+1)+bytes.length := by
  have hs := header_aux_bound bytes [] 0
  rw [Nat.zero_add] at hs
  have hr : headerReverseCharge (takeHeader bytes [])≤bytes.length := by
    cases e : takeHeader bytes [] with
    | none => exact Nat.zero_le _
    | some pair =>
      cases pair with
      | mk h b => exact header_length bytes [] h b (header_sound bytes [] h b e)
  unfold headerMeter
  change (headerAux bytes [] 0).2+headerReverseCharge (headerAux bytes [] 0).1≤_
  rw [header_aux_value]
  exact Nat.add_le_add hs hr

def wordMass : List (List Nat) → Nat
  | [] => 0
  | w::ws => w.length+wordMass ws

private theorem reverse_aux_mass (a b : List (List Nat)) :
    wordMass (a.reverseAux b)=wordMass a+wordMass b := by
  induction a generalizing b with
  | nil => exact (Nat.zero_add _).symm
  | cons w ws ih =>
    change wordMass (ws.reverseAux (w::b))=(w.length+wordMass ws)+wordMass b
    rw [ih (w::b)]
    change wordMass ws+(w.length+wordMass b)=(w.length+wordMass ws)+wordMass b
    rw [← Nat.add_assoc,Nat.add_comm (wordMass ws) w.length]

private theorem reverse_mass (a : List (List Nat)) :
    wordMass a.reverse=wordMass a :=
  reverse_aux_mass a []

private theorem flush_mass (w : List Nat) (a : List (List Nat)) :
    wordMass (flush w a)=w.length+wordMass a := by
  cases w with
  | nil => exact (Nat.zero_add _).symm
  | cons b bs =>
    change wordMass ((b::bs).reverse::a)=(b::bs).length+wordMass a
    change (b::bs).reverse.length+wordMass a=(b::bs).length+wordMass a
    rw [rev_len]

theorem split_mass (bytes word : List Nat) (acc out : List (List Nat))
    (h : Split bytes word acc out) :
    wordMass out≤bytes.length+word.length+wordMass acc := by
  induction h with
  | done w a =>
    change wordMass (flush w a).reverse≤0+w.length+wordMass a
    rw [reverse_mass,flush_mass,Nat.zero_add] <;> exact Nat.le_refl _
  | @sep b bs w a out sp sub ih =>
    change wordMass out≤bs.length+0+wordMass (flush w a) at ih
    rw [flush_mass] at ih
    change wordMass out≤(bs.length+1)+w.length+wordMass a
    calc
      wordMass out ≤ bs.length+(w.length+wordMass a) := ih
      _ = bs.length+w.length+wordMass a := (Nat.add_assoc _ _ _).symm
      _ ≤ (bs.length+1)+w.length+wordMass a :=
        Nat.add_le_add (Nat.add_le_add (Nat.le_succ _) (Nat.le_refl _)) (Nat.le_refl _)
  | @char b bs w a out sp sub ih =>
    change wordMass out≤bs.length+(w.length+1)+wordMass a at ih
    change wordMass out≤(bs.length+1)+w.length+wordMass a
    rw [Nat.succ_add bs.length w.length]
    exact ih

-- Each input byte is visited, as is EOF. Each non-space byte is
-- reversed once inside a word; each completed word is reversed
-- once in the outer list. Count those reversal cells structurally
-- from the output, not by an instrumented reverse implementation.
def splitMeter (bytes : List Nat) : List (List Nat) × Nat :=
  let ws := splitWords bytes [] []
  (ws,(bytes.length+1)+wordMass ws+ws.length)

theorem split_value (bytes : List Nat) :
    (splitMeter bytes).1=splitWords bytes [] [] := rfl

theorem split_bound (bytes : List Nat) :
    (splitMeter bytes).2≤(bytes.length+1)+bytes.length+bytes.length := by
  have h := split_sound bytes [] []
  have hm := split_mass bytes [] [] _ h
  have hc := ProctorDimacsSize.split_count bytes [] [] _ h
  exact Nat.add_le_add (Nat.add_le_add (Nat.le_refl _) hm) hc

-- One charge per copied cell of word ++ [LF], scanner charges,
-- and one result-shape test (not each pattern comparison).
def naturalMeter (word : List Nat) : Option Nat × Nat :=
  let m := tokenizeMeter (word++[10])
  let result := match m.1 with
    | some [v] => some v
    | _ => none
  (result,word.length+m.2+1)

theorem natural_value (word : List Nat) :
    (naturalMeter word).1=naturalWord word := by
  unfold naturalMeter naturalWord
  change (match (tokenizeMeter (word++[10])).1 with
    | some [v] => some v | _ => none) =
    (match ProctorDataParser.tokenize (word++[10]) with
    | some [v] => some v | _ => none)
  rw [tokenize_value]

def naturalUnit (n : Nat) : Nat := n+((n+2)+(n+2)+(n+1))+1

theorem natural_bound (word : List Nat) :
    (naturalMeter word).2≤naturalUnit word.length := by
  have h := tokenize_bound (word++[10])
  unfold tokenBudget at h
  rw [len_append] at h
  exact Nat.add_le_add (Nat.add_le_add (Nat.le_refl _) h) (Nat.le_refl 1)

theorem natural_mono (a b : Nat) (h : a≤b) :
    naturalUnit a≤naturalUnit b :=
  Nat.add_le_add (Nat.add_le_add h
    (Nat.add_le_add (Nat.add_le_add
      (Nat.add_le_add h (Nat.le_refl 2)) (Nat.add_le_add h (Nat.le_refl 2)))
      (Nat.succ_le_succ h))) (Nat.le_refl 1)

def signedMeter : List Nat → Option Literal × Nat
  | [] => (none,1)
  | b::ds =>
    if b=45 then
      let m := naturalMeter ds
      let out := match m.1 with
        | none => none
        | some v => if v=0 then none else some (v,false)
      (out,m.2+2)
    else
      let m := naturalMeter (b::ds)
      (m.1.map (fun v => (v,true)),m.2+1)

theorem signed_value (w : List Nat) :
    (signedMeter w).1=signedWord w := by
  cases w with
  | nil => rfl
  | cons b ds =>
    unfold signedMeter signedWord
    by_cases h : b=45
    · rw [if_pos h,if_pos h]
      change (match (naturalMeter ds).1 with
        | none => none
        | some v => if v=0 then none else some (v,false)) =
        (do let v ← naturalWord ds
            if v=0 then none else some (v,false))
      rw [natural_value]
      cases naturalWord ds <;> rfl
    · rw [if_neg h,if_neg h]
      change (naturalMeter (b::ds)).1.map (fun v => (v,true)) =
        (do let v ← naturalWord (b::ds)
            some (v,true))
      rw [natural_value]
      cases naturalWord (b::ds) <;> rfl

def signedUnit (n : Nat) : Nat := naturalUnit n+2

theorem signed_bound (w : List Nat) :
    (signedMeter w).2≤signedUnit w.length := by
  cases w with
  | nil => exact (by decide : 1≤signedUnit 0)
  | cons b ds =>
    unfold signedMeter signedUnit
    by_cases h : b=45
    · rw [if_pos h]
      exact Nat.add_le_add (Nat.le_trans (natural_bound ds)
        (natural_mono _ _ (Nat.le_succ _))) (Nat.le_refl 2)
    · rw [if_neg h]
      exact Nat.add_le_add (natural_bound (b::ds)) (by decide : 1≤2)

end ProctorDimacsLexMeter

#print axioms ProctorDimacsLexMeter.header_aux_value
#print axioms ProctorDimacsLexMeter.header_aux_bound
#print axioms ProctorDimacsLexMeter.header_length
#print axioms ProctorDimacsLexMeter.header_value
#print axioms ProctorDimacsLexMeter.header_bound
#print axioms ProctorDimacsLexMeter.split_mass
#print axioms ProctorDimacsLexMeter.split_value
#print axioms ProctorDimacsLexMeter.split_bound
#print axioms ProctorDimacsLexMeter.natural_value
#print axioms ProctorDimacsLexMeter.natural_bound
#print axioms ProctorDimacsLexMeter.natural_mono
#print axioms ProctorDimacsLexMeter.signed_value
#print axioms ProctorDimacsLexMeter.signed_bound
