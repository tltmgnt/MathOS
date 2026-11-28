import Init

/-! Concrete two-variable boundary of unsigned primal graph information.
This is a finite mathematical statement, not a correctness proof for Python
or an unrestricted computational complexity lower bound. -/

namespace PnpConvergenceBoundary

abbrev Assignment := Bool × Bool
abbrev Literal := Bool × Bool
abbrev Formula := List (List Literal)

def literalTruth (a : Assignment) (l : Literal) : Bool :=
  (if l.1 then a.2 else a.1) == l.2

def cnfTruth (f : Formula) (a : Assignment) : Bool :=
  f.all (fun c => c.any (literalTruth a))

def primalEdge (f : Formula) (u v : Bool) : Bool :=
  (u != v) && f.any (fun c =>
    (c.any (fun l => l.1 == u)) && (c.any (fun l => l.1 == v)))

def satFormula : Formula := [[(false, true), (true, true)]]
def unsatFormula : Formula :=
  satFormula ++ [[(false, false)], [(true, false)]]

theorem samePrimal (u v : Bool) :
    primalEdge satFormula u v = primalEdge unsatFormula u v := by
  cases u <;> cases v <;> decide

theorem satWitness : ∃ a : Assignment, cnfTruth satFormula a = true := by
  exact ⟨(true, true), by decide⟩

theorem unsatAll (a : Assignment) : cnfTruth unsatFormula a = false := by
  rcases a with ⟨x, y⟩
  cases x <;> cases y <;> decide

theorem unsignedGraphInsufficient :
    (∀ u v, primalEdge satFormula u v = primalEdge unsatFormula u v) ∧
    (∃ a, cnfTruth satFormula a = true) ∧
    (∀ a, cnfTruth unsatFormula a = false) :=
  ⟨samePrimal, satWitness, unsatAll⟩

#print axioms PnpConvergenceBoundary.samePrimal
#print axioms PnpConvergenceBoundary.satWitness
#print axioms PnpConvergenceBoundary.unsatAll
#print axioms PnpConvergenceBoundary.unsignedGraphInsufficient

end PnpConvergenceBoundary
