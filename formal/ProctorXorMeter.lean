/-! F034: selected structural charges for sparse parity terminals.
Independent of the pending capacity meter. Eager folds, not runtime traces. -/
namespace ProctorXorMeter
open ProctorHallDeficiency
open ProctorCapacityReplay (every someCheck test)
open ProctorExecutableReplay (contains)
open ProctorCheckerCost (containsMeter contains_value contains_bound)
open ProctorChainMeter (refsMeter refsBudget refs_value refs_bound)
open ProctorXorReplay (Block bx patternParity patternCheck patterns blockCheck toggle combine sumSupport sumRhs xorCheck)

abbrev Meter := Bool × Nat

def allMeter {α : Type} (p : α → Meter) : List α → Meter
  | [] => (true,0)
  | a::as =>
    let u := p a
    let v := allMeter p as
    (u.1 && v.1,u.2+v.2+1)

def anyMeter {α : Type} (p : α → Meter) : List α → Meter
  | [] => (false,0)
  | a::as =>
    let u := p a
    let v := anyMeter p as
    (u.1 || v.1,u.2+v.2+1)

def visitsBudget {α : Type} (q : α → Nat) : List α → Nat
  | [] => 0
  | a::as => q a + visitsBudget q as + 1

theorem all_value {α : Type} (p : α → Meter) (q : α → Bool)
    (xs : List α) (h : ∀ a, (p a).1 = q a) :
    (allMeter p xs).1 = every q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change ((p a).1 && (allMeter p as).1) = (q a && every q as)
    rw [h a,ih]

theorem all_bound {α : Type} (p : α → Meter) (q : α → Nat)
    (xs : List α) (h : ∀ a, (p a).2 ≤ q a) :
    (allMeter p xs).2 ≤ visitsBudget q xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    exact Nat.add_le_add (Nat.add_le_add (h a) ih) (Nat.le_refl 1)

theorem any_value {α : Type} (p : α → Meter) (q : α → Bool)
    (xs : List α) (h : ∀ a, (p a).1 = q a) :
    (anyMeter p xs).1 = someCheck q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change ((p a).1 || (anyMeter p as).1) = (q a || someCheck q as)
    rw [h a,ih]

theorem any_bound {α : Type} (p : α → Meter) (q : α → Nat)
    (xs : List α) (h : ∀ a, (p a).2 ≤ q a) :
    (anyMeter p xs).2 ≤ visitsBudget q xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    exact Nat.add_le_add (Nat.add_le_add (h a) ih) (Nat.le_refl 1)

-- Charge one parity term per pattern literal and one RHS comparison.
-- A wrong parity pattern also scans references and membership.
def patternMeter (b : Block) (ls : Clause) : Meter :=
  if patternParity ls = b.rhs then (true,ls.length+1)
  else
    let m := anyMeter (fun r => allMeter (fun l => containsMeter l ls) r.row) b.refs
    (m.1,(ls.length+1)+m.2)

def patternBudget (b : Block) (ls : Clause) : Nat :=
  (ls.length+1) + visitsBudget (fun r =>
    visitsBudget (fun _ => ls.length) r.row) b.refs

theorem pattern_value (b : Block) (ls : Clause) :
    (patternMeter b ls).1 = patternCheck b ls := by
  unfold patternMeter patternCheck
  by_cases e : patternParity ls = b.rhs
  · rw [if_pos e,if_pos e]
  · rw [if_neg e,if_neg e]
    apply any_value
    intro r
    apply all_value
    intro l
    exact contains_value l ls

theorem pattern_bound (b : Block) (ls : Clause) :
    (patternMeter b ls).2 ≤ patternBudget b ls := by
  unfold patternMeter patternBudget
  by_cases e : patternParity ls = b.rhs
  · rw [if_pos e]
    exact Nat.le_add_right _ _
  · rw [if_neg e]
    apply Nat.add_le_add (Nat.le_refl _)
    apply any_bound
    intro r
    apply all_bound
    intro l
    exact contains_bound l ls

-- One charge per internal binary pattern-tree node.
def patternsMeter : List Nat → (Clause → Meter) → Meter
  | [],p => p []
  | v::vs,p =>
    let a := patternsMeter vs (fun ls => p ((v,false)::ls))
    let b := patternsMeter vs (fun ls => p ((v,true)::ls))
    (a.1 && b.1,a.2+b.2+1)

def patternsBudget : List Nat → (Clause → Nat) → Nat
  | [],q => q []
  | v::vs,q =>
    patternsBudget vs (fun ls => q ((v,false)::ls)) +
    patternsBudget vs (fun ls => q ((v,true)::ls)) + 1

theorem patterns_value (vs : List Nat) (p : Clause → Meter)
    (q : Clause → Bool) (h : ∀ ls, (p ls).1 = q ls) :
    (patternsMeter vs p).1 = patterns vs q := by
  induction vs generalizing p q with
  | nil => exact h []
  | cons v vs ih =>
    change ((patternsMeter vs (fun ls => p ((v,false)::ls))).1 &&
      (patternsMeter vs (fun ls => p ((v,true)::ls))).1) =
      (patterns vs (fun ls => q ((v,false)::ls)) &&
        patterns vs (fun ls => q ((v,true)::ls)))
    rw [ih _ _ (fun ls => h ((v,false)::ls)),
        ih _ _ (fun ls => h ((v,true)::ls))]

theorem patterns_bound (vs : List Nat) (p : Clause → Meter)
    (q : Clause → Nat) (h : ∀ ls, (p ls).2 ≤ q ls) :
    (patternsMeter vs p).2 ≤ patternsBudget vs q := by
  induction vs generalizing p q with
  | nil => exact h []
  | cons v vs ih =>
    exact Nat.add_le_add (Nat.add_le_add
      (ih _ _ (fun ls => h ((v,false)::ls)))
      (ih _ _ (fun ls => h ((v,true)::ls)))) (Nat.le_refl 1)

def blockMeter (f : Formula) (b : Block) : Meter :=
  if b.support.length ≤ 5 then
    let r := refsMeter f b.refs
    let p := patternsMeter b.support (patternMeter b)
    (r.1 && p.1,r.2+p.2+1)
  else (false,1)

def blockBudget (f : Formula) (b : Block) : Nat :=
  if b.support.length ≤ 5 then
    refsBudget f b.refs + patternsBudget b.support (patternBudget b) + 1
  else 1

theorem block_value (f : Formula) (b : Block) :
    (blockMeter f b).1 = blockCheck f b := by
  unfold blockMeter blockCheck test
  by_cases h : b.support.length ≤ 5
  · rw [if_pos h,if_pos h]
    change ((refsMeter f b.refs).1 &&
      (patternsMeter b.support (patternMeter b)).1) =
      (every (ProctorCapacityReplay.refCheck f) b.refs &&
        patterns b.support (patternCheck b))
    rw [refs_value,patterns_value _ _ _ (pattern_value b)]
  · rw [if_neg h,if_neg h] <;> rfl

theorem block_bound (f : Formula) (b : Block) :
    (blockMeter f b).2 ≤ blockBudget f b := by
  unfold blockMeter blockBudget
  by_cases h : b.support.length ≤ 5
  · rw [if_pos h,if_pos h]
    exact Nat.add_le_add (Nat.add_le_add (refs_bound f b.refs)
      (patterns_bound _ _ _ (pattern_bound b))) (Nat.le_refl 1)
  · rw [if_neg h,if_neg h] <;> exact Nat.le_refl 1

-- Sparse toggle: charge one equality comparison per examined label.
def toggleMeter (v : Nat) : List Nat → List Nat × Nat
  | [] => ([v],0)
  | a::as =>
    if v=a then (as,1)
    else
      let r := toggleMeter v as
      (a::r.1,r.2+1)

theorem toggle_value (v : Nat) (vs : List Nat) :
    (toggleMeter v vs).1 = toggle v vs := by
  induction vs with
  | nil => rfl
  | cons a as ih =>
    change (if v=a then (as,1) else
      (a::(toggleMeter v as).1,(toggleMeter v as).2+1)).1 =
      (if v=a then as else a::toggle v as)
    by_cases e : v=a
    · rw [if_pos e,if_pos e]
    · rw [if_neg e,if_neg e]
      exact congrArg (List.cons a) ih

theorem toggle_bound (v : Nat) (vs : List Nat) :
    (toggleMeter v vs).2 ≤ vs.length := by
  induction vs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change (if v=a then (as,1) else
      (a::(toggleMeter v as).1,(toggleMeter v as).2+1)).2 ≤ as.length+1
    by_cases e : v=a
    · rw [if_pos e]
      exact Nat.succ_le_succ (Nat.zero_le as.length)
    · rw [if_neg e]
      exact Nat.succ_le_succ ih

def combineMeter : List Nat → List Nat → List Nat × Nat
  | [],ys => (ys,0)
  | v::vs,ys =>
    let r := combineMeter vs ys
    let t := toggleMeter v r.1
    (t.1,r.2+t.2)

def combineBudget : List Nat → List Nat → Nat
  | [],_ => 0
  | _::vs,ys => combineBudget vs ys + (combine vs ys).length

theorem combine_value (a b : List Nat) :
    (combineMeter a b).1 = combine a b := by
  induction a with
  | nil => rfl
  | cons v vs ih =>
    change (toggleMeter v (combineMeter vs b).1).1 = toggle v (combine vs b)
    rw [toggle_value,ih]

theorem combine_bound (a b : List Nat) :
    (combineMeter a b).2 ≤ combineBudget a b := by
  induction a with
  | nil => exact Nat.le_refl 0
  | cons v vs ih =>
    change (combineMeter vs b).2 + (toggleMeter v (combineMeter vs b).1).2 ≤
      combineBudget vs b + (combine vs b).length
    rw [combine_value]
    exact Nat.add_le_add ih (toggle_bound v (combine vs b))

def sumMeter : List Block → List Nat × Nat
  | [] => ([],0)
  | b::bs =>
    let r := sumMeter bs
    let t := combineMeter b.support r.1
    (t.1,r.2+t.2)

def sumBudget : List Block → Nat
  | [] => 0
  | b::bs => sumBudget bs + combineBudget b.support (sumSupport bs)

theorem sum_value (bs : List Block) :
    (sumMeter bs).1 = sumSupport bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    change (combineMeter b.support (sumMeter bs).1).1 =
      combine b.support (sumSupport bs)
    rw [combine_value,ih]

theorem sum_bound (bs : List Block) :
    (sumMeter bs).2 ≤ sumBudget bs := by
  induction bs with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    change (sumMeter bs).2 + (combineMeter b.support (sumMeter bs).1).2 ≤
      sumBudget bs + combineBudget b.support (sumSupport bs)
    rw [sum_value]
    exact Nat.add_le_add ih (combine_bound b.support (sumSupport bs))

def rhsMeter : List Block → Meter
  | [] => (false,0)
  | b::bs =>
    let r := rhsMeter bs
    (bx b.rhs r.1,r.2+1)

theorem rhs_value (bs : List Block) :
    (rhsMeter bs).1 = sumRhs bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih => exact congrArg (bx b.rhs) ih

theorem rhs_count (bs : List Block) :
    (rhsMeter bs).2 = bs.length := by
  induction bs with
  | nil => rfl
  | cons b bs ih => exact congrArg Nat.succ ih

def xorMeter (f : Formula) (bs : List Block) : Meter :=
  let c := allMeter (blockMeter f) bs
  let s := sumMeter bs
  let r := rhsMeter bs
  (c.1 && (test (s.1=[]) && r.1),c.2+s.2+r.2+1)

def xorBudget (f : Formula) (bs : List Block) : Nat :=
  visitsBudget (blockBudget f) bs + sumBudget bs + bs.length + 1

theorem xor_value (f : Formula) (bs : List Block) :
    (xorMeter f bs).1 = xorCheck f bs := by
  unfold xorMeter xorCheck
  dsimp only
  rw [all_value _ _ _ (block_value f),sum_value,rhs_value]

theorem xor_bound (f : Formula) (bs : List Block) :
    (xorMeter f bs).2 ≤ xorBudget f bs := by
  unfold xorMeter xorBudget
  dsimp only
  rw [rhs_count]
  exact Nat.add_le_add (Nat.add_le_add
    (Nat.add_le_add (all_bound _ _ _ (block_bound f)) (sum_bound bs))
    (Nat.le_refl _)) (Nat.le_refl 1)

end ProctorXorMeter

#print axioms ProctorXorMeter.all_value
#print axioms ProctorXorMeter.all_bound
#print axioms ProctorXorMeter.any_value
#print axioms ProctorXorMeter.any_bound
#print axioms ProctorXorMeter.pattern_value
#print axioms ProctorXorMeter.pattern_bound
#print axioms ProctorXorMeter.patterns_value
#print axioms ProctorXorMeter.patterns_bound
#print axioms ProctorXorMeter.block_value
#print axioms ProctorXorMeter.block_bound
#print axioms ProctorXorMeter.toggle_value
#print axioms ProctorXorMeter.toggle_bound
#print axioms ProctorXorMeter.combine_value
#print axioms ProctorXorMeter.combine_bound
#print axioms ProctorXorMeter.sum_value
#print axioms ProctorXorMeter.sum_bound
#print axioms ProctorXorMeter.rhs_value
#print axioms ProctorXorMeter.rhs_count
#print axioms ProctorXorMeter.xor_value
#print axioms ProctorXorMeter.xor_bound
