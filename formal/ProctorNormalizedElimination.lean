/-! F035: semantics-preserving literal deduplication, tautology deletion,
and one-direction subsumption. No global polynomial residual bound. -/
namespace ProctorNormalizedElimination
open ProctorHallDeficiency
open ProctorExecutableReplay (contains contains_sound)
open ProctorResolutionBridge (contains_complete)
open ProctorExecutableDiscovery (contained contained_sound)
open ProctorGeneralBranching (formula_cons Satisfiable)
open ProctorAdaptiveElimination (eliminate eliminate_exists)
open ProctorOrdinaryCompleteness (update)
open ProctorPathResourceBounds (occurrences)
open ProctorCapacityDeficiency (opposite)

def uniqueRow : Clause → Clause
  | [] => []
  | l::ls => if contains l ls then uniqueRow ls else l::uniqueRow ls

theorem unique_mem (c : Clause) (l : Literal) :
    l∈uniqueRow c ↔ l∈c := by
  induction c with
  | nil => exact Iff.rfl
  | cons a as ih =>
    change l∈(if contains a as then uniqueRow as else a::uniqueRow as) ↔ l∈a::as
    cases h : contains a as with
    | true =>
      constructor
      · intro e
        exact List.Mem.tail _ (ih.1 e)
      · intro e
        cases e with
        | head => exact ih.2 (contains_sound _ _ h)
        | tail _ hm => exact ih.2 hm
    | false =>
      constructor
      · intro e
        cases e with
        | head => exact List.Mem.head _
        | tail _ hm => exact List.Mem.tail _ (ih.1 hm)
      · intro e
        cases e with
        | head => exact List.Mem.head _
        | tail _ hm => exact List.Mem.tail _ (ih.2 hm)

theorem unique_length (c : Clause) : (uniqueRow c).length≤c.length := by
  induction c with
  | nil => exact Nat.le_refl _
  | cons a as ih =>
    change (if contains a as then uniqueRow as else a::uniqueRow as).length≤as.length+1
    cases h : contains a as with
    | true => exact Nat.le_trans ih (Nat.le_succ _)
    | false => exact Nat.succ_le_succ ih

theorem unique_correct (c : Clause) (x : Assignment) :
    ClauseSat (uniqueRow c) x ↔ ClauseSat c x := by
  constructor
  · intro h
    obtain ⟨l,hl,he⟩ := h
    exact ⟨l,(unique_mem c l).1 hl,he⟩
  · intro h
    obtain ⟨l,hl,he⟩ := h
    exact ⟨l,(unique_mem c l).2 hl,he⟩

def taut : Clause → Bool
  | [] => false
  | l::ls => contains (opposite l) ls || taut ls

theorem taut_sound (c : Clause) (x : Assignment) (h : taut c=true) :
    ClauseSat c x := by
  induction c with
  | nil => cases h
  | cons l ls ih =>
    change (contains (opposite l) ls || taut ls)=true at h
    cases e : contains (opposite l) ls with
    | false =>
      rw [e] at h
      obtain ⟨a,ha,ht⟩ := ih h
      exact ⟨a,List.Mem.tail _ ha,ht⟩
    | true =>
      have hm := contains_sound _ _ e
      cases l with
      | mk v b =>
        cases b <;> cases hx : x v
        · exact ⟨(v,false),List.Mem.head _,hx⟩
        · exact ⟨(v,true),List.Mem.tail _ hm,hx⟩
        · exact ⟨(v,false),List.Mem.tail _ hm,hx⟩
        · exact ⟨(v,true),List.Mem.head _,hx⟩

def subsumed (c : Clause) : Formula → Bool
  | [] => false
  | d::ds => contained c d || subsumed c ds

theorem subsumed_sound (c : Clause) (f : Formula) (x : Assignment)
    (h : subsumed c f=true) (hf : FormulaSat f x) : ClauseSat c x := by
  induction f with
  | nil => cases h
  | cons d ds ih =>
    change (contained c d || subsumed c ds)=true at h
    cases e : contained c d with
    | true =>
      obtain ⟨l,hl,he⟩ := hf d (List.Mem.head _)
      exact ⟨l,contained_sound c d e l hl,he⟩
    | false =>
      rw [e] at h
      exact ih h (fun r hr => hf r (List.Mem.tail _ hr))

def normalize : Formula → Formula
  | [] => []
  | c::cs =>
    let d := uniqueRow c
    let g := normalize cs
    if taut d || subsumed d g then g else d::g

theorem normalize_correct (f : Formula) (x : Assignment) :
    FormulaSat (normalize f) x ↔ FormulaSat f x := by
  induction f with
  | nil => exact Iff.rfl
  | cons c cs ih =>
    let d := uniqueRow c
    let g := normalize cs
    apply Iff.trans _ (formula_cons x c cs).symm
    change FormulaSat (if taut d || subsumed d g then g else d::g) x ↔
      ClauseSat c x ∧ FormulaSat cs x
    cases ht : taut d with
    | true =>
      change FormulaSat g x ↔ _
      exact ⟨fun h => ⟨(unique_correct c x).1 (taut_sound d x ht),ih.1 h⟩,
        fun h => ih.2 h.2⟩
    | false =>
      cases hs : subsumed d g with
      | true =>
        change FormulaSat g x ↔ _
        exact ⟨fun h => ⟨(unique_correct c x).1 (subsumed_sound d g x hs h),ih.1 h⟩,
          fun h => ih.2 h.2⟩
      | false =>
        change FormulaSat (d::g) x ↔ _
        apply Iff.trans (formula_cons x d g)
        exact ⟨fun h => ⟨(unique_correct c x).1 h.1,ih.1 h.2⟩,
          fun h => ⟨(unique_correct c x).2 h.1,ih.2 h.2⟩⟩

theorem normalize_length (f : Formula) : (normalize f).length≤f.length := by
  induction f with
  | nil => exact Nat.le_refl _
  | cons c cs ih =>
    change (if taut (uniqueRow c) || subsumed (uniqueRow c) (normalize cs)
      then normalize cs else uniqueRow c::normalize cs).length≤cs.length+1
    cases h : taut (uniqueRow c) || subsumed (uniqueRow c) (normalize cs) with
    | true => exact Nat.le_trans ih (Nat.le_succ _)
    | false => exact Nat.succ_le_succ ih

theorem normalize_occurrences (f : Formula) : occurrences (normalize f)≤occurrences f := by
  induction f with
  | nil => exact Nat.le_refl _
  | cons c cs ih =>
    change occurrences (if taut (uniqueRow c) || subsumed (uniqueRow c) (normalize cs)
      then normalize cs else uniqueRow c::normalize cs)≤c.length+occurrences cs
    cases h : taut (uniqueRow c) || subsumed (uniqueRow c) (normalize cs) with
    | true => exact Nat.le_trans ih (Nat.le_add_left _ _)
    | false => exact Nat.add_le_add (unique_length c) ih

def normalizedEliminate (v : Nat) (f : Formula) : Formula :=
  normalize (eliminate v (normalize f))

theorem normalized_exists (v : Nat) (f : Formula) (x : Assignment) :
    FormulaSat (normalizedEliminate v f) x ↔ ∃ b : Bool, FormulaSat f (update x v b) := by
  apply Iff.trans (normalize_correct _ x)
  apply Iff.trans (eliminate_exists v (normalize f) x)
  constructor
  · intro h
    obtain ⟨b,hb⟩ := h
    exact ⟨b,(normalize_correct f _).1 hb⟩
  · intro h
    obtain ⟨b,hb⟩ := h
    exact ⟨b,(normalize_correct f _).2 hb⟩

theorem normalized_sat (v : Nat) (f : Formula) :
    Satisfiable (normalizedEliminate v f) ↔ Satisfiable f := by
  constructor
  · intro h
    obtain ⟨x,hx⟩ := h
    obtain ⟨b,hb⟩ := (normalized_exists v f x).1 hx
    exact ⟨update x v b,hb⟩
  · intro h
    obtain ⟨x,hx⟩ := h
    exact ⟨x,(normalized_exists v f x).2
      ⟨x v,ProctorGeneralBranching.update_same_on x v f hx⟩⟩

end ProctorNormalizedElimination

#print axioms ProctorNormalizedElimination.unique_mem
#print axioms ProctorNormalizedElimination.unique_length
#print axioms ProctorNormalizedElimination.unique_correct
#print axioms ProctorNormalizedElimination.taut_sound
#print axioms ProctorNormalizedElimination.subsumed_sound
#print axioms ProctorNormalizedElimination.normalize_correct
#print axioms ProctorNormalizedElimination.normalize_length
#print axioms ProctorNormalizedElimination.normalize_occurrences
#print axioms ProctorNormalizedElimination.normalized_exists
#print axioms ProctorNormalizedElimination.normalized_sat
