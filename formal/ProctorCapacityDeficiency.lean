/-! F033: signed capacity certificates, with arbitrary finite capacities.
Replay after the unchanged ProctorHallDeficiency.lean source.
The finite groups and original-clause evidence are supplied, not discovered.
-/
namespace ProctorCapacityDeficiency

abbrev Literal := ProctorHallDeficiency.Literal
abbrev Assignment := ProctorHallDeficiency.Assignment
abbrev Clause := ProctorHallDeficiency.Clause
abbrev Formula := ProctorHallDeficiency.Formula

def Holds (x : Assignment) (l : Literal) : Prop := x l.1 = l.2

def opposite (l : Literal) : Literal := (l.1, !l.2)

inductive Distinct : List Literal → Prop where
  | nil : Distinct []
  | cons {a : Literal} {as : List Literal} :
      (a ∈ as → False) → Distinct as → Distinct (a::as)

def truths (x : Assignment) : List Literal → List Literal
  | [] => []
  | a::as => if x a.1 = a.2 then a :: truths x as else truths x as

theorem truths_mem (x : Assignment) (xs : List Literal) (l : Literal) :
    l ∈ truths x xs ↔ l ∈ xs ∧ Holds x l := by
  induction xs with
  | nil =>
    constructor
    · intro h
      cases h
    · intro h
      cases h.left
  | cons a as ih =>
    change (l ∈ (if x a.1 = a.2 then a :: truths x as else truths x as)) ↔
      (l ∈ a::as ∧ Holds x l)
    by_cases e : x a.1 = a.2
    · rw [if_pos e]
      constructor
      · intro h
        cases h with
        | head => exact ⟨List.Mem.head _, e⟩
        | tail _ hm =>
          exact ⟨List.Mem.tail _ (ih.mp hm).left, (ih.mp hm).right⟩
      · intro h
        cases h.left with
        | head => exact List.Mem.head _
        | tail _ hm => exact List.Mem.tail _ (ih.mpr ⟨hm,h.right⟩)
    · rw [if_neg e]
      constructor
      · intro h
        exact ⟨List.Mem.tail _ (ih.mp h).left, (ih.mp h).right⟩
      · intro h
        cases h.left with
        | head => exact (e h.right).elim
        | tail _ hm => exact ih.mpr ⟨hm,h.right⟩

theorem truths_distinct (x : Assignment) (xs : List Literal)
    (h : Distinct xs) : Distinct (truths x xs) := by
  induction h with
  | nil => exact Distinct.nil
  | @cons a as hn hd ih =>
    change Distinct (if x a.1 = a.2 then a :: truths x as else truths x as)
    by_cases e : x a.1 = a.2
    · rw [if_pos e]
      exact Distinct.cons (fun hm => hn ((truths_mem x as a).mp hm).left) ih
    · rw [if_neg e]
      exact ih

/-- Construct a distinct prefix of any requested feasible length. -/
theorem distinct_prefix (xs : List Literal) (k : Nat)
    (hd : Distinct xs) (hk : k ≤ xs.length) :
    ∃ ys : List Literal, ys.length = k ∧ Distinct ys ∧
      (∀ l, l ∈ ys → l ∈ xs) := by
  induction k generalizing xs with
  | zero =>
    refine ⟨[], rfl, Distinct.nil, ?_⟩
    intro l hm
    cases hm
  | succ k ih =>
    cases xs with
    | nil =>
      exact (Nat.not_lt_zero k hk).elim
    | cons a as =>
      cases hd with
      | cons hn hd =>
        obtain ⟨ys,hy,hdy,sub⟩ := ih as hd (Nat.le_of_succ_le_succ hk)
        refine ⟨a::ys, congrArg Nat.succ hy, Distinct.cons (fun hm => hn (sub a hm)) hdy, ?_⟩
        intro l hm
        cases hm with
        | head => exact List.Mem.head _
        | tail _ ht => exact List.Mem.tail _ (sub l ht)

theorem opposite_conflict (x : Assignment) (l : Literal)
    (h : Holds x l) (hn : Holds x (opposite l)) : False := by
  cases l with
  | mk v b =>
    cases b with
    | false => exact Bool.noConfusion (h.symm.trans hn)
    | true => exact Bool.noConfusion (h.symm.trans hn)

structure Group where
  literals : List Literal
  cap : Nat

/-- A complementary clause for every distinct (cap+1)-subset.
The clause can use a subset of those complements, in any order and
with repetitions; this permits sound transport of set-normalized refs. -/
def ConflictEvidence (formula : Formula) (g : Group) : Prop :=
  ∀ ys : List Literal, ys.length = g.cap+1 → Distinct ys →
    (∀ l, l ∈ ys → l ∈ g.literals) →
    ∃ c ∈ formula, ∀ l ∈ c, ∃ p ∈ ys, l = opposite p

theorem group_bound (formula : Formula) (g : Group) (x : Assignment)
    (model : ProctorHallDeficiency.FormulaSat formula x)
    (distinct : Distinct g.literals)
    (evidence : ConflictEvidence formula g) :
    (truths x g.literals).length ≤ g.cap := by
  by_cases h : (truths x g.literals).length ≤ g.cap
  · exact h
  · have bigger : g.cap+1 ≤ (truths x g.literals).length := Nat.lt_of_not_ge h
    obtain ⟨ys,hy,hdy,sub⟩ := distinct_prefix (truths x g.literals) (g.cap+1)
      (truths_distinct x g.literals distinct) bigger
    obtain ⟨c,hc,complements⟩ := evidence ys hy hdy
      (fun l hl => ((truths_mem x g.literals l).mp (sub l hl)).left)
    obtain ⟨l,hl,ht⟩ := model c hc
    obtain ⟨p,hp,he⟩ := complements l hl
    have hptrue := ((truths_mem x g.literals p).mp (sub p hp)).right
    cases he
    exact (opposite_conflict x p hptrue ht).elim

def totalCapacity : List Group → Nat
  | [] => 0
  | g::gs => g.cap + totalCapacity gs

def allTruths (x : Assignment) : List Group → List Literal
  | [] => []
  | g::gs => truths x g.literals ++ allTruths x gs

theorem length_append_local (as bs : List Literal) :
    (as ++ bs).length = as.length + bs.length := by
  induction as with
  | nil => exact (Nat.zero_add bs.length).symm
  | cons a as ih =>
    change Nat.succ ((as ++ bs).length) = Nat.succ as.length + bs.length
    rw [ih, Nat.succ_add]

theorem mem_append_left_local (as bs : List Literal) (l : Literal)
    (h : l ∈ as) : l ∈ as ++ bs := by
  induction as with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

theorem mem_append_right_local (as bs : List Literal) (l : Literal)
    (h : l ∈ bs) : l ∈ as ++ bs := by
  induction as with
  | nil => exact h
  | cons a as ih => exact List.Mem.tail _ ih

theorem total_bound (gs : List Group) (x : Assignment)
    (h : ∀ g ∈ gs, (truths x g.literals).length ≤ g.cap) :
    (allTruths x gs).length ≤ totalCapacity gs := by
  induction gs with
  | nil => exact Nat.le_refl 0
  | cons g gs ih =>
    change (truths x g.literals ++ allTruths x gs).length ≤
      g.cap + totalCapacity gs
    rw [length_append_local]
    exact Nat.add_le_add (h g (List.Mem.head _))
      (ih (fun q hq => h q (List.Mem.tail _ hq)))

theorem covered_truth (gs : List Group) (x : Assignment) (g : Group)
    (hg : g ∈ gs) (l : Literal) (hl : l ∈ g.literals)
    (ht : Holds x l) : l ∈ allTruths x gs := by
  induction gs with
  | nil => cases hg
  | cons a as ih =>
    cases hg with
    | head =>
      exact mem_append_left_local (truths x g.literals) (allTruths x as) l
        ((truths_mem x g.literals l).mpr ⟨hl,ht⟩)
    | tail _ hm =>
      exact mem_append_right_local (truths x a.literals) (allTruths x as) l (ih hm)

theorem finite_choices (demands : Nat → Clause) (d : Nat) (x : Assignment)
    (h : ∀ i, i < d → ProctorHallDeficiency.ClauseSat (demands i) x) :
    ∃ f : Nat → Literal, ∀ i, i < d → f i ∈ demands i ∧ Holds x (f i) := by
  induction d with
  | zero =>
    refine ⟨fun _ => (0,false), ?_⟩
    intro i hi
    exact (Nat.not_lt_zero i hi).elim
  | succ d ih =>
    obtain ⟨f,hf⟩ := ih (fun i hi => h i (Nat.lt_trans hi (Nat.lt_succ_self d)))
    obtain ⟨l,hl,ht⟩ := h d (Nat.lt_succ_self d)
    refine ⟨fun i => if i=d then l else f i, ?_⟩
    intro i hi
    change (if i=d then l else f i) ∈ demands i ∧ Holds x (if i=d then l else f i)
    by_cases e : i=d
    · cases e
      rw [if_pos rfl]
      exact ⟨hl,ht⟩
    · rw [if_neg e]
      exact hf i (Nat.lt_of_le_of_ne (Nat.le_of_lt_succ hi) e)

def locate (l : Literal) : List Literal → Nat
  | [] => 0
  | a::as => if l=a then 0 else Nat.succ (locate l as)

theorem locate_bound (l : Literal) (xs : List Literal) (h : l ∈ xs) :
    locate l xs < xs.length := by
  induction xs with
  | nil => cases h
  | cons a as ih =>
    change (if l=a then 0 else Nat.succ (locate l as)) < Nat.succ as.length
    by_cases e : l=a
    · rw [if_pos e]
      exact Nat.zero_lt_succ _
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact Nat.succ_lt_succ (ih hm)

theorem locate_injective (xs : List Literal) (a b : Literal)
    (ha : locate a xs < xs.length) (hb : locate b xs < xs.length)
    (e : locate a xs = locate b xs) : a=b := by
  induction xs with
  | nil => exact (Nat.not_lt_zero _ ha).elim
  | cons l ls ih =>
    change (if a=l then 0 else Nat.succ (locate a ls)) < Nat.succ ls.length at ha
    change (if b=l then 0 else Nat.succ (locate b ls)) < Nat.succ ls.length at hb
    change (if a=l then 0 else Nat.succ (locate a ls)) =
      (if b=l then 0 else Nat.succ (locate b ls)) at e
    by_cases ea : a=l
    · by_cases eb : b=l
      · exact ea.trans eb.symm
      · rw [if_pos ea, if_neg eb] at e
        exact (Nat.noConfusion e)
    · by_cases eb : b=l
      · rw [if_neg ea, if_pos eb] at e
        exact (Nat.noConfusion e)
      · rw [if_neg ea] at ha
        rw [if_neg eb] at hb
        rw [if_neg ea, if_neg eb] at e
        exact ih (Nat.lt_of_succ_lt_succ ha) (Nat.lt_of_succ_lt_succ hb) (Nat.succ.inj e)

/-- Arbitrary mixed finite capacities and signed demands. Group
disjointness is not needed for this sufficient contradiction:
overcounting capacity slots only weakens the bound. -/
theorem capacity_cnf_unsat (formula : Formula) (demands : Nat → Clause)
    (d : Nat) (gs : List Group)
    (disjoint : ∀ i j, i < d → j < d → ∀ a ∈ demands i, ∀ b ∈ demands j,
      a.1 = b.1 → i=j)
    (covered : ∀ i, i < d → ∀ l ∈ demands i, ∃ g ∈ gs, l ∈ g.literals)
    (distinct : ∀ g ∈ gs, Distinct g.literals)
    (evidence : ∀ g ∈ gs, ConflictEvidence formula g)
    (present : ∀ i, i < d → demands i ∈ formula)
    (deficient : totalCapacity gs < d) :
    ¬ ∃ x : Assignment, ProctorHallDeficiency.FormulaSat formula x := by
  intro h
  obtain ⟨x,hx⟩ := h
  obtain ⟨f,hf⟩ := finite_choices demands d x (fun i hi => hx _ (present i hi))
  have bound := total_bound gs x (fun g hg => group_bound formula g x hx (distinct g hg) (evidence g hg))
  have mem : ∀ i, i < d → f i ∈ allTruths x gs := by
    intro i hi
    obtain ⟨g,hg,hl⟩ := covered i hi (f i) (hf i hi).left
    exact covered_truth gs x g hg (f i) hl (hf i hi).right
  have le := ProctorHallDeficiency.bounded_injection d (allTruths x gs).length
    (fun i => locate (f i) (allTruths x gs))
    (fun i hi => locate_bound (f i) (allTruths x gs) (mem i hi))
    (by
      intro i j hi hj e
      have same := locate_injective (allTruths x gs) (f i) (f j)
        (locate_bound (f i) _ (mem i hi)) (locate_bound (f j) _ (mem j hj)) e
      exact disjoint i j hi hj (f i) (hf i hi).left (f j) (hf j hj).left
        (congrArg Prod.fst same))
  exact Nat.not_lt_of_ge (Nat.le_trans le bound) deficient

end ProctorCapacityDeficiency

#print axioms ProctorCapacityDeficiency.truths_mem
#print axioms ProctorCapacityDeficiency.truths_distinct
#print axioms ProctorCapacityDeficiency.distinct_prefix
#print axioms ProctorCapacityDeficiency.opposite_conflict
#print axioms ProctorCapacityDeficiency.group_bound
#print axioms ProctorCapacityDeficiency.length_append_local
#print axioms ProctorCapacityDeficiency.mem_append_left_local
#print axioms ProctorCapacityDeficiency.mem_append_right_local
#print axioms ProctorCapacityDeficiency.total_bound
#print axioms ProctorCapacityDeficiency.covered_truth
#print axioms ProctorCapacityDeficiency.finite_choices
#print axioms ProctorCapacityDeficiency.locate_bound
#print axioms ProctorCapacityDeficiency.locate_injective
#print axioms ProctorCapacityDeficiency.capacity_cnf_unsat
