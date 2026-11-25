/-! F034 candidate: compose scanner selected resource reservations.
Independent of binary certificate reference candidate.
Padding is a separate coordinate, not allocation or runtime.
The encoder coordinate counts abstract Nat events and append visits.
The meter reserves work on visited digit bytes even if a guard rejects.
Requires strict exact-head replay and executable controls before PR. -/
namespace ProctorScannerPaddingCompose
open ProctorCheckedBinaryScanner (encode encode_sound zeroBits zeroWord checkedDigit)
open ProctorScannerCounters (countZero countLimit nextCount scanCounted)
open ProctorBinaryScannerGates (meterCore digit_width count_width)
open ProctorPaddingVisits (decimalResources decimal_bounds compareResources
  addResources compare_bounds add_bounds)
open ProctorBytePrepass (byteOK tokenizeBounded)
open ProctorDecimalBitWidth (bitsValue)

def digitPadding (v : List Bool) (b : Nat) : Nat :=
  match encode 4 (b-48) with
  | none => 0
  | some d => (decimalResources v d).2

theorem digit_padding_bound (v : List Bool) (b : Nat) (hv : v.length≤512) :
    digitPadding v b≤1031 := by
  unfold digitPadding
  cases e : encode 4 (b-48) with
  | none => exact Nat.zero_le _
  | some d =>
    have hd : d.length≤4 := by
      rw [(encode_sound 4 (b-48) d e).left]
      exact Nat.le_refl _
    exact (decimal_bounds v d 512 hv hd).right

def counterPadding (c : List Bool) : Nat :=
  (compareResources c countLimit).2+(addResources c [true]).2

theorem counter_padding_bound (c : List Bool) (hc : c.length≤8) :
    counterPadding c≤16 := by
  exact Nat.add_le_add (compare_bounds c countLimit 8 hc (by decide)).right
    (add_bounds c [true] 8 hc (by decide)).right

-- Generalize the existing scanner gate bound without changing its meter.
theorem core_budget (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (vg : List Bool → Nat → Nat) (cg : List Bool → Nat) (K : Nat)
    (hr : reset.length≤512) (hz : cz.length≤8)
    (hs : ∀ v b out, step v b=some out → out.length≤512)
    (hn : ∀ c d, next c=some d → d.length≤8)
    (hg : ∀ v c b, v.length≤512 → c.length≤8 → vg v b+cg c≤K)
    (bytes : List Nat) (v c : List Bool) (acc : List Nat)
    (hv : v.length≤512) (hw : c.length≤8) :
    (meterCore reset cz step next vg cg bytes v c acc).2≤K*bytes.length := by
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
        have hcost := hg v c b hv hw
        change (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
          else match next c with
            | none => (none,0)
            | some d => match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next vg cg bs out d acc).2+
          (vg v b+cg c)≤K*bs.length+K
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

def tokenizeExtra (vg : List Bool → Nat → Nat) (cg : List Bool → Nat)
    (bytes : List Nat) : Option (List Nat) × Nat :=
  if byteOK bytes then
    meterCore zeroWord countZero checkedDigit nextCount vg cg bytes zeroWord countZero []
  else (none,0)

theorem extra_projection (vg : List Bool → Nat → Nat) (cg : List Bool → Nat)
    (bytes : List Nat) : (tokenizeExtra vg cg bytes).1=tokenizeBounded bytes := by
  unfold tokenizeExtra tokenizeBounded
  by_cases h : byteOK bytes=true
  · rw [if_pos h,if_pos h]
    exact ProctorBinaryScannerGates.core_projection zeroWord countZero checkedDigit
      nextCount vg cg bytes zeroWord countZero []
  · rw [if_neg h,if_neg h]

private theorem replicate_length (w : Nat) : (List.replicate w false).length=w := by
  induction w with
  | zero => rfl
  | succ w ih =>
    change (List.replicate w false).length+1=w+1
    exact congrArg Nat.succ ih

private theorem reset_width : zeroWord.length≤512 := by
  rw [zeroWord,replicate_length]
  exact Nat.le_refl 512

private theorem count_reset_width : countZero.length≤8 := by
  rw [countZero,replicate_length]
  exact Nat.le_refl 8

theorem extra_bound (vg : List Bool → Nat → Nat) (cg : List Bool → Nat)
    (K : Nat) (hg : ∀ v c b, v.length≤512 → c.length≤8 → vg v b+cg c≤K)
    (bytes : List Nat) : (tokenizeExtra vg cg bytes).2≤K*bytes.length := by
  unfold tokenizeExtra
  by_cases h : byteOK bytes=true
  · rw [if_pos h]
    exact core_budget zeroWord countZero checkedDigit nextCount vg cg K
      reset_width count_reset_width (fun v b out e => digit_width v out b e)
      count_width hg bytes zeroWord countZero [] reset_width count_reset_width
  · rw [if_neg h]
    exact Nat.zero_le _

def tokenizePadding := tokenizeExtra digitPadding counterPadding
def tokenizeEncoder := tokenizeExtra
  (fun _ b => (ProctorEncodeVisits.encodeMeter 4 (b-48)).2) (fun _ => 0)

theorem padding_bound (bytes : List Nat) : (tokenizePadding bytes).2≤1047*bytes.length :=
  extra_bound digitPadding counterPadding 1047
    (fun v c b hv hc => Nat.add_le_add (digit_padding_bound v b hv)
      (counter_padding_bound c hc)) bytes

theorem encoder_bound (bytes : List Nat) : (tokenizeEncoder bytes).2≤21*bytes.length :=
  extra_bound _ _ 21 (fun _ _ b _ _ => ProctorEncodeVisits.four_bound (b-48)) bytes

-- These independent reservations share the same scanner result.
-- Byte prepass visits are a specification, not an executed cost accumulator.
def resources (bytes : List Nat) : Nat × Nat × Nat × Nat × Nat :=
  let r := ProctorScannerResourceCompose.resources bytes
  (r.1,r.2.1,r.2.2,(tokenizePadding bytes).2,(tokenizeEncoder bytes).2)

theorem resource_bounds (bytes : List Nat) :
    (resources bytes).1≤5235*bytes.length ∧
    (resources bytes).2.1≤1046*bytes.length+8 ∧
    (resources bytes).2.2.1≤20*bytes.length ∧
    (resources bytes).2.2.2.1≤1047*bytes.length ∧
    (resources bytes).2.2.2.2≤21*bytes.length := by
  have h := ProctorScannerResourceCompose.resource_bounds bytes
  exact ⟨h.left,h.right.left,h.right.right,padding_bound bytes,encoder_bound bytes⟩

end ProctorScannerPaddingCompose

#print axioms ProctorScannerPaddingCompose.digit_padding_bound
#print axioms ProctorScannerPaddingCompose.counter_padding_bound
#print axioms ProctorScannerPaddingCompose.core_budget
#print axioms ProctorScannerPaddingCompose.extra_projection
#print axioms ProctorScannerPaddingCompose.extra_bound
#print axioms ProctorScannerPaddingCompose.padding_bound
#print axioms ProctorScannerPaddingCompose.encoder_bound
#print axioms ProctorScannerPaddingCompose.resource_bounds
