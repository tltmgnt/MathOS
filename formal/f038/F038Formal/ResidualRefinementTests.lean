import F038Formal.ResidualRefinement
import F038Formal.LocalMaterializationTests

namespace MathOS.F038.ResidualRefinement.Tests
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.LocalMaterialization
open MathOS.F038.LocalMaterialization.Tests
open MathOS.F038.Composition.Tests
open MathOS.F038.ResidualRefinement

def allRows : RowFactor 1 := ⟨[0], [[false],[true]]⟩
def emptyRows : RowFactor 1 := ⟨[0], []⟩
def constantTrue : RowFactor 0 := ⟨[], [[]]⟩
def constantFalse : RowFactor 0 := ⟨[], []⟩
def swapped : RowFactor 2 := ⟨[1,0], [[true,false]]⟩
def original : RowFactor 2 := ⟨[0,1], [[false,true]]⟩

example : tautCheck 1 allRows = true := by decide
example : tautCheck 0 allRows = false := by decide
example : tautCheck 0 constantTrue = true := by decide
example : tautCheck 0 constantFalse = false := by decide
example : tautCheck 1 emptyRows = false := by decide
example : tableSetCheck (simplifyResidual 1 satLocal) [oneResidual] = true := by decide
example : tableSetCheck (simplifyResidual 1 unsatLocal) [emptyRows] = true := by decide
example : tableSetCheck (simplifyResidual 1 unsatLocal) [] = false := by decide
example : tableSetCheck (simplifyResidual 1 satLocal) [zeroResidual] = false := by decide
example : sameFactor original swapped = false := by decide
example : sameFactor allRows ⟨[0], [[true],[false],[true]]⟩ = true := by decide
example : tableSetCheck (simplifyResidual 2 [original,swapped]) [original,swapped] = true := by decide
example : tableSetCheck (padZero (simplifyResidual 0 [constantTrue])) [dummyZero] = true := by decide
example : tableSetCheck (padZero (simplifyResidual 0 [constantFalse])) [dummyZero] = false := by decide
example : tableSetCheck (padZero []) [allRows] = false := by decide

theorem concrete_sat_exact (z : Assignment 1) :
    TableModels [oneResidual] z ↔ TableModels satInput (expand aMap z) :=
  simplified_exact 1 aMap satInput satLocal [oneResidual] [[0],[0]] (by decide) (by decide) z

theorem concrete_unsat_exact (z : Assignment 1) :
    TableModels [emptyRows] z ↔ TableModels unsatInput (expand aMap z) :=
  simplified_exact 1 aMap unsatInput unsatLocal [emptyRows] [[0],[0],[0]] (by decide) (by decide) z

theorem zero_dimensional_exact :
    (∃ z, TableModels (padZero [constantFalse]) z) ↔
      (∃ x, TableModels [constantFalse] x) := padZero_satisfiable _

#print axioms concrete_sat_exact
#print axioms concrete_unsat_exact
#print axioms zero_dimensional_exact
end MathOS.F038.ResidualRefinement.Tests
