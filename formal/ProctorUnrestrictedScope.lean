/-! F024-A: affine relational expressiveness barrier and local nonlinear clause compiler.
Replay after ProctorGF2.lean. No decision-reduction or general SAT time theorem. -/
namespace ProctorUnrestrictedScope
open ProctorGF2

theorem dot_comm_scope (a b : List Bool) : dot a b = dot b a := by
  induction a generalizing b with
  | nil => cases b <;> rfl
  | cons x xs ih =>
    cases b with
    | nil => rfl
    | cons y ys =>
      change bx (x && y) (dot xs ys) = bx (y && x) (dot ys xs)
      rw [ih ys]
      cases x <;> cases y <;> rfl

theorem dot_add_right_scope (a b c : List Bool) :
    dot a (addVec b c) = bx (dot a b) (dot a c) :=
  (dot_comm_scope a (addVec b c)).trans
    ((dot_add b c a).trans
      ((congrArg (fun v => bx v (dot c a)) (dot_comm_scope b a)).trans
        (congrArg (bx (dot a b)) (dot_comm_scope c a))))

def combine (a b c : List Bool) : List Bool := addVec (addVec a b) c

theorem bx_three (b : Bool) : bx (bx b b) b = b := by
  cases b <;> rfl

theorem row_closed (r : Row) (a b c : List Bool)
    (ha : Sat r a) (hb : Sat r b) (hc : Sat r c) :
    Sat r (combine a b c) := by
  change dot r.coeff (addVec (addVec a b) c) = r.rhs
  rw [dot_add_right_scope, dot_add_right_scope]
  change dot r.coeff a = r.rhs at ha
  change dot r.coeff b = r.rhs at hb
  change dot r.coeff c = r.rhs at hc
  rw [ha, hb, hc]
  exact bx_three r.rhs

theorem system_closed (rs : List Row) (a b c : List Bool)
    (ha : AllSat rs a) (hb : AllSat rs b) (hc : AllSat rs c) :
    AllSat rs (combine a b c) := by
  induction rs with
  | nil => exact True.intro
  | cons r rs ih =>
    exact ⟨row_closed r a b c ha.left hb.left hc.left,
      ih ha.right hb.right hc.right⟩

-- Project three designated original coordinates, allowing arbitrary auxiliary
-- lists. This stronger statement even allows zero-padded unequal tail lengths.
def EncodesOr3 (rs : List Row) : Prop :=
  ∀ a b c : Bool, (a || b || c) = true ↔
    ∃ z : List Bool, AllSat rs (a :: b :: c :: z)

theorem or_not_affine_projection (rs : List Row) : ¬ EncodesOr3 rs := by
  intro h
  obtain ⟨u, hu⟩ := (h true false false).mp rfl
  obtain ⟨v, hv⟩ := (h false true false).mp rfl
  obtain ⟨w, hw⟩ := (h true true false).mp rfl
  have bad := system_closed rs _ _ _ hu hv hw
  change AllSat rs (false :: false :: false :: combine u v w) at bad
  have e := (h false false false).mpr ⟨combine u v w, bad⟩
  exact Bool.noConfusion e

-- Explicit nonlinear relations are retained, rather than replacing
-- multiplication by an unconstrained auxiliary symbol.
def violation (a b c : Bool) : Bool := ((!a) && (!b)) && (!c)

theorem clause_encoding_correct (a b c : Bool) :
    (a || b || c) = true ↔ violation a b c = false := by
  cases a <;> cases b <;> cases c <;> decide

theorem clause_gate_iff (a b c : Bool) :
    (a || b || c) = true ↔
      ∃ t z : Bool, t = ((!a) && (!b)) ∧
        z = (t && (!c)) ∧ z = false := by
  constructor
  · intro h
    exact ⟨(!a) && (!b), violation a b c, rfl, rfl,
      (clause_encoding_correct a b c).mp h⟩
  · intro h
    obtain ⟨t, z, ht, hz, hf⟩ := h
    apply (clause_encoding_correct a b c).mpr
    unfold violation
    rw [← ht, ← hz, hf]

end ProctorUnrestrictedScope
#print axioms ProctorUnrestrictedScope.dot_comm_scope
#print axioms ProctorUnrestrictedScope.dot_add_right_scope
#print axioms ProctorUnrestrictedScope.bx_three
#print axioms ProctorUnrestrictedScope.row_closed
#print axioms ProctorUnrestrictedScope.system_closed
#print axioms ProctorUnrestrictedScope.or_not_affine_projection
#print axioms ProctorUnrestrictedScope.clause_encoding_correct
#print axioms ProctorUnrestrictedScope.clause_gate_iff
