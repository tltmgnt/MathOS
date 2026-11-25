/-! F034 candidate: selected dispatch ledger for binary transition
composition. Charge one per base transition invocation and one per
doubled-transition wrapper invocation. Failure short-circuits.
The meter does not charge word traversal, closure construction,
allocation, underlying transition work, or compiler/runtime costs. -/
namespace ProctorIteratorDispatch
open ProctorDecimalBitWidth (bitsValue)
open ProctorFuelFreeParser (doubleStep iterWord)
open ProctorCheckedBinaryScanner (encode encode_sound)
open ProctorTerminalPolynomial (mul_mono)
open ProctorDataParser (listLimit)

abbrev Metered (σ : Type) := σ → Option σ × Nat

def liftStep {σ : Type} (step : σ → Option σ) : Metered σ :=
  fun s => (step s,1)

def doubleMeter {σ : Type} (step : Metered σ) (s : σ) : Option σ × Nat :=
  let r := step s
  match r.1 with
  | none => (none,r.2+1)
  | some t =>
    let q := step t
    (q.1,r.2+q.2+1)

def wordMeter {σ : Type} : List Bool → Metered σ → σ → Option σ × Nat
  | [],_,s => (some s,0)
  | false::bs,step,s => wordMeter bs (doubleMeter step) s
  | true::bs,step,s =>
    let r := step s
    match r.1 with
    | none => (none,r.2)
    | some t =>
      let q := wordMeter bs (doubleMeter step) t
      (q.1,r.2+q.2)

theorem double_projection {σ : Type} (step : Metered σ) (plain : σ → Option σ)
    (h : ∀ s, (step s).1=plain s) (s : σ) :
    (doubleMeter step s).1=doubleStep plain s := by
  unfold doubleMeter doubleStep
  rw [← h s]
  cases e : (step s).1 with
  | none => rfl
  | some t => exact h t

theorem word_projection {σ : Type} (bs : List Bool) (step : Metered σ)
    (plain : σ → Option σ) (h : ∀ s, (step s).1=plain s) (s : σ) :
    (wordMeter bs step s).1=iterWord bs plain s := by
  induction bs generalizing step plain s with
  | nil => rfl
  | cons b bs ih =>
    cases b with
    | false =>
      exact ih (doubleMeter step) (doubleStep plain)
        (double_projection step plain h) s
    | true =>
      rw [wordMeter,iterWord,← h s]
      cases e : (step s).1 with
      | none => rfl
      | some t =>
        exact ih (doubleMeter step) (doubleStep plain)
          (double_projection step plain h) t

-- Potential +1 absorbs the extra wrapper invocation under doubling.
theorem double_potential {σ : Type} (step : Metered σ) (K : Nat)
    (h : ∀ s, (step s).2+1≤K) (s : σ) :
    (doubleMeter step s).2+1≤K+K := by
  rw [doubleMeter]
  cases e : (step s).1 with
  | none =>
    change (step s).2+1+1≤K+K
    have one : 1≤K := Nat.le_trans
      (Nat.succ_le_succ (Nat.zero_le (step s).2)) (h s)
    exact Nat.add_le_add (h s) one
  | some t =>
    change (step s).2+(step t).2+1+1≤K+K
    calc
      (step s).2+(step t).2+1+1 =
          ((step s).2+1)+((step t).2+1) := by
        rw [Nat.add_assoc (step s).2 (step t).2 1,
          Nat.add_comm (step t).2 1, ← Nat.add_assoc (step s).2 1 (step t).2,
          Nat.add_assoc ((step s).2+1) (step t).2 1]
      _ ≤ K+K := Nat.add_le_add (h s) (h t)

private theorem double_scale (K n : Nat) : (K+K)*n=K*(2*n) := by
  have e : K+K=K*2 := by
    change K+K=0+K+K
    rw [Nat.zero_add]
  rw [e,Nat.mul_assoc]

private theorem set_scale (K n : Nat) : K+(K+K)*n=K*(1+2*n) := by
  rw [double_scale,Nat.add_comm 1 (2*n)]
  change K+K*(2*n)=K*(2*n)+K
  exact Nat.add_comm _ _

theorem word_dispatch_bound {σ : Type} (bs : List Bool) (step : Metered σ)
    (K : Nat) (h : ∀ s, (step s).2+1≤K) (s : σ) :
    (wordMeter bs step s).2≤K*bitsValue bs := by
  induction bs generalizing step K s with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    have hd := double_potential step K h
    cases b with
    | false =>
      change (wordMeter bs (doubleMeter step) s).2≤K*(0+2*bitsValue bs)
      rw [Nat.zero_add,← double_scale]
      exact ih (doubleMeter step) (K+K) hd s
    | true =>
      rw [wordMeter]
      cases e : (step s).1 with
      | none =>
        change (step s).2≤K*(1+2*bitsValue bs)
        rw [← set_scale]
        exact Nat.le_trans (Nat.le_trans (Nat.le_succ _) (h s))
          (Nat.le_add_right _ _)
      | some t =>
        change (step s).2+(wordMeter bs (doubleMeter step) t).2≤K*(1+2*bitsValue bs)
        rw [← set_scale]
        exact Nat.add_le_add (Nat.le_trans (Nat.le_succ _) (h s))
          (ih (doubleMeter step) (K+K) hd t)

theorem lifted_projection {σ : Type} (bs : List Bool) (step : σ → Option σ) (s : σ) :
    (wordMeter bs (liftStep step) s).1=iterWord bs step s :=
  word_projection bs (liftStep step) step (fun _ => rfl) s

theorem lifted_dispatch_bound {σ : Type} (bs : List Bool) (step : σ → Option σ) (s : σ) :
    (wordMeter bs (liftStep step) s).2≤2*bitsValue bs :=
  word_dispatch_bound bs (liftStep step) 2 (fun _ => Nat.le_refl 2) s

theorem list_dispatch_bound {σ : Type} (k : Nat) (c : List Bool)
    (h : encode 17 k=some c) (hk : k≤listLimit)
    (step : σ → Option σ) (s : σ) :
    (wordMeter c (liftStep step) s).2≤200000 := by
  have hv := (encode_sound 17 k c h).right
  have hb := lifted_dispatch_bound c step s
  rw [hv] at hb
  exact Nat.le_trans hb (mul_mono (Nat.le_refl 2) hk)

end ProctorIteratorDispatch

#print axioms ProctorIteratorDispatch.double_projection
#print axioms ProctorIteratorDispatch.word_projection
#print axioms ProctorIteratorDispatch.double_potential
#print axioms ProctorIteratorDispatch.word_dispatch_bound
#print axioms ProctorIteratorDispatch.lifted_projection
#print axioms ProctorIteratorDispatch.lifted_dispatch_bound
#print axioms ProctorIteratorDispatch.list_dispatch_bound
