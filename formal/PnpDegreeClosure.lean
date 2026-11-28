import Init

namespace PnpDegreeClosure

theorem xorZero (a b : Bool) (ha : a = false) (hb : b = false) :
    (a != b) = false := by
  cases ha
  cases hb
  rfl

theorem mulZero (a b : Bool) (ha : a = false) :
    (a && b) = false := by
  cases ha
  rfl

inductive Derivable {P V : Type} (axiom : P → Prop)
    (add : P → P → P) (mul : P → V → P) (eligible : P → Prop) : P → Prop where
  | initial {p} : axiom p → Derivable axiom add mul eligible p
  | sum {p q} : Derivable axiom add mul eligible p →
      Derivable axiom add mul eligible q → Derivable axiom add mul eligible (add p q)
  | product {p v} : Derivable axiom add mul eligible p →
      eligible (mul p v) → Derivable axiom add mul eligible (mul p v)

theorem closedSpaceObstruction {P V : Type} (axiom space : P → Prop)
    (add : P → P → P) (mul : P → V → P) (eligible : P → Prop)
    (initial : ∀ p, axiom p → space p)
    (sumClosed : ∀ p q, space p → space q → space (add p q))
    (mulClosed : ∀ p v, space p → eligible (mul p v) → space (mul p v))
    (one : P) (notOne : ¬ space one) :
    ¬ Derivable axiom add mul eligible one := by
  intro h
  apply notOne
  induction h with
  | initial ha => exact initial _ ha
  | sum _ _ hp hq => exact sumClosed _ _ hp hq
  | product _ he hp => exact mulClosed _ _ hp he

#print axioms PnpDegreeClosure.xorZero
#print axioms PnpDegreeClosure.mulZero
#print axioms PnpDegreeClosure.closedSpaceObstruction

end PnpDegreeClosure
