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

inductive Derivable {P V : Type} (premises : P → Prop)
    (add : P → P → P) (mul : P → V → P) (eligible : P → Prop) : P → Prop where
  | initial {p} : premises p → Derivable premises add mul eligible p
  | sum {p q} : Derivable premises add mul eligible p →
      Derivable premises add mul eligible q → Derivable premises add mul eligible (add p q)
  | product {p v} : Derivable premises add mul eligible p →
      eligible (mul p v) → Derivable premises add mul eligible (mul p v)

theorem closedSpaceObstruction {P V : Type} (premises space : P → Prop)
    (add : P → P → P) (mul : P → V → P) (eligible : P → Prop)
    (initial : ∀ p, premises p → space p)
    (sumClosed : ∀ p q, space p → space q → space (add p q))
    (mulClosed : ∀ p v, space p → eligible (mul p v) → space (mul p v))
    (one : P) (notOne : ¬ space one) :
    ¬ Derivable premises add mul eligible one := by
  have contained : ∀ p, Derivable premises add mul eligible p → space p := by
    intro p h
    induction h with
    | initial ha => exact initial _ ha
    | sum _ _ hp hq => exact sumClosed _ _ hp hq
    | product _ he hp => exact mulClosed _ _ hp he
  exact fun h => notOne (contained one h)

#print axioms PnpDegreeClosure.xorZero
#print axioms PnpDegreeClosure.mulZero
#print axioms PnpDegreeClosure.closedSpaceObstruction

end PnpDegreeClosure
