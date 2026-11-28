import F038Formal.Certificate

namespace MathOS.F038.Cert.Tests
open MathOS.F038
open MathOS.F038.Cert

-- x, y required; x -> u -> not y. A two-group, one-hole contradiction.
def x : Lit 3 := ⟨0, true⟩
def y : Lit 3 := ⟨1, true⟩
def u : Lit 3 := ⟨2, true⟩

def tables : List (RowFactor 3) :=
  [⟨[0], [[true]]⟩,
   ⟨[1], [[true]]⟩,
   ⟨[0,2], [[false,false],[false,true],[true,true]]⟩,
   ⟨[2,1], [[false,false],[false,true],[true,false]]⟩]

def forward : Steps 3 :=
  [(u, .source 2 [true,false]), (neg y, .source 3 [true,true])]

def backward : Steps 3 :=
  [(neg u, .source 3 [true,true]), (neg x, .source 2 [true,false])]

def certificate : HallCert 3 :=
  { groupCount := 2
    holeCount := 1
    groups := fun i => if i.val = 0 then ⟨[x], .source 0 [false]⟩
      else ⟨[y], .source 1 [false]⟩
    placements := [(x, 0), (y, 0)]
    conflicts := [⟨x,y,forward⟩, ⟨y,x,backward⟩] }

-- Positive replay and proof transfer on the actual finite table fixture.
example : hallCheck tables certificate = true := by decide

theorem fixture_unsat : ¬ ∃ a, TableModels tables a :=
  hallCheck_sound tables certificate (by decide)

-- Concrete source decoding, resolution, path endpoints and corruption controls.
example : clauseCheck tables (.source 0 [false]) [x] = true := by decide
example : clauseCheck tables (.source 99 [false]) [x] = false := by decide
example : clauseCheck tables (.source 0 []) [x] = false := by decide
example : clauseCheck tables (.source 0 [true]) [x] = false := by decide
example : clauseCheck tables (.source 0 [false]) [neg x] = false := by decide
example : clauseCheck tables
    (.resolution (.source 2 [true,false]) (.source 3 [true,true]) u)
    [neg x, neg y] = true := by decide
example : pathCheck tables x (neg y) forward = true := by decide
example : pathCheck tables x (neg y) [(u, .source 2 [true,false])] = false := by decide
example : pathCheck tables x y forward = false := by decide
example : pathCheck tables x (neg y)
    [(u, .source 2 [true,true]), (neg y, .source 3 [true,true])] = false := by decide
example : hallCheck tables { certificate with conflicts := [] } = false := by decide
example : hallCheck tables { certificate with placements := [(x, 0)] } = false := by decide

def groupsList : List (Group 3) :=
  [⟨[x], .source 0 [false]⟩, ⟨[y], .source 1 [false]⟩]
def conflictsList : List (Conflict 3) := [⟨x,y,forward⟩, ⟨y,x,backward⟩]

example : checkHallLists tables 1 groupsList [(x,0),(y,0)] conflictsList = true := by decide
example : checkHallLists tables 1 groupsList [(x,1),(y,0)] conflictsList = false := by decide
example : checkHallLists tables 2 groupsList [(x,0),(y,1)] conflictsList = false := by decide

theorem list_fixture_unsat : ¬ ∃ a, TableModels tables a :=
  checkHallLists_sound tables 1 groupsList [(x,0),(y,0)] conflictsList (by decide)

#print axioms list_fixture_unsat
#print axioms fixture_unsat
end MathOS.F038.Cert.Tests
