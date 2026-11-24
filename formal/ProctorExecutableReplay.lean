/-! F034: executable, Boolean paired-replay checker with a soundness
theorem. Claimed tails are explicit; every parent literal must be the
appropriate pivot or occur in the tail. This checker deliberately
accepts weakening and does not require Python's exact tail equality.
Append after ProctorPairedReplay.lean. -/
namespace ProctorExecutableReplay
open ProctorHallDeficiency
open ProctorCapacityDeficiency (opposite)
open ProctorPairedReplay (ParentShape BatchEvidence)
open ProctorMixedInference (Entails)

theorem and_true_local (a b : Bool) (h : (a && b) = true) :
    a = true ∧ b = true := by
  cases a <;> cases b <;> first | exact ⟨rfl,rfl⟩ | exact Bool.noConfusion h

def lookup : Formula → Nat → Option Clause
  | [], _ => none
  | c::_, 0 => some c
  | _::cs, i+1 => lookup cs i

theorem lookup_mem (f : Formula) (i : Nat) (c : Clause)
    (h : lookup f i = some c) : c ∈ f := by
  induction f generalizing i with
  | nil => cases h
  | cons a as ih =>
    cases i with
    | zero =>
      change some a = some c at h
      have e := Option.some.inj h
      cases e
      exact List.Mem.head _
    | succ i =>
      exact List.Mem.tail _ (ih i h)

def contains (l : Literal) : Clause → Bool
  | [] => false
  | a::as => if l=a then true else contains l as

theorem contains_sound (l : Literal) (c : Clause)
    (h : contains l c = true) : l ∈ c := by
  induction c with
  | nil => exact Bool.noConfusion h
  | cons a as ih =>
    change (if l=a then true else contains l as) = true at h
    by_cases e : l=a
    · cases e
      exact List.Mem.head _
    · rw [if_neg e] at h
      exact List.Mem.tail _ (ih h)

def shapeCheck (pivot : Literal) (tail : Clause) : Clause → Bool
  | [] => true
  | l::ls =>
    if l=pivot then shapeCheck pivot tail ls
    else if contains l tail then shapeCheck pivot tail ls else false

theorem shape_sound (row tail : Clause) (pivot : Literal)
    (h : shapeCheck pivot tail row = true) : ParentShape row tail pivot := by
  induction row with
  | nil =>
    intro l hl
    cases hl
  | cons a as ih =>
    change (if a=pivot then shapeCheck pivot tail as
      else if contains a tail then shapeCheck pivot tail as else false) = true at h
    by_cases e : a=pivot
    · rw [if_pos e] at h
      intro l hl
      cases hl with
      | head => exact Or.inl e
      | tail _ hm => exact ih h l hm
    · rw [if_neg e] at h
      cases hc : contains a tail with
      | false =>
        rw [hc] at h
        exact Bool.noConfusion h
      | true =>
        rw [hc] at h
        intro l hl
        cases hl with
        | head => exact Or.inr (contains_sound a tail hc)
        | tail _ hm => exact ih h l hm

structure Step where
  left : Nat
  right : Nat
  pivot : Nat
  tail : Clause

abbrev Batch := List Step

def stepCheck (f : Formula) (s : Step) : Bool :=
  match lookup f s.left, lookup f s.right with
  | some a, some b =>
    shapeCheck (s.pivot,true) s.tail a && shapeCheck (s.pivot,false) s.tail b
  | _, _ => false

theorem step_sound (f : Formula) (s : Step)
    (h : stepCheck f s = true) :
    ∃ a ∈ f, ∃ b ∈ f, ∃ p : Literal,
      ParentShape a s.tail p ∧ ParentShape b s.tail (opposite p) := by
  unfold stepCheck at h
  cases ha : lookup f s.left with
  | none =>
    rw [ha] at h
    exact Bool.noConfusion h
  | some a =>
    rw [ha] at h
    cases hb : lookup f s.right with
    | none =>
      rw [hb] at h
      exact Bool.noConfusion h
    | some b =>
      rw [hb] at h
      change (shapeCheck (s.pivot,true) s.tail a &&
        shapeCheck (s.pivot,false) s.tail b) = true at h
      have hh := and_true_local _ _ h
      exact ⟨a,lookup_mem f s.left a ha,b,lookup_mem f s.right b hb,
        (s.pivot,true),shape_sound a s.tail _ hh.left,
        shape_sound b s.tail _ hh.right⟩

def tails : Batch → Formula
  | [] => []
  | s::ss => s.tail :: tails ss

def batchCheck (f : Formula) : Batch → Bool
  | [] => true
  | s::ss => stepCheck f s && batchCheck f ss

theorem batch_sound (f : Formula) (ss : Batch)
    (h : batchCheck f ss = true) : BatchEvidence f (tails ss) := by
  induction ss with
  | nil =>
    intro c hc
    cases hc
  | cons s ss ih =>
    change (stepCheck f s && batchCheck f ss) = true at h
    have hh := and_true_local _ _ h
    intro c hc
    change c ∈ s.tail :: tails ss at hc
    cases hc with
    | head => exact step_sound f s hh.left
    | tail _ hm => exact ih hh.right c hm

def frontier (f : Formula) : List Batch → Formula
  | [] => f
  | ss::rest => frontier (tails ss) rest

def chainCheck (f : Formula) : List Batch → Bool
  | [] => true
  | ss::rest => batchCheck f ss && chainCheck (tails ss) rest

theorem chain_sound (f : Formula) (bs : List Batch)
    (h : chainCheck f bs = true) : Entails f (frontier f bs) := by
  induction bs generalizing f with
  | nil =>
    intro x hx
    exact hx
  | cons ss rest ih =>
    change (batchCheck f ss && chainCheck (tails ss) rest) = true at h
    have hh := and_true_local _ _ h
    intro x hx
    exact ih (tails ss) hh.right x
      (ProctorPairedReplay.batch_set_entails f (tails ss)
        (batch_sound f ss hh.left) x hx)

def hasEmpty : Formula → Bool
  | [] => false
  | []::_ => true
  | (_::_)::cs => hasEmpty cs

theorem empty_member (f : Formula) (h : hasEmpty f = true) :
    ([] : Clause) ∈ f := by
  induction f with
  | nil => exact Bool.noConfusion h
  | cons c cs ih =>
    cases c with
    | nil => exact List.Mem.head _
    | cons a as => exact List.Mem.tail _ (ih h)

def checkEmpty (f : Formula) (bs : List Batch) : Bool :=
  chainCheck f bs && hasEmpty (frontier f bs)

/-- A fully executable Boolean UNSAT checker for the empty-clause
terminal, as opposed to a semantic theorem with assumed replay evidence. -/
theorem checked_empty_refutes (f : Formula) (bs : List Batch)
    (h : checkEmpty f bs = true) :
    ¬ ∃ x : Assignment, FormulaSat f x := by
  intro model
  obtain ⟨x,hx⟩ := model
  unfold checkEmpty at h
  have hh := and_true_local _ _ h
  have hf := chain_sound f bs hh.left x hx
  obtain ⟨l,hl,_⟩ := hf [] (empty_member _ hh.right)
  cases hl

end ProctorExecutableReplay

#print axioms ProctorExecutableReplay.lookup_mem
#print axioms ProctorExecutableReplay.contains_sound
#print axioms ProctorExecutableReplay.shape_sound
#print axioms ProctorExecutableReplay.step_sound
#print axioms ProctorExecutableReplay.batch_sound
#print axioms ProctorExecutableReplay.chain_sound
#print axioms ProctorExecutableReplay.empty_member
#print axioms ProctorExecutableReplay.checked_empty_refutes

#print axioms ProctorExecutableReplay.and_true_local
