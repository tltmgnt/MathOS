/-! F035: all-order multiplicity obstruction for raw, unsimplified
factored elimination. No claim about normalized resolution, other
representations, or unrestricted SAT algorithms. -/
namespace ProctorAllOrderBarrier
open ProctorHallDeficiency
open ProctorGeneralBranching (reduceRow)
open ProctorAdaptiveElimination (Buckets split eliminate)
open ProctorSemanticProjection (rowProduct orProduct)
open ProctorTotalTwoCNF (supported supported_iff)

def countRow (c : Clause) : Formula → Nat
  | [] => 0
  | d::ds => if c=d then countRow c ds+1 else countRow c ds

theorem count_cons_ge (c d : Clause) (f : Formula) :
    countRow c f≤countRow c (d::f) := by
  change countRow c f≤(if c=d then countRow c f+1 else countRow c f)
  by_cases h : c=d
  · rw [if_pos h]
    exact Nat.le_succ _
  · rw [if_neg h]
    exact Nat.le_refl _

theorem count_length (c : Clause) (f : Formula) : countRow c f≤f.length := by
  induction f with
  | nil => exact Nat.le_refl _
  | cons d ds ih =>
    change (if c=d then countRow c ds+1 else countRow c ds)≤ds.length+1
    by_cases h : c=d
    · rw [if_pos h]
      exact Nat.succ_le_succ ih
    · rw [if_neg h]
      exact Nat.le_trans ih (Nat.le_succ _)

theorem count_append (c : Clause) (f g : Formula) :
    countRow c (f++g)=countRow c f+countRow c g := by
  induction f with
  | nil => exact (Nat.zero_add _).symm
  | cons d ds ih =>
    change (if c=d then countRow c (ds++g)+1 else countRow c (ds++g))=
      (if c=d then countRow c ds+1 else countRow c ds)+countRow c g
    by_cases h : c=d
    · rw [if_pos h,if_pos h,ih,Nat.add_assoc (countRow c ds) 1,
        Nat.add_comm 1 (countRow c g),← Nat.add_assoc]
    · rw [if_neg h,if_neg h,ih]

theorem count_positive (c : Clause) (f : Formula) (h : 0<countRow c f) : c∈f := by
  induction f with
  | nil => exact (Nat.not_lt_zero _ h).elim
  | cons d ds ih =>
    by_cases he : c=d
    · cases he
      exact List.Mem.head _
    · change 0<(if c=d then countRow c ds+1 else countRow c ds) at h
      rw [if_neg he] at h
      exact List.Mem.tail _ (ih h)

inductive Side where
  | common | left | right

def bucket (s : Side) (t : Buckets) : Formula :=
  match s with
  | .common => t.common
  | .left => t.left
  | .right => t.right

theorem split_cons (s : Side) (v : Nat) (c : Clause) (f : Formula) :
    bucket s (split v (c::f))=bucket s (split v [c])++bucket s (split v f) := by
  rw [split,split]
  cases h0 : reduceRow v false c <;> cases h1 : reduceRow v true c <;> cases s <;> rfl

theorem split_count (s : Side) (v : Nat) (c r : Clause) (f : Formula)
    (h : bucket s (split v [c])=[r]) :
    countRow c f≤countRow r (bucket s (split v f)) := by
  induction f with
  | nil => exact Nat.zero_le _
  | cons d ds ih =>
    rw [split_cons,count_append]
    change (if c=d then countRow c ds+1 else countRow c ds)≤_
    by_cases he : c=d
    · cases he
      rw [if_pos rfl,h]
      have h1 : countRow r [r]=1 := by
        change (if r=r then 0+1 else 0)=1
        rw [if_pos rfl]
      rw [h1]
      rw [Nat.add_comm 1]
      exact Nat.succ_le_succ ih
    · rw [if_neg he]
      exact Nat.le_trans ih (Nat.le_add_left _ _)

theorem row_product_count (a b : Clause) (g : Formula) :
    countRow b g≤countRow (a++b) (rowProduct a g) := by
  induction g with
  | nil => exact Nat.le_refl _
  | cons d ds ih =>
    change (if b=d then countRow b ds+1 else countRow b ds)≤
      countRow (a++b) ((a++d)::rowProduct a ds)
    by_cases h : b=d
    · cases h
      rw [if_pos rfl]
      change countRow b ds+1≤(if a++b=a++b then countRow (a++b) (rowProduct a ds)+1 else _)
      rw [if_pos rfl]
      exact Nat.succ_le_succ ih
    · rw [if_neg h]
      exact Nat.le_trans ih (count_cons_ge _ _ _)

theorem product_count (a b : Clause) (f g : Formula) :
    countRow a f*countRow b g≤countRow (a++b) (orProduct f g) := by
  induction f with
  | nil =>
    change 0*countRow b g≤0
    rw [Nat.zero_mul]
    exact Nat.le_refl _
  | cons c cs ih =>
    change (if a=c then countRow a cs+1 else countRow a cs)*countRow b g≤
      countRow (a++b) (rowProduct c g++orProduct cs g)
    rw [count_append]
    by_cases h : a=c
    · cases h
      rw [if_pos rfl,Nat.mul_comm (countRow a cs+1),Nat.mul_succ,
        Nat.mul_comm (countRow b g) (countRow a cs),Nat.add_comm (countRow a cs*countRow b g)]
      exact Nat.add_le_add (row_product_count a b g) ih
    · rw [if_neg h]
      exact Nat.le_trans ih (Nat.le_add_left _ _)

private theorem reduce_other (v : Nat) (b : Bool) (l : Literal) (ls : Clause)
    (h : l.1≠v) : reduceRow v b (l::ls)=(reduceRow v b ls).map (fun r => l::r) := by
  change (if l.1=v then (if l.2=b then none else reduceRow v b ls)
    else (reduceRow v b ls).map (fun r => l::r))=_
  rw [if_neg h]

theorem reduce_untouched (v : Nat) (b : Bool) (c : Clause)
    (h : ∀ l∈c,l.1≠v) : reduceRow v b c=some c := by
  induction c with
  | nil => rfl
  | cons l ls ih =>
    rw [reduce_other v b l ls (h l (List.Mem.head _)),
      ih (fun a ha => h a (List.Mem.tail _ ha))]
    rfl

theorem common_single (v : Nat) (c : Clause) (h : ∀ l∈c,l.1≠v) :
    bucket .common (split v [c])=[c] := by
  unfold split
  dsimp only
  rw [reduce_untouched v false c h,reduce_untouched v true c h]
  rfl

theorem left_single (v u : Nat) (b : Bool) (h : u≠v) :
    bucket .left (split v [[(v,true),(u,b)]])=[[(u,b)]] := by
  have h0 : reduceRow v false [(v,true),(u,b)]=some [(u,b)] := by
    rw [reduceRow,if_pos rfl,if_neg (by decide : true≠false)]
    exact reduce_untouched v false _ (fun l hl => by cases hl with
      | head => exact h
      | tail _ hm => cases hm)
  have h1 : reduceRow v true [(v,true),(u,b)]=none := by
    rw [reduceRow,if_pos rfl,if_pos rfl]
  unfold split
  dsimp only
  rw [h0,h1]
  rfl

theorem right_single (v u : Nat) (b : Bool) (h : u≠v) :
    bucket .right (split v [[(v,false),(u,b)]])=[[(u,b)]] := by
  have h1 : reduceRow v true [(v,false),(u,b)]=some [(u,b)] := by
    rw [reduceRow,if_pos rfl,if_neg (by decide : false≠true)]
    exact reduce_untouched v true _ (fun l hl => by cases hl with
      | head => exact h
      | tail _ hm => cases hm)
  have h0 : reduceRow v false [(v,false),(u,b)]=none := by
    rw [reduceRow,if_pos rfl,if_pos rfl]
  unfold split
  dsimp only
  rw [h0,h1]
  rfl

def Rich (f : Formula) (m : Nat) (vs : List Nat) : Prop :=
  ∀ u∈vs,∀ w∈vs,u≠w → ∀ a b : Bool,
    m≤countRow [(u,a),(w,b)] f

def marker (u : Nat) : Clause := [(u,true),(u,true),(u,true)]

def Marked (f : Formula) (vs : List Nat) : Prop :=
  ∀ u∈vs, 0<countRow (marker u) f

theorem rich_step (f : Formula) (v : Nat) (vs : List Nat) (m : Nat)
    (hf : Rich f m (v::vs)) (fresh : ∀ u∈vs,u≠v) :
    Rich (eliminate v f) (m+m*m) vs := by
  intro u hu w hw huw a b
  let c : Clause := [(u,a),(w,b)]
  let t := split v f
  have hc : ∀ l∈c,l.1≠v := by
    intro l hl
    change l∈[(u,a),(w,b)] at hl
    cases hl with
    | head => exact fresh u hu
    | tail _ hm =>
      cases hm with
      | head => exact fresh w hw
      | tail _ hz => cases hz
  have hcommon := Nat.le_trans
    (hf u (List.Mem.tail _ hu) w (List.Mem.tail _ hw) huw a b)
    (split_count .common v c c f (common_single v c hc))
  have hl := Nat.le_trans
    (hf v (List.Mem.head _) u (List.Mem.tail _ hu) (fun h => fresh u hu h.symm) true a)
    (split_count .left v [(v,true),(u,a)] [(u,a)] f (left_single v u a (fresh u hu)))
  have hr := Nat.le_trans
    (hf v (List.Mem.head _) w (List.Mem.tail _ hw) (fun h => fresh w hw h.symm) false b)
    (split_count .right v [(v,false),(w,b)] [(w,b)] f (right_single v w b (fresh w hw)))
  have hp := Nat.le_trans (Nat.mul_le_mul hl hr) (product_count [(u,a)] [(w,b)] t.left t.right)
  change m+m*m≤countRow c (t.common++orProduct t.left t.right)
  rw [count_append]
  exact Nat.add_le_add hcommon hp

theorem marked_step (f : Formula) (v : Nat) (vs : List Nat)
    (hf : Marked f (v::vs)) (fresh : ∀ u∈vs,u≠v) :
    Marked (eliminate v f) vs := by
  intro u hu
  have hc : ∀ l∈marker u,l.1≠v := by
    intro l hl
    cases hl with
    | head => exact fresh u hu
    | tail _ hm =>
      cases hm with
      | head => exact fresh u hu
      | tail _ hn =>
        cases hn with
        | head => exact fresh u hu
        | tail _ hz => cases hz
  have h := split_count .common v (marker u) (marker u) f (common_single v _ hc)
  change 0<countRow (marker u) ((split v f).common++orProduct (split v f).left (split v f).right)
  rw [count_append]
  exact Nat.lt_of_lt_of_le (hf u (List.Mem.tail _ hu))
    (Nat.le_trans h (Nat.le_add_right _ _))

theorem marked_blocks_leaf (f : Formula) (u : Nat)
    (h : 0<countRow (marker u) f) : supported f=false := by
  cases e : supported f with
  | false => rfl
  | true =>
    have hw := (supported_iff f).1 e (marker u) (count_positive _ _ h)
    exact (Nat.not_succ_le_self 2 hw).elim

theorem rich_lower (f : Formula) (m : Nat) (vs : List Nat) (u w : Nat)
    (h : Rich f m vs) (hu : u∈vs) (hw : w∈vs) (he : u≠w) :
    m≤f.length :=
  Nat.le_trans (h u hu w hw he true true) (count_length _ _)

-- A pre may be any sequence of distinct offered variables.
-- Keep its unprocessed suffix as part of the invariant.
def Distinct : List Nat → Prop
  | [] => True
  | v::vs => (∀ u∈vs,u≠v) ∧ Distinct vs

def advance : List Nat → Formula → Formula
  | [],f => f
  | v::vs,f => advance vs (eliminate v f)

def growth : Nat → Nat → Nat
  | 0,m => m
  | k+1,m => growth k (m+m*m)

theorem rich_prefix (pre suffix : List Nat) (f : Formula) (m : Nat)
    (hd : Distinct (pre++suffix)) (hr : Rich f m (pre++suffix)) :
    Rich (advance pre f) (growth pre.length m) suffix := by
  induction pre generalizing f m with
  | nil => exact hr
  | cons v vs ih =>
    change (∀ u∈vs++suffix,u≠v) ∧ Distinct (vs++suffix) at hd
    exact ih (eliminate v f) (m+m*m) hd.2 (rich_step f v (vs++suffix) m hr hd.1)

theorem marked_prefix (pre suffix : List Nat) (f : Formula)
    (hd : Distinct (pre++suffix)) (hm : Marked f (pre++suffix)) :
    Marked (advance pre f) suffix := by
  induction pre generalizing f with
  | nil => exact hm
  | cons v vs ih =>
    change (∀ u∈vs++suffix,u≠v) ∧ Distinct (vs++suffix) at hd
    exact ih (eliminate v f) hd.2 (marked_step f v (vs++suffix) hm hd.1)

theorem growth_exponential (k m : Nat) (hm : 1≤m) :
    2^k*m≤growth k m := by
  induction k generalizing m with
  | zero =>
    change 1*m≤m
    rw [Nat.one_mul]
    exact Nat.le_refl _
  | succ k ih =>
    have hmul : m≤m*m := by
      have h := Nat.mul_le_mul_left m hm
      rw [Nat.mul_one] at h
      exact h
    have hstep : m+m≤m+m*m := Nat.add_le_add_left hmul _
    have hpos : 1≤m+m*m := Nat.le_trans hm (Nat.le_add_right _ _)
    have h := ih (m+m*m) hpos
    have h2 := Nat.mul_le_mul_left (2^k) hstep
    have he : 2^(k+1)*m=2^k*(m+m) := by
      rw [Nat.pow_succ,Nat.mul_succ,Nat.mul_one]
      -- distribute without relying on propositional extensionality
      have hadd : ∀ a b c : Nat,a*(b+c)=a*b+a*c := by
        intro a b c
        induction c with
        | zero => rfl
        | succ c ih =>
          change a*(b+c+1)=a*b+a*(c+1)
          rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]
      rw [Nat.mul_comm (2^k+2^k) m,hadd,hadd,Nat.mul_comm m (2^k)]
    rw [he]
    exact Nat.le_trans h2 h

theorem all_order_prefix_bound (pre suffix : List Nat) (f : Formula)
    (hd : Distinct (pre++suffix)) (hr : Rich f 1 (pre++suffix))
    (u w : Nat) (hu : u∈suffix) (hw : w∈suffix) (he : u≠w) :
    2^pre.length≤(advance pre f).length := by
  have h := growth_exponential pre.length 1 (Nat.le_refl 1)
  rw [Nat.mul_one] at h
  exact Nat.le_trans h (rich_lower _ _ _ u w (rich_prefix pre suffix f 1 hd hr) hu hw he)

theorem all_order_prefix_unsupported (pre suffix : List Nat) (f : Formula)
    (hd : Distinct (pre++suffix)) (hm : Marked f (pre++suffix))
    (u : Nat) (hu : u∈suffix) : supported (advance pre f)=false :=
  marked_blocks_leaf _ u (marked_prefix pre suffix f hd hm u hu)

end ProctorAllOrderBarrier

#print axioms ProctorAllOrderBarrier.count_cons_ge
#print axioms ProctorAllOrderBarrier.count_length
#print axioms ProctorAllOrderBarrier.count_append
#print axioms ProctorAllOrderBarrier.count_positive
#print axioms ProctorAllOrderBarrier.split_cons
#print axioms ProctorAllOrderBarrier.split_count
#print axioms ProctorAllOrderBarrier.row_product_count
#print axioms ProctorAllOrderBarrier.product_count
#print axioms ProctorAllOrderBarrier.reduce_untouched
#print axioms ProctorAllOrderBarrier.common_single
#print axioms ProctorAllOrderBarrier.left_single
#print axioms ProctorAllOrderBarrier.right_single
#print axioms ProctorAllOrderBarrier.rich_step
#print axioms ProctorAllOrderBarrier.marked_step
#print axioms ProctorAllOrderBarrier.marked_blocks_leaf
#print axioms ProctorAllOrderBarrier.rich_lower

#print axioms ProctorAllOrderBarrier.rich_prefix
#print axioms ProctorAllOrderBarrier.marked_prefix
#print axioms ProctorAllOrderBarrier.growth_exponential
#print axioms ProctorAllOrderBarrier.all_order_prefix_bound
#print axioms ProctorAllOrderBarrier.all_order_prefix_unsupported
