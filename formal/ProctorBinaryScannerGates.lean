/-! F034 candidate: Boolean arithmetic gate budget along the checked
binary scanner. For every visited digit-classified byte reserve both
counter circuits and the decimal-update circuit, even when a guard
rejects before executing them. Other operations remain uncharged.
This is an executable conservative ledger, not exact gate execution. -/
namespace ProctorBinaryScannerGates
open ProctorBinaryPrimitives (decimalMeter decimal_bound)
open ProctorCheckedBinaryScanner (encode encode_sound narrow narrow_sound
  zeroBits zeroWord checkedDigit)
open ProctorStructuralCounters (bumpBudget bump_sound)
open ProctorScannerCounters (countZero countLimit nextCount next_gate_bound scanCore scanCounted)
open ProctorDecimalBitWidth (bitsValue)
open ProctorBytePrepass (byteOK tokenizeBounded)

def digitGates (v : List Bool) (b : Nat) : Nat :=
  match encode 4 (b-48) with
  | none => 0
  | some d => (decimalMeter v d).2

theorem digit_gate_bound (v : List Bool) (b : Nat) (hv : v.length≤512) :
    digitGates v b≤5155 := by
  unfold digitGates
  cases e : encode 4 (b-48) with
  | none => exact Nat.zero_le _
  | some d =>
    have hd := (encode_sound 4 (b-48) d e).left
    have hb : d.length≤4 := by
      rw [hd]
      exact Nat.le_refl _
    exact (decimal_bound v d 512 hv hb).right

theorem digit_width (v out : List Bool) (b : Nat)
    (h : checkedDigit v b=some out) : out.length≤512 := by
  unfold checkedDigit at h
  cases e : encode 4 (b-48) with
  | none => rw [e] at h; cases h
  | some d =>
    rw [e] at h
    have hw := (narrow_sound 512 (decimalMeter v d).1 out h).left
    rw [hw]
    exact Nat.le_refl _

theorem count_width (c d : List Bool) (h : nextCount c=some d) :
    d.length≤8 := by
  have hw := (bump_sound 8 c countLimit d h).left
  rw [hw]
  exact Nat.le_refl _

def charge (k : Nat) (r : Option (List Nat) × Nat) :
    Option (List Nat) × Nat := (r.1,r.2+k)

def meterCore (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg : List Bool → Nat) :
    List Nat → List Bool → List Bool → List Nat → Option (List Nat) × Nat
  | [],_,c,acc => (if zeroBits c=true then some acc.reverse else none,0)
  | b::bs,v,c,acc =>
    if b=10 then
      if zeroBits c=true then (none,0)
      else meterCore reset cz step next vg cg bs reset cz (bitsValue v::acc)
    else if 48≤b ∧ b≤57 then
      charge (vg v b+cg c)
        (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
        else match next c with
          | none => (none,0)
          | some d =>
            match step v b with
            | none => (none,0)
            | some out => meterCore reset cz step next vg cg bs out d acc)
    else (none,0)

theorem core_projection (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg : List Bool → Nat)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (meterCore reset cz step next vg cg bytes v c acc).1=
      scanCore reset cz step next bytes v c acc := by
  induction bytes generalizing v c acc with
  | nil => rfl
  | cons b bs ih =>
    rw [meterCore,scanCore]
    by_cases lf : b=10
    · rw [if_pos lf,if_pos lf]
      by_cases z : zeroBits c=true
      · rw [if_pos z,if_pos z]
      · rw [if_neg z,if_neg z]
        exact ih reset cz (bitsValue v::acc)
    · rw [if_neg lf,if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit,if_pos digit]
        change (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
          else match next c with
            | none => (none,0)
            | some d => match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next vg cg bs out d acc).1=_
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead,if_pos lead]
        · rw [if_neg lead,if_neg lead]
          cases en : next c with
          | none => rfl
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next vg cg bs out d acc).1=
              (match step v b with
                | none => none
                | some out => scanCore reset cz step next bs out d acc)
            cases es : step v b with
            | none => rfl
            | some out => exact ih out d acc
      · rw [if_neg digit,if_neg digit]

theorem core_bound (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg : List Bool → Nat)
    (hr : reset.length≤512) (hz : cz.length≤8)
    (hs : ∀ v b out, step v b=some out → out.length≤512)
    (hn : ∀ c d, next c=some d → d.length≤8)
    (hg : ∀ v b, v.length≤512 → vg v b≤5155)
    (hc : ∀ c, c.length≤8 → cg c≤80)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) (hw : c.length≤8) :
    (meterCore reset cz step next vg cg bytes v c acc).2≤5235*bytes.length := by
  induction bytes generalizing v c acc with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    rw [meterCore]
    by_cases lf : b=10
    · rw [if_pos lf]
      by_cases z : zeroBits c=true
      · rw [if_pos z]
        exact Nat.zero_le _
      · rw [if_neg z]
        exact Nat.le_trans (ih reset cz (bitsValue v::acc) hr hz) (Nat.le_add_right _ _)
    · rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit]
        have hcost : vg v b+cg c≤5235 := Nat.add_le_add (hg v b hv) (hc c hw)
        change (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
          else match next c with
            | none => (none,0)
            | some d => match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next vg cg bs out d acc).2+
          (vg v b+cg c)≤5235*bs.length+5235
        apply Nat.add_le_add _ hcost
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead]
          exact Nat.zero_le _
        · rw [if_neg lead]
          cases en : next c with
          | none => exact Nat.zero_le _
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next vg cg bs out d acc).2≤_
            cases es : step v b with
            | none => exact Nat.zero_le _
            | some out => exact ih out d acc (hs v b out es) (hn c d en)
      · rw [if_neg digit]
        exact Nat.zero_le _

def countGates (c : List Bool) : Nat := bumpBudget c countLimit

def scanGates := meterCore zeroWord countZero checkedDigit nextCount digitGates countGates

theorem scan_projection (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (scanGates bytes v c acc).1=scanCounted bytes v c acc :=
  core_projection zeroWord countZero checkedDigit nextCount digitGates countGates bytes v c acc

private theorem reset_width : zeroWord.length≤512 := by
  rw [zeroWord, List.length_replicate]

private theorem reset_count_width : countZero.length≤8 := by
  rw [countZero, List.length_replicate]

theorem scan_gate_bound (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) (hc : c.length≤8) :
    (scanGates bytes v c acc).2≤5235*bytes.length :=
  core_bound zeroWord countZero checkedDigit nextCount digitGates countGates
    reset_width reset_count_width (fun v b out h => digit_width v out b h) count_width digit_gate_bound
    next_gate_bound bytes v c acc hv hc

def tokenizeGates (bytes : List Nat) : Option (List Nat) × Nat :=
  if byteOK bytes then scanGates bytes zeroWord countZero [] else (none,0)

theorem tokenize_projection (bytes : List Nat) :
    (tokenizeGates bytes).1=tokenizeBounded bytes := by
  unfold tokenizeGates tokenizeBounded
  by_cases h : byteOK bytes=true
  · rw [if_pos h,if_pos h]
    exact scan_projection bytes zeroWord countZero []
  · rw [if_neg h,if_neg h]

theorem tokenize_refines (bytes : List Nat) :
    (tokenizeGates bytes).1=ProctorDataParser.tokenize bytes :=
  (tokenize_projection bytes).trans (ProctorBytePrepass.tokenize_refines bytes)

theorem tokenize_gate_bound (bytes : List Nat) :
    (tokenizeGates bytes).2≤5235*bytes.length := by
  unfold tokenizeGates
  by_cases h : byteOK bytes=true
  · rw [if_pos h]
    exact scan_gate_bound bytes zeroWord countZero [] reset_width reset_count_width
  · rw [if_neg h]
    exact Nat.zero_le _

end ProctorBinaryScannerGates

#print axioms ProctorBinaryScannerGates.digit_gate_bound
#print axioms ProctorBinaryScannerGates.digit_width
#print axioms ProctorBinaryScannerGates.count_width
#print axioms ProctorBinaryScannerGates.core_projection
#print axioms ProctorBinaryScannerGates.core_bound
#print axioms ProctorBinaryScannerGates.scan_projection
#print axioms ProctorBinaryScannerGates.scan_gate_bound
#print axioms ProctorBinaryScannerGates.tokenize_projection
#print axioms ProctorBinaryScannerGates.tokenize_refines
#print axioms ProctorBinaryScannerGates.tokenize_gate_bound
