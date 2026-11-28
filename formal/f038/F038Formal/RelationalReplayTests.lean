import F038Formal.RelationalReplay
import F038Formal.LocalMaterializationTests

namespace MathOS.F038.RelationalReplay.Tests
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.LocalMaterialization
open MathOS.F038.RelationalReplay
open MathOS.F038.Composition.Tests
open MathOS.F038.LocalMaterialization.Tests

def equality : RowFactor 2 := ⟨[0,1], [[false,false],[true,true]]⟩
def pin : RowFactor 2 := ⟨[1], [[true]]⟩
def refined : RowFactor 2 := ⟨[0,1], [[true,true]]⟩
def wrong : RowFactor 2 := ⟨[0,1], [[false,false]]⟩
def input : List (RowFactor 2) := [equality,pin]
def output : List (RowFactor 2) := [refined,pin]
def step : Deletion := ⟨0,1,[[false,false]]⟩
example : closureCheck input output [step] = true := by decide
example : closureCheck input [pin,refined] [step] = true := by decide
example : closureCheck input output [⟨0,1,[[true,true]]⟩] = false := by decide
example : closureCheck input output [⟨0,1,[]⟩] = false := by decide
example : closureCheck input output [⟨0,0,[[false,false]]⟩] = false := by decide
example : closureCheck input output [⟨2,1,[[false,false]]⟩] = false := by decide
example : closureCheck input output [step,step] = false := by decide
example : closureCheck input output [] = false := by decide
example : closureCheck input [wrong,pin] [step] = false := by decide
example : closureCheck input [refined] [step] = false := by decide
example : entailCheck 2 refined pin [0,1] = true := by decide
example : entailCheck 1 refined pin [0,1] = false := by decide
example : entailCheck 2 refined pin [1] = false := by decide
example : entailCheck 2 equality pin [0,1] = false := by decide

theorem deletion_fixture_exact (x : Assignment 2) :
    TableModels output x ↔ TableModels input x :=
  closureCheck_exact input output [step] (by decide) x

theorem addition_fixture_exact (x : Assignment 2) :
    TableModels (pin :: [refined]) x ↔ TableModels [refined] x :=
  addStep_exact 2 [refined] (pin :: [refined]) ⟨0,pin,[0,1]⟩ (by decide) x

#print axioms deletion_fixture_exact
#print axioms addition_fixture_exact
end MathOS.F038.RelationalReplay.Tests
