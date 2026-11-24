/-! F032 local CNF parity and exact existential elimination semantics.
Replay appended to the unchanged ProctorGF2.lean source.
These statements do not refine the Python implementation or its cost. -/
namespace ProctorParityElimination

theorem resolution_sound (v a b : Bool)
    (hp : (v || a) = true) (hn : (!v || b) = true) :
    (a || b) = true := by
  cases v <;> cases a <;> cases b <;> first | rfl | contradiction

theorem all_true_or_false_member (xs : List Bool) :
    (∀ x ∈ xs, x = true) ∨ (∃ x ∈ xs, x = false) := by
  induction xs with
  | nil =>
    apply Or.inl
    intro x hx
    cases hx
  | cons a as ih =>
    cases a with
    | false => exact Or.inr ⟨false, List.Mem.head _, rfl⟩
    | true =>
      cases ih with
      | inl h =>
        apply Or.inl
        intro x hx
        cases hx with
        | head => rfl
        | tail _ hm => exact h _ hm
      | inr h =>
        obtain ⟨x, hx, he⟩ := h
        exact Or.inr ⟨x, List.Mem.tail _ hx, he⟩

/-- Positive and negative lists are clause-tail truth values under a
fixed assignment to all nonpivot variables. Every cross resolvent is
necessary and sufficient for some Boolean pivot value. -/
theorem projection_iff (pos neg : List Bool) :
    (∃ v : Bool, (∀ a ∈ pos, (v || a) = true) ∧
      (∀ b ∈ neg, (!v || b) = true)) ↔
    (∀ a ∈ pos, ∀ b ∈ neg, (a || b) = true) := by
  constructor
  · intro h
    obtain ⟨v, hp, hn⟩ := h
    intro a ha b hb
    exact resolution_sound v a b (hp a ha) (hn b hb)
  · intro h
    cases all_true_or_false_member pos with
    | inl hp =>
      refine ⟨false, ?_, ?_⟩
      · intro a ha
        exact hp a ha
      · intro b _
        rfl
    | inr hf =>
      obtain ⟨a, ha, he⟩ := hf
      refine ⟨true, ?_, ?_⟩
      · intro a _
        rfl
      · intro b hb
        have e := h a ha b hb
        rw [he] at e
        exact e

theorem clause_split_iff (a b c : Bool) :
    (∃ z : Bool, (a || z) = true ∧ (!z || b || c) = true) ↔
      (a || b || c) = true := by
  constructor
  · intro h
    obtain ⟨z, hp, hn⟩ := h
    cases a <;> cases b <;> cases c <;> cases z <;> first | rfl | contradiction
  · intro h
    cases a with
    | false => exact ⟨true, rfl, h⟩
    | true => exact ⟨false, rfl, rfl⟩

-- A pattern's clause forbids precisely that assignment on its support.
-- Length mismatches return true; actual CNF supports have equal length.
def block : List Bool → List Bool → Bool
  | [], [] => false
  | [], _::_ => true
  | _::_, [] => true
  | p::ps, x::xs =>
    if p then (if x then block ps xs else true)
    else (if x then true else block ps xs)

theorem block_self (p : List Bool) : block p p = false := by
  induction p with
  | nil => rfl
  | cons a as ih => cases a <;> exact ih

theorem block_false_eq (p x : List Bool) (h : block p x = false) :
    p = x := by
  induction p generalizing x with
  | nil =>
    cases x with
    | nil => rfl
    | cons _ _ => exact Bool.noConfusion h
  | cons a as ih =>
    cases x with
    | nil => exact Bool.noConfusion h
    | cons b bs =>
      cases a <;> cases b
      · exact congrArg (List.cons false) (ih bs h)
      · exact Bool.noConfusion h
      · exact Bool.noConfusion h
      · exact congrArg (List.cons true) (ih bs h)

def parity : List Bool → Bool
  | [] => false
  | x::xs => ProctorGF2.bx x (parity xs)

def BlocksSat (patterns : List (List Bool)) (x : List Bool) : Prop :=
  ∀ p ∈ patterns, block p x = true

theorem parity_block_iff (patterns : List (List Bool)) (k : Nat)
    (rhs : Bool) (x : List Bool) (hx : x.length = k)
    (complete : ∀ p : List Bool, p.length = k → parity p ≠ rhs → p ∈ patterns)
    (sound : ∀ p ∈ patterns, parity p ≠ rhs) :
    BlocksSat patterns x ↔ parity x = rhs := by
  constructor
  · intro h
    by_cases e : parity x = rhs
    · exact e
    · have hb := h x (complete x hx e)
      exact Bool.noConfusion ((block_self x).symm.trans hb)
  · intro h p hp
    cases e : block p x with
    | true => rfl
    | false =>
      have he := block_false_eq p x e
      exact ((sound p hp) ((congrArg parity he).trans h)).elim

-- Select coordinates from the existing F002 padded coefficient model.
def select : List Bool → List Bool → List Bool
  | [], _ => []
  | _::_, [] => []
  | a::as, x::xs => if a then x :: select as xs else select as xs

theorem parity_select (a x : List Bool) :
    parity (select a x) = ProctorGF2.dot a x := by
  induction a generalizing x with
  | nil => rfl
  | cons b bs ih =>
    cases x with
    | nil => rfl
    | cons y ys =>
      cases b with
      | false => exact ih ys
      | true => exact congrArg (ProctorGF2.bx y) (ih ys)

theorem row_block_sound (r : ProctorGF2.Row) (patterns : List (List Bool))
    (k : Nat) (x : List Bool) (hx : (select r.coeff x).length = k)
    (complete : ∀ p : List Bool, p.length = k → parity p ≠ r.rhs → p ∈ patterns)
    (h : BlocksSat patterns (select r.coeff x)) : ProctorGF2.Sat r x := by
  have hp : parity (select r.coeff x) = r.rhs := by
    by_cases e : parity (select r.coeff x) = r.rhs
    · exact e
    · have hb := h (select r.coeff x) (complete _ hx e)
      exact Bool.noConfusion ((block_self (select r.coeff x)).symm.trans hb)
  exact (parity_select r.coeff x).symm.trans hp

/-- Compose complete parity-block evidence with the existing GF(2)
contradiction theorem. All supports and width hypotheses are supplied. -/
theorem parity_blocks_unsat (rs : List ProctorGF2.Row)
    (patterns : ProctorGF2.Row → List (List Bool))
    (width : ProctorGF2.Row → Nat)
    (complete : ∀ r ∈ rs, ∀ p : List Bool,
      p.length = width r → parity p ≠ r.rhs → p ∈ patterns r)
    (hz : ProctorGF2.ZeroVec (ProctorGF2.sumRows rs).coeff)
    (hr : (ProctorGF2.sumRows rs).rhs = true) :
    ¬ ∃ x : List Bool, ∀ r ∈ rs,
      (select r.coeff x).length = width r ∧
      BlocksSat (patterns r) (select r.coeff x) := by
  intro h
  obtain ⟨x, hx⟩ := h
  apply ProctorGF2.certificate_sound rs rs (fun _ hmem => hmem) hz hr
  refine ⟨x, ?_⟩
  intro r hm
  exact row_block_sound r (patterns r) (width r) x
    (hx r hm).left (complete r hm) (hx r hm).right

end ProctorParityElimination

#print axioms ProctorParityElimination.resolution_sound
#print axioms ProctorParityElimination.projection_iff
#print axioms ProctorParityElimination.clause_split_iff
#print axioms ProctorParityElimination.block_self
#print axioms ProctorParityElimination.block_false_eq
#print axioms ProctorParityElimination.parity_block_iff
#print axioms ProctorParityElimination.parity_select
#print axioms ProctorParityElimination.row_block_sound
#print axioms ProctorParityElimination.parity_blocks_unsat
#print axioms ProctorParityElimination.all_true_or_false_member
