import Init

/-! Algebraic certificate facts, independent of the Python compiler.
The Boolean row evaluation facts apply to arbitrary finite lists of rows. -/
namespace PnpConstraintAlgebra

def xor (a b : Bool) : Bool := a != b

theorem xorSound (a b r s : Bool) (ha : a = r) (hb : b = s) :
    xor a b = xor r s := by
  rw [ha, hb]

def parity : List Bool → Bool
  | [] => false
  | x :: xs => xor x (parity xs)

theorem parityAppend (xs ys : List Bool) :
    parity (xs ++ ys) = xor (parity xs) (parity ys) := by
  induction xs with
  | nil =>
    change parity ys = xor false (parity ys)
    cases parity ys <;> rfl
  | cons x xs ih =>
    change xor x (parity (xs ++ ys)) = xor (xor x (parity xs)) (parity ys)
    rw [ih]
    cases x <;> cases parity xs <;> cases parity ys <;> rfl

theorem parityCancel (xs : List Bool) : parity (xs ++ xs) = false := by
  rw [parityAppend]
  cases parity xs <;> rfl

theorem rowSumSound (rows rhs : List Bool) (h : rows = rhs) :
    parity rows = parity rhs := by
  rw [h]

theorem contradiction (rows rhs : List Bool) (h : rows = rhs)
    (hz : parity rows = false) (ho : parity rhs = true) : False := by
  have he := rowSumSound rows rhs h
  rw [hz, ho] at he
  nomatch he

theorem splitUnsat (p : Bool → Prop)
    (h0 : ¬ p false) (h1 : ¬ p true) : ¬ (∃ b, p b) := by
  intro h
  rcases h with ⟨b, hb⟩
  cases b
  · exact h0 hb
  · exact h1 hb

theorem splitSat (p : Bool → Prop) (b : Bool) (h : p b) : ∃ x, p x :=
  ⟨b, h⟩

#print axioms PnpConstraintAlgebra.parityAppend
#print axioms PnpConstraintAlgebra.parityCancel
#print axioms PnpConstraintAlgebra.contradiction
#print axioms PnpConstraintAlgebra.splitUnsat
#print axioms PnpConstraintAlgebra.splitSat

end PnpConstraintAlgebra
