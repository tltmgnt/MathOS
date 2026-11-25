/-! F035/F038 candidate: ordinary completeness of the original typed
input-bound envelope checker, with identifier validity preserved.
No byte encoder or polynomial proof-size claim. -/
namespace ProctorEnvelopeCompleteness
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch lookup stepCheck hasEmpty and_true_local)
open ProctorCapacityReplay (test every every_sound)
open ProctorUnifiedReplay (Proof Envelope validId validClause validFormula validProof boundCheck check)
open ProctorResolutionBridge (Unsat copySteps extend compile step_complete sequentialCheck sequentialFrontier compile_refutation)
open ProctorOrdinaryCompleteness (Cover update cover_branch covered_false false_row lookup_exists variables rowVars empty_complete)

def RowOK (n : Nat) (c : Clause) : Prop := ∀ l∈c, validId n l.1=true
def FormulaOK (n : Nat) (f : Formula) : Prop := ∀ c∈f, RowOK n c
def StepOK (n : Nat) (s : Step) : Prop := validId n s.pivot=true ∧ RowOK n s.tail

theorem every_complete {α : Type} (p : α → Bool) (xs : List α)
    (h : ∀ a∈xs, p a=true) : every p xs=true := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change (p a && every p as)=true
    rw [h a (List.Mem.head _),ih (fun b hb => h b (List.Mem.tail _ hb))] <;> rfl

theorem formula_ok (n : Nat) (f : Formula) (h : validFormula n f=true) :
    FormulaOK n f :=
  fun c hc l hl => every_sound _ c (every_sound _ f h c hc) l hl

theorem row_cons (n v : Nat) (b : Bool) (c : Clause)
    (hv : validId n v=true) (hc : RowOK n c) : RowOK n ((v,b)::c) := by
  intro l hl
  cases hl with
  | head => exact hv
  | tail _ hm => exact hc l hm

theorem row_vars_ok (n : Nat) (c : Clause) (h : RowOK n c) :
    ∀ v∈rowVars c, validId n v=true := by
  induction c with
  | nil => intro v hv; cases hv
  | cons l ls ih =>
    intro v hv
    cases hv with
    | head => exact h l (List.Mem.head _)
    | tail _ hm => exact ih (fun a ha => h a (List.Mem.tail _ ha)) v hm

private theorem append_cases {α : Type} (xs ys : List α) (a : α)
    (h : a∈xs++ys) : a∈xs ∨ a∈ys := by
  induction xs with
  | nil => exact Or.inr h
  | cons b bs ih =>
    cases h with
    | head => exact Or.inl (List.Mem.head _)
    | tail _ hm =>
      cases ih hm with
      | inl e => exact Or.inl (List.Mem.tail _ e)
      | inr e => exact Or.inr e

theorem variables_ok (n : Nat) (f : Formula) (h : FormulaOK n f) :
    ∀ v∈variables f, validId n v=true := by
  induction f with
  | nil => intro v hv; cases hv
  | cons c cs ih =>
    intro v hv
    cases append_cases (rowVars c) (variables cs) v hv with
    | inl e => exact row_vars_ok n c (h c (List.Mem.head _)) v e
    | inr e => exact ih (fun d hd => h d (List.Mem.tail _ hd)) v e

inductive ReachOK (n : Nat) : Formula → Formula → Prop where
  | refl (f : Formula) : ReachOK n f f
  | step {f g : Formula} (s : Step) :
      stepCheck f s=true → StepOK n s → ReachOK n (s.tail::f) g → ReachOK n f g

theorem reach_trans {n : Nat} {f g h : Formula}
    (a : ReachOK n f g) (b : ReachOK n g h) : ReachOK n f h := by
  induction a with
  | refl => exact b
  | step s hs hv rest ih => exact ReachOK.step s hs hv (ih b)

theorem reach_mem {n : Nat} {f g : Formula} (h : ReachOK n f g) (c : Clause)
    (hc : c∈f) : c∈g := by
  induction h with
  | refl => exact hc
  | step s hs hv rest ih => exact ih (List.Mem.tail _ hc)

theorem weaken_reach (n q : Nat) (g : Formula) (c path : Clause)
    (hq : validId n q=true) (hp : RowOK n path)
    (hc : c∈g) (h : ∀ l∈c, l∈path) : ReachOK n g (path::g) := by
  obtain ⟨i,hi⟩ := lookup_exists g c hc
  exact ReachOK.step ⟨i,i,q,path⟩
    (step_complete g ⟨i,i,q,path⟩ c c hi hi
      (fun l hl => Or.inr (h l hl)) (fun l hl => Or.inr (h l hl)))
    ⟨hq,hp⟩ (ReachOK.refl _)

theorem resolve_reach (n : Nat) (g : Formula) (v : Nat) (path : Clause)
    (hv : validId n v=true) (hc : RowOK n path)
    (hp : ((v,true)::path)∈g) (hn : ((v,false)::path)∈g) :
    ReachOK n g (path::g) := by
  obtain ⟨i,hi⟩ := lookup_exists g _ hp
  obtain ⟨j,hj⟩ := lookup_exists g _ hn
  have hpos : ∀ l∈((v,true)::path), l=(v,true) ∨ l∈path := by
    intro l hl
    cases hl with
    | head => exact Or.inl rfl
    | tail _ hm => exact Or.inr hm
  have hneg : ∀ l∈((v,false)::path), l=(v,false) ∨ l∈path := by
    intro l hl
    cases hl with
    | head => exact Or.inl rfl
    | tail _ hm => exact Or.inr hm
  exact ReachOK.step ⟨i,j,v,path⟩
    (step_complete g ⟨i,j,v,path⟩ _ _ hi hj hpos hneg) ⟨hv,hc⟩ (ReachOK.refl _)

theorem split_complete (n q : Nat) (hq : validId n q=true)
    (f : Formula) (vs : List Nat) (path : Clause) (x : Assignment)
    (u : Unsat f) (h : Cover f vs path x)
    (hv : ∀ v∈vs, validId n v=true) (hp : RowOK n path)
    (g : Formula) (sub : ∀ c∈f, c∈g) :
    ∃ g', ReachOK n g g' ∧ path∈g' := by
  induction vs generalizing path x g with
  | nil =>
    obtain ⟨c,hc,hf⟩ := false_row f x u
    exact ⟨path::g,weaken_reach n q g c path hq hp (sub c hc)
      (covered_false f path x h c hc hf),List.Mem.head _⟩
  | cons v vs ih =>
    have hval := hv v (List.Mem.head _)
    have ht : ∀ a∈vs, validId n a=true := fun a ha => hv a (List.Mem.tail _ ha)
    obtain ⟨g1,r1,p1⟩ := ih ((v,true)::path) (update x v false)
      (cover_branch f v vs path x false h) ht (row_cons n v true path hval hp) g sub
    have sub1 : ∀ c∈f, c∈g1 := fun c hc => reach_mem r1 c (sub c hc)
    obtain ⟨g2,r2,p2⟩ := ih ((v,false)::path) (update x v true)
      (cover_branch f v vs path x true h) ht (row_cons n v false path hval hp) g1 sub1
    exact ⟨path::g2,reach_trans (reach_trans r1 r2)
      (resolve_reach n g2 v path hval hp (reach_mem r2 _ p1) p2),List.Mem.head _⟩

theorem reach_trace {n : Nat} {f g : Formula} (h : ReachOK n f g) :
    ∃ ss : List Step, sequentialCheck f ss=true ∧ sequentialFrontier f ss=g ∧
      ∀ s∈ss, StepOK n s := by
  induction h with
  | refl => exact ⟨[],rfl,rfl,fun _ hs => nomatch hs⟩
  | step s hs hv rest ih =>
    obtain ⟨ss,hc,hf,hr⟩ := ih
    refine ⟨s::ss,?_,hf,?_⟩
    · change (stepCheck _ s && sequentialCheck (s.tail::_) ss)=true
      rw [hs,hc] <;> rfl
    · intro t ht
      cases ht with
      | head => exact hv
      | tail _ hm => exact hr t hm

def batchRange (n : Nat) (bs : Batch) : Bool :=
  every (fun s : Step => validId n s.pivot && validClause n s.tail) bs

theorem step_range (n : Nat) (s : Step) (h : StepOK n s) :
    (validId n s.pivot && validClause n s.tail)=true := by
  have hc : validClause n s.tail=true := every_complete _ _ h.right
  rw [h.left,hc] <;> rfl

theorem copy_range (n q i : Nat) (f : Formula)
    (hq : validId n q=true) (hf : FormulaOK n f) :
    batchRange n (copySteps q i f)=true := by
  induction f generalizing i with
  | nil => rfl
  | cons c cs ih =>
    change ((validId n q && validClause n c) &&
      batchRange n (copySteps q (i+1) cs))=true
    have hc : validClause n c=true := every_complete _ _ (hf c (List.Mem.head _))
    rw [hq,hc,ih (i+1) (fun d hd => hf d (List.Mem.tail _ hd))] <;> rfl

theorem compile_range (n q : Nat) (f : Formula) (ss : List Step)
    (hq : validId n q=true) (hf : FormulaOK n f)
    (hs : ∀ s∈ss, StepOK n s) :
    every (batchRange n) (compile q f ss)=true := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    have hv := hs s (List.Mem.head _)
    have hf' : FormulaOK n (s.tail::f) := by
      intro c hc
      cases hc with
      | head => exact hv.right
      | tail _ hm => exact hf c hm
    change (((validId n s.pivot && validClause n s.tail) &&
      batchRange n (copySteps q 0 f)) &&
      every (batchRange n) (compile q (s.tail::f) ss))=true
    rw [step_range n s hv,copy_range n q 0 f hq hf,
      ih (s.tail::f) hf' (fun t ht => hs t (List.Mem.tail _ ht))] <;> rfl

theorem envelope_of_proof (n : Nat) (f : Formula) (p : Proof)
    (hf : validFormula n f=true) (hp : validProof n p=true)
    (hc : check f p=true) : boundCheck n f ⟨n,f,p⟩=true := by
  unfold boundCheck
  dsimp only
  rw [hf,hp,hc]
  unfold test
  rw [if_pos rfl,if_pos rfl] <;> rfl

theorem positive_complete (n : Nat) (f : Formula)
    (hn : 0<n) (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p : Proof, boundCheck n f ⟨n,f,p⟩=true := by
  have hq : validId n 1=true := by
    unfold validId test
    rw [if_pos (Nat.zero_lt_succ 0),if_pos (Nat.succ_le_of_lt hn)] <;> rfl
  have ho := formula_ok n f hf
  obtain ⟨g,hr,he⟩ := split_complete n 1 hq f (variables f) [] (fun _ => false) hu
    (fun c hc l hl => Or.inl (ProctorOrdinaryCompleteness.variable_mem f c l hc hl))
    (variables_ok n f ho) (fun _ hl => nomatch hl) f (fun _ hc => hc)
  obtain ⟨ss,hc,hfront,hs⟩ := reach_trace hr
  let p : Proof := ⟨compile 1 f ss,false,.empty⟩
  have hp : validProof n p=true := by
    change (every (batchRange n) (compile 1 f ss) && true)=true
    rw [compile_range n 1 f ss hq ho hs] <;> rfl
  have hcheck : check f p=true :=
    compile_refutation 1 f ss hc (hfront.symm ▸ empty_complete g he)
  exact ⟨p,envelope_of_proof n f p hf hp hcheck⟩

theorem zero_complete (f : Formula) (hf : validFormula 0 f=true) (hu : Unsat f) :
    ∃ p : Proof, boundCheck 0 f ⟨0,f,p⟩=true := by
  obtain ⟨c,hc,_⟩ := false_row f (fun _ => false) hu
  have hrow := formula_ok 0 f hf c hc
  have he : ([] : Clause)∈f := by
    cases c with
    | nil => exact hc
    | cons l ls =>
      have hv := hrow l (List.Mem.head _)
      have h := and_true_local _ _ hv
      have lo := ProctorCapacityReplay.test_sound _ h.left
      have hi := ProctorCapacityReplay.test_sound _ h.right
      exact (Nat.not_lt_of_ge hi lo).elim
  let p : Proof := ⟨[],false,.empty⟩
  have hp : validProof 0 p=true := rfl
  have hcheck : check f p=true := by
    change (true && hasEmpty f)=true
    rw [empty_complete f he] <;> rfl
  exact ⟨p,envelope_of_proof 0 f p hf hp hcheck⟩

theorem envelope_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p : Proof, boundCheck n f ⟨n,f,p⟩=true := by
  cases n with
  | zero => exact zero_complete f hf hu
  | succ n => exact positive_complete (n+1) f (Nat.zero_lt_succ n) hf hu

theorem envelope_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    (∃ e : Envelope, boundCheck n f e=true) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨e,he⟩ := h
    exact ProctorUnifiedReplay.bound_sound n f e he
  · intro hu
    obtain ⟨p,hp⟩ := envelope_complete n f hf hu
    exact ⟨⟨n,f,p⟩,hp⟩

end ProctorEnvelopeCompleteness

#print axioms ProctorEnvelopeCompleteness.every_complete
#print axioms ProctorEnvelopeCompleteness.formula_ok
#print axioms ProctorEnvelopeCompleteness.row_cons
#print axioms ProctorEnvelopeCompleteness.row_vars_ok
#print axioms ProctorEnvelopeCompleteness.variables_ok
#print axioms ProctorEnvelopeCompleteness.reach_trans
#print axioms ProctorEnvelopeCompleteness.reach_mem
#print axioms ProctorEnvelopeCompleteness.weaken_reach
#print axioms ProctorEnvelopeCompleteness.resolve_reach
#print axioms ProctorEnvelopeCompleteness.split_complete
#print axioms ProctorEnvelopeCompleteness.reach_trace
#print axioms ProctorEnvelopeCompleteness.step_range
#print axioms ProctorEnvelopeCompleteness.copy_range
#print axioms ProctorEnvelopeCompleteness.compile_range
#print axioms ProctorEnvelopeCompleteness.envelope_of_proof
#print axioms ProctorEnvelopeCompleteness.positive_complete
#print axioms ProctorEnvelopeCompleteness.zero_complete
#print axioms ProctorEnvelopeCompleteness.envelope_complete
#print axioms ProctorEnvelopeCompleteness.envelope_iff
