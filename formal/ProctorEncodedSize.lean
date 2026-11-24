/-! F034: structural-to-token-size bridge and unified selected-charge
polynomial. Canonical typed encodings, not arbitrary accepted bytes. -/
namespace ProctorEncodedSize
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch tails frontier)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorXorReplay (Block)
open ProctorUnifiedReplay (Proof Envelope Terminal target)
open ProctorWireRoundtrip (encNat encBool encLiteral encClause encFormula encItems encList encExpected)
open ProctorEnvelopeRoundtrip (encRef encGroup encCapacity encBlock encStep encBatch encTerminal encProof encEnvelope)
open ProctorPolynomialMeter (formulaMass chainMass chainSteps chain_steps_mass chain_uniform stepUnit supportMass)
open ProctorTerminalPolynomial (mass rowWeight groupWeight blockWeight mul_mono weighted_visits capacityUnit xorUnit capacity_poly xor_poly)
open ProctorCapacityMeter (visitsBudget)
open ProctorUnifiedMeter (formulaBudget clauseBudget formulaRangeBudget refsRangeBudget terminalRangeBudget proofRangeBudget terminalBudget boundBudget boundMeter bound_cost)

private theorem len_append {α : Type} (a b : List α) :
    (a++b).length=a.length+b.length := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++b).length+1=(xs.length+1)+b.length
    rw [ih]
    calc
      (xs.length+b.length)+1 = xs.length+(b.length+1) := Nat.add_assoc _ _ _
      _ = xs.length+(1+b.length) := congrArg (fun z => xs.length+z) (Nat.add_comm _ _)
      _ = (xs.length+1)+b.length := (Nat.add_assoc _ _ _).symm

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

private theorem items_len {α : Type} (enc : α → List Nat) (xs : List α) :
    (encItems enc xs).length=mass (fun a => (enc a).length) xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (enc a++encItems enc as).length=(enc a).length+mass (fun a => (enc a).length) as
    rw [len_append,ih]

private theorem mass_le_items {α : Type} (w : α → Nat) (enc : α → List Nat)
    (xs : List α) (h : ∀ a, w a≤(enc a).length) :
    mass w xs≤(encItems enc xs).length := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change w a+mass w as≤(enc a++encItems enc as).length
    rw [len_append]
    exact Nat.add_le_add (h a) ih

private theorem mass_le_list {α : Type} (w : α → Nat) (enc : α → List Nat)
    (xs : List α) (h : ∀ a, w a≤(enc a).length) :
    mass w xs≤(encList enc xs).length :=
  Nat.le_trans (mass_le_items w enc xs h) (Nat.le_succ _)

private theorem clause_items (c : Clause) : c.length≤(encItems encLiteral c).length := by
  induction c with
  | nil => exact Nat.le_refl 0
  | cons l ls ih =>
    change ls.length+1≤(encLiteral l++encItems encLiteral ls).length
    rw [len_append]
    change ls.length+1≤2+(encItems encLiteral ls).length
    rw [Nat.add_comm 2 _]
    exact Nat.add_le_add ih (by decide : 1≤2)

theorem clause_size (c : Clause) : c.length+1≤(encClause c).length :=
  Nat.succ_le_succ (clause_items c)

private theorem formula_items (f : Formula) : formulaMass f≤(encItems encClause f).length := by
  induction f with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    change (c.length+1)+formulaMass cs≤(encClause c++encItems encClause cs).length
    rw [len_append]
    exact Nat.add_le_add (clause_size c) ih

theorem formula_size (f : Formula) : formulaMass f≤(encFormula f).length :=
  Nat.le_trans (formula_items f) (Nat.le_succ _)

theorem ref_size (r : RefRow) : rowWeight r≤(encRef r).length := by
  unfold rowWeight encRef
  rw [len_append]
  exact Nat.le_trans (clause_size r.row) (Nat.le_add_left _ _)

theorem group_size (g : Group) : groupWeight g≤(encGroup g).length := by
  unfold groupWeight encGroup
  rw [len_append]
  exact Nat.le_trans (clause_size g.literals) (Nat.le_add_right _ _)

private theorem nat_items_len (vs : List Nat) :
    (encItems encNat vs).length=vs.length := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change ((encItems encNat vs).length+1)=vs.length+1
    exact congrArg Nat.succ ih

private theorem nat_list_len (vs : List Nat) :
    (encList encNat vs).length=vs.length+1 :=
  congrArg Nat.succ (nat_items_len vs)

theorem block_size (b : Block) : blockWeight b≤(encBlock b).length := by
  unfold blockWeight encBlock
  rw [len_append,len_append,nat_list_len]
  change 1+b.support.length+mass rowWeight b.refs≤
    (b.support.length+1)+(1+(encList encRef b.refs).length)
  rw [Nat.add_comm 1 b.support.length]
  exact Nat.add_le_add (Nat.le_refl _)
    (Nat.le_trans (mass_le_list rowWeight encRef b.refs ref_size) (Nat.le_add_left _ _))

theorem support_size (bs : List Block) :
    supportMass bs≤mass blockWeight bs := by
  induction bs with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    exact Nat.add_le_add
      (Nat.le_trans (Nat.le_add_left _ _) (Nat.le_add_right _ _)) ih

private theorem step_size (s : Step) : s.tail.length+1≤(encStep s).length :=
  Nat.le_trans (clause_size s.tail) (Nat.le_trans (Nat.le_succ _) (Nat.le_trans (Nat.le_succ _) (Nat.le_succ _)))

theorem batch_size (ss : Batch) : formulaMass (tails ss)≤(encBatch ss).length := by
  have h : formulaMass (tails ss)≤(encItems encStep ss).length := by
    induction ss with
    | nil => exact Nat.le_refl 0
    | cons s ss ih =>
      change (s.tail.length+1)+formulaMass (tails ss)≤(encStep s++encItems encStep ss).length
      rw [len_append]
      exact Nat.add_le_add (step_size s) ih
  exact Nat.le_trans h (Nat.le_succ _)

private theorem chain_items (f : Formula) (bs : List Batch) :
    chainMass f bs≤formulaMass f+(encItems encBatch bs).length := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl _
  | cons ss rest ih =>
    change formulaMass f+chainMass (tails ss) rest≤
      formulaMass f+(encBatch ss++encItems encBatch rest).length
    rw [len_append]
    exact Nat.add_le_add (Nat.le_refl _) (Nat.le_trans (ih (tails ss))
      (Nat.add_le_add (batch_size ss) (Nat.le_refl _)))

def size (n : Nat) (f : Formula) (e : Envelope) : Nat :=
  (encExpected n f).length+(encEnvelope e).length

private theorem expected_mass (n : Nat) (f : Formula) :
    formulaMass f≤(encExpected n f).length :=
  Nat.le_trans (formula_size f) (Nat.le_trans (Nat.le_succ _) (Nat.le_succ _))

private theorem proof_size (e : Envelope) : (encProof e.proof).length≤(encEnvelope e).length := by
  unfold encEnvelope
  change (encProof e.proof).length≤(encFormula e.original++encProof e.proof).length+1+1
  rw [len_append]
  exact Nat.le_trans (Nat.le_add_left _ _) (Nat.le_trans (Nat.le_succ _) (Nat.le_succ _))

private theorem batches_size (p : Proof) :
    (encList encBatch p.batches).length≤(encProof p).length := by
  unfold encProof
  rw [len_append]
  exact Nat.le_add_right _ _

private theorem terminal_size (p : Proof) : (encTerminal p.terminal).length≤(encProof p).length := by
  unfold encProof
  rw [len_append,len_append]
  exact Nat.le_trans (Nat.le_add_left _ _) (Nat.le_add_left _ _)

theorem chain_size (n : Nat) (f : Formula) (e : Envelope) :
    chainMass f e.proof.batches≤size n f e :=
  Nat.le_trans (chain_items f e.proof.batches)
    (Nat.add_le_add (expected_mass n f) (Nat.le_trans (Nat.le_succ _)
      (Nat.le_trans (batches_size e.proof) (proof_size e))))

private theorem frontier_mass (f : Formula) (bs : List Batch) :
    formulaMass (frontier f bs)≤chainMass f bs := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl _
  | cons ss rest ih =>
    exact Nat.le_trans (ih (tails ss)) (Nat.le_add_left _ _)

private theorem formula_append (a b : Formula) :
    formulaMass (a++b)=formulaMass a+formulaMass b := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons c cs ih =>
    change (c.length+1)+formulaMass (cs++b)=(c.length+1+formulaMass cs)+formulaMass b
    rw [ih]
    exact (Nat.add_assoc (c.length+1) (formulaMass cs) (formulaMass b)).symm

def cap (n : Nat) (f : Formula) (e : Envelope) : Nat :=
  size n f e+size n f e+1

theorem target_mass (n : Nat) (f : Formula) (e : Envelope) :
    formulaMass (target f e.proof)≤cap n f e := by
  have hc := chain_size n f e
  have hf : formulaMass f≤size n f e :=
    Nat.le_trans (expected_mass n f) (Nat.le_add_right _ _)
  have ht := Nat.le_trans (frontier_mass f e.proof.batches) hc
  unfold target cap
  cases e.proof.augmented with
  | false =>
    exact Nat.le_trans ht (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _))
  | true =>
    change formulaMass (f++frontier f e.proof.batches)≤_
    rw [formula_append]
    exact Nat.le_trans (Nat.add_le_add hf ht) (Nat.le_succ _)

def terminalMassOK (t : Terminal) (B : Nat) : Prop :=
  match t with
  | .empty => True
  | .capacity c => mass rowWeight c.demands≤B ∧
      mass rowWeight c.conflicts≤B ∧ mass groupWeight c.groups≤B
  | .xor bs => mass blockWeight bs≤B ∧ supportMass bs≤B

theorem terminal_sizes (t : Terminal) :
    terminalMassOK t (encTerminal t).length := by
  cases t with
  | empty => exact True.intro
  | capacity c =>
    change mass rowWeight c.demands≤(encCapacity c).length+1 ∧
      mass rowWeight c.conflicts≤(encCapacity c).length+1 ∧
      mass groupWeight c.groups≤(encCapacity c).length+1
    unfold encCapacity
    rw [len_append,len_append]
    exact ⟨Nat.le_trans (mass_le_list rowWeight encRef c.demands ref_size)
      (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _)),
      Nat.le_trans (mass_le_list rowWeight encRef c.conflicts ref_size)
        (Nat.le_trans (Nat.le_add_left _ _) (Nat.le_trans (Nat.le_add_left _ _) (Nat.le_succ _))),
      Nat.le_trans (mass_le_list groupWeight encGroup c.groups group_size)
        (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_trans (Nat.le_add_left _ _) (Nat.le_succ _)))⟩
  | xor bs =>
    have h := Nat.le_trans (mass_le_list blockWeight encBlock bs block_size) (Nat.le_succ _)
    exact ⟨h,Nat.le_trans (support_size bs) h⟩

private theorem terminal_mono (t : Terminal) (a b : Nat) (h : a≤b)
    (ha : terminalMassOK t a) : terminalMassOK t b := by
  cases t with
  | empty => exact True.intro
  | capacity _ =>
    exact ⟨Nat.le_trans ha.left h,Nat.le_trans ha.right.left h,Nat.le_trans ha.right.right h⟩
  | xor _ => exact ⟨Nat.le_trans ha.left h,Nat.le_trans ha.right h⟩

-- Binding/range budgets. Use a deliberately loose four charges
-- per canonical natural token. The extra count prefix pays for
-- the outer list visit when nested.
private theorem list_charge {α : Type} (q : α → Nat) (enc : α → List Nat)
    (xs : List α) (h : ∀ a, q a+1≤(enc a).length*4) :
    visitsBudget q xs+1≤(encList enc xs).length*4 := by
  have hc := weighted_visits q (fun a => (enc a).length) xs 4 (fun a _ => h a)
  rw [← items_len enc xs] at hc
  change visitsBudget q xs+1≤((encItems enc xs).length+1)*4
  rw [add_mul_local]
  exact Nat.add_le_add hc (by decide : 1≤1*4)

private theorem charge_append (a b : List Nat) (x y : Nat)
    (hx : x≤a.length*4) (hy : y≤b.length*4) :
    x+y≤(a++b).length*4 := by
  rw [len_append,add_mul_local]
  exact Nat.add_le_add hx hy

private theorem charge_prepend (a : List Nat) (v : Nat) (x : Nat)
    (hx : x≤a.length*4) : x≤(v::a).length*4 :=
  Nat.le_trans hx (mul_mono (Nat.le_succ _) (Nat.le_refl _))

theorem formula_binding_size (f : Formula) :
    formulaBudget f≤(encFormula f).length*4 := by
  have h : formulaBudget f≤(encItems encClause f).length*4+1 := by
    induction f with
    | nil => exact Nat.le_refl 1
    | cons c cs ih =>
      change (c.length+1)+formulaBudget cs+1≤
        (encClause c++encItems encClause cs).length*4+1
      rw [len_append,add_mul_local]
      have hc : c.length+1+1≤(encClause c).length*4 := by
        have hm := mul_mono (clause_size c) (by decide : 2≤4)
        have hp : c.length+1+1≤(c.length+1)*2 := by
          change c.length+1+1≤(0+(c.length+1))+(c.length+1)
          rw [Nat.zero_add]
          exact Nat.add_le_add (Nat.le_refl _) (Nat.succ_le_succ (Nat.zero_le _))
        exact Nat.le_trans hp hm
      calc
        (c.length+1)+formulaBudget cs+1 = (c.length+1+1)+formulaBudget cs := by
          rw [Nat.add_assoc,Nat.add_comm (formulaBudget cs) 1,← Nat.add_assoc]
        _ ≤ (encClause c).length*4+((encItems encClause cs).length*4+1) := Nat.add_le_add hc ih
        _ = (encClause c).length*4+(encItems encClause cs).length*4+1 := (Nat.add_assoc _ _ _).symm
  change formulaBudget f≤((encItems encClause f).length+1)*4
  rw [add_mul_local]
  exact Nat.le_trans h (Nat.add_le_add (Nat.le_refl _) (by decide : 1≤1*4))

theorem clause_range_size (c : Clause) :
    clauseBudget c+1≤(encClause c).length*4 :=
  list_charge (fun _ : Literal => 2) encLiteral c (fun l => by
    change 3 ≤ 8
    decide)

theorem formula_range_size (f : Formula) :
    formulaRangeBudget f+1≤(encFormula f).length*4 :=
  list_charge clauseBudget encClause f clause_range_size

private theorem ref_range (r : RefRow) :
    clauseBudget r.row+1≤(encRef r).length*4 := by
  unfold encRef
  exact charge_prepend _ r.index _ (clause_range_size r.row)

theorem refs_range_size (rs : List RefRow) :
    refsRangeBudget rs+1≤(encList encRef rs).length*4 :=
  list_charge (fun r : RefRow => clauseBudget r.row) encRef rs ref_range

private theorem group_range (g : Group) :
    clauseBudget g.literals+1≤(encGroup g).length*4 := by
  unfold encGroup
  rw [len_append]
  exact Nat.le_trans (clause_range_size g.literals)
    (mul_mono (Nat.le_add_right _ _) (Nat.le_refl _))

private theorem support_range (vs : List Nat) :
    visitsBudget (fun _ : Nat => 2) vs+1≤(encList encNat vs).length*4 :=
  list_charge (fun _ : Nat => 2) encNat vs (fun v => by
    change 3 ≤ 4
    decide)

private theorem block_range (b : Block) :
    visitsBudget (fun _ : Nat => 2) b.support+refsRangeBudget b.refs+1≤(encBlock b).length*4 := by
  unfold encBlock
  rw [Nat.add_assoc]
  exact charge_append _ _ _ _
    (Nat.le_trans (Nat.le_succ _) (support_range b.support))
    (charge_prepend _ _ _ (refs_range_size b.refs))

theorem terminal_range_size (t : Terminal) :
    terminalRangeBudget t≤(encTerminal t).length*4 := by
  cases t with
  | empty => exact Nat.zero_le _
  | capacity c =>
    change refsRangeBudget c.demands+(refsRangeBudget c.conflicts+
      visitsBudget (fun g => clauseBudget g.literals) c.groups)≤(1::encCapacity c).length*4
    apply charge_prepend
    unfold encCapacity
    rw [Nat.add_comm (refsRangeBudget c.conflicts) (visitsBudget (fun g => clauseBudget g.literals) c.groups)]
    exact charge_append _ _ _ _
      (Nat.le_trans (Nat.le_succ _) (refs_range_size c.demands))
      (charge_append _ _ _ _
        (Nat.le_trans (Nat.le_succ _) (list_charge (fun g => clauseBudget g.literals) encGroup c.groups group_range))
        (Nat.le_trans (Nat.le_succ _) (refs_range_size c.conflicts)))
  | xor bs =>
    change visitsBudget (fun b => visitsBudget (fun _ => 2) b.support+refsRangeBudget b.refs) bs≤
      (2::encList encBlock bs).length*4
    exact charge_prepend _ _ _ (Nat.le_trans (Nat.le_succ _)
      (list_charge _ encBlock bs block_range))

private theorem step_range (s : Step) :
    2+clauseBudget s.tail+1≤(encStep s).length*4 := by
  unfold encStep
  change 2+clauseBudget s.tail+1≤((encClause s.tail).length+1+1+1)*4
  rw [Nat.add_assoc]
  have h := Nat.add_le_add (by decide : 2≤1*4) (clause_range_size s.tail)
  rw [add_mul_local,add_mul_local,add_mul_local]
  exact Nat.le_trans h (by
    rw [Nat.add_comm (1*4) ((encClause s.tail).length*4)]
    exact Nat.le_trans (Nat.le_add_right _ _) (Nat.le_add_right _ _))

private theorem batch_range (ss : Batch) :
    visitsBudget (fun s : Step => 2+clauseBudget s.tail) ss+1≤(encBatch ss).length*4 :=
  list_charge _ encStep ss step_range

theorem proof_range_size (p : Proof) :
    proofRangeBudget p≤(encProof p).length*4 := by
  unfold proofRangeBudget encProof
  exact charge_append _ _ _ _
    (Nat.le_trans (Nat.le_succ _) (list_charge _ encBatch p.batches batch_range))
    (charge_prepend _ _ _ (terminal_range_size p.terminal))

def terminalUnit (B : Nat) : Nat := B+capacityUnit B+xorUnit B

theorem terminal_poly (f : Formula) (t : Terminal) (B : Nat)
    (hb : 1≤B) (hf : formulaMass f≤B) (ht : terminalMassOK t B) :
    terminalBudget f t≤terminalUnit B := by
  unfold terminalUnit
  cases t with
  | empty =>
    exact Nat.le_trans (Nat.le_trans (ProctorPolynomialMeter.mass_rows f) hf)
      (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_add_right _ _))
  | capacity c =>
    exact Nat.le_trans (capacity_poly f c B hb hf ht.left ht.right.left ht.right.right)
      (Nat.le_trans (Nat.le_add_left _ _) (Nat.le_add_right _ _))
  | xor bs =>
    exact Nat.le_trans (xor_poly f bs B hf ht.left ht.right) (Nat.le_add_left _ _)

def globalUnit (B : Nat) : Nat :=
  1+(B*4+(B*4+(B*4+(B*stepUnit B+terminalUnit B))))

theorem global_budget (n : Nat) (f : Formula) (e : Envelope) :
    boundBudget f e≤globalUnit (cap n f e) := by
  let B := cap n f e
  have hs : size n f e≤B := Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _)
  have hb : 1≤B := Nat.le_add_left _ _
  have he : (encExpected n f).length≤B :=
    Nat.le_trans (Nat.le_add_right _ _) hs
  have hp : (encProof e.proof).length≤B :=
    Nat.le_trans (proof_size e) (Nat.le_trans (Nat.le_add_left _ _) hs)
  have hf : (encFormula f).length≤B :=
    Nat.le_trans (Nat.le_trans (Nat.le_succ _) (Nat.le_succ _)) he
  have hc : chainMass f e.proof.batches≤B := Nat.le_trans (chain_size n f e) hs
  have ht : terminalMassOK e.proof.terminal B :=
    terminal_mono _ _ _ (Nat.le_trans (terminal_size e.proof) hp) (terminal_sizes _)
  unfold boundBudget ProctorUnifiedMeter.checkBudget globalUnit
  exact Nat.add_le_add (Nat.le_refl 1)
    (Nat.add_le_add (Nat.le_trans (formula_binding_size f) (mul_mono hf (Nat.le_refl _)))
      (Nat.add_le_add (Nat.le_trans (Nat.le_trans (Nat.le_succ _) (formula_range_size f))
        (mul_mono hf (Nat.le_refl _)))
        (Nat.add_le_add (Nat.le_trans (proof_range_size e.proof) (mul_mono hp (Nat.le_refl _)))
          (Nat.add_le_add (Nat.le_trans (chain_uniform f e.proof.batches B hc)
            (mul_mono (Nat.le_trans (chain_steps_mass f e.proof.batches) hc) (Nat.le_refl _)))
            (terminal_poly _ _ B hb (target_mass n f e) ht)))))

theorem global_meter (n : Nat) (f : Formula) (e : Envelope) :
    (boundMeter n f e).2≤globalUnit (cap n f e) :=
  Nat.le_trans (bound_cost n f e) (global_budget n f e)

theorem global_sound (n : Nat) (f : Formula) (e : Envelope)
    (h : (boundMeter n f e).1=true) :
    (¬ ∃ x : Assignment, FormulaSat f x) ∧
      (boundMeter n f e).2≤globalUnit (cap n f e) :=
  ⟨ProctorUnifiedMeter.bound_sound n f e h,global_meter n f e⟩

end ProctorEncodedSize

#print axioms ProctorEncodedSize.clause_size
#print axioms ProctorEncodedSize.formula_size
#print axioms ProctorEncodedSize.ref_size
#print axioms ProctorEncodedSize.group_size
#print axioms ProctorEncodedSize.block_size
#print axioms ProctorEncodedSize.support_size
#print axioms ProctorEncodedSize.batch_size
#print axioms ProctorEncodedSize.chain_size
#print axioms ProctorEncodedSize.target_mass
#print axioms ProctorEncodedSize.terminal_sizes
#print axioms ProctorEncodedSize.formula_binding_size
#print axioms ProctorEncodedSize.clause_range_size
#print axioms ProctorEncodedSize.formula_range_size
#print axioms ProctorEncodedSize.refs_range_size
#print axioms ProctorEncodedSize.terminal_range_size
#print axioms ProctorEncodedSize.proof_range_size
#print axioms ProctorEncodedSize.terminal_poly
#print axioms ProctorEncodedSize.global_budget
#print axioms ProctorEncodedSize.global_meter
#print axioms ProctorEncodedSize.global_sound
