/-! A total supply of sound branch certificates gives ordinary
UNSAT traces. This is a logical theorem, not a polynomial size claim.
No assumption of total certificate coverage is asserted. -/
namespace ProctorChoiceCertificates
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (variables variable_mem)
open ProctorGeneralBranching (Satisfiable Covered restrict restrict_cover restriction_correct shannon)

abbrev Verifier := Formula → Nat → Bool → List Nat → Bool

def Sound (check : Verifier) : Prop :=
  ∀ f v b c, check f v b c = true →
    Satisfiable f → Satisfiable (restrict v b f)

def TotalSupply (check : Verifier) : Prop :=
  ∀ f v, ∃ b c, check f v b c = true

inductive Trace (check : Verifier) : List Nat → Formula → Prop where
  | done (f : Formula) (h : ([] : Clause) ∈ f) : Trace check [] f
  | step (v : Nat) (vs : List Nat) (f : Formula) (b : Bool) (c : List Nat)
      (h : check f v b c = true)
      (tail : Trace check vs (restrict v b f)) : Trace check (v::vs) f

theorem empty_unsat (f : Formula) (he : ([] : Clause) ∈ f) :
    ¬ Satisfiable f := by
  intro hs
  obtain ⟨x,hx⟩ := hs
  obtain ⟨l,hl,_⟩ := hx [] he
  cases hl

theorem restriction_unsat (f : Formula) (v : Nat) (b : Bool)
    (hu : ¬ Satisfiable f) : ¬ Satisfiable (restrict v b f) := by
  intro h
  obtain ⟨x,hx⟩ := h
  exact hu ⟨_,(restriction_correct v b f x).1 hx⟩

theorem covered_unsat_empty (f : Formula) (hc : Covered [] f)
    (hu : ¬ Satisfiable f) : ([] : Clause) ∈ f := by
  cases f with
  | nil =>
    exact (hu ⟨fun _ => false,fun c h => nomatch h⟩).elim
  | cons c cs =>
    cases c with
    | nil => exact List.Mem.head _
    | cons l ls =>
      have h := hc (l::ls) (List.Mem.head _) l (List.Mem.head _)
      cases h

theorem trace_sound (check : Verifier) (hs : Sound check)
    (vs : List Nat) (f : Formula) (t : Trace check vs f) :
    ¬ Satisfiable f := by
  induction t with
  | done f he => exact empty_unsat f he
  | step v vs f b c h tail ih =>
    intro hm
    exact ih (hs f v b c h hm)

theorem trace_complete (check : Verifier) (ht : TotalSupply check)
    (vs : List Nat) (f : Formula) (hc : Covered vs f)
    (hu : ¬ Satisfiable f) : Trace check vs f := by
  induction vs generalizing f with
  | nil => exact Trace.done f (covered_unsat_empty f hc hu)
  | cons v vs ih =>
    obtain ⟨b,c,h⟩ := ht f v
    exact Trace.step v vs f b c h
      (ih (restrict v b f) (restrict_cover v b vs f hc)
        (restriction_unsat f v b hu))

theorem trace_iff (check : Verifier) (hs : Sound check)
    (ht : TotalSupply check) (f : Formula) :
    Trace check (variables f) f ↔ ¬ Satisfiable f := by
  constructor
  · intro h
    exact trace_sound check hs _ f h
  · intro h
    exact trace_complete check ht _ f
      (fun c hc l hl => variable_mem f c l hc hl) h

end ProctorChoiceCertificates

#print axioms ProctorChoiceCertificates.empty_unsat
#print axioms ProctorChoiceCertificates.restriction_unsat
#print axioms ProctorChoiceCertificates.covered_unsat_empty
#print axioms ProctorChoiceCertificates.trace_sound
#print axioms ProctorChoiceCertificates.trace_complete
#print axioms ProctorChoiceCertificates.trace_iff
