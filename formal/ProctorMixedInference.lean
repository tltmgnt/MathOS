/-! F034: semantic composition of paired resolution with any sound
UNSAT certificate. Append after the verified Hall/capacity sources. -/
namespace ProctorMixedInference
open ProctorHallDeficiency

theorem paired_sound (x : Assignment) (p : Nat) (tail : Clause)
    (hp : ClauseSat ((p,true)::tail) x)
    (hn : ClauseSat ((p,false)::tail) x) : ClauseSat tail x := by
  cases e : x p with
  | false =>
    obtain ⟨l,hl,ht⟩ := hp
    cases hl with
    | head => exact (Bool.noConfusion (e.symm.trans ht))
    | tail _ hm => exact ⟨l,hm,ht⟩
  | true =>
    obtain ⟨l,hl,ht⟩ := hn
    cases hl with
    | head => exact (Bool.noConfusion (e.symm.trans ht))
    | tail _ hm => exact ⟨l,hm,ht⟩

def Entails (original derived : Formula) : Prop :=
  ∀ x, FormulaSat original x → FormulaSat derived x

theorem paired_batch_entails (original derived : Formula)
    (parents : ∀ tail ∈ derived, ∃ p : Nat,
      ((p,true)::tail) ∈ original ∧ ((p,false)::tail) ∈ original) :
    Entails original derived := by
  intro x hx tail ht
  obtain ⟨p,hp,hn⟩ := parents tail ht
  exact paired_sound x p tail (hx _ hp) (hx _ hn)

theorem derived_unsat_lifts (original derived : Formula)
    (entails : Entails original derived)
    (refutes : ¬ ∃ x : Assignment, FormulaSat derived x) :
    ¬ ∃ x : Assignment, FormulaSat original x := by
  intro h
  obtain ⟨x,hx⟩ := h
  exact refutes ⟨x,entails x hx⟩

theorem append_sat (a b : Formula) (x : Assignment)
    (ha : FormulaSat a x) (hb : FormulaSat b x) :
    FormulaSat (a++b) x := by
  induction a with
  | nil => exact hb
  | cons c cs ih =>
    intro row hr
    change row ∈ c::(cs++b) at hr
    cases hr with
    | head => exact ha c (List.Mem.head _)
    | tail _ hm =>
      exact ih (fun d hd => ha d (List.Mem.tail _ hd)) row hm

theorem augmented_unsat_lifts (original derived : Formula)
    (entails : Entails original derived)
    (refutes : ¬ ∃ x : Assignment, FormulaSat (original++derived) x) :
    ¬ ∃ x : Assignment, FormulaSat original x := by
  intro h
  obtain ⟨x,hx⟩ := h
  exact refutes ⟨x,append_sat original derived x hx (entails x hx)⟩

end ProctorMixedInference

#print axioms ProctorMixedInference.paired_sound
#print axioms ProctorMixedInference.paired_batch_entails
#print axioms ProctorMixedInference.derived_unsat_lifts
#print axioms ProctorMixedInference.append_sat
#print axioms ProctorMixedInference.augmented_unsat_lifts
