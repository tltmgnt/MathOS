import Init

namespace MraXTga

-- A row-scope family is a predicate on predicates of coordinate indices.
-- Admissibility means that each selected scope agrees with some feasible witness.
def Relaxation {I V : Type} (F : (I → V) → Prop)
    (scopes : (I → Prop) → Prop) (x : I → V) : Prop :=
  ∀ S : I → Prop, scopes S → ∃ y : I → V, F y ∧ ∀ i : I, S i → x i = y i

theorem feasible_in_relaxation {I V : Type} (F : (I → V) → Prop)
    (scopes : (I → Prop) → Prop) (x : I → V) :
    F x → Relaxation F scopes x := by
  intro hx S _
  exact ⟨x, hx, fun _ _ => rfl⟩

theorem scope_monotone {I V : Type} (F : (I → V) → Prop)
    (small large : (I → Prop) → Prop) (x : I → V) :
    (∀ S : I → Prop, small S → large S) →
      Relaxation F large x → Relaxation F small x := by
  intro h hx S hs
  exact hx S (h S hs)

theorem full_scope_exact {I V : Type} (F : (I → V) → Prop)
    (scopes : (I → Prop) → Prop) (x : I → V) :
    scopes (fun _ : I => True) → Relaxation F scopes x → F x := by
  intro hs hx
  obtain ⟨y, hy, heq⟩ := hx (fun _ => True) hs
  have hxy : x = y := funext (fun i => heq i True.intro)
  exact hxy.symm ▸ hy

end MraXTga
