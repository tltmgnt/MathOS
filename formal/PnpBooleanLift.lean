import Init

namespace PnpBooleanLift

theorem falsificationOr (a b : Bool) :
    !(a || b) = ((!a) && (!b)) := by
  cases a <;> cases b <;> rfl

theorem multiplyZero (p m : Bool) (h : p = false) :
    (m && p) = false := by
  rw [h]
  cases m <;> rfl

theorem squareFree (a : Bool) : (a && a) = a := by
  cases a <;> rfl

theorem relaxationRefutation {A B : Type} (f : A → Prop) (g : B → Prop)
    (lift : A → B) (necessary : ∀ a, f a → g (lift a))
    (unsat : ∀ b, ¬ g b) : ∀ a, ¬ f a :=
  fun a h => unsat (lift a) (necessary a h)

#print axioms PnpBooleanLift.falsificationOr
#print axioms PnpBooleanLift.multiplyZero
#print axioms PnpBooleanLift.squareFree
#print axioms PnpBooleanLift.relaxationRefutation

end PnpBooleanLift
