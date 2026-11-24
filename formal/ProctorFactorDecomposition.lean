/-! F025: exact separator-conditioned gluing for Boolean constraints.
A clause's nonseparator variables must belong to its assigned component.
No claim of a universally small separator or polynomial unrestricted SAT. -/
namespace ProctorFactorDecomposition

abbrev Assignment := Nat → Bool
abbrev Family := Nat → Assignment

structure Literal where
  varId : Nat
  positive : Bool

def Literal.holds (l : Literal) (x : Assignment) : Prop :=
  x l.varId = l.positive

abbrev Clause := List Literal
def Clause.holds (c : Clause) (x : Assignment) : Prop :=
  ∃ l : Literal, l ∈ c ∧ Literal.holds l x

def localView (shared : Nat → Bool) (sigma : Assignment)
    (locals : Family) (j : Nat) : Assignment :=
  fun v => if shared v then sigma v else locals j v

def assemble (shared : Nat → Bool) (sigma : Assignment)
    (owner : Nat → Nat) (locals : Family) : Assignment :=
  fun v => if shared v then sigma v else locals (owner v) v

theorem assemble_shared (shared : Nat → Bool) (sigma : Assignment)
    (owner : Nat → Nat) (locals : Family) (v : Nat)
    (h : shared v = true) :
    assemble shared sigma owner locals v = sigma v := by
  unfold assemble
  rw [h] <;> rfl

theorem assemble_local (shared : Nat → Bool) (sigma : Assignment)
    (owner : Nat → Nat) (locals : Family) (j v : Nat)
    (h : shared v = true ∨ owner v = j) :
    assemble shared sigma owner locals v = localView shared sigma locals j v := by
  cases h with
  | inl hs =>
    unfold assemble localView
    rw [hs] <;> rfl
  | inr ho =>
    unfold assemble localView
    rw [ho] <;> rfl

theorem clause_agrees (c : Clause) (x y : Assignment)
    (h : ∀ l ∈ c, x l.varId = y l.varId) :
    Clause.holds c x ↔ Clause.holds c y := by
  constructor
  · intro hx
    unfold Clause.holds at hx ⊢
    obtain ⟨l, hl, ht⟩ := hx
    change x l.varId = l.positive at ht
    exact ⟨l, hl, (h l hl).symm.trans ht⟩
  · intro hy
    unfold Clause.holds at hy ⊢
    obtain ⟨l, hl, ht⟩ := hy
    change y l.varId = l.positive at ht
    exact ⟨l, hl, (h l hl).trans ht⟩

-- The labels are a certificate of separation. Each original clause is
-- indexed by i, and all its nonseparator variables have one owner.
def ValidPartition (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (owner component : Nat → Nat) : Prop :=
  ∀ i, i < m → ∀ l ∈ clauses i,
    shared l.varId = true ∨ owner l.varId = component i

def GlobalSat (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (sigma : Assignment) : Prop :=
  ∃ x : Assignment,
    (∀ v, shared v = true → x v = sigma v) ∧
    ∀ i, i < m → Clause.holds (clauses i) x

def LocalSat (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (sigma : Assignment)
    (component : Nat → Nat) : Prop :=
  ∃ locals : Family, ∀ i, i < m →
    Clause.holds (clauses i) (localView shared sigma locals (component i))

theorem separator_forward (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (sigma : Assignment) (component : Nat → Nat)
    (h : GlobalSat clauses m shared sigma) :
    LocalSat clauses m shared sigma component := by
  obtain ⟨x, hs, hc⟩ := h
  refine ⟨fun _ => x, ?_⟩
  intro i hi
  apply (clause_agrees (clauses i) x _ ?_).mp (hc i hi)
  intro l _
  unfold localView
  cases e : shared l.varId with
  | false => rfl
  | true => exact hs l.varId e

theorem separator_backward (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (sigma : Assignment)
    (owner component : Nat → Nat)
    (valid : ValidPartition clauses m shared owner component)
    (h : LocalSat clauses m shared sigma component) :
    GlobalSat clauses m shared sigma := by
  obtain ⟨locals, hc⟩ := h
  refine ⟨assemble shared sigma owner locals, ?_, ?_⟩
  · intro v hv
    exact assemble_shared shared sigma owner locals v hv
  · intro i hi
    apply (clause_agrees (clauses i) _ _ ?_).mpr (hc i hi)
    intro l hl
    exact assemble_local shared sigma owner locals (component i) l.varId
      (valid i hi l hl)

theorem separator_iff (clauses : Nat → Clause) (m : Nat)
    (shared : Nat → Bool) (sigma : Assignment)
    (owner component : Nat → Nat)
    (valid : ValidPartition clauses m shared owner component) :
    GlobalSat clauses m shared sigma ↔ LocalSat clauses m shared sigma component :=
  ⟨separator_forward clauses m shared sigma component,
   separator_backward clauses m shared sigma owner component valid⟩

theorem component_iff (clauses : Nat → Clause) (m : Nat)
    (owner component : Nat → Nat)
    (valid : ValidPartition clauses m (fun _ => false) owner component) :
    GlobalSat clauses m (fun _ => false) (fun _ => false) ↔
    LocalSat clauses m (fun _ => false) (fun _ => false) component :=
  separator_iff clauses m (fun _ => false) (fun _ => false) owner component valid

-- F031: explicit witnesses for finitely many disconnected components.
-- The partition is supplied; no claim about construction or search cost.
def ComponentSat (clauses : Nat → Clause) (m : Nat)
    (component : Nat → Nat) (j : Nat) : Prop :=
  ∃ x : Assignment, ∀ i, i < m → component i = j →
    Clause.holds (clauses i) x

theorem finite_component_witnesses (clauses : Nat → Clause) (m : Nat)
    (component : Nat → Nat) (k : Nat)
    (h : ∀ j, j < k → ComponentSat clauses m component j) :
    ∃ locals : Family, ∀ j, j < k → ∀ i, i < m →
      component i = j → Clause.holds (clauses i) (locals j) := by
  induction k with
  | zero =>
    refine ⟨fun _ _ => false, ?_⟩
    intro j hj
    exact (Nat.not_lt_zero j hj).elim
  | succ k ih =>
    obtain ⟨locals, hl⟩ := ih (fun j hj => h j (Nat.lt_trans hj (Nat.lt_succ_self k)))
    obtain ⟨x, hx⟩ := h k (Nat.lt_succ_self k)
    refine ⟨fun j => if j = k then x else locals j, ?_⟩
    intro j hj i hi hc
    change Clause.holds (clauses i) (if j = k then x else locals j)
    by_cases e : j = k
    · rw [if_pos e]
      exact hx i hi (hc.trans e)
    · rw [if_neg e]
      exact hl j (Nat.lt_of_le_of_ne (Nat.le_of_lt_succ hj) e) i hi hc

theorem component_witness_union (clauses : Nat → Clause) (m : Nat)
    (owner component : Nat → Nat) (locals : Family)
    (valid : ValidPartition clauses m (fun _ => false) owner component)
    (h : ∀ i, i < m → Clause.holds (clauses i) (locals (component i))) :
    ∀ i, i < m → Clause.holds (clauses i) (fun v => locals (owner v) v) := by
  intro i hi
  apply (clause_agrees (clauses i) _ _ ?_).mpr (h i hi)
  intro l hl
  cases valid i hi l hl with
  | inl hf => contradiction
  | inr ho => rw [ho]

theorem finite_component_iff (clauses : Nat → Clause) (m k : Nat)
    (owner component : Nat → Nat)
    (valid : ValidPartition clauses m (fun _ => false) owner component)
    (bounded : ∀ i, i < m → component i < k) :
    (∃ x : Assignment, ∀ i, i < m → Clause.holds (clauses i) x) ↔
      ∀ j, j < k → ComponentSat clauses m component j := by
  constructor
  · intro hg j _
    obtain ⟨x, hx⟩ := hg
    exact ⟨x, fun i hi _ => hx i hi⟩
  · intro h
    obtain ⟨locals, hl⟩ := finite_component_witnesses clauses m component k h
    exact ⟨fun v => locals (owner v) v,
      component_witness_union clauses m owner component locals valid
        (fun i hi => hl (component i) (bounded i hi) i hi rfl)⟩

-- UNSAT lifting needs neither disjointness nor bounded labels: a model
-- of the full conjunction would be a model of each sub-conjunction.
theorem component_unsat_lifts (clauses : Nat → Clause) (m : Nat)
    (component : Nat → Nat) (j : Nat)
    (h : ¬ ComponentSat clauses m component j) :
    ¬ ∃ x : Assignment, ∀ i, i < m → Clause.holds (clauses i) x := by
  intro hg
  obtain ⟨x, hx⟩ := hg
  exact h ⟨x, fun i hi _ => hx i hi⟩

end ProctorFactorDecomposition
#print axioms ProctorFactorDecomposition.assemble_shared
#print axioms ProctorFactorDecomposition.assemble_local
#print axioms ProctorFactorDecomposition.clause_agrees
#print axioms ProctorFactorDecomposition.separator_forward
#print axioms ProctorFactorDecomposition.separator_backward
#print axioms ProctorFactorDecomposition.separator_iff
#print axioms ProctorFactorDecomposition.component_iff
#print axioms ProctorFactorDecomposition.finite_component_witnesses
#print axioms ProctorFactorDecomposition.component_witness_union
#print axioms ProctorFactorDecomposition.finite_component_iff
#print axioms ProctorFactorDecomposition.component_unsat_lifts
