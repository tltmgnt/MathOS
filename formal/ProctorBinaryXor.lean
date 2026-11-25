/-! F034 candidate: binary identifier equality, reference lookup,
and literal membership in XOR terminal checking. Structural length
guard, Boolean parity and emptiness checks remain unchanged.
Selected toggle comparison gates are separately bounded. -/
namespace ProctorBinaryXor
open ProctorHallDeficiency
open ProctorCapacityReplay (RefRow every someCheck refCheck test)
open ProctorExecutableReplay (contains)
open ProctorXorReplay (Block patterns patternParity patternCheck blockCheck toggle combine sumSupport sumRhs xorCheck)
open ProctorBinaryReferences (Fits refMeter ref_value containsMeter contains_value)
open ProctorCheckedBinaryScanner (cap)
open ProctorCheckerBinaryTests (checkedEq checked_eq_value checked_eq_bound)
open ProctorBinaryInputBinding (optFalse)
open ProctorIntermediateWidth (SupportFit combine_fit sum_support_fit target_fit)

def FormulaFit (w : Nat) (f : Formula) : Prop := ∀ c ∈ f, Fits w c
def RefsFit (w : Nat) (rs : List RefRow) : Prop :=
  ∀ r ∈ rs, r.index<cap w ∧ Fits w r.row
def BlockFit (w : Nat) (b : Block) : Prop :=
  SupportFit (cap w) b.support ∧ RefsFit w b.refs

theorem every_congr {α : Type} (p q : α → Bool) (xs : List α)
    (h : ∀ a ∈ xs, p a=q a) : every p xs=every q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a && every p as)=(q a && every q as)
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))]

theorem some_congr {α : Type} (p q : α → Bool) (xs : List α)
    (h : ∀ a ∈ xs, p a=q a) : someCheck p xs=someCheck q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a || someCheck p as)=(q a || someCheck q as)
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))]

def refsCheck (w : Nat) (f : Formula) (rs : List RefRow) : Bool :=
  every (fun r => (refMeter w f r).1) rs

theorem refs_value (w : Nat) (f : Formula) (rs : List RefRow)
    (hf : FormulaFit w f) (hr : RefsFit w rs) :
    refsCheck w f rs=every (refCheck f) rs :=
  every_congr _ _ rs (fun r hm => ref_value w f r (hr r hm).left hf (hr r hm).right)

def patternBinary (w : Nat) (b : Block) (ls : Clause) : Bool :=
  if patternParity ls=b.rhs then true
  else someCheck (fun r => every (fun l => (containsMeter w l ls).1) r.row) b.refs

theorem pattern_value (w : Nat) (b : Block) (ls : Clause)
    (hr : RefsFit w b.refs) (hl : Fits w ls) :
    patternBinary w b ls=patternCheck b ls := by
  unfold patternBinary patternCheck
  by_cases h : patternParity ls=b.rhs
  · rw [if_pos h,if_pos h]
  · rw [if_neg h,if_neg h]
    exact some_congr _ _ b.refs (fun r hm =>
      every_congr _ _ r.row (fun l hmem => contains_value w l ls ((hr r hm).right l hmem) hl))

-- Enumerated signed patterns inherit width from their support.
theorem patterns_value (w : Nat) (vs : List Nat) (p q : Clause → Bool)
    (hv : SupportFit (cap w) vs) (h : ∀ ls, Fits w ls → p ls=q ls) :
    patterns vs p=patterns vs q := by
  induction vs generalizing p q with
  | nil =>
    exact h [] (fun l hl => by cases hl)
  | cons v vs ih =>
    have ht : SupportFit (cap w) vs := fun n hn => hv n (List.Mem.tail _ hn)
    have hc : ∀ sign ls, Fits w ls → Fits w ((v,sign)::ls) := by
      intro sign ls hl l hm
      cases hm with
      | head => exact hv v (List.Mem.head _)
      | tail _ hm => exact hl l hm
    change (patterns vs (fun ls => p ((v,false)::ls)) &&
      patterns vs (fun ls => p ((v,true)::ls)))=
      (patterns vs (fun ls => q ((v,false)::ls)) &&
      patterns vs (fun ls => q ((v,true)::ls)))
    rw [ih _ _ ht (fun ls hl => h _ (hc false ls hl)),
      ih _ _ ht (fun ls hl => h _ (hc true ls hl))]

def blockBinary (w : Nat) (f : Formula) (b : Block) : Bool :=
  test (b.support.length≤5) &&
    (refsCheck w f b.refs && patterns b.support (patternBinary w b))

theorem block_value (w : Nat) (f : Formula) (b : Block)
    (hf : FormulaFit w f) (hb : BlockFit w b) :
    blockBinary w f b=blockCheck f b := by
  unfold blockBinary blockCheck
  rw [refs_value w f b.refs hf hb.right,
    patterns_value w b.support _ _ hb.left (fun ls hl => pattern_value w b ls hb.right hl)]

-- Meter only the selected unsigned identifier comparisons in toggle.
def toggleMeter (w v : Nat) : List Nat → List Nat × Nat
  | [] => ([v],0)
  | a::as =>
    let e := checkedEq w v a
    if optFalse e.1 then (as,e.2)
    else let r := toggleMeter w v as; (a::r.1,r.2+e.2)

theorem toggle_value (w v : Nat) (vs : List Nat)
    (hv : v<cap w) (hs : SupportFit (cap w) vs) :
    (toggleMeter w v vs).1=toggle v vs := by
  induction vs with
  | nil => rfl
  | cons a as ih =>
    unfold toggleMeter toggle
    dsimp only
    rw [checked_eq_value w v a hv (hs a (List.Mem.head _))]
    unfold optFalse test
    by_cases e : v=a
    · rw [if_pos e,if_pos e]
      rfl
    · rw [if_neg e,if_neg e]
      change a::(toggleMeter w v as).1=a::toggle v as
      rw [ih (fun n hn => hs n (List.Mem.tail _ hn))]

def eqBudget (w : Nat) : Nat := (5*w+5*w)+3

theorem toggle_bound (w v : Nat) (vs : List Nat) :
    (toggleMeter w v vs).2≤eqBudget w*vs.length := by
  induction vs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change (if optFalse (checkedEq w v a).1 then (as,(checkedEq w v a).2)
      else (a::(toggleMeter w v as).1,(toggleMeter w v as).2+(checkedEq w v a).2)).2≤
      eqBudget w*as.length+eqBudget w
    cases e : optFalse (checkedEq w v a).1 with
    | true => exact Nat.le_trans (checked_eq_bound w v a) (Nat.le_add_left _ _)
    | false => exact Nat.add_le_add ih (checked_eq_bound w v a)

def combineBinary (w : Nat) : List Nat → List Nat → List Nat
  | [],ys => ys
  | v::vs,ys => (toggleMeter w v (combineBinary w vs ys)).1

theorem combine_value (w : Nat) (a b : List Nat)
    (ha : SupportFit (cap w) a) (hb : SupportFit (cap w) b) :
    combineBinary w a b=combine a b := by
  induction a with
  | nil => rfl
  | cons v vs ih =>
    have ht : SupportFit (cap w) vs := fun n hn => ha n (List.Mem.tail _ hn)
    change (toggleMeter w v (combineBinary w vs b)).1=toggle v (combine vs b)
    rw [ih ht]
    exact toggle_value w v (combine vs b) (ha v (List.Mem.head _))
      (combine_fit (cap w) vs b ht hb)

def sumBinary (w : Nat) : List Block → List Nat
  | [] => []
  | b::bs => combineBinary w b.support (sumBinary w bs)

theorem sum_value (w : Nat) (bs : List Block)
    (h : ∀ b ∈ bs, SupportFit (cap w) b.support) :
    sumBinary w bs=sumSupport bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    have ht : ∀ q ∈ bs, SupportFit (cap w) q.support :=
      fun q hq => h q (List.Mem.tail _ hq)
    change combineBinary w b.support (sumBinary w bs)=combine b.support (sumSupport bs)
    rw [ih ht]
    exact combine_value w b.support (sumSupport bs) (h b (List.Mem.head _))
      (sum_support_fit (cap w) bs ht)

def xorBinary (w : Nat) (f : Formula) (bs : List Block) : Bool :=
  every (blockBinary w f) bs && (test (sumBinary w bs=[]) && sumRhs bs)

theorem xor_value (w : Nat) (f : Formula) (bs : List Block)
    (hf : FormulaFit w f) (hb : ∀ b ∈ bs, BlockFit w b) :
    xorBinary w f bs=xorCheck f bs := by
  unfold xorBinary xorCheck
  rw [every_congr _ _ bs (fun b hm => block_value w f b hf (hb b hm)),
    sum_value w bs (fun b hm => (hb b hm).left)]

theorem xor_sound (w : Nat) (f : Formula) (bs : List Block)
    (hf : FormulaFit w f) (hb : ∀ b ∈ bs, BlockFit w b)
    (h : xorBinary w f bs=true) : ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [xor_value w f bs hf hb] at h
  exact ProctorXorReplay.xor_check_sound f bs h

theorem decoded_xor_value (a b : List Nat) (n : Nat) (f : Formula)
    (e : ProctorUnifiedReplay.Envelope) (bs : List Block)
    (ha : ProctorDataParser.decodeExpected a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e)
    (ht : e.proof.terminal=ProctorUnifiedReplay.Terminal.xor bs) :
    xorBinary 512 (ProctorUnifiedReplay.target f e.proof) bs=
      xorCheck (ProctorUnifiedReplay.target f e.proof) bs := by
  have h1 := ProctorDecodedWidth.decoded_expected a n f ha
  have h2 := ProctorDecodedWidth.decoded_envelope b e hb
  have htarget := target_fit (cap 512) f e.proof h1.right
    (fun batch hm s hs => (h2.right.right.left batch hm s hs).right.right.right)
  have hterminal := h2.right.right.right
  rw [ht] at hterminal
  exact xor_value 512 _ bs htarget hterminal

end ProctorBinaryXor

#print axioms ProctorBinaryXor.every_congr
#print axioms ProctorBinaryXor.some_congr
#print axioms ProctorBinaryXor.refs_value
#print axioms ProctorBinaryXor.pattern_value
#print axioms ProctorBinaryXor.patterns_value
#print axioms ProctorBinaryXor.block_value
#print axioms ProctorBinaryXor.toggle_value
#print axioms ProctorBinaryXor.toggle_bound
#print axioms ProctorBinaryXor.combine_value
#print axioms ProctorBinaryXor.sum_value
#print axioms ProctorBinaryXor.xor_value
#print axioms ProctorBinaryXor.xor_sound
#print axioms ProctorBinaryXor.decoded_xor_value
