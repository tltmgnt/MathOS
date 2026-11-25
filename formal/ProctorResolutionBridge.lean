/-! F035 candidate: backward proof bridge. The typed checker is
sound; generator completeness is an explicit OPEN hypothesis, not
a proved result. Local rule completeness and weakening permit
ordinary resolution steps to be carried into the batch language. -/
namespace ProctorResolutionBridge
open ProctorHallDeficiency
open ProctorExecutableReplay (contains shapeCheck lookup Step Batch stepCheck batchCheck tails chainCheck frontier)
open ProctorUnifiedReplay (Proof check)

def Unsat (f : Formula) : Prop := ¬ ∃ x : Assignment, FormulaSat f x

theorem contains_complete (l : Literal) (c : Clause) (h : l∈c) :
    contains l c=true := by
  induction c with
  | nil => cases h
  | cons a as ih =>
    change (if l=a then true else contains l as)=true
    by_cases e : l=a
    · rw [if_pos e]
    · rw [if_neg e]
      cases h with
      | head => exact (e rfl).elim
      | tail _ hm => exact ih hm

theorem shape_complete (p : Literal) (t row : Clause)
    (h : ∀ l∈row, l=p ∨ l∈t) : shapeCheck p t row=true := by
  induction row with
  | nil => rfl
  | cons a as ih =>
    have hr := ih (fun l hm => h l (List.Mem.tail _ hm))
    change (if a=p then shapeCheck p t as
      else if contains a t then shapeCheck p t as else false)=true
    by_cases e : a=p
    · rw [if_pos e]; exact hr
    · rw [if_neg e]
      cases h a (List.Mem.head _) with
      | inl eq => exact (e eq).elim
      | inr hm => rw [contains_complete a t hm]; exact hr

theorem step_complete (f : Formula) (s : Step) (a b : Clause)
    (ha : lookup f s.left=some a) (hb : lookup f s.right=some b)
    (hp : ∀ l∈a, l=(s.pivot,true) ∨ l∈s.tail)
    (hn : ∀ l∈b, l=(s.pivot,false) ∨ l∈s.tail) :
    stepCheck f s=true := by
  unfold stepCheck
  rw [ha,hb]
  change (shapeCheck (s.pivot,true) s.tail a &&
    shapeCheck (s.pivot,false) s.tail b)=true
  rw [shape_complete _ _ _ hp,shape_complete _ _ _ hn] <;> rfl

theorem copy_step (f : Formula) (i v : Nat) (row : Clause)
    (h : lookup f i=some row) :
    stepCheck f ⟨i,i,v,row⟩=true :=
  step_complete f ⟨i,i,v,row⟩ row row h h
    (fun _ hl => Or.inr hl) (fun _ hl => Or.inr hl)

def copySteps (v : Nat) : Nat → Formula → Batch
  | _,[] => []
  | i,c::cs => ⟨i,i,v,c⟩::copySteps v (i+1) cs

theorem copy_tails (v i : Nat) (f : Formula) :
    tails (copySteps v i f)=f := by
  induction f generalizing i with
  | nil => rfl
  | cons c cs ih =>
    change c::tails (copySteps v (i+1) cs)=c::cs
    rw [ih]

theorem copy_checked (v i : Nat) (f xs : Formula)
    (h : ∀ j c, lookup xs j=some c → lookup f (i+j)=some c) :
    batchCheck f (copySteps v i xs)=true := by
  induction xs generalizing i with
  | nil => rfl
  | cons c cs ih =>
    have hc : lookup f i=some c := h 0 c rfl
    have ht : ∀ j d, lookup cs j=some d → lookup f ((i+1)+j)=some d := by
      intro j d hd
      have e : (i+1)+j=i+(j+1) := by
        rw [Nat.add_assoc, Nat.add_comm 1 j]
      rw [e]
      exact h (j+1) d hd
    change (stepCheck f ⟨i,i,v,c⟩ && batchCheck f (copySteps v (i+1) cs))=true
    rw [copy_step f i v c hc,ih (i+1) ht] <;> rfl

theorem copy_batch (v : Nat) (f : Formula) :
    batchCheck f (copySteps v 0 f)=true :=
  copy_checked v 0 f f (fun j c h => by rw [Nat.zero_add]; exact h)

-- Prepend one checked derived row while retaining the entire old formula.
def extend (v : Nat) (f : Formula) (s : Step) : Batch :=
  s::copySteps v 0 f

theorem extend_checked (v : Nat) (f : Formula) (s : Step)
    (h : stepCheck f s=true) : batchCheck f (extend v f s)=true := by
  change (stepCheck f s && batchCheck f (copySteps v 0 f))=true
  rw [h,copy_batch] <;> rfl

theorem extend_tails (v : Nat) (f : Formula) (s : Step) :
    tails (extend v f s)=s.tail::f := by
  change s.tail::tails (copySteps v 0 f)=s.tail::f
  rw [copy_tails]

-- A sequential trace of checked ordinary/weakening resolution steps.
-- Indices refer to the current frontier with newly derived rows prepended.
def sequentialCheck : Formula → List Step → Bool
  | _,[] => true
  | f,s::ss => stepCheck f s && sequentialCheck (s.tail::f) ss

def sequentialFrontier : Formula → List Step → Formula
  | f,[] => f
  | f,s::ss => sequentialFrontier (s.tail::f) ss

def compile (v : Nat) : Formula → List Step → List Batch
  | _,[] => []
  | f,s::ss => extend v f s :: compile v (s.tail::f) ss

theorem compile_checked (v : Nat) (f : Formula) (ss : List Step) :
    chainCheck f (compile v f ss)=sequentialCheck f ss := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change (batchCheck f (extend v f s) &&
      chainCheck (tails (extend v f s)) (compile v (s.tail::f) ss))=
      (stepCheck f s && sequentialCheck (s.tail::f) ss)
    rw [extend_tails,ih]
    change ((stepCheck f s && batchCheck f (copySteps v 0 f)) &&
      sequentialCheck (s.tail::f) ss)=_
    rw [copy_batch]
    cases stepCheck f s <;> rfl

theorem compile_frontier (v : Nat) (f : Formula) (ss : List Step) :
    frontier f (compile v f ss)=sequentialFrontier f ss := by
  induction ss generalizing f with
  | nil => rfl
  | cons s ss ih =>
    change frontier (tails (extend v f s)) (compile v (s.tail::f) ss)=_
    rw [extend_tails]
    exact ih (s.tail::f)

theorem compile_refutation (v : Nat) (f : Formula) (ss : List Step)
    (hc : sequentialCheck f ss=true)
    (he : ProctorExecutableReplay.hasEmpty (sequentialFrontier f ss)=true) :
    check f ⟨compile v f ss,false,.empty⟩=true := by
  change (chainCheck f (compile v f ss) &&
    ProctorExecutableReplay.hasEmpty (frontier f (compile v f ss)))=true
  rw [compile_checked,compile_frontier,hc,he] <;> rfl

def decideUnsat (g : Formula → Option Proof) (f : Formula) : Bool :=
  match g f with | none => false | some p => check f p

def DiscoveryComplete (g : Formula → Option Proof) : Prop :=
  ∀ f, Unsat f → ∃ p, g f=some p ∧ check f p=true

theorem decision_sound (g : Formula → Option Proof) (f : Formula)
    (h : decideUnsat g f=true) : Unsat f := by
  unfold decideUnsat at h
  cases hg : g f with
  | none => rw [hg] at h; cases h
  | some p => rw [hg] at h; exact ProctorUnifiedReplay.check_sound f p h

theorem decision_complete (g : Formula → Option Proof) (hg : DiscoveryComplete g)
    (f : Formula) (h : Unsat f) : decideUnsat g f=true := by
  obtain ⟨p,hp,hc⟩ := hg f h
  unfold decideUnsat
  rw [hp]
  exact hc

theorem decision_iff (g : Formula → Option Proof) (hg : DiscoveryComplete g)
    (f : Formula) : decideUnsat g f=true ↔ Unsat f :=
  ⟨decision_sound g f,decision_complete g hg f⟩

theorem sat_iff (g : Formula → Option Proof) (hg : DiscoveryComplete g)
    (f : Formula) (alternative : (∃ x : Assignment, FormulaSat f x) ∨ Unsat f) :
    decideUnsat g f=false ↔ ∃ x : Assignment, FormulaSat f x := by
  constructor
  · intro h
    cases alternative with
    | inl m => exact m
    | inr u =>
      have e := decision_complete g hg f u
      rw [h] at e
      exact Bool.noConfusion e
  · intro m
    cases e : decideUnsat g f with
    | false => rfl
    | true => exact (decision_sound g f e m).elim

end ProctorResolutionBridge

#print axioms ProctorResolutionBridge.contains_complete
#print axioms ProctorResolutionBridge.shape_complete
#print axioms ProctorResolutionBridge.step_complete
#print axioms ProctorResolutionBridge.copy_step
#print axioms ProctorResolutionBridge.copy_tails
#print axioms ProctorResolutionBridge.copy_checked
#print axioms ProctorResolutionBridge.copy_batch
#print axioms ProctorResolutionBridge.extend_checked
#print axioms ProctorResolutionBridge.extend_tails
#print axioms ProctorResolutionBridge.compile_checked
#print axioms ProctorResolutionBridge.compile_frontier
#print axioms ProctorResolutionBridge.compile_refutation
#print axioms ProctorResolutionBridge.decision_sound
#print axioms ProctorResolutionBridge.decision_complete
#print axioms ProctorResolutionBridge.decision_iff
#print axioms ProctorResolutionBridge.sat_iff
