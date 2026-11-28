import Init

namespace PnpProofAbstraction

theorem resolutionSound (p a b : Bool)
    (hp : (p || a) = true) (hn : ((!p) || b) = true) :
    (a || b) = true := by
  cases p <;> cases a <;> cases b <;>
    first | rfl | exact hp | exact hn

theorem refutationReuse {A B : Type} (premise : A → Prop) (target : B → Prop)
    (embed : B → A)
    (unsat : ∀ a, ¬ premise a)
    (preserves : ∀ b, target b → premise (embed b)) :
    ∀ b, ¬ target b :=
  fun b hb => unsat (embed b) (preserves b hb)

theorem strongerFormula {A : Type} (p q : A → Prop)
    (h : ∀ a, ¬ p a) : ∀ a, ¬ (p a ∧ q a) :=
  fun a ha => h a ha.1

#print axioms PnpProofAbstraction.resolutionSound
#print axioms PnpProofAbstraction.refutationReuse
#print axioms PnpProofAbstraction.strongerFormula

end PnpProofAbstraction
