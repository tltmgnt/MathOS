/-! F035: finite counterexample to global peak optimality of the
local next-clause-count selector. The exact unsimplified adaptive
elimination implementation is used, including its tie rule.
This is not an asymptotic lower bound. -/
namespace ProctorGreedyObstruction
open ProctorHallDeficiency
open ProctorAdaptiveElimination (eliminate estimate choose)

def trap : Formula :=
  [[(2,true),(4,true),(5,true)],
   [(1,true),(2,true),(3,false)],
   [(2,true),(3,false),(4,false)],
   [(1,false),(2,false),(4,false)],
   [(3,true),(4,false),(5,false)],
   [(3,true),(4,false),(5,true)],
   [(3,false),(4,false),(5,false)],
   [(1,false),(3,false),(5,true)],
   [(2,false),(3,true),(4,true)],
   [(1,true),(2,true),(3,true)],
   [(2,false),(4,false),(5,true)],
   [(1,true),(3,false),(4,false)]]

def remove (v : Nat) : List Nat → List Nat
  | [] => []
  | w::ws => if v=w then remove v ws else w::remove v ws

def greedy : Nat → List Nat → Formula → List Nat
  | 0,_,_ => []
  | _+1,[],_ => []
  | k+1,v::vs,f =>
    let u := choose f v vs
    u::greedy k (remove u (v::vs)) (eliminate u f)

def counts : List Nat → Formula → List Nat
  | [],f => [f.length]
  | v::vs,f => f.length::counts vs (eliminate v f)

def peak : List Nat → Nat
  | [] => 0
  | a::as => max a (peak as)

def offered : List Nat := [1,2,3,4,5]
def alternative : List Nat := [5,4,1,2,3]

theorem initial_costs :
    offered.map (fun v => estimate v trap)=[13,17,23,17,14] := rfl

theorem greedy_order : greedy 5 offered trap=[1,2,3,4,5] := rfl

theorem greedy_counts : counts (greedy 5 offered trap) trap=[12,13,16,22,0,0] := rfl

theorem alternative_counts : counts alternative trap=[12,14,11,14,0,0] := rfl

theorem greedy_peak : peak (counts (greedy 5 offered trap) trap)=22 := rfl

theorem alternative_peak : peak (counts alternative trap)=14 := rfl

theorem locally_cheaper : estimate 1 trap<estimate 5 trap := by decide

theorem globally_worse :
    peak (counts alternative trap)<peak (counts (greedy 5 offered trap) trap) := by decide

theorem both_finish :
    (counts alternative trap).getLast?=some 0 ∧
      (counts (greedy 5 offered trap) trap).getLast?=some 0 :=
  ⟨rfl,rfl⟩

end ProctorGreedyObstruction

#print axioms ProctorGreedyObstruction.initial_costs
#print axioms ProctorGreedyObstruction.greedy_order
#print axioms ProctorGreedyObstruction.greedy_counts
#print axioms ProctorGreedyObstruction.alternative_counts
#print axioms ProctorGreedyObstruction.greedy_peak
#print axioms ProctorGreedyObstruction.alternative_peak
#print axioms ProctorGreedyObstruction.locally_cheaper
#print axioms ProctorGreedyObstruction.globally_worse
#print axioms ProctorGreedyObstruction.both_finish
