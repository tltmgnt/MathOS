/-! F035/F040: fuel-indexed completeness of the existing implication
saturation. This module proves completeness for walks within the fuel
budget and for arbitrary walks once a fixed point has been attained.
The unconditional finite stabilization bound is a separate obligation. -/
namespace ProctorReachabilityCompleteness
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc Routes routeFor relax sweep saturate reach arcs)

def Known (rs : Routes) (a : Literal) : Prop :=
  ∃ ps, routeFor a rs=some ps

def Extends (rs qs : Routes) : Prop :=
  ∀ a ps, routeFor a rs=some ps → routeFor a qs=some ps

theorem extends_refl (rs : Routes) : Extends rs rs :=
  fun _ _ h => h

theorem extends_trans (rs qs ts : Routes) (h : Extends rs qs) (k : Extends qs ts) :
    Extends rs ts :=
  fun a ps ha => k a ps (h a ps ha)

theorem known_mono (rs qs : Routes) (a : Literal)
    (h : Extends rs qs) (ha : Known rs a) : Known qs a := by
  obtain ⟨ps,hp⟩ := ha
  exact ⟨ps,h a ps hp⟩

theorem relax_extends (rs : Routes) (e : Arc) : Extends rs (relax rs e) := by
  unfold relax
  cases hs : routeFor e.1 rs with
  | none => exact extends_refl rs
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _qs => exact extends_refl rs
    | none =>
      intro a path hp
      change (if a=e.2 then some (ps++[e.2]) else routeFor a rs)=some path
      by_cases h : a=e.2
      · cases h
        rw [hd] at hp
        cases hp
      · rw [if_neg h]
        exact hp

theorem relax_reaches (rs : Routes) (e : Arc) (h : Known rs e.1) :
    Known (relax rs e) e.2 := by
  obtain ⟨ps,hp⟩ := h
  unfold relax
  rw [hp]
  cases hd : routeFor e.2 rs with
  | some qs => exact ⟨qs,hd⟩
  | none =>
    refine ⟨ps++[e.2],?_⟩
    change (if e.2=e.2 then some (ps++[e.2]) else routeFor e.2 rs)=_
    rw [if_pos rfl]

theorem sweep_extends (es : List Arc) (rs : Routes) :
    Extends rs (sweep es rs) := by
  induction es generalizing rs with
  | nil => exact extends_refl rs
  | cons e es ih =>
    change Extends rs (sweep es (relax rs e))
    exact extends_trans rs _ _ (relax_extends rs e) (ih _)

theorem sweep_reaches (es : List Arc) (rs : Routes) (e : Arc)
    (he : e∈es) (ha : Known rs e.1) :
    Known (sweep es rs) e.2 := by
  induction es generalizing rs with
  | nil => cases he
  | cons d ds ih =>
    change Known (sweep ds (relax rs d)) e.2
    cases he with
    | head =>
      exact known_mono _ _ _ (sweep_extends ds _) (relax_reaches rs e ha)
    | tail _ hm =>
      exact ih _ hm (known_mono _ _ _ (relax_extends rs d) ha)

theorem saturate_extends (es : List Arc) (fuel : Nat) (rs : Routes) :
    Extends rs (saturate es fuel rs) := by
  induction fuel generalizing rs with
  | zero => exact extends_refl rs
  | succ k ih =>
    exact extends_trans rs _ _ (sweep_extends es rs) (ih _)

inductive WalkN (es : List Arc) : Nat → Literal → Literal → Prop where
  | nil (a : Literal) : WalkN es 0 a a
  | cons {k : Nat} {a b c : Literal} :
      (a,b)∈es → WalkN es k b c → WalkN es (k+1) a c

theorem saturate_walk (es : List Arc) {k : Nat} {a b : Literal}
    (h : WalkN es k a b) (fuel : Nat) (hk : k≤fuel)
    (rs : Routes) (ha : Known rs a) : Known (saturate es fuel rs) b := by
  induction h generalizing fuel rs with
  | nil => exact known_mono _ _ _ (saturate_extends es fuel rs) ha
  | @cons k a c b he _ ih =>
    cases fuel with
    | zero => exact (Nat.not_succ_le_zero k hk).elim
    | succ fuel =>
      exact ih fuel (Nat.le_of_succ_le_succ hk) (sweep es rs)
        (sweep_reaches es rs (a,c) he ha)

theorem reach_bounded_complete (es : List Arc) (a b : Literal) (k : Nat)
    (h : WalkN es k a b) (hk : k≤es.length) :
    ∃ ps, reach es a b=some ps := by
  have h0 : Known [(a,[])] a := by
    refine ⟨[],?_⟩
    change (if a=a then some [] else none)=some []
    rw [if_pos rfl]
  exact saturate_walk es h es.length hk _ h0

def Closed (es : List Arc) (rs : Routes) : Prop :=
  ∀ e∈es, Known rs e.1 → Known rs e.2

theorem sweep_fixed_closed (es : List Arc) (rs : Routes)
    (h : sweep es rs=rs) : Closed es rs := by
  intro e he ha
  have hb := sweep_reaches es rs e he ha
  rw [h] at hb
  exact hb

theorem closed_walk (es : List Arc) (rs : Routes) {k : Nat} {a b : Literal}
    (h : WalkN es k a b) (hc : Closed es rs) (ha : Known rs a) :
    Known rs b := by
  induction h with
  | nil => exact ha
  | @cons k a c b he _ ih => exact ih (hc (a,c) he ha)

theorem saturate_fixed (es : List Arc) (rs : Routes) (fuel : Nat)
    (h : sweep es rs=rs) : saturate es fuel rs=rs := by
  induction fuel with
  | zero => rfl
  | succ k ih =>
    change saturate es k (sweep es rs)=rs
    rw [h,ih]

theorem reach_fixed_complete (es : List Arc) (a b : Literal) (k : Nat)
    (h : WalkN es k a b)
    (hf : sweep es (saturate es es.length [(a,[])])=
      saturate es es.length [(a,[])]) :
    ∃ ps, reach es a b=some ps := by
  have h0 : Known [(a,[])] a := by
    refine ⟨[],?_⟩
    change (if a=a then some [] else none)=some []
    rw [if_pos rfl]
  exact closed_walk es _ h (sweep_fixed_closed es _ hf)
    (known_mono _ _ _ (saturate_extends es es.length _) h0)

end ProctorReachabilityCompleteness

#print axioms ProctorReachabilityCompleteness.extends_refl
#print axioms ProctorReachabilityCompleteness.extends_trans
#print axioms ProctorReachabilityCompleteness.known_mono
#print axioms ProctorReachabilityCompleteness.relax_extends
#print axioms ProctorReachabilityCompleteness.relax_reaches
#print axioms ProctorReachabilityCompleteness.sweep_extends
#print axioms ProctorReachabilityCompleteness.sweep_reaches
#print axioms ProctorReachabilityCompleteness.saturate_extends
#print axioms ProctorReachabilityCompleteness.saturate_walk
#print axioms ProctorReachabilityCompleteness.reach_bounded_complete
#print axioms ProctorReachabilityCompleteness.sweep_fixed_closed
#print axioms ProctorReachabilityCompleteness.closed_walk
#print axioms ProctorReachabilityCompleteness.saturate_fixed
#print axioms ProctorReachabilityCompleteness.reach_fixed_complete
