/-! F026: bag-interface join and path agreement kernel.
The join is semantic, not a formal refinement of Python's tree DP. -/
namespace ProctorTreeDecomposition

abbrev Assignment := Nat → Bool
abbrev Scope := Nat → Bool

def Agree (s : Scope) (x y : Assignment) : Prop :=
  ∀ v, s v = true → x v = y v

def Compatible (a b : Scope) (x y : Assignment) : Prop :=
  ∀ v, a v = true → b v = true → x v = y v

def Local (s : Scope) (P : Assignment → Prop) : Prop :=
  ∀ x y, Agree s x y → P x → P y

def merge (a : Scope) (x y : Assignment) : Assignment :=
  fun v => match a v with
    | true => x v
    | false => y v

theorem merge_left (a : Scope) (x y : Assignment) :
    Agree a x (merge a x y) := by
  intro v h
  unfold merge
  rw [h]

theorem merge_right (a b : Scope) (x y : Assignment)
    (h : Compatible a b x y) : Agree b y (merge a x y) := by
  intro v hb
  unfold merge
  cases e : a v with
  | false => rfl
  | true => exact (h v e hb).symm

theorem compatible_of_global (a b : Scope) (x y g : Assignment)
    (hx : Agree a x g) (hy : Agree b y g) :
    Compatible a b x y := by
  intro v ha hb
  exact (hx v ha).trans (hy v hb).symm

/-- The feasibility recurrence at one subtree join.
Each predicate may depend only on its own region; overlap must agree. -/
theorem join_iff (a b : Scope) (P Q : Assignment → Prop)
    (hp : Local a P) (hq : Local b Q) :
    (∃ g : Assignment, P g ∧ Q g) ↔
    (∃ x y : Assignment, P x ∧ Q y ∧ Compatible a b x y) := by
  constructor
  · intro h
    obtain ⟨g, pg, qg⟩ := h
    exact ⟨g, g, pg, qg, fun _ _ _ => rfl⟩
  · intro h
    obtain ⟨x, y, px, qy, hc⟩ := h
    exact ⟨merge a x y, hp x _ (merge_left a x y) px,
      hq y _ (merge_right a b x y hc) qy⟩

/-- If bags along a path all contain a coordinate, the edge checks
give a chain of equalities for that coordinate. -/
inductive PathAgreement (v : Nat) : Assignment → Assignment → Prop where
  | refl (x : Assignment) : PathAgreement v x x
  | step {x y z : Assignment} :
      x v = y v → PathAgreement v y z → PathAgreement v x z

theorem path_agrees (v : Nat) (x y : Assignment)
    (h : PathAgreement v x y) : x v = y v := by
  induction h with
  | refl _ => rfl
  | step e _ ih => exact e.trans ih

theorem join_with_boundary (a b s : Scope) (P Q : Assignment → Prop)
    (hp : Local a P) (hq : Local b Q)
    (hs : ∀ v, s v = true → a v = true) (sigma : Assignment) :
    (∃ g : Assignment, P g ∧ Q g ∧ Agree s sigma g) ↔
    (∃ x y : Assignment, P x ∧ Q y ∧ Compatible a b x y ∧
      Agree s sigma x) := by
  constructor
  · intro h
    obtain ⟨g, pg, qg, hg⟩ := h
    exact ⟨g, g, pg, qg, fun _ _ _ => rfl, hg⟩
  · intro h
    obtain ⟨x, y, px, qy, hc, hx⟩ := h
    refine ⟨merge a x y, hp x _ (merge_left a x y) px,
      hq y _ (merge_right a b x y hc) qy, ?_⟩
    intro v hv
    exact (hx v hv).trans (merge_left a x y v (hs v hv))

end ProctorTreeDecomposition
#print axioms ProctorTreeDecomposition.merge_left
#print axioms ProctorTreeDecomposition.merge_right
#print axioms ProctorTreeDecomposition.compatible_of_global
#print axioms ProctorTreeDecomposition.join_iff
#print axioms ProctorTreeDecomposition.path_agrees
#print axioms ProctorTreeDecomposition.join_with_boundary
