/-! F035/F040 baseline: deterministic exhaustive generator with
candidate universal ordinary correctness. The search tree is exponential;
no polynomial discovery or bit-machine cost theorem. -/
namespace ProctorExecutableDiscovery
open ProctorHallDeficiency
open ProctorExecutableReplay (Step lookup stepCheck hasEmpty contains)
open ProctorCapacityReplay (test test_sound every every_sound)
open ProctorUnifiedReplay (Proof Envelope validId validClause validFormula validProof boundCheck check)
open ProctorResolutionBridge (Unsat compile step_complete sequentialCheck sequentialFrontier compile_refutation contains_complete)
open ProctorOrdinaryCompleteness (Cover update cover_branch covered_false false_row variables empty_complete)
open ProctorEnvelopeCompleteness (RowOK FormulaOK StepOK formula_ok row_cons variables_ok every_complete batchRange compile_range envelope_of_proof)

def findRow (p : Clause → Bool) : Formula → Option Nat
  | [] => none
  | c::cs => if p c then some 0 else (findRow p cs).map (fun i => i+1)

theorem find_complete (p : Clause → Bool) (g : Formula)
    (h : ∃ c∈g, p c=true) :
    ∃ i, findRow p g=some i := by
  induction g with
  | nil =>
    obtain ⟨c,hc,_⟩ := h
    cases hc
  | cons c cs ih =>
    cases e : p c with
    | true =>
      exact ⟨0,by rw [findRow,e]; rfl⟩
    | false =>
      obtain ⟨d,hd,hp⟩ := h
      cases hd with
      | head => rw [e] at hp; cases hp
      | tail _ hm =>
        obtain ⟨i,hi⟩ := ih ⟨d,hm,hp⟩
        exact ⟨i+1,by rw [findRow,e]; change (findRow p cs).map _=some _; rw [hi]; rfl⟩

theorem find_sound (p : Clause → Bool) (g : Formula) (i : Nat)
    (h : findRow p g=some i) :
    ∃ c, lookup g i=some c ∧ p c=true := by
  induction g generalizing i with
  | nil => cases h
  | cons c cs ih =>
    cases e : p c with
    | true =>
      rw [findRow,e] at h
      change some 0=some i at h
      cases h
      exact ⟨c,rfl,e⟩
    | false =>
      rw [findRow,e] at h
      change (findRow p cs).map (fun j => j+1)=some i at h
      cases z : findRow p cs with
      | none => rw [z] at h; cases h
      | some j =>
        rw [z] at h
        change some (j+1)=some i at h
        cases h
        obtain ⟨d,hd,hp⟩ := ih j z
        exact ⟨d,hd,hp⟩

def contained (path row : Clause) : Bool :=
  every (fun l => contains l path) row

theorem contained_complete (path c : Clause) (h : ∀ l∈c, l∈path) :
    contained path c=true :=
  every_complete _ _ (fun l hl => contains_complete l path (h l hl))

theorem contained_sound (path c : Clause) (h : contained path c=true) :
    ∀ l∈c, l∈path :=
  fun l hl => ProctorExecutableReplay.contains_sound l path (every_sound _ c h l hl)

theorem locate_exact (g : Formula) (c : Clause) (h : c∈g) :
    ∃ i, findRow (fun d => test (d=c)) g=some i ∧ lookup g i=some c := by
  have ht : test (c=c)=true := by unfold test; rw [if_pos rfl]
  obtain ⟨i,hi⟩ := find_complete (fun d => test (d=c)) g ⟨c,h,ht⟩
  obtain ⟨d,hd,hp⟩ := find_sound (fun d => test (d=c)) g i hi
  have e : d=c := test_sound _ hp
  cases e
  exact ⟨i,hi,hd⟩

inductive Trace (n : Nat) : Formula → List Step → Formula → Prop where
  | nil (g : Formula) : Trace n g [] g
  | cons {g h : Formula} {ss : List Step} (s : Step) :
      stepCheck g s=true → StepOK n s → Trace n (s.tail::g) ss h →
      Trace n g (s::ss) h

theorem trace_append {n : Nat} {f g h : Formula} {as bs : List Step}
    (a : Trace n f as g) (b : Trace n g bs h) :
    Trace n f (as++bs) h := by
  induction a with
  | nil => exact b
  | cons s hc hr rest ih => exact Trace.cons s hc hr (ih b)

theorem trace_mem {n : Nat} {f g : Formula} {ss : List Step}
    (h : Trace n f ss g) (c : Clause) (hc : c∈f) : c∈g := by
  induction h with
  | nil => exact hc
  | cons s hs hv rest ih => exact ih (List.Mem.tail _ hc)

theorem trace_check {n : Nat} {f g : Formula} {ss : List Step}
    (h : Trace n f ss g) : sequentialCheck f ss=true := by
  induction h with
  | nil => rfl
  | cons s hc hr rest ih =>
    change (stepCheck _ s && sequentialCheck (s.tail::_ ) _)=true
    rw [hc,ih] <;> rfl

theorem trace_frontier {n : Nat} {f g : Formula} {ss : List Step}
    (h : Trace n f ss g) : sequentialFrontier f ss=g := by
  induction h with
  | nil => rfl
  | cons s hc hr rest ih => exact ih

theorem trace_range {n : Nat} {f g : Formula} {ss : List Step}
    (h : Trace n f ss g) : ∀ s∈ss, StepOK n s := by
  induction h with
  | nil => intro s hs; cases hs
  | cons s hc hr rest ih =>
    intro t ht
    cases ht with
    | head => exact hr
    | tail _ hm => exact ih t hm

-- Search for a clause contained in the blocking path, not merely an
-- arbitrary row falsified by a partial assignment. All references
-- refer to the current explicit, accumulating frontier.
def build (q : Nat) : List Nat → Formula → Clause → Option (List Step × Formula)
  | [],g,path => do
    let i ← findRow (contained path) g
    some ([⟨i,i,q,path⟩],path::g)
  | v::vs,g,path => do
    let (a,h) ← build q vs g ((v,true)::path)
    let (b,j) ← build q vs h ((v,false)::path)
    let i ← findRow (fun c => test (c=(v,true)::path)) j
    let k ← findRow (fun c => test (c=(v,false)::path)) j
    some (a++(b++[⟨i,k,v,path⟩]),path::j)

theorem build_complete (n q : Nat) (hq : validId n q=true)
    (f : Formula) (vs : List Nat) (path : Clause) (x : Assignment)
    (u : Unsat f) (h : Cover f vs path x)
    (hv : ∀ v∈vs, validId n v=true) (hp : RowOK n path)
    (g : Formula) (sub : ∀ c∈f, c∈g) :
    ∃ ss g', build q vs g path=some (ss,g') ∧ Trace n g ss g' ∧ path∈g' := by
  induction vs generalizing path x g with
  | nil =>
    obtain ⟨c,hc,hf⟩ := false_row f x u
    have hs := contained_complete path c (covered_false f path x h c hc hf)
    obtain ⟨i,hi⟩ := find_complete (contained path) g ⟨c,sub c hc,hs⟩
    obtain ⟨d,hd,hdp⟩ := find_sound (contained path) g i hi
    let s : Step := ⟨i,i,q,path⟩
    have hstep : stepCheck g s=true :=
      step_complete g s d d hd hd
        (fun l hl => Or.inr (contained_sound path d hdp l hl))
        (fun l hl => Or.inr (contained_sound path d hdp l hl))
    refine ⟨[s],path::g,?_,Trace.cons s hstep ⟨hq,hp⟩ (Trace.nil _),List.Mem.head _⟩
    unfold build
    rw [hi] <;> rfl
  | cons v vs ih =>
    have hval := hv v (List.Mem.head _)
    have ht : ∀ a∈vs, validId n a=true := fun a ha => hv a (List.Mem.tail _ ha)
    obtain ⟨a,g1,ha,ra,p1⟩ := ih ((v,true)::path) (update x v false)
      (cover_branch f v vs path x false h) ht (row_cons n v true path hval hp) g sub
    have sub1 : ∀ c∈f, c∈g1 := fun c hc => trace_mem ra c (sub c hc)
    obtain ⟨b,g2,hb,rb,p2⟩ := ih ((v,false)::path) (update x v true)
      (cover_branch f v vs path x true h) ht (row_cons n v false path hval hp) g1 sub1
    obtain ⟨i,hi,hip⟩ := locate_exact g2 ((v,true)::path) (trace_mem rb _ p1)
    obtain ⟨j,hj,hjn⟩ := locate_exact g2 ((v,false)::path) p2
    let s : Step := ⟨i,j,v,path⟩
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
    have hs : stepCheck g2 s=true := step_complete g2 s _ _ hip hjn hpos hneg
    refine ⟨a++(b++[s]),path::g2,?_,trace_append ra
      (trace_append rb (Trace.cons s hs ⟨hval,hp⟩ (Trace.nil _))),List.Mem.head _⟩
    unfold build
    rw [ha]
    change (do
      let (b,h) ← build q vs g1 ((v,false)::path)
      let i ← findRow (fun c => test (c=(v,true)::path)) h
      let j ← findRow (fun c => test (c=(v,false)::path)) h
      some (a++(b++[⟨i,j,v,path⟩]),path::h))=_
    rw [hb]
    change (do
      let i ← findRow (fun c => test (c=(v,true)::path)) g2
      let j ← findRow (fun c => test (c=(v,false)::path)) g2
      some (a++(b++[⟨i,j,v,path⟩]),path::g2))=_
    rw [hi,hj] <;> rfl

def generate (n : Nat) (f : Formula) : Option Proof :=
  if n=0 then some ⟨[],false,.empty⟩
  else (build 1 (variables f) f []).map (fun r => ⟨compile 1 f r.1,false,.empty⟩)

theorem generate_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p, generate n f=some p ∧ boundCheck n f ⟨n,f,p⟩=true := by
  by_cases hn : n=0
  · cases hn
    have he : ([] : Clause)∈f := by
      obtain ⟨c,hc,_⟩ := false_row f (fun _ => false) hu
      have hr := formula_ok 0 f hf c hc
      cases c with
      | nil => exact hc
      | cons l ls =>
        have hv := hr l (List.Mem.head _)
        have h := ProctorExecutableReplay.and_true_local _ _ hv
        exact (Nat.not_lt_of_ge (test_sound _ h.right) (test_sound _ h.left)).elim
    let p : Proof := ⟨[],false,.empty⟩
    have hc : check f p=true := by
      change (true && hasEmpty f)=true
      rw [empty_complete f he] <;> rfl
    exact ⟨p,rfl,envelope_of_proof 0 f p hf rfl hc⟩
  · have hq : validId n 1=true := by
      unfold validId test
      rw [if_pos (Nat.zero_lt_succ 0),if_pos (Nat.succ_le_of_lt (Nat.pos_of_ne_zero hn))] <;> rfl
    have ho := formula_ok n f hf
    obtain ⟨ss,g,hb,ht,he⟩ := build_complete n 1 hq f (variables f) [] (fun _ => false) hu
      (fun c hc l hl => Or.inl (ProctorOrdinaryCompleteness.variable_mem f c l hc hl))
      (variables_ok n f ho) (fun _ hl => nomatch hl) f (fun _ hc => hc)
    let p : Proof := ⟨compile 1 f ss,false,.empty⟩
    have hp : validProof n p=true := by
      change (every (batchRange n) (compile 1 f ss) && true)=true
      rw [compile_range n 1 f ss hq ho (trace_range ht)] <;> rfl
    have hc : check f p=true :=
      compile_refutation 1 f ss (trace_check ht) ((trace_frontier ht).symm ▸ empty_complete g he)
    refine ⟨p,?_,envelope_of_proof n f p hf hp hc⟩
    unfold generate
    rw [if_neg hn,hb] <;> rfl

def decide (n : Nat) (f : Formula) : Bool :=
  match generate n f with | none => false | some p => boundCheck n f ⟨n,f,p⟩

theorem decide_sound (n : Nat) (f : Formula) (h : decide n f=true) : Unsat f := by
  unfold decide at h
  cases e : generate n f with
  | none => rw [e] at h; cases h
  | some p => rw [e] at h; exact ProctorUnifiedReplay.bound_sound n f _ h

theorem decide_complete (n : Nat) (f : Formula) (hf : validFormula n f=true)
    (h : Unsat f) : decide n f=true := by
  obtain ⟨p,hp,hc⟩ := generate_complete n f hf h
  unfold decide
  rw [hp]
  exact hc

theorem decide_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    decide n f=true ↔ Unsat f :=
  ⟨decide_sound n f,decide_complete n f hf⟩

end ProctorExecutableDiscovery

#print axioms ProctorExecutableDiscovery.find_complete
#print axioms ProctorExecutableDiscovery.find_sound
#print axioms ProctorExecutableDiscovery.contained_complete
#print axioms ProctorExecutableDiscovery.contained_sound
#print axioms ProctorExecutableDiscovery.locate_exact
#print axioms ProctorExecutableDiscovery.trace_append
#print axioms ProctorExecutableDiscovery.trace_mem
#print axioms ProctorExecutableDiscovery.trace_check
#print axioms ProctorExecutableDiscovery.trace_frontier
#print axioms ProctorExecutableDiscovery.trace_range
#print axioms ProctorExecutableDiscovery.build_complete
#print axioms ProctorExecutableDiscovery.generate_complete
#print axioms ProctorExecutableDiscovery.decide_sound
#print axioms ProctorExecutableDiscovery.decide_complete
#print axioms ProctorExecutableDiscovery.decide_iff
