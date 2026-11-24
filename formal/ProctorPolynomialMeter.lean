/-! F034: concrete polynomial inequalities for selected sub-budgets.
No assumption of a global machine model. Structural sizes count
explicit row/label occurrences, not the numeric variable bound. -/
namespace ProctorPolynomialMeter
open ProctorHallDeficiency
open ProctorExecutableReplay (lookup Step Batch tails)
open ProctorCapacityMeter (visitsBudget wordsBudget)
open ProctorXorReplay (Block toggle combine sumSupport)
open ProctorXorMeter (sumBudget combineBudget sumMeter sum_bound)
open ProctorCheckerCost (shapeBudget)
open ProctorChainMeter (parentBudget stepBudget batchBudget chainBudget chainMeter chain_bound)

-- Local constructive arithmetic identities avoid importing any
-- axiom-dependent library simplification lemmas into the strict gate.
private theorem zero_mul_local (k : Nat) : 0*k=0 := by
  induction k with
  | zero => rfl
  | succ k ih => exact ih

private theorem one_mul_local (k : Nat) : 1*k=k := by
  induction k with
  | zero => rfl
  | succ k ih => exact congrArg Nat.succ ih

private theorem add_mul_local (a b k : Nat) : (a+b)*k=a*k+b*k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change (a+b)*k+(a+b)=(a*k+a)+(b*k+b)
    rw [ih]
    calc
      (a*k+b*k)+(a+b) = a*k+(b*k+(a+b)) := Nat.add_assoc _ _ _
      _ = a*k+((b*k+a)+b) := congrArg (fun z => a*k+z) (Nat.add_assoc _ _ _).symm
      _ = a*k+((a+b*k)+b) := congrArg (fun z => a*k+(z+b)) (Nat.add_comm _ _)
      _ = a*k+(a+(b*k+b)) := congrArg (fun z => a*k+z) (Nat.add_assoc _ _ _)
      _ = (a*k+a)+(b*k+b) := (Nat.add_assoc _ _ _).symm

private theorem mul_left_mono (a b k : Nat) (h : a≤b) : a*k≤b*k := by
  induction k with
  | zero => exact Nat.le_refl 0
  | succ k ih => exact Nat.add_le_add ih h

private theorem mul_right_mono (k a b : Nat) (h : a≤b) : k*a≤k*b := by
  induction h with
  | refl => exact Nat.le_refl _
  | step h ih => exact Nat.le_trans ih (Nat.le_add_right _ _)

private theorem mul_mono {a b c d : Nat} (h : a≤b) (g : c≤d) :
    a*c≤b*d :=
  Nat.le_trans (mul_left_mono a b c h) (mul_right_mono b c d g)

theorem visits_uniform {α : Type} (q : α → Nat) (xs : List α)
    (B : Nat) (h : ∀ a, q a ≤ B) :
    visitsBudget q xs ≤ xs.length*(B+1) := by
  induction xs with
  | nil => exact Nat.zero_le _
  | cons a as ih =>
    change q a + visitsBudget q as + 1 ≤ (as.length+1)*(B+1)
    rw [add_mul_local,one_mul_local]
    calc
      q a + visitsBudget q as + 1 ≤ B + as.length*(B+1) + 1 :=
        Nat.add_le_add (Nat.add_le_add (h a) ih) (Nat.le_refl 1)
      _ = as.length*(B+1)+(B+1) := by
        rw [Nat.add_comm B (as.length*(B+1)),Nat.add_assoc]

def wordUnit (g : Nat) : Nat → Nat → Nat
  | 0,L => L
  | k+1,L => g*(wordUnit g k L+1)

theorem words_uniform (xs : Clause) (k : Nat) (q : Clause → Nat)
    (L : Nat) (h : ∀ ys, ys.length=k → q ys≤L) :
    wordsBudget xs k q ≤ wordUnit xs.length k L := by
  induction k generalizing q with
  | zero => exact h [] rfl
  | succ k ih =>
    change visitsBudget (fun a => wordsBudget xs k (fun rest => q (a::rest))) xs ≤
      xs.length*(wordUnit xs.length k L+1)
    apply visits_uniform
    intro a
    exact ih (fun rest => q (a::rest)) (fun rest hr =>
      h (a::rest) (congrArg Nat.succ hr))

theorem words_depth_three (xs : Clause) (q : Clause → Nat) (L : Nat)
    (h : ∀ ys, ys.length=3 → q ys≤L) :
    wordsBudget xs 3 q ≤
      xs.length*(xs.length*(xs.length*(L+1)+1)+1) :=
  words_uniform xs 3 q L h

theorem toggle_length (v : Nat) (vs : List Nat) :
    (toggle v vs).length ≤ vs.length+1 := by
  induction vs with
  | nil => exact Nat.le_refl 1
  | cons a as ih =>
    change (if v=a then as else a::toggle v as).length ≤ as.length+1+1
    by_cases e : v=a
    · rw [if_pos e]
      exact Nat.le_trans (Nat.le_succ _) (Nat.le_succ _)
    · rw [if_neg e]
      exact Nat.succ_le_succ ih

theorem combine_length (a b : List Nat) :
    (combine a b).length ≤ a.length+b.length := by
  induction a with
  | nil =>
    change b.length ≤ 0+b.length
    rw [Nat.zero_add] <;> exact Nat.le_refl _
  | cons v vs ih =>
    change (toggle v (combine vs b)).length ≤ (vs.length+1)+b.length
    calc
      (toggle v (combine vs b)).length ≤ (combine vs b).length+1 :=
        toggle_length v (combine vs b)
      _ ≤ (vs.length+b.length)+1 := Nat.succ_le_succ ih
      _ = (vs.length+1)+b.length := by
        calc
          (vs.length+b.length)+1 = vs.length+(b.length+1) := Nat.add_assoc _ _ _
          _ = vs.length+(1+b.length) := congrArg (fun x => vs.length+x) (Nat.add_comm _ _)
          _ = (vs.length+1)+b.length := (Nat.add_assoc _ _ _).symm

theorem combine_uniform (a b : List Nat) (B : Nat)
    (h : a.length+b.length≤B) : combineBudget a b ≤ a.length*B := by
  induction a with
  | nil => exact Nat.zero_le _
  | cons v vs ih =>
    have ht : vs.length+b.length≤B :=
      Nat.le_trans (Nat.add_le_add (Nat.le_succ vs.length) (Nat.le_refl b.length)) h
    change combineBudget vs b + (combine vs b).length ≤ (vs.length+1)*B
    rw [add_mul_local,one_mul_local]
    exact Nat.add_le_add (ih ht) (Nat.le_trans (combine_length vs b) ht)

def supportMass : List Block → Nat
  | [] => 0
  | b::bs => b.support.length + supportMass bs

theorem sum_length (bs : List Block) : (sumSupport bs).length ≤ supportMass bs := by
  induction bs with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    exact Nat.le_trans (combine_length b.support (sumSupport bs))
      (Nat.add_le_add (Nat.le_refl b.support.length) ih)

theorem sum_uniform (bs : List Block) (B : Nat)
    (h : supportMass bs≤B) : sumBudget bs ≤ supportMass bs*B := by
  induction bs with
  | nil => exact Nat.zero_le _
  | cons b bs ih =>
    have hr : supportMass bs≤B :=
      Nat.le_trans (Nat.le_add_left _ _) h
    have hc : b.support.length+(sumSupport bs).length≤B :=
      Nat.le_trans (Nat.add_le_add (Nat.le_refl b.support.length) (sum_length bs)) h
    change sumBudget bs + combineBudget b.support (sumSupport bs) ≤
      (b.support.length+supportMass bs)*B
    rw [add_mul_local,Nat.add_comm (b.support.length*B) (supportMass bs*B)]
    exact Nat.add_le_add (ih hr) (combine_uniform _ _ B hc)

theorem sum_quadratic (bs : List Block) :
    sumBudget bs ≤ supportMass bs*supportMass bs :=
  sum_uniform bs _ (Nat.le_refl _)

theorem sum_meter_quadratic (bs : List Block) :
    (sumMeter bs).2 ≤ supportMass bs*supportMass bs :=
  Nat.le_trans (sum_bound bs) (sum_quadratic bs)

def formulaMass : Formula → Nat
  | [] => 0
  | c::cs => (c.length+1)+formulaMass cs

theorem shape_closed (tail row : Clause) :
    shapeBudget tail row = row.length*(tail.length+1) := by
  induction row with
  | nil => exact (zero_mul_local _).symm
  | cons _ ls ih =>
    change shapeBudget tail ls+(tail.length+1) =
      (ls.length+1)*(tail.length+1)
    rw [ih,add_mul_local,one_mul_local]

theorem mass_rows (f : Formula) : f.length≤formulaMass f := by
  induction f with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    change cs.length+1≤(c.length+1)+formulaMass cs
    rw [Nat.add_comm (c.length+1) (formulaMass cs)]
    exact Nat.add_le_add ih (Nat.succ_le_succ (Nat.zero_le c.length))

theorem lookup_mass (f : Formula) (i : Nat) (row : Clause)
    (h : lookup f i=some row) : row.length≤formulaMass f := by
  induction f generalizing i with
  | nil => cases h
  | cons c cs ih =>
    cases i with
    | zero =>
      change some c=some row at h
      have eq := Option.some.inj h
      cases eq
      exact Nat.le_trans (Nat.le_succ _) (Nat.le_add_right _ _)
    | succ i =>
      exact Nat.le_trans (ih i h) (Nat.le_add_left _ _)

def parentUnit (B : Nat) : Nat := B+B*(B+1)
def stepUnit (B : Nat) : Nat := parentUnit B+parentUnit B

theorem parent_poly (f : Formula) (i : Nat) (t : Clause) (B : Nat)
    (hf : formulaMass f≤B) (ht : t.length≤B) :
    parentBudget f i t≤parentUnit B := by
  unfold parentBudget parentUnit
  have hrows := Nat.le_trans (mass_rows f) hf
  cases e : lookup f i with
  | none =>
    rw [Nat.add_zero]
    exact Nat.le_trans hrows (Nat.le_add_right _ _)
  | some row =>
    change f.length+shapeBudget t row≤B+B*(B+1)
    rw [shape_closed]
    exact Nat.add_le_add hrows (mul_mono
      (Nat.le_trans (lookup_mass f i row e) hf) (Nat.succ_le_succ ht))

theorem step_poly (f : Formula) (s : Step) (B : Nat)
    (hf : formulaMass f≤B) (ht : s.tail.length≤B) :
    stepBudget f s≤stepUnit B :=
  Nat.add_le_add (parent_poly f s.left s.tail B hf ht)
    (parent_poly f s.right s.tail B hf ht)

theorem batch_poly (f : Formula) (ss : Batch) (B : Nat)
    (hf : formulaMass f≤B) (hs : formulaMass (tails ss)≤B) :
    batchBudget f ss≤ss.length*stepUnit B := by
  induction ss with
  | nil => exact Nat.zero_le _
  | cons s ss ih =>
    change (s.tail.length+1)+formulaMass (tails ss)≤B at hs
    have ht : s.tail.length≤B :=
      Nat.le_trans (Nat.le_succ _) (Nat.le_trans (Nat.le_add_right _ _) hs)
    have hr : formulaMass (tails ss)≤B :=
      Nat.le_trans (Nat.le_add_left _ _) hs
    change stepBudget f s+batchBudget f ss≤(ss.length+1)*stepUnit B
    rw [add_mul_local,one_mul_local,Nat.add_comm (ss.length*stepUnit B) (stepUnit B)]
    exact Nat.add_le_add (step_poly f s B hf ht) (ih hr)

def chainMass (f : Formula) : List Batch → Nat
  | [] => formulaMass f
  | ss::rest => formulaMass f+chainMass (tails ss) rest

def chainSteps : List Batch → Nat
  | [] => 0
  | ss::rest => ss.length+chainSteps rest

theorem chain_mass_head (f : Formula) (bs : List Batch) :
    formulaMass f≤chainMass f bs := by
  cases bs with
  | nil => exact Nat.le_refl _
  | cons ss rest => exact Nat.le_add_right _ _

private theorem tails_length (ss : Batch) : (tails ss).length=ss.length := by
  induction ss with
  | nil => rfl
  | cons s ss ih => exact congrArg Nat.succ ih

private theorem chain_steps_strong (f : Formula) (bs : List Batch) :
    formulaMass f+chainSteps bs≤chainMass f bs := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl _
  | cons ss rest ih =>
    change formulaMass f+(ss.length+chainSteps rest)≤
      formulaMass f+chainMass (tails ss) rest
    apply Nat.add_le_add (Nat.le_refl _)
    have hl := mass_rows (tails ss)
    rw [tails_length] at hl
    exact Nat.le_trans (Nat.add_le_add hl (Nat.le_refl _)) (ih (tails ss))

theorem chain_steps_mass (f : Formula) (bs : List Batch) :
    chainSteps bs≤chainMass f bs :=
  Nat.le_trans (Nat.le_add_left _ _) (chain_steps_strong f bs)

theorem chain_uniform (f : Formula) (bs : List Batch) (B : Nat)
    (h : chainMass f bs≤B) : chainBudget f bs≤chainSteps bs*stepUnit B := by
  induction bs generalizing f with
  | nil => exact Nat.zero_le _
  | cons ss rest ih =>
    change formulaMass f+chainMass (tails ss) rest≤B at h
    have hf : formulaMass f≤B := Nat.le_trans (Nat.le_add_right _ _) h
    have hr : chainMass (tails ss) rest≤B := Nat.le_trans (Nat.le_add_left _ _) h
    have hs := Nat.le_trans (chain_mass_head (tails ss) rest) hr
    change batchBudget f ss+chainBudget (tails ss) rest≤
      (ss.length+chainSteps rest)*stepUnit B
    rw [add_mul_local]
    exact Nat.add_le_add (batch_poly f ss B hf hs) (ih (tails ss) hr)

theorem chain_polynomial (f : Formula) (bs : List Batch) :
    chainBudget f bs≤chainMass f bs*stepUnit (chainMass f bs) :=
  Nat.le_trans (chain_uniform f bs _ (Nat.le_refl _))
    (mul_mono (chain_steps_mass f bs) (Nat.le_refl _))

theorem chain_meter_polynomial (f : Formula) (bs : List Batch) :
    (chainMeter f bs).2≤chainMass f bs*stepUnit (chainMass f bs) :=
  Nat.le_trans (chain_bound f bs) (chain_polynomial f bs)

end ProctorPolynomialMeter

#print axioms ProctorPolynomialMeter.visits_uniform
#print axioms ProctorPolynomialMeter.words_uniform
#print axioms ProctorPolynomialMeter.words_depth_three
#print axioms ProctorPolynomialMeter.toggle_length
#print axioms ProctorPolynomialMeter.combine_length
#print axioms ProctorPolynomialMeter.combine_uniform
#print axioms ProctorPolynomialMeter.sum_length
#print axioms ProctorPolynomialMeter.sum_uniform
#print axioms ProctorPolynomialMeter.sum_quadratic
#print axioms ProctorPolynomialMeter.sum_meter_quadratic
#print axioms ProctorPolynomialMeter.shape_closed
#print axioms ProctorPolynomialMeter.mass_rows
#print axioms ProctorPolynomialMeter.lookup_mass
#print axioms ProctorPolynomialMeter.parent_poly
#print axioms ProctorPolynomialMeter.step_poly
#print axioms ProctorPolynomialMeter.batch_poly
#print axioms ProctorPolynomialMeter.chain_mass_head
#print axioms ProctorPolynomialMeter.chain_steps_mass
#print axioms ProctorPolynomialMeter.chain_uniform
#print axioms ProctorPolynomialMeter.chain_polynomial
#print axioms ProctorPolynomialMeter.chain_meter_polynomial
