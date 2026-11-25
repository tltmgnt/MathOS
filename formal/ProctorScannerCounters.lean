/-! F034 candidate: replace the decimal scanner's digit counter by
checked eight-bit increment and Boolean zero detection. Byte tests,
length prepass, output Nat projection and list operations remain
unrefined. No new total-cost claim. -/
namespace ProctorScannerCounters
open ProctorDecimalBitWidth (bitsValue radix)
open ProctorCheckedBinaryScanner (cap zeroBits zero_sound zero_complete zeroWord zero_word_value checkedDigit checked_digit_refines)
open ProctorStructuralCounters (bumpBelow bump_sound bump_complete bumpBudget bump_gate_bound)
open ProctorDataParser (digitLimit byteLimit)

def countZero : List Bool := List.replicate 8 false
def countLimit : List Bool := [false,false,false,false,false,false,false,true]

theorem count_zero : bitsValue countZero=0 := rfl
theorem count_limit : bitsValue countLimit=digitLimit := rfl

def nextCount (c : List Bool) : Option (List Bool) := bumpBelow 8 c countLimit

theorem next_complete (c : List Bool) (h : bitsValue c<digitLimit) :
    ∃ d, nextCount c=some d ∧ d.length=8 ∧ bitsValue d=bitsValue c+1 := by
  have hl : bitsValue countLimit<cap 8 := by decide
  have hc : bitsValue c<bitsValue countLimit := by
    rw [count_limit]
    exact h
  obtain ⟨d,e⟩ := bump_complete 8 c countLimit hl hc
  have hs := bump_sound 8 c countLimit d e
  exact ⟨d,e,hs.left,hs.right.left⟩

theorem next_reject (c : List Bool) (h : digitLimit≤bitsValue c) :
    nextCount c=none := by
  cases e : nextCount c with
  | none => rfl
  | some d =>
    have hs := bump_sound 8 c countLimit d e
    have bad := hs.right.right
    rw [hs.right.left,count_limit] at bad
    exact False.elim (Nat.not_lt_of_ge h bad)

theorem next_gate_bound (c : List Bool) (h : c.length≤8) :
    bumpBudget c countLimit≤80 :=
  bump_gate_bound 8 c countLimit (by decide) h (by decide)

private theorem count_positive (c : List Bool) :
    zeroBits c≠true ↔ 0<bitsValue c := by
  constructor
  · intro h
    apply Nat.lt_of_not_ge
    intro hz
    exact h (zero_complete c (Nat.eq_zero_of_le_zero hz))
  · intro h z
    have e := zero_sound c z
    rw [e] at h
    cases h

-- Abstract transition contracts prevent proof elaboration from
-- normalizing the concrete 512-bit accumulator or the eight-bit counter.
def scanCore (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool)) :
    List Nat → List Bool → List Bool → List Nat → Option (List Nat)
  | [],_,c,acc => if zeroBits c=true then some acc.reverse else none
  | b::bs,v,c,acc =>
    if b=10 then
      if zeroBits c=true then none
      else scanCore reset cz step next bs reset cz (bitsValue v::acc)
    else if 48≤b ∧ b≤57 then
      if zeroBits c≠true ∧ zeroBits v=true then none
      else match next c with
        | none => none
        | some d =>
          match step v b with
          | none => none
          | some out => scanCore reset cz step next bs out d acc
    else none

theorem core_refines (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (hr : bitsValue reset=0) (hc : bitsValue cz=0)
    (hs : ∀ (v : List Bool) (k b : Nat),
      bitsValue v+1≤radix k → k<digitLimit → b≤57 →
      ∃ out, step v b=some out ∧ out.length=512 ∧
        bitsValue out=10*bitsValue v+(b-48) ∧ bitsValue out+1≤radix (k+1))
    (hn : ∀ c : List Bool, bitsValue c<digitLimit →
      ∃ d, next c=some d ∧ d.length=8 ∧ bitsValue d=bitsValue c+1)
    (hf : ∀ c : List Bool, digitLimit≤bitsValue c → next c=none)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : bitsValue v+1≤radix (bitsValue c)) :
    scanCore reset cz step next bytes v c acc=
      ProctorDataParser.scan bytes (bitsValue v) (bitsValue c) acc := by
  induction bytes generalizing v c acc with
  | nil =>
    rw [scanCore,ProctorDataParser.scan]
    by_cases z : bitsValue c=0
    · rw [if_pos (zero_complete c z),if_pos z]
    · have nz : ¬ zeroBits c=true := fun e => z (zero_sound c e)
      rw [if_neg nz,if_neg z]
  | cons b bs ih =>
    rw [scanCore,ProctorDataParser.scan]
    by_cases lf : b=10
    · rw [if_pos lf] <;> try rw [if_pos lf]
      by_cases z : bitsValue c=0
      · rw [if_pos (zero_complete c z),if_pos z]
      · have nz : ¬ zeroBits c=true := fun e => z (zero_sound c e)
        rw [if_neg nz,if_neg z]
        have hz : bitsValue reset+1≤radix (bitsValue cz) := by
          rw [hr,hc]
          exact Nat.le_refl 1
        have e := ih reset cz (bitsValue v::acc) hz
        rw [hr,hc] at e
        exact e
    · rw [if_neg lf] <;> try rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit] <;> try rw [if_pos digit]
        by_cases lead : bitsValue c>0 ∧ bitsValue v=0
        · have lb : zeroBits c≠true ∧ zeroBits v=true :=
            ⟨(count_positive c).mpr lead.left,zero_complete v lead.right⟩
          have g : bitsValue c≥digitLimit ∨ (bitsValue c>0 ∧ bitsValue v=0) :=
            Or.inr lead
          rw [if_pos lb,if_pos g]
        · have lb : ¬ (zeroBits c≠true ∧ zeroBits v=true) :=
            fun e => lead ⟨(count_positive c).mp e.left,zero_sound v e.right⟩
          rw [if_neg lb]
          by_cases over : digitLimit≤bitsValue c
          · have g : bitsValue c≥digitLimit ∨ (bitsValue c>0 ∧ bitsValue v=0) :=
              Or.inl over
            rw [if_pos g,hf c over]
          · have g : ¬ (bitsValue c≥digitLimit ∨ (bitsValue c>0 ∧ bitsValue v=0)) :=
              fun e => e.elim over lead
            rw [if_neg g]
            have hk : bitsValue c<digitLimit := Nat.lt_of_not_ge over
            obtain ⟨d,ed,_,vd⟩ := hn c hk
            obtain ⟨out,eo,_,vo,hi⟩ := hs v (bitsValue c) b hv hk digit.right
            rw [ed]
            change (match step v b with
              | none => none
              | some u => scanCore reset cz step next bs u d acc)=_
            rw [eo]
            have hd : bitsValue out+1≤radix (bitsValue d) := by
              rw [vd]
              exact hi
            have e := ih out d acc hd
            rw [vo,vd] at e
            exact e
      · rw [if_neg digit] <;> try rw [if_neg digit]

def scanCounted (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    Option (List Nat) :=
  scanCore zeroWord countZero checkedDigit nextCount bytes v c acc

theorem scan_refines (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : bitsValue v+1≤radix (bitsValue c)) :
    scanCounted bytes v c acc=
      ProctorDataParser.scan bytes (bitsValue v) (bitsValue c) acc :=
  core_refines zeroWord countZero checkedDigit nextCount zero_word_value
    count_zero checked_digit_refines next_complete next_reject bytes v c acc hv

private theorem initial_scan (bytes : List Nat) (v c : List Bool)
    (hv : bitsValue v=0) (hc : bitsValue c=0) :
    scanCounted bytes v c []=ProctorDataParser.scan bytes 0 0 [] := by
  have hi : bitsValue v+1≤radix (bitsValue c) := by
    rw [hv,hc]
    exact Nat.le_refl 1
  have e := scan_refines bytes v c [] hi
  rw [hv,hc] at e
  exact e

def tokenizeCounted (bytes : List Nat) : Option (List Nat) :=
  if bytes.length≤byteLimit then scanCounted bytes zeroWord countZero [] else none

theorem tokenize_refines (bytes : List Nat) :
    tokenizeCounted bytes=ProctorDataParser.tokenize bytes := by
  unfold tokenizeCounted ProctorDataParser.tokenize
  by_cases h : bytes.length≤byteLimit
  · rw [if_pos h] <;> try rw [if_pos h]
    exact initial_scan bytes zeroWord countZero zero_word_value count_zero
  · rw [if_neg h] <;> try rw [if_neg h]

end ProctorScannerCounters

#print axioms ProctorScannerCounters.count_zero
#print axioms ProctorScannerCounters.count_limit
#print axioms ProctorScannerCounters.next_complete
#print axioms ProctorScannerCounters.next_reject
#print axioms ProctorScannerCounters.next_gate_bound
#print axioms ProctorScannerCounters.core_refines
#print axioms ProctorScannerCounters.scan_refines
#print axioms ProctorScannerCounters.tokenize_refines
