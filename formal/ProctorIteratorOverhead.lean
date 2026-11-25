/-! F034 candidate: joint iterator dispatch and structural overhead ledger.
One unit per visited word cell (including the empty terminator) and
one per constructed doubled-transition wrapper. A rejecting set bit
does not construct the next wrapper. These are source-level selected
events, not actual closure allocation or machine instructions. -/
namespace ProctorIteratorOverhead
open ProctorDecimalBitWidth (bitsValue)
open ProctorFuelFreeParser (iterWord)
open ProctorCheckedBinaryScanner (encode encode_sound)
open ProctorIteratorDispatch (Metered liftStep doubleMeter wordMeter
  word_dispatch_bound lifted_projection list_dispatch_bound)
open ProctorDataParser (listLimit)

-- First component is the previous result and dispatch ledger;
-- second component is the selected structural overhead.
def ledger {σ : Type} :
    List Bool → Metered σ → σ → (Option σ × Nat) × Nat
  | [],_,s => ((some s,0),1)
  | false::bs,step,s =>
    let q := ledger bs (doubleMeter step) s
    (q.1,q.2+2)
  | true::bs,step,s =>
    let r := step s
    match r.1 with
    | none => ((none,r.2),1)
    | some t =>
      let q := ledger bs (doubleMeter step) t
      ((q.1.1,r.2+q.1.2),q.2+2)

theorem dispatch_projection {σ : Type} (bs : List Bool)
    (step : Metered σ) (s : σ) :
    (ledger bs step s).1=wordMeter bs step s := by
  induction bs generalizing step s with
  | nil => rfl
  | cons b bs ih =>
    cases b with
    | false => exact ih (doubleMeter step) s
    | true =>
      change (match (step s).1 with
        | none => ((none,(step s).2),1)
        | some t =>
          let q := ledger bs (doubleMeter step) t
          ((q.1.1,(step s).2+q.1.2),q.2+2)).1=
        (match (step s).1 with
          | none => (none,(step s).2)
          | some t =>
            let q := wordMeter bs (doubleMeter step) t
            (q.1,(step s).2+q.2))
      cases e : (step s).1 with
      | none => rfl
      | some t =>
        change ((ledger bs (doubleMeter step) t).1.1,
          (step s).2+(ledger bs (doubleMeter step) t).1.2)=
          ((wordMeter bs (doubleMeter step) t).1,
           (step s).2+(wordMeter bs (doubleMeter step) t).2)
        rw [ih (doubleMeter step) t]

theorem overhead_bound {σ : Type} (bs : List Bool)
    (step : Metered σ) (s : σ) :
    (ledger bs step s).2≤2*bs.length+1 := by
  induction bs generalizing step s with
  | nil => exact Nat.le_refl 1
  | cons b bs ih =>
    cases b with
    | false =>
      change (ledger bs (doubleMeter step) s).2+2≤(2*bs.length+1)+2
      exact Nat.add_le_add (ih (doubleMeter step) s) (Nat.le_refl 2)
    | true =>
      change (match (step s).1 with
        | none => ((none,(step s).2),1)
        | some t =>
          let q := ledger bs (doubleMeter step) t
          ((q.1.1,(step s).2+q.1.2),q.2+2)).2≤2*(bs.length+1)+1
      cases e : (step s).1 with
      | none => exact Nat.succ_le_succ (Nat.zero_le _)
      | some t =>
        change (ledger bs (doubleMeter step) t).2+2≤(2*bs.length+1)+2
        exact Nat.add_le_add (ih (doubleMeter step) t) (Nat.le_refl 2)

theorem success_overhead_exact {σ : Type} (bs : List Bool)
    (step : Metered σ) (s out : σ)
    (h : (ledger bs step s).1.1=some out) :
    (ledger bs step s).2=2*bs.length+1 := by
  induction bs generalizing step s out with
  | nil => rfl
  | cons b bs ih =>
    cases b with
    | false =>
      change (ledger bs (doubleMeter step) s).1.1=some out at h
      change (ledger bs (doubleMeter step) s).2+2=(2*bs.length+1)+2
      exact congrArg (fun n => n+2) (ih (doubleMeter step) s out h)
    | true =>
      rw [ledger] at h ⊢
      cases e : (step s).1 with
      | none =>
        change none=some out at h
        cases h
      | some t =>
        change (ledger bs (doubleMeter step) t).1.1=some out at h
        change (ledger bs (doubleMeter step) t).2+2=(2*bs.length+1)+2
        exact congrArg (fun n => n+2) (ih (doubleMeter step) t out h)

def selectedTotal {σ : Type} (bs : List Bool) (step : Metered σ) (s : σ) : Nat :=
  let r := ledger bs step s
  r.1.2+r.2

theorem total_bound {σ : Type} (bs : List Bool) (step : Metered σ)
    (K : Nat) (h : ∀ s, (step s).2+1≤K) (s : σ) :
    selectedTotal bs step s≤K*bitsValue bs+(2*bs.length+1) := by
  have hd := word_dispatch_bound bs step K h s
  have he := overhead_bound bs step s
  unfold selectedTotal
  change (ledger bs step s).1.2+(ledger bs step s).2≤_
  rw [dispatch_projection bs step s]
  exact Nat.add_le_add hd he

theorem result_projection {σ : Type} (bs : List Bool)
    (step : σ → Option σ) (s : σ) :
    (ledger bs (liftStep step) s).1.1=iterWord bs step s := by
  rw [dispatch_projection bs (liftStep step) s]
  exact lifted_projection bs step s

theorem list_total_bound {σ : Type} (k : Nat) (c : List Bool)
    (h : encode 17 k=some c) (hk : k≤listLimit)
    (step : σ → Option σ) (s : σ) :
    selectedTotal c (liftStep step) s≤200035 := by
  have hw := (encode_sound 17 k c h).left
  have hd := list_dispatch_bound k c h hk step s
  have he := overhead_bound c (liftStep step) s
  rw [hw] at he
  unfold selectedTotal
  change (ledger c (liftStep step) s).1.2+(ledger c (liftStep step) s).2≤_
  rw [dispatch_projection c (liftStep step) s]
  exact Nat.add_le_add hd he

end ProctorIteratorOverhead

#print axioms ProctorIteratorOverhead.dispatch_projection
#print axioms ProctorIteratorOverhead.overhead_bound
#print axioms ProctorIteratorOverhead.success_overhead_exact
#print axioms ProctorIteratorOverhead.total_bound
#print axioms ProctorIteratorOverhead.result_projection
#print axioms ProctorIteratorOverhead.list_total_bound
