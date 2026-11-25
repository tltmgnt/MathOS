/-! F034 candidate: account for binary accumulator conversion to Nat
at token emission. One bit visit, one abstract multiplication by two,
one abstract addition per nonempty bitsValue recursion. No claim that
Nat arithmetic, storage or result allocation has constant bit cost. -/
namespace ProctorValueProjection
open ProctorDecimalBitWidth (bitsValue bitVal)
open ProctorCheckedBinaryScanner (cap value_bound zeroBits zeroWord checkedDigit)
open ProctorScannerCounters (scanCore scanCounted countZero nextCount)
open ProctorBinaryScannerGates (charge digit_width)
open ProctorBytePrepass (byteOK tokenizeBounded)
open ProctorTerminalPolynomial (mul_mono)

def valueMeter : List Bool → Nat × Nat
  | [] => (0,0)
  | a::as =>
    let r := valueMeter as
    (bitVal a+2*r.1,r.2+3)

theorem value_projection (xs : List Bool) : (valueMeter xs).1=bitsValue xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change bitVal a+2*(valueMeter as).1=bitVal a+2*bitsValue as
    rw [ih]

theorem value_exact (xs : List Bool) : (valueMeter xs).2=3*xs.length := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (valueMeter as).2+3=3*as.length+3
    rw [ih]

theorem value_width (xs : List Bool) : (valueMeter xs).1<cap xs.length := by
  rw [value_projection]
  exact value_bound xs

theorem value_bound_512 (xs : List Bool) (h : xs.length≤512) :
    (valueMeter xs).2≤1536 := by
  rw [value_exact]
  exact mul_mono (Nat.le_refl 3) h

-- Use the metered value in the emitted token itself. Charge only
-- at successful LF emission, including emissions before later rejection.
def emitCore (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool)) :
    List Nat → List Bool → List Bool → List Nat → Option (List Nat) × Nat
  | [],_,c,acc => (if zeroBits c=true then some acc.reverse else none,0)
  | b::bs,v,c,acc =>
    if b=10 then
      if zeroBits c=true then (none,0)
      else
        let q := valueMeter v
        charge q.2 (emitCore reset cz step next bs reset cz (q.1::acc))
    else if 48≤b ∧ b≤57 then
      if zeroBits c≠true ∧ zeroBits v=true then (none,0)
      else match next c with
        | none => (none,0)
        | some d => match step v b with
          | none => (none,0)
          | some out => emitCore reset cz step next bs out d acc
    else (none,0)

theorem core_projection (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (emitCore reset cz step next bytes v c acc).1=
      scanCore reset cz step next bytes v c acc := by
  induction bytes generalizing v c acc with
  | nil => rfl
  | cons b bs ih =>
    rw [emitCore,scanCore]
    by_cases lf : b=10
    · rw [if_pos lf,if_pos lf]
      by_cases z : zeroBits c=true
      · rw [if_pos z,if_pos z]
      · rw [if_neg z,if_neg z]
        change (emitCore reset cz step next bs reset cz ((valueMeter v).1::acc)).1=_
        rw [value_projection]
        exact ih reset cz (bitsValue v::acc)
    · rw [if_neg lf,if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit,if_pos digit]
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead,if_pos lead]
        · rw [if_neg lead,if_neg lead]
          cases en : next c with
          | none => rfl
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => emitCore reset cz step next bs out d acc).1=
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
    (hr : reset.length≤512)
    (hs : ∀ v b out, step v b=some out → out.length≤512)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) :
    (emitCore reset cz step next bytes v c acc).2≤1536*bytes.length := by
  induction bytes generalizing v c acc with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    rw [emitCore]
    by_cases lf : b=10
    · rw [if_pos lf]
      by_cases z : zeroBits c=true
      · rw [if_pos z]
        exact Nat.zero_le _
      · rw [if_neg z]
        change (emitCore reset cz step next bs reset cz ((valueMeter v).1::acc)).2+
          (valueMeter v).2≤1536*bs.length+1536
        exact Nat.add_le_add (ih reset cz ((valueMeter v).1::acc) hr)
          (value_bound_512 v hv)
    · rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit]
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead]
          exact Nat.zero_le _
        · rw [if_neg lead]
          cases en : next c with
          | none => exact Nat.zero_le _
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => emitCore reset cz step next bs out d acc).2≤_
            cases es : step v b with
            | none => exact Nat.zero_le _
            | some out =>
              exact Nat.le_trans (ih out d acc (hs v b out es)) (Nat.le_add_right _ _)
      · rw [if_neg digit]
        exact Nat.zero_le _

def scanEmit := emitCore zeroWord countZero checkedDigit nextCount

private theorem reset_length (w : Nat) : (List.replicate w false).length=w := by
  induction w with
  | zero => rfl
  | succ w ih =>
    change (List.replicate w false).length+1=w+1
    exact congrArg Nat.succ ih

private theorem reset_width : zeroWord.length≤512 := by
  rw [zeroWord,reset_length]
  exact Nat.le_refl 512

theorem scan_projection (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (scanEmit bytes v c acc).1=scanCounted bytes v c acc :=
  core_projection zeroWord countZero checkedDigit nextCount bytes v c acc

def tokenizeEmit (bytes : List Nat) : Option (List Nat) × Nat :=
  if byteOK bytes then scanEmit bytes zeroWord countZero [] else (none,0)

theorem tokenize_projection (bytes : List Nat) :
    (tokenizeEmit bytes).1=tokenizeBounded bytes := by
  unfold tokenizeEmit tokenizeBounded
  by_cases h : byteOK bytes=true
  · rw [if_pos h,if_pos h]
    exact scan_projection bytes zeroWord countZero []
  · rw [if_neg h,if_neg h]

theorem tokenize_refines (bytes : List Nat) :
    (tokenizeEmit bytes).1=ProctorDataParser.tokenize bytes :=
  (tokenize_projection bytes).trans (ProctorBytePrepass.tokenize_refines bytes)

theorem tokenize_bound (bytes : List Nat) :
    (tokenizeEmit bytes).2≤1536*bytes.length := by
  unfold tokenizeEmit
  by_cases h : byteOK bytes=true
  · rw [if_pos h]
    exact core_bound zeroWord countZero checkedDigit nextCount reset_width
      (fun v b out e => digit_width v out b e) bytes zeroWord countZero [] reset_width
  · rw [if_neg h]
    exact Nat.zero_le _

end ProctorValueProjection

#print axioms ProctorValueProjection.value_projection
#print axioms ProctorValueProjection.value_exact
#print axioms ProctorValueProjection.value_width
#print axioms ProctorValueProjection.value_bound_512
#print axioms ProctorValueProjection.core_projection
#print axioms ProctorValueProjection.core_bound
#print axioms ProctorValueProjection.scan_projection
#print axioms ProctorValueProjection.tokenize_projection
#print axioms ProctorValueProjection.tokenize_refines
#print axioms ProctorValueProjection.tokenize_bound
