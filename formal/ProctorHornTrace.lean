/-! F028: logical Horn replay invariant, not a machine refinement. -/
namespace ProctorHornTrace

abbrev Rule := List Nat × Option Nat

def Models (rules : List Rule) (x : Nat → Prop) : Prop :=
  ∀ r, r ∈ rules → (∀ v, v ∈ r.1 → x v) →
    match r.2 with
    | none => False
    | some v => x v

def Forced (rules : List Rule) (known : List Nat) : Prop :=
  ∀ v, v ∈ known → ∀ x : Nat → Prop, Models rules x → x v

theorem empty_forced (rules : List Rule) : Forced rules [] := by
  intro v hv
  cases hv

theorem extend_forced (rules : List Rule) (known body : List Nat) (head : Nat)
    (hs : Forced rules known) (hr : (body, some head) ∈ rules)
    (hb : ∀ v, v ∈ body → v ∈ known) : Forced rules (head :: known) := by
  intro v hv x hx
  cases List.mem_cons.mp hv with
  | inl he =>
    subst v
    exact hx (body, some head) hr (fun w hw => hs w (hb w hw) x hx)
  | inr ht =>
    exact hs v ht x hx

theorem conflict_refutes (rules : List Rule) (known body : List Nat)
    (hs : Forced rules known) (hr : (body, none) ∈ rules)
    (hb : ∀ v, v ∈ body → v ∈ known) :
    ¬ ∃ x : Nat → Prop, Models rules x := by
  intro h
  obtain ⟨x, hx⟩ := h
  exact hx (body, none) hr (fun w hw => hs w (hb w hw) x hx)

end ProctorHornTrace

#print axioms ProctorHornTrace.empty_forced
#print axioms ProctorHornTrace.extend_forced
#print axioms ProctorHornTrace.conflict_refutes
