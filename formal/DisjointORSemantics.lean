import Init

/-!
# Boolean semantics for the disjoint-clause SAT1 product

For each pair of Boolean inputs, x + y - x*y (with Boolean values embedded
into integers) is the indicator of x OR y. The product of these factors is
therefore the indicator of a conjunction of disjoint 2-clauses, for every
finite list of input pairs. A constructive all-true-first-coordinate
assignment satisfies every such conjunction.

This is an exact, kernel-checkable statement in the explicitly defined
Boolean/Int semantics. It does NOT define a general multivariate polynomial
ring, prove a uniform polynomial-time SAT algorithm for arbitrary CNF, or
prove anything about P versus NP.
-/

namespace MathOS

/-- Embed a Boolean into the integer ring. -/
def satBitInt : Bool → Int
  | false => 0
  | true => 1

/-- The OR polynomial on Boolean 0/1 inputs. -/
def satOrFactor (a b : Bool) : Int :=
  satBitInt a + satBitInt b - satBitInt a * satBitInt b

/-- The Boolean conjunction of disjoint OR clauses. -/
def satDisjointCNF : List (Bool × Bool) → Bool
  | [] => true
  | (a, b) :: rest => (a || b) && satDisjointCNF rest

/-- Numerical product of OR factors, evaluated on Boolean inputs. -/
def satDisjointProduct : List (Bool × Bool) → Int
  | [] => 1
  | (a, b) :: rest => satOrFactor a b * satDisjointProduct rest

/-- Verify all four Boolean pairs algebraically. -/
theorem satOrFactor_indicator (a b : Bool) :
    satOrFactor a b = satBitInt (a || b) := by
  cases a <;> cases b <;> decide

/-- Boolean AND corresponds to multiplication of 0/1 indicators. -/
theorem satBitInt_and (a b : Bool) :
    satBitInt (a && b) = satBitInt a * satBitInt b := by
  cases a <;> cases b <;> decide

/-- An exact algebraic-semantics bridge for every finite assignment list. -/
theorem satDisjointProduct_indicator (xs : List (Bool × Bool)) :
    satDisjointProduct xs = satBitInt (satDisjointCNF xs) := by
  induction xs with
  | nil => rfl
  | cons pair rest ih =>
    cases pair with
    | mk a b =>
      simp only [satDisjointProduct, satDisjointCNF]
      rw [ih, satOrFactor_indicator]
      exact (satBitInt_and (a || b) (satDisjointCNF rest)).symm

/-- Numerical value 1 is equivalent to satisfaction, for this family. -/
theorem satDisjointProduct_one_iff (xs : List (Bool × Bool)) :
    satDisjointProduct xs = 1 ↔ satDisjointCNF xs = true := by
  rw [satDisjointProduct_indicator]
  cases h : satDisjointCNF xs <;> simp [satBitInt, h]

/-- A simple explicit satisfying assignment for each number of clauses. -/
def satCanonicalAssignment : Nat → List (Bool × Bool)
  | 0 => []
  | n + 1 => (true, false) :: satCanonicalAssignment n

theorem satCanonicalAssignment_length (n : Nat) :
    (satCanonicalAssignment n).length = n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [satCanonicalAssignment, ih]

theorem satCanonicalAssignment_satisfies (n : Nat) :
    satDisjointCNF (satCanonicalAssignment n) = true := by
  induction n with
  | zero => rfl
  | succ n ih => simp [satCanonicalAssignment, satDisjointCNF, ih]

/-- All finite conjunctions in THIS restricted family are satisfiable. -/
theorem satDisjointCNF_has_witness (n : Nat) :
    ∃ assignment : List (Bool × Bool),
      assignment.length = n ∧ satDisjointCNF assignment = true := by
  exact ⟨satCanonicalAssignment n,
    satCanonicalAssignment_length n,
    satCanonicalAssignment_satisfies n⟩

end MathOS

#print axioms MathOS.satDisjointProduct_indicator
#print axioms MathOS.satDisjointCNF_has_witness
