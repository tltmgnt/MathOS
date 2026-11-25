/-! F035: exact token counts for finite SAT witnesses and empty-terminal
resolution certificates of bounded row width. These count natural tokens,
not decimal bytes or machine operations. -/
namespace ProctorWireTokenBounds
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorUnifiedReplay (Proof Envelope)
open ProctorWireRoundtrip (encItems encList encLiteral encClause encFormula encExpected)
open ProctorEnvelopeRoundtrip (encStep encBatch encProof encEnvelope)
open ProctorPathResourceBounds (occurrences steps)
open ProctorOrdinaryCompleteness (rowVars variables)
open ProctorFiniteModel (materialize materialize_length modelTokens)
open ProctorSerializedTwoCNF (Witness tokens produce)
open ProctorTotalTwoCNF (WidthTwo solve solve_size)
open ProctorResolutionBridge (copySteps extend compile)
open ProctorImplicationPathDiscovery (pathStart pathTail firstStep advanceStep closeStep compilePair tryVar arcs reach)
open ProctorBinarySquareDiscovery (checked)
private theorem len_append {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons a as ih =>
    change (as++ys).length+1=as.length+1+ys.length
    rw [ih,Nat.add_assoc as.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

private theorem mul_add' (a b c : Nat) : a*(b+c)=a*b+a*c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change a*(b+c+1)=a*b+a*(c+1)
    rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]

private theorem sum_swap (a b c d : Nat) : (a+b)+(c+d)=(a+c)+(b+d) := by
  rw [Nat.add_assoc a b (c+d),← Nat.add_assoc b c d,Nat.add_comm b c,
    Nat.add_assoc c b d,← Nat.add_assoc a c (b+d)]

theorem variables_length (f : Formula) : (variables f).length=occurrences f := by
  have row : ∀ c : Clause, (rowVars c).length=c.length := by
    intro c
    induction c with
    | nil => rfl
    | cons l ls ih => exact congrArg Nat.succ ih
  induction f with
  | nil => rfl
  | cons c cs ih =>
    change (rowVars c++variables cs).length=c.length+occurrences cs
    rw [len_append,row,ih]

theorem literal_length (l : Literal) : (encLiteral l).length=2 := rfl

theorem clause_length (c : Clause) : (encClause c).length=2*c.length+1 := by
  have h : ∀ xs : Clause, (encItems encLiteral xs).length=2*xs.length := by
    intro xs
    induction xs with
    | nil => rfl
    | cons a as ih =>
      change (encLiteral a++encItems encLiteral as).length=2*(as.length+1)
      rw [len_append,literal_length,ih,Nat.mul_succ,Nat.add_comm 2]
  change (encItems encLiteral c).length+1=_
  rw [h]

theorem formula_length (f : Formula) : (encFormula f).length=2*occurrences f+f.length+1 := by
  have h : ∀ xs : Formula, (encItems encClause xs).length=2*occurrences xs+xs.length := by
    intro xs
    induction xs with
    | nil => rfl
    | cons c cs ih =>
      change (encClause c++encItems encClause cs).length=2*(c.length+occurrences cs)+(cs.length+1)
      rw [len_append,clause_length,ih,mul_add']
      rw [sum_swap (2*c.length) 1 (2*occurrences cs) cs.length,Nat.add_comm 1 cs.length]
  change (encItems encClause f).length+1=_
  rw [h]

theorem expected_length (n : Nat) (f : Formula) :
    (encExpected n f).length=2*occurrences f+f.length+3 := by
  change (encFormula f).length+2=_
  rw [formula_length,Nat.add_assoc]

theorem sat_tokens_length (f : Formula) (x : Assignment) :
    (tokens (.sat (materialize x (variables f)))).length=2*occurrences f+2 := by
  change (encClause (materialize x (variables f))).length+1=_
  rw [clause_length,materialize_length,variables_length,Nat.add_assoc]

theorem step_length (s : Step) :
    (encStep s).length=2*s.tail.length+4 := by
  change (encClause s.tail).length+3=_
  rw [clause_length,Nat.add_assoc]

def NarrowSteps (ss : List Step) : Prop := ∀ s∈ss, s.tail.length≤2
def NarrowBatches (bs : List Batch) : Prop := ∀ b∈bs, NarrowSteps b

theorem narrow_step_length (s : Step) (h : s.tail.length≤2) : (encStep s).length≤8 := by
  rw [step_length]
  exact Nat.add_le_add_right (Nat.mul_le_mul_left 2 h) 4

theorem batch_length (b : Batch) (h : NarrowSteps b) : (encBatch b).length≤8*b.length+1 := by
  have hh : ∀ xs : Batch, NarrowSteps xs → (encItems encStep xs).length≤8*xs.length := by
    intro xs hx
    induction xs with
    | nil => exact Nat.le_refl _
    | cons s ss ih =>
      change (encStep s++encItems encStep ss).length≤8*(ss.length+1)
      rw [len_append,Nat.mul_succ,Nat.add_comm (8*ss.length)]
      exact Nat.add_le_add (narrow_step_length s (hx s (List.Mem.head _)))
        (ih (fun t ht => hx t (List.Mem.tail _ ht)))
  exact Nat.add_le_add_right (hh b h) 1

theorem batches_length (bs : List Batch) (h : NarrowBatches bs) :
    (encList encBatch bs).length≤8*steps bs+bs.length+1 := by
  have hh : ∀ xs : List Batch, NarrowBatches xs →
      (encItems encBatch xs).length≤8*steps xs+xs.length := by
    intro xs hx
    induction xs with
    | nil => exact Nat.le_refl _
    | cons b bs ih =>
      change (encBatch b++encItems encBatch bs).length≤8*(b.length+steps bs)+(bs.length+1)
      rw [len_append,mul_add']
      have hb := batch_length b (hx b (List.Mem.head _))
      have ht := ih (fun t ht => hx t (List.Mem.tail _ ht))
      have hz := Nat.add_le_add hb ht
      rw [sum_swap (8*b.length) 1 (8*steps bs) bs.length,Nat.add_comm 1 bs.length] at hz
      exact hz
  exact Nat.add_le_add_right (hh bs h) 1

theorem proof_length (p : Proof) (ht : p.terminal=.empty) (h : NarrowBatches p.batches) :
    (encProof p).length≤8*steps p.batches+p.batches.length+3 := by
  cases p with
  | mk bs aug t =>
    change t=.empty at ht
    cases ht
    change (encList encBatch bs++[if aug then 1 else 0,0]).length≤8*steps bs+bs.length+3
    rw [len_append]
    change (encList encBatch bs).length+2≤_
    exact Nat.add_le_add_right (batches_length bs h) 2

theorem unsat_tokens_length (n : Nat) (f : Formula) (p : Proof)
    (ht : p.terminal=.empty) (h : NarrowBatches p.batches) :
    (tokens (.unsat ⟨n,f,p⟩)).length≤
      2*occurrences f+f.length+1+(8*steps p.batches+p.batches.length+3)+3 := by
  change (encFormula f++encProof p).length+3≤_
  rw [len_append,formula_length]
  exact Nat.add_le_add_right (Nat.add_le_add_left (proof_length p ht h) _) 3

-- Width invariant for the actual compiled resolution output.
theorem copy_narrow (v i : Nat) (f : Formula) (h : WidthTwo f) :
    NarrowSteps (copySteps v i f) := by
  induction f generalizing i with
  | nil => intro s hs; cases hs
  | cons c cs ih =>
    intro s hs
    cases hs with
    | head => exact h c (List.Mem.head _)
    | tail _ hm => exact ih (i+1) (fun d hd => h d (List.Mem.tail _ hd)) s hm

theorem compile_narrow (v : Nat) (f : Formula) (ss : List Step)
    (hf : WidthTwo f) (hs : NarrowSteps ss) : NarrowBatches (compile v f ss) := by
  induction ss generalizing f with
  | nil => intro b hb; cases hb
  | cons s ss ih =>
    have ht := hs s (List.Mem.head _)
    intro b hb
    cases hb with
    | head =>
      intro t hm
      change t∈s::copySteps v 0 f at hm
      cases hm with
      | head => exact ht
      | tail _ hmem => exact copy_narrow v 0 f hf t hmem
    | tail _ hm =>
      have hw : WidthTwo (s.tail::f) := by
        intro c hc
        cases hc with
        | head => exact ht
        | tail _ hmem => exact hf c hmem
      exact ih _ hw (fun t ht' => hs t (List.Mem.tail _ ht')) b hm

private theorem append_narrow (as bs : List Step) (ha : NarrowSteps as) (hb : NarrowSteps bs) :
    NarrowSteps (as++bs) := by
  induction as with
  | nil => exact hb
  | cons a as ih =>
    intro s hs
    cases hs with
    | head => exact ha a (List.Mem.head _)
    | tail _ hm => exact ih (fun t ht => ha t (List.Mem.tail _ ht)) s hm

theorem advance_narrow (s a b : Literal) (i : Nat) : (advanceStep s a b i).tail.length≤2 := by
  unfold advanceStep
  cases a.2 <;> exact Nat.le_refl _

theorem pathTail_narrow (s a : Literal) (g : Formula) (bs : List Literal)
    (ss : List Step) (out : Formula) (h : pathTail s a g bs=some (ss,out)) :
    NarrowSteps ss := by
  induction bs generalizing a g ss out with
  | nil =>
    change some ([],g)=some (ss,out) at h
    cases h
    intro t ht
    cases ht
  | cons b bs ih =>
    unfold pathTail at h
    cases hi : ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite a,b]) g with
    | none => rw [hi] at h; cases h
    | some i =>
      rw [hi] at h
      let t := advanceStep s a b i
      change (do
        let (ts,h') ← pathTail s b (t.tail::g) bs
        some (t::ts,h'))=some (ss,out) at h
      cases he : pathTail s b (t.tail::g) bs with
      | none => rw [he] at h; cases h
      | some pair =>
        cases pair with
        | mk ts g' =>
          rw [he] at h
          change some (t::ts,g')=some (ss,out) at h
          cases h
          intro d hd
          cases hd with
          | head => exact advance_narrow s a b i
          | tail _ hm => exact ih b (t.tail::g) ts out he d hm

theorem pathStart_narrow (g : Formula) (s : Literal) (bs : List Literal)
    (ss : List Step) (out : Formula) (h : pathStart g s bs=some (ss,out)) :
    NarrowSteps ss := by
  cases bs with
  | nil => cases h
  | cons b bs =>
    change (do
      let i ← ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite s,b]) g
      let t := firstStep s b i
      let (ts,h') ← pathTail s b (t.tail::g) bs
      some (t::ts,h'))=some (ss,out) at h
    cases hi : ProctorExecutableDiscovery.findRow
        (ProctorExecutableDiscovery.contained [ProctorCapacityDeficiency.opposite s,b]) g with
    | none => rw [hi] at h; cases h
    | some i =>
      rw [hi] at h
      let t := firstStep s b i
      change (do
        let (ts,h') ← pathTail s b (t.tail::g) bs
        some (t::ts,h'))=some (ss,out) at h
      cases he : pathTail s b (t.tail::g) bs with
      | none => rw [he] at h; cases h
      | some pair =>
        cases pair with
        | mk ts g' =>
          rw [he] at h
          change some (t::ts,g')=some (ss,out) at h
          cases h
          intro d hd
          cases hd with
          | head => exact Nat.le_refl _
          | tail _ hm => exact pathTail_narrow s b (t.tail::g) bs ts out he d hm

theorem pair_narrow (f : Formula) (v : Nat) (pos neg : List Literal) (p : Proof)
    (hf : WidthTwo f) (h : compilePair f v pos neg=some p) :
    p.terminal=.empty ∧ NarrowBatches p.batches := by
  unfold compilePair at h
  cases ha : pathStart f (v,true) pos with
  | none => rw [ha] at h; cases h
  | some pair =>
    cases pair with
    | mk a g =>
      rw [ha] at h
      change (do
        let (b,_) ← pathStart g (v,false) neg
        some ⟨compile v f (a++(b++[closeStep v b.length])),false,.empty⟩)=some p at h
      cases hb : pathStart g (v,false) neg with
      | none => rw [hb] at h; cases h
      | some pair =>
        cases pair with
        | mk b out =>
          rw [hb] at h
          change some (⟨compile v f (a++(b++[closeStep v b.length])),false,.empty⟩ : Proof)=some p at h
          cases h
          have hc : NarrowSteps [closeStep v b.length] := by
            intro s hs
            cases hs with
            | head => exact Nat.zero_le _
            | tail _ hm => cases hm
          exact ⟨rfl,compile_narrow v f _ hf
            (append_narrow a _ (pathStart_narrow f (v,true) pos a g ha)
              (append_narrow b _ (pathStart_narrow g (v,false) neg b out hb) hc))⟩

theorem tryVar_narrow (f : Formula) (v : Nat) (p : Proof)
    (hf : WidthTwo f) (h : tryVar f (arcs f) v=some p) :
    p.terminal=.empty ∧ NarrowBatches p.batches := by
  unfold tryVar at h
  cases hp : reach (arcs f) (v,true) (v,false) with
  | none => rw [hp] at h; cases h
  | some pos =>
    rw [hp] at h
    change (do
      let neg ← reach (arcs f) (v,false) (v,true)
      compilePair f v pos neg)=some p at h
    cases hn : reach (arcs f) (v,false) (v,true) with
    | none => rw [hn] at h; cases h
    | some neg =>
      rw [hn] at h
      exact pair_narrow f v pos neg p hf h

theorem solve_narrow (n : Nat) (f : Formula) (p : Proof)
    (h : solve n f=.unsat p) : p.terminal=.empty ∧ NarrowBatches p.batches := by
  have hs := ProctorTotalTwoCNF.solve_spec n f
  rw [h] at hs
  have hw := hs.2.1
  unfold solve at h
  cases hv : ProctorUnifiedReplay.validFormula n f with
  | false => rw [hv] at h; cases h
  | true =>
    rw [hv] at h
    change (if ProctorTotalTwoCNF.supported f then _ else ProctorTotalTwoCNF.Result.unsupported)=_ at h
    rw [(ProctorTotalTwoCNF.supported_iff f).2 hw] at h
    change (if ProctorExecutableReplay.hasEmpty f then _ else _)=_ at h
    cases he : ProctorExecutableReplay.hasEmpty f with
    | true =>
      rw [he] at h
      change ProctorTotalTwoCNF.Result.unsat ProctorTotalTwoCNF.emptyProof=.unsat p at h
      cases h
      exact ⟨rfl,fun _ hb => nomatch hb⟩
    | false =>
      rw [he] at h
      change (match ProctorTwoCNFModel.findConflict f (variables f) with
        | none => ProctorTotalTwoCNF.Result.sat (ProctorTwoCNFModel.model f)
        | some v => match checked n f (tryVar f (arcs f) v) with
          | none => ProctorTotalTwoCNF.Result.internalError
          | some q => ProctorTotalTwoCNF.Result.unsat q)=_ at h
      cases hc : ProctorTwoCNFModel.findConflict f (variables f) with
      | none => rw [hc] at h; cases h
      | some v =>
        rw [hc] at h
        change (match checked n f (tryVar f (arcs f) v) with
          | none => ProctorTotalTwoCNF.Result.internalError
          | some q => ProctorTotalTwoCNF.Result.unsat q)=_ at h
        cases hp : checked n f (tryVar f (arcs f) v) with
        | none => rw [hp] at h; cases h
        | some q =>
          rw [hp] at h
          cases h
          exact tryVar_narrow f v p hw (ProctorTotalTwoCNF.checked_eq n f _ p hp)

theorem solve_unsat_tokens (n : Nat) (f : Formula) (p : Proof)
    (h : solve n f=.unsat p) :
    (tokens (.unsat ⟨n,f,p⟩)).length≤
      2*occurrences f+f.length+1+
        (8*((f.length+(2*occurrences f+1))*(2*occurrences f+1))+(2*occurrences f+1)+3)+3 := by
  have hn := solve_narrow n f p h
  have hs := solve_size n f p h
  exact Nat.le_trans (unsat_tokens_length n f p hn.left hn.right)
    (Nat.add_le_add_right (Nat.add_le_add_left
      (Nat.add_le_add_right (Nat.add_le_add (Nat.mul_le_mul_left 8 hs.right) hs.left) 3) _) 3)

end ProctorWireTokenBounds

#print axioms ProctorWireTokenBounds.variables_length
#print axioms ProctorWireTokenBounds.literal_length
#print axioms ProctorWireTokenBounds.clause_length
#print axioms ProctorWireTokenBounds.formula_length
#print axioms ProctorWireTokenBounds.expected_length
#print axioms ProctorWireTokenBounds.sat_tokens_length
#print axioms ProctorWireTokenBounds.step_length
#print axioms ProctorWireTokenBounds.narrow_step_length
#print axioms ProctorWireTokenBounds.batch_length
#print axioms ProctorWireTokenBounds.batches_length
#print axioms ProctorWireTokenBounds.proof_length
#print axioms ProctorWireTokenBounds.unsat_tokens_length
#print axioms ProctorWireTokenBounds.copy_narrow
#print axioms ProctorWireTokenBounds.compile_narrow
#print axioms ProctorWireTokenBounds.advance_narrow
#print axioms ProctorWireTokenBounds.pathTail_narrow
#print axioms ProctorWireTokenBounds.pathStart_narrow
#print axioms ProctorWireTokenBounds.pair_narrow
#print axioms ProctorWireTokenBounds.tryVar_narrow
#print axioms ProctorWireTokenBounds.solve_narrow
#print axioms ProctorWireTokenBounds.solve_unsat_tokens
