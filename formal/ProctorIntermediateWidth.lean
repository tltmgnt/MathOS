/-! F034 candidate: closure of selected intermediate checker operands
under an arbitrary identifier ceiling, plus guarded capacity bounds.
No dependency on pending decoded-width or binary reference candidates.
No complete machine cost or certificate completeness claim. -/
namespace ProctorIntermediateWidth
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch tails frontier lookup lookup_mem and_true_local)
open ProctorUnifiedReplay (Proof target)
open ProctorXorReplay (Block toggle combine sumSupport falseLits)
open ProctorCapacityDeficiency (Group totalCapacity)
open ProctorCapacityReplay (RefRow Certificate getAt getAt_mem demandAt indices
  every every_sound test_sound groupCheck capacityCheck)
open ProctorCheckedBinaryScanner (cap)
open ProctorTerminalPolynomial (mul_mono)

def ClauseFit (K : Nat) (c : Clause) : Prop := ∀ l ∈ c, l.1<K
def FormulaFit (K : Nat) (f : Formula) : Prop := ∀ c ∈ f, ClauseFit K c
def BatchFit (K : Nat) (b : Batch) : Prop := ∀ s ∈ b, ClauseFit K s.tail
def SupportFit (K : Nat) (vs : List Nat) : Prop := ∀ v ∈ vs, v<K

theorem lookup_fit (K : Nat) (f : Formula) (i : Nat) (c : Clause)
    (hf : FormulaFit K f) (h : lookup f i=some c) : ClauseFit K c :=
  hf c (lookup_mem f i c h)

theorem tails_fit (K : Nat) (b : Batch) (h : BatchFit K b) :
    FormulaFit K (tails b) := by
  induction b with
  | nil => intro c hc; cases hc
  | cons s ss ih =>
    intro c hc
    change c ∈ s.tail::tails ss at hc
    cases hc with
    | head => exact h s (List.Mem.head _)
    | tail _ hm => exact ih (fun t ht => h t (List.Mem.tail _ ht)) c hm

theorem frontier_fit (K : Nat) (f : Formula) (bs : List Batch)
    (hf : FormulaFit K f) (hb : ∀ b ∈ bs, BatchFit K b) :
    FormulaFit K (frontier f bs) := by
  induction bs generalizing f with
  | nil => exact hf
  | cons b bs ih =>
    exact ih (tails b) (tails_fit K b (hb b (List.Mem.head _)))
      (fun q hq => hb q (List.Mem.tail _ hq))

theorem append_fit (K : Nat) (a b : Formula)
    (ha : FormulaFit K a) (hb : FormulaFit K b) :
    FormulaFit K (a++b) := by
  induction a with
  | nil => exact hb
  | cons c cs ih =>
    intro d hd
    change d ∈ c::(cs++b) at hd
    cases hd with
    | head => exact ha c (List.Mem.head _)
    | tail _ hm => exact ih (fun e he => ha e (List.Mem.tail _ he)) d hm

theorem target_fit (K : Nat) (f : Formula) (p : Proof)
    (hf : FormulaFit K f) (hb : ∀ b ∈ p.batches, BatchFit K b) :
    FormulaFit K (target f p) := by
  have h := frontier_fit K f p.batches hf hb
  unfold target
  cases p.augmented with
  | false => exact h
  | true => exact append_fit K f (frontier f p.batches) hf h

theorem demand_fit (K : Nat) (ds : List RefRow) (i : Nat)
    (h : ∀ r ∈ ds, ClauseFit K r.row) : ClauseFit K (demandAt ds i) := by
  unfold demandAt
  cases e : getAt ds i with
  | none => intro l hl; cases hl
  | some r => exact h r (getAt_mem ds i r e)

theorem false_lits_fit (K : Nat) (x : Assignment) (vs : List Nat)
    (h : SupportFit K vs) : ClauseFit K (falseLits x vs) := by
  induction vs with
  | nil => intro l hl; cases hl
  | cons v vs ih =>
    intro l hl
    change l ∈ (v,!x v)::falseLits x vs at hl
    cases hl with
    | head => exact h v (List.Mem.head _)
    | tail _ hm => exact ih (fun n hn => h n (List.Mem.tail _ hn)) l hm

theorem toggle_fit (K v : Nat) (vs : List Nat)
    (hv : v<K) (h : SupportFit K vs) : SupportFit K (toggle v vs) := by
  induction vs with
  | nil =>
    intro n hn
    change n ∈ [v] at hn
    cases hn with
    | head => exact hv
    | tail _ hm => cases hm
  | cons a as ih =>
    rw [toggle]
    by_cases e : v=a
    · rw [if_pos e]
      exact fun n hn => h n (List.Mem.tail _ hn)
    · rw [if_neg e]
      intro n hn
      cases hn with
      | head => exact h a (List.Mem.head _)
      | tail _ hm => exact ih (fun b hb => h b (List.Mem.tail _ hb)) n hm

theorem combine_fit (K : Nat) (a b : List Nat)
    (ha : SupportFit K a) (hb : SupportFit K b) :
    SupportFit K (combine a b) := by
  induction a with
  | nil => exact hb
  | cons v vs ih =>
    exact toggle_fit K v (combine vs b) (ha v (List.Mem.head _))
      (ih (fun n hn => ha n (List.Mem.tail _ hn)))

theorem sum_support_fit (K : Nat) (bs : List Block)
    (h : ∀ b ∈ bs, SupportFit K b.support) : SupportFit K (sumSupport bs) := by
  induction bs with
  | nil => intro n hn; cases hn
  | cons b bs ih =>
    exact combine_fit K b.support (sumSupport bs) (h b (List.Mem.head _))
      (ih (fun q hq => h q (List.Mem.tail _ hq)))

theorem index_lt (d i : Nat) (h : i ∈ indices d) : i<d := by
  induction d with
  | zero => cases h
  | succ d ih =>
    change i ∈ d::indices d at h
    cases h with
    | head => exact Nat.lt_succ_self d
    | tail _ hm => exact Nat.lt_trans (ih hm) (Nat.lt_succ_self d)

theorem index_fit (d : Nat) (h : d≤100000) :
    SupportFit (cap 17) (indices d) := by
  intro i hi
  exact Nat.lt_trans (index_lt d i hi)
    (Nat.lt_of_le_of_lt h (by decide : 100000<cap 17))

-- These bounds are conditional on guard success, not on the mere
-- representability of a possibly malformed input capacity.
theorem group_guard (refs : List RefRow) (g : Group)
    (h : groupCheck refs g=true) : g.cap≤2 := by
  unfold groupCheck at h
  exact test_sound _ (and_true_local _ _ h).left

theorem group_word_bound (refs : List RefRow) (g : Group)
    (h : groupCheck refs g=true) : g.cap+1≤3 :=
  Nat.succ_le_succ (group_guard refs g h)

theorem total_bound (gs : List Group) (h : ∀ g ∈ gs, g.cap≤2) :
    totalCapacity gs≤2*gs.length := by
  induction gs with
  | nil => exact Nat.le_refl 0
  | cons g gs ih =>
    change g.cap+totalCapacity gs≤2*gs.length+2
    rw [Nat.add_comm g.cap (totalCapacity gs)]
    exact Nat.add_le_add (ih (fun q hq => h q (List.Mem.tail _ hq)))
      (h g (List.Mem.head _))

theorem capacity_groups (f : Formula) (c : Certificate)
    (h : capacityCheck f c=true) : ∀ g ∈ c.groups, g.cap≤2 := by
  unfold capacityCheck at h
  have h1 := and_true_local _ _ h
  have h2 := and_true_local _ _ h1.right
  have h3 := and_true_local _ _ h2.right
  intro g hg
  exact group_guard c.conflicts g (every_sound _ c.groups h3.left g hg)

theorem capacity_total_fit (f : Formula) (c : Certificate)
    (h : capacityCheck f c=true) (hl : c.groups.length≤100000) :
    totalCapacity c.groups<cap 18 :=
  Nat.lt_of_le_of_lt
    (Nat.le_trans (total_bound c.groups (capacity_groups f c h))
      (mul_mono (Nat.le_refl 2) hl))
    (by decide : 2*100000<cap 18)

end ProctorIntermediateWidth

#print axioms ProctorIntermediateWidth.lookup_fit
#print axioms ProctorIntermediateWidth.tails_fit
#print axioms ProctorIntermediateWidth.frontier_fit
#print axioms ProctorIntermediateWidth.append_fit
#print axioms ProctorIntermediateWidth.target_fit
#print axioms ProctorIntermediateWidth.demand_fit
#print axioms ProctorIntermediateWidth.false_lits_fit
#print axioms ProctorIntermediateWidth.toggle_fit
#print axioms ProctorIntermediateWidth.combine_fit
#print axioms ProctorIntermediateWidth.sum_support_fit
#print axioms ProctorIntermediateWidth.index_lt
#print axioms ProctorIntermediateWidth.index_fit
#print axioms ProctorIntermediateWidth.group_guard
#print axioms ProctorIntermediateWidth.group_word_bound
#print axioms ProctorIntermediateWidth.total_bound
#print axioms ProctorIntermediateWidth.capacity_groups
#print axioms ProctorIntermediateWidth.capacity_total_fit
