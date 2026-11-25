/-! F036: exact equivalence of compact monotone Boolean circuits
already encodes general CNF unsatisfiability. Dual rails need not
be total: consistent partial selections extend to a model. -/
namespace ProctorMonotoneCircuitBarrier
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (variables variable_mem)

abbrev Rails := Literal → Bool

inductive Circuit where
  | input : Literal → Circuit
  | constant : Bool → Circuit
  | both : Circuit → Circuit → Circuit
  | either : Circuit → Circuit → Circuit

def eval (r : Rails) : Circuit → Bool
  | .input l => r l
  | .constant b => b
  | .both a b => eval r a && eval r b
  | .either a b => eval r a || eval r b

def coverRow : Clause → Circuit
  | [] => .constant false
  | l::ls => .either (.input l) (coverRow ls)

def cover : Formula → Circuit
  | [] => .constant true
  | c::cs => .both (coverRow c) (cover cs)

def conflict : List Nat → Circuit
  | [] => .constant false
  | v::vs => .either (.both (.input (v,true)) (.input (v,false))) (conflict vs)

def Hits (r : Rails) (c : Clause) : Prop := ∃ l∈c,r l=true
def Covers (r : Rails) (f : Formula) : Prop := ∀ c∈f,Hits r c
def Consistent (r : Rails) (vs : List Nat) : Prop :=
  ∀ v∈vs,r (v,true)=true → r (v,false)=false

theorem row_correct (r : Rails) (c : Clause) :
    eval r (coverRow c)=true ↔ Hits r c := by
  induction c with
  | nil =>
    constructor
    · intro h
      cases h
    · intro h
      obtain ⟨l,hl,_⟩ := h
      cases hl
  | cons l ls ih =>
    change (r l || eval r (coverRow ls))=true ↔ Hits r (l::ls)
    constructor
    · intro h
      cases e : r l with
      | true => exact ⟨l,List.Mem.head _,e⟩
      | false =>
        rw [e] at h
        obtain ⟨a,ha,ht⟩ := ih.1 h
        exact ⟨a,List.Mem.tail _ ha,ht⟩
    · intro h
      obtain ⟨a,ha,ht⟩ := h
      cases ha with
      | head => rw [ht]; rfl
      | tail _ hm =>
        rw [ih.2 ⟨a,hm,ht⟩]
        cases r l <;> rfl

theorem cover_correct (r : Rails) (f : Formula) :
    eval r (cover f)=true ↔ Covers r f := by
  induction f with
  | nil =>
    exact ⟨fun _ c hc => by cases hc,fun _ => rfl⟩
  | cons c cs ih =>
    change (eval r (coverRow c) && eval r (cover cs))=true ↔ Covers r (c::cs)
    constructor
    · intro h
      have hh := ProctorExecutableReplay.and_true_local _ _ h
      intro d hd
      cases hd with
      | head => exact (row_correct r c).1 hh.left
      | tail _ hm => exact ih.1 hh.right d hm
    · intro h
      rw [(row_correct r c).2 (h c (List.Mem.head _)),
        ih.2 (fun d hd => h d (List.Mem.tail _ hd))]

theorem conflict_correct (r : Rails) (vs : List Nat) :
    eval r (conflict vs)=false ↔ Consistent r vs := by
  induction vs with
  | nil => exact ⟨fun _ v hv => by cases hv,fun _ => rfl⟩
  | cons v vs ih =>
    change ((r (v,true) && r (v,false)) || eval r (conflict vs))=false ↔ Consistent r (v::vs)
    constructor
    · intro h
      have ht : eval r (conflict vs)=false := by
        cases e : eval r (conflict vs) with
        | false => rfl
        | true =>
          rw [e] at h
          cases r (v,true) <;> cases r (v,false) <;> cases h
      intro u hu hp
      cases hu with
      | head =>
        rw [hp,ht] at h
        cases e : r (v,false) with
        | false => rfl
        | true => rw [e] at h; cases h
      | tail _ hm => exact ih.1 ht u hm hp
    · intro h
      have ht := ih.2 (fun u hu => h u (List.Mem.tail _ hu))
      rw [ht]
      cases e : r (v,true) with
      | false => rfl
      | true => rw [h v (List.Mem.head _) e]; rfl

def rails (x : Assignment) : Rails :=
  fun l => if x l.1=l.2 then true else false

theorem rails_true (x : Assignment) (l : Literal) (h : x l.1=l.2) :
    rails x l=true := by
  unfold rails
  rw [if_pos h]

theorem rails_consistent (x : Assignment) (vs : List Nat) :
    Consistent (rails x) vs := by
  intro v _ h
  change (if x v=true then true else false)=true at h
  change (if x v=false then true else false)=false
  cases e : x v with
  | false => rw [e] at h; cases h
  | true => rw [e]; rfl

theorem model_covers (f : Formula) (x : Assignment) (h : FormulaSat f x) :
    Covers (rails x) f := by
  intro c hc
  obtain ⟨l,hl,he⟩ := h c hc
  exact ⟨l,hl,rails_true x l he⟩

def decode (r : Rails) : Assignment := fun v => r (v,true)

theorem selected_true (r : Rails) (vs : List Nat) (l : Literal)
    (h : Consistent r vs) (hv : l.1∈vs) (hl : r l=true) :
    decode r l.1=l.2 := by
  cases l with
  | mk v b =>
    cases b with
    | true => exact hl
    | false =>
      change r (v,true)=false
      cases e : r (v,true) with
      | false => rfl
      | true => exact (Bool.noConfusion ((h v hv e).symm.trans hl)).elim

theorem consistent_cover_model (f : Formula) (r : Rails)
    (hc : Covers r f) (hs : Consistent r (variables f)) :
    FormulaSat f (decode r) := by
  intro c hm
  obtain ⟨l,hl,ht⟩ := hc c hm
  exact ⟨l,hl,selected_true r (variables f) l hs (variable_mem f c l hm hl) ht⟩

def lhs (f : Formula) : Circuit := .either (cover f) (conflict (variables f))
def rhs (f : Formula) : Circuit := conflict (variables f)

theorem distinguishes (f : Formula) (r : Rails) :
    eval r (lhs f)≠eval r (rhs f) ↔
      Covers r f ∧ Consistent r (variables f) := by
  change (eval r (cover f) || eval r (conflict (variables f)))≠
    eval r (conflict (variables f)) ↔ _
  cases h : eval r (conflict (variables f)) with
  | true =>
    constructor
    · intro e
      have he : (eval r (cover f) || true)=true := by cases eval r (cover f) <;> rfl
      exact (e he).elim
    · intro e
      have he := (conflict_correct r _).2 e.2
      rw [h] at he
      cases he
  | false =>
    constructor
    · intro e
      have hc : eval r (cover f)=true := by
        cases z : eval r (cover f) with
        | true => rfl
        | false => exact (e rfl).elim
      exact ⟨(cover_correct r f).1 hc,(conflict_correct r _).1 h⟩
    · intro e
      have hc := (cover_correct r f).2 e.1
      rw [hc]
      intro bad
      exact Bool.noConfusion bad

theorem inequivalent_iff_sat (f : Formula) :
    (∃ r : Rails,eval r (lhs f)≠eval r (rhs f)) ↔ ∃ x : Assignment,FormulaSat f x := by
  constructor
  · intro h
    obtain ⟨r,hr⟩ := h
    have hh := (distinguishes f r).1 hr
    exact ⟨decode r,consistent_cover_model f r hh.1 hh.2⟩
  · intro h
    obtain ⟨x,hx⟩ := h
    exact ⟨rails x,(distinguishes f _).2 ⟨model_covers f x hx,rails_consistent x _⟩⟩

theorem equivalent_iff_unsat (f : Formula) :
    (∀ r : Rails,eval r (lhs f)=eval r (rhs f)) ↔
      ¬ ∃ x : Assignment,FormulaSat f x := by
  constructor
  · intro h hs
    obtain ⟨r,hr⟩ := (inequivalent_iff_sat f).2 hs
    exact hr (h r)
  · intro h r
    by_cases e : eval r (lhs f)=eval r (rhs f)
    · exact e
    · exact (h ((inequivalent_iff_sat f).1 ⟨r,e⟩)).elim

end ProctorMonotoneCircuitBarrier

#print axioms ProctorMonotoneCircuitBarrier.row_correct
#print axioms ProctorMonotoneCircuitBarrier.cover_correct
#print axioms ProctorMonotoneCircuitBarrier.conflict_correct
#print axioms ProctorMonotoneCircuitBarrier.rails_true
#print axioms ProctorMonotoneCircuitBarrier.rails_consistent
#print axioms ProctorMonotoneCircuitBarrier.model_covers
#print axioms ProctorMonotoneCircuitBarrier.selected_true
#print axioms ProctorMonotoneCircuitBarrier.consistent_cover_model
#print axioms ProctorMonotoneCircuitBarrier.distinguishes
#print axioms ProctorMonotoneCircuitBarrier.inequivalent_iff_sat
#print axioms ProctorMonotoneCircuitBarrier.equivalent_iff_unsat
