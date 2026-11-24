/-! F030: local Boolean propagation and exhaustive split soundness.
These lemmas do not formalize the Python search or its complexity. -/
namespace ProctorAdaptivePropagation

def literal (positive x : Bool) : Bool :=
  if positive then x else !x

theorem unit_forces (positive x : Bool)
    (h : literal positive x = true) : x = positive := by
  cases positive <;> cases x <;> first | rfl | contradiction

theorem pure_positive_preserves (x rest : Bool) :
    (x || rest) = true → (true || rest) = true := by
  intro _
  rfl

theorem pure_negative_preserves (x rest : Bool) :
    (!x || rest) = true → (!false || rest) = true := by
  intro _
  rfl

theorem false_residual_refutes (a b c : Bool)
    (ha : a = false) (hb : b = false) (hc : c = false) :
    (a || b || c) = false := by
  cases ha
  cases hb
  cases hc
  rfl

theorem split_refutes (p : Bool → Prop)
    (hf : ¬ p false) (ht : ¬ p true) : ¬ ∃ b : Bool, p b := by
  intro h
  obtain ⟨b, hb⟩ := h
  cases b with
  | false => exact hf hb
  | true => exact ht hb

end ProctorAdaptivePropagation

#print axioms ProctorAdaptivePropagation.unit_forces
#print axioms ProctorAdaptivePropagation.pure_positive_preserves
#print axioms ProctorAdaptivePropagation.pure_negative_preserves
#print axioms ProctorAdaptivePropagation.false_residual_refutes
#print axioms ProctorAdaptivePropagation.split_refutes
