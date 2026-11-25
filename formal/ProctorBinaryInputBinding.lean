/-! F034 candidate: ordered formula equality and identifier range
checking through verified binary circuits, with exact projection on
decoded inputs. The remaining validProof and semantic checker are
unchanged. Selected comparison gate counts only, not machine cost. -/
namespace ProctorBinaryInputBinding
open ProctorHallDeficiency
open ProctorCapacityReplay (test every)
open ProctorUnifiedReplay (Envelope validId validClause validFormula validProof check boundCheck)
open ProctorCheckedBinaryScanner (cap)
open ProctorCheckerBinaryTests (checkedEq checkedId checked_eq_value checked_id_value
  checked_eq_bound checked_id_bound)
open ProctorBinaryReferences (Fits rowMeter row_value row_bound literalBudget)

def FormulaFit (w : Nat) (f : Formula) : Prop := ∀ c ∈ f, Fits w c

def literalCount : Formula → Nat
  | [] => 0
  | c::cs => literalCount cs+c.length

def formulaEq (w : Nat) : Formula → Formula → Bool × Nat
  | [],[] => (true,0)
  | [],_::_ => (false,0)
  | _::_,[] => (false,0)
  | a::as,b::bs =>
    let e := rowMeter w a b
    if e.1 then let r := formulaEq w as bs; (r.1,r.2+e.2)
    else (false,e.2)

theorem formula_eq_value (w : Nat) (a b : Formula)
    (ha : FormulaFit w a) (hb : FormulaFit w b) :
    (formulaEq w a b).1=test (a=b) := by
  induction a generalizing b with
  | nil => cases b <;> rfl
  | cons l ls ih =>
    cases b with
    | nil => rfl
    | cons m ms =>
      change (if (rowMeter w l m).1 then
        ((formulaEq w ls ms).1,(formulaEq w ls ms).2+(rowMeter w l m).2)
        else (false,(rowMeter w l m).2)).1=test (l::ls=m::ms)
      rw [row_value w l m (ha l (List.Mem.head _)) (hb m (List.Mem.head _))]
      unfold test
      by_cases e : l=m
      · rw [if_pos e]
        cases e
        change (formulaEq w ls ms).1=test (l::ls=l::ms)
        rw [ih ms (fun c h => ha c (List.Mem.tail _ h))
          (fun c h => hb c (List.Mem.tail _ h))]
        unfold test
        by_cases t : ls=ms
        · rw [if_pos t,if_pos (congrArg (List.cons l) t)]
        · have ne : l::ls≠l::ms := fun h => t (List.cons.inj h).2
          rw [if_neg t,if_neg ne]
      · rw [if_neg e]
        have ne : l::ls≠m::ms := fun h => e (List.cons.inj h).1
        rw [if_neg ne]
        rfl

private theorem mul_add (k a b : Nat) : k*(a+b)=k*a+k*b := by
  induction b with
  | zero => rfl
  | succ b ih =>
    change k*(a+b)+k=k*a+(k*b+k)
    rw [ih]
    exact Nat.add_assoc _ _ _

theorem formula_eq_bound (w : Nat) (a b : Formula) :
    (formulaEq w a b).2≤literalBudget w*literalCount a := by
  induction a generalizing b with
  | nil => cases b <;> exact Nat.le_refl 0
  | cons l ls ih =>
    cases b with
    | nil => exact Nat.zero_le _
    | cons m ms =>
      change (if (rowMeter w l m).1 then
        ((formulaEq w ls ms).1,(formulaEq w ls ms).2+(rowMeter w l m).2)
        else (false,(rowMeter w l m).2)).2≤
        literalBudget w*(literalCount ls+l.length)
      rw [mul_add]
      cases e : (rowMeter w l m).1 with
      | true => exact Nat.add_le_add (ih ms) (row_bound w l m)
      | false => exact Nat.le_trans (row_bound w l m) (Nat.le_add_left _ _)

def optFalse : Option Bool → Bool
  | none => false
  | some b => b

def idGate (w n v : Nat) : Bool × Nat :=
  let e := checkedId w n v
  (optFalse e.1,e.2)

theorem id_gate_value (w n v : Nat) (hn : n<cap w) (hv : v<cap w) :
    (idGate w n v).1=validId n v := by
  change optFalse (checkedId w n v).1=_
  rw [checked_id_value w n v hn hv]
  rfl

def allGate {α : Type} (p : α → Bool × Nat) : List α → Bool × Nat
  | [] => (true,0)
  | a::as =>
    let e := p a
    if e.1 then let r := allGate p as; (r.1,r.2+e.2)
    else (false,e.2)

def weight {α : Type} (cost : α → Nat) : List α → Nat
  | [] => 0
  | a::as => weight cost as+cost a

theorem all_value {α : Type} (p : α → Bool × Nat) (q : α → Bool)
    (xs : List α) (h : ∀ a ∈ xs, (p a).1=q a) :
    (allGate p xs).1=every q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (if (p a).1 then ((allGate p as).1,(allGate p as).2+(p a).2)
      else (false,(p a).2)).1=(q a && every q as)
    rw [h a (List.Mem.head _)]
    cases e : q a with
    | false => rfl
    | true => exact ih (fun b hb => h b (List.Mem.tail _ hb))

theorem all_bound {α : Type} (p : α → Bool × Nat) (cost : α → Nat)
    (hp : ∀ a, (p a).2≤cost a) (xs : List α) :
    (allGate p xs).2≤weight cost xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change (if (p a).1 then ((allGate p as).1,(allGate p as).2+(p a).2)
      else (false,(p a).2)).2≤weight cost as+cost a
    cases e : (p a).1 with
    | true => exact Nat.add_le_add ih (hp a)
    | false => exact Nat.le_trans (hp a) (Nat.le_add_left _ _)

def clauseRange (w n : Nat) (c : Clause) : Bool × Nat :=
  allGate (fun l : Literal => idGate w n l.1) c

def formulaRange (w n : Nat) (f : Formula) : Bool × Nat :=
  allGate (clauseRange w n) f

def idBudget (w : Nat) : Nat := (5*w+5*w)+2

theorem clause_range_value (w n : Nat) (c : Clause) (hn : n<cap w) (hc : Fits w c) :
    (clauseRange w n c).1=validClause n c :=
  all_value _ _ c (fun l hl => id_gate_value w n l.1 hn (hc l hl))

theorem formula_range_value (w n : Nat) (f : Formula) (hn : n<cap w)
    (hf : FormulaFit w f) : (formulaRange w n f).1=validFormula n f :=
  all_value _ _ f (fun c hc => clause_range_value w n c hn (hf c hc))

private theorem const_weight {α : Type} (k : Nat) (xs : List α) :
    weight (fun _ : α => k) xs=k*xs.length := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change weight (fun _ : α => k) as+k=k*as.length+k
    rw [ih]

theorem clause_range_bound (w n : Nat) (c : Clause) :
    (clauseRange w n c).2≤idBudget w*c.length := by
  rw [← const_weight (idBudget w) c]
  exact all_bound _ _ (fun l : Literal => checked_id_bound w n l.1) c

private theorem formula_weight (k : Nat) (f : Formula) :
    weight (fun c : Clause => k*c.length) f=k*literalCount f := by
  induction f with
  | nil => rfl
  | cons c cs ih =>
    change weight (fun c : Clause => k*c.length) cs+k*c.length=
      k*(literalCount cs+c.length)
    rw [ih,mul_add]

theorem formula_range_bound (w n : Nat) (f : Formula) :
    (formulaRange w n f).2≤idBudget w*literalCount f := by
  rw [← formula_weight (idBudget w) f]
  exact all_bound _ _ (clause_range_bound w n) f

-- Independent conservative comparison-gate reservations; all three
-- selected tests are charged, including when a preceding test fails.
def bindingMeter (w n : Nat) (f : Formula) (e : Envelope) : Bool × Nat :=
  let a := checkedEq w n e.variableBound
  let b := formulaEq w f e.original
  let c := formulaRange w n f
  (optFalse a.1 && (b.1 && c.1),a.2+b.2+c.2)

theorem binding_value (w n : Nat) (f : Formula) (e : Envelope)
    (hn : n<cap w) (hf : FormulaFit w f)
    (he : e.variableBound<cap w) (hg : FormulaFit w e.original) :
    (bindingMeter w n f e).1=
      (test (n=e.variableBound) && (test (f=e.original) && validFormula n f)) := by
  change (optFalse (checkedEq w n e.variableBound).1 &&
    ((formulaEq w f e.original).1 && (formulaRange w n f).1))=_
  rw [checked_eq_value w n e.variableBound hn he,
    formula_eq_value w f e.original hf hg,formula_range_value w n f hn hf]
  rfl

theorem binding_bound (w n : Nat) (f : Formula) (e : Envelope) :
    (bindingMeter w n f e).2≤((5*w+5*w)+3)+
      literalBudget w*literalCount f+idBudget w*literalCount f :=
  Nat.add_le_add (Nat.add_le_add (checked_eq_bound w n e.variableBound)
    (formula_eq_bound w f e.original)) (formula_range_bound w n f)

def binaryCheck (n : Nat) (f : Formula) (e : Envelope) : Bool :=
  (bindingMeter 512 n f e).1 && (validProof n e.proof && check f e.proof)

private theorem bool_assoc (a b c d : Bool) :
    ((a && (b && c)) && d) = (a && (b && (c && d))) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

theorem binary_check_value (n : Nat) (f : Formula) (e : Envelope)
    (hn : n<cap 512) (hf : FormulaFit 512 f)
    (he : e.variableBound<cap 512) (hg : FormulaFit 512 e.original) :
    binaryCheck n f e=boundCheck n f e := by
  unfold binaryCheck boundCheck
  rw [binding_value 512 n f e hn hf he hg]
  exact bool_assoc _ _ _ _

def checkBytes (a b : List Nat) : Bool :=
  match ProctorFuelFreeDecoder.decodeExpected a,ProctorFuelFreeDecoder.decodeEnvelope b with
  | some (n,f),some e => binaryCheck n f e
  | _,_ => false

theorem decoded_check_value (a b : List Nat) :
    checkBytes a b=ProctorDataParser.checkBytes a b := by
  unfold checkBytes ProctorDataParser.checkBytes
  rw [ProctorFuelFreeDecoder.expected_bytes_refines,ProctorFuelFreeDecoder.envelope_bytes_refines]
  cases ha : ProctorDataParser.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases hb : ProctorDataParser.decodeEnvelope b with
      | none => rfl
      | some e =>
        have h1 := ProctorDecodedWidth.decoded_expected a n f ha
        have h2 := ProctorDecodedWidth.decoded_envelope b e hb
        exact binary_check_value n f e h1.left h1.right h2.left h2.right.left

theorem decoded_check_sound (a b : List Nat) (h : checkBytes a b=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [decoded_check_value] at h
  exact ProctorDataParser.accepted_unsat a b h

end ProctorBinaryInputBinding

#print axioms ProctorBinaryInputBinding.formula_eq_value
#print axioms ProctorBinaryInputBinding.formula_eq_bound
#print axioms ProctorBinaryInputBinding.id_gate_value
#print axioms ProctorBinaryInputBinding.all_value
#print axioms ProctorBinaryInputBinding.all_bound
#print axioms ProctorBinaryInputBinding.clause_range_value
#print axioms ProctorBinaryInputBinding.formula_range_value
#print axioms ProctorBinaryInputBinding.clause_range_bound
#print axioms ProctorBinaryInputBinding.formula_range_bound
#print axioms ProctorBinaryInputBinding.binding_value
#print axioms ProctorBinaryInputBinding.binding_bound
#print axioms ProctorBinaryInputBinding.binary_check_value
#print axioms ProctorBinaryInputBinding.decoded_check_value
#print axioms ProctorBinaryInputBinding.decoded_check_sound
