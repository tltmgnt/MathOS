/-! F035: amortized route-list construction charge. A successful
relaxation copies the old path spine, appends one literal cell and
prepends one route-table cell. Count those list cells, not native
allocator instructions, pairs, or other temporary values. -/
namespace ProctorRouteAllocation
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc Routes routeFor relax sweep saturate arcs)
open ProctorPathResourceBounds (Short route_mem relax_short sweep_short saturate_short route_table_bound occurrences arcs_bound)
open ProctorReachCost (budget relax_budget sweep_budget saturate_budget table_le_budget seed_budget)

def relaxCells (rs : Routes) (e : Arc) : Nat :=
  match routeFor e.1 rs with
  | none => 0
  | some ps =>
    match routeFor e.2 rs with
    | some _ => 0
    | none => ps.length+2

def sweepCells : List Arc → Routes → Nat
  | [],_ => 0
  | e::es,rs => relaxCells rs e+sweepCells es (relax rs e)

def saturateCells (es : List Arc) : Nat → Routes → Nat
  | 0,_ => 0
  | k+1,rs => sweepCells es rs+saturateCells es k (sweep es rs)

def reachCells (es : List Arc) (a : Literal) : Nat :=
  saturateCells es es.length [(a,[])]

theorem relax_cells (rs : Routes) (e : Arc) (cap : Nat)
    (hs : Short rs) (hb : rs.length+1≤cap) :
    relaxCells rs e+cap*rs.length≤cap*(relax rs e).length := by
  unfold relaxCells relax
  cases hsrc : routeFor e.1 rs with
  | none =>
    change 0+cap*rs.length≤cap*rs.length
    rw [Nat.zero_add]
  | some ps =>
    cases hdst : routeFor e.2 rs with
    | some qs =>
      change 0+cap*rs.length≤cap*rs.length
      rw [Nat.zero_add]
    | none =>
      have hp := hs (e.1,ps) (route_mem rs e.1 ps hsrc)
      have hcost : ps.length+2≤cap :=
        Nat.le_trans (Nat.succ_le_succ (Nat.succ_le_of_lt hp)) hb
      change ps.length+2+cap*rs.length≤cap*(rs.length+1)
      rw [Nat.mul_succ,Nat.add_comm (cap*rs.length) cap]
      exact Nat.add_le_add_right hcost _

private theorem compose (a b x y z : Nat)
    (ha : a+x≤y) (hb : b+y≤z) : a+b+x≤z := by
  have h := Nat.le_trans (Nat.add_le_add_left ha b) hb
  rw [← Nat.add_assoc,Nat.add_comm b a] at h
  exact h

theorem sweep_cells (es work : List Arc) (rs : Routes) (cap : Nat)
    (hs : Short rs) (hb : budget es rs≤cap)
    (sub : ∀ e∈work,e∈es) :
    sweepCells work rs+(cap+1)*rs.length≤(cap+1)*(sweep work rs).length := by
  induction work generalizing rs with
  | nil =>
    change 0+(cap+1)*rs.length≤(cap+1)*rs.length
    rw [Nat.zero_add]
  | cons e work ih =>
    have h1 := relax_cells rs e (cap+1) hs
      (Nat.succ_le_succ (Nat.le_trans (table_le_budget es rs) hb))
    have h2 := ih (relax rs e) (relax_short rs e hs)
      (Nat.le_trans (relax_budget es rs e (sub e (List.Mem.head _))) hb)
      (fun d hd => sub d (List.Mem.tail _ hd))
    change relaxCells rs e+sweepCells work (relax rs e)+(cap+1)*rs.length≤
      (cap+1)*(sweep work (relax rs e)).length
    exact compose _ _ _ _ _ h1 h2

theorem saturate_cells (es : List Arc) (fuel : Nat) (rs : Routes) (cap : Nat)
    (hs : Short rs) (hb : budget es rs≤cap) :
    saturateCells es fuel rs+(cap+1)*rs.length≤
      (cap+1)*(saturate es fuel rs).length := by
  induction fuel generalizing rs with
  | zero =>
    change 0+(cap+1)*rs.length≤(cap+1)*rs.length
    rw [Nat.zero_add]
  | succ k ih =>
    have h1 := sweep_cells es es rs cap hs hb (fun _ h => h)
    have h2 := ih (sweep es rs) (sweep_short es rs hs)
      (Nat.le_trans (sweep_budget es es rs (fun _ h => h)) hb)
    exact compose _ _ _ _ _ h1 h2

-- The seed contains one table cell. Charge only successful new rows.
theorem reach_cells_bound (es : List Arc) (a : Literal) :
    reachCells es a≤(1+es.length+1)*(es.length+1) := by
  have hs : Short [(a,[])] := by
    intro e he
    cases he with
    | head => exact Nat.zero_lt_succ _
    | tail _ hm => cases hm
  have h := saturate_cells es es.length [(a,[])] (1+es.length) hs (seed_budget es a)
  exact Nat.le_trans (Nat.le_trans (Nat.le_add_right _ _) h)
    (Nat.mul_le_mul_left _ (route_table_bound es a es.length))

theorem formula_cells_bound (f : Formula) (a : Literal) :
    reachCells (arcs f) a≤(1+occurrences f+1)*(occurrences f+1) := by
  have h := arcs_bound f
  exact Nat.le_trans (reach_cells_bound _ _)
    (Nat.mul_le_mul (Nat.succ_le_succ (Nat.add_le_add_left h 1)) (Nat.succ_le_succ h))

end ProctorRouteAllocation

#print axioms ProctorRouteAllocation.relax_cells
#print axioms ProctorRouteAllocation.sweep_cells
#print axioms ProctorRouteAllocation.saturate_cells
#print axioms ProctorRouteAllocation.reach_cells_bound
#print axioms ProctorRouteAllocation.formula_cells_bound
