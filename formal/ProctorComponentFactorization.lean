/-! General-width component factorization. Exact logical decomposition,
not a universal polynomial decomposition theorem. -/
namespace ProctorComponentFactorization
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (variables rowVars variable_mem)

def Sat (f : Formula) : Prop := ∃ x, FormulaSat f x

def member (v : Nat) : List Nat → Bool
  | [] => false
  | w::ws => if v=w then true else member v ws

theorem member_sound (v : Nat) (vs : List Nat) (h : member v vs=true) : v∈vs := by
  induction vs with
  | nil => cases h
  | cons w ws ih =>
    change (if v=w then true else member v ws)=true at h
    by_cases e : v=w
    · cases e
      exact List.Mem.head _
    · rw [if_neg e] at h
      exact List.Mem.tail _ (ih h)

theorem member_complete (v : Nat) (vs : List Nat) (h : v∈vs) : member v vs=true := by
  induction vs with
  | nil => cases h
  | cons w ws ih =>
    change (if v=w then true else member v ws)=true
    by_cases e : v=w
    · rw [if_pos e]
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact ih hm

def Disjoint (f g : Formula) : Prop :=
  ∀ v∈variables f, v∈variables g → False

def disjointCheck (f g : Formula) : Bool :=
  (variables f).all (fun v => !(member v (variables g)))

private theorem all_sound {α : Type} (p : α → Bool) (xs : List α)
    (h : xs.all p=true) : ∀ a∈xs,p a=true := by
  induction xs with
  | nil => intro a ha; cases ha
  | cons a as ih =>
    change (p a && as.all p)=true at h
    have hh := ProctorExecutableReplay.and_true_local _ _ h
    intro b hb
    cases hb with
    | head => exact hh.left
    | tail _ hm => exact ih hh.right b hm

private theorem all_complete {α : Type} (p : α → Bool) (xs : List α)
    (h : ∀ a∈xs,p a=true) : xs.all p=true := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a && as.all p)=true
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))]
    rfl

theorem disjoint_sound (f g : Formula) (h : disjointCheck f g=true) : Disjoint f g := by
  intro v hv hg
  have hh := all_sound _ _ h v hv
  change Bool.not (member v (variables g))=true at hh
  rw [member_complete v (variables g) hg] at hh
  cases hh

theorem disjoint_complete (f g : Formula) (h : Disjoint f g) : disjointCheck f g=true := by
  apply all_complete
  intro v hv
  change Bool.not (member v (variables g))=true
  cases e : member v (variables g) with
  | false => rfl
  | true => exact (h v hv (member_sound v _ e)).elim

def join (f : Formula) (x y : Assignment) : Assignment :=
  fun v => if member v (variables f) then x v else y v

theorem join_left (f : Formula) (x y : Assignment) (h : FormulaSat f x) :
    FormulaSat f (join f x y) := by
  intro c hc
  obtain ⟨l,hl,he⟩ := h c hc
  refine ⟨l,hl,?_⟩
  unfold join
  rw [member_complete l.1 (variables f) (variable_mem f c l hc hl)]
  exact he

theorem join_right (f g : Formula) (x y : Assignment) (hd : Disjoint f g)
    (h : FormulaSat g y) : FormulaSat g (join f x y) := by
  intro c hc
  obtain ⟨l,hl,he⟩ := h c hc
  refine ⟨l,hl,?_⟩
  unfold join
  cases e : member l.1 (variables f) with
  | false => exact he
  | true =>
    exact (hd l.1 (member_sound l.1 _ e) (variable_mem g c l hc hl)).elim

private theorem append_left {α : Type} (a : α) (xs ys : List α) (h : a∈xs) :
    a∈xs++ys := by
  induction xs with
  | nil => cases h
  | cons x xs ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

private theorem append_right {α : Type} (a : α) (xs ys : List α) (h : a∈ys) :
    a∈xs++ys := by
  induction xs with
  | nil => exact h
  | cons x xs ih => exact List.Mem.tail _ ih

private theorem append_cases {α : Type} (a : α) (xs ys : List α) (h : a∈xs++ys) :
    a∈xs ∨ a∈ys := by
  induction xs with
  | nil => exact Or.inr h
  | cons x xs ih =>
    cases h with
    | head => exact Or.inl (List.Mem.head _)
    | tail _ hm =>
      cases ih hm with
      | inl e => exact Or.inl (List.Mem.tail _ e)
      | inr e => exact Or.inr e

theorem append_sat (f g : Formula) (x : Assignment) :
    FormulaSat (f++g) x ↔ FormulaSat f x ∧ FormulaSat g x := by
  constructor
  · intro h
    exact ⟨fun c hc => h c (append_left c f g hc),fun c hc => h c (append_right c f g hc)⟩
  · intro h c hc
    cases append_cases c f g hc with
    | inl e => exact h.left c e
    | inr e => exact h.right c e

theorem factor (f g : Formula) (hd : Disjoint f g) :
    Sat (f++g) ↔ Sat f ∧ Sat g := by
  constructor
  · intro h
    obtain ⟨x,hx⟩ := h
    have hh := (append_sat f g x).1 hx
    exact ⟨⟨x,hh.left⟩,⟨x,hh.right⟩⟩
  · intro h
    obtain ⟨⟨x,hx⟩,⟨y,hy⟩⟩ := h
    exact ⟨join f x y,(append_sat f g _).2
      ⟨join_left f x y hx,join_right f g x y hd hy⟩⟩

theorem checked_factor (f g : Formula) (h : disjointCheck f g=true) :
    Sat (f++g) ↔ Sat f ∧ Sat g :=
  factor f g (disjoint_sound f g h)

-- A shared variable invalidates the naive conjunction of independent
-- satisfiability answers; both individual unit clauses are satisfiable.
theorem overlap_counterexample :
    Sat [[(1,true)]] ∧ Sat [[(1,false)]] ∧
      ¬ Sat [[(1,true)],[(1,false)]] := by
  refine ⟨⟨fun _ => true,?_⟩,⟨fun _ => false,?_⟩,?_⟩
  · intro c hc
    cases hc with
    | head => exact ⟨(1,true),List.Mem.head _,rfl⟩
    | tail _ hm => cases hm
  · intro c hc
    cases hc with
    | head => exact ⟨(1,false),List.Mem.head _,rfl⟩
    | tail _ hm => cases hm
  · intro h
    obtain ⟨x,hx⟩ := h
    obtain ⟨a,ha,ht⟩ := hx _ (List.Mem.head _)
    obtain ⟨b,hb,hf⟩ := hx _ (List.Mem.tail _ (List.Mem.head _))
    cases ha with
    | head =>
      cases hb with
      | head => exact Bool.noConfusion (ht.symm.trans hf)
      | tail _ hm => cases hm
    | tail _ hm => cases hm

end ProctorComponentFactorization

#print axioms ProctorComponentFactorization.member_sound
#print axioms ProctorComponentFactorization.member_complete
#print axioms ProctorComponentFactorization.disjoint_sound
#print axioms ProctorComponentFactorization.disjoint_complete
#print axioms ProctorComponentFactorization.join_left
#print axioms ProctorComponentFactorization.join_right
#print axioms ProctorComponentFactorization.append_sat
#print axioms ProctorComponentFactorization.factor
#print axioms ProctorComponentFactorization.checked_factor
#print axioms ProctorComponentFactorization.overlap_counterexample
