import Init

/-! Abstract soundness of complete case analysis and disjoint composition.
This does not formalize the Python partitioner, backdoor finder or bounds. -/
namespace PnpComposition

theorem independentProduct {A B : Type} (p : A → Prop) (q : B → Prop) :
    (∃ a : A, ∃ b : B, p a ∧ q b) ↔
      (∃ a : A, p a) ∧ (∃ b : B, q b) := by
  constructor
  · intro h
    rcases h with ⟨a, b, hp, hq⟩
    exact ⟨⟨a, hp⟩, ⟨b, hq⟩⟩
  · intro h
    rcases h with ⟨⟨a, hp⟩, ⟨b, hq⟩⟩
    exact ⟨a, b, hp, hq⟩

inductive DecisionTree where
  | leaf : Bool → DecisionTree
  | split : DecisionTree → DecisionTree → DecisionTree

def result : DecisionTree → Bool
  | .leaf b => b
  | .split l r => result l || result r

def accepts : DecisionTree → Prop
  | .leaf b => b = true
  | .split l r => accepts l ∨ accepts r

theorem orTrue (a b : Bool) : (a || b) = true ↔ a = true ∨ b = true := by
  constructor
  · intro h
    cases a
    · exact Or.inr h
    · exact Or.inl rfl
  · intro h
    cases h with
    | inl ha => rw [ha]
    | inr hb => rw [hb] <;> cases a <;> rfl

theorem treeSound (t : DecisionTree) : result t = true ↔ accepts t := by
  induction t with
  | leaf b => exact Iff.rfl
  | split l r hl hr =>
    change (result l || result r) = true ↔ accepts l ∨ accepts r
    constructor
    · intro h
      cases (orTrue (result l) (result r)).mp h with
      | inl h => exact Or.inl (hl.mp h)
      | inr h => exact Or.inr (hr.mp h)
    · intro h
      apply (orTrue (result l) (result r)).mpr
      cases h with
      | inl h => exact Or.inl (hl.mpr h)
      | inr h => exact Or.inr (hr.mpr h)

def allResults : List DecisionTree → Bool
  | [] => true
  | t :: ts => result t && allResults ts

def allAccept : List DecisionTree → Prop
  | [] => True
  | t :: ts => accepts t ∧ allAccept ts

theorem andTrue (a b : Bool) : (a && b) = true ↔ a = true ∧ b = true := by
  constructor
  · intro h
    cases a
    · nomatch h
    · exact ⟨rfl, h⟩
  · intro h
    rw [h.1]
    exact h.2

theorem forestSound (ts : List DecisionTree) :
    allResults ts = true ↔ allAccept ts := by
  induction ts with
  | nil => exact ⟨fun _ => True.intro, fun _ => rfl⟩
  | cons t ts ih =>
    change (result t && allResults ts) = true ↔ accepts t ∧ allAccept ts
    constructor
    · intro h
      have pair := (andTrue (result t) (allResults ts)).mp h
      exact ⟨(treeSound t).mp pair.1, ih.mp pair.2⟩
    · intro h
      exact (andTrue (result t) (allResults ts)).mpr
        ⟨(treeSound t).mpr h.1, ih.mpr h.2⟩

#print axioms PnpComposition.independentProduct
#print axioms PnpComposition.treeSound
#print axioms PnpComposition.forestSound

end PnpComposition
