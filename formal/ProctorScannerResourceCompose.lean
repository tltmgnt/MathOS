/-! F034 candidate: selected scanner structural visit reservations
along the verified checked scanner, combined with gate reservations
and byte prepass visits. Separate resource coordinates, not runtime. -/
namespace ProctorScannerResourceCompose
open ProctorCheckedBinaryScanner (zeroBits zeroWord checkedDigit)
open ProctorScannerCounters (scanCore scanCounted countZero nextCount)
open ProctorNarrowVisits (zeroMeter zero_bound digitNarrowMeter digit_bound countNarrowMeter count_bound)
open ProctorBinaryScannerGates (charge digit_width count_width tokenizeGates tokenize_gate_bound)
open ProctorDecimalBitWidth (bitsValue)
open ProctorBytePrepass (byteOK tokenizeBounded visits byteWord byte_visit_length_bound)

-- Reserve zero tests and both narrowing operations on visited digit
-- bytes, even if an earlier guard would skip a later operation.
def digitVisits (v : List Bool) (b : Nat) : Nat :=
  (zeroMeter v).2+(digitNarrowMeter v b).2

def counterVisits (c : List Bool) : Nat :=
  (zeroMeter c).2+(countNarrowMeter c).2

theorem digit_visit_bound (v : List Bool) (b : Nat) (h : v.length≤512) :
    digitVisits v b≤1029 :=
  Nat.add_le_add (Nat.le_trans (zero_bound v) h) (digit_bound v b h)

theorem counter_visit_bound (c : List Bool) (h : c.length≤8) :
    counterVisits c≤17 :=
  Nat.add_le_add (Nat.le_trans (zero_bound c) h) (count_bound c h)

def visitCore (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg zg : List Bool → Nat) :
    List Nat → List Bool → List Bool → List Nat → Option (List Nat) × Nat
  | [],_,c,acc => (if zeroBits c=true then some acc.reverse else none,zg c)
  | b::bs,v,c,acc =>
    if b=10 then
      charge (zg c)
        (if zeroBits c=true then (none,0)
        else visitCore reset cz step next vg cg zg bs reset cz (bitsValue v::acc))
    else if 48≤b ∧ b≤57 then
      charge (vg v b+cg c)
        (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
        else match next c with
          | none => (none,0)
          | some d => match step v b with
            | none => (none,0)
            | some out => visitCore reset cz step next vg cg zg bs out d acc)
    else (none,0)

theorem core_projection (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg zg : List Bool → Nat)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (visitCore reset cz step next vg cg zg bytes v c acc).1=
      scanCore reset cz step next bytes v c acc := by
  induction bytes generalizing v c acc with
  | nil => rfl
  | cons b bs ih =>
    rw [visitCore,scanCore]
    by_cases lf : b=10
    · rw [if_pos lf,if_pos lf]
      change (if zeroBits c=true then (none,0)
        else visitCore reset cz step next vg cg zg bs reset cz (bitsValue v::acc)).1=_
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
              | some out => visitCore reset cz step next vg cg zg bs out d acc).1=_
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead,if_pos lead]
        · rw [if_neg lead,if_neg lead]
          cases en : next c with
          | none => rfl
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => visitCore reset cz step next vg cg zg bs out d acc).1=
              (match step v b with
                | none => none
                | some out => scanCore reset cz step next bs out d acc)
            cases es : step v b with
            | none => rfl
            | some out => exact ih out d acc
      · rw [if_neg digit,if_neg digit]

private theorem shift (a b c : Nat) : (a+b)+c=(a+c)+b := by
  calc
    (a+b)+c = a+(b+c) := Nat.add_assoc _ _ _
    _ = a+(c+b) := congrArg (fun n => a+n) (Nat.add_comm _ _)
    _ = (a+c)+b := (Nat.add_assoc _ _ _).symm

theorem core_bound (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg zg : List Bool → Nat)
    (hr : reset.length≤512) (hz : cz.length≤8)
    (hs : ∀ v b out, step v b=some out → out.length≤512)
    (hn : ∀ c d, next c=some d → d.length≤8)
    (hg : ∀ v b, v.length≤512 → vg v b≤1029)
    (hc : ∀ c, c.length≤8 → cg c≤17)
    (ht : ∀ c, c.length≤8 → zg c≤8)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) (hw : c.length≤8) :
    (visitCore reset cz step next vg cg zg bytes v c acc).2≤1046*bytes.length+8 := by
  induction bytes generalizing v c acc with
  | nil => exact ht c hw
  | cons b bs ih =>
    rw [visitCore]
    change _≤(1046*bs.length+1046)+8
    rw [shift (1046*bs.length) 1046 8]
    by_cases lf : b=10
    · rw [if_pos lf]
      change (if zeroBits c=true then (none,0)
        else visitCore reset cz step next vg cg zg bs reset cz (bitsValue v::acc)).2+
        zg c≤(1046*bs.length+8)+1046
      apply Nat.add_le_add _ (Nat.le_trans (ht c hw) (by decide : 8≤1046))
      by_cases z : zeroBits c=true
      · rw [if_pos z]
        exact Nat.zero_le _
      · rw [if_neg z]
        exact ih reset cz (bitsValue v::acc) hr hz
    · rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit]
        have hcost : vg v b+cg c≤1046 := Nat.add_le_add (hg v b hv) (hc c hw)
        change (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
          else match next c with
            | none => (none,0)
            | some d => match step v b with
              | none => (none,0)
              | some out => visitCore reset cz step next vg cg zg bs out d acc).2+
          (vg v b+cg c)≤(1046*bs.length+8)+1046
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
              | some out => visitCore reset cz step next vg cg zg bs out d acc).2≤_
            cases es : step v b with
            | none => exact Nat.zero_le _
            | some out => exact ih out d acc (hs v b out es) (hn c d en)
      · rw [if_neg digit]
        exact Nat.zero_le _

def zeroVisits (c : List Bool) : Nat := (zeroMeter c).2

def scanVisits := visitCore zeroWord countZero checkedDigit nextCount
  digitVisits counterVisits zeroVisits

private theorem reset_length (w : Nat) : (List.replicate w false).length=w := by
  induction w with
  | zero => rfl
  | succ w ih =>
    change (List.replicate w false).length+1=w+1
    exact congrArg Nat.succ ih

private theorem reset_width : zeroWord.length≤512 := by
  rw [zeroWord,reset_length]
  exact Nat.le_refl 512

private theorem count_reset_width : countZero.length≤8 := by
  rw [countZero,reset_length]
  exact Nat.le_refl 8

theorem scan_projection (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (scanVisits bytes v c acc).1=scanCounted bytes v c acc :=
  core_projection zeroWord countZero checkedDigit nextCount digitVisits
    counterVisits zeroVisits bytes v c acc

theorem scan_bound (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) (hc : c.length≤8) :
    (scanVisits bytes v c acc).2≤1046*bytes.length+8 :=
  core_bound zeroWord countZero checkedDigit nextCount digitVisits counterVisits zeroVisits
    reset_width count_reset_width (fun v b out h => digit_width v out b h)
    count_width digit_visit_bound counter_visit_bound
    (fun c h => Nat.le_trans (zero_bound c) h) bytes v c acc hv hc

def tokenizeVisits (bytes : List Nat) : Option (List Nat) × Nat :=
  if byteOK bytes then scanVisits bytes zeroWord countZero [] else (none,0)

theorem tokenize_projection (bytes : List Nat) :
    (tokenizeVisits bytes).1=tokenizeBounded bytes := by
  unfold tokenizeVisits tokenizeBounded
  by_cases h : byteOK bytes=true
  · rw [if_pos h,if_pos h]
    exact scan_projection bytes zeroWord countZero []
  · rw [if_neg h,if_neg h]

theorem tokenize_bound (bytes : List Nat) :
    (tokenizeVisits bytes).2≤1046*bytes.length+8 := by
  unfold tokenizeVisits
  by_cases h : byteOK bytes=true
  · rw [if_pos h]
    exact scan_bound bytes zeroWord countZero [] reset_width count_reset_width
  · rw [if_neg h]
    exact Nat.zero_le _

-- The independent ledgers describe the same bounded tokenization.
-- The prepass visit function is a specification, not a tail-recursive
-- executable cost accumulator. No double-scanning runtime claim.
def resources (bytes : List Nat) : Nat × Nat × Nat :=
  ((tokenizeGates bytes).2,(tokenizeVisits bytes).2,visits bytes byteWord)

theorem agreement (bytes : List Nat) :
    (tokenizeVisits bytes).1=(tokenizeGates bytes).1 :=
  (tokenize_projection bytes).trans (ProctorBinaryScannerGates.tokenize_projection bytes).symm

theorem resource_bounds (bytes : List Nat) :
    (resources bytes).1≤5235*bytes.length ∧
    (resources bytes).2.1≤1046*bytes.length+8 ∧
    (resources bytes).2.2≤20*bytes.length :=
  ⟨tokenize_gate_bound bytes,tokenize_bound bytes,byte_visit_length_bound bytes⟩

end ProctorScannerResourceCompose

#print axioms ProctorScannerResourceCompose.digit_visit_bound
#print axioms ProctorScannerResourceCompose.counter_visit_bound
#print axioms ProctorScannerResourceCompose.core_projection
#print axioms ProctorScannerResourceCompose.core_bound
#print axioms ProctorScannerResourceCompose.scan_projection
#print axioms ProctorScannerResourceCompose.scan_bound
#print axioms ProctorScannerResourceCompose.tokenize_projection
#print axioms ProctorScannerResourceCompose.tokenize_bound
#print axioms ProctorScannerResourceCompose.agreement
#print axioms ProctorScannerResourceCompose.resource_bounds
