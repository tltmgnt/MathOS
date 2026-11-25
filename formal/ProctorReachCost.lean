/-! F035: executable cost instrumentation for the existing reachability
algorithm. Units are literal-equality probes, not machine instructions.
A parameterized bit-cost bound is conditional on a comparison-cost
contract, not a proof about Lean's runtime representation. -/
namespace ProctorReachCost
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc Routes routeFor relax sweep saturate reach)
open ProctorReachabilityCompleteness (Known Extends relax_extends missing missing_strict missing_bound)

-- Count the actual comparisons in a successful or unsuccessful lookup.
def probes (a : Literal) : Routes → Nat
  | [] => 0
  | (b,_)::rs => if a=b then 1 else 1+probes a rs

theorem probes_bound (a : Literal) (rs : Routes) : probes a rs≤rs.length := by
  induction rs with
  | nil => exact Nat.le_refl _
  | cons e rs ih =>
    cases e with
    | mk b ps =>
      change (if a=b then 1 else 1+probes a rs)≤rs.length+1
      by_cases h : a=b
      · rw [if_pos h,Nat.add_comm rs.length 1]
        exact Nat.add_le_add_left (Nat.zero_le _) 1
      · rw [if_neg h,Nat.add_comm rs.length 1]
        exact Nat.add_le_add_left ih 1

-- Charge both lookups: a conservative bound even if an implementation
-- short-circuits one. Does not charge list allocation or append.
def relaxCost (rs : Routes) (e : Arc) : Nat :=
  probes e.1 rs+probes e.2 rs

def sweepCost : List Arc → Routes → Nat
  | [],_ => 0
  | e::es,rs => relaxCost rs e+sweepCost es (relax rs e)

def saturateCost (es : List Arc) : Nat → Routes → Nat
  | 0,_ => 0
  | k+1,rs => sweepCost es rs+saturateCost es k (sweep es rs)

def reachCost (es : List Arc) (a b : Literal) : Nat :=
  saturateCost es es.length [(a,[])]+probes b (saturate es es.length [(a,[])])

def budget (es : List Arc) (rs : Routes) : Nat :=
  rs.length+missing rs es

theorem relax_budget (es : List Arc) (rs : Routes) (e : Arc) (he : e∈es) :
    budget es (relax rs e)≤budget es rs := by
  have hx := relax_extends rs e
  unfold relax at hx
  unfold budget relax
  cases hs : routeFor e.1 rs with
  | none => exact Nat.le_refl _
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _ => exact Nat.le_refl _
    | none =>
      let qs : Routes := (e.2,ps++[e.2])::rs
      rw [hs,hd] at hx
      have hk : Known qs e.2 := by
        refine ⟨ps++[e.2],?_⟩
        change (if e.2=e.2 then some (ps++[e.2]) else routeFor e.2 rs)=_
        rw [if_pos rfl]
      have hm := missing_strict rs qs es e hx he hd hk
      change rs.length+1+missing qs es≤rs.length+missing rs es
      rw [Nat.add_assoc,Nat.add_comm 1 (missing qs es)]
      exact Nat.add_le_add_left (Nat.succ_le_of_lt hm) _

theorem sweep_budget (es work : List Arc) (rs : Routes)
    (h : ∀ e∈work, e∈es) : budget es (sweep work rs)≤budget es rs := by
  induction work generalizing rs with
  | nil => exact Nat.le_refl _
  | cons e work ih =>
    change budget es (sweep work (relax rs e))≤budget es rs
    exact Nat.le_trans (ih _ (fun d hd => h d (List.Mem.tail _ hd)))
      (relax_budget es rs e (h e (List.Mem.head _)))

theorem saturate_budget (es : List Arc) (fuel : Nat) (rs : Routes) :
    budget es (saturate es fuel rs)≤budget es rs := by
  induction fuel generalizing rs with
  | zero => exact Nat.le_refl _
  | succ k ih =>
    exact Nat.le_trans (ih _) (sweep_budget es es rs (fun _ h => h))

theorem table_le_budget (es : List Arc) (rs : Routes) : rs.length≤budget es rs :=
  Nat.le_add_right _ _

theorem relax_cost_bound (es : List Arc) (rs : Routes) (e : Arc) (cap : Nat)
    (h : budget es rs≤cap) : relaxCost rs e≤cap+cap :=
  Nat.add_le_add (Nat.le_trans (probes_bound e.1 rs) (Nat.le_trans (table_le_budget es rs) h))
    (Nat.le_trans (probes_bound e.2 rs) (Nat.le_trans (table_le_budget es rs) h))

theorem sweep_cost_bound (es work : List Arc) (rs : Routes) (cap : Nat)
    (h : budget es rs≤cap) (sub : ∀ e∈work, e∈es) :
    sweepCost work rs≤work.length*(cap+cap) := by
  induction work generalizing rs with
  | nil => exact Nat.le_refl _
  | cons e work ih =>
    change relaxCost rs e+sweepCost work (relax rs e)≤(work.length+1)*(cap+cap)
    rw [Nat.add_mul,Nat.one_mul,Nat.add_comm (work.length*(cap+cap))]
    exact Nat.add_le_add (relax_cost_bound es rs e cap h)
      (ih _ (Nat.le_trans (relax_budget es rs e (sub e (List.Mem.head _))) h)
        (fun d hd => sub d (List.Mem.tail _ hd)))

theorem saturate_cost_bound (es : List Arc) (fuel : Nat) (rs : Routes) (cap : Nat)
    (h : budget es rs≤cap) :
    saturateCost es fuel rs≤fuel*(es.length*(cap+cap)) := by
  induction fuel generalizing rs with
  | zero => exact Nat.le_refl _
  | succ k ih =>
    change sweepCost es rs+saturateCost es k (sweep es rs)≤(k+1)*(es.length*(cap+cap))
    rw [Nat.add_mul,Nat.one_mul,Nat.add_comm (k*(es.length*(cap+cap)))]
    exact Nat.add_le_add (sweep_cost_bound es es rs cap h (fun _ he => he))
      (ih _ (Nat.le_trans (sweep_budget es es rs (fun _ he => he)) h))

theorem seed_budget (es : List Arc) (a : Literal) :
    budget es [(a,[])]≤1+es.length :=
  Nat.add_le_add_left (missing_bound [(a,[])] es) 1

theorem reach_cost_bound (es : List Arc) (a b : Literal) :
    reachCost es a b≤es.length*(es.length*((1+es.length)+(1+es.length)))+(1+es.length) := by
  let cap := 1+es.length
  have h := seed_budget es a
  have h1 := saturate_cost_bound es es.length [(a,[])] cap h
  have h2 := Nat.le_trans (probes_bound b (saturate es es.length [(a,[])]))
    (Nat.le_trans (table_le_budget es _) (Nat.le_trans (saturate_budget es es.length _) h))
  exact Nat.add_le_add h1 h2

-- Abstract charge for a bounded-cost literal comparison. No claim that
-- this equals the full execution time or allocator work.
def chargedReach (es : List Arc) (a b : Literal) (comparisonCharge : Nat) : Nat :=
  comparisonCharge*reachCost es a b

theorem charged_reach_bound (es : List Arc) (a b : Literal) (c : Nat) :
    chargedReach es a b c≤
      c*(es.length*(es.length*((1+es.length)+(1+es.length)))+(1+es.length)) :=
  Nat.mul_le_mul_left c (reach_cost_bound es a b)

end ProctorReachCost

#print axioms ProctorReachCost.probes_bound
#print axioms ProctorReachCost.relax_budget
#print axioms ProctorReachCost.sweep_budget
#print axioms ProctorReachCost.saturate_budget
#print axioms ProctorReachCost.table_le_budget
#print axioms ProctorReachCost.relax_cost_bound
#print axioms ProctorReachCost.sweep_cost_bound
#print axioms ProctorReachCost.saturate_cost_bound
#print axioms ProctorReachCost.seed_budget
#print axioms ProctorReachCost.reach_cost_bound
#print axioms ProctorReachCost.charged_reach_bound
