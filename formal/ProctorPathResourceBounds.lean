/-! F035/F040: structural output resource bounds for the executable
implication search and sequential-to-batch path certificate compiler.
These are list and inference counts, not a machine bit-cost theorem. -/
namespace ProctorPathResourceBounds
open ProctorHallDeficiency
open ProctorExecutableReplay (Batch Step)
open ProctorImplicationPathDiscovery (Arc Routes rowArcs arcs routeFor relax sweep saturate reach pathTail pathStart compilePair tryVar)
open ProctorReachabilityCompleteness (Extends Known missing missing_bound missing_mono missing_strict relax_extends)
open ProctorResolutionBridge (copySteps extend compile)
open ProctorUnifiedReplay (Proof)

theorem route_mem (rs : Routes) (a : Literal) (ps : List Literal)
    (h : routeFor a rs=some ps) : (a,ps)∈rs := by
  induction rs with
  | nil => cases h
  | cons e rs ih =>
    cases e with
    | mk b qs =>
      change (if a=b then some qs else routeFor a rs)=some ps at h
      by_cases z : a=b
      · cases z
        rw [if_pos rfl] at h
        cases h
        exact List.Mem.head _
      · rw [if_neg z] at h
        exact List.Mem.tail _ (ih h)

def Short (rs : Routes) : Prop :=
  ∀ e∈rs, e.2.length<rs.length

theorem relax_short (rs : Routes) (e : Arc) (h : Short rs) :
    Short (relax rs e) := by
  unfold relax
  cases hs : routeFor e.1 rs with
  | none => exact h
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _ => exact h
    | none =>
      have hp := h (e.1,ps) (route_mem rs e.1 ps hs)
      intro d hd'
      change d∈(e.2,ps++[e.2])::rs at hd'
      cases hd' with
      | head =>
        change (ps++[e.2]).length<rs.length+1
        rw [List.length_append]
        exact Nat.succ_lt_succ hp
      | tail _ hm => exact Nat.lt_trans (h d hm) (Nat.lt_succ_self _)

theorem sweep_short (es : List Arc) (rs : Routes) (h : Short rs) :
    Short (sweep es rs) := by
  induction es generalizing rs with
  | nil => exact h
  | cons e es ih =>
    exact ih _ (relax_short rs e h)

theorem saturate_short (es : List Arc) (fuel : Nat) (rs : Routes) (h : Short rs) :
    Short (saturate es fuel rs) := by
  induction fuel generalizing rs with
  | zero => exact h
  | succ k ih => exact ih _ (sweep_short es rs h)

-- One new table row consumes at least one unit of missing-destination
-- potential, even with repeated arcs. This is a linear size bound,
-- not the looser bound obtained by counting every relaxation.
theorem relax_budget (es : List Arc) (rs : Routes) (e : Arc) (he : e∈es) :
    (relax rs e).length+missing (relax rs e) es≤rs.length+missing rs es := by
  have hx := relax_extends rs e
  unfold relax at *
  cases hs : routeFor e.1 rs with
  | none => exact Nat.le_refl _
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _ => exact Nat.le_refl _
    | none =>
      let qs : Routes := (e.2,ps++[e.2])::rs
      have hk : Known qs e.2 := by
        refine ⟨ps++[e.2],?_⟩
        change (if e.2=e.2 then some (ps++[e.2]) else routeFor e.2 rs)=_
        rw [if_pos rfl]
      have hm := missing_strict rs qs es e hx he hd hk
      change rs.length+1+missing qs es≤rs.length+missing rs es
      rw [Nat.add_assoc,Nat.add_comm 1 (missing qs es)]
      exact Nat.add_le_add_left (Nat.succ_le_of_lt hm) _

theorem sweep_budget (es work : List Arc) (rs : Routes)
    (h : ∀ e∈work, e∈es) :
    (sweep work rs).length+missing (sweep work rs) es≤rs.length+missing rs es := by
  induction work generalizing rs with
  | nil => exact Nat.le_refl _
  | cons e work ih =>
    change (sweep work (relax rs e)).length+missing (sweep work (relax rs e)) es≤
      rs.length+missing rs es
    exact Nat.le_trans (ih _ (fun d hd => h d (List.Mem.tail _ hd)))
      (relax_budget es rs e (h e (List.Mem.head _)))

theorem saturate_budget (es : List Arc) (fuel : Nat) (rs : Routes) :
    (saturate es fuel rs).length+missing (saturate es fuel rs) es≤rs.length+missing rs es := by
  induction fuel generalizing rs with
  | zero => exact Nat.le_refl _
  | succ k ih =>
    exact Nat.le_trans (ih (sweep es rs)) (sweep_budget es es rs (fun _ h => h))

theorem route_table_bound (es : List Arc) (a : Literal) (fuel : Nat) :
    (saturate es fuel [(a,[])]).length≤es.length+1 := by
  have hb := saturate_budget es fuel [(a,[])]
  have hm := missing_bound ([(a,[])] : Routes) es
  change (saturate es fuel [(a,[])]).length+missing (saturate es fuel [(a,[])]) es≤
    1+missing [(a,[])] es at hb
  exact Nat.le_trans (Nat.le_trans (Nat.le_add_right _ _) hb)
    (Nat.add_le_add_left hm 1) |>.trans (by rw [Nat.add_comm]) (es : List Arc) (a b : Literal) (ps : List Literal)
    (h : reach es a b=some ps) : ps.length≤es.length := by
  have h0 : Short [(a,[])] := by
    intro e he
    cases he with
    | head => exact Nat.zero_lt_succ 0
    | tail _ hz => cases hz
  have hs := saturate_short es es.length _ h0
  have hp := hs (b,ps) (route_mem _ b ps h)
  have hb := route_table_bound es a es.length
  change ps.length<(saturate es es.length [(a,[])]).length at hp
  exact Nat.le_of_succ_le_succ (Nat.le_trans (Nat.succ_le_of_lt hp) hb) (c : Clause) : (rowArcs c).length≤c.length := by
  cases c with
  | nil => exact Nat.le_refl _
  | cons a cs =>
    cases cs with
    | nil => exact Nat.le_refl _
    | cons b bs =>
      cases bs with
      | nil => exact Nat.le_refl _
      | cons d ds => exact Nat.zero_le _

def occurrences : Formula → Nat
  | [] => 0
  | c::cs => c.length+occurrences cs

theorem arcs_bound (f : Formula) : (arcs f).length≤occurrences f := by
  induction f with
  | nil => exact Nat.le_refl _
  | cons c cs ih =>
    change (rowArcs c++arcs cs).length≤c.length+occurrences cs
    rw [List.length_append]
    exact Nat.add_le_add (row_arcs_bound c) ih

theorem copy_length (v i : Nat) (f : Formula) :
    (copySteps v i f).length=f.length := by
  induction f generalizing i with
  | nil => rfl
  | cons c cs ih =>
    change (copySteps v (i+1) cs).length+1=cs.length+1
    rw [ih]

theorem extend_length (v : Nat) (f : Formula) (s : Step) :
    (extend v f s).length=f.length+1 := by
  change (copySteps v 0 f).length+1=f.length+1
  rw [copy_length]

theorem compile_length (v : Nat) (f : Formula) (ss : List Step) :
    (compile v f ss).length=ss.length := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change (compile v (s.tail::f) ss).length+1=ss.length+1
    rw [ih]

def steps : List Batch → Nat
  | [] => 0
  | b::bs => b.length+steps bs

def triangular : Nat → Nat
  | 0 => 0
  | k+1 => k+1+triangular k

theorem compile_steps (v : Nat) (f : Formula) (ss : List Step) :
    steps (compile v f ss)=f.length*ss.length+triangular ss.length := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change (extend v f s).length+steps (compile v (s.tail::f) ss)=
      f.length*(ss.length+1)+(ss.length+1+triangular ss.length)
    rw [extend_length,ih]
    change f.length+1+((f.length+1)*ss.length+triangular ss.length)=_
    rw [Nat.add_mul,Nat.mul_add,Nat.one_mul,Nat.mul_one]
    ac_rfl

theorem triangular_bound (k : Nat) : triangular k≤k*k := by
  induction k with
  | zero => exact Nat.le_refl _
  | succ k ih =>
    change k+1+triangular k≤(k+1)*(k+1)
    rw [Nat.add_mul,Nat.mul_add,Nat.mul_one,Nat.one_mul]
    have hh : k+1+triangular k≤k+1+k*k := Nat.add_le_add_left ih _
    exact Nat.le_trans hh (by
      calc
        k+1+k*k = k*k+k+1 := by ac_rfl
        _ ≤ k*k+k+(k+1) := Nat.add_le_add_left (Nat.succ_le_succ (Nat.zero_le k)) _
        _ = k*k+k+(k+1) := rfl)

theorem compile_steps_bound (v : Nat) (f : Formula) (ss : List Step) :
    steps (compile v f ss)≤(f.length+ss.length)*ss.length := by
  rw [compile_steps,Nat.add_mul]
  exact Nat.add_le_add_left (triangular_bound ss.length) _

private theorem pathTail_length (s a : Literal) (g : Formula) (bs : List Literal)
    (ss : List Step) (out : Formula) (h : pathTail s a g bs=some (ss,out)) :
    ss.length=bs.length := by
  induction bs generalizing a g ss out with
  | nil =>
    change some ([],g)=some (ss,out) at h
    cases h
    rfl
  | cons b bs ih =>
    unfold pathTail at h
    cases hi : ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite a,b]) g with
    | none => rw [hi] at h; cases h
    | some i =>
      rw [hi] at h
      let t := ProctorImplicationPathDiscovery.advanceStep s a b i
      change (do
        let (ts,h') ← pathTail s b (t.tail::g) bs
        some (t::ts,h'))=some (ss,out) at h
      cases he : pathTail s b (t.tail::g) bs with
      | none => rw [he] at h; cases h
      | some pair =>
        cases pair with
        | mk ts g' =>
          rw [he] at h
          change some (t::ts,g')=some (ss,out) at h
          cases h
          exact congrArg Nat.succ (ih b (t.tail::g) ts g' he)

theorem pathStart_length (g : Formula) (s : Literal) (bs : List Literal)
    (ss : List Step) (out : Formula) (h : pathStart g s bs=some (ss,out)) :
    ss.length=bs.length := by
  cases bs with
  | nil => cases h
  | cons b bs =>
    change (do
      let i ← ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite s,b]) g
      let t := ProctorImplicationPathDiscovery.firstStep s b i
      let (ts,h') ← pathTail s b (t.tail::g) bs
      some (t::ts,h'))=some (ss,out) at h
    cases hi : ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite s,b]) g with
    | none => rw [hi] at h; cases h
    | some i =>
      rw [hi] at h
      let t := ProctorImplicationPathDiscovery.firstStep s b i
      change (do
        let (ts,h') ← pathTail s b (t.tail::g) bs
        some (t::ts,h'))=some (ss,out) at h
      cases he : pathTail s b (t.tail::g) bs with
      | none => rw [he] at h; cases h
      | some pair =>
        cases pair with
        | mk ts g' =>
          rw [he] at h
          change some (t::ts,g')=some (ss,out) at h
          cases h
          exact congrArg Nat.succ (pathTail_length s b (t.tail::g) bs ts g' he)

theorem pair_size (f : Formula) (v : Nat) (pos neg : List Literal) (p : Proof)
    (h : compilePair f v pos neg=some p) :
    p.batches.length=pos.length+neg.length+1 ∧
      steps p.batches=f.length*p.batches.length+triangular p.batches.length := by
  unfold compilePair at h
  cases ha : pathStart f (v,true) pos with
  | none => rw [ha] at h; cases h
  | some pair =>
    cases pair with
    | mk a g =>
      rw [ha] at h
      change (do
        let (b,_) ← pathStart g (v,false) neg
        some ⟨compile v f (a++(b++[ProctorImplicationPathDiscovery.closeStep v b.length])),false,.empty⟩)=some p at h
      cases hb : pathStart g (v,false) neg with
      | none => rw [hb] at h; cases h
      | some pair =>
        cases pair with
        | mk b out =>
          rw [hb] at h
          let ss := a++(b++[ProctorImplicationPathDiscovery.closeStep v b.length])
          change some (⟨compile v f ss,false,.empty⟩ : Proof)=some p at h
          cases h
          have h1 := pathStart_length f (v,true) pos a g ha
          have h2 := pathStart_length g (v,false) neg b out hb
          change (compile v f ss).length=pos.length+neg.length+1 ∧
            steps (compile v f ss)=f.length*(compile v f ss).length+triangular (compile v f ss).length
          rw [compile_length,compile_steps]
          constructor
          · unfold ss
            rw [List.length_append,List.length_append,h1,h2]
            rfl
          · rfl

theorem tryVar_size (f : Formula) (v : Nat) (p : Proof)
    (h : tryVar f (arcs f) v=some p) :
    p.batches.length≤2*occurrences f+1 ∧
      steps p.batches≤(f.length+(2*occurrences f+1))*(2*occurrences f+1) := by
  unfold tryVar at h
  cases hp : reach (arcs f) (v,true) (v,false) with
  | none => rw [hp] at h; cases h
  | some pos =>
    rw [hp] at h
    change (do
      let neg ← reach (arcs f) (v,false) (v,true)
      compilePair f v pos neg)=some p at h
    cases hn : reach (arcs f) (v,false) (v,true) with
    | none => rw [hn] at h; cases h
    | some neg =>
      rw [hn] at h
      have hs := pair_size f v pos neg p h
      have h1 := reach_length_bound (arcs f) _ _ pos hp
      have h2 := reach_length_bound (arcs f) _ _ neg hn
      have ha := arcs_bound f
      have hb : p.batches.length≤2*occurrences f+1 := by
        rw [hs.left,Nat.two_mul]
        exact Nat.add_le_add_right (Nat.add_le_add (Nat.le_trans h1 ha) (Nat.le_trans h2 ha)) 1
      refine ⟨hb,?_⟩
      rw [hs.right,Nat.add_mul]
      have hc := Nat.add_le_add (Nat.mul_le_mul_left f.length hb)
        (Nat.le_trans (triangular_bound p.batches.length) (Nat.mul_le_mul hb hb))
      exact hc

end ProctorPathResourceBounds

#print axioms ProctorPathResourceBounds.route_mem
#print axioms ProctorPathResourceBounds.relax_short
#print axioms ProctorPathResourceBounds.sweep_short
#print axioms ProctorPathResourceBounds.saturate_short
#print axioms ProctorPathResourceBounds.relax_budget
#print axioms ProctorPathResourceBounds.sweep_budget
#print axioms ProctorPathResourceBounds.saturate_budget
#print axioms ProctorPathResourceBounds.route_table_bound
#print axioms ProctorPathResourceBounds.reach_length_bound
#print axioms ProctorPathResourceBounds.row_arcs_bound
#print axioms ProctorPathResourceBounds.arcs_bound
#print axioms ProctorPathResourceBounds.copy_length
#print axioms ProctorPathResourceBounds.extend_length
#print axioms ProctorPathResourceBounds.compile_length
#print axioms ProctorPathResourceBounds.compile_steps
#print axioms ProctorPathResourceBounds.triangular_bound
#print axioms ProctorPathResourceBounds.compile_steps_bound
#print axioms ProctorPathResourceBounds.pathStart_length
#print axioms ProctorPathResourceBounds.pair_size
#print axioms ProctorPathResourceBounds.tryVar_size
