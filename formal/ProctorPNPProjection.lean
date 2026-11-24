import Init

/-! Exact projection/lifting for PNP-B006. No general SAT runtime theorem. -/
namespace ProctorPNP

abbrev Pair := Bool × Bool
abbrev Domains := List (List Pair)
def gate (p : Pair) : Bool := p.1 && p.2

inductive Allowed : Domains → List Pair → Prop where
  | nil : Allowed [] []
  | cons {d : List Pair} {ds : Domains} {p : Pair} {ps : List Pair} :
      p ∈ d → Allowed ds ps → Allowed (d :: ds) (p :: ps)

inductive Projected : Domains → List Bool → Prop where
  | nil : Projected [] []
  | cons {d : List Pair} {ds : Domains} {y : Bool} {ys : List Bool} :
      y ∈ d.map gate → Projected ds ys → Projected (d :: ds) (y :: ys)

theorem project (ds : Domains) (ps : List Pair) (h : Allowed ds ps) :
    Projected ds (ps.map gate) := by
  induction h with
  | nil => exact Projected.nil
  | cons hp _ ih =>
    exact Projected.cons (List.mem_map_of_mem gate hp) ih

theorem lift (ds : Domains) (ys : List Bool) (h : Projected ds ys) :
    ∃ ps : List Pair, Allowed ds ps ∧ ps.map gate = ys := by
  induction h with
  | nil => exact ⟨[], Allowed.nil, rfl⟩
  | @cons d ds y ys hy _ ih =>
    obtain ⟨p, hp, heq⟩ := List.mem_map.mp hy
    obtain ⟨ps, hs, hout⟩ := ih
    exact ⟨p :: ps, Allowed.cons hp hs,
      congrArg₂ List.cons heq hout⟩

/-- Arbitrary output coupling, including the affine GF(2) system in B006. -/
theorem projection_iff (ds : Domains) (C : List Bool → Prop) :
    (∃ ps : List Pair, Allowed ds ps ∧ C (ps.map gate)) ↔
    (∃ ys : List Bool, Projected ds ys ∧ C ys) := by
  constructor
  · intro h
    obtain ⟨ps, ha, hc⟩ := h
    exact ⟨ps.map gate, project ds ps ha, hc⟩
  · intro h
    obtain ⟨ys, hp, hc⟩ := h
    obtain ⟨ps, ha, heq⟩ := lift ds ys hp
    exact ⟨ps, ha, heq.symm ▸ hc⟩

/-- Local singleton domains can be incompatible if a coordinate is shared. -/
def clashDomains : Domains := [[(true,false)], [(false,true)]]

theorem shared_projection : Projected clashDomains [false,false] :=
  Projected.cons (List.Mem.head _) (Projected.cons (List.Mem.head _) Projected.nil)

theorem shared_clash :
    ¬ (∃ a b c : Bool, (a,b) = (true,false) ∧ (a,c) = (false,true)) := by
  intro h
  obtain ⟨a,b,c,h1,h2⟩ := h
  have e1 : a = true := congrArg Prod.fst h1
  have e2 : a = false := congrArg Prod.fst h2
  exact Bool.noConfusion (e1.symm.trans e2)

end ProctorPNP
#print axioms ProctorPNP.project
#print axioms ProctorPNP.lift
#print axioms ProctorPNP.projection_iff
#print axioms ProctorPNP.shared_projection
#print axioms ProctorPNP.shared_clash
