import F038Formal.Composition

namespace MathOS.F038.Composition.Tests
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.Bridge
open MathOS.F038.Composition

def eqF : RowFactor 2 := ⟨[0,1], [[false,false],[true,true]]⟩
def oneF : RowFactor 2 := ⟨[1], [[true]]⟩
def zeroF : RowFactor 2 := ⟨[1], [[false]]⟩
def satInput : List (RowFactor 2) := [eqF,oneF]
def unsatInput : List (RowFactor 2) := [eqF,oneF,zeroF]

def aMap : AffineMap 2 1 :=
  { free := fun _ => 1
    forms := fun _ => ⟨[0],false⟩
    proofs := fun i => if i.val = 0 then .source 0 [true,true] false else .reflexive 1 }

def satResidual : List (RowFactor 1) := [⟨[0], [[true]]⟩]
def unsatResidual : List (RowFactor 1) := [⟨[], []⟩]

def emptyPacket : Packet 1 :=
  { retained := [0], paths := [], holeCount := 0,
    groups := [⟨[], .source 0 []⟩], placements := [], conflicts := [] }

def contradictionProof : EqProof 2 :=
  .cancel (.add (.source 1 [true] true) (.source 2 [true] false)) 1

def tag {n : Nat} : Verdict n → Nat
  | .unknown => 0
  | .sat _ => 1
  | .unsat => 2

example : (assignments 0).length = 1 := by decide
example : (assignments 3).length = 8 := by decide
example : materializedCheck satInput aMap satResidual = true := by decide
example : materializedCheck satInput aMap unsatResidual = false := by decide
example : materializedCheck unsatInput aMap unsatResidual = true := by decide
example : tag (certify satInput [] aMap satResidual (.reducedSat (fun _ => true))) = 1 := by decide
example : tag (certify satInput [] aMap satResidual (.reducedSat (fun _ => false))) = 0 := by decide
example : tag (certify unsatInput [] aMap unsatResidual (.reducedHall emptyPacket)) = 2 := by decide
example : tag (certify satInput [] aMap unsatResidual (.reducedHall emptyPacket)) = 0 := by decide
example : tag (certify unsatInput [99] aMap unsatResidual (.reducedHall emptyPacket)) = 0 := by decide
example : tag (certify unsatInput [] aMap unsatResidual (.affineUnsat contradictionProof)) = 2 := by decide
example : tag (release unsatInput [] aMap unsatResidual (.reducedHall emptyPacket) .timeout) = 0 := by decide
example : tag (release unsatInput [] aMap unsatResidual .unknown .unsat) = 0 := by decide
example : tag (release satInput [] aMap satResidual .unknown (.sat (fun _ => true))) = 1 := by decide
example : tag (release unsatInput [] aMap unsatResidual .unknown (.sat (fun _ => true))) = 0 := by decide

theorem certified_fixture : Sound unsatInput
    (certify unsatInput [] aMap unsatResidual (.reducedHall emptyPacket)) :=
  certify_sound _ _ _ _ _

theorem released_fixture : Sound unsatInput
    (release unsatInput [] aMap unsatResidual (.reducedHall emptyPacket) .unsat) :=
  release_sound _ _ _ _ _ _

#print axioms certified_fixture
#print axioms released_fixture
end MathOS.F038.Composition.Tests
