/-! F035/F040: exact route witnesses and universal path-to-certificate
compilation for the existing implication graph. No fallback is used by
the theorem for a pair of returned routes. -/
namespace ProctorPathCompilerCompleteness
open ProctorHallDeficiency
open ProctorCapacityDeficiency (opposite)
open ProctorCapacityReplay (every)
open ProctorExecutableReplay (Step lookup stepCheck)
open ProctorUnifiedReplay (Proof validId validFormula validProof boundCheck check)
open ProctorResolutionBridge (compile compile_refutation)
open ProctorEnvelopeCompleteness (FormulaOK StepOK RowOK formula_ok row_cons batchRange compile_range envelope_of_proof)
open ProctorExecutableDiscovery (Trace trace_append trace_mem trace_check trace_frontier trace_range)
open ProctorImplicationPathDiscovery (Arc Routes arcs rowArcs Edge arcs_sound edge_find
  routeFor relax sweep saturate reach firstStep advanceStep first_checked advance_checked
  pathTail pathStart closeStep close_checked compilePair tryVar)
open ProctorBinarySquareDiscovery (checked checked_complete)

-- The actual list returned by the algorithm, not just its endpoint,
-- is a forward walk in the input arc list.
inductive Walk (es : List Arc) : Literal → List Literal → Literal → Prop where
  | nil (a : Literal) : Walk es a [] a
  | cons {a b z : Literal} {bs : List Literal} :
      (a,b)∈es → Walk es b bs z → Walk es a (b::bs) z

theorem walk_snoc (es : List Arc) {a b c : Literal} {ps : List Literal}
    (h : Walk es a ps b) (he : (b,c)∈es) :
    Walk es a (ps++[c]) c := by
  induction h with
  | nil => exact Walk.cons he (Walk.nil _)
  | cons he' _ ih => exact Walk.cons he' (ih he)

def WitnessOK (es : List Arc) (a : Literal) (rs : Routes) : Prop :=
  ∀ e∈rs, Walk es a e.2 e.1

theorem route_witness (es : List Arc) (a b : Literal) (rs : Routes)
    (h : WitnessOK es a rs) (ps : List Literal) (hp : routeFor b rs=some ps) :
    Walk es a ps b := by
  induction rs with
  | nil => cases hp
  | cons e rs ih =>
    cases e with
    | mk c qs =>
      change (if b=c then some qs else routeFor b rs)=some ps at hp
      by_cases z : b=c
      · cases z
        rw [if_pos rfl] at hp
        cases hp
        exact h (b,qs) (List.Mem.head _)
      · rw [if_neg z] at hp
        exact ih (fun e he => h e (List.Mem.tail _ he)) hp

theorem relax_witness (es : List Arc) (a : Literal) (rs : Routes) (e : Arc)
    (h : WitnessOK es a rs) (he : e∈es) :
    WitnessOK es a (relax rs e) := by
  unfold relax
  cases hs : routeFor e.1 rs with
  | none => exact h
  | some ps =>
    cases hd : routeFor e.2 rs with
    | some _qs => exact h
    | none =>
      intro p hp
      change p∈(e.2,ps++[e.2])::rs at hp
      cases hp with
      | head => exact walk_snoc es (route_witness es a e.1 rs h ps hs) he
      | tail _ hm => exact h p hm

theorem sweep_witness (es work : List Arc) (a : Literal) (rs : Routes)
    (h : WitnessOK es a rs) (he : ∀ e∈work, e∈es) :
    WitnessOK es a (sweep work rs) := by
  induction work generalizing rs with
  | nil => exact h
  | cons e rest ih =>
    change WitnessOK es a (sweep rest (relax rs e))
    exact ih _ (relax_witness es a rs e h (he e (List.Mem.head _)))
      (fun e hm => he e (List.Mem.tail _ hm))

theorem saturate_witness (es : List Arc) (a : Literal)
    (fuel : Nat) (rs : Routes) (h : WitnessOK es a rs) :
    WitnessOK es a (saturate es fuel rs) := by
  induction fuel generalizing rs with
  | zero => exact h
  | succ k ih =>
    exact ih _ (sweep_witness es es a rs h (fun _ he => he))

theorem reach_witness (es : List Arc) (a b : Literal) (ps : List Literal)
    (h : reach es a b=some ps) : Walk es a ps b := by
  have h0 : WitnessOK es a [(a,[])] := by
    intro e he
    cases he with
    | head => exact Walk.nil _
    | tail _ hz => cases hz
  exact route_witness es a b _ (saturate_witness es a es.length _ h0) ps h

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

private theorem row_arc_range (n : Nat) (c : Clause) (e : Arc)
    (hc : RowOK n c) (he : e∈rowArcs c) :
    validId n e.1.1=true ∧ validId n e.2.1=true := by
  cases c with
  | nil => cases he
  | cons a cs =>
    have ha := hc a (List.Mem.head _)
    cases cs with
    | nil =>
      change e∈[(opposite a,a)] at he
      cases he with
      | head => exact ⟨ha,ha⟩
      | tail _ hz => cases hz
    | cons b bs =>
      have hb := hc b (List.Mem.tail _ (List.Mem.head _))
      cases bs with
      | nil =>
        change e∈[(opposite a,b),(opposite b,a)] at he
        cases he with
        | head => exact ⟨ha,hb⟩
        | tail _ ht =>
          cases ht with
          | head => exact ⟨hb,ha⟩
          | tail _ hz => cases hz
      | cons _ _ => cases he

theorem arc_range (n : Nat) (f : Formula) (e : Arc)
    (hf : FormulaOK n f) (he : e∈arcs f) :
    validId n e.1.1=true ∧ validId n e.2.1=true := by
  induction f with
  | nil => cases he
  | cons c cs ih =>
    change e∈rowArcs c ++ arcs cs at he
    cases append_cases (rowArcs c) (arcs cs) e he with
    | inl h => exact row_arc_range n c e (hf c (List.Mem.head _)) h
    | inr h => exact ih (fun d hd => hf d (List.Mem.tail _ hd)) h

theorem trace_lookup_shift {n : Nat} {g h : Formula} {ss : List Step}
    (tr : Trace n g ss h) (i : Nat) (c : Clause)
    (hi : lookup g i=some c) : lookup h (ss.length+i)=some c := by
  induction tr generalizing i with
  | nil =>
    change lookup _ (0+i)=some c
    rw [Nat.zero_add]
    exact hi
  | @cons g h ss t _ _ _ ih =>
    have hs : lookup (t.tail::g) (i+1)=some c := hi
    have e := ih (i+1) hs
    change lookup h (ss.length+1+i)=some c
    rw [Nat.add_assoc,Nat.add_comm 1 i]
    exact e

private theorem advance_tail (s a b : Literal) (i : Nat) :
    (advanceStep s a b i).tail=[opposite s,b] := by
  cases a with
  | mk v pol => cases pol <;> rfl

private theorem advance_range (n : Nat) (s a b : Literal) (i : Nat)
    (hs : validId n s.1=true) (ha : validId n a.1=true)
    (hb : validId n b.1=true) : StepOK n (advanceStep s a b i) := by
  cases s with
  | mk sv sb =>
    cases b with
    | mk bv bb =>
      cases a with
      | mk av ab =>
        cases ab <;> exact ⟨ha,row_cons n sv (!sb) _ hs
          (row_cons n bv bb [] hb (fun _ h => nomatch h))⟩

private theorem first_range (n : Nat) (s b : Literal) (i : Nat)
    (hs : validId n s.1=true) (hb : validId n b.1=true) :
    StepOK n (firstStep s b i) := by
  cases s with
  | mk sv sb =>
    cases b with
    | mk bv bb =>
      exact ⟨hs,row_cons n sv (!sb) _ hs
        (row_cons n bv bb [] hb (fun _ h => nomatch h))⟩

theorem pathTail_complete (n : Nat) (f : Formula) (s a z : Literal)
    (bs : List Literal) (h : Walk (arcs f) a bs z)
    (hf : FormulaOK n f) (hs : validId n s.1=true)
    (g : Formula) (sub : ∀ c∈f, c∈g)
    (top : lookup g 0=some [opposite s,a]) :
    ∃ ss out, pathTail s a g bs=some (ss,out) ∧
      Trace n g ss out ∧ lookup out 0=some [opposite s,z] ∧ ss.length=bs.length := by
  induction h generalizing g with
  | nil => exact ⟨[],g,rfl,Trace.nil _,top,rfl⟩
  | @cons a b z bs he rest ih =>
    obtain ⟨i,hi⟩ := edge_find f g a b (arcs_sound f (a,b) he) sub
    let t := advanceStep s a b i
    have ht : stepCheck g t=true := advance_checked g s a b i top hi
    have hr := arc_range n f (a,b) hf he
    have hv : StepOK n t := advance_range n s a b i hs hr.left hr.right
    have sub' : ∀ c∈f, c∈t.tail::g := fun c hc => List.Mem.tail _ (sub c hc)
    have top' : lookup (t.tail::g) 0=some [opposite s,b] :=
      congrArg some (advance_tail s a b i)
    obtain ⟨ss,out,hh,tr,hl,hn⟩ := ih (t.tail::g) sub' top'
    refine ⟨t::ss,out,?_,Trace.cons t ht hv tr,hl,congrArg Nat.succ hn⟩
    unfold pathTail
    rw [hi]
    change (do
      let (ts,h) ← pathTail s b (t.tail::g) bs
      some (t::ts,h))=some (t::ss,out)
    rw [hh] <;> rfl

theorem pathStart_complete (n : Nat) (f : Formula) (s z : Literal)
    (bs : List Literal) (h : Walk (arcs f) s bs z)
    (hne : s≠z) (hf : FormulaOK n f) (g : Formula) (sub : ∀ c∈f, c∈g) :
    ∃ ss out, pathStart g s bs=some (ss,out) ∧
      Trace n g ss out ∧ lookup out 0=some [opposite s,z] ∧ ss.length=bs.length := by
  cases h with
  | nil => exact (hne rfl).elim
  | @cons a b z rest he hw =>
    obtain ⟨i,hi⟩ := edge_find f g a b (arcs_sound f (a,b) he) sub
    let t := firstStep a b i
    have ht : stepCheck g t=true := first_checked g a b i hi
    have hr := arc_range n f (a,b) hf he
    have hv : StepOK n t := first_range n a b i hr.left hr.right
    obtain ⟨ss,out,hh,tr,hl,hn⟩ := pathTail_complete n f a b z rest hw hf hr.left
      (t.tail::g) (fun c hc => List.Mem.tail _ (sub c hc)) rfl
    refine ⟨t::ss,out,?_,Trace.cons t ht hv tr,hl,congrArg Nat.succ hn⟩
    unfold pathStart
    rw [hi]
    change (do
      let (ts,h) ← pathTail a b (t.tail::g) rest
      some (t::ts,h))=some (t::ss,out)
    rw [hh] <;> rfl

private theorem opposite_ne (v : Nat) (b : Bool) : (v,b)≠(v,!b) := by
  intro h
  have e := congrArg Prod.snd h
  cases b <;> exact Bool.noConfusion e

theorem walk_source_range (n : Nat) (f : Formula) (a z : Literal)
    (bs : List Literal) (h : Walk (arcs f) a bs z)
    (hne : a≠z) (hf : FormulaOK n f) : validId n a.1=true := by
  cases h with
  | nil => exact (hne rfl).elim
  | @cons a b _z _rest he _hw => exact (arc_range n f (a,b) hf he).left

theorem compilePair_complete (n v : Nat) (f : Formula) (pos neg : List Literal)
    (hf : validFormula n f=true)
    (hp : Walk (arcs f) (v,true) pos (v,false))
    (hn : Walk (arcs f) (v,false) neg (v,true)) :
    ∃ p, compilePair f v pos neg=some p ∧ boundCheck n f ⟨n,f,p⟩=true := by
  have ho := formula_ok n f hf
  have hv : validId n v=true := walk_source_range n f _ _ pos hp (opposite_ne v true) ho
  obtain ⟨a,g,ha,ta,la,_na⟩ := pathStart_complete n f _ _ pos hp (opposite_ne v true)
    ho f (fun _ hc => hc)
  obtain ⟨b,h,hb,tb,lb,_nb⟩ := pathStart_complete n f _ _ neg hn (opposite_ne v false)
    ho g (fun c hc => trace_mem ta c hc)
  have old := trace_lookup_shift tb 0 [(v,false),(v,false)] la
  have old' : lookup h b.length=some [(v,false),(v,false)] := by
    rw [Nat.add_zero] at old
    exact old
  let t := closeStep v b.length
  have ht : stepCheck h t=true := close_checked h v b.length lb old'
  have hr : StepOK n t := ⟨hv,fun _ he => nomatch he⟩
  have tr : Trace n f (a++(b++[t])) ([]::h) :=
    trace_append ta (trace_append tb (Trace.cons t ht hr (Trace.nil _)))
  let ss := a++(b++[t])
  let p : Proof := ⟨compile v f ss,false,.empty⟩
  have hvalid : validProof n p=true := by
    change (every (batchRange n) (compile v f ss) && true)=true
    rw [compile_range n v f ss hv ho (trace_range tr)] <;> rfl
  have he : ProctorExecutableReplay.hasEmpty
      (ProctorResolutionBridge.sequentialFrontier f ss)=true := by
    rw [trace_frontier tr]
    rfl
  have hc : check f p=true := compile_refutation v f ss (trace_check tr) he
  refine ⟨p,?_,envelope_of_proof n f p hf hvalid hc⟩
  unfold compilePair
  rw [ha]
  change (do
    let (b,_) ← pathStart g (v,false) neg
    some ⟨compile v f (a++(b++[closeStep v b.length])),false,.empty⟩)=some p
  rw [hb] <;> rfl

theorem tryVar_complete (n v : Nat) (f : Formula) (pos neg : List Literal)
    (hf : validFormula n f=true)
    (hp : reach (arcs f) (v,true) (v,false)=some pos)
    (hn : reach (arcs f) (v,false) (v,true)=some neg) :
    ∃ p, tryVar f (arcs f) v=some p ∧ boundCheck n f ⟨n,f,p⟩=true := by
  obtain ⟨p,hp',hc⟩ := compilePair_complete n v f pos neg hf
    (reach_witness _ _ _ _ hp) (reach_witness _ _ _ _ hn)
  refine ⟨p,?_,hc⟩
  unfold tryVar
  rw [hp]
  change (do
    let neg' ← reach (arcs f) (v,false) (v,true)
    compilePair f v pos neg')=some p
  rw [hn]
  exact hp'

theorem checked_tryVar_complete (n v : Nat) (f : Formula) (pos neg : List Literal)
    (hf : validFormula n f=true)
    (hp : reach (arcs f) (v,true) (v,false)=some pos)
    (hn : reach (arcs f) (v,false) (v,true)=some neg) :
    ∃ p, checked n f (tryVar f (arcs f) v)=some p := by
  obtain ⟨p,h,hc⟩ := tryVar_complete n v f pos neg hf hp hn
  exact ⟨p,checked_complete n f _ p h hc⟩

end ProctorPathCompilerCompleteness

#print axioms ProctorPathCompilerCompleteness.walk_snoc
#print axioms ProctorPathCompilerCompleteness.route_witness
#print axioms ProctorPathCompilerCompleteness.relax_witness
#print axioms ProctorPathCompilerCompleteness.sweep_witness
#print axioms ProctorPathCompilerCompleteness.saturate_witness
#print axioms ProctorPathCompilerCompleteness.reach_witness
#print axioms ProctorPathCompilerCompleteness.arc_range
#print axioms ProctorPathCompilerCompleteness.trace_lookup_shift
#print axioms ProctorPathCompilerCompleteness.pathTail_complete
#print axioms ProctorPathCompilerCompleteness.pathStart_complete
#print axioms ProctorPathCompilerCompleteness.walk_source_range
#print axioms ProctorPathCompilerCompleteness.compilePair_complete
#print axioms ProctorPathCompilerCompleteness.tryVar_complete
#print axioms ProctorPathCompilerCompleteness.checked_tryVar_complete
