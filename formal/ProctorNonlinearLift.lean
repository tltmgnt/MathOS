/-! F035: exact monomial expansion and the gap between arbitrary
linearized moments and multiplicatively consistent Boolean assignments.
No bounded-degree completeness claim. -/
namespace ProctorNonlinearLift
open ProctorHallDeficiency
open ProctorXorReplay (bx)
open ProctorAffineBarrier (falseFactor falseProduct product_zero)

abbrev Monomial := List Nat
abbrev Polynomial := List Monomial
abbrev Moments := Monomial → Bool

def monomial (x : Assignment) : Monomial → Bool
  | [] => true
  | v::vs => x v && monomial x vs

def evaluate (m : Moments) : Polynomial → Bool
  | [] => false
  | t::ts => bx (m t) (evaluate m ts)

theorem evaluate_append (m : Moments) (p q : Polynomial) :
    evaluate m (p++q)=bx (evaluate m p) (evaluate m q) := by
  induction p with
  | nil => rfl
  | cons t ts ih =>
    change bx (m t) (evaluate m (ts++q))=
      bx (bx (m t) (evaluate m ts)) (evaluate m q)
    rw [ih]
    cases m t <;> cases evaluate m ts <;> cases evaluate m q <;> rfl

def multiplyVar (v : Nat) (p : Polynomial) : Polynomial :=
  p.map (List.cons v)

theorem multiply_eval (x : Assignment) (v : Nat) (p : Polynomial) :
    evaluate (monomial x) (multiplyVar v p)=
      (x v && evaluate (monomial x) p) := by
  induction p with
  | nil =>
    change false=(x v && false)
    cases x v <;> rfl
  | cons t ts ih =>
    change bx (x v && monomial x t)
      (evaluate (monomial x) (multiplyVar v ts))=
      (x v && bx (monomial x t) (evaluate (monomial x) ts))
    rw [ih]
    cases x v <;> cases monomial x t <;> cases evaluate (monomial x) ts <;> rfl

def expand : Clause → Polynomial
  | [] => [[]]
  | (v,b)::ls =>
    let p := expand ls
    if b then p++multiplyVar v p else multiplyVar v p

theorem expand_exact (x : Assignment) (c : Clause) :
    evaluate (monomial x) (expand c)=falseProduct x c := by
  induction c with
  | nil => rfl
  | cons l ls ih =>
    cases l with
    | mk v b =>
      cases b with
      | false =>
        change evaluate (monomial x) (multiplyVar v (expand ls))=
          (bx (x v) false && falseProduct x ls)
        rw [multiply_eval,ih]
        cases x v <;> rfl
      | true =>
        change evaluate (monomial x) (expand ls++multiplyVar v (expand ls))=
          (bx (x v) true && falseProduct x ls)
        rw [evaluate_append,multiply_eval,ih]
        cases x v <;> cases falseProduct x ls <;> rfl

theorem expanded_clause (x : Assignment) (c : Clause) :
    evaluate (monomial x) (expand c)=false ↔ ClauseSat c x := by
  rw [expand_exact]
  exact product_zero x c

def Relaxed (f : Formula) (m : Moments) : Prop :=
  m []=true ∧ ∀ c∈f,evaluate m (expand c)=false

theorem relaxation_contains_models (f : Formula) (x : Assignment)
    (h : FormulaSat f x) : Relaxed f (monomial x) :=
  ⟨rfl,fun c hc => (expanded_clause x c).2 (h c hc)⟩

theorem lift_sound (f : Formula) (x : Assignment) (c : Clause)
    (hf : FormulaSat f x) (hc : c∈f) (v : Nat) :
    evaluate (monomial x) (multiplyVar v (expand c))=false := by
  rw [multiply_eval,(expanded_clause x c).2 (hf c hc)]
  cases x v <;> rfl

-- A pseudo-moment assignment can satisfy every original linearized
-- equation without arising from any Boolean assignment.
def trap : Formula :=
  [[(1,false)],[(2,false)],[(3,false)],[(1,true),(2,true),(3,true)]]

def pseudo : Moments :=
  fun m => if m=[] then true else if m=[1,2,3] then true else false

theorem relaxed_trap : Relaxed trap pseudo := by
  constructor
  · rfl
  · intro c hc
    change c∈[[(1,false)],[(2,false)],[(3,false)],[(1,true),(2,true),(3,true)]] at hc
    cases hc with
    | head => rfl
    | tail _ h1 =>
      cases h1 with
      | head => rfl
      | tail _ h2 =>
        cases h2 with
        | head => rfl
        | tail _ h3 =>
          cases h3 with
          | head => rfl
          | tail _ h4 => cases h4

private theorem unit_value (x : Assignment) (v : Nat)
    (h : ClauseSat [(v,false)] x) : x v=false := by
  obtain ⟨l,hl,he⟩ := h
  cases hl with
  | head => exact he
  | tail _ hm => cases hm

theorem trap_unsat : ¬ ∃ x : Assignment, FormulaSat trap x := by
  intro h
  obtain ⟨x,hx⟩ := h
  have h1 := unit_value x 1 (hx _ (List.Mem.head _))
  have h2 := unit_value x 2 (hx _ (List.Mem.tail _ (List.Mem.head _)))
  have h3 := unit_value x 3 (hx _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _))))
  obtain ⟨l,hl,he⟩ := hx _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.tail _ (List.Mem.head _))))
  change l∈[(1,true),(2,true),(3,true)] at hl
  cases hl with
  | head => exact Bool.noConfusion (h1.symm.trans he)
  | tail _ hm =>
    cases hm with
    | head => exact Bool.noConfusion (h2.symm.trans he)
    | tail _ hn =>
      cases hn with
      | head => exact Bool.noConfusion (h3.symm.trans he)
      | tail _ hz => cases hz

theorem no_moment_realization :
    ¬ ∃ x : Assignment, ∀ t : Monomial, monomial x t=pseudo t := by
  intro h
  obtain ⟨x,hx⟩ := h
  have h1 := hx [1]
  have h2 := hx [1,2,3]
  change (x 1 && true)=false at h1
  change (x 1 && (x 2 && (x 3 && true)))=true at h2
  cases he : x 1 with
  | false => rw [he] at h2; cases h2
  | true => rw [he] at h1; cases h1

end ProctorNonlinearLift

#print axioms ProctorNonlinearLift.evaluate_append
#print axioms ProctorNonlinearLift.multiply_eval
#print axioms ProctorNonlinearLift.expand_exact
#print axioms ProctorNonlinearLift.expanded_clause
#print axioms ProctorNonlinearLift.relaxation_contains_models
#print axioms ProctorNonlinearLift.lift_sound
#print axioms ProctorNonlinearLift.relaxed_trap
#print axioms ProctorNonlinearLift.trap_unsat
#print axioms ProctorNonlinearLift.no_moment_realization
