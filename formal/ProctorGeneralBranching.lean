/-! A general CNF decision route via Shannon restriction and the verified
width-two solver. Correctness for all finite valid CNFs is the target;
the branching schedule is exponential in the supplied variable list.
This is not a candidate polynomial SAT algorithm. -/
namespace ProctorGeneralBranching
open ProctorHallDeficiency
open ProctorOrdinaryCompleteness (update variables variable_mem)
open ProctorUnifiedReplay (validFormula validClause)
open ProctorEnvelopeCompleteness (formula_ok every_complete)
open ProctorTotalTwoCNF (solve supported WidthTwo supported_iff)
open ProctorResolutionBridge (Unsat)

def reduceRow (v : Nat) (b : Bool) : Clause → Option Clause
  | [] => some []
  | l::ls =>
    if l.1=v then
      if l.2=b then none else reduceRow v b ls
    else (reduceRow v b ls).map (fun r => l::r)

def restrict (v : Nat) (b : Bool) : Formula → Formula
  | [] => []
  | c::cs =>
    match reduceRow v b c with
    | none => restrict v b cs
    | some r => r::restrict v b cs

def RowMeaning (x : Assignment) : Option Clause → Prop
  | none => True
  | some c => ClauseSat c x

theorem cons_sat (x : Assignment) (l : Literal) (ls : Clause) :
    ClauseSat (l::ls) x ↔ x l.1=l.2 ∨ ClauseSat ls x := by
  constructor
  · intro h
    obtain ⟨a,ha,ht⟩ := h
    cases ha with
    | head => exact Or.inl ht
    | tail _ hm => exact Or.inr ⟨a,hm,ht⟩
  · intro h
    cases h with
    | inl e => exact ⟨l,List.Mem.head _,e⟩
    | inr e =>
      obtain ⟨a,ha,ht⟩ := e
      exact ⟨a,List.Mem.tail _ ha,ht⟩

theorem formula_cons (x : Assignment) (c : Clause) (cs : Formula) :
    FormulaSat (c::cs) x ↔ ClauseSat c x ∧ FormulaSat cs x := by
  constructor
  · intro h
    exact ⟨h c (List.Mem.head _),fun d hd => h d (List.Mem.tail _ hd)⟩
  · intro h d hd
    cases hd with
    | head => exact h.left
    | tail _ hm => exact h.right d hm

theorem row_correct (v : Nat) (b : Bool) (c : Clause) (x : Assignment) :
    RowMeaning x (reduceRow v b c) ↔ ClauseSat c (update x v b) := by
  induction c with
  | nil =>
    constructor
    · intro h
      obtain ⟨l,hl,_⟩ := h
      cases hl
    · intro h
      obtain ⟨l,hl,_⟩ := h
      cases hl
  | cons l ls ih =>
    have hcons := cons_sat (update x v b) l ls
    apply Iff.trans _ hcons.symm
    change RowMeaning x (if l.1=v then
      (if l.2=b then none else reduceRow v b ls)
      else (reduceRow v b ls).map (fun r => l::r)) ↔ _
    by_cases hv : l.1=v
    · have hu : update x v b l.1=b := by unfold update; rw [if_pos hv]
      rw [if_pos hv,hu]
      by_cases he : l.2=b
      · rw [if_pos he]
        exact ⟨fun _ => Or.inl he.symm,fun _ => True.intro⟩
      · rw [if_neg he]
        exact ⟨fun h => Or.inr (ih.1 h),fun h => match h with
          | .inl e => (he e.symm).elim
          | .inr e => ih.2 e⟩
    · have hu : update x v b l.1=x l.1 := by unfold update; rw [if_neg hv]
      rw [if_neg hv,hu]
      cases hr : reduceRow v b ls with
      | none =>
        rw [hr] at ih
        exact ⟨fun _ => Or.inr (ih.1 True.intro),fun _ => True.intro⟩
      | some r =>
        rw [hr] at ih
        change ClauseSat (l::r) x ↔ _
        apply Iff.trans (cons_sat x l r)
        exact ⟨fun h => match h with
          | .inl e => .inl e | .inr e => .inr (ih.1 e),
          fun h => match h with
          | .inl e => .inl e | .inr e => .inr (ih.2 e)⟩

theorem restriction_correct (v : Nat) (b : Bool) (f : Formula) (x : Assignment) :
    FormulaSat (restrict v b f) x ↔ FormulaSat f (update x v b) := by
  induction f with
  | nil =>
    constructor
    · intro _ c hc
      cases hc
    · intro _ c hc
      cases hc
  | cons c cs ih =>
    have h := row_correct v b c x
    apply Iff.trans _ (formula_cons (update x v b) c cs).symm
    unfold restrict
    cases hr : reduceRow v b c with
    | none =>
      rw [hr] at h
      exact ⟨fun e => ⟨h.1 True.intro,ih.1 e⟩,fun e => ih.2 e.2⟩
    | some r =>
      rw [hr] at h
      change FormulaSat (r::restrict v b cs) x ↔ _
      apply Iff.trans (formula_cons x r (restrict v b cs))
      exact ⟨fun e => ⟨h.1 e.1,ih.1 e.2⟩,fun e => ⟨h.2 e.1,ih.2 e.2⟩⟩

theorem row_remaining (v : Nat) (b : Bool) (c r : Clause)
    (h : reduceRow v b c=some r) : ∀ l∈r, l∈c ∧ l.1≠v := by
  induction c generalizing r with
  | nil =>
    change some []=some r at h
    cases h
    intro l hl; cases hl
  | cons a as ih =>
    change (if a.1=v then (if a.2=b then none else reduceRow v b as)
      else (reduceRow v b as).map (fun q => a::q))=some r at h
    by_cases hv : a.1=v
    · rw [if_pos hv] at h
      by_cases hb : a.2=b
      · rw [if_pos hb] at h; cases h
      · rw [if_neg hb] at h
        intro l hl
        have ht := ih r h l hl
        exact ⟨List.Mem.tail _ ht.1,ht.2⟩
    · rw [if_neg hv] at h
      cases he : reduceRow v b as with
      | none => rw [he] at h; cases h
      | some q =>
        rw [he] at h
        change some (a::q)=some r at h
        cases h
        intro l hl
        cases hl with
        | head => exact ⟨List.Mem.head _,hv⟩
        | tail _ hm =>
          have ht := ih q he l hm
          exact ⟨List.Mem.tail _ ht.1,ht.2⟩

theorem restrict_remaining (v : Nat) (b : Bool) (f : Formula) :
    ∀ r∈restrict v b f, ∃ c∈f, ∀ l∈r, l∈c ∧ l.1≠v := by
  induction f with
  | nil => intro r hr; cases hr
  | cons c cs ih =>
    intro r hr
    unfold restrict at hr
    cases he : reduceRow v b c with
    | none =>
      rw [he] at hr
      obtain ⟨d,hd,ht⟩ := ih r hr
      exact ⟨d,List.Mem.tail _ hd,ht⟩
    | some q =>
      rw [he] at hr
      change r∈q::restrict v b cs at hr
      cases hr with
      | head => exact ⟨c,List.Mem.head _,row_remaining v b c _ he⟩
      | tail _ hm =>
        obtain ⟨d,hd,ht⟩ := ih r hm
        exact ⟨d,List.Mem.tail _ hd,ht⟩

theorem restrict_valid (n v : Nat) (b : Bool) (f : Formula)
    (h : validFormula n f=true) : validFormula n (restrict v b f)=true := by
  apply every_complete
  intro r hr
  apply every_complete
  intro l hl
  obtain ⟨c,hc,ht⟩ := restrict_remaining v b f r hr
  exact formula_ok n f h c hc l (ht l hl).1

theorem update_same_on (x : Assignment) (v : Nat) (f : Formula)
    (h : FormulaSat f x) : FormulaSat f (update x v (x v)) := by
  intro c hc
  obtain ⟨l,hl,he⟩ := h c hc
  refine ⟨l,hl,?_⟩
  unfold update
  by_cases e : l.1=v
  · rw [if_pos e,← e]
    exact he
  · rw [if_neg e]
    exact he

def Satisfiable (f : Formula) : Prop := ∃ x, FormulaSat f x

theorem shannon (v : Nat) (f : Formula) :
    Satisfiable f ↔ Satisfiable (restrict v false f) ∨ Satisfiable (restrict v true f) := by
  constructor
  · intro h
    obtain ⟨x,hx⟩ := h
    have ht := (restriction_correct v (x v) f x).2 (update_same_on x v f hx)
    cases he : x v with
    | false =>
      rw [he] at ht
      exact Or.inl ⟨x,ht⟩
    | true =>
      rw [he] at ht
      exact Or.inr ⟨x,ht⟩
  · intro h
    cases h with
    | inl h =>
      obtain ⟨x,hx⟩ := h
      exact ⟨update x v false,(restriction_correct v false f x).1 hx⟩
    | inr h =>
      obtain ⟨x,hx⟩ := h
      exact ⟨update x v true,(restriction_correct v true f x).1 hx⟩

def Covered (vs : List Nat) (f : Formula) : Prop :=
  ∀ c∈f, ∀ l∈c, l.1∈vs

theorem restrict_cover (v : Nat) (b : Bool) (vs : List Nat) (f : Formula)
    (h : Covered (v::vs) f) : Covered vs (restrict v b f) := by
  intro r hr l hl
  obtain ⟨c,hc,ht⟩ := restrict_remaining v b f r hr
  have he := ht l hl
  cases h c hc l he.1 with
  | head => exact (he.2 rfl).elim
  | tail _ hm => exact hm

theorem covered_empty_width (f : Formula) (h : Covered [] f) : WidthTwo f := by
  intro c hc
  cases c with
  | nil => exact Nat.zero_le _
  | cons l ls => exact (nomatch h (l::ls) hc l (List.Mem.head _))

def leaf (n : Nat) (f : Formula) : Option Bool :=
  match solve n f with
  | .sat _ => some true
  | .unsat _ => some false
  | _ => none

def Answer (f : Formula) : Bool → Prop
  | true => Satisfiable f
  | false => Unsat f

theorem leaf_total (n : Nat) (f : Formula) (hf : validFormula n f=true) (hw : WidthTwo f) :
    ∃ b, leaf n f=some b ∧ Answer f b := by
  have hs := ProctorTotalTwoCNF.solve_spec n f
  unfold leaf
  cases h : solve n f with
  | invalid =>
    rw [h] at hs
    change validFormula n f=false at hs
    rw [hf] at hs
    cases hs
  | unsupported =>
    rw [h] at hs
    have he := hs.2
    rw [(supported_iff f).2 hw] at he
    cases he
  | internalError => exact (ProctorTotalTwoCNF.solve_no_internal_error n f h).elim
  | sat x => exact ⟨true,rfl,⟨x,ProctorTotalTwoCNF.solve_sat_sound n f x h⟩⟩
  | unsat p => exact ⟨false,rfl,ProctorTotalTwoCNF.solve_unsat_sound n f p h⟩

def combine : Option Bool → Option Bool → Option Bool
  | some a,some b => some (a || b)
  | _,_ => none

def branch (n : Nat) : List Nat → Formula → Option Bool
  | [],f => leaf n f
  | v::vs,f =>
    if supported f then leaf n f
    else combine (branch n vs (restrict v false f)) (branch n vs (restrict v true f))

theorem combine_correct (v : Nat) (f : Formula) (a b : Bool)
    (ha : Answer (restrict v false f) a) (hb : Answer (restrict v true f) b) :
    Answer f (a || b) := by
  cases a with
  | true => exact (shannon v f).2 (Or.inl ha)
  | false =>
    cases b with
    | true => exact (shannon v f).2 (Or.inr hb)
    | false =>
      intro h
      cases (shannon v f).1 h with
      | inl e => exact ha e
      | inr e => exact hb e

theorem branch_total (n : Nat) (vs : List Nat) (f : Formula)
    (hf : validFormula n f=true) (hc : Covered vs f) :
    ∃ b, branch n vs f=some b ∧ Answer f b := by
  induction vs generalizing f with
  | nil => exact leaf_total n f hf (covered_empty_width f hc)
  | cons v vs ih =>
    change ∃ b, (if supported f then leaf n f else
      combine (branch n vs (restrict v false f)) (branch n vs (restrict v true f)))=some b ∧ Answer f b
    cases he : supported f with
    | true => exact leaf_total n f hf ((supported_iff f).1 he)
    | false =>
      obtain ⟨a,ha,hta⟩ := ih (restrict v false f) (restrict_valid n v false f hf) (restrict_cover v false vs f hc)
      obtain ⟨b,hb,htb⟩ := ih (restrict v true f) (restrict_valid n v true f hf) (restrict_cover v true vs f hc)
      refine ⟨a || b,?_,combine_correct v f a b hta htb⟩
      rw [ha,hb] <;> rfl

def decideCNF (n : Nat) (f : Formula) : Option Bool := branch n (variables f) f

theorem general_total (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    ∃ b, decideCNF n f=some b ∧ Answer f b :=
  branch_total n (variables f) f hf (fun c hc l hl => variable_mem f c l hc hl)

-- An upper bound on the number of specialized leaf calls, not a
-- polynomial bound: the explicit branch list may have linear length.
def leafCalls (n : Nat) : List Nat → Formula → Nat
  | [],_ => 1
  | v::vs,f => if supported f then 1 else
      leafCalls n vs (restrict v false f)+leafCalls n vs (restrict v true f)

theorem one_le_pow (k : Nat) : 1≤2^k := by
  induction k with
  | zero => exact Nat.le_refl _
  | succ k ih =>
    rw [Nat.pow_succ,Nat.mul_succ,Nat.mul_one]
    exact Nat.le_trans ih (Nat.le_add_right _ _)

theorem leaf_calls_bound (n : Nat) (vs : List Nat) (f : Formula) :
    leafCalls n vs f≤2^vs.length := by
  induction vs generalizing f with
  | nil => exact Nat.le_refl _
  | cons v vs ih =>
    change (if supported f then 1 else leafCalls n vs (restrict v false f)+
      leafCalls n vs (restrict v true f))≤2^(vs.length+1)
    cases h : supported f with
    | true => exact one_le_pow _
    | false =>
      rw [Nat.pow_succ,Nat.mul_succ,Nat.mul_one]
      exact Nat.add_le_add (ih _) (ih _)

end ProctorGeneralBranching

#print axioms ProctorGeneralBranching.cons_sat
#print axioms ProctorGeneralBranching.formula_cons
#print axioms ProctorGeneralBranching.row_correct
#print axioms ProctorGeneralBranching.restriction_correct
#print axioms ProctorGeneralBranching.row_remaining
#print axioms ProctorGeneralBranching.restrict_remaining
#print axioms ProctorGeneralBranching.restrict_valid
#print axioms ProctorGeneralBranching.update_same_on
#print axioms ProctorGeneralBranching.shannon
#print axioms ProctorGeneralBranching.restrict_cover
#print axioms ProctorGeneralBranching.covered_empty_width
#print axioms ProctorGeneralBranching.leaf_total
#print axioms ProctorGeneralBranching.combine_correct
#print axioms ProctorGeneralBranching.branch_total
#print axioms ProctorGeneralBranching.general_total
#print axioms ProctorGeneralBranching.one_le_pow
#print axioms ProctorGeneralBranching.leaf_calls_bound
