import Init

namespace MraXTape

-- Feasible cost relations: absence of a row represents infeasibility.
def GlobalMin {C : Type} (le : C → C → Prop) (R : C → Prop) (m : C) : Prop :=
  R m ∧ ∀ c, R c → le m c

def Original {S X C : Type} (cost : S → X → C → Prop)
    (combine : S → C → C) (z : C) : Prop :=
  ∃ s x c, cost s x c ∧ z = combine s c

def Projected {S C : Type} (project : S → C → Prop)
    (combine : S → C → C) (z : C) : Prop :=
  ∃ s p, project s p ∧ z = combine s p

-- Every projected cost is attained; every original feasible cost is
-- dominated by an attained projected cost at the same separator.
-- The combine operation represents the contribution of unaffected factors.
theorem projected_min_iff {S X C : Type} (le : C → C → Prop)
    (trans : ∀ {a b c}, le a b → le b c → le a c)
    (cost : S → X → C → Prop) (project : S → C → Prop)
    (combine : S → C → C)
    (mono : ∀ s {a b}, le a b → le (combine s a) (combine s b))
    (attained : ∀ s p, project s p → ∃ x, cost s x p)
    (dominates : ∀ s x c, cost s x c → ∃ p, project s p ∧ le p c)
    (antisymm : ∀ {a b}, le a b → le b a → a = b)
    (m : C) :
    GlobalMin le (Original cost combine) m ↔
      GlobalMin le (Projected project combine) m := by
  constructor
  · intro h
    obtain ⟨⟨s, x, c, hc, heq⟩, hmin⟩ := h
    obtain ⟨p, hp, hpc⟩ := dominates s x c hc
    obtain ⟨y, hy⟩ := attained s p hp
    have hlow : le m (combine s p) := hmin _ ⟨s, y, p, hy, rfl⟩
    have hupp : le (combine s p) m := heq.symm ▸ mono s hpc
    have hm : m = combine s p := antisymm hlow hupp
    refine ⟨⟨s, p, hp, hm⟩, ?_⟩
    intro z hz
    obtain ⟨s', p', hp', heq'⟩ := hz
    obtain ⟨x', hx'⟩ := attained s' p' hp'
    exact hmin z ⟨s', x', p', hx', heq'⟩
  · intro h
    obtain ⟨⟨s, p, hp, heq⟩, hmin⟩ := h
    obtain ⟨x, hx⟩ := attained s p hp
    refine ⟨⟨s, x, p, hx, heq⟩, ?_⟩
    intro z hz
    obtain ⟨s', x', c', hc', heq'⟩ := hz
    obtain ⟨p', hp', hpc⟩ := dominates s' x' c' hc'
    have hlow : le m (combine s' p') := hmin _ ⟨s', p', hp', rfl⟩
    exact heq'.symm ▸ trans hlow (mono s' hpc)

-- If the projected instance is feasible, its recorded choice can be lifted.
theorem projected_witness {S X C : Type}
    (cost : S → X → C → Prop) (project : S → C → Prop)
    (attained : ∀ s p, project s p → ∃ x, cost s x p)
    (s : S) (p : C) (h : project s p) : ∃ x, cost s x p :=
  attained s p h

end MraXTape

#print axioms MraXTape.projected_min_iff
#print axioms MraXTape.projected_witness
