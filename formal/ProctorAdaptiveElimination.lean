/-! F035: factor common residual clauses before distributing the
Shannon disjunction. This is Davis-Putnam-style elimination, not a
universal polynomial-size or polynomial-time claim. -/
namespace ProctorAdaptiveElimination
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (update)
open ProctorGeneralBranching (reduceRow restrict formula_cons restriction_correct Satisfiable)
open ProctorSemanticProjection (orProduct product_correct product_length project project_correct)
open ProctorComponentFactorization (append_sat)

structure Buckets where
  common : Formula
  left : Formula
  right : Formula

def split (v : Nat) : Formula → Buckets
  | [] => ⟨[],[],[]⟩
  | c::cs =>
    let t := split v cs
    match reduceRow v false c,reduceRow v true c with
    | none,none => t
    | some a,none => ⟨t.common,a::t.left,t.right⟩
    | none,some b => ⟨t.common,t.left,b::t.right⟩
    | some a,some _ => ⟨a::t.common,t.left,t.right⟩

theorem both_same (v : Nat) (c a b : Clause)
    (ha : reduceRow v false c=some a) (hb : reduceRow v true c=some b) :
    a=b := by
  induction c generalizing a b with
  | nil =>
    change some []=some a at ha
    change some []=some b at hb
    cases ha
    cases hb
    rfl
  | cons l ls ih =>
    change (if l.1=v then (if l.2=false then none else reduceRow v false ls)
      else (reduceRow v false ls).map (fun r => l::r))=some a at ha
    change (if l.1=v then (if l.2=true then none else reduceRow v true ls)
      else (reduceRow v true ls).map (fun r => l::r))=some b at hb
    by_cases hv : l.1=v
    · rw [if_pos hv] at ha hb
      cases hs : l.2 with
      | false => rw [hs,if_pos rfl] at ha; cases ha
      | true => rw [hs,if_pos rfl] at hb; cases hb
    · rw [if_neg hv] at ha hb
      cases h0 : reduceRow v false ls with
      | none => rw [h0] at ha; cases ha
      | some r =>
        rw [h0] at ha
        change some (l::r)=some a at ha
        cases ha
        cases h1 : reduceRow v true ls with
        | none => rw [h1] at hb; cases hb
        | some s =>
          rw [h1] at hb
          change some (l::s)=some b at hb
          cases hb
          exact congrArg (List.cons l) (ih _ _ h0 h1)

private theorem and_shift (A B C : Prop) :
    (A ∧ (B ∧ C)) ↔ (B ∧ (A ∧ C)) :=
  ⟨fun h => ⟨h.2.1,h.1,h.2.2⟩,fun h => ⟨h.2.1,h.1,h.2.2⟩⟩

theorem split_correct (v : Nat) (f : Formula) (x : Assignment) :
    (FormulaSat (restrict v false f) x ↔
      FormulaSat (split v f).common x ∧ FormulaSat (split v f).left x) ∧
    (FormulaSat (restrict v true f) x ↔
      FormulaSat (split v f).common x ∧ FormulaSat (split v f).right x) := by
  induction f with
  | nil =>
    have he : FormulaSat [] x := fun _ h => nomatch h
    exact ⟨⟨fun _ => ⟨he,he⟩,fun _ => he⟩,⟨fun _ => ⟨he,he⟩,fun _ => he⟩⟩
  | cons c cs ih =>
    unfold split restrict
    dsimp only
    cases ha : reduceRow v false c with
    | none =>
      cases hb : reduceRow v true c with
      | none => exact ih
      | some b =>
        refine ⟨ih.1,?_⟩
        apply Iff.trans (formula_cons x b (restrict v true cs))
        constructor
        · intro h
          have ht := ih.2.1 h.2
          exact ⟨ht.1,(formula_cons x b _).2 ⟨h.1,ht.2⟩⟩
        · intro h
          have ht := (formula_cons x b _).1 h.2
          exact ⟨ht.1,ih.2.2 ⟨h.1,ht.2⟩⟩
    | some a =>
      cases hb : reduceRow v true c with
      | none =>
        refine ⟨?_,ih.2⟩
        apply Iff.trans (formula_cons x a (restrict v false cs))
        constructor
        · intro h
          have ht := ih.1.1 h.2
          exact ⟨ht.1,(formula_cons x a _).2 ⟨h.1,ht.2⟩⟩
        · intro h
          have ht := (formula_cons x a _).1 h.2
          exact ⟨ht.1,ih.1.2 ⟨h.1,ht.2⟩⟩
      | some b =>
        have he := both_same v c a b ha hb
        cases he
        constructor
        · apply Iff.trans (formula_cons x a (restrict v false cs))
          constructor
          · intro h
            have ht := ih.1.1 h.2
            exact ⟨(formula_cons x a _).2 ⟨h.1,ht.1⟩,ht.2⟩
          · intro h
            have ht := (formula_cons x a _).1 h.1
            exact ⟨ht.1,ih.1.2 ⟨ht.2,h.2⟩⟩
        · apply Iff.trans (formula_cons x a (restrict v true cs))
          constructor
          · intro h
            have ht := ih.2.1 h.2
            exact ⟨(formula_cons x a _).2 ⟨h.1,ht.1⟩,ht.2⟩
          · intro h
            have ht := (formula_cons x a _).1 h.1
            exact ⟨ht.1,ih.2.2 ⟨ht.2,h.2⟩⟩

def eliminate (v : Nat) (f : Formula) : Formula :=
  let t := split v f
  t.common++orProduct t.left t.right

theorem eliminate_correct (v : Nat) (f : Formula) (x : Assignment) :
    FormulaSat (eliminate v f) x ↔ FormulaSat (project v f) x := by
  let t := split v f
  have hs := split_correct v f x
  constructor
  · intro h
    have hh := (append_sat t.common (orProduct t.left t.right) x).1 h
    apply (product_correct _ _ x).2
    cases (product_correct t.left t.right x).1 hh.2 with
    | inl e => exact Or.inl (hs.1.2 ⟨hh.1,e⟩)
    | inr e => exact Or.inr (hs.2.2 ⟨hh.1,e⟩)
  · intro h
    apply (append_sat t.common (orProduct t.left t.right) x).2
    cases (product_correct _ _ x).1 h with
    | inl e =>
      have hh := hs.1.1 e
      exact ⟨hh.1,(product_correct t.left t.right x).2 (Or.inl hh.2)⟩
    | inr e =>
      have hh := hs.2.1 e
      exact ⟨hh.1,(product_correct t.left t.right x).2 (Or.inr hh.2)⟩

theorem eliminate_exists (v : Nat) (f : Formula) (x : Assignment) :
    FormulaSat (eliminate v f) x ↔ ∃ b : Bool, FormulaSat f (update x v b) :=
  Iff.trans (eliminate_correct v f x) (project_correct v f x)

private theorem len_append {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons a as ih =>
    change (as++ys).length+1=as.length+1+ys.length
    rw [ih,Nat.add_assoc as.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

def estimate (v : Nat) (f : Formula) : Nat :=
  let t := split v f
  t.common.length+t.left.length*t.right.length

theorem estimate_exact (v : Nat) (f : Formula) :
    (eliminate v f).length=estimate v f := by
  unfold eliminate estimate
  dsimp only
  rw [len_append,product_length]

-- Choose a locally minimum projected clause count among the offered
-- variables. Ties retain the first candidate. This is NOT a global bound.
def choose (f : Formula) (v : Nat) : List Nat → Nat
  | [] => v
  | w::ws =>
    let u := choose f w ws
    if estimate v f≤estimate u f then v else u

theorem choose_first (f : Formula) (v : Nat) (vs : List Nat) :
    estimate (choose f v vs) f≤estimate v f := by
  cases vs with
  | nil => exact Nat.le_refl _
  | cons w ws =>
    change estimate (if estimate v f≤estimate (choose f w ws) f then v else choose f w ws) f≤estimate v f
    by_cases h : estimate v f≤estimate (choose f w ws) f
    · rw [if_pos h]
      exact Nat.le_refl _
    · rw [if_neg h]
      exact Nat.le_of_lt (Nat.lt_of_not_ge h)

theorem choose_min (f : Formula) (v : Nat) (vs : List Nat) :
    ∀ w∈v::vs,estimate (choose f v vs) f≤estimate w f := by
  induction vs generalizing v with
  | nil =>
    intro w hw
    cases hw with
    | head => exact Nat.le_refl _
    | tail _ hm => cases hm
  | cons u us ih =>
    intro w hw
    cases hw with
    | head => exact choose_first f _ _
    | tail _ hm =>
      change estimate (if estimate v f≤estimate (choose f u us) f then v else choose f u us) f≤estimate w f
      by_cases h : estimate v f≤estimate (choose f u us) f
      · rw [if_pos h]
        exact Nat.le_trans h (ih u w hm)
      · rw [if_neg h]
        exact ih u w hm

theorem adaptive_local_bound (f : Formula) (v : Nat) (vs : List Nat)
    (w : Nat) (h : w∈v::vs) :
    (eliminate (choose f v vs) f).length≤(eliminate w f).length := by
  rw [estimate_exact,estimate_exact]
  exact choose_min f v vs w h

end ProctorAdaptiveElimination

#print axioms ProctorAdaptiveElimination.both_same
#print axioms ProctorAdaptiveElimination.split_correct
#print axioms ProctorAdaptiveElimination.eliminate_correct
#print axioms ProctorAdaptiveElimination.eliminate_exists
#print axioms ProctorAdaptiveElimination.estimate_exact
#print axioms ProctorAdaptiveElimination.choose_first
#print axioms ProctorAdaptiveElimination.choose_min
#print axioms ProctorAdaptiveElimination.adaptive_local_bound
