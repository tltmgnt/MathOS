/-! F034: executable typed capacity checking. Append after
ProctorExecutableReplay. Explicit referenced rows are checked against
the supplied formula. Fixed capacities <=2 keep tuple enumeration
bounded in degree. The checker is sound but not Python-equivalent. -/
namespace ProctorCapacityReplay
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group Distinct ConflictEvidence opposite totalCapacity capacity_cnf_unsat)
open ProctorExecutableReplay (and_true_local contains contains_sound lookup lookup_mem)

def test (p : Prop) [Decidable p] : Bool := if p then true else false

theorem test_sound (p : Prop) [Decidable p] (h : test p = true) : p := by
  unfold test at h
  by_cases e : p
  · exact e
  · rw [if_neg e] at h
    exact Bool.noConfusion h

def every {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | a::as => p a && every p as

def someCheck {α : Type} (p : α → Bool) : List α → Bool
  | [] => false
  | a::as => p a || someCheck p as

theorem every_sound {α : Type} (p : α → Bool) (xs : List α)
    (h : every p xs = true) : ∀ a ∈ xs, p a = true := by
  induction xs with
  | nil =>
    intro a ha
    cases ha
  | cons a as ih =>
    change (p a && every p as) = true at h
    have hh := and_true_local _ _ h
    intro b hb
    cases hb with
    | head => exact hh.left
    | tail _ hm => exact ih hh.right b hm

theorem some_sound {α : Type} (p : α → Bool) (xs : List α)
    (h : someCheck p xs = true) : ∃ a ∈ xs, p a = true := by
  induction xs with
  | nil => exact Bool.noConfusion h
  | cons a as ih =>
    change (p a || someCheck p as) = true at h
    cases e : p a with
    | true => exact ⟨a,List.Mem.head _,e⟩
    | false =>
      rw [e] at h
      obtain ⟨b,hb,ht⟩ := ih h
      exact ⟨b,List.Mem.tail _ hb,ht⟩

def getAt {α : Type} : List α → Nat → Option α
  | [], _ => none
  | a::_, 0 => some a
  | _::as, i+1 => getAt as i

theorem getAt_mem {α : Type} (xs : List α) (i : Nat) (a : α)
    (h : getAt xs i = some a) : a ∈ xs := by
  induction xs generalizing i with
  | nil => cases h
  | cons b bs ih =>
    cases i with
    | zero =>
      change some b = some a at h
      have e := Option.some.inj h
      cases e
      exact List.Mem.head _
    | succ i => exact List.Mem.tail _ (ih i h)

theorem getAt_exists {α : Type} (xs : List α) (i : Nat)
    (h : i < xs.length) : ∃ a, getAt xs i = some a := by
  induction xs generalizing i with
  | nil => exact (Nat.not_lt_zero i h).elim
  | cons a as ih =>
    cases i with
    | zero => exact ⟨a,rfl⟩
    | succ i =>
      obtain ⟨b,hb⟩ := ih i (Nat.lt_of_succ_lt_succ h)
      exact ⟨b,hb⟩

structure RefRow where
  index : Nat
  row : Clause

def refCheck (f : Formula) (r : RefRow) : Bool :=
  match lookup f r.index with
  | none => false
  | some c => test (c = r.row)

theorem ref_sound (f : Formula) (r : RefRow)
    (h : refCheck f r = true) : r.row ∈ f := by
  unfold refCheck at h
  cases e : lookup f r.index with
  | none =>
    rw [e] at h
    exact Bool.noConfusion h
  | some c =>
    rw [e] at h
    have eq := test_sound (c = r.row) h
    exact eq ▸ lookup_mem f r.index c e

theorem contains_complete (l : Literal) (xs : Clause) (h : l ∈ xs) :
    contains l xs = true := by
  induction xs with
  | nil => cases h
  | cons a as ih =>
    change (if l=a then true else contains l as) = true
    by_cases e : l=a
    · rw [if_pos e]
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact ih hm

def distinctCheck : Clause → Bool
  | [] => true
  | a::as => if contains a as then false else distinctCheck as

theorem distinct_sound (xs : Clause) (h : distinctCheck xs = true) :
    Distinct xs := by
  induction xs with
  | nil => exact Distinct.nil
  | cons a as ih =>
    change (if contains a as then false else distinctCheck as) = true at h
    cases e : contains a as with
    | true =>
      rw [e] at h
      exact Bool.noConfusion h
    | false =>
      rw [e] at h
      exact Distinct.cons
        (fun hm => Bool.noConfusion (e.symm.trans (contains_complete a as hm)))
        (ih h)

theorem distinct_complete (xs : Clause) (h : Distinct xs) :
    distinctCheck xs = true := by
  induction h with
  | nil => rfl
  | @cons a as hn hd ih =>
    change (if contains a as then false else distinctCheck as) = true
    cases e : contains a as with
    | true => exact (hn (contains_sound a as e)).elim
    | false =>
      rw [e]
      exact ih

/-- Check every ordered word of length k over xs. Repetitions are
allowed in enumeration, then excluded by distinctCheck. -/
def words (xs : Clause) : Nat → (Clause → Bool) → Bool
  | 0, p => p []
  | k+1, p => every (fun a => words xs k (fun rest => p (a::rest))) xs

theorem words_sound (xs : Clause) (k : Nat) (p : Clause → Bool)
    (h : words xs k p = true) (ys : Clause) (len : ys.length = k)
    (sub : ∀ l, l ∈ ys → l ∈ xs) : p ys = true := by
  induction k generalizing p ys with
  | zero =>
    cases ys with
    | nil => exact h
    | cons a as => exact Nat.noConfusion len
  | succ k ih =>
    cases ys with
    | nil => exact Nat.noConfusion len
    | cons a as =>
      have ha := every_sound _ xs h a (sub a (List.Mem.head _))
      exact ih (fun rest => p (a::rest)) ha as (Nat.succ.inj len)
        (fun l hl => sub l (List.Mem.tail _ hl))

def conflictCheck (refs : List RefRow) (ys : Clause) : Bool :=
  someCheck (fun r => every (fun l =>
    someCheck (fun p => test (l = opposite p)) ys) r.row) refs

def groupCheck (refs : List RefRow) (g : Group) : Bool :=
  test (g.cap ≤ 2) && (distinctCheck g.literals &&
    words g.literals (g.cap+1) (fun ys =>
      if distinctCheck ys then conflictCheck refs ys else true))

theorem group_sound (f : Formula) (refs : List RefRow) (g : Group)
    (valid : every (refCheck f) refs = true)
    (h : groupCheck refs g = true) :
    Distinct g.literals ∧ ConflictEvidence f g := by
  unfold groupCheck at h
  have hh := and_true_local _ _ (and_true_local _ _ h).right
  refine ⟨distinct_sound _ hh.left, ?_⟩
  intro ys len hd sub
  have w := words_sound g.literals (g.cap+1) _ hh.right ys len sub
  change (if distinctCheck ys then conflictCheck refs ys else true) = true at w
  rw [distinct_complete ys hd] at w
  obtain ⟨r,hr,hc⟩ := some_sound _ refs w
  refine ⟨r.row,ref_sound f r (every_sound _ refs valid r hr), ?_⟩
  intro l hl
  obtain ⟨p,hp,he⟩ := some_sound _ ys (every_sound _ r.row hc l hl)
  exact ⟨p,hp,test_sound _ he⟩

def indices : Nat → List Nat
  | 0 => []
  | k+1 => k :: indices k

theorem index_mem (d i : Nat) (h : i < d) : i ∈ indices d := by
  induction d with
  | zero => exact (Nat.not_lt_zero i h).elim
  | succ d ih =>
    by_cases e : i=d
    · cases e
      exact List.Mem.head _
    · exact List.Mem.tail _ (ih (Nat.lt_of_le_of_ne (Nat.le_of_lt_succ h) e))

def demandAt (ds : List RefRow) (i : Nat) : Clause :=
  match getAt ds i with
  | some r => r.row
  | none => []

theorem demand_at_mem (ds : List RefRow) (i : Nat) (hi : i < ds.length) :
    ∃ r ∈ ds, demandAt ds i = r.row := by
  obtain ⟨r,hr⟩ := getAt_exists ds i hi
  refine ⟨r,getAt_mem ds i r hr,?_⟩
  unfold demandAt
  rw [hr]

def different (ds : List RefRow) (i j : Nat) : Bool :=
  if i=j then true else
    every (fun a => every (fun b => test (a.1 ≠ b.1)) (demandAt ds j)) (demandAt ds i)

theorem different_sound (ds : List RefRow) (i j : Nat)
    (h : different ds i j = true) (a b : Literal)
    (ha : a ∈ demandAt ds i) (hb : b ∈ demandAt ds j)
    (eq : a.1=b.1) : i=j := by
  by_cases e : i=j
  · exact e
  · unfold different at h
    rw [if_neg e] at h
    exact (test_sound (a.1 ≠ b.1) (every_sound _ _ (every_sound _ _ h a ha) b hb) eq).elim

structure Certificate where
  demands : List RefRow
  groups : List Group
  conflicts : List RefRow

def capacityCheck (f : Formula) (c : Certificate) : Bool :=
  every (refCheck f) c.demands &&
  (every (refCheck f) c.conflicts &&
  (every (groupCheck c.conflicts) c.groups &&
  (every (fun i => every (different c.demands i) (indices c.demands.length))
      (indices c.demands.length) &&
  (every (fun r => every (fun l =>
      someCheck (fun g => contains l g.literals) c.groups) r.row) c.demands &&
    test (totalCapacity c.groups < c.demands.length)))))

theorem capacity_check_sound (f : Formula) (c : Certificate)
    (h : capacityCheck f c = true) : ¬ ∃ x : Assignment, FormulaSat f x := by
  unfold capacityCheck at h
  have h1 := and_true_local _ _ h
  have h2 := and_true_local _ _ h1.right
  have h3 := and_true_local _ _ h2.right
  have h4 := and_true_local _ _ h3.right
  have h5 := and_true_local _ _ h4.right
  apply capacity_cnf_unsat f (demandAt c.demands) c.demands.length c.groups
  · intro i j hi hj a ha b hb eq
    exact different_sound c.demands i j
      (every_sound _ _ (every_sound _ _ h4.left i (index_mem _ _ hi)) j (index_mem _ _ hj))
      a b ha hb eq
  · intro i hi l hl
    obtain ⟨r,hr,he⟩ := demand_at_mem c.demands i hi
    rw [he] at hl
    obtain ⟨g,hg,hc⟩ := some_sound _ c.groups
      (every_sound _ r.row (every_sound _ _ h5.left r hr) l hl)
    exact ⟨g,hg,contains_sound _ _ hc⟩
  · intro g hg
    exact (group_sound f c.conflicts g h2.left (every_sound _ _ h3.left g hg)).left
  · intro g hg
    exact (group_sound f c.conflicts g h2.left (every_sound _ _ h3.left g hg)).right
  · intro i hi
    obtain ⟨r,hr,he⟩ := demand_at_mem c.demands i hi
    rw [he]
    exact ref_sound f r (every_sound _ _ h1.left r hr)
  · exact test_sound _ h5.right

def checkChainCapacity (f : Formula) (bs : List ProctorExecutableReplay.Batch)
    (c : Certificate) : Bool :=
  ProctorExecutableReplay.chainCheck f bs &&
    capacityCheck (ProctorExecutableReplay.frontier f bs) c

theorem checked_chain_capacity_refutes (f : Formula)
    (bs : List ProctorExecutableReplay.Batch) (c : Certificate)
    (h : checkChainCapacity f bs c = true) :
    ¬ ∃ x : Assignment, FormulaSat f x := by
  unfold checkChainCapacity at h
  have hh := and_true_local _ _ h
  exact ProctorMixedInference.derived_unsat_lifts f _
    (ProctorExecutableReplay.chain_sound f bs hh.left)
    (capacity_check_sound _ c hh.right)

end ProctorCapacityReplay

#print axioms ProctorCapacityReplay.test_sound
#print axioms ProctorCapacityReplay.every_sound
#print axioms ProctorCapacityReplay.some_sound
#print axioms ProctorCapacityReplay.getAt_mem
#print axioms ProctorCapacityReplay.getAt_exists
#print axioms ProctorCapacityReplay.ref_sound
#print axioms ProctorCapacityReplay.contains_complete
#print axioms ProctorCapacityReplay.distinct_sound
#print axioms ProctorCapacityReplay.distinct_complete
#print axioms ProctorCapacityReplay.words_sound
#print axioms ProctorCapacityReplay.group_sound
#print axioms ProctorCapacityReplay.index_mem
#print axioms ProctorCapacityReplay.demand_at_mem
#print axioms ProctorCapacityReplay.different_sound
#print axioms ProctorCapacityReplay.capacity_check_sound
#print axioms ProctorCapacityReplay.checked_chain_capacity_refutes
