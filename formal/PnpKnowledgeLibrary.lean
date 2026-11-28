import Init

namespace PnpKnowledgeLibrary

theorem premiseStrengthening {A : Type} (target premise : A → Prop)
    (h : ∀ a, target a → premise a)
    (unsat : ∀ a, ¬ premise a) : ∀ a, ¬ target a :=
  fun a ht => unsat a (h a ht)

theorem coverTransitive {A B C : Type} (p : A → Prop) (q : B → Prop) (r : C → Prop)
    (f : B → A) (g : C → B)
    (hp : ∀ b, q b → p (f b))
    (hq : ∀ c, r c → q (g c)) :
    ∀ c, r c → p (f (g c)) :=
  fun c hc => hp (g c) (hq c hc)

theorem strengtheningOr (a b c : Bool) (h : (a || b) = true) :
    ((a || b) || c) = true := by
  rw [h]
  rfl

#print axioms PnpKnowledgeLibrary.premiseStrengthening
#print axioms PnpKnowledgeLibrary.coverTransitive
#print axioms PnpKnowledgeLibrary.strengtheningOr

end PnpKnowledgeLibrary
