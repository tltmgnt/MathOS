/-! F034 candidate: selected binary capacity terminal resource ledger.
Eager reservations, not a short-circuit trace. Demand row lookups are
explicitly hoisted once per compared pair. Structural arithmetic,
enumeration, encoding and other machine costs are not metered. -/
namespace ProctorCapacityResourceLedger
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group opposite totalCapacity)
open ProctorCapacityReplay (RefRow Certificate every someCheck words indices test)
open ProctorBinaryCapacity (distinctBinary conflictBinary groupBinary demandBinary natEq differentBinary coverageBinary capacityBinary refsBinary)
open ProctorBinaryReferences (containsMeter contains_bound literalMeter literal_bound literalBudget refMeter)
open ProctorBinaryLookup (checkedLookup checked_bound)
open ProctorCheckerBinaryTests (checkedEq checked_eq_bound)
open ProctorXorResourceLedger (Meter both allMeter anyMeter reserve all_value any_value all_bounds any_bounds reserve_zero refsMeter refs_bounds refGateBudget membershipMeter)
open ProctorBinaryXor (eqBudget)
open ProctorBinaryInputBinding (optFalse)

def gateOnly (a : Bool × Nat) : Meter := (a.1,0,a.2)

def distinctMeter (w : Nat) : Clause → Bool × Nat
  | [] => (true,0)
  | a::as =>
    let m := containsMeter w a as
    if m.1 then (false,m.2)
    else let r := distinctMeter w as; (r.1,m.2+r.2)

def distinctBudget (w : Nat) : Clause → Nat
  | [] => 0
  | _::as => literalBudget w*as.length+distinctBudget w as

theorem distinct_value (w : Nat) (xs : Clause) :
    (distinctMeter w xs).1=distinctBinary w xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    unfold distinctMeter distinctBinary
    dsimp only
    cases e : (containsMeter w a as).1 with
    | true => rfl
    | false => exact ih

theorem distinct_bound (w : Nat) (xs : Clause) :
    (distinctMeter w xs).2≤distinctBudget w xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    unfold distinctMeter distinctBudget
    dsimp only
    cases e : (containsMeter w a as).1 with
    | true => exact Nat.le_trans (contains_bound w a as) (Nat.le_add_right _ _)
    | false => exact Nat.add_le_add (contains_bound w a as) ih

def conflictLiteral (w : Nat) (l p : Literal) : Meter :=
  gateOnly (literalMeter w l (opposite p))

def conflictRow (w : Nat) (ys row : Clause) : Meter :=
  allMeter (fun l => anyMeter (conflictLiteral w l) ys) row

def conflictMeter (w : Nat) (rs : List RefRow) (ys : Clause) : Meter :=
  anyMeter (fun r => conflictRow w ys r.row) rs

def conflictRowBudget (w : Nat) (ys row : Clause) : Nat :=
  reserve (fun _ : Literal => reserve (fun _ : Literal => literalBudget w) ys) row

def conflictBudget (w : Nat) (rs : List RefRow) (ys : Clause) : Nat :=
  reserve (fun r : RefRow => conflictRowBudget w ys r.row) rs

theorem conflict_value (w : Nat) (rs : List RefRow) (ys : Clause) :
    (conflictMeter w rs ys).1=conflictBinary w rs ys := by
  unfold conflictMeter conflictBinary
  apply any_value
  intro r
  unfold conflictRow
  apply all_value
  intro l
  exact any_value _ _ ys (fun _ => rfl)

theorem conflict_row_bounds (w : Nat) (ys row : Clause) :
    (conflictRow w ys row).2.1≤0 ∧ (conflictRow w ys row).2.2≤conflictRowBudget w ys row := by
  have one := fun l : Literal => any_bounds (conflictLiteral w l) (fun _ => 0)
    (fun _ => literalBudget w) ys (fun _ => Nat.le_refl 0)
    (fun p => literal_bound w l (opposite p))
  have h := all_bounds (fun l => anyMeter (conflictLiteral w l) ys)
    (fun _ => 0) (fun _ => reserve (fun _ : Literal => literalBudget w) ys) row
    (fun l => by have a := (one l).left; rw [reserve_zero] at a; exact a)
    (fun l => (one l).right)
  rw [reserve_zero] at h
  exact h

theorem conflict_bounds (w : Nat) (rs : List RefRow) (ys : Clause) :
    (conflictMeter w rs ys).2.1≤0 ∧ (conflictMeter w rs ys).2.2≤conflictBudget w rs ys := by
  have h := any_bounds (fun r : RefRow => conflictRow w ys r.row)
    (fun _ => 0) (fun r => conflictRowBudget w ys r.row) rs
    (fun r => (conflict_row_bounds w ys r.row).left)
    (fun r => (conflict_row_bounds w ys r.row).right)
  rw [reserve_zero] at h
  exact h

def wordMeter (xs : Clause) : Nat → (Clause → Meter) → Meter
  | 0,p => p []
  | k+1,p => allMeter (fun l => wordMeter xs k (fun ys => p (l::ys))) xs

def wordBudget (xs : Clause) : Nat → (Clause → Nat) → Nat
  | 0,q => q []
  | k+1,q => reserve (fun l => wordBudget xs k (fun ys => q (l::ys))) xs

theorem word_value (xs : Clause) (k : Nat) (p : Clause → Meter) (q : Clause → Bool)
    (h : ∀ ys, (p ys).1=q ys) : (wordMeter xs k p).1=words xs k q := by
  induction k generalizing p q with
  | zero => exact h []
  | succ k ih =>
    exact all_value _ _ xs (fun l => ih _ _ (fun ys => h (l::ys)))

theorem word_bounds (xs : Clause) (k : Nat) (p : Clause → Meter) (q : Clause → Nat)
    (hv : ∀ ys, (p ys).2.1≤0) (hg : ∀ ys, (p ys).2.2≤q ys) :
    (wordMeter xs k p).2.1≤0 ∧ (wordMeter xs k p).2.2≤wordBudget xs k q := by
  induction k generalizing p q with
  | zero => exact ⟨hv [],hg []⟩
  | succ k ih =>
    have one := fun l : Literal => ih (fun ys => p (l::ys)) (fun ys => q (l::ys))
      (fun ys => hv (l::ys)) (fun ys => hg (l::ys))
    have h := all_bounds (fun l => wordMeter xs k (fun ys => p (l::ys)))
      (fun _ => 0) (fun l => wordBudget xs k (fun ys => q (l::ys))) xs
      (fun l => (one l).left) (fun l => (one l).right)
    rw [reserve_zero] at h
    exact h

def witnessMeter (w : Nat) (rs : List RefRow) (ys : Clause) : Meter :=
  let d := distinctMeter w ys
  if d.1 then
    let c := conflictMeter w rs ys
    (c.1,c.2.1,d.2+c.2.2)
  else (true,0,d.2)

def witnessBudget (w : Nat) (rs : List RefRow) (ys : Clause) : Nat :=
  distinctBudget w ys+conflictBudget w rs ys

theorem witness_value (w : Nat) (rs : List RefRow) (ys : Clause) :
    (witnessMeter w rs ys).1=(if distinctBinary w ys then conflictBinary w rs ys else true) := by
  unfold witnessMeter
  dsimp only
  rw [← distinct_value w ys,← conflict_value w rs ys]
  cases (distinctMeter w ys).1 <;> rfl

theorem witness_bounds (w : Nat) (rs : List RefRow) (ys : Clause) :
    (witnessMeter w rs ys).2.1≤0 ∧ (witnessMeter w rs ys).2.2≤witnessBudget w rs ys := by
  unfold witnessMeter witnessBudget
  dsimp only
  cases (distinctMeter w ys).1 with
  | false => exact ⟨Nat.le_refl 0,Nat.le_trans (distinct_bound w ys) (Nat.le_add_right _ _)⟩
  | true =>
    have h := conflict_bounds w rs ys
    exact ⟨h.left,Nat.add_le_add (distinct_bound w ys) h.right⟩

def groupMeter (w : Nat) (rs : List RefRow) (g : Group) : Meter :=
  if g.cap≤2 then both (gateOnly (distinctMeter w g.literals))
    (wordMeter g.literals (g.cap+1) (witnessMeter w rs))
  else (false,0,0)

def groupBudget (w : Nat) (rs : List RefRow) (g : Group) : Nat :=
  if g.cap≤2 then distinctBudget w g.literals+
    wordBudget g.literals (g.cap+1) (witnessBudget w rs) else 0

theorem group_value (w : Nat) (rs : List RefRow) (g : Group) :
    (groupMeter w rs g).1=groupBinary w rs g := by
  unfold groupMeter groupBinary test
  by_cases h : g.cap≤2
  · rw [if_pos h,if_pos h]
    change ((distinctMeter w g.literals).1 && (wordMeter g.literals (g.cap+1)
      (witnessMeter w rs)).1)=_
    rw [distinct_value,word_value _ _ _ _ (witness_value w rs)] <;> rfl
  · rw [if_neg h,if_neg h] <;> rfl

theorem group_bounds (w : Nat) (rs : List RefRow) (g : Group) :
    (groupMeter w rs g).2.1≤0 ∧ (groupMeter w rs g).2.2≤groupBudget w rs g := by
  unfold groupMeter groupBudget
  by_cases h : g.cap≤2
  · rw [if_pos h,if_pos h]
    have p := word_bounds g.literals (g.cap+1) (witnessMeter w rs) (witnessBudget w rs)
      (fun ys => (witness_bounds w rs ys).left) (fun ys => (witness_bounds w rs ys).right)
    exact ⟨Nat.add_le_add (Nat.le_refl 0) p.left,Nat.add_le_add (distinct_bound w g.literals) p.right⟩
  · rw [if_neg h,if_neg h]
    exact ⟨Nat.le_refl 0,Nat.le_refl 0⟩

def unequalMeter (w : Nat) (a b : Literal) : Meter :=
  let m := checkedEq w a.1 b.1
  (!optFalse m.1,0,m.2)

def disjointMeter (w : Nat) (a b : Clause) : Meter :=
  allMeter (fun l => allMeter (unequalMeter w l) b) a

def disjointBudget (w : Nat) (a b : Clause) : Nat :=
  reserve (fun _ : Literal => reserve (fun _ : Literal => eqBudget w) b) a

theorem disjoint_value (w : Nat) (a b : Clause) :
    (disjointMeter w a b).1=every (fun l => every (fun m => !natEq w l.1 m.1) b) a := by
  unfold disjointMeter
  apply all_value
  intro l
  exact all_value _ _ b (fun _ => rfl)

theorem disjoint_bounds (w : Nat) (a b : Clause) :
    (disjointMeter w a b).2.1≤0 ∧ (disjointMeter w a b).2.2≤disjointBudget w a b := by
  have one := fun l : Literal => all_bounds (unequalMeter w l) (fun _ => 0)
    (fun _ => eqBudget w) b (fun _ => Nat.le_refl 0)
    (fun m => checked_eq_bound w l.1 m.1)
  have h := all_bounds (fun l => allMeter (unequalMeter w l) b)
    (fun _ => 0) (fun _ => reserve (fun _ : Literal => eqBudget w) b) a
    (fun l => by have t := (one l).left; rw [reserve_zero] at t; exact t)
    (fun l => (one l).right)
  rw [reserve_zero] at h
  exact h

-- Hoist the two checked demand lookups once per unequal index pair.
-- demandBinary projects their rows; no extra lookup is charged for the
-- row projection. This is a costed alternative, not a trace of old code.
def differentMeter (w : Nat) (ds : List RefRow) (i j : Nat) : Meter :=
  let e := checkedEq w i j
  if optFalse e.1 then (true,0,e.2)
  else
    let a := checkedLookup w ds i
    let b := checkedLookup w ds j
    let row := fun x : Option RefRow => match x with | none => [] | some r => r.row
    let d := disjointMeter w (row a.1) (row b.1)
    (d.1,a.2+b.2+d.2.1,e.2+d.2.2)

def pairVisitBudget (w : Nat) (ds : List RefRow) : Nat :=
  (w+1)*ds.length+(w+1)*ds.length

def pairGateBudget (w : Nat) (ds : List RefRow) (i j : Nat) : Nat :=
  eqBudget w+disjointBudget w (demandBinary w ds i) (demandBinary w ds j)

theorem different_value (w : Nat) (ds : List RefRow) (i j : Nat) :
    (differentMeter w ds i j).1=differentBinary w ds i j := by
  unfold differentMeter differentBinary natEq
  dsimp only
  cases optFalse (checkedEq w i j).1 with
  | true => rfl
  | false =>
    change (disjointMeter w (demandBinary w ds i) (demandBinary w ds j)).1=_
    exact disjoint_value w (demandBinary w ds i) (demandBinary w ds j)

theorem different_bounds (w : Nat) (ds : List RefRow) (i j : Nat) :
    (differentMeter w ds i j).2.1≤pairVisitBudget w ds ∧
    (differentMeter w ds i j).2.2≤pairGateBudget w ds i j := by
  unfold differentMeter pairVisitBudget pairGateBudget
  dsimp only
  cases optFalse (checkedEq w i j).1 with
  | true => exact ⟨Nat.zero_le _,Nat.le_trans (checked_eq_bound w i j) (Nat.le_add_right _ _)⟩
  | false =>
    have h := disjoint_bounds w (demandBinary w ds i) (demandBinary w ds j)
    change (checkedLookup w ds i).2+(checkedLookup w ds j).2+
      (disjointMeter w (demandBinary w ds i) (demandBinary w ds j)).2.1≤
      (w+1)*ds.length+(w+1)*ds.length ∧
      (checkedEq w i j).2+(disjointMeter w (demandBinary w ds i) (demandBinary w ds j)).2.2≤
        eqBudget w+disjointBudget w (demandBinary w ds i) (demandBinary w ds j)
    have hz := Nat.le_antisymm h.left (Nat.zero_le _)
    rw [hz]
    exact ⟨Nat.add_le_add (checked_bound w ds i) (checked_bound w ds j),
      Nat.add_le_add (checked_eq_bound w i j) h.right⟩

def pairsMeter (w : Nat) (ds : List RefRow) : Meter :=
  allMeter (fun i => allMeter (differentMeter w ds i) (indices ds.length)) (indices ds.length)
def pairsVisitBudget (w : Nat) (ds : List RefRow) : Nat :=
  reserve (fun _ : Nat => reserve (fun _ : Nat => pairVisitBudget w ds) (indices ds.length)) (indices ds.length)
def pairsGateBudget (w : Nat) (ds : List RefRow) : Nat :=
  reserve (fun i => reserve (pairGateBudget w ds i) (indices ds.length)) (indices ds.length)

theorem pairs_value (w : Nat) (ds : List RefRow) :
    (pairsMeter w ds).1=every (fun i => every (differentBinary w ds i) (indices ds.length))
      (indices ds.length) := by
  unfold pairsMeter
  apply all_value
  intro i
  exact all_value _ _ _ (different_value w ds i)

theorem pairs_bounds (w : Nat) (ds : List RefRow) :
    (pairsMeter w ds).2.1≤pairsVisitBudget w ds ∧
    (pairsMeter w ds).2.2≤pairsGateBudget w ds := by
  have one := fun i : Nat => all_bounds (differentMeter w ds i) (fun _ => pairVisitBudget w ds)
    (pairGateBudget w ds i) (indices ds.length)
    (fun j => (different_bounds w ds i j).left) (fun j => (different_bounds w ds i j).right)
  exact all_bounds _ _ _ _ (fun i => (one i).left) (fun i => (one i).right)

def coverLiteral (w : Nat) (gs : List Group) (l : Literal) : Meter :=
  anyMeter (fun g : Group => membershipMeter w g.literals l) gs
def coverRow (w : Nat) (gs : List Group) (row : Clause) : Meter :=
  allMeter (coverLiteral w gs) row
def coverageMeter (w : Nat) (ds : List RefRow) (gs : List Group) : Meter :=
  allMeter (fun r => coverRow w gs r.row) ds
def coverRowBudget (w : Nat) (gs : List Group) (row : Clause) : Nat :=
  reserve (fun _ : Literal => reserve (fun g : Group => literalBudget w*g.literals.length) gs) row
def coverageBudget (w : Nat) (ds : List RefRow) (gs : List Group) : Nat :=
  reserve (fun r : RefRow => coverRowBudget w gs r.row) ds

theorem coverage_value (w : Nat) (ds : List RefRow) (gs : List Group) :
    (coverageMeter w ds gs).1=coverageBinary w ds gs := by
  unfold coverageMeter coverageBinary
  apply all_value
  intro r
  unfold coverRow
  apply all_value
  intro l
  exact any_value _ _ gs (fun _ => rfl)

theorem cover_row_bounds (w : Nat) (gs : List Group) (row : Clause) :
    (coverRow w gs row).2.1≤0 ∧ (coverRow w gs row).2.2≤coverRowBudget w gs row := by
  have one := fun l : Literal => any_bounds (fun g : Group => membershipMeter w g.literals l)
    (fun _ => 0) (fun g => literalBudget w*g.literals.length) gs
    (fun _ => Nat.le_refl 0) (fun g => contains_bound w l g.literals)
  have h := all_bounds (coverLiteral w gs) (fun _ => 0)
    (fun _ => reserve (fun g : Group => literalBudget w*g.literals.length) gs) row
    (fun l => by have t := (one l).left; rw [reserve_zero] at t; exact t)
    (fun l => (one l).right)
  rw [reserve_zero] at h
  exact h

theorem coverage_bounds (w : Nat) (ds : List RefRow) (gs : List Group) :
    (coverageMeter w ds gs).2.1≤0 ∧ (coverageMeter w ds gs).2.2≤coverageBudget w ds gs := by
  have h := all_bounds (fun r : RefRow => coverRow w gs r.row) (fun _ => 0)
    (fun r => coverRowBudget w gs r.row) ds
    (fun r => (cover_row_bounds w gs r.row).left) (fun r => (cover_row_bounds w gs r.row).right)
  rw [reserve_zero] at h
  exact h

def capacityMeter (w : Nat) (f : Formula) (c : Certificate) : Meter :=
  both (refsMeter w f c.demands) (both (refsMeter w f c.conflicts)
    (both (allMeter (groupMeter w c.conflicts) c.groups)
      (both (pairsMeter w c.demands) (both (coverageMeter w c.demands c.groups)
        (test (totalCapacity c.groups<c.demands.length),0,0)))))

def visitBudget (w : Nat) (f : Formula) (c : Certificate) : Nat :=
  reserve (fun _ : RefRow => (w+1)*f.length) c.demands+
    (reserve (fun _ : RefRow => (w+1)*f.length) c.conflicts+
      (0+(pairsVisitBudget w c.demands+(0+0))))

def gateBudget (w : Nat) (f : Formula) (c : Certificate) : Nat :=
  reserve (refGateBudget w f) c.demands+
    (reserve (refGateBudget w f) c.conflicts+
      (reserve (groupBudget w c.conflicts) c.groups+
        (pairsGateBudget w c.demands+(coverageBudget w c.demands c.groups+0))))

theorem refs_value (w : Nat) (f : Formula) (rs : List RefRow) :
    (refsMeter w f rs).1=refsBinary w f rs :=
  all_value _ _ rs (fun _ => rfl)

theorem capacity_value (w : Nat) (f : Formula) (c : Certificate) :
    (capacityMeter w f c).1=capacityBinary w f c := by
  unfold capacityMeter both capacityBinary
  rw [refs_value,refs_value,all_value _ _ _ (group_value w c.conflicts),
    pairs_value,coverage_value]

theorem capacity_bounds (w : Nat) (f : Formula) (c : Certificate) :
    (capacityMeter w f c).2.1≤visitBudget w f c ∧
    (capacityMeter w f c).2.2≤gateBudget w f c := by
  have a := refs_bounds w f c.demands
  have b := refs_bounds w f c.conflicts
  have g := all_bounds (groupMeter w c.conflicts) (fun _ => 0)
    (groupBudget w c.conflicts) c.groups
    (fun x => (group_bounds w c.conflicts x).left) (fun x => (group_bounds w c.conflicts x).right)
  rw [reserve_zero] at g
  have p := pairs_bounds w c.demands
  have v := coverage_bounds w c.demands c.groups
  exact ⟨Nat.add_le_add a.left (Nat.add_le_add b.left (Nat.add_le_add g.left
      (Nat.add_le_add p.left (Nat.add_le_add v.left (Nat.le_refl 0))))),
    Nat.add_le_add a.right (Nat.add_le_add b.right (Nat.add_le_add g.right
      (Nat.add_le_add p.right (Nat.add_le_add v.right (Nat.le_refl 0)))))⟩

end ProctorCapacityResourceLedger

#print axioms ProctorCapacityResourceLedger.distinct_value
#print axioms ProctorCapacityResourceLedger.distinct_bound
#print axioms ProctorCapacityResourceLedger.conflict_value
#print axioms ProctorCapacityResourceLedger.conflict_row_bounds
#print axioms ProctorCapacityResourceLedger.conflict_bounds
#print axioms ProctorCapacityResourceLedger.word_value
#print axioms ProctorCapacityResourceLedger.word_bounds
#print axioms ProctorCapacityResourceLedger.witness_value
#print axioms ProctorCapacityResourceLedger.witness_bounds
#print axioms ProctorCapacityResourceLedger.group_value
#print axioms ProctorCapacityResourceLedger.group_bounds
#print axioms ProctorCapacityResourceLedger.disjoint_value
#print axioms ProctorCapacityResourceLedger.disjoint_bounds
#print axioms ProctorCapacityResourceLedger.different_value
#print axioms ProctorCapacityResourceLedger.different_bounds
#print axioms ProctorCapacityResourceLedger.pairs_value
#print axioms ProctorCapacityResourceLedger.pairs_bounds
#print axioms ProctorCapacityResourceLedger.coverage_value
#print axioms ProctorCapacityResourceLedger.cover_row_bounds
#print axioms ProctorCapacityResourceLedger.coverage_bounds
#print axioms ProctorCapacityResourceLedger.refs_value
#print axioms ProctorCapacityResourceLedger.capacity_value
#print axioms ProctorCapacityResourceLedger.capacity_bounds
