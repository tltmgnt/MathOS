/-! F034: unified typed UNSAT replay and explicit original-input binding.
The trusted caller supplies the expected formula independently of the
certificate envelope. This is not an external text parser. -/
namespace ProctorUnifiedReplay
open ProctorHallDeficiency
open ProctorExecutableReplay (Batch Step chainCheck frontier chain_sound and_true_local)
open ProctorCapacityReplay (test test_sound every every_sound)
open ProctorMixedInference (Entails)

inductive Terminal where
  | empty
  | capacity (c : ProctorCapacityReplay.Certificate)
  | xor (bs : List ProctorXorReplay.Block)

def terminalCheck (f : Formula) : Terminal → Bool
  | .empty => ProctorExecutableReplay.hasEmpty f
  | .capacity c => ProctorCapacityReplay.capacityCheck f c
  | .xor bs => ProctorXorReplay.xorCheck f bs

theorem terminal_sound (f : Formula) (t : Terminal)
    (h : terminalCheck f t = true) : ¬ ∃ x : Assignment, FormulaSat f x := by
  cases t with
  | empty =>
    intro model
    obtain ⟨x,hx⟩ := model
    obtain ⟨l,hl,_⟩ := hx [] (ProctorExecutableReplay.empty_member f h)
    cases hl
  | capacity c => exact ProctorCapacityReplay.capacity_check_sound f c h
  | xor bs => exact ProctorXorReplay.xor_check_sound f bs h

structure Proof where
  batches : List Batch
  augmented : Bool
  terminal : Terminal

def target (f : Formula) (p : Proof) : Formula :=
  if p.augmented then f ++ frontier f p.batches else frontier f p.batches

theorem target_entails (f : Formula) (p : Proof)
    (h : chainCheck f p.batches = true) : Entails f (target f p) := by
  intro x hx
  have hf := chain_sound f p.batches h x hx
  unfold target
  cases e : p.augmented with
  | false => exact hf
  | true => exact ProctorMixedInference.append_sat _ _ x hx hf

def check (f : Formula) (p : Proof) : Bool :=
  chainCheck f p.batches && terminalCheck (target f p) p.terminal

theorem check_sound (f : Formula) (p : Proof)
    (h : check f p = true) : ¬ ∃ x : Assignment, FormulaSat f x := by
  unfold check at h
  have hh := and_true_local _ _ h
  exact ProctorMixedInference.derived_unsat_lifts f _
    (target_entails f p hh.left) (terminal_sound _ p.terminal hh.right)

def validId (n v : Nat) : Bool := test (0 < v) && test (v ≤ n)

def validClause (n : Nat) (c : Clause) : Bool :=
  every (fun l => validId n l.1) c

def validFormula (n : Nat) (f : Formula) : Bool :=
  every (validClause n) f

def validRefs (n : Nat) (rs : List ProctorCapacityReplay.RefRow) : Bool :=
  every (fun r => validClause n r.row) rs

def validTerminal (n : Nat) : Terminal → Bool
  | .empty => true
  | .capacity c =>
    validRefs n c.demands && (validRefs n c.conflicts &&
      every (fun g => validClause n g.literals) c.groups)
  | .xor bs =>
    every (fun b => every (validId n) b.support && validRefs n b.refs) bs

def validProof (n : Nat) (p : Proof) : Bool :=
  every (fun batch => every (fun s : Step =>
    validId n s.pivot && validClause n s.tail) batch) p.batches &&
    validTerminal n p.terminal

structure Envelope where
  variableBound : Nat
  original : Formula
  proof : Proof

/-- Compare typed ordered CNFs, including duplicate rows and literal order.
Do not use a producer-supplied digest as the input identity. -/
def boundCheck (n : Nat) (expected : Formula) (e : Envelope) : Bool :=
  test (n = e.variableBound) &&
  (test (expected = e.original) &&
  (validFormula n expected &&
  (validProof n e.proof && check expected e.proof)))

theorem bound_sound (n : Nat) (expected : Formula) (e : Envelope)
    (h : boundCheck n expected e = true) :
    ¬ ∃ x : Assignment, FormulaSat expected x := by
  unfold boundCheck at h
  have h1 := and_true_local _ _ h
  have h2 := and_true_local _ _ h1.right
  have h3 := and_true_local _ _ h2.right
  have h4 := and_true_local _ _ h3.right
  exact check_sound expected e.proof h4.right

theorem binding_exact (n : Nat) (expected : Formula) (e : Envelope)
    (h : boundCheck n expected e = true) :
    n = e.variableBound ∧ expected = e.original := by
  unfold boundCheck at h
  have hh := and_true_local _ _ h
  exact ⟨test_sound _ hh.left, test_sound _ (and_true_local _ _ hh.right).left⟩

theorem original_range_sound (n : Nat) (expected : Formula) (e : Envelope)
    (h : boundCheck n expected e = true) :
    ∀ c ∈ expected, ∀ l ∈ c, 0 < l.1 ∧ l.1 ≤ n := by
  unfold boundCheck at h
  have hh := and_true_local _ _ (and_true_local _ _ (and_true_local _ _ h).right).right
  intro c hc l hl
  have hv := every_sound _ c (every_sound _ expected hh.left c hc) l hl
  have hr := and_true_local _ _ hv
  exact ⟨test_sound _ hr.left,test_sound _ hr.right⟩

end ProctorUnifiedReplay

#print axioms ProctorUnifiedReplay.terminal_sound
#print axioms ProctorUnifiedReplay.target_entails
#print axioms ProctorUnifiedReplay.check_sound
#print axioms ProctorUnifiedReplay.bound_sound
#print axioms ProctorUnifiedReplay.binding_exact
#print axioms ProctorUnifiedReplay.original_range_sound
