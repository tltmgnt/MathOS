/-! F034 candidate: exact selected iterator charges on success.
Prove the successful invocation count previously tested only by
fixtures. No claim about runtime calls, allocation or machine cost. -/
namespace ProctorIteratorExact
open ProctorDecimalBitWidth (bitsValue)
open ProctorIteratorDispatch (Metered liftStep doubleMeter wordMeter lifted_dispatch_bound)
open ProctorIteratorOverhead (ledger selectedTotal dispatch_projection success_overhead_exact)
open ProctorCheckedBinaryScanner (encode encode_sound)

def ones : List Bool → Nat
  | [] => 0
  | false::bs => ones bs
  | true::bs => ones bs+1

private theorem rearrange (a b c : Nat) :
    (a+b)+c+1=(a+1)+(b+c) := by
  calc
    (a+b)+c+1 = (a+(b+c))+1 :=
      congrArg (fun n => n+1) (Nat.add_assoc a b c)
    _ = a+((b+c)+1) := Nat.add_assoc a (b+c) 1
    _ = a+(1+(b+c)) := congrArg (fun n => a+n) (Nat.add_comm (b+c) 1)
    _ = (a+1)+(b+c) := (Nat.add_assoc a 1 (b+c)).symm

theorem double_exact {σ : Type} (step : Metered σ) (K : Nat)
    (h : ∀ s t, (step s).1=some t → (step s).2+1=K)
    (s out : σ) (hs : (doubleMeter step s).1=some out) :
    (doubleMeter step s).2+1=K+K := by
  rw [doubleMeter] at hs ⊢
  cases e : (step s).1 with
  | none =>
    rw [e] at hs
    change none=some out at hs
    cases hs
  | some t =>
    rw [e] at hs
    change (step t).1=some out at hs
    change (step s).2+(step t).2+1+1=K+K
    calc
      (step s).2+(step t).2+1+1 =
          ((step s).2+1)+((step t).2+1) :=
        rearrange (step s).2 (step t).2 1
      _ = K+K := by rw [h s t e,h t out hs]

private theorem double_scale (K n : Nat) : (K+K)*n=K*(2*n) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change (K+K)*n+(K+K)=(K*(2*n)+K)+K
    rw [ih]
    exact (Nat.add_assoc (K*(2*n)) K K).symm

private theorem set_scale (K n : Nat) : K+(K+K)*n=K*(1+2*n) := by
  rw [double_scale,Nat.add_comm 1 (2*n)]
  change K+K*(2*n)=K*(2*n)+K
  exact Nat.add_comm _ _

theorem word_exact {σ : Type} (bs : List Bool) (step : Metered σ)
    (K : Nat) (h : ∀ s t, (step s).1=some t → (step s).2+1=K)
    (s out : σ) (hs : (wordMeter bs step s).1=some out) :
    (wordMeter bs step s).2+ones bs=K*bitsValue bs := by
  induction bs generalizing step K s out with
  | nil => rfl
  | cons b bs ih =>
    have hd := double_exact step K h
    cases b with
    | false =>
      change (wordMeter bs (doubleMeter step) s).1=some out at hs
      change (wordMeter bs (doubleMeter step) s).2+ones bs=K*(0+2*bitsValue bs)
      rw [Nat.zero_add,← double_scale]
      exact ih (doubleMeter step) (K+K) hd s out hs
    | true =>
      rw [wordMeter] at hs ⊢
      cases e : (step s).1 with
      | none =>
        rw [e] at hs
        change none=some out at hs
        cases hs
      | some t =>
        rw [e] at hs
        change (wordMeter bs (doubleMeter step) t).1=some out at hs
        change (step s).2+(wordMeter bs (doubleMeter step) t).2+(ones bs+1)=
          K*(1+2*bitsValue bs)
        have ht := ih (doubleMeter step) (K+K) hd t out hs
        calc
          (step s).2+(wordMeter bs (doubleMeter step) t).2+(ones bs+1) =
              ((step s).2+(wordMeter bs (doubleMeter step) t).2)+ones bs+1 :=
            (Nat.add_assoc ((step s).2+(wordMeter bs (doubleMeter step) t).2) (ones bs) 1).symm
          _ = ((step s).2+1)+((wordMeter bs (doubleMeter step) t).2+ones bs) :=
            rearrange _ _ _
          _ = K+(K+K)*bitsValue bs := by rw [h s t e,ht]
          _ = K*(1+2*bitsValue bs) := set_scale K _

theorem unit_exact {σ : Type} (bs : List Bool) (step : σ → Option σ)
    (s out : σ) (hs : (wordMeter bs (liftStep step) s).1=some out) :
    (wordMeter bs (liftStep step) s).2+ones bs=2*bitsValue bs :=
  word_exact bs (liftStep step) 2 (fun _ _ _ => rfl) s out hs

theorem joint_exact {σ : Type} (bs : List Bool) (step : σ → Option σ)
    (s out : σ) (hs : (ledger bs (liftStep step) s).1.1=some out) :
    selectedTotal bs (liftStep step) s+ones bs=
      2*bitsValue bs+(2*bs.length+1) := by
  have hw := hs
  rw [dispatch_projection bs (liftStep step) s] at hw
  have hd := unit_exact bs step s out hw
  have he := success_overhead_exact bs (liftStep step) s out hs
  change ((ledger bs (liftStep step) s).1.2+(ledger bs (liftStep step) s).2)+ones bs=_
  rw [he,dispatch_projection bs (liftStep step) s]
  let d := (wordMeter bs (liftStep step) s).2
  let o := 2*bs.length+1
  change (d+o)+ones bs=2*bitsValue bs+o
  calc
    (d+o)+ones bs = d+(o+ones bs) := Nat.add_assoc _ _ _
    _ = d+(ones bs+o) := congrArg (fun n => d+n) (Nat.add_comm _ _)
    _ = (d+ones bs)+o := (Nat.add_assoc _ _ _).symm
    _ = 2*bitsValue bs+o := congrArg (fun n => n+o) hd

theorem encoded_exact {σ : Type} (k : Nat) (c : List Bool)
    (hc : encode 17 k=some c) (step : σ → Option σ)
    (s out : σ) (hs : (ledger c (liftStep step) s).1.1=some out) :
    selectedTotal c (liftStep step) s+ones c=2*k+35 := by
  have h := joint_exact c step s out hs
  have he := encode_sound 17 k c hc
  rw [he.left,he.right] at h
  exact h

end ProctorIteratorExact

#print axioms ProctorIteratorExact.double_exact
#print axioms ProctorIteratorExact.word_exact
#print axioms ProctorIteratorExact.unit_exact
#print axioms ProctorIteratorExact.joint_exact
#print axioms ProctorIteratorExact.encoded_exact
