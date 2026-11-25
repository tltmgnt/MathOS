/-! F035/F038 candidate: constructive ordinary refutation completeness
for the typed mixed checker. Finite assignment splitting, not a
polynomial proof-size or discovery claim. -/
namespace ProctorOrdinaryCompleteness
open ProctorHallDeficiency
open ProctorExecutableReplay (Step lookup stepCheck hasEmpty)
open ProctorResolutionBridge (Unsat sequentialCheck sequentialFrontier compile step_complete compile_refutation)
open ProctorUnifiedReplay (Proof check)

theorem clause_alternative (c : Clause) (x : Assignment) :
    ClauseSat c x ∨ (∀ l∈c, x l.1≠l.2) := by
  induction c with
  | nil => exact Or.inr (fun _ h => nomatch h)
  | cons a as ih =>
    by_cases e : x a.1=a.2
    · exact Or.inl ⟨a,List.Mem.head _,e⟩
    · cases ih with
      | inl sat =>
        obtain ⟨l,hl,ht⟩ := sat
        exact Or.inl ⟨l,List.Mem.tail _ hl,ht⟩
      | inr bad =>
        apply Or.inr
        intro l hl
        cases hl with
        | head => exact e
        | tail _ hm => exact bad l hm

theorem formula_alternative (f : Formula) (x : Assignment) :
    FormulaSat f x ∨ ∃ c∈f, ∀ l∈c, x l.1≠l.2 := by
  induction f with
  | nil => exact Or.inl (fun _ h => nomatch h)
  | cons c cs ih =>
    cases clause_alternative c x with
    | inr bad => exact Or.inr ⟨c,List.Mem.head _,bad⟩
    | inl good =>
      cases ih with
      | inr bad =>
        obtain ⟨d,hd,hb⟩ := bad
        exact Or.inr ⟨d,List.Mem.tail _ hd,hb⟩
      | inl sat =>
        apply Or.inl
        intro d hd
        cases hd with
        | head => exact good
        | tail _ hm => exact sat d hm

theorem false_row (f : Formula) (x : Assignment) (h : Unsat f) :
    ∃ c∈f, ∀ l∈c, x l.1≠l.2 := by
  cases formula_alternative f x with
  | inl sat => exact (h ⟨x,sat⟩).elim
  | inr bad => exact bad

theorem lookup_exists (f : Formula) (c : Clause) (h : c∈f) :
    ∃ i, lookup f i=some c := by
  induction f with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head => exact ⟨0,rfl⟩
    | tail _ hm =>
      obtain ⟨i,hi⟩ := ih hm
      exact ⟨i+1,hi⟩

inductive Reach : Formula → Formula → Prop where
  | refl (f : Formula) : Reach f f
  | step {f g : Formula} (s : Step) :
      stepCheck f s=true → Reach (s.tail::f) g → Reach f g

theorem reach_trans {f g h : Formula} (a : Reach f g) (b : Reach g h) :
    Reach f h := by
  induction a with
  | refl => exact b
  | step s hs rest ih => exact Reach.step s hs (ih b)

theorem reach_mem {f g : Formula} (h : Reach f g) (c : Clause) (hc : c∈f) :
    c∈g := by
  induction h with
  | refl => exact hc
  | step s hs rest ih => exact ih (List.Mem.tail _ hc)

theorem weaken_reach (g : Formula) (c path : Clause)
    (hc : c∈g) (h : ∀ l∈c, l∈path) :
    Reach g (path::g) := by
  obtain ⟨i,hi⟩ := lookup_exists g c hc
  exact Reach.step ⟨i,i,0,path⟩
    (step_complete g ⟨i,i,0,path⟩ c c hi hi
      (fun l hl => Or.inr (h l hl)) (fun l hl => Or.inr (h l hl))) (Reach.refl _)

theorem resolve_reach (g : Formula) (v : Nat) (path : Clause)
    (hp : ((v,true)::path)∈g) (hn : ((v,false)::path)∈g) :
    Reach g (path::g) := by
  obtain ⟨i,hi⟩ := lookup_exists g _ hp
  obtain ⟨j,hj⟩ := lookup_exists g _ hn
  have hpos : ∀ l∈((v,true)::path), l=(v,true) ∨ l∈path := by
    intro l hl
    cases hl with
    | head => exact Or.inl rfl
    | tail _ hm => exact Or.inr hm
  have hneg : ∀ l∈((v,false)::path), l=(v,false) ∨ l∈path := by
    intro l hl
    cases hl with
    | head => exact Or.inl rfl
    | tail _ hm => exact Or.inr hm
  exact Reach.step ⟨i,j,v,path⟩
    (step_complete g ⟨i,j,v,path⟩ _ _ hi hj hpos hneg) (Reach.refl _)

def update (x : Assignment) (v : Nat) (b : Bool) : Assignment :=
  fun u => if u=v then b else x u

def Cover (f : Formula) (vs : List Nat) (path : Clause) (x : Assignment) : Prop :=
  ∀ c∈f, ∀ l∈c, l.1∈vs ∨ (l.1,!x l.1)∈path

theorem cover_branch (f : Formula) (v : Nat) (vs : List Nat)
    (path : Clause) (x : Assignment) (b : Bool)
    (h : Cover f (v::vs) path x) :
    Cover f vs ((v,!b)::path) (update x v b) := by
  intro c hc l hl
  by_cases e : l.1=v
  · apply Or.inr
    rw [e]
    change (v, !(if v=v then b else x v))∈((v,!b)::path)
    rw [if_pos rfl]
    exact List.Mem.head _
  · have hu : update x v b l.1=x l.1 := by unfold update; rw [if_neg e]
    rw [hu]
    cases h c hc l hl with
    | inr hm => exact Or.inr (List.Mem.tail _ hm)
    | inl hm =>
      cases hm with
      | head => exact (e rfl).elim
      | tail _ ht => exact Or.inl ht

private theorem opposite_value (a b : Bool) (h : a≠b) : b= !a := by
  cases a <;> cases b <;> first | rfl | exact (h rfl).elim

theorem covered_false (f : Formula) (path : Clause) (x : Assignment)
    (h : Cover f [] path x) (c : Clause) (hc : c∈f)
    (hf : ∀ l∈c, x l.1≠l.2) : ∀ l∈c, l∈path := by
  intro l hl
  cases h c hc l hl with
  | inl hm => cases hm
  | inr hm =>
    have e := opposite_value (x l.1) l.2 (hf l hl)
    cases l with
    | mk v b =>
      change b= !(x v) at e
      change (v,!(x v))∈path at hm
      rw [e]
      exact hm

-- The two branch proofs can be constructed sequentially because
-- Reach preserves every original and previously derived clause.
theorem split_complete (f : Formula) (vs : List Nat) (path : Clause)
    (x : Assignment) (u : Unsat f) (h : Cover f vs path x)
    (g : Formula) (sub : ∀ c∈f, c∈g) :
    ∃ g', Reach g g' ∧ path∈g' := by
  induction vs generalizing path x g with
  | nil =>
    obtain ⟨c,hc,hf⟩ := false_row f x u
    exact ⟨path::g,weaken_reach g c path (sub c hc)
      (covered_false f path x h c hc hf),List.Mem.head _⟩
  | cons v vs ih =>
    have hp : Cover f vs ((v,true)::path) (update x v false) :=
      cover_branch f v vs path x false h
    obtain ⟨g1,r1,p1⟩ := ih ((v,true)::path) (update x v false) hp g sub
    have sub1 : ∀ c∈f, c∈g1 := fun c hc => reach_mem r1 c (sub c hc)
    have hn : Cover f vs ((v,false)::path) (update x v true) :=
      cover_branch f v vs path x true h
    obtain ⟨g2,r2,p2⟩ := ih ((v,false)::path) (update x v true) hn g1 sub1
    have rp : ((v,true)::path)∈g2 := reach_mem r2 _ p1
    exact ⟨path::g2,reach_trans (reach_trans r1 r2)
      (resolve_reach g2 v path rp p2),List.Mem.head _⟩

def rowVars : Clause → List Nat
  | [] => []
  | l::ls => l.1::rowVars ls

def variables : Formula → List Nat
  | [] => []
  | c::cs => rowVars c++variables cs

private theorem mem_append_left {α : Type} (a : α) (xs ys : List α)
    (h : a∈xs) : a∈xs++ys := by
  induction xs with
  | nil => cases h
  | cons x xs ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

private theorem mem_append_right {α : Type} (a : α) (xs ys : List α)
    (h : a∈ys) : a∈xs++ys := by
  induction xs with
  | nil => exact h
  | cons x xs ih => exact List.Mem.tail _ ih

theorem row_var_mem (c : Clause) (l : Literal) (h : l∈c) :
    l.1∈rowVars c := by
  induction c with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

theorem variable_mem (f : Formula) (c : Clause) (l : Literal)
    (hc : c∈f) (hl : l∈c) : l.1∈variables f := by
  induction f with
  | nil => cases hc
  | cons a as ih =>
    cases hc with
    | head => exact mem_append_left _ _ _ (row_var_mem c l hl)
    | tail _ hm => exact mem_append_right _ _ _ (ih hm)

theorem reach_refutation (f : Formula) (h : Unsat f) :
    ∃ g, Reach f g ∧ ([] : Clause)∈g :=
  split_complete f (variables f) [] (fun _ => false) h
    (fun c hc l hl => Or.inl (variable_mem f c l hc hl)) f (fun _ hc => hc)

theorem reach_trace {f g : Formula} (h : Reach f g) :
    ∃ ss : List Step, sequentialCheck f ss=true ∧ sequentialFrontier f ss=g := by
  induction h with
  | refl => exact ⟨[],rfl,rfl⟩
  | step s hs rest ih =>
    obtain ⟨ss,hc,hf⟩ := ih
    refine ⟨s::ss,?_,hf⟩
    change (stepCheck _ s && sequentialCheck (s.tail::_) ss)=true
    rw [hs,hc] <;> rfl

theorem empty_complete (g : Formula) (h : ([] : Clause)∈g) :
    hasEmpty g=true := by
  induction g with
  | nil => cases h
  | cons c cs ih =>
    cases c with
    | nil => rfl
    | cons l ls =>
      cases h with
      | tail _ hm => exact ih hm

theorem sequential_complete (f : Formula) (h : Unsat f) :
    ∃ ss : List Step, sequentialCheck f ss=true ∧
      hasEmpty (sequentialFrontier f ss)=true := by
  obtain ⟨g,hr,he⟩ := reach_refutation f h
  obtain ⟨ss,hc,hf⟩ := reach_trace hr
  exact ⟨ss,hc,hf.symm ▸ empty_complete g he⟩

theorem typed_complete (f : Formula) (h : Unsat f) :
    ∃ p : Proof, check f p=true := by
  obtain ⟨ss,hc,he⟩ := sequential_complete f h
  exact ⟨⟨compile 0 f ss,false,.empty⟩,compile_refutation 0 f ss hc he⟩

theorem typed_iff (f : Formula) :
    (∃ p : Proof, check f p=true) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨p,hp⟩ := h
    exact ProctorUnifiedReplay.check_sound f p hp
  · exact typed_complete f

end ProctorOrdinaryCompleteness

#print axioms ProctorOrdinaryCompleteness.clause_alternative
#print axioms ProctorOrdinaryCompleteness.formula_alternative
#print axioms ProctorOrdinaryCompleteness.false_row
#print axioms ProctorOrdinaryCompleteness.lookup_exists
#print axioms ProctorOrdinaryCompleteness.reach_trans
#print axioms ProctorOrdinaryCompleteness.reach_mem
#print axioms ProctorOrdinaryCompleteness.weaken_reach
#print axioms ProctorOrdinaryCompleteness.resolve_reach
#print axioms ProctorOrdinaryCompleteness.cover_branch
#print axioms ProctorOrdinaryCompleteness.covered_false
#print axioms ProctorOrdinaryCompleteness.split_complete
#print axioms ProctorOrdinaryCompleteness.row_var_mem
#print axioms ProctorOrdinaryCompleteness.variable_mem
#print axioms ProctorOrdinaryCompleteness.reach_refutation
#print axioms ProctorOrdinaryCompleteness.reach_trace
#print axioms ProctorOrdinaryCompleteness.empty_complete
#print axioms ProctorOrdinaryCompleteness.sequential_complete
#print axioms ProctorOrdinaryCompleteness.typed_complete
#print axioms ProctorOrdinaryCompleteness.typed_iff
