/-! F034 candidate: input-sensitive amortization for the verified
binary iterator. Successful transitions pay from decreasing potential;
a single rejecting transition may use an additive allowance. Doubling
increases the rejecting allowance by one, not by a factor of two.
Selected resource events only. -/
namespace ProctorInputSensitiveIterator
open ProctorIteratorDispatch (Metered doubleMeter wordMeter)
open ProctorIteratorOverhead (ledger selectedTotal dispatch_projection overhead_bound)
open ProctorFuelFreeParser (State)
open ProctorParserMeterCompose (advanceMeter natMeter wordRun listMeter)
open ProctorCheckedBinaryScanner (encode encode_sound)
open ProctorDataParser (listLimit)

def Safe {σ : Type} (step : Metered σ) (potential : σ → Nat) (D : Nat) : Prop :=
  (∀ s t, (step s).1=some t → ((step s).2+1)+potential t≤potential s) ∧
  (∀ s, (step s).1=none → (step s).2+1≤potential s+D)

private theorem add_chain (a b x y : Nat) (ha : a+y≤x)
    (hb : b≤y) : a+b≤x :=
  Nat.le_trans (Nat.add_le_add (Nat.le_refl a) hb) ha

private theorem add_extra (a b x y z : Nat) (ha : a+y≤x)
    (hb : b≤y+z) : a+b≤x+z := by
  calc
    a+b ≤ a+(y+z) := Nat.add_le_add (Nat.le_refl _) hb
    _ = (a+y)+z := (Nat.add_assoc _ _ _).symm
    _ ≤ x+z := Nat.add_le_add ha (Nat.le_refl _)

private theorem pair_charge (a b : Nat) : a+b+1+1=(a+1)+(b+1) := by
  calc
    (a+b)+1+1 = (a+(b+1))+1 :=
      congrArg (fun n => n+1) (Nat.add_assoc a b 1)
    _ = a+((b+1)+1) := Nat.add_assoc _ _ _
    _ = a+(1+(b+1)) := congrArg (fun n => a+n) (Nat.add_comm _ _)
    _ = (a+1)+(b+1) := (Nat.add_assoc _ _ _).symm

private theorem double_none {σ : Type} (step : Metered σ) (s : σ)
    (e : (step s).1=none) :
    doubleMeter step s=(none,(step s).2+1) := by
  change (match (step s).1 with
    | none => (none,(step s).2+1)
    | some t => ((step t).1,(step s).2+(step t).2+1))=_
  rw [e]

private theorem double_some {σ : Type} (step : Metered σ) (s t : σ)
    (e : (step s).1=some t) :
    doubleMeter step s=((step t).1,(step s).2+(step t).2+1) := by
  change (match (step s).1 with
    | none => (none,(step s).2+1)
    | some u => ((step u).1,(step s).2+(step u).2+1))=_
  rw [e]

theorem double_safe {σ : Type} (step : Metered σ) (potential : σ → Nat)
    (D : Nat) (h : Safe step potential D) :
    Safe (doubleMeter step) potential (D+1) := by
  constructor
  · intro s out hs
    cases e : (step s).1 with
    | none =>
      rw [double_none step s e] at hs
      cases hs
    | some t =>
      rw [double_some step s t e] at hs
      change (step t).1=some out at hs
      rw [double_some step s t e]
      change ((step s).2+(step t).2+1+1)+potential out≤potential s
      rw [pair_charge,Nat.add_assoc]
      exact add_chain _ _ _ _ (h.1 s t e) (h.1 t out hs)
  · intro s hs
    cases e : (step s).1 with
    | none =>
      rw [double_none step s e]
      change (step s).2+1+1≤potential s+(D+1)
      rw [← Nat.add_assoc]
      exact Nat.succ_le_succ (h.2 s e)
    | some t =>
      rw [double_some step s t e] at hs
      change (step t).1=none at hs
      rw [double_some step s t e]
      change (step s).2+(step t).2+1+1≤potential s+(D+1)
      rw [pair_charge]
      exact Nat.le_trans (add_extra _ _ _ _ _ (h.1 s t e) (h.2 t hs))
        (Nat.le_succ _)

private theorem word_none {σ : Type} (bs : List Bool) (step : Metered σ)
    (s : σ) (e : (step s).1=none) :
    wordMeter (true::bs) step s=(none,(step s).2) := by
  change (match (step s).1 with
    | none => (none,(step s).2)
    | some t => ((wordMeter bs (doubleMeter step) t).1,
        (step s).2+(wordMeter bs (doubleMeter step) t).2))=_
  rw [e]

private theorem word_some {σ : Type} (bs : List Bool) (step : Metered σ)
    (s t : σ) (e : (step s).1=some t) :
    wordMeter (true::bs) step s=((wordMeter bs (doubleMeter step) t).1,
      (step s).2+(wordMeter bs (doubleMeter step) t).2) := by
  change (match (step s).1 with
    | none => (none,(step s).2)
    | some u => ((wordMeter bs (doubleMeter step) u).1,
        (step s).2+(wordMeter bs (doubleMeter step) u).2))=_
  rw [e]

private theorem drop_one (a b x : Nat) (h : (a+1)+b≤x) : a+b≤x :=
  Nat.le_trans (Nat.add_le_add (Nat.le_succ a) (Nat.le_refl b)) h

private theorem shift (a b : Nat) : (a+1)+b=a+(b+1) := by
  calc
    (a+1)+b = a+(1+b) := Nat.add_assoc _ _ _
    _ = a+(b+1) := congrArg (fun n => a+n) (Nat.add_comm _ _)

theorem word_success {σ : Type} (bs : List Bool) (step : Metered σ)
    (potential : σ → Nat) (D : Nat) (h : Safe step potential D)
    (s out : σ) (hs : (wordMeter bs step s).1=some out) :
    (wordMeter bs step s).2+potential out≤potential s := by
  induction bs generalizing step D s out with
  | nil =>
    change some s=some out at hs
    cases hs
    change 0+potential s≤potential s
    rw [Nat.zero_add]
    exact Nat.le_refl _
  | cons b bs ih =>
    have hd := double_safe step potential D h
    cases b with
    | false => exact ih (doubleMeter step) (D+1) hd s out hs
    | true =>
      cases e : (step s).1 with
      | none =>
        rw [word_none bs step s e] at hs
        cases hs
      | some t =>
        rw [word_some bs step s t e] at hs
        change (wordMeter bs (doubleMeter step) t).1=some out at hs
        rw [word_some bs step s t e]
        change (step s).2+(wordMeter bs (doubleMeter step) t).2+potential out≤potential s
        rw [Nat.add_assoc]
        exact add_chain _ _ _ _ (drop_one _ _ _ (h.1 s t e))
          (ih (doubleMeter step) (D+1) hd t out hs)

theorem word_bound {σ : Type} (bs : List Bool) (step : Metered σ)
    (potential : σ → Nat) (D : Nat) (h : Safe step potential D) (s : σ) :
    (wordMeter bs step s).2≤potential s+(D+bs.length) := by
  induction bs generalizing step D s with
  | nil => exact Nat.zero_le _
  | cons b bs ih =>
    have hd := double_safe step potential D h
    have eq := shift D bs.length
    cases b with
    | false =>
      change (wordMeter bs (doubleMeter step) s).2≤potential s+(D+(bs.length+1))
      rw [← eq]
      exact ih (doubleMeter step) (D+1) hd s
    | true =>
      cases e : (step s).1 with
      | none =>
        rw [word_none bs step s e]
        change (step s).2≤potential s+(D+(bs.length+1))
        exact Nat.le_trans (Nat.le_trans (Nat.le_succ _) (h.2 s e))
          (Nat.add_le_add (Nat.le_refl _) (Nat.le_add_right _ _))
      | some t =>
        rw [word_some bs step s t e]
        change (step s).2+(wordMeter bs (doubleMeter step) t).2≤
          potential s+(D+(bs.length+1))
        rw [← eq]
        exact add_extra _ _ _ _ _ (drop_one _ _ _ (h.1 s t e))
          (ih (doubleMeter step) (D+1) hd t)

theorem joint_bound {σ : Type} (bs : List Bool) (step : Metered σ)
    (potential : σ → Nat) (D : Nat) (h : Safe step potential D) (s : σ) :
    selectedTotal bs step s≤(potential s+(D+bs.length))+(2*bs.length+1) := by
  change (ledger bs step s).1.2+(ledger bs step s).2≤_
  rw [dispatch_projection]
  exact Nat.add_le_add (word_bound bs step potential D h s) (overhead_bound bs step s)

def natPotential (s : State Nat) : Nat := 3*s.2.length

theorem nat_safe : Safe (advanceMeter natMeter) natPotential 3 := by
  constructor
  · intro s out hs
    cases s with
    | mk acc ts =>
      cases ts with
      | nil => cases hs
      | cons a rest =>
        change some (a::acc,rest)=some out at hs
        cases hs
        change 3+3*rest.length≤3*rest.length+3
        rw [Nat.add_comm 3 (3*rest.length)]
        exact Nat.le_refl _
  · intro s hs
    cases s with
    | mk acc ts =>
      cases ts with
      | nil => exact Nat.le_refl 3
      | cons a rest => cases hs

theorem nat_word_bound (c : List Bool) (ts : List Nat) :
    (wordRun natMeter c ts).2≤(3*ts.length+(3+c.length))+(2*c.length+1) :=
  joint_bound c (advanceMeter natMeter) natPotential 3 nat_safe ([],ts)

theorem nat_list_bound (input : List Nat) :
    (listMeter natMeter input).2≤3*input.length+56 := by
  cases input with
  | nil => exact Nat.succ_le_succ (Nat.zero_le _)
  | cons k ts =>
    change (if k≤listLimit then
      match encode 17 k with
      | none => (none,1)
      | some c => ((wordRun natMeter c ts).1,(wordRun natMeter c ts).2+1)
      else (none,1)).2≤3*(ts.length+1)+56
    by_cases hk : k≤listLimit
    · rw [if_pos hk]
      cases e : encode 17 k with
      | none => exact Nat.succ_le_succ (Nat.zero_le _)
      | some c =>
        have hb := nat_word_bound c ts
        rw [(encode_sound 17 k c e).left] at hb
        change (wordRun natMeter c ts).2+1≤(3*ts.length+3)+56
        have he : (3*ts.length+(3+17))+(2*17+1)=3*ts.length+55 :=
          Nat.add_assoc (3*ts.length) 20 35
        rw [he] at hb
        have hh := Nat.succ_le_succ hb
        exact Nat.le_trans hh
          (Nat.add_le_add (Nat.le_add_right (3*ts.length) 3) (Nat.le_refl 56))
    · rw [if_neg hk]
      exact Nat.succ_le_succ (Nat.zero_le _)

end ProctorInputSensitiveIterator

#print axioms ProctorInputSensitiveIterator.double_safe
#print axioms ProctorInputSensitiveIterator.word_success
#print axioms ProctorInputSensitiveIterator.word_bound
#print axioms ProctorInputSensitiveIterator.joint_bound
#print axioms ProctorInputSensitiveIterator.nat_safe
#print axioms ProctorInputSensitiveIterator.nat_word_bound
#print axioms ProctorInputSensitiveIterator.nat_list_bound
