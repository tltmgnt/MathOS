import Init

namespace PnpInferenceComplexity

inductive Tree where
  | leaf : Tree
  | node : Tree → Tree → Tree

def leaves : Tree → Nat
  | .leaf => 1
  | .node l r => leaves l + leaves r

def capacity : Nat → Nat
  | 0 => 1
  | d + 1 => capacity d + capacity d

inductive Fits : Nat → Tree → Prop where
  | leaf (d : Nat) : Fits d .leaf
  | node {d : Nat} {l r : Tree} :
      Fits d l → Fits d r → Fits (d+1) (.node l r)

theorem capacityPositive (d : Nat) : 1 ≤ capacity d := by
  induction d with
  | zero => exact Nat.le_refl 1
  | succ d ih =>
    exact Nat.le_trans ih (Nat.le_add_right (capacity d) (capacity d))

theorem leafBound {d : Nat} {t : Tree} (h : Fits d t) :
    leaves t ≤ capacity d := by
  induction h with
  | leaf d => exact capacityPositive d
  | node hl hr il ir => exact Nat.add_le_add il ir

theorem supportNecessary {I A : Type} (premise : I → A → Prop)
    (used : I → Prop) (j : I) (a : A)
    (witness : ∀ i, i ≠ j → premise i a)
    (contradiction : ∀ b, (∀ i, used i → premise i b) → False) :
    ¬ (¬ used j) := by
  intro missing
  apply contradiction a
  intro i hi
  apply witness i
  intro eq
  exact missing (eq ▸ hi)

#print axioms PnpInferenceComplexity.capacityPositive
#print axioms PnpInferenceComplexity.leafBound
#print axioms PnpInferenceComplexity.supportNecessary

end PnpInferenceComplexity
