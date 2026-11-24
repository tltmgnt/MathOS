/-! F034: executable sparse signed parity-block checking and XOR
contradiction replay. Append after ProctorCapacityReplay. -/
namespace ProctorXorReplay
open ProctorHallDeficiency
open ProctorCapacityReplay (RefRow refCheck ref_sound every every_sound someCheck some_sound test test_sound)
open ProctorExecutableReplay (and_true_local contains contains_sound)

def bx : Bool → Bool → Bool
  | false, b => b
  | true, b => !b

def evalSupport (x : Assignment) : List Nat → Bool
  | [] => false
  | v::vs => bx (x v) (evalSupport x vs)

def falseLits (x : Assignment) : List Nat → Clause
  | [] => []
  | v::vs => (v,!x v)::falseLits x vs

def patternParity : Clause → Bool
  | [] => false
  | l::ls => bx (!l.2) (patternParity ls)

def patterns : List Nat → (Clause → Bool) → Bool
  | [], p => p []
  | v::vs, p =>
    patterns vs (fun ls => p ((v,false)::ls)) &&
    patterns vs (fun ls => p ((v,true)::ls))

theorem pattern_sound (vs : List Nat) (p : Clause → Bool)
    (h : patterns vs p = true) (x : Assignment) :
    p (falseLits x vs) = true := by
  induction vs generalizing p with
  | nil => exact h
  | cons v vs ih =>
    change (patterns vs (fun ls => p ((v,false)::ls)) &&
      patterns vs (fun ls => p ((v,true)::ls))) = true at h
    have hh := and_true_local _ _ h
    change p ((v,!x v)::falseLits x vs) = true
    cases e : x v with
    | false => exact ih _ hh.right
    | true => exact ih _ hh.left

theorem false_member (x : Assignment) (vs : List Nat) (l : Literal)
    (h : l ∈ falseLits x vs) : x l.1 ≠ l.2 := by
  induction vs with
  | nil => cases h
  | cons v vs ih =>
    change l ∈ (v,!x v)::falseLits x vs at h
    cases h with
    | head =>
      intro e
      change x v = !x v at e
      cases hv : x v with
      | false =>
        rw [hv] at e
        exact Bool.noConfusion e
      | true =>
        rw [hv] at e
        exact Bool.noConfusion e
    | tail _ hm => exact ih hm

theorem pattern_parity (x : Assignment) (vs : List Nat) :
    patternParity (falseLits x vs) = evalSupport x vs := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change bx (!(!x v)) (patternParity (falseLits x vs)) =
      bx (x v) (evalSupport x vs)
    rw [ih]
    cases x v <;> rfl

structure Block where
  support : List Nat
  rhs : Bool
  refs : List RefRow

def patternCheck (b : Block) (ls : Clause) : Bool :=
  if patternParity ls = b.rhs then true
  else someCheck (fun r => every (fun l => contains l ls) r.row) b.refs

def blockCheck (f : Formula) (b : Block) : Bool :=
  test (b.support.length ≤ 5) &&
    (every (refCheck f) b.refs && patterns b.support (patternCheck b))

theorem block_sound (f : Formula) (b : Block) (x : Assignment)
    (model : FormulaSat f x) (h : blockCheck f b = true) :
    evalSupport x b.support = b.rhs := by
  unfold blockCheck at h
  have hh := and_true_local _ _ (and_true_local _ _ h).right
  have hp := pattern_sound b.support (patternCheck b) hh.right x
  by_cases e : evalSupport x b.support = b.rhs
  · exact e
  · unfold patternCheck at hp
    rw [pattern_parity x b.support, if_neg e] at hp
    obtain ⟨r,hr,hc⟩ := some_sound _ b.refs hp
    have hm := ref_sound f r (every_sound _ b.refs hh.left r hr)
    obtain ⟨l,hl,ht⟩ := model r.row hm
    exact (false_member x b.support l
      (contains_sound _ _ (every_sound _ r.row hc l hl)) ht).elim

theorem bx_zero (a : Bool) : bx a false = a := by cases a <;> rfl

theorem bx_swap (a b c : Bool) : bx a (bx b c) = bx b (bx a c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem bx_mix (a b c : Bool) : bx a (bx a (bx b c)) = bx b c := by
  cases a <;> cases b <;> cases c <;> rfl

def toggle (v : Nat) : List Nat → List Nat
  | [] => [v]
  | a::as => if v=a then as else a::toggle v as

theorem toggle_sound (x : Assignment) (v : Nat) (vs : List Nat) :
    evalSupport x (toggle v vs) = bx (x v) (evalSupport x vs) := by
  induction vs with
  | nil => rfl
  | cons a as ih =>
    change evalSupport x (if v=a then as else a::toggle v as) =
      bx (x v) (bx (x a) (evalSupport x as))
    by_cases e : v=a
    · rw [if_pos e, e]
      cases x a <;> cases evalSupport x as <;> rfl
    · rw [if_neg e]
      change bx (x a) (evalSupport x (toggle v as)) = _
      rw [ih]
      exact bx_swap _ _ _

def combine : List Nat → List Nat → List Nat
  | [], ys => ys
  | v::vs, ys => toggle v (combine vs ys)

theorem combine_sound (x : Assignment) (a b : List Nat) :
    evalSupport x (combine a b) =
      bx (evalSupport x a) (evalSupport x b) := by
  induction a with
  | nil => rfl
  | cons v vs ih =>
    change evalSupport x (toggle v (combine vs b)) =
      bx (bx (x v) (evalSupport x vs)) (evalSupport x b)
    rw [toggle_sound, ih]
    cases x v <;> cases evalSupport x vs <;> cases evalSupport x b <;> rfl

def sumSupport : List Block → List Nat
  | [] => []
  | b::bs => combine b.support (sumSupport bs)

def sumRhs : List Block → Bool
  | [] => false
  | b::bs => bx b.rhs (sumRhs bs)

theorem sum_sound (bs : List Block) (x : Assignment)
    (h : ∀ b ∈ bs, evalSupport x b.support = b.rhs) :
    evalSupport x (sumSupport bs) = sumRhs bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    change evalSupport x (combine b.support (sumSupport bs)) =
      bx b.rhs (sumRhs bs)
    rw [combine_sound, h b (List.Mem.head _),
      ih (fun q hq => h q (List.Mem.tail _ hq))]

def xorCheck (f : Formula) (bs : List Block) : Bool :=
  every (blockCheck f) bs &&
    (test (sumSupport bs = []) && sumRhs bs)

theorem xor_check_sound (f : Formula) (bs : List Block)
    (h : xorCheck f bs = true) : ¬ ∃ x : Assignment, FormulaSat f x := by
  intro model
  obtain ⟨x,hx⟩ := model
  unfold xorCheck at h
  have hh := and_true_local _ _ h
  have hc := and_true_local _ _ hh.right
  have he := test_sound (sumSupport bs = []) hc.left
  have hs := sum_sound bs x (fun b hb =>
    block_sound f b x hx (every_sound _ bs hh.left b hb))
  rw [he] at hs
  have bad : false = true := hs.trans hc.right
  exact Bool.noConfusion bad

def checkChainXor (f : Formula) (ps : List ProctorExecutableReplay.Batch)
    (bs : List Block) : Bool :=
  ProctorExecutableReplay.chainCheck f ps &&
    xorCheck (ProctorExecutableReplay.frontier f ps) bs

theorem checked_chain_xor_refutes (f : Formula)
    (ps : List ProctorExecutableReplay.Batch) (bs : List Block)
    (h : checkChainXor f ps bs = true) :
    ¬ ∃ x : Assignment, FormulaSat f x := by
  unfold checkChainXor at h
  have hh := and_true_local _ _ h
  exact ProctorMixedInference.derived_unsat_lifts f _
    (ProctorExecutableReplay.chain_sound f ps hh.left)
    (xor_check_sound _ bs hh.right)

end ProctorXorReplay

#print axioms ProctorXorReplay.pattern_sound
#print axioms ProctorXorReplay.false_member
#print axioms ProctorXorReplay.pattern_parity
#print axioms ProctorXorReplay.block_sound
#print axioms ProctorXorReplay.bx_zero
#print axioms ProctorXorReplay.bx_swap
#print axioms ProctorXorReplay.bx_mix
#print axioms ProctorXorReplay.toggle_sound
#print axioms ProctorXorReplay.combine_sound
#print axioms ProctorXorReplay.sum_sound
#print axioms ProctorXorReplay.xor_check_sound
#print axioms ProctorXorReplay.checked_chain_xor_refutes
