/-! F034: replay semantics for set-normalized paired clauses and
finite batches. This is not the Python parser or a verified executable. -/
namespace ProctorPairedReplay
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Holds opposite opposite_conflict)
open ProctorMixedInference (Entails)

def ParentShape (row tail : Clause) (pivot : Literal) : Prop :=
  ∀ l ∈ row, l = pivot ∨ l ∈ tail

theorem parent_tail (x : Assignment) (row tail : Clause) (pivot : Literal)
    (shape : ParentShape row tail pivot)
    (falsePivot : ¬ Holds x pivot) (sat : ClauseSat row x) :
    ClauseSat tail x := by
  obtain ⟨l,hl,ht⟩ := sat
  cases shape l hl with
  | inl eq =>
    cases eq
    exact (falsePivot ht).elim
  | inr hm => exact ⟨l,hm,ht⟩

theorem paired_set_sound (x : Assignment) (a b tail : Clause) (p : Literal)
    (sa : ParentShape a tail p)
    (sb : ParentShape b tail (opposite p))
    (ha : ClauseSat a x) (hb : ClauseSat b x) : ClauseSat tail x := by
  cases p with
  | mk v bit =>
    cases bit with
    | false =>
      cases e : x v with
      | false =>
        exact parent_tail x b tail (opposite (v,false)) sb
          (fun h => opposite_conflict x (v,false) e h) hb
      | true =>
        exact parent_tail x a tail (v,false) sa
          (fun h => Bool.noConfusion (e.symm.trans h)) ha
    | true =>
      cases e : x v with
      | false =>
        exact parent_tail x a tail (v,true) sa
          (fun h => Bool.noConfusion (e.symm.trans h)) ha
      | true =>
        exact parent_tail x b tail (opposite (v,true)) sb
          (fun h => opposite_conflict x (v,true) e h) hb

def BatchEvidence (original derived : Formula) : Prop :=
  ∀ tail ∈ derived, ∃ a ∈ original, ∃ b ∈ original, ∃ p : Literal,
    ParentShape a tail p ∧ ParentShape b tail (opposite p)

theorem batch_set_entails (original derived : Formula)
    (e : BatchEvidence original derived) : Entails original derived := by
  intro x hx tail ht
  obtain ⟨a,ha,b,hb,p,sa,sb⟩ := e tail ht
  exact paired_set_sound x a b tail p sa sb (hx _ ha) (hx _ hb)

inductive Chain : Formula → Formula → Prop where
  | refl (f : Formula) : Chain f f
  | next {a b c : Formula} : Chain a b → BatchEvidence b c → Chain a c

theorem chain_entails (original derived : Formula) (h : Chain original derived) :
    Entails original derived := by
  induction h with
  | refl f =>
    intro x hx
    exact hx
  | next h e ih =>
    intro x hx
    exact batch_set_entails _ _ e x (ih x hx)

theorem chain_unsat_lifts (original derived : Formula)
    (h : Chain original derived)
    (refutes : ¬ ∃ x : Assignment, FormulaSat derived x) :
    ¬ ∃ x : Assignment, FormulaSat original x :=
  ProctorMixedInference.derived_unsat_lifts original derived
    (chain_entails original derived h) refutes

end ProctorPairedReplay

#print axioms ProctorPairedReplay.parent_tail
#print axioms ProctorPairedReplay.paired_set_sound
#print axioms ProctorPairedReplay.batch_set_entails
#print axioms ProctorPairedReplay.chain_entails
#print axioms ProctorPairedReplay.chain_unsat_lifts
