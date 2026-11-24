/-! F034: unified typed meter, including binding and label checks.
Selected charges only; eager traversal need not match runtime trace. -/
namespace ProctorUnifiedMeter
open ProctorHallDeficiency
open ProctorExecutableReplay (Step hasEmpty chainCheck)
open ProctorCapacityReplay (RefRow test every)
open ProctorChainMeter (both rowEqMeter row_eq_value row_eq_bound chainMeter chainBudget chain_value chain_bound)
open ProctorCapacityMeter (Meter allMeter all_value all_bound visitsBudget capacityMeter capacityBudget capacity_value capacity_bound)
open ProctorXorMeter (xorMeter xorBudget xor_value xor_bound)
open ProctorUnifiedReplay (Terminal Proof Envelope validId validClause validFormula validRefs validTerminal validProof terminalCheck target check boundCheck)

def emptyMeter : Formula → Meter
  | [] => (false,0)
  | []::_ => (true,1)
  | (_::_)::cs =>
    let r := emptyMeter cs
    (r.1,r.2+1)

theorem empty_value (f : Formula) : (emptyMeter f).1 = hasEmpty f := by
  induction f with
  | nil => rfl
  | cons c cs ih =>
    cases c with
    | nil => rfl
    | cons l ls => exact ih

theorem empty_bound (f : Formula) : (emptyMeter f).2 ≤ f.length := by
  induction f with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    cases c with
    | nil => exact Nat.succ_le_succ (Nat.zero_le cs.length)
    | cons l ls => exact Nat.succ_le_succ ih

-- One row-list comparison per visited pair or end marker,
-- plus the previously verified row equality meter.
def formulaMeter : Formula → Formula → Meter
  | [],[] => (true,1)
  | [],_::_ => (false,1)
  | _::_,[] => (false,1)
  | c::cs,d::ds =>
    let a := rowEqMeter c d
    let b := formulaMeter cs ds
    (a.1 && b.1,a.2+b.2+1)

def formulaBudget : Formula → Nat
  | [] => 1
  | c::cs => (c.length+1)+formulaBudget cs+1

theorem formula_value (f g : Formula) : (formulaMeter f g).1 = test (f=g) := by
  induction f generalizing g with
  | nil => cases g <;> rfl
  | cons c cs ih =>
    cases g with
    | nil => rfl
    | cons d ds =>
      change ((rowEqMeter c d).1 && (formulaMeter cs ds).1) =
        test (c::cs=d::ds)
      rw [row_eq_value,ih ds]
      unfold test
      by_cases a : c=d
      · cases a
        by_cases b : cs=ds
        · rw [if_pos rfl,if_pos b,if_pos (congrArg (List.cons c) b)] <;> rfl
        · have ne : c::cs ≠ c::ds := fun h => b (List.cons.inj h).2
          rw [if_pos rfl,if_neg b,if_neg ne] <;> rfl
      · have ne : c::cs ≠ d::ds := fun h => a (List.cons.inj h).1
        rw [if_neg a,if_neg ne] <;> rfl

theorem formula_bound (f g : Formula) : (formulaMeter f g).2 ≤ formulaBudget f := by
  induction f generalizing g with
  | nil => cases g <;> exact Nat.le_refl 1
  | cons c cs ih =>
    cases g with
    | nil => exact Nat.succ_le_succ (Nat.zero_le _)
    | cons d ds =>
      exact Nat.add_le_add (Nat.add_le_add (row_eq_bound c d) (ih ds)) (Nat.le_refl 1)

def idMeter (n v : Nat) : Meter := (validId n v,2)

theorem id_value (n v : Nat) : (idMeter n v).1 = validId n v := rfl

def clauseMeter (n : Nat) (c : Clause) : Meter :=
  allMeter (fun l => idMeter n l.1) c

def clauseBudget (c : Clause) : Nat := visitsBudget (fun _ => 2) c

theorem clause_value (n : Nat) (c : Clause) :
    (clauseMeter n c).1 = validClause n c :=
  all_value _ _ _ (fun l => id_value n l.1)

theorem clause_bound (n : Nat) (c : Clause) :
    (clauseMeter n c).2 ≤ clauseBudget c :=
  all_bound _ _ _ (fun _ => Nat.le_refl 2)

def formulaRangeMeter (n : Nat) (f : Formula) : Meter :=
  allMeter (clauseMeter n) f

def formulaRangeBudget (f : Formula) : Nat := visitsBudget clauseBudget f

theorem range_formula_value (n : Nat) (f : Formula) :
    (formulaRangeMeter n f).1 = validFormula n f :=
  all_value _ _ _ (clause_value n)

theorem range_formula_bound (n : Nat) (f : Formula) :
    (formulaRangeMeter n f).2 ≤ formulaRangeBudget f :=
  all_bound _ _ _ (clause_bound n)

def refsRangeMeter (n : Nat) (rs : List RefRow) : Meter :=
  allMeter (fun r => clauseMeter n r.row) rs

def refsRangeBudget (rs : List RefRow) : Nat :=
  visitsBudget (fun r => clauseBudget r.row) rs

theorem refs_range_value (n : Nat) (rs : List RefRow) :
    (refsRangeMeter n rs).1 = validRefs n rs :=
  all_value _ _ _ (fun r => clause_value n r.row)

theorem refs_range_bound (n : Nat) (rs : List RefRow) :
    (refsRangeMeter n rs).2 ≤ refsRangeBudget rs :=
  all_bound _ _ _ (fun r => clause_bound n r.row)

def terminalRangeMeter (n : Nat) : Terminal → Meter
  | .empty => (true,0)
  | .capacity c =>
    both (refsRangeMeter n c.demands)
      (both (refsRangeMeter n c.conflicts)
        (allMeter (fun g => clauseMeter n g.literals) c.groups))
  | .xor bs =>
    allMeter (fun b => both (allMeter (idMeter n) b.support)
      (refsRangeMeter n b.refs)) bs

def terminalRangeBudget : Terminal → Nat
  | .empty => 0
  | .capacity c => refsRangeBudget c.demands +
      (refsRangeBudget c.conflicts + visitsBudget (fun g => clauseBudget g.literals) c.groups)
  | .xor bs => visitsBudget (fun b => visitsBudget (fun _ => 2) b.support +
      refsRangeBudget b.refs) bs

theorem terminal_range_value (n : Nat) (t : Terminal) :
    (terminalRangeMeter n t).1 = validTerminal n t := by
  cases t with
  | empty => rfl
  | capacity c =>
    change ((refsRangeMeter n c.demands).1 &&
      ((refsRangeMeter n c.conflicts).1 &&
        (allMeter (fun g => clauseMeter n g.literals) c.groups).1)) =
      (validRefs n c.demands && (validRefs n c.conflicts &&
        every (fun g => validClause n g.literals) c.groups))
    have h : (allMeter (fun g => clauseMeter n g.literals) c.groups).1 =
        every (fun g => validClause n g.literals) c.groups := by
      apply all_value
      intro g
      exact clause_value n g.literals
    rw [refs_range_value,refs_range_value,h]
  | xor bs =>
    change (allMeter (fun b => both (allMeter (idMeter n) b.support)
      (refsRangeMeter n b.refs)) bs).1 =
      every (fun b => every (validId n) b.support && validRefs n b.refs) bs
    apply all_value
    intro b
    change ((allMeter (idMeter n) b.support).1 && (refsRangeMeter n b.refs).1) =
      (every (validId n) b.support && validRefs n b.refs)
    rw [all_value _ _ _ (id_value n),refs_range_value]

theorem terminal_range_bound (n : Nat) (t : Terminal) :
    (terminalRangeMeter n t).2 ≤ terminalRangeBudget t := by
  cases t with
  | empty => exact Nat.le_refl 0
  | capacity c =>
    exact Nat.add_le_add (refs_range_bound n c.demands)
      (Nat.add_le_add (refs_range_bound n c.conflicts)
        (all_bound _ _ _ (fun g => clause_bound n g.literals)))
  | xor bs =>
    change (allMeter (fun b => both (allMeter (idMeter n) b.support)
      (refsRangeMeter n b.refs)) bs).2 ≤
      visitsBudget (fun b => visitsBudget (fun _ => 2) b.support +
        refsRangeBudget b.refs) bs
    apply all_bound
    intro b
    exact Nat.add_le_add (all_bound _ _ _ (fun _ => Nat.le_refl 2))
      (refs_range_bound n b.refs)

def proofRangeMeter (n : Nat) (p : Proof) : Meter :=
  both (allMeter (fun batch => allMeter (fun s : Step =>
    both (idMeter n s.pivot) (clauseMeter n s.tail)) batch) p.batches)
    (terminalRangeMeter n p.terminal)

def proofRangeBudget (p : Proof) : Nat :=
  visitsBudget (fun batch => visitsBudget (fun s : Step => 2+clauseBudget s.tail) batch)
    p.batches + terminalRangeBudget p.terminal

theorem proof_range_value (n : Nat) (p : Proof) :
    (proofRangeMeter n p).1 = validProof n p := by
  change ((allMeter (fun batch => allMeter (fun s : Step =>
    both (idMeter n s.pivot) (clauseMeter n s.tail)) batch) p.batches).1 &&
    (terminalRangeMeter n p.terminal).1) =
    (every (fun batch => every (fun s : Step => validId n s.pivot &&
      validClause n s.tail) batch) p.batches && validTerminal n p.terminal)
  have h := all_value
    (fun batch => allMeter (fun s : Step =>
      both (idMeter n s.pivot) (clauseMeter n s.tail)) batch)
    (fun batch => every (fun s : Step => validId n s.pivot && validClause n s.tail) batch)
    p.batches (fun batch => all_value _ _ batch (fun s => by
      change (validId n s.pivot && (clauseMeter n s.tail).1) =
        (validId n s.pivot && validClause n s.tail)
      rw [clause_value]))
  rw [h,terminal_range_value]

theorem proof_range_bound (n : Nat) (p : Proof) :
    (proofRangeMeter n p).2 ≤ proofRangeBudget p := by
  unfold proofRangeMeter proofRangeBudget both
  apply Nat.add_le_add
  · apply all_bound
    intro batch
    apply all_bound
    intro s
    exact Nat.add_le_add (Nat.le_refl 2) (clause_bound n s.tail)
  · exact terminal_range_bound n p.terminal

def terminalMeter (f : Formula) : Terminal → Meter
  | .empty => emptyMeter f
  | .capacity c => capacityMeter f c
  | .xor bs => xorMeter f bs

def terminalBudget (f : Formula) : Terminal → Nat
  | .empty => f.length
  | .capacity c => capacityBudget f c
  | .xor bs => xorBudget f bs

theorem terminal_value (f : Formula) (t : Terminal) :
    (terminalMeter f t).1 = terminalCheck f t := by
  cases t with
  | empty => exact empty_value f
  | capacity c => exact capacity_value f c
  | xor bs => exact xor_value f bs

theorem terminal_bound (f : Formula) (t : Terminal) :
    (terminalMeter f t).2 ≤ terminalBudget f t := by
  cases t with
  | empty => exact empty_bound f
  | capacity c => exact capacity_bound f c
  | xor bs => exact xor_bound f bs

def checkMeter (f : Formula) (p : Proof) : Meter :=
  both (chainMeter f p.batches) (terminalMeter (target f p) p.terminal)

def checkBudget (f : Formula) (p : Proof) : Nat :=
  chainBudget f p.batches + terminalBudget (target f p) p.terminal

theorem check_value (f : Formula) (p : Proof) :
    (checkMeter f p).1 = check f p := by
  unfold checkMeter check both
  rw [chain_value,terminal_value]

theorem check_bound (f : Formula) (p : Proof) :
    (checkMeter f p).2 ≤ checkBudget f p :=
  Nat.add_le_add (chain_bound f p.batches) (terminal_bound (target f p) p.terminal)

def boundMeter (n : Nat) (f : Formula) (e : Envelope) : Meter :=
  both (test (n=e.variableBound),1)
    (both (formulaMeter f e.original)
      (both (formulaRangeMeter n f)
        (both (proofRangeMeter n e.proof) (checkMeter f e.proof))))

def boundBudget (f : Formula) (e : Envelope) : Nat :=
  1 + (formulaBudget f +
    (formulaRangeBudget f + (proofRangeBudget e.proof + checkBudget f e.proof)))

theorem bound_value (n : Nat) (f : Formula) (e : Envelope) :
    (boundMeter n f e).1 = boundCheck n f e := by
  unfold boundMeter boundCheck both
  rw [formula_value,range_formula_value,proof_range_value,check_value]

theorem bound_cost (n : Nat) (f : Formula) (e : Envelope) :
    (boundMeter n f e).2 ≤ boundBudget f e :=
  Nat.add_le_add (Nat.le_refl 1)
    (Nat.add_le_add (formula_bound f e.original)
      (Nat.add_le_add (range_formula_bound n f)
        (Nat.add_le_add (proof_range_bound n e.proof) (check_bound f e.proof))))

theorem bound_sound (n : Nat) (f : Formula) (e : Envelope)
    (h : (boundMeter n f e).1 = true) : ¬ ∃ x : Assignment, FormulaSat f x :=
  by
    rw [bound_value] at h
    exact ProctorUnifiedReplay.bound_sound n f e h

end ProctorUnifiedMeter

#print axioms ProctorUnifiedMeter.empty_value
#print axioms ProctorUnifiedMeter.empty_bound
#print axioms ProctorUnifiedMeter.formula_value
#print axioms ProctorUnifiedMeter.formula_bound
#print axioms ProctorUnifiedMeter.id_value
#print axioms ProctorUnifiedMeter.clause_value
#print axioms ProctorUnifiedMeter.clause_bound
#print axioms ProctorUnifiedMeter.range_formula_value
#print axioms ProctorUnifiedMeter.range_formula_bound
#print axioms ProctorUnifiedMeter.refs_range_value
#print axioms ProctorUnifiedMeter.refs_range_bound
#print axioms ProctorUnifiedMeter.terminal_range_value
#print axioms ProctorUnifiedMeter.terminal_range_bound
#print axioms ProctorUnifiedMeter.proof_range_value
#print axioms ProctorUnifiedMeter.proof_range_bound
#print axioms ProctorUnifiedMeter.terminal_value
#print axioms ProctorUnifiedMeter.terminal_bound
#print axioms ProctorUnifiedMeter.check_value
#print axioms ProctorUnifiedMeter.check_bound
#print axioms ProctorUnifiedMeter.bound_value
#print axioms ProctorUnifiedMeter.bound_cost
#print axioms ProctorUnifiedMeter.bound_sound
