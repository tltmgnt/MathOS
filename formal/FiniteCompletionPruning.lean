/-!
# Stage 3a: finite candidate pruning

A finite list of candidate assumption sets is filtered to remove any set
strictly containing another candidate. These are abstract predicate-sets;
the analyzer's candidate-generation recurrence is NOT formalized here.

Claims:
* every output appears among the candidates;
* no output has a strict-subset candidate;
* output membership precisely characterizes undominated candidates;
* output candidates form an antichain up to extensional equality.

Noncomputable classical decidability is used for predicate-set inclusion.
This is logical formalization, not an executable finite-set implementation.
-/
namespace MathOS

universe u

def SetIncluded {α : Type u} (a b : α → Prop) : Prop :=
  ∀ x, a x → b x

def StrictlyIncluded {α : Type u} (a b : α → Prop) : Prop :=
  SetIncluded a b ∧ ¬ SetIncluded b a

noncomputable def pruneCandidates {α : Type u}
    (candidates : List (α → Prop)) : List (α → Prop) := by
  classical
  exact candidates.filter (fun c =>
    ¬ ∃ d, d ∈ candidates ∧ StrictlyIncluded d c)

theorem mem_pruneCandidates_iff {α : Type u}
    (candidates : List (α → Prop)) (c : α → Prop) :
    c ∈ pruneCandidates candidates ↔
      c ∈ candidates ∧
      ¬ ∃ d, d ∈ candidates ∧ StrictlyIncluded d c := by
  classical
  simp [pruneCandidates]

theorem pruneCandidates_sound {α : Type u}
    (candidates : List (α → Prop)) (c : α → Prop)
    (hc : c ∈ pruneCandidates candidates) :
    c ∈ candidates :=
  (mem_pruneCandidates_iff candidates c).mp hc |>.left

theorem pruneCandidates_minimal {α : Type u}
    (candidates : List (α → Prop)) (c : α → Prop)
    (hc : c ∈ pruneCandidates candidates) :
    ¬ ∃ d, d ∈ candidates ∧ StrictlyIncluded d c :=
  (mem_pruneCandidates_iff candidates c).mp hc |>.right

theorem pruneCandidates_antichain {α : Type u}
    (candidates : List (α → Prop)) (a b : α → Prop)
    (ha : a ∈ pruneCandidates candidates)
    (hb : b ∈ pruneCandidates candidates)
    (hab : SetIncluded a b) :
    SetIncluded b a := by
  apply Classical.byContradiction
  intro hba
  have hs : StrictlyIncluded a b := ⟨hab, hba⟩
  have hminimal := pruneCandidates_minimal candidates b hb
  exact hminimal ⟨a, pruneCandidates_sound candidates a ha, hs⟩

theorem pruneCandidates_exact {α : Type u}
    (candidates : List (α → Prop)) (c : α → Prop)
    (hc : c ∈ candidates)
    (hminimal : ¬ ∃ d, d ∈ candidates ∧ StrictlyIncluded d c) :
    c ∈ pruneCandidates candidates :=
  (mem_pruneCandidates_iff candidates c).mpr ⟨hc, hminimal⟩

end MathOS
