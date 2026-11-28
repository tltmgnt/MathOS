import Init

/-! Soundness of abstract three-valued AND/OR trees with certified leaves.
This is not a formalization of the Python separator finder or its complexity. -/
namespace PnpRecursive

inductive Outcome where
  | sat
  | unsat
  | unknown

def allows : Outcome → Bool → Bool
  | .sat, b => b
  | .unsat, b => !b
  | .unknown, _ => true

def both : Outcome → Outcome → Outcome
  | .unsat, _ => .unsat
  | _, .unsat => .unsat
  | .sat, .sat => .sat
  | _, _ => .unknown

def either : Outcome → Outcome → Outcome
  | .sat, _ => .sat
  | _, .sat => .sat
  | .unsat, .unsat => .unsat
  | _, _ => .unknown

theorem bothSound (p q : Outcome) (a b : Bool)
    (hp : allows p a = true) (hq : allows q b = true) :
    allows (both p q) (a && b) = true := by
  cases p <;> cases q <;> cases a <;> cases b <;>
    first | rfl | exact hp | exact hq

theorem eitherSound (p q : Outcome) (a b : Bool)
    (hp : allows p a = true) (hq : allows q b = true) :
    allows (either p q) (a || b) = true := by
  cases p <;> cases q <;> cases a <;> cases b <;>
    first | rfl | exact hp | exact hq

inductive Tree where
  | leaf : Outcome → Bool → Tree
  | andNode : Tree → Tree → Tree
  | orNode : Tree → Tree → Tree

def reported : Tree → Outcome
  | .leaf p _ => p
  | .andNode l r => both (reported l) (reported r)
  | .orNode l r => either (reported l) (reported r)

def actual : Tree → Bool
  | .leaf _ b => b
  | .andNode l r => actual l && actual r
  | .orNode l r => actual l || actual r

def validLeaves : Tree → Prop
  | .leaf p b => allows p b = true
  | .andNode l r => validLeaves l ∧ validLeaves r
  | .orNode l r => validLeaves l ∧ validLeaves r

theorem treeSound (t : Tree) : validLeaves t → allows (reported t) (actual t) = true := by
  induction t with
  | leaf p b => intro h; exact h
  | andNode l r hl hr =>
    intro h
    exact bothSound (reported l) (reported r) (actual l) (actual r) (hl h.1) (hr h.2)
  | orNode l r hl hr =>
    intro h
    exact eitherSound (reported l) (reported r) (actual l) (actual r) (hl h.1) (hr h.2)

theorem knownSat (t : Tree) (h : validLeaves t) (hs : reported t = .sat) :
    actual t = true := by
  have q := treeSound t h
  rw [hs] at q
  exact q

theorem negTrueFalse (b : Bool) (h : (!b) = true) : b = false := by
  cases b
  · rfl
  · nomatch h

theorem knownUnsat (t : Tree) (h : validLeaves t) (hs : reported t = .unsat) :
    actual t = false := by
  have q := treeSound t h
  rw [hs] at q
  change (!actual t) = true at q
  exact negTrueFalse (actual t) q

#print axioms PnpRecursive.bothSound
#print axioms PnpRecursive.eitherSound
#print axioms PnpRecursive.treeSound
#print axioms PnpRecursive.knownSat
#print axioms PnpRecursive.knownUnsat

end PnpRecursive
