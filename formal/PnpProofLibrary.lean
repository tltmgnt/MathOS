import Init

namespace PnpProofLibrary

def Holds (valuation : Nat → Bool) (l : Nat × Bool) : Prop :=
  valuation l.1 = l.2

def Sat (valuation : Nat → Bool) (c : List (Nat × Bool)) : Prop :=
  ∃ l, l ∈ c ∧ Holds valuation l

def Models (valuation : Nat → Bool) (f : List (List (Nat × Bool))) : Prop :=
  ∀ c, c ∈ f → Sat valuation c

theorem subsumptionSound (v : Nat → Bool) (a b : List (Nat × Bool))
    (sub : ∀ l, l ∈ a → l ∈ b) (ha : Sat v a) : Sat v b := by
  obtain ⟨l, hl, hv⟩ := ha
  exact ⟨l, sub l hl, hv⟩

def signedMap (m : Nat → Nat) (flip : Nat → Bool) (l : Nat × Bool) :
    Nat × Bool := (m l.1, if flip l.1 then !l.2 else l.2)

def pullback (v : Nat → Bool) (m : Nat → Nat) (flip : Nat → Bool) :
    Nat → Bool := fun x => if flip x then !(v (m x)) else v (m x)

theorem signedLiteralSound (v : Nat → Bool) (m : Nat → Nat)
    (flip : Nat → Bool) (l : Nat × Bool)
    (h : Holds v (signedMap m flip l)) : Holds (pullback v m flip) l := by
  rcases l with ⟨x,b⟩
  -- Direct Boolean case analysis avoids propositional extensionality.
  have transport : ∀ (s bit value : Bool),
      value = (if s then !bit else bit) →
      (if s then !value else value) = bit := by
    intro s bit value heq
    cases s <;> cases bit <;> cases value <;>
      first | rfl | exact heq | exact heq.symm
  exact transport (flip x) b (v (m x)) h

theorem fragmentComposition {A : Type} (p q r : A → Prop)
    (first : ∀ a, p a → q a) (second : ∀ a, p a → q a → r a) :
    ∀ a, p a → r a :=
  fun a hp => second a hp (first a hp)

theorem checkedAddition {A : Type} (p c : A → Prop)
    (entails : ∀ a, p a → c a) : ∀ a, p a → p a ∧ c a :=
  fun a hp => ⟨hp, entails a hp⟩

theorem emptyClause (v : Nat → Bool) : ¬ Sat v [] := by
  intro h
  obtain ⟨l, hl, _⟩ := h
  nomatch hl

theorem refutationComposition {A : Type} (p q : A → Prop)
    (fragment : ∀ a, p a → q a) (refute : ∀ a, p a → q a → False) :
    ∀ a, ¬ p a := fun a hp => refute a hp (fragment a hp)

#print axioms PnpProofLibrary.subsumptionSound
#print axioms PnpProofLibrary.signedLiteralSound
#print axioms PnpProofLibrary.fragmentComposition
#print axioms PnpProofLibrary.checkedAddition
#print axioms PnpProofLibrary.emptyClause
#print axioms PnpProofLibrary.refutationComposition

end PnpProofLibrary
