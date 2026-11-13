/-!
Finite AND/OR proof-route syntax and its monotonic Boolean semantics.

This is a structural formula model, not a proof of the Python DAG algorithm.
-/
namespace MathOS

universe u

inductive RouteFormula (α : Type u) where
  | assumed : RouteFormula α
  | openLeaf : α → RouteFormula α
  | andNode : RouteFormula α → RouteFormula α → RouteFormula α
  | orNode : RouteFormula α → RouteFormula α → RouteFormula α

def RouteFormula.eval {α : Type u} : RouteFormula α → (α → Prop) → Prop
  | .assumed, _ => True
  | .openLeaf x, accepted => accepted x
  | .andNode left right, accepted =>
      left.eval accepted ∧ right.eval accepted
  | .orNode left right, accepted =>
      left.eval accepted ∨ right.eval accepted

def Included {α : Type u} (a b : α → Prop) : Prop :=
  ∀ x, a x → b x

theorem eval_monotone {α : Type u} (f : RouteFormula α) :
    ∀ a b : α → Prop, Included a b → f.eval a → f.eval b := by
  induction f with
  | assumed =>
      intro a b hab h
      trivial
  | openLeaf x =>
      intro a b hab h
      exact hab x h
  | andNode left right ihLeft ihRight =>
      intro a b hab h
      exact ⟨ihLeft a b hab h.left, ihRight a b hab h.right⟩
  | orNode left right ihLeft ihRight =>
      intro a b hab h
      cases h with
      | inl hl => exact Or.inl (ihLeft a b hab hl)
      | inr hr => exact Or.inr (ihRight a b hab hr)

theorem eval_iff_of_mutual_inclusion {α : Type u}
    (f : RouteFormula α) (a b : α → Prop)
    (hab : Included a b) (hba : Included b a) :
    f.eval a ↔ f.eval b := by
  constructor
  · exact eval_monotone f a b hab
  · exact eval_monotone f b a hba

def MinimalCompletion {α : Type u}
    (f : RouteFormula α) (accepted : α → Prop) : Prop :=
  f.eval accepted ∧
    ∀ other : α → Prop,
      f.eval other → Included other accepted → Included accepted other

theorem minimal_completions_antichain {α : Type u}
    (f : RouteFormula α) (a b : α → Prop)
    (ha : MinimalCompletion f a)
    (hb : MinimalCompletion f b)
    (hab : Included a b) : Included b a := by
  exact hb.right a ha.left hab

theorem minimal_completion_sound {α : Type u}
    (f : RouteFormula α) (a : α → Prop)
    (ha : MinimalCompletion f a) : f.eval a := by
  exact ha.left

theorem minimal_completion_no_strict_subset {α : Type u}
    (f : RouteFormula α) (a b : α → Prop)
    (ha : MinimalCompletion f a)
    (hb : f.eval b) (hba : Included b a) :
    Included a b := by
  exact ha.right b hb hba

end MathOS
