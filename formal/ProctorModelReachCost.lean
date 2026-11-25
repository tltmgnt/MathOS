/-! F035: aggregate reachability comparison charges for the actual
conflict scan and occurrence-based SAT model materialization.
Conservatively charge both complementary searches and both scores.
This does not count rank arithmetic, graph allocation, path compiler,
serialization, or checker execution. -/
namespace ProctorModelReachCost
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc arcs)
open ProctorReachCost (reachCost reach_cost_bound)
open ProctorTwoCNFModel (vertices conflictAt)
open ProctorOrdinaryCompleteness (variables)
open ProctorPathResourceBounds (occurrences arcs_bound)
open ProctorWireTokenBounds (variables_length)

def queryCap (E : Nat) : Nat := E*(E*((1+E)+(1+E)))+(1+E)

theorem query_cap_mono (a b : Nat) (h : a≤b) : queryCap a≤queryCap b := by
  have h1 := Nat.add_le_add_left h 1
  exact Nat.add_le_add (Nat.mul_le_mul h (Nat.mul_le_mul h (Nat.add_le_add h1 h1))) h1

theorem query_bound (f : Formula) (a b : Literal) :
    reachCost (arcs f) a b≤queryCap (occurrences f) :=
  Nat.le_trans (reach_cost_bound _ _ _) (query_cap_mono _ _ (arcs_bound f))

def conflictCost (f : Formula) (v : Nat) : Nat :=
  reachCost (arcs f) (v,true) (v,false)+reachCost (arcs f) (v,false) (v,true)

def scanCost (f : Formula) : List Nat → Nat
  | [] => 0
  | v::vs => conflictCost f v + if conflictAt f v then 0 else scanCost f vs

def scoreCost (f : Formula) (a : Literal) : List Literal → Nat
  | [] => 0
  | b::bs => reachCost (arcs f) a b+scoreCost f a bs

def valueCost (f : Formula) (v : Nat) : Nat :=
  scoreCost f (v,true) (vertices (variables f))+
  scoreCost f (v,false) (vertices (variables f))

def materializeCost (f : Formula) : List Nat → Nat
  | [] => 0
  | v::vs => valueCost f v+materializeCost f vs

private theorem mul_add' (a b c : Nat) : a*(b+c)=a*b+a*c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change a*(b+c+1)=a*b+a*(c+1)
    rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]

private theorem add_mul' (a b c : Nat) : (a+b)*c=a*c+b*c := by
  rw [Nat.mul_comm (a+b) c,mul_add',Nat.mul_comm c a,Nat.mul_comm c b]

theorem conflict_bound (f : Formula) (v : Nat) :
    conflictCost f v≤2*queryCap (occurrences f) := by
  rw [Nat.mul_comm 2,Nat.mul_succ,Nat.mul_one]
  exact Nat.add_le_add (query_bound f _ _) (query_bound f _ _)

theorem scan_bound (f : Formula) (vs : List Nat) :
    scanCost f vs≤vs.length*(2*queryCap (occurrences f)) := by
  induction vs with
  | nil => exact Nat.le_refl _
  | cons v vs ih =>
    change conflictCost f v+(if conflictAt f v then 0 else scanCost f vs)≤
      (vs.length+1)*(2*queryCap (occurrences f))
    rw [add_mul',Nat.one_mul,Nat.add_comm (vs.length*(2*queryCap (occurrences f)))]
    cases h : conflictAt f v with
    | false => exact Nat.add_le_add (conflict_bound f v) ih
    | true => exact Nat.add_le_add (conflict_bound f v) (Nat.zero_le _)

theorem vertices_length (vs : List Nat) : (vertices vs).length=2*vs.length := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change (vertices vs).length+2=2*(vs.length+1)
    rw [ih,Nat.mul_succ]

theorem score_bound (f : Formula) (a : Literal) (bs : List Literal) :
    scoreCost f a bs≤bs.length*queryCap (occurrences f) := by
  induction bs with
  | nil => exact Nat.le_refl _
  | cons b bs ih =>
    change reachCost (arcs f) a b+scoreCost f a bs≤(bs.length+1)*queryCap (occurrences f)
    rw [add_mul',Nat.one_mul,Nat.add_comm (bs.length*queryCap (occurrences f))]
    exact Nat.add_le_add (query_bound f a b) ih

theorem value_bound (f : Formula) (v : Nat) :
    valueCost f v≤2*((2*occurrences f)*queryCap (occurrences f)) := by
  unfold valueCost
  have h1 := score_bound f (v,true) (vertices (variables f))
  have h2 := score_bound f (v,false) (vertices (variables f))
  rw [vertices_length,variables_length] at h1 h2
  rw [Nat.mul_comm 2,Nat.mul_succ,Nat.mul_one]
  exact Nat.add_le_add h1 h2

theorem materialize_bound (f : Formula) (vs : List Nat) :
    materializeCost f vs≤vs.length*(2*((2*occurrences f)*queryCap (occurrences f))) := by
  induction vs with
  | nil => exact Nat.le_refl _
  | cons v vs ih =>
    change valueCost f v+materializeCost f vs≤
      (vs.length+1)*(2*((2*occurrences f)*queryCap (occurrences f)))
    rw [add_mul',Nat.one_mul,Nat.add_comm (vs.length*(2*((2*occurrences f)*queryCap (occurrences f))))]
    exact Nat.add_le_add (value_bound f v) ih

-- Covers both branches conservatively: the SAT branch materializes
-- all occurrences; the UNSAT branch repeats two reach queries.
def totalCharge (f : Formula) (v : Nat) : Nat :=
  scanCost f (variables f)+materializeCost f (variables f)+conflictCost f v

theorem total_bound (f : Formula) (v : Nat) :
    totalCharge f v≤
      occurrences f*(2*queryCap (occurrences f))+
      occurrences f*(2*((2*occurrences f)*queryCap (occurrences f)))+
      2*queryCap (occurrences f) := by
  unfold totalCharge
  have hs := scan_bound f (variables f)
  have hm := materialize_bound f (variables f)
  rw [variables_length] at hs hm
  exact Nat.add_le_add (Nat.add_le_add hs hm) (conflict_bound f v)

end ProctorModelReachCost

#print axioms ProctorModelReachCost.query_cap_mono
#print axioms ProctorModelReachCost.query_bound
#print axioms ProctorModelReachCost.conflict_bound
#print axioms ProctorModelReachCost.scan_bound
#print axioms ProctorModelReachCost.vertices_length
#print axioms ProctorModelReachCost.score_bound
#print axioms ProctorModelReachCost.value_bound
#print axioms ProctorModelReachCost.materialize_bound
#print axioms ProctorModelReachCost.total_bound
