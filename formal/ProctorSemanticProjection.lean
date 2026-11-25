/-! F035: exact existential variable projection by CNF disjunction.
This avoids explicit search for a chosen variable, but may increase
representation size. No universal polynomial projection bound. -/
namespace ProctorSemanticProjection
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (update clause_alternative formula_alternative)
open ProctorGeneralBranching (restrict restriction_correct restrict_remaining shannon Satisfiable Covered)
open ProctorEnvelopeCompleteness (formula_ok every_complete)
open ProctorUnifiedReplay (validFormula)

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

theorem clause_or (c d : Clause) (x : Assignment) :
    ClauseSat (c++d) x ↔ ClauseSat c x ∨ ClauseSat d x := by
  constructor
  · intro h
    obtain ⟨l,hl,he⟩ := h
    cases append_cases l c d hl with
    | inl e => exact Or.inl ⟨l,e,he⟩
    | inr e => exact Or.inr ⟨l,e,he⟩
  · intro h
    cases h with
    | inl e =>
      obtain ⟨l,hl,he⟩ := e
      exact ⟨l,append_left l c d hl,he⟩
    | inr e =>
      obtain ⟨l,hl,he⟩ := e
      exact ⟨l,append_right l c d hl,he⟩

def rowProduct (c : Clause) : Formula → Formula
  | [] => []
  | d::ds => (c++d)::rowProduct c ds

def orProduct : Formula → Formula → Formula
  | [],_ => []
  | c::cs,g => rowProduct c g++orProduct cs g

theorem row_product_mem (c : Clause) (g : Formula) (d : Clause) (h : d∈g) :
    c++d∈rowProduct c g := by
  induction g with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head => exact List.Mem.head _
    | tail _ hm => exact List.Mem.tail _ (ih hm)

theorem row_product_origin (c : Clause) (g : Formula) (r : Clause)
    (h : r∈rowProduct c g) : ∃ d∈g,r=c++d := by
  induction g with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head => exact ⟨a,List.Mem.head _,rfl⟩
    | tail _ hm =>
      obtain ⟨d,hd,he⟩ := ih hm
      exact ⟨d,List.Mem.tail _ hd,he⟩

theorem product_mem (f g : Formula) (c d : Clause) (hc : c∈f) (hd : d∈g) :
    c++d∈orProduct f g := by
  induction f with
  | nil => cases hc
  | cons a as ih =>
    cases hc with
    | head => exact append_left _ _ _ (row_product_mem a g d hd)
    | tail _ hm => exact append_right _ _ _ (ih hm)

theorem product_origin (f g : Formula) (r : Clause)
    (h : r∈orProduct f g) : ∃ c∈f,∃ d∈g,r=c++d := by
  induction f with
  | nil => cases h
  | cons a as ih =>
    change r∈rowProduct a g++orProduct as g at h
    cases append_cases r _ _ h with
    | inl e =>
      obtain ⟨d,hd,he⟩ := row_product_origin a g r e
      exact ⟨a,List.Mem.head _,d,hd,he⟩
    | inr e =>
      obtain ⟨c,hc,d,hd,he⟩ := ih e
      exact ⟨c,List.Mem.tail _ hc,d,hd,he⟩

theorem product_correct (f g : Formula) (x : Assignment) :
    FormulaSat (orProduct f g) x ↔ FormulaSat f x ∨ FormulaSat g x := by
  constructor
  · intro h
    cases formula_alternative f x with
    | inl hf => exact Or.inl hf
    | inr hf =>
      obtain ⟨c,hc,hbad⟩ := hf
      apply Or.inr
      intro d hd
      cases (clause_or c d x).1 (h _ (product_mem f g c d hc hd)) with
      | inl e =>
        obtain ⟨l,hl,he⟩ := e
        exact (hbad l hl he).elim
      | inr e => exact e
  · intro h r hr
    obtain ⟨c,hc,d,hd,he⟩ := product_origin f g r hr
    rw [he]
    apply (clause_or c d x).2
    cases h with
    | inl hf => exact Or.inl (hf c hc)
    | inr hg => exact Or.inr (hg d hd)

def project (v : Nat) (f : Formula) : Formula :=
  orProduct (restrict v false f) (restrict v true f)

theorem project_correct (v : Nat) (f : Formula) (x : Assignment) :
    FormulaSat (project v f) x ↔ ∃ b : Bool, FormulaSat f (update x v b) := by
  constructor
  · intro h
    cases (product_correct _ _ x).1 h with
    | inl e => exact ⟨false,(restriction_correct v false f x).1 e⟩
    | inr e => exact ⟨true,(restriction_correct v true f x).1 e⟩
  · intro h
    obtain ⟨b,hb⟩ := h
    apply (product_correct _ _ x).2
    cases b with
    | false => exact Or.inl ((restriction_correct v false f x).2 hb)
    | true => exact Or.inr ((restriction_correct v true f x).2 hb)

theorem project_sat (v : Nat) (f : Formula) :
    Satisfiable (project v f) ↔ Satisfiable f := by
  constructor
  · intro h
    obtain ⟨x,hx⟩ := h
    obtain ⟨b,hb⟩ := (project_correct v f x).1 hx
    exact ⟨update x v b,hb⟩
  · intro h
    cases (shannon v f).1 h with
    | inl e =>
      obtain ⟨x,hx⟩ := e
      exact ⟨x,(product_correct _ _ x).2 (Or.inl hx)⟩
    | inr e =>
      obtain ⟨x,hx⟩ := e
      exact ⟨x,(product_correct _ _ x).2 (Or.inr hx)⟩

theorem project_remaining (v : Nat) (f : Formula) :
    ∀ r∈project v f, ∀ l∈r, l.1≠v ∧ ∃ c∈f,l∈c := by
  intro r hr l hl
  obtain ⟨a,ha,b,hb,he⟩ := product_origin _ _ r hr
  rw [he] at hl
  cases append_cases l a b hl with
  | inl e =>
    obtain ⟨c,hc,ht⟩ := restrict_remaining v false f a ha
    exact ⟨(ht l e).2,c,hc,(ht l e).1⟩
  | inr e =>
    obtain ⟨c,hc,ht⟩ := restrict_remaining v true f b hb
    exact ⟨(ht l e).2,c,hc,(ht l e).1⟩

theorem project_valid (n v : Nat) (f : Formula) (h : validFormula n f=true) :
    validFormula n (project v f)=true := by
  apply every_complete
  intro r hr
  apply every_complete
  intro l hl
  obtain ⟨_,c,hc,he⟩ := project_remaining v f r hr l hl
  exact formula_ok n f h c hc l he

private theorem len_append {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons a as ih =>
    change (as++ys).length+1=as.length+1+ys.length
    rw [ih,Nat.add_assoc as.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

theorem row_product_length (c : Clause) (g : Formula) :
    (rowProduct c g).length=g.length := by
  induction g with
  | nil => rfl
  | cons d ds ih => exact congrArg Nat.succ ih

theorem product_length (f g : Formula) :
    (orProduct f g).length=f.length*g.length := by
  induction f with
  | nil => exact (Nat.zero_mul _).symm
  | cons c cs ih =>
    change (rowProduct c g++orProduct cs g).length=(cs.length+1)*g.length
    rw [len_append,row_product_length,ih,Nat.mul_comm (cs.length+1),Nat.mul_succ,
      Nat.mul_comm g.length cs.length,Nat.add_comm g.length]

theorem project_length (v : Nat) (f : Formula) :
    (project v f).length=(restrict v false f).length*(restrict v true f).length :=
  product_length _ _

-- A pattern specifies a partial assignment. A clause's falsifying
-- assignments form such a pattern (unless the clause is tautological).
def parity : List Bool → Bool
  | [] => false
  | b::bs => if b then !(parity bs) else parity bs

inductive Matches : List (Option Bool) → List Bool → Prop where
  | nil : Matches [] []
  | fixed (b : Bool) {p xs} : Matches p xs → Matches (some b::p) (b::xs)
  | free (b : Bool) {p xs} : Matches p xs → Matches (none::p) (b::xs)

theorem parity_flip (b t : Bool) :
    (if !b then !t else t) = !(if b then !t else t) := by
  cases b <;> cases t <;> rfl

theorem parity_neg (b : Bool) (xs ys : List Bool)
    (h : parity ys= !(parity xs)) :
    parity (b::ys)= !(parity (b::xs)) := by
  change (if b then !(parity ys) else parity ys)=_
  rw [h]
  cases b <;> cases parity xs <;> rfl

-- A nonempty falsifying pattern containing a wildcard cannot
-- exclude only one parity class. Otherwise the pattern is a singleton.
theorem parity_pattern_unique (p : List (Option Bool)) (xs : List Bool)
    (h : Matches p xs)
    (constant : ∀ ys, Matches p ys → parity ys=parity xs) :
    ∀ ys, Matches p ys → ys=xs := by
  induction h with
  | nil =>
    intro ys hy
    cases hy
    rfl
  | @fixed b p xs hm ih =>
    intro ys hy
    cases hy with
    | fixed _ ht =>
      have hc : ∀ zs, Matches p zs → parity zs=parity xs := by
        intro zs hz
        have he := constant (b::zs) (Matches.fixed b hz)
        change (if b then !(parity zs) else parity zs) =
          (if b then !(parity xs) else parity xs) at he
        cases b with
        | false => exact he
        | true =>
          cases h1 : parity zs <;> cases h2 : parity xs <;>
            rw [h1,h2] at he <;> first | rfl | cases he
      exact congrArg (List.cons b) (ih hc _ ht)
  | @free b p xs hm ih =>
    have he := constant ((!b)::xs) (Matches.free (!b) hm)
    change (if !b then !(parity xs) else parity xs)=
      (if b then !(parity xs) else parity xs) at he
    rw [parity_flip] at he
    cases b <;> cases parity xs <;> cases he

end ProctorSemanticProjection

#print axioms ProctorSemanticProjection.clause_or
#print axioms ProctorSemanticProjection.row_product_mem
#print axioms ProctorSemanticProjection.row_product_origin
#print axioms ProctorSemanticProjection.product_mem
#print axioms ProctorSemanticProjection.product_origin
#print axioms ProctorSemanticProjection.product_correct
#print axioms ProctorSemanticProjection.project_correct
#print axioms ProctorSemanticProjection.project_sat
#print axioms ProctorSemanticProjection.project_remaining
#print axioms ProctorSemanticProjection.project_valid
#print axioms ProctorSemanticProjection.row_product_length
#print axioms ProctorSemanticProjection.product_length
#print axioms ProctorSemanticProjection.project_length
#print axioms ProctorSemanticProjection.parity_flip
#print axioms ProctorSemanticProjection.parity_neg
#print axioms ProctorSemanticProjection.parity_pattern_unique
