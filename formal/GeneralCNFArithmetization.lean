import Init

/-!
# Arbitrary finite CNF: truth-preserving arithmetic-circuit evaluation

Unlike DisjointORSemantics.lean, literals here can reuse variable indices,
be negated, appear in any order, and occur in empty clauses/formulas.
The theorem is FOR EVERY finite CNF and every total Boolean assignment:
the recursively evaluated arithmetic expression is its truth indicator.

This is an encoding/evaluation equivalence. It does not produce a satisfying
assignment efficiently and proves neither P=NP nor P!=NP. Arithmetic values
are evaluated at 0/1 inputs, NOT formal multivariate polynomials.
-/

namespace MathOS

inductive CnfLiteral where
  | pos : Nat → CnfLiteral
  | neg : Nat → CnfLiteral
  deriving DecidableEq, Repr

/-- A (possibly infinite) total assignment; every finite CNF reads finitely many indices. -/
def cnfLiteralTruth (a : Nat → Bool) : CnfLiteral → Bool
  | .pos n => a n
  | .neg n => !(a n)

/-- Integer indicator of Boolean truth. -/
def cnfBit : Bool → Int
  | false => 0
  | true => 1

/-- Evaluate a clause, including the empty clause (false). -/
def cnfClauseTruth (a : Nat → Bool) : List CnfLiteral → Bool
  | [] => false
  | l :: rest => cnfLiteralTruth a l || cnfClauseTruth a rest

/-- Evaluate arbitrary CNF, including the empty conjunction (true). -/
def cnfFormulaTruth (a : Nat → Bool) : List (List CnfLiteral) → Bool
  | [] => true
  | clause :: rest => cnfClauseTruth a clause && cnfFormulaTruth a rest

/-- Numeric OR gate; a+b-a*b, evaluated at Boolean-indicator inputs. -/
def cnfOrValue (x y : Int) : Int := x + y - x * y

/-- Numeric OR-fold for one clause, retaining the factored expression. -/
def cnfClauseValue (a : Nat → Bool) : List CnfLiteral → Int
  | [] => 0
  | l :: rest => cnfOrValue (cnfBit (cnfLiteralTruth a l))
                    (cnfClauseValue a rest)

/-- Numeric AND-fold for all clauses, retaining factored expressions. -/
def cnfFormulaValue (a : Nat → Bool) : List (List CnfLiteral) → Int
  | [] => 1
  | clause :: rest => cnfClauseValue a clause * cnfFormulaValue a rest

theorem cnfBit_or (b c : Bool) :
    cnfOrValue (cnfBit b) (cnfBit c) = cnfBit (b || c) := by
  cases b <;> cases c <;> decide

theorem cnfBit_and (b c : Bool) :
    cnfBit b * cnfBit c = cnfBit (b && c) := by
  cases b <;> cases c <;> decide

/-- All clauses, including empty clauses, duplicates and variable sharing. -/
theorem cnfClauseValue_indicator (a : Nat → Bool) (clause : List CnfLiteral) :
    cnfClauseValue a clause = cnfBit (cnfClauseTruth a clause) := by
  induction clause with
  | nil => rfl
  | cons l tail ih =>
    change cnfOrValue (cnfBit (cnfLiteralTruth a l))
      (cnfClauseValue a tail) =
      cnfBit (cnfLiteralTruth a l || cnfClauseTruth a tail)
    rw [ih]
    exact cnfBit_or _ _

/-- Main theorem: arbitrary finite CNF matches its integer arithmetic circuit. -/
theorem cnfFormulaValue_indicator (a : Nat → Bool)
    (formula : List (List CnfLiteral)) :
    cnfFormulaValue a formula = cnfBit (cnfFormulaTruth a formula) := by
  induction formula with
  | nil => rfl
  | cons clause rest ih =>
    change cnfClauseValue a clause * cnfFormulaValue a rest =
      cnfBit (cnfClauseTruth a clause && cnfFormulaTruth a rest)
    rw [ih, cnfClauseValue_indicator]
    exact cnfBit_and _ _

/-- The arithmetic value 1 is logically equivalent to CNF satisfaction. -/
theorem cnfFormulaValue_one_iff (a : Nat → Bool)
    (formula : List (List CnfLiteral)) :
    cnfFormulaValue a formula = 1 ↔ cnfFormulaTruth a formula = true := by
  rw [cnfFormulaValue_indicator]
  cases h : cnfFormulaTruth a formula <;> simp [cnfBit, h]

/-- The existence of a satisfying assignment is preserved in BOTH directions.

This is an equivalence of existential statements; it supplies NO polynomial
time witness-search procedure for arbitrary formulas.
-/
theorem cnfHasWitness_iff (formula : List (List CnfLiteral)) :
    (∃ a : Nat → Bool, cnfFormulaValue a formula = 1) ↔
    (∃ a : Nat → Bool, cnfFormulaTruth a formula = true) := by
  constructor
  · rintro ⟨a, h⟩
    exact ⟨a, (cnfFormulaValue_one_iff a formula).mp h⟩
  · rintro ⟨a, h⟩
    exact ⟨a, (cnfFormulaValue_one_iff a formula).mpr h⟩

/-- The classic contradictory two-unit-clause example remains unsatisfiable. -/
def cnfContradiction : List (List CnfLiteral) :=
  [[.pos 0], [.neg 0]]

theorem cnfContradiction_unsat (a : Nat → Bool) :
    cnfFormulaTruth a cnfContradiction = false := by
  cases h : a 0 <;> simp [cnfContradiction, cnfFormulaTruth,
    cnfClauseTruth, cnfLiteralTruth, h]

/-- Counting numeric OR gates: one per literal occurrence. -/
def cnfClauseOrGates : List CnfLiteral → Nat
  | [] => 0
  | _ :: rest => 1 + cnfClauseOrGates rest

theorem cnfClauseOrGates_length (clause : List CnfLiteral) :
    cnfClauseOrGates clause = clause.length := by
  induction clause with
  | nil => rfl
  | cons l rest ih => simp [cnfClauseOrGates, ih]

/-- Every clause uses one numeric AND gate, including the empty clause. -/
def cnfTotalGates : List (List CnfLiteral) → Nat
  | [] => 0
  | clause :: rest => cnfClauseOrGates clause + 1 + cnfTotalGates rest

def cnfTotalLiterals : List (List CnfLiteral) → Nat
  | [] => 0
  | clause :: rest => clause.length + cnfTotalLiterals rest

/-- Explicit linear bound on the number of factored OR/AND gates. -/
theorem cnfTotalGates_eq (formula : List (List CnfLiteral)) :
    cnfTotalGates formula = cnfTotalLiterals formula + formula.length := by
  induction formula with
  | nil => rfl
  | cons clause rest ih =>
    simp only [cnfTotalGates, cnfTotalLiterals, List.length_cons,
      cnfClauseOrGates_length, ih]
    omega

end MathOS

#print axioms MathOS.cnfFormulaValue_indicator
#print axioms MathOS.cnfHasWitness_iff
#print axioms MathOS.cnfTotalGates_eq
