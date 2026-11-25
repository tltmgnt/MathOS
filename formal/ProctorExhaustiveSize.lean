/-! Exact output-size obstruction for the particular exhaustive
generator. Not a lower bound on all certificates or SAT algorithms. -/
namespace ProctorExhaustiveSize
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch tails)
open ProctorUnifiedReplay (Proof validFormula)
open ProctorCapacityReplay (test)
open ProctorResolutionBridge (Unsat compile copySteps extend)
open ProctorOrdinaryCompleteness (variables rowVars)
open ProctorExecutableDiscovery (build findRow contained generate)

def nodes : Nat → Nat
  | 0 => 1
  | k+1 => nodes k + (nodes k + 1)

private theorem length_append_local {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++ys).length+1=(xs.length+1)+ys.length
    rw [ih]
    rw [Nat.add_assoc,Nat.add_comm ys.length 1,← Nat.add_assoc]

theorem build_length (q : Nat) (vs : List Nat) (g : Formula) (path : Clause)
    (ss : List Step) (out : Formula) (h : build q vs g path=some (ss,out)) :
    ss.length=nodes vs.length := by
  induction vs generalizing g path ss out with
  | nil =>
    unfold build at h
    cases e : findRow (contained path) g with
    | none => rw [e] at h; cases h
    | some i =>
      rw [e] at h
      change some ([Step.mk i i q path],path::g)=some (ss,out) at h
      cases h
      rfl
  | cons v vs ih =>
    unfold build at h
    cases ea : build q vs g ((v,true)::path) with
    | none => rw [ea] at h; cases h
    | some a =>
      cases a with
      | mk as g1 =>
        rw [ea] at h
        change (do
          let (bs,g2) ← build q vs g1 ((v,false)::path)
          let i ← findRow (fun c => test (c=(v,true)::path)) g2
          let j ← findRow (fun c => test (c=(v,false)::path)) g2
          some (as++(bs++[Step.mk i j v path]),path::g2))=some (ss,out) at h
        cases eb : build q vs g1 ((v,false)::path) with
        | none => rw [eb] at h; cases h
        | some b =>
          cases b with
          | mk bs g2 =>
            rw [eb] at h
            change (do
              let i ← findRow (fun c => test (c=(v,true)::path)) g2
              let j ← findRow (fun c => test (c=(v,false)::path)) g2
              some (as++(bs++[Step.mk i j v path]),path::g2))=some (ss,out) at h
            cases ei : findRow (fun c => test (c=(v,true)::path)) g2 with
            | none => rw [ei] at h; cases h
            | some i =>
              rw [ei] at h
              change (do
                let j ← findRow (fun c => test (c=(v,false)::path)) g2
                some (as++(bs++[Step.mk i j v path]),path::g2))=some (ss,out) at h
              cases ej : findRow (fun c => test (c=(v,false)::path)) g2 with
              | none => rw [ej] at h; cases h
              | some j =>
                rw [ej] at h
                change some (as++(bs++[Step.mk i j v path]),path::g2)=some (ss,out) at h
                cases h
                rw [length_append_local,length_append_local,ih g ((v,true)::path) as g1 ea,
                  ih g1 ((v,false)::path) bs g2 eb] <;> rfl

theorem nodes_lower (k : Nat) : 2^k≤nodes k := by
  induction k with
  | zero => exact Nat.le_refl 1
  | succ k ih =>
    change 2^k*2≤nodes k+(nodes k+1)
    rw [Nat.mul_succ,Nat.mul_one]
    exact Nat.add_le_add ih (Nat.le_trans ih (Nat.le_succ _))

theorem compile_batches (q : Nat) (f : Formula) (ss : List Step) :
    (compile q f ss).length=ss.length := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change (compile q (s.tail::f) ss).length+1=ss.length+1
    exact congrArg Nat.succ (ih _)

def stepCount : List Batch → Nat
  | [] => 0
  | b::bs => b.length+stepCount bs

def copies : Nat → Nat → Nat
  | 0,_ => 0
  | k+1,m => (m+1)+copies k (m+1)

theorem copy_length (q i : Nat) (f : Formula) :
    (copySteps q i f).length=f.length := by
  induction f generalizing i with
  | nil => rfl
  | cons c cs ih =>
    change (copySteps q (i+1) cs).length+1=cs.length+1
    exact congrArg Nat.succ (ih _)

theorem compiled_steps (q : Nat) (f : Formula) (ss : List Step) :
    stepCount (compile q f ss)=copies ss.length f.length := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change ((copySteps q 0 f).length+1)+stepCount (compile q (s.tail::f) ss)=
      (f.length+1)+copies ss.length (f.length+1)
    rw [copy_length,ih] <;> rfl

theorem generated_batches (n : Nat) (f : Formula) (p : Proof)
    (hn : n≠0) (h : generate n f=some p) :
    p.batches.length=nodes (variables f).length := by
  unfold generate at h
  rw [if_neg hn] at h
  cases e : build 1 (variables f) f [] with
  | none => rw [e] at h; cases h
  | some pair =>
    cases pair with
    | mk ss g =>
      rw [e] at h
      change some (Proof.mk (compile 1 f ss) false .empty)=some p at h
      cases h
      exact (compile_batches 1 f ss).trans (build_length 1 (variables f) f [] ss g e)

theorem generated_lower (n : Nat) (f : Formula) (p : Proof)
    (hn : n≠0) (h : generate n f=some p) :
    2^(variables f).length≤p.batches.length := by
  rw [generated_batches n f p hn h]
  exact nodes_lower _

-- A linear-length family with a constant-size refutation. The
-- exhaustive generator nevertheless branches on every occurrence.
def padded : Nat → Formula
  | 0 => [[(1,true)],[(1,false)]]
  | k+1 => [(2,true)]::padded k

theorem padded_unsat (k : Nat) : Unsat (padded k) := by
  induction k with
  | zero =>
    intro h
    obtain ⟨x,hx⟩ := h
    obtain ⟨a,ha,ht⟩ := hx [(1,true)] (List.Mem.head _)
    obtain ⟨b,hb,hf⟩ := hx [(1,false)] (List.Mem.tail _ (List.Mem.head _))
    cases ha with
    | tail _ hm => cases hm
    | head =>
      cases hb with
      | tail _ hm => cases hm
      | head => exact Bool.noConfusion (ht.symm.trans hf)
  | succ k ih =>
    intro h
    obtain ⟨x,hx⟩ := h
    exact ih ⟨x,fun c hc => hx c (List.Mem.tail _ hc)⟩

theorem padded_valid (k : Nat) : validFormula 2 (padded k)=true := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change (true && validFormula 2 (padded k))=true
    rw [ih] <;> rfl

theorem padded_vars (k : Nat) : (variables (padded k)).length=k+2 := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change (variables (padded k)).length+1=(k+1)+2
    rw [ih]

theorem padded_generator_lower (k : Nat) :
    ∃ p, generate 2 (padded k)=some p ∧
      ProctorUnifiedReplay.boundCheck 2 (padded k) ⟨2,padded k,p⟩=true ∧
      2^(k+2)≤p.batches.length := by
  obtain ⟨p,hp,hc⟩ := ProctorExecutableDiscovery.generate_complete 2 (padded k)
    (padded_valid k) (padded_unsat k)
  have h := generated_lower 2 (padded k) p (by decide) hp
  rw [padded_vars] at h
  exact ⟨p,hp,hc,h⟩

end ProctorExhaustiveSize

#print axioms ProctorExhaustiveSize.build_length
#print axioms ProctorExhaustiveSize.nodes_lower
#print axioms ProctorExhaustiveSize.compile_batches
#print axioms ProctorExhaustiveSize.copy_length
#print axioms ProctorExhaustiveSize.compiled_steps
#print axioms ProctorExhaustiveSize.generated_batches
#print axioms ProctorExhaustiveSize.generated_lower
#print axioms ProctorExhaustiveSize.padded_unsat
#print axioms ProctorExhaustiveSize.padded_valid
#print axioms ProctorExhaustiveSize.padded_vars
#print axioms ProctorExhaustiveSize.padded_generator_lower
