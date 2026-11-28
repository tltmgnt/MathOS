import Mathlib

/-! Scoped semantic kernel for F038 RE-X. No claim of JS refinement or full SAT correctness. -/
namespace MathOS.F038

abbrev Assignment (n : Nat) := Fin n → Bool

def flipBit (b x : Bool) : Bool := if b then !x else x

@[simp] theorem flipBit_involutive (b x : Bool) :
    flipBit b (flipBit b x) = x := by
  cases b <;> cases x <;> rfl

def flip {n : Nat} (s x : Assignment n) : Assignment n :=
  fun i => flipBit (s i) (x i)

@[simp] theorem flip_involutive {n : Nat} (s x : Assignment n) :
    flip s (flip s x) = x := by
  funext i
  exact flipBit_involutive (s i) (x i)

structure Factor (n : Nat) where
  arity : Nat
  scope : Fin arity → Fin n
  allowed : (Fin arity → Bool) → Prop

def accepts {n : Nat} (f : Factor n) (x : Assignment n) : Prop :=
  f.allowed (fun j => x (f.scope j))

def normalizeFactor {n : Nat} (s : Assignment n) (f : Factor n) : Factor n :=
  { arity := f.arity
    scope := f.scope
    allowed := fun y => f.allowed (fun j => flipBit (s (f.scope j)) (y j)) }

theorem normalized_accepts {n : Nat} (s x : Assignment n) (f : Factor n) :
    accepts (normalizeFactor s f) (flip s x) ↔ accepts f x := by
  change f.allowed (fun j => flipBit (s (f.scope j))
    (flipBit (s (f.scope j)) (x (f.scope j)))) ↔
    f.allowed (fun j => x (f.scope j))
  simp only [flipBit_involutive]

def Models {n : Nat} (fs : List (Factor n)) (x : Assignment n) : Prop :=
  ∀ f ∈ fs, accepts f x

theorem normalized_models {n : Nat} (fs : List (Factor n)) (s x : Assignment n) :
    Models (fs.map (normalizeFactor s)) (flip s x) ↔ Models fs x := by
  constructor
  · intro h f hf
    exact (normalized_accepts s x f).mp (h _ (List.mem_map.mpr ⟨f, hf, rfl⟩))
  · intro h f hf
    obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hf
    exact (normalized_accepts s x g).mpr (h g hg)

structure Lit (n : Nat) where
  var : Fin n
  positive : Bool
  deriving DecidableEq

def neg {n : Nat} (l : Lit n) : Lit n := ⟨l.var, !l.positive⟩

def holds {n : Nat} (x : Assignment n) (l : Lit n) : Prop :=
  x l.var = l.positive

theorem neg_holds_iff {n : Nat} (x : Assignment n) (l : Lit n) :
    holds x (neg l) ↔ ¬ holds x l := by
  cases l with
  | mk i b =>
    cases b <;> cases h : x i <;> simp [holds, neg, h]

def SatClause {n : Nat} (x : Assignment n) (c : Set (Lit n)) : Prop :=
  ∃ l ∈ c, holds x l

def resolve {n : Nat} (a b : Set (Lit n)) (p : Lit n) : Set (Lit n) :=
  (a \ {p}) ∪ (b \ {neg p})

theorem resolution_sound {n : Nat} (x : Assignment n)
    (a b : Set (Lit n)) (p : Lit n)
    (ha : SatClause x a) (hb : SatClause x b) :
    SatClause x (resolve a b p) := by
  classical
  rcases ha with ⟨l, hl, ht⟩
  by_cases he : l = p
  · subst l
    rcases hb with ⟨q, hq, hqt⟩
    have hne : q ≠ neg p := by
      intro eq
      subst q
      exact (neg_holds_iff x p).mp hqt ht
    refine ⟨q, ?_, hqt⟩
    simp only [resolve, Set.mem_union, Set.mem_diff, Set.mem_singleton_iff]
    exact Or.inr ⟨hq, hne⟩
  · refine ⟨l, ?_, ht⟩
    simp only [resolve, Set.mem_union, Set.mem_diff, Set.mem_singleton_iff]
    exact Or.inl ⟨hl, he⟩

theorem binary_edge_sound {n : Nat} (x : Assignment n) (a b : Lit n)
    (clause : holds x (neg a) ∨ holds x b) (ha : holds x a) : holds x b := by
  rcases clause with hn | hb
  · exact False.elim ((neg_holds_iff x a).mp hn ha)
  · exact hb

inductive ImpPath {n : Nat} (edge : Lit n → Lit n → Prop) :
    Lit n → Lit n → Prop where
  | refl (a : Lit n) : ImpPath edge a a
  | step {a b c : Lit n} : edge a b → ImpPath edge b c → ImpPath edge a c

theorem path_sound {n : Nat} (x : Assignment n) (edge : Lit n → Lit n → Prop)
    (sound : ∀ a b, edge a b → holds x a → holds x b)
    {a b : Lit n} (p : ImpPath edge a b) : holds x a → holds x b := by
  induction p with
  | refl => exact id
  | step hab _ ih => intro ha; exact ih (sound _ _ hab ha)

theorem implied_exclusion_sound {n : Nat} (x : Assignment n)
    (edge : Lit n → Lit n → Prop)
    (sound : ∀ a b, edge a b → holds x a → holds x b)
    (a b : Lit n) (p : ImpPath edge a (neg b)) :
    ¬ (holds x a ∧ holds x b) := by
  intro h
  exact (neg_holds_iff x b).mp (path_sound x edge sound p h.1) h.2

/-- Every group has a selected true option assigned to a hole.
    Cross-group options sharing a hole are mutually exclusive. -/
theorem hall_deficiency_sound {n g h : Nat} (x : Assignment n)
    (groups : Fin g → Set (Lit n)) (hole : Lit n → Option (Fin h))
    (deficient : h < g)
    (covered : ∀ i, ∃ l, ∃ j, l ∈ groups i ∧ holds x l ∧ hole l = some j)
    (mutex : ∀ i j a b, i ≠ j → a ∈ groups i → b ∈ groups j →
      hole a = hole b → ¬ (holds x a ∧ holds x b)) : False := by
  classical
  choose pick slot hp using covered
  have inj : Function.Injective slot := by
    intro i j eq
    by_contra hne
    apply mutex i j (pick i) (pick j) hne (hp i).1 (hp j).1
    · rw [(hp i).2.2, (hp j).2.2, eq]
    · exact ⟨(hp i).2.1, (hp j).2.1⟩
  have bound := Fintype.card_le_of_injective slot inj
  simp only [Fintype.card_fin] at bound
  exact (Nat.not_le_of_gt deficient) bound

theorem unsat_transfers_from_relaxation {n : Nat}
    (original projected : List (Factor n))
    (preserve : ∀ x, Models original x → Models projected x)
    (unsat : ¬ ∃ x, Models projected x) : ¬ ∃ x, Models original x := by
  rintro ⟨x, hx⟩
  exact unsat ⟨x, preserve x hx⟩

#print axioms flip_involutive
#print axioms normalized_models
#print axioms resolution_sound
#print axioms path_sound
#print axioms implied_exclusion_sound
#print axioms hall_deficiency_sound
#print axioms unsat_transfers_from_relaxation

end MathOS.F038
