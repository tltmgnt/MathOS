/-! General obstruction to inference from a finite prefix. -/
namespace ProctorScopeGap

def prefixFunction (N n : Nat) : Nat := if n ≤ N then 0 else 1

theorem prefix_countermodel (N : Nat) :
    (∀ n : Nat, n ≤ N → prefixFunction N n = 0) ∧
      prefixFunction N (N+1) = 1 := by
  constructor
  · intro n h
    simp [prefixFunction, h]
  · have h : ¬ N+1 ≤ N := Nat.not_le_of_gt (Nat.lt_succ_self N)
    simp [prefixFunction, h]

theorem no_finite_prefix_rule (N : Nat) :
    ¬ (∀ f : Nat → Nat, (∀ n : Nat, n ≤ N → f n = 0) → ∀ n, f n = 0) := by
  intro rule
  have h := rule (prefixFunction N) (prefix_countermodel N).left (N+1)
  rw [(prefix_countermodel N).right] at h
  exact Nat.noConfusion h

end ProctorScopeGap
#print axioms ProctorScopeGap.prefix_countermodel
#print axioms ProctorScopeGap.no_finite_prefix_rule
