/-! F035: preflight the full materialized CNF size and stop with
UNKNOWN before exceeding the declared budget. Soundness is unconditional
for returned decisions; completeness is conditional on a bounded
elimination schedule. No universal polynomial schedule is assumed. -/
namespace ProctorBoundedElimination
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (update)
open ProctorGeneralBranching (reduceRow row_remaining leaf Answer Satisfiable leaf_total)
open ProctorSemanticProjection (rowProduct orProduct product_origin)
open ProctorAdaptiveElimination (split eliminate eliminate_exists estimate estimate_exact)
open ProctorPathResourceBounds (occurrences)
open ProctorTotalTwoCNF (supported supported_iff WidthTwo)
open ProctorUnifiedReplay (validFormula validId)
open ProctorEnvelopeCompleteness (FormulaOK RowOK formula_ok every_complete)

private theorem len_append {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++ys).length+1=xs.length+1+ys.length
    rw [ih,Nat.add_assoc xs.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

private theorem mul_add' (a b c : Nat) : a*(b+c)=a*b+a*c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change a*(b+c+1)=a*b+a*(c+1)
    rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]

private theorem add_mul' (a b c : Nat) : (a+b)*c=a*c+b*c := by
  rw [Nat.mul_comm (a+b) c,mul_add',Nat.mul_comm c a,Nat.mul_comm c b]

private theorem middle (a b c d : Nat) : (a+b)+(c+d)=(a+c)+(b+d) := by
  rw [Nat.add_assoc a b (c+d),← Nat.add_assoc b c d,Nat.add_comm b c,Nat.add_assoc c b d,← Nat.add_assoc a c]

theorem occurrences_append (f g : Formula) :
    occurrences (f++g)=occurrences f+occurrences g := by
  induction f with
  | nil => exact (Nat.zero_add _).symm
  | cons c cs ih =>
    change c.length+occurrences (cs++g)=(c.length+occurrences cs)+occurrences g
    rw [ih,Nat.add_assoc]

theorem row_product_occurrences (c : Clause) (g : Formula) :
    occurrences (rowProduct c g)=g.length*c.length+occurrences g := by
  induction g with
  | nil => rw [Nat.zero_mul]; rfl
  | cons d ds ih =>
    change (c++d).length+occurrences (rowProduct c ds)=
      (ds.length+1)*c.length+(d.length+occurrences ds)
    rw [len_append,ih,add_mul',Nat.one_mul,Nat.add_comm (ds.length*c.length) c.length,middle]

theorem product_occurrences (f g : Formula) :
    occurrences (orProduct f g)=g.length*occurrences f+f.length*occurrences g := by
  induction f with
  | nil =>
    change 0=g.length*0+0*occurrences g
    rw [Nat.mul_zero,Nat.zero_mul]
  | cons c cs ih =>
    change occurrences (rowProduct c g++orProduct cs g)=
      g.length*(c.length+occurrences cs)+(cs.length+1)*occurrences g
    rw [occurrences_append,row_product_occurrences,ih,middle,mul_add',add_mul',Nat.one_mul,
      Nat.add_comm (occurrences g) (cs.length*occurrences g)]

def weight (f : Formula) : Nat := f.length+occurrences f

def predicted (v : Nat) (f : Formula) : Nat :=
  let t := split v f
  estimate v f+occurrences t.common+
    t.right.length*occurrences t.left+t.left.length*occurrences t.right

theorem predicted_exact (v : Nat) (f : Formula) :
    weight (eliminate v f)=predicted v f := by
  unfold weight
  rw [estimate_exact]
  unfold eliminate predicted
  dsimp only
  rw [occurrences_append,product_occurrences]
  rw [← Nat.add_assoc,← Nat.add_assoc]

private theorem append_cases {α : Type} (xs ys : List α) (a : α)
    (h : a∈xs++ys) : a∈xs ∨ a∈ys := by
  induction xs with
  | nil => exact Or.inr h
  | cons x xs ih =>
    cases h with
    | head => exact Or.inl (List.Mem.head _)
    | tail _ hm =>
      cases ih hm with
      | inl e => exact Or.inl (List.Mem.tail _ e)
      | inr e => exact Or.inr e

private theorem cons_ok (n : Nat) (r : Clause) (f : Formula)
    (hr : RowOK n r) (hf : FormulaOK n f) : FormulaOK n (r::f) := by
  intro c hc
  cases hc with
  | head => exact hr
  | tail _ hm => exact hf c hm

theorem split_valid (n v : Nat) (f : Formula) (h : FormulaOK n f) :
    FormulaOK n (split v f).common ∧ FormulaOK n (split v f).left ∧
      FormulaOK n (split v f).right := by
  induction f with
  | nil =>
    have he : FormulaOK n [] := by intro c hc; cases hc
    exact ⟨he,he,he⟩
  | cons c cs ih =>
    have ht := ih (fun d hd => h d (List.Mem.tail _ hd))
    have hr : ∀ b r, reduceRow v b c=some r → RowOK n r := by
      intro b r he l hl
      exact h c (List.Mem.head _) l (row_remaining v b c r he l hl).1
    unfold split
    dsimp only
    cases h0 : reduceRow v false c with
    | none =>
      cases h1 : reduceRow v true c with
      | none => exact ht
      | some b => exact ⟨ht.1,ht.2.1,cons_ok n b _ (hr true b h1) ht.2.2⟩
    | some a =>
      cases h1 : reduceRow v true c with
      | none => exact ⟨ht.1,cons_ok n a _ (hr false a h0) ht.2.1,ht.2.2⟩
      | some b => exact ⟨cons_ok n a _ (hr false a h0) ht.1,ht.2.1,ht.2.2⟩

theorem eliminate_valid (n v : Nat) (f : Formula) (h : validFormula n f=true) :
    validFormula n (eliminate v f)=true := by
  have ht := split_valid n v f (formula_ok n f h)
  let t := split v f
  apply every_complete
  intro r hr
  apply every_complete
  intro l hl
  change r∈t.common++orProduct t.left t.right at hr
  cases append_cases _ _ r hr with
  | inl e => exact ht.1 r e l hl
  | inr e =>
    obtain ⟨a,ha,b,hb,he⟩ := product_origin t.left t.right r e
    rw [he] at hl
    cases append_cases a b l hl with
    | inl e => exact ht.2.1 a ha l e
    | inr e => exact ht.2.2 b hb l e

theorem eliminate_sat (v : Nat) (f : Formula) :
    Satisfiable (eliminate v f) ↔ Satisfiable f := by
  constructor
  · intro h
    obtain ⟨x,hx⟩ := h
    obtain ⟨b,hb⟩ := (eliminate_exists v f x).1 hx
    exact ⟨update x v b,hb⟩
  · intro h
    cases (ProctorGeneralBranching.shannon v f).1 h with
    | inl e =>
      obtain ⟨x,hx⟩ := e
      exact ⟨x,(eliminate_exists v f x).2
        ⟨false,(ProctorGeneralBranching.restriction_correct v false f x).1 hx⟩⟩
    | inr e =>
      obtain ⟨x,hx⟩ := e
      exact ⟨x,(eliminate_exists v f x).2
        ⟨true,(ProctorGeneralBranching.restriction_correct v true f x).1 hx⟩⟩

theorem answer_transfer (v : Nat) (f : Formula) (b : Bool)
    (h : Answer (eliminate v f) b) : Answer f b := by
  cases b with
  | false => exact fun hs => h ((eliminate_sat v f).2 hs)
  | true => exact (eliminate_sat v f).1 h

def run (n cap : Nat) : List Nat → Formula → Option Bool
  | [],f => if weight f≤cap then leaf n f else none
  | v::vs,f =>
    if weight f≤cap then
      if supported f then leaf n f
      else if predicted v f≤cap then run n cap vs (eliminate v f) else none
    else none

-- A schedule supplies actual IDs. The bound is checked before
-- constructing each elimination output, not after allocating it.
def ScheduleOK (cap : Nat) : List Nat → Formula → Prop
  | [],f => weight f≤cap ∧ WidthTwo f
  | v::vs,f => weight f≤cap ∧
      (WidthTwo f ∨ (predicted v f≤cap ∧ ScheduleOK cap vs (eliminate v f)))

theorem leaf_sound (n : Nat) (f : Formula) (b : Bool) (h : leaf n f=some b) :
    Answer f b := by
  unfold leaf at h
  cases he : ProctorTotalTwoCNF.solve n f with
  | invalid => rw [he] at h; cases h
  | unsupported => rw [he] at h; cases h
  | internalError => rw [he] at h; cases h
  | sat x =>
    rw [he] at h
    cases h
    exact ⟨x,ProctorTotalTwoCNF.solve_sat_sound n f x he⟩
  | unsat p =>
    rw [he] at h
    cases h
    exact ProctorTotalTwoCNF.solve_unsat_sound n f p he

theorem run_sound (n cap : Nat) (vs : List Nat) (f : Formula) (b : Bool)
    (h : run n cap vs f=some b) : Answer f b := by
  induction vs generalizing f with
  | nil =>
    change (if weight f≤cap then leaf n f else none)=some b at h
    by_cases hw : weight f≤cap
    · rw [if_pos hw] at h
      exact leaf_sound n f b h
    · rw [if_neg hw] at h
      cases h
  | cons v vs ih =>
    change (if weight f≤cap then if supported f then leaf n f
      else if predicted v f≤cap then run n cap vs (eliminate v f) else none else none)=some b at h
    by_cases hw : weight f≤cap
    · rw [if_pos hw] at h
      cases he : supported f with
      | true =>
        rw [he] at h
        exact leaf_sound n f b h
      | false =>
        rw [he] at h
        change (if predicted v f≤cap then run n cap vs (eliminate v f) else none)=some b at h
        by_cases hp : predicted v f≤cap
        · rw [if_pos hp] at h
          exact answer_transfer v f b (ih _ h)
        · rw [if_neg hp] at h
          cases h
    · rw [if_neg hw] at h
      cases h

theorem run_total (n cap : Nat) (vs : List Nat) (f : Formula)
    (hv : validFormula n f=true) (hs : ScheduleOK cap vs f) :
    ∃ b, run n cap vs f=some b ∧ Answer f b := by
  induction vs generalizing f with
  | nil =>
    change weight f≤cap ∧ WidthTwo f at hs
    change ∃ b, (if weight f≤cap then leaf n f else none)=some b ∧ Answer f b
    rw [if_pos hs.1]
    exact leaf_total n f hv hs.2
  | cons v vs ih =>
    change weight f≤cap ∧
      (WidthTwo f ∨ (predicted v f≤cap ∧ ScheduleOK cap vs (eliminate v f))) at hs
    change ∃ b, (if weight f≤cap then if supported f then leaf n f
      else if predicted v f≤cap then run n cap vs (eliminate v f) else none else none)=some b ∧ Answer f b
    rw [if_pos hs.1]
    cases he : supported f with
    | true => exact leaf_total n f hv ((supported_iff f).1 he)
    | false =>
      cases hs.2 with
      | inl e =>
        have hh := (supported_iff f).2 e
        rw [he] at hh
        cases hh
      | inr e =>
        change ∃ b, (if predicted v f≤cap then run n cap vs (eliminate v f) else none)=some b ∧ Answer f b
        rw [if_pos e.1]
        obtain ⟨b,hb,ht⟩ := ih _ (eliminate_valid n v f hv) e.2
        exact ⟨b,hb,answer_transfer v f b ht⟩

theorem preflight_safe (cap v : Nat) (f : Formula) (h : predicted v f≤cap) :
    weight (eliminate v f)≤cap := by
  rw [predicted_exact]
  exact h

end ProctorBoundedElimination

#print axioms ProctorBoundedElimination.occurrences_append
#print axioms ProctorBoundedElimination.row_product_occurrences
#print axioms ProctorBoundedElimination.product_occurrences
#print axioms ProctorBoundedElimination.predicted_exact
#print axioms ProctorBoundedElimination.split_valid
#print axioms ProctorBoundedElimination.eliminate_valid
#print axioms ProctorBoundedElimination.eliminate_sat
#print axioms ProctorBoundedElimination.answer_transfer
#print axioms ProctorBoundedElimination.leaf_sound
#print axioms ProctorBoundedElimination.run_sound
#print axioms ProctorBoundedElimination.run_total
#print axioms ProctorBoundedElimination.preflight_safe
