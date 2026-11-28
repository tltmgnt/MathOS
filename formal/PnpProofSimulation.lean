import Init

namespace PnpProofSimulation

theorem paddingEquiv (c z : Bool) :
    ((c || z) && (c || !z)) = c := by
  cases c <;> cases z <;> rfl

theorem restrictedResolution (a b x : Bool)
    (hp : (x || a) = true) (hn : ((!x) || b) = true) :
    (a || b) = true := by
  cases x <;> cases a <;> cases b <;>
    first | rfl | exact hp | exact hn

theorem implicationTransport {A B : Type} (f : A → Prop) (g : B → Prop)
    (pull : B → A) (preserves : ∀ b, g b → f (pull b))
    (unsat : ∀ a, ¬ f a) : ∀ b, ¬ g b :=
  fun b hg => unsat (pull b) (preserves b hg)

#print axioms PnpProofSimulation.paddingEquiv
#print axioms PnpProofSimulation.restrictedResolution
#print axioms PnpProofSimulation.implicationTransport

end PnpProofSimulation
