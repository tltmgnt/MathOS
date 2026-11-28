import F038Formal.LocalMaterialization
import F038Formal.CompositionTests

namespace MathOS.F038.LocalMaterialization.Tests
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.Bridge
open MathOS.F038.Composition
open MathOS.F038.Composition.Tests
open MathOS.F038.LocalMaterialization

def eqResidual : RowFactor 1 := ⟨[], [[]]⟩
def oneResidual : RowFactor 1 := ⟨[0], [[true]]⟩
def zeroResidual : RowFactor 1 := ⟨[0], [[false]]⟩
def satLocal : List (RowFactor 1) := [eqResidual, oneResidual]
def unsatLocal : List (RowFactor 1) := [eqResidual, oneResidual, zeroResidual]
example : (localAssignments ([0,1,0] : List (Fin 2))).length = 8 := by decide
example : factorCheck 1 aMap eqF eqResidual [0] = true := by decide
example : factorCheck 1 aMap oneF oneResidual [0] = true := by decide
example : factorCheck 1 aMap oneF zeroResidual [0] = false := by decide
example : factorCheck 1 aMap oneF oneResidual [] = false := by decide
example : factorCheck 0 aMap oneF oneResidual [0] = false := by decide
example : factorCheck 1 aMap oneF oneResidual [0,0] = false := by decide
example : localCheck 1 aMap satInput satLocal [[0],[0]] = true := by decide
example : localCheck 1 aMap unsatInput unsatLocal [[0],[0],[0]] = true := by decide
example : localCheck 1 aMap satInput satLocal [[0]] = false := by decide
example : localCheck 1 aMap satInput [oneResidual] [[0],[0]] = false := by decide
example : localCheck 1 aMap satInput [eqResidual,zeroResidual] [[0],[0]] = false := by decide

def identity64 : AffineMap 64 64 :=
  { free := id, forms := fun i => ⟨[i],false⟩, proofs := fun i => .reflexive i }
def wideUniverse : RowFactor 64 := ⟨[0,63], [[false,true],[true,false]]⟩
example : factorCheck 2 identity64 wideUniverse wideUniverse [0,63] = true := by decide
example : factorCheck 2 identity64 wideUniverse wideUniverse [0] = false := by decide
example : factorCheck 1 identity64 wideUniverse wideUniverse [0,63] = false := by decide

theorem sat_fixture_exact (z : Assignment 1) :
    TableModels satLocal z ↔ TableModels satInput (expand aMap z) :=
  localCheck_exact 1 aMap satInput satLocal [[0],[0]] (by decide) z

theorem unsat_fixture_exact :
    (∃ x, TableModels unsatInput x) ↔ (∃ z, TableModels unsatLocal z) :=
  local_reduction_exact 1 unsatInput unsatInput [] rfl aMap (by decide)
    unsatLocal [[0],[0],[0]] (by decide)

#print axioms sat_fixture_exact
#print axioms unsat_fixture_exact
end MathOS.F038.LocalMaterialization.Tests
