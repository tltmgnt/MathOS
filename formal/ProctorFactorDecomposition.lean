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

end ProctorFactorDecomposition
#print axioms ProctorFactorDecomposition.assemble_shared
#print axioms ProctorFactorDecomposition.assemble_local
#print axioms ProctorFactorDecomposition.clause_agrees
#print axioms ProctorFactorDecomposition.separator_forward
#print axioms ProctorFactorDecomposition.separator_backward
#print axioms ProctorFactorDecomposition.separator_iff
#print axioms ProctorFactorDecomposition.component_iff
