import Init

/-! F033: constructive finite counting and CNF Hall-certificate soundness.
The finite demand list, disjointness, group ownership, coverage and
original-clause premises are supplied. No Python refinement claim. -/
namespace ProctorHallDeficiency

/-- A finite injection into a bounded set cannot increase cardinality.
Remove the image of the last domain point by swapping it with the
last codomain point. No classical choice or finite-set axiom. -/
theorem bounded_injection (d k : Nat) (f : Nat → Nat)
    (bound : ∀ i, i < d → f i < k)
    (inj : ∀ i j, i < d → j < d → f i = f j → i = j) :
    d ≤ k := by
  induction k generalizing d f with
  | zero =>
    cases d with
    | zero => exact Nat.le_refl 0
    | succ d =>
      exact (Nat.not_lt_zero (f 0) (bound 0 (Nat.zero_lt_succ d))).elim
  | succ k ih =>
    cases d with
    | zero => exact Nat.zero_le _
    | succ d =>
      have hd : d < d+1 := Nat.lt_succ_self d
      have neLast : ∀ i, i < d → f i ≠ f d := by
        intro i hi e
        exact (Nat.ne_of_lt hi) (inj i d (Nat.lt_trans hi hd) hd e)
      let g : Nat → Nat := fun i => if f i = k then f d else f i
      have gb : ∀ i, i < d → g i < k := by
        intro i hi
        change (if f i = k then f d else f i) < k
        by_cases e : f i = k
        · rw [if_pos e]
          exact Nat.lt_of_le_of_ne (Nat.le_of_lt_succ (bound d hd))
            (fun h => neLast i hi (e.trans h.symm))
        · rw [if_neg e]
          exact Nat.lt_of_le_of_ne (Nat.le_of_lt_succ (bound i (Nat.lt_trans hi hd))) e
      have gi : ∀ i j, i < d → j < d → g i = g j → i = j := by
        intro i j hi hj e
        change (if f i = k then f d else f i) =
          (if f j = k then f d else f j) at e
        by_cases ei : f i = k
        · by_cases ej : f j = k
          · exact inj i j (Nat.lt_trans hi hd) (Nat.lt_trans hj hd) (ei.trans ej.symm)
          · rw [if_pos ei, if_neg ej] at e
            exact (neLast j hj e.symm).elim
        · by_cases ej : f j = k
          · rw [if_neg ei, if_pos ej] at e
            exact (neLast i hi e).elim
          · rw [if_neg ei, if_neg ej] at e
            exact inj i j (Nat.lt_trans hi hd) (Nat.lt_trans hj hd) e
      exact Nat.succ_le_succ (ih d g gb gi)

abbrev Assignment := Nat → Bool
abbrev Demands := Nat → List Nat

def DemandSat (demands : Demands) (d : Nat) (x : Assignment) : Prop :=
  ∀ i, i < d → ∃ v, v ∈ demands i ∧ x v = true

def DisjointDemands (demands : Demands) (d : Nat) : Prop :=
  ∀ i j, i < d → j < d → ∀ v, v ∈ demands i → v ∈ demands j → i = j

def Covered (demands : Demands) (d k : Nat) (owner : Nat → Nat) : Prop :=
  ∀ i, i < d → ∀ v, v ∈ demands i → owner v < k

def Capacity (demands : Demands) (d : Nat) (owner : Nat → Nat)
    (x : Assignment) : Prop :=
  ∀ i j, i < d → j < d → ∀ v w,
    v ∈ demands i → w ∈ demands j → owner v = owner w →
    x v = true → x w = true → v = w

/-- Constructively choose a true variable in each of finitely many demands. -/
theorem finite_demand_choices (demands : Demands) (d : Nat) (x : Assignment)
    (h : DemandSat demands d x) :
    ∃ f : Nat → Nat, ∀ i, i < d → f i ∈ demands i ∧ x (f i) = true := by
  induction d with
  | zero =>
    refine ⟨fun _ => 0, ?_⟩
    intro i hi
    exact (Nat.not_lt_zero i hi).elim
  | succ d ih =>
    obtain ⟨f, hf⟩ := ih (fun i hi => h i (Nat.lt_trans hi (Nat.lt_succ_self d)))
    obtain ⟨v, hv, ht⟩ := h d (Nat.lt_succ_self d)
    refine ⟨fun i => if i = d then v else f i, ?_⟩
    intro i hi
    change (if i = d then v else f i) ∈ demands i ∧
      x (if i = d then v else f i) = true
    by_cases e : i = d
    · cases e
      rw [if_pos rfl]
      exact ⟨hv,ht⟩
    · rw [if_neg e]
      exact hf i (Nat.lt_of_le_of_ne (Nat.le_of_lt_succ hi) e)

/-- Distinct demands must use distinct capacity groups. -/
theorem capacity_injection (demands : Demands) (d : Nat)
    (owner : Nat → Nat) (x : Assignment) (f : Nat → Nat)
    (disjoint : DisjointDemands demands d)
    (capacity : Capacity demands d owner x)
    (selected : ∀ i, i < d → f i ∈ demands i ∧ x (f i) = true) :
    ∀ i j, i < d → j < d → owner (f i) = owner (f j) → i = j := by
  intro i j hi hj e
  have eq := capacity i j hi hj (f i) (f j)
    (selected i hi).left (selected j hj).left e
    (selected i hi).right (selected j hj).right
  exact disjoint i j hi hj (f i) (selected i hi).left
    (eq.symm ▸ (selected j hj).left)

theorem hall_deficiency (demands : Demands) (d k : Nat)
    (owner : Nat → Nat) (disjoint : DisjointDemands demands d)
    (covered : Covered demands d k owner) (deficient : k < d) :
    ¬ ∃ x : Assignment, DemandSat demands d x ∧ Capacity demands d owner x := by
  intro h
  obtain ⟨x, hs, hc⟩ := h
  obtain ⟨f, hf⟩ := finite_demand_choices demands d x hs
  have le := bounded_injection d k (fun i => owner (f i))
    (fun i hi => covered i hi (f i) (hf i hi).left)
    (capacity_injection demands d owner x f disjoint hc hf)
  exact Nat.not_lt_of_ge le deficient

abbrev Literal := Nat × Bool
abbrev Clause := List Literal
abbrev Formula := List Clause

def ClauseSat (c : Clause) (x : Assignment) : Prop :=
  ∃ l ∈ c, x l.1 = l.2

def FormulaSat (formula : Formula) (x : Assignment) : Prop :=
  ∀ c ∈ formula, ClauseSat c x

def positiveClause (vs : List Nat) : Clause :=
  vs.map (fun v => (v,true))

theorem positive_clause_demand (vs : List Nat) (x : Assignment)
    (h : ClauseSat (positiveClause vs) x) :
    ∃ v, v ∈ vs ∧ x v = true := by
  obtain ⟨l, hl, ht⟩ := h
  change l ∈ vs.map (fun v => (v,true)) at hl
  obtain ⟨v, hv, he⟩ := List.mem_map.mp hl
  rw [← he] at ht
  exact ⟨v,hv,ht⟩

theorem negative_pair_capacity (a b : Nat) (x : Assignment)
    (h : ClauseSat [(a,false),(b,false)] x) :
    ¬ (x a = true ∧ x b = true) := by
  intro hh
  obtain ⟨l, hl, ht⟩ := h
  cases hl with
  | head => exact Bool.noConfusion (hh.left.symm.trans ht)
  | tail _ hm =>
    cases hm with
    | head => exact Bool.noConfusion (hh.right.symm.trans ht)
    | tail _ hn => cases hn

/-- Original normalized positive demands and negative pair clauses imply
UNSAT when their supplied group certificate is deficient. Either order of
a negative pair is allowed. Additional formula clauses are unrestricted. -/
theorem hall_cnf_unsat (formula : Formula) (demands : Demands) (d k : Nat)
    (owner : Nat → Nat) (disjoint : DisjointDemands demands d)
    (covered : Covered demands d k owner) (deficient : k < d)
    (demand_present : ∀ i, i < d → positiveClause (demands i) ∈ formula)
    (conflict_present : ∀ i j, i < d → j < d → ∀ v w,
      v ∈ demands i → w ∈ demands j → owner v = owner w → v ≠ w →
      [(v,false),(w,false)] ∈ formula ∨ [(w,false),(v,false)] ∈ formula) :
    ¬ ∃ x : Assignment, FormulaSat formula x := by
  intro h
  obtain ⟨x,hx⟩ := h
  apply hall_deficiency demands d k owner disjoint covered deficient
  refine ⟨x, ?_, ?_⟩
  · intro i hi
    exact positive_clause_demand (demands i) x
      (hx _ (demand_present i hi))
  · intro i j hi hj v w hv hw eq ht hs
    by_cases e : v = w
    · exact e
    · cases conflict_present i j hi hj v w hv hw eq e with
      | inl hc => exact (negative_pair_capacity v w x (hx _ hc) ⟨ht,hs⟩).elim
      | inr hc => exact (negative_pair_capacity w v x (hx _ hc) ⟨hs,ht⟩).elim

end ProctorHallDeficiency
#print axioms ProctorHallDeficiency.bounded_injection
#print axioms ProctorHallDeficiency.finite_demand_choices
#print axioms ProctorHallDeficiency.capacity_injection
#print axioms ProctorHallDeficiency.hall_deficiency
#print axioms ProctorHallDeficiency.positive_clause_demand
#print axioms ProctorHallDeficiency.negative_pair_capacity
#print axioms ProctorHallDeficiency.hall_cnf_unsat
