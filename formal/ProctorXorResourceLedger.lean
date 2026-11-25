/-! F034 candidate: compose selected XOR terminal binary resources.
Separate gate and lookup reservations, not an exact short-circuit trace.
Guarded block reservation avoids enumerating oversized supports.
No encoder, padding, allocation or whole-machine cost claim. -/
namespace ProctorXorResourceLedger
open ProctorHallDeficiency
open ProctorCapacityReplay (RefRow test every someCheck)
open ProctorXorReplay (Block patterns patternParity sumRhs)
open ProctorBinaryXor (refsCheck patternBinary blockBinary toggleMeter combineBinary sumBinary xorBinary eqBudget toggle_bound)
open ProctorBinaryReferences (refMeter ref_visits ref_gates containsMeter contains_bound literalBudget)
open ProctorBinaryLookup (checkedLookup)
open ProctorBinaryInputBinding (weight)

abbrev Meter := Bool × Nat × Nat

def both (a b : Meter) : Meter :=
  (a.1 && b.1,a.2.1+b.2.1,a.2.2+b.2.2)
def either (a b : Meter) : Meter :=
  (a.1 || b.1,a.2.1+b.2.1,a.2.2+b.2.2)

def allMeter {α : Type} (p : α → Meter) : List α → Meter
  | [] => (true,0,0)
  | a::as => both (p a) (allMeter p as)
def anyMeter {α : Type} (p : α → Meter) : List α → Meter
  | [] => (false,0,0)
  | a::as => either (p a) (anyMeter p as)

theorem all_value {α : Type} (p : α → Meter) (q : α → Bool)
    (xs : List α) (h : ∀ a, (p a).1=q a) :
    (allMeter p xs).1=every q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change ((p a).1 && (allMeter p as).1)=(q a && every q as)
    rw [h a,ih]

theorem any_value {α : Type} (p : α → Meter) (q : α → Bool)
    (xs : List α) (h : ∀ a, (p a).1=q a) :
    (anyMeter p xs).1=someCheck q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change ((p a).1 || (anyMeter p as).1)=(q a || someCheck q as)
    rw [h a,ih]

def reserve {α : Type} (q : α → Nat) : List α → Nat
  | [] => 0
  | a::as => q a+reserve q as

theorem all_bounds {α : Type} (p : α → Meter) (v g : α → Nat)
    (xs : List α) (hv : ∀ a, (p a).2.1≤v a) (hg : ∀ a, (p a).2.2≤g a) :
    (allMeter p xs).2.1≤reserve v xs ∧ (allMeter p xs).2.2≤reserve g xs := by
  induction xs with
  | nil => exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩
  | cons a as ih =>
    exact ⟨Nat.add_le_add (hv a) ih.left,Nat.add_le_add (hg a) ih.right⟩

theorem any_bounds {α : Type} (p : α → Meter) (v g : α → Nat)
    (xs : List α) (hv : ∀ a, (p a).2.1≤v a) (hg : ∀ a, (p a).2.2≤g a) :
    (anyMeter p xs).2.1≤reserve v xs ∧ (anyMeter p xs).2.2≤reserve g xs := by
  induction xs with
  | nil => exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩
  | cons a as ih =>
    exact ⟨Nat.add_le_add (hv a) ih.left,Nat.add_le_add (hg a) ih.right⟩

def refGateBudget (w : Nat) (f : Formula) (r : RefRow) : Nat :=
  literalBudget w*(match (checkedLookup w f r.index).1 with
    | none => 0
    | some c => c.length)

def refsMeter (w : Nat) (f : Formula) (rs : List RefRow) : Meter :=
  allMeter (refMeter w f) rs

theorem refs_value (w : Nat) (f : Formula) (rs : List RefRow) :
    (refsMeter w f rs).1=refsCheck w f rs :=
  all_value _ _ rs (fun _ => rfl)

theorem refs_bounds (w : Nat) (f : Formula) (rs : List RefRow) :
    (refsMeter w f rs).2.1≤reserve (fun _ => (w+1)*f.length) rs ∧
    (refsMeter w f rs).2.2≤reserve (refGateBudget w f) rs :=
  all_bounds _ _ _ rs (ref_visits w f) (ref_gates w f)

def membershipMeter (w : Nat) (ls : Clause) (l : Literal) : Meter :=
  let m := containsMeter w l ls
  (m.1,0,m.2)

def rowMemberMeter (w : Nat) (ls row : Clause) : Meter :=
  allMeter (membershipMeter w ls) row

def rowMemberBudget (w : Nat) (ls row : Clause) : Nat :=
  reserve (fun _ => literalBudget w*ls.length) row

theorem row_member_value (w : Nat) (ls row : Clause) :
    (rowMemberMeter w ls row).1=every (fun l => (containsMeter w l ls).1) row :=
  all_value _ _ row (fun _ => rfl)

theorem reserve_zero {α : Type} (xs : List α) :
    reserve (fun _ : α => 0) xs=0 := by
  induction xs with
  | nil => rfl
  | cons a as ih => change 0+reserve (fun _ : α => 0) as=0; rw [ih]

theorem row_member_bounds (w : Nat) (ls row : Clause) :
    (rowMemberMeter w ls row).2.1≤0 ∧
    (rowMemberMeter w ls row).2.2≤rowMemberBudget w ls row := by
  have h := all_bounds (membershipMeter w ls) (fun _ => 0)
    (fun _ => literalBudget w*ls.length) row
    (fun _ => Nat.le_refl 0) (fun l => contains_bound w l ls)
  rw [reserve_zero] at h
  exact h

def patternMeter (w : Nat) (b : Block) (ls : Clause) : Meter :=
  if patternParity ls=b.rhs then (true,0,0)
  else anyMeter (fun r => rowMemberMeter w ls r.row) b.refs

def patternBudget (w : Nat) (b : Block) (ls : Clause) : Nat :=
  reserve (fun r : RefRow => rowMemberBudget w ls r.row) b.refs

theorem pattern_value (w : Nat) (b : Block) (ls : Clause) :
    (patternMeter w b ls).1=patternBinary w b ls := by
  unfold patternMeter patternBinary
  by_cases h : patternParity ls=b.rhs
  · rw [if_pos h,if_pos h]
  · rw [if_neg h,if_neg h]
    exact any_value _ _ b.refs (fun r => row_member_value w ls r.row)

theorem pattern_bounds (w : Nat) (b : Block) (ls : Clause) :
    (patternMeter w b ls).2.1≤0 ∧ (patternMeter w b ls).2.2≤patternBudget w b ls := by
  unfold patternMeter
  by_cases h : patternParity ls=b.rhs
  · rw [if_pos h]
    exact ⟨Nat.le_refl 0,Nat.zero_le _⟩
  · rw [if_neg h]
    have hm := any_bounds (fun r : RefRow => rowMemberMeter w ls r.row)
      (fun _ => 0) (fun r => rowMemberBudget w ls r.row) b.refs
      (fun r => (row_member_bounds w ls r.row).left)
      (fun r => (row_member_bounds w ls r.row).right)
    rw [reserve_zero] at hm
    exact hm

def patternsMeter : List Nat → (Clause → Meter) → Meter
  | [],p => p []
  | v::vs,p => both (patternsMeter vs (fun ls => p ((v,false)::ls)))
      (patternsMeter vs (fun ls => p ((v,true)::ls)))

def patternsBudget : List Nat → (Clause → Nat) → Nat
  | [],q => q []
  | v::vs,q => patternsBudget vs (fun ls => q ((v,false)::ls))+
      patternsBudget vs (fun ls => q ((v,true)::ls))

theorem patterns_value (vs : List Nat) (p : Clause → Meter) (q : Clause → Bool)
    (h : ∀ ls, (p ls).1=q ls) :
    (patternsMeter vs p).1=patterns vs q := by
  induction vs generalizing p q with
  | nil => exact h []
  | cons v vs ih =>
    change (((patternsMeter vs (fun ls => p ((v,false)::ls))).1) &&
      ((patternsMeter vs (fun ls => p ((v,true)::ls))).1))=
      (patterns vs (fun ls => q ((v,false)::ls)) &&
        patterns vs (fun ls => q ((v,true)::ls)))
    rw [ih _ _ (fun ls => h ((v,false)::ls)),ih _ _ (fun ls => h ((v,true)::ls))]

theorem patterns_bounds (vs : List Nat) (p : Clause → Meter) (q : Clause → Nat)
    (hv : ∀ ls, (p ls).2.1≤0) (hg : ∀ ls, (p ls).2.2≤q ls) :
    (patternsMeter vs p).2.1≤0 ∧ (patternsMeter vs p).2.2≤patternsBudget vs q := by
  induction vs generalizing p q with
  | nil => exact ⟨hv [],hg []⟩
  | cons v vs ih =>
    have a := ih (fun ls => p ((v,false)::ls)) (fun ls => q ((v,false)::ls))
      (fun ls => hv _) (fun ls => hg _)
    have b := ih (fun ls => p ((v,true)::ls)) (fun ls => q ((v,true)::ls))
      (fun ls => hv _) (fun ls => hg _)
    exact ⟨Nat.add_le_add a.left b.left,Nat.add_le_add a.right b.right⟩

def blockMeter (w : Nat) (f : Formula) (b : Block) : Meter :=
  if b.support.length≤5 then both (refsMeter w f b.refs)
    (patternsMeter b.support (patternMeter w b))
  else (false,0,0)

def blockVisitBudget (w : Nat) (f : Formula) (b : Block) : Nat :=
  if b.support.length≤5 then reserve (fun _ => (w+1)*f.length) b.refs else 0
def blockGateBudget (w : Nat) (f : Formula) (b : Block) : Nat :=
  if b.support.length≤5 then reserve (refGateBudget w f) b.refs+
    patternsBudget b.support (patternBudget w b) else 0

theorem block_value (w : Nat) (f : Formula) (b : Block) :
    (blockMeter w f b).1=blockBinary w f b := by
  unfold blockMeter blockBinary test
  by_cases h : b.support.length≤5
  · rw [if_pos h,if_pos h]
    change ((refsMeter w f b.refs).1 && (patternsMeter b.support (patternMeter w b)).1)=_
    rw [refs_value,patterns_value _ _ _ (pattern_value w b)] <;> rfl
  · rw [if_neg h,if_neg h] <;> rfl

theorem block_bounds (w : Nat) (f : Formula) (b : Block) :
    (blockMeter w f b).2.1≤blockVisitBudget w f b ∧
    (blockMeter w f b).2.2≤blockGateBudget w f b := by
  unfold blockMeter blockVisitBudget blockGateBudget
  by_cases h : b.support.length≤5
  · rw [if_pos h,if_pos h,if_pos h]
    have r := refs_bounds w f b.refs
    have p := patterns_bounds b.support (patternMeter w b) (patternBudget w b)
      (fun ls => (pattern_bounds w b ls).left) (fun ls => (pattern_bounds w b ls).right)
    exact ⟨Nat.add_le_add r.left p.left,Nat.add_le_add r.right p.right⟩
  · rw [if_neg h,if_neg h,if_neg h]
    exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩

-- Track the exact binary support output, including out-of-width inputs.
def combineMeter (w : Nat) : List Nat → List Nat → List Nat × Nat
  | [],ys => (ys,0)
  | v::vs,ys =>
    let r := combineMeter w vs ys
    let t := toggleMeter w v r.1
    (t.1,r.2+t.2)

def combineBudget (w : Nat) : List Nat → List Nat → Nat
  | [],_ => 0
  | _::vs,ys => combineBudget w vs ys+eqBudget w*(combineBinary w vs ys).length

theorem combine_value (w : Nat) (a b : List Nat) :
    (combineMeter w a b).1=combineBinary w a b := by
  induction a with
  | nil => rfl
  | cons v vs ih =>
    change (toggleMeter w v (combineMeter w vs b).1).1=_
    rw [ih] <;> rfl

theorem combine_bound (w : Nat) (a b : List Nat) :
    (combineMeter w a b).2≤combineBudget w a b := by
  induction a with
  | nil => exact Nat.le_refl 0
  | cons v vs ih =>
    change (combineMeter w vs b).2+(toggleMeter w v (combineMeter w vs b).1).2≤
      combineBudget w vs b+eqBudget w*(combineBinary w vs b).length
    rw [combine_value]
    exact Nat.add_le_add ih (toggle_bound w v (combineBinary w vs b))

def sumMeter (w : Nat) : List Block → List Nat × Nat
  | [] => ([],0)
  | b::bs =>
    let r := sumMeter w bs
    let t := combineMeter w b.support r.1
    (t.1,r.2+t.2)

def sumBudget (w : Nat) : List Block → Nat
  | [] => 0
  | b::bs => sumBudget w bs+combineBudget w b.support (sumBinary w bs)

theorem sum_value (w : Nat) (bs : List Block) :
    (sumMeter w bs).1=sumBinary w bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    change (combineMeter w b.support (sumMeter w bs).1).1=_
    rw [combine_value,ih] <;> rfl

theorem sum_bound (w : Nat) (bs : List Block) :
    (sumMeter w bs).2≤sumBudget w bs := by
  induction bs with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    change (sumMeter w bs).2+(combineMeter w b.support (sumMeter w bs).1).2≤
      sumBudget w bs+combineBudget w b.support (sumBinary w bs)
    rw [sum_value]
    exact Nat.add_le_add ih (combine_bound w b.support (sumBinary w bs))

def xorMeter (w : Nat) (f : Formula) (bs : List Block) : Meter :=
  let r := allMeter (blockMeter w f) bs
  let s := sumMeter w bs
  (r.1 && (test (s.1=[]) && sumRhs bs),r.2.1,r.2.2+s.2)

def visitBudget (w : Nat) (f : Formula) (bs : List Block) : Nat :=
  reserve (blockVisitBudget w f) bs
def gateBudget (w : Nat) (f : Formula) (bs : List Block) : Nat :=
  reserve (blockGateBudget w f) bs+sumBudget w bs

theorem xor_value (w : Nat) (f : Formula) (bs : List Block) :
    (xorMeter w f bs).1=xorBinary w f bs := by
  unfold xorMeter xorBinary
  dsimp only
  rw [all_value _ _ _ (block_value w f),sum_value]

theorem xor_bounds (w : Nat) (f : Formula) (bs : List Block) :
    (xorMeter w f bs).2.1≤visitBudget w f bs ∧
    (xorMeter w f bs).2.2≤gateBudget w f bs := by
  have h := all_bounds (blockMeter w f) (blockVisitBudget w f)
    (blockGateBudget w f) bs (fun b => (block_bounds w f b).left)
    (fun b => (block_bounds w f b).right)
  exact ⟨h.left,Nat.add_le_add h.right (sum_bound w bs)⟩

end ProctorXorResourceLedger

#print axioms ProctorXorResourceLedger.all_value
#print axioms ProctorXorResourceLedger.any_value
#print axioms ProctorXorResourceLedger.all_bounds
#print axioms ProctorXorResourceLedger.any_bounds
#print axioms ProctorXorResourceLedger.refs_value
#print axioms ProctorXorResourceLedger.refs_bounds
#print axioms ProctorXorResourceLedger.row_member_value
#print axioms ProctorXorResourceLedger.reserve_zero
#print axioms ProctorXorResourceLedger.row_member_bounds
#print axioms ProctorXorResourceLedger.pattern_value
#print axioms ProctorXorResourceLedger.pattern_bounds
#print axioms ProctorXorResourceLedger.patterns_value
#print axioms ProctorXorResourceLedger.patterns_bounds
#print axioms ProctorXorResourceLedger.block_value
#print axioms ProctorXorResourceLedger.block_bounds
#print axioms ProctorXorResourceLedger.combine_value
#print axioms ProctorXorResourceLedger.combine_bound
#print axioms ProctorXorResourceLedger.sum_value
#print axioms ProctorXorResourceLedger.sum_bound
#print axioms ProctorXorResourceLedger.xor_value
#print axioms ProctorXorResourceLedger.xor_bounds
