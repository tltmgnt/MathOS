import F038Formal.Reduction

namespace MathOS.F038.Reduction.Tests
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction

def wide : RowFactor 2 := ⟨[0,1], [[false,false],[false,true],[true,false],[true,true]]⟩
def one : RowFactor 2 := ⟨[1], [[true]]⟩
def equality : RowFactor 2 := ⟨[0,1], [[false,false],[true,true]]⟩
def unequal : RowFactor 2 := ⟨[0,1], [[false,true],[true,false]]⟩

example : (semijoin wide one).rows = [[false,true],[true,true]] := by decide
example : (semijoin equality one).rows = [[true,true]] := by decide
example : (semijoin equality unequal).rows = [] := by decide
example : (relationalReplay [wide,one] [1]).map (List.map RowFactor.rows) =
    some [[[false,true],[true,true]],[[true]]] := by decide
example : (relationalReplay [wide,one] [5]).isNone = true := by decide

def eqSource : EqProof 2 := .source 0 [true,true] false
def neqSource : EqProof 2 := .source 1 [true,true] true
def contradictionProof : EqProof 2 := .cancel (.cancel (.add eqSource neqSource) 0) 1

example : equationCheck [equality,unequal] eqSource ⟨[0,1],false⟩ = true := by decide
example : equationCheck [equality,unequal] contradictionProof ⟨[],true⟩ = true := by decide
example : equationCheck [equality] (.source 0 [true,true] true) ⟨[0,1],true⟩ = false := by decide
example : equationCheck [equality] (.source 0 [true] false) ⟨[0],false⟩ = false := by decide
example : equationCheck [equality] (.source 4 [true,true] false) ⟨[0,1],false⟩ = false := by decide
example : equationCheck [equality] (.cancel eqSource 0) ⟨[1],false⟩ = false := by decide
example : equationCheck [equality] (.reflexive 1) ⟨[1,1],false⟩ = true := by decide

theorem contradictory_fixture : ¬ ∃ x, TableModels [equality,unequal] x :=
  affine_contradiction_sound _ contradictionProof (by decide)

-- x0 = x1, with x1 the retained free coordinate. Its own reconstruction
-- equation is the reflexive identity, not a constraint on x1.
def aMap : AffineMap 2 1 :=
  { free := fun _ => 1
    forms := fun _ => ⟨[0],false⟩
    proofs := fun i => if i.val = 0 then eqSource else .reflexive 1 }

example : affineMapCheck [equality,one] aMap = true := by decide
example : pullbackCheck [equality,one] aMap (fun _ => true) = true := by decide
example : pullbackCheck [equality,one] aMap (fun _ => false) = false := by decide
example : (expand aMap (fun _ => true)) 0 = true := by decide
example : affineMapCheck [unequal,one] aMap = false := by decide

theorem fixture_reduction :
    (∃ x, TableModels [equality,one] x) ↔
    (∃ z, pullbackCheck [equality,one] aMap z = true) :=
  affine_reduction_exact _ aMap (by decide)

#print axioms contradictory_fixture
#print axioms fixture_reduction
end MathOS.F038.Reduction.Tests
