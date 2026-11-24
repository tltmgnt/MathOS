/-! F034: compositional abstract meters for the typed capacity terminal.
Counts include selected list visits, lookup cells, and atomic comparisons.
Eager evaluation is intentionally not the production short-circuit trace. -/
namespace ProctorCapacityMeter
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group opposite totalCapacity)
open ProctorCapacityReplay (RefRow Certificate every someCheck test distinctCheck words conflictCheck groupCheck getAt demandAt different indices capacityCheck)
open ProctorCheckerCost (containsMeter contains_value contains_bound)
open ProctorChainMeter (both refsMeter refsBudget refs_value refs_bound)

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

def distinctMeter : Clause → Meter
  | [] => (true,0)
  | a::as =>
    let m := containsMeter a as
    let r := distinctMeter as
    (if m.1 then false else r.1,m.2+r.2)

def distinctBudget : Clause → Nat
  | [] => 0
  | _::as => as.length + distinctBudget as

theorem distinct_value (xs : Clause) :
    (distinctMeter xs).1 = distinctCheck xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (if (containsMeter a as).1 then false else (distinctMeter as).1) =
      (if ProctorExecutableReplay.contains a as then false else distinctCheck as)
    rw [contains_value,ih]

theorem distinct_bound (xs : Clause) :
    (distinctMeter xs).2 ≤ distinctBudget xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih => exact Nat.add_le_add (contains_bound a as) ih

/-- Enumerate exactly the ordered words of the original checker,
including repetitions. Each non-root edge is one list visit. -/
def wordsMeter (xs : Clause) : Nat → (Clause → Meter) → Meter
  | 0,p => p []
  | k+1,p => allMeter (fun a => wordsMeter xs k (fun rest => p (a::rest))) xs

def wordsBudget (xs : Clause) : Nat → (Clause → Nat) → Nat
  | 0,q => q []
  | k+1,q => visitsBudget (fun a => wordsBudget xs k (fun rest => q (a::rest))) xs

theorem words_value (xs : Clause) (k : Nat) (p : Clause → Meter)
    (q : Clause → Bool) (h : ∀ ys, (p ys).1 = q ys) :
    (wordsMeter xs k p).1 = words xs k q := by
  induction k generalizing p q with
  | zero => exact h []
  | succ k ih =>
    change (allMeter (fun a => wordsMeter xs k (fun rest => p (a::rest))) xs).1 =
      every (fun a => words xs k (fun rest => q (a::rest))) xs
    apply all_value
    intro a
    exact ih (fun rest => p (a::rest)) (fun rest => q (a::rest)) (fun rest => h (a::rest))

theorem words_bound (xs : Clause) (k : Nat) (p : Clause → Meter)
    (q : Clause → Nat) (h : ∀ ys, (p ys).2 ≤ q ys) :
    (wordsMeter xs k p).2 ≤ wordsBudget xs k q := by
  induction k generalizing p q with
  | zero => exact h []
  | succ k ih =>
    change (allMeter (fun a => wordsMeter xs k (fun rest => p (a::rest))) xs).2 ≤
      visitsBudget (fun a => wordsBudget xs k (fun rest => q (a::rest))) xs
    apply all_bound
    intro a
    exact ih (fun rest => p (a::rest)) (fun rest => q (a::rest)) (fun rest => h (a::rest))

def conflictMeter (refs : List RefRow) (ys : Clause) : Meter :=
  anyMeter (fun r => allMeter (fun l =>
    anyMeter (fun p => (test (l=opposite p),1)) ys) r.row) refs

def conflictBudget (refs : List RefRow) (ys : Clause) : Nat :=
  visitsBudget (fun r => visitsBudget (fun _ =>
    visitsBudget (fun _ => 1) ys) r.row) refs

theorem conflict_value (refs : List RefRow) (ys : Clause) :
    (conflictMeter refs ys).1 = conflictCheck refs ys := by
  unfold conflictMeter conflictCheck
  apply any_value
  intro r
  apply all_value
  intro l
  apply any_value
  intro p
  rfl

theorem conflict_bound (refs : List RefRow) (ys : Clause) :
    (conflictMeter refs ys).2 ≤ conflictBudget refs ys := by
  unfold conflictMeter conflictBudget
  apply any_bound
  intro r
  apply all_bound
  intro l
  apply any_bound
  intro p
  exact Nat.le_refl 1

def tupleMeter (refs : List RefRow) (ys : Clause) : Meter :=
  let d := distinctMeter ys
  if d.1 then
    let c := conflictMeter refs ys
    (c.1,d.2+c.2)
  else (true,d.2)

def tupleBudget (refs : List RefRow) (ys : Clause) : Nat :=
  distinctBudget ys + conflictBudget refs ys

theorem tuple_value (refs : List RefRow) (ys : Clause) :
    (tupleMeter refs ys).1 =
      (if distinctCheck ys then conflictCheck refs ys else true) := by
  unfold tupleMeter
  dsimp only
  rw [distinct_value]
  cases distinctCheck ys with
  | false => rfl
  | true => exact conflict_value refs ys

theorem tuple_bound (refs : List RefRow) (ys : Clause) :
    (tupleMeter refs ys).2 ≤ tupleBudget refs ys := by
  unfold tupleMeter tupleBudget
  dsimp only
  cases (distinctMeter ys).1 with
  | false =>
    exact Nat.le_trans (distinct_bound ys) (Nat.le_add_right _ _)
  | true => exact Nat.add_le_add (distinct_bound ys) (conflict_bound refs ys)

def groupMeter (refs : List RefRow) (g : Group) : Meter :=
  if g.cap ≤ 2 then
    let d := distinctMeter g.literals
    let w := wordsMeter g.literals (g.cap+1) (tupleMeter refs)
    (d.1 && w.1,d.2+w.2+1)
  else (false,1)

def groupBudget (refs : List RefRow) (g : Group) : Nat :=
  if g.cap ≤ 2 then
    distinctBudget g.literals +
      wordsBudget g.literals (g.cap+1) (tupleBudget refs) + 1
  else 1

theorem group_value (refs : List RefRow) (g : Group) :
    (groupMeter refs g).1 = groupCheck refs g := by
  unfold groupMeter groupCheck test
  by_cases h : g.cap ≤ 2
  · rw [if_pos h,if_pos h]
    change ((distinctMeter g.literals).1 &&
      (wordsMeter g.literals (g.cap+1) (tupleMeter refs)).1) =
      (distinctCheck g.literals && words g.literals (g.cap+1)
        (fun ys => if distinctCheck ys then conflictCheck refs ys else true))
    rw [distinct_value,words_value _ _ _ _ (tuple_value refs)]
  · rw [if_neg h,if_neg h] <;> rfl

theorem group_bound (refs : List RefRow) (g : Group) :
    (groupMeter refs g).2 ≤ groupBudget refs g := by
  unfold groupMeter groupBudget
  by_cases h : g.cap ≤ 2
  · rw [if_pos h,if_pos h]
    exact Nat.add_le_add (Nat.add_le_add (distinct_bound g.literals)
      (words_bound _ _ _ _ (tuple_bound refs))) (Nat.le_refl 1)
  · rw [if_neg h,if_neg h] <;> exact Nat.le_refl 1

def atMeter {α : Type} : List α → Nat → Option α × Nat
  | [],_ => (none,0)
  | a::_,0 => (some a,1)
  | _::as,i+1 =>
    let r := atMeter as i
    (r.1,r.2+1)

theorem at_value {α : Type} (xs : List α) (i : Nat) :
    (atMeter xs i).1 = getAt xs i := by
  induction xs generalizing i with
  | nil => rfl
  | cons a as ih =>
    cases i with
    | zero => rfl
    | succ i => exact ih i

theorem at_bound {α : Type} (xs : List α) (i : Nat) :
    (atMeter xs i).2 ≤ xs.length := by
  induction xs generalizing i with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    cases i with
    | zero => exact Nat.succ_le_succ (Nat.zero_le as.length)
    | succ i => exact Nat.succ_le_succ (ih i)

def demandMeter (ds : List RefRow) (i : Nat) : Clause × Nat :=
  let r := atMeter ds i
  let row := match r.1 with | some a => a.row | none => []
  (row,r.2)

theorem demand_value (ds : List RefRow) (i : Nat) :
    (demandMeter ds i).1 = demandAt ds i := by
  unfold demandMeter demandAt
  dsimp only
  rw [at_value]

theorem demand_bound (ds : List RefRow) (i : Nat) :
    (demandMeter ds i).2 ≤ ds.length :=
  at_bound ds i

/-- Hoist the two indexed demand lookups once per unequal pair.
This is a value-equivalent algorithm, not a trace claim. -/
def differentMeter (ds : List RefRow) (i j : Nat) : Meter :=
  if i=j then (true,1)
  else
    let a := demandMeter ds i
    let b := demandMeter ds j
    let r := allMeter (fun l => allMeter (fun m => (test (l.1≠m.1),1)) b.1) a.1
    (r.1,a.2+b.2+r.2+1)

def differentBudget (ds : List RefRow) (i j : Nat) : Nat :=
  if i=j then 1 else ds.length+ds.length+
    visitsBudget (fun _ => visitsBudget (fun _ => 1) (demandAt ds j))
      (demandAt ds i)+1

theorem different_value (ds : List RefRow) (i j : Nat) :
    (differentMeter ds i j).1 = different ds i j := by
  unfold differentMeter different
  by_cases e : i=j
  · rw [if_pos e,if_pos e]
  · rw [if_neg e,if_neg e]
    dsimp only
    rw [demand_value,demand_value]
    apply all_value
    intro a
    apply all_value
    intro b
    rfl

theorem different_bound (ds : List RefRow) (i j : Nat) :
    (differentMeter ds i j).2 ≤ differentBudget ds i j := by
  unfold differentMeter differentBudget
  by_cases e : i=j
  · rw [if_pos e,if_pos e] <;> exact Nat.le_refl 1
  · rw [if_neg e,if_neg e]
    dsimp only
    rw [demand_value,demand_value]
    apply Nat.add_le_add
    · apply Nat.add_le_add
      · exact Nat.add_le_add (demand_bound ds i) (demand_bound ds j)
      · apply all_bound
        intro a
        apply all_bound
        intro b
        exact Nat.le_refl 1
    · exact Nat.le_refl 1

def coverageMeter (ds : List RefRow) (gs : List Group) : Meter :=
  allMeter (fun r => allMeter (fun l =>
    anyMeter (fun g => containsMeter l g.literals) gs) r.row) ds

def coverageBudget (ds : List RefRow) (gs : List Group) : Nat :=
  visitsBudget (fun r => visitsBudget (fun _ =>
    visitsBudget (fun g => g.literals.length) gs) r.row) ds

theorem coverage_value (ds : List RefRow) (gs : List Group) :
    (coverageMeter ds gs).1 = every (fun r => every (fun l =>
      someCheck (fun g => ProctorExecutableReplay.contains l g.literals) gs) r.row) ds := by
  unfold coverageMeter
  apply all_value
  intro r
  apply all_value
  intro l
  apply any_value
  intro g
  exact contains_value l g.literals

theorem coverage_bound (ds : List RefRow) (gs : List Group) :
    (coverageMeter ds gs).2 ≤ coverageBudget ds gs := by
  unfold coverageMeter coverageBudget
  apply all_bound
  intro r
  apply all_bound
  intro l
  apply any_bound
  intro g
  exact contains_bound l g.literals

def capacityMeter (f : Formula) (c : Certificate) : Meter :=
  both (refsMeter f c.demands)
    (both (refsMeter f c.conflicts)
    (both (allMeter (groupMeter c.conflicts) c.groups)
    (both (allMeter (fun i => allMeter (differentMeter c.demands i)
      (indices c.demands.length)) (indices c.demands.length))
    (both (coverageMeter c.demands c.groups)
      (test (totalCapacity c.groups < c.demands.length),1)))))

def capacityBudget (f : Formula) (c : Certificate) : Nat :=
  refsBudget f c.demands +
    (refsBudget f c.conflicts +
    (visitsBudget (groupBudget c.conflicts) c.groups +
    (visitsBudget (fun i => visitsBudget (differentBudget c.demands i)
      (indices c.demands.length)) (indices c.demands.length) +
    (coverageBudget c.demands c.groups + 1))))

theorem capacity_value (f : Formula) (c : Certificate) :
    (capacityMeter f c).1 = capacityCheck f c := by
  unfold capacityMeter capacityCheck both
  rw [refs_value,refs_value,coverage_value]
  have hg := all_value (groupMeter c.conflicts) (groupCheck c.conflicts)
    c.groups (group_value c.conflicts)
  have hd := all_value
    (fun i => allMeter (differentMeter c.demands i) (indices c.demands.length))
    (fun i => every (different c.demands i) (indices c.demands.length))
    (indices c.demands.length)
    (fun i => all_value _ _ _ (different_value c.demands i))
  rw [hg,hd]

theorem capacity_bound (f : Formula) (c : Certificate) :
    (capacityMeter f c).2 ≤ capacityBudget f c := by
  unfold capacityMeter capacityBudget both
  apply Nat.add_le_add (refs_bound f c.demands)
  apply Nat.add_le_add (refs_bound f c.conflicts)
  apply Nat.add_le_add (all_bound _ _ _ (group_bound c.conflicts))
  apply Nat.add_le_add
  · apply all_bound
    intro i
    exact all_bound _ _ _ (different_bound c.demands i)
  · exact Nat.add_le_add (coverage_bound c.demands c.groups) (Nat.le_refl 1)

end ProctorCapacityMeter

#print axioms ProctorCapacityMeter.all_value
#print axioms ProctorCapacityMeter.all_bound
#print axioms ProctorCapacityMeter.any_value
#print axioms ProctorCapacityMeter.any_bound
#print axioms ProctorCapacityMeter.distinct_value
#print axioms ProctorCapacityMeter.distinct_bound
#print axioms ProctorCapacityMeter.words_value
#print axioms ProctorCapacityMeter.words_bound
#print axioms ProctorCapacityMeter.conflict_value
#print axioms ProctorCapacityMeter.conflict_bound
#print axioms ProctorCapacityMeter.tuple_value
#print axioms ProctorCapacityMeter.tuple_bound
#print axioms ProctorCapacityMeter.group_value
#print axioms ProctorCapacityMeter.group_bound
#print axioms ProctorCapacityMeter.at_value
#print axioms ProctorCapacityMeter.at_bound
#print axioms ProctorCapacityMeter.demand_value
#print axioms ProctorCapacityMeter.demand_bound
#print axioms ProctorCapacityMeter.different_value
#print axioms ProctorCapacityMeter.different_bound
#print axioms ProctorCapacityMeter.coverage_value
#print axioms ProctorCapacityMeter.coverage_bound
#print axioms ProctorCapacityMeter.capacity_value
#print axioms ProctorCapacityMeter.capacity_bound
