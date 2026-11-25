/-! F035/F040: a checked two-batch binary-square refutation.
This independent candidate uses the verified exhaustive baseline, not the
unverified deduplication sibling. No polynomial worst-case claim. -/
namespace ProctorBinarySquareDiscovery
open ProctorHallDeficiency
open ProctorExecutableReplay (Step lookup stepCheck)
open ProctorCapacityReplay (test)
open ProctorUnifiedReplay (Proof validId validFormula validProof boundCheck check)
open ProctorResolutionBridge (Unsat step_complete)
open ProctorEnvelopeCompleteness (envelope_of_proof)
open ProctorExecutableDiscovery (findRow locate_exact)

def squareProof (v w i j k l : Nat) : Proof :=
  ⟨[[⟨i,j,v,[(w,true)]⟩,⟨k,l,v,[(w,false)]⟩],
    [⟨0,1,w,[]⟩]],false,.empty⟩

theorem square_shape (v w i j k l : Nat) :
    (squareProof v w i j k l).batches.map List.length=[2,1] := rfl

private theorem two_shape (p t : Literal) :
    ∀ l∈[p,t], l=p ∨ l∈[t] := by
  intro l hl
  cases hl with
  | head => exact Or.inl rfl
  | tail _ hm => exact Or.inr hm

private theorem unit_shape (p : Literal) :
    ∀ l∈[p], l=p ∨ l∈([] : Clause) := by
  intro l hl
  cases hl with
  | head => exact Or.inl rfl
  | tail _ hm => cases hm

theorem square_certificate (n v w i j k l : Nat) (f : Formula)
    (hf : validFormula n f=true)
    (hv : validId n v=true) (hw : validId n w=true)
    (hi : lookup f i=some [(v,true),(w,true)])
    (hj : lookup f j=some [(v,false),(w,true)])
    (hk : lookup f k=some [(v,true),(w,false)])
    (hl : lookup f l=some [(v,false),(w,false)]) :
    boundCheck n f ⟨n,f,squareProof v w i j k l⟩=true := by
  let a : Step := ⟨i,j,v,[(w,true)]⟩
  let b : Step := ⟨k,l,v,[(w,false)]⟩
  let c : Step := ⟨0,1,w,[]⟩
  have ha : stepCheck f a=true :=
    step_complete f a _ _ hi hj (two_shape _ _) (two_shape _ _)
  have hb : stepCheck f b=true :=
    step_complete f b _ _ hk hl (two_shape _ _) (two_shape _ _)
  have hc : stepCheck [[(w,true)],[(w,false)]] c=true :=
    step_complete _ c _ _ rfl rfl (unit_shape _) (unit_shape _)
  let p : Proof := squareProof v w i j k l
  have hp : validProof n p=true := by
    change ((((validId n v && (validId n w && true)) &&
      ((validId n v && (validId n w && true)) && true)) &&
      (((validId n w && true) && true) && true)) && true)=true
    rw [hv,hw] <;> rfl
  have hcheck : check f p=true := by
    change (((stepCheck f a && (stepCheck f b && true)) &&
      ((stepCheck [[(w,true)],[(w,false)]] c && true) && true)) && true)=true
    rw [ha,hb,hc] <;> rfl
  exact envelope_of_proof n f p hf hp hcheck

def atPair (f : Formula) (v w : Nat) : Option Proof := do
  let i ← findRow (fun c => test (c=[(v,true),(w,true)])) f
  let j ← findRow (fun c => test (c=[(v,false),(w,true)])) f
  let k ← findRow (fun c => test (c=[(v,true),(w,false)])) f
  let l ← findRow (fun c => test (c=[(v,false),(w,false)])) f
  some (squareProof v w i j k l)

theorem atPair_complete (n v w : Nat) (f : Formula)
    (hf : validFormula n f=true)
    (hv : validId n v=true) (hw : validId n w=true)
    (a : [(v,true),(w,true)]∈f) (b : [(v,false),(w,true)]∈f)
    (c : [(v,true),(w,false)]∈f) (d : [(v,false),(w,false)]∈f) :
    ∃ p, atPair f v w=some p ∧ boundCheck n f ⟨n,f,p⟩=true ∧
      p.batches.map List.length=[2,1] := by
  obtain ⟨i,hi,li⟩ := locate_exact f _ a
  obtain ⟨j,hj,lj⟩ := locate_exact f _ b
  obtain ⟨k,hk,lk⟩ := locate_exact f _ c
  obtain ⟨l,hl,ll⟩ := locate_exact f _ d
  refine ⟨squareProof v w i j k l,?_,square_certificate n v w i j k l f hf hv hw li lj lk ll,rfl⟩
  unfold atPair
  rw [hi,hj,hk,hl] <;> rfl

-- The exact ordered pattern is intentional: no clause canonicalization
-- or arbitrary 2-SAT completeness claim is made.
def scan (f : Formula) : Formula → Option Proof
  | [] => none
  | c::cs =>
    match c with
    | [(v,true),(w,true)] =>
      match atPair f v w with
      | some p => some p
      | none => scan f cs
    | _ => scan f cs

def checked (n : Nat) (f : Formula) : Option Proof → Option Proof
  | none => none
  | some p => if boundCheck n f ⟨n,f,p⟩ then some p else none

theorem checked_sound (n : Nat) (f : Formula) (o : Option Proof) (p : Proof)
    (h : checked n f o=some p) : boundCheck n f ⟨n,f,p⟩=true := by
  cases o with
  | none => cases h
  | some q =>
    change (if boundCheck n f ⟨n,f,q⟩ then some q else none)=some p at h
    by_cases e : boundCheck n f ⟨n,f,q⟩=true
    · rw [if_pos e] at h
      cases h
      exact e
    · rw [if_neg e] at h
      cases h

theorem checked_complete (n : Nat) (f : Formula) (o : Option Proof) (p : Proof)
    (h : o=some p) (hc : boundCheck n f ⟨n,f,p⟩=true) :
    checked n f o=some p := by
  rw [h]
  change (if boundCheck n f ⟨n,f,p⟩ then some p else none)=some p
  rw [if_pos hc]

-- Return the checked proof itself, rather than discarding it as a Bool.
def discover (n : Nat) (f : Formula) : Option Proof :=
  match checked n f (scan f f) with
  | some p => some p
  | none => checked n f (ProctorExecutableDiscovery.generate n f)

theorem discover_accepts (n : Nat) (f : Formula) (p : Proof)
    (h : discover n f=some p) : boundCheck n f ⟨n,f,p⟩=true := by
  unfold discover at h
  cases e : checked n f (scan f f) with
  | none =>
    rw [e] at h
    exact checked_sound n f _ p h
  | some q =>
    rw [e] at h
    change some q=some p at h
    cases h
    exact checked_sound n f _ _ e

theorem discover_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ p, discover n f=some p := by
  unfold discover
  cases e : checked n f (scan f f) with
  | some p => exact ⟨p,rfl⟩
  | none =>
    obtain ⟨p,hp,hc⟩ := ProctorExecutableDiscovery.generate_complete n f hf hu
    exact ⟨p,checked_complete n f _ p hp hc⟩

theorem discover_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    (∃ p, discover n f=some p) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨p,hp⟩ := h
    exact ProctorUnifiedReplay.bound_sound n f _ (discover_accepts n f p hp)
  · exact discover_complete n f hf

end ProctorBinarySquareDiscovery

#print axioms ProctorBinarySquareDiscovery.square_shape
#print axioms ProctorBinarySquareDiscovery.square_certificate
#print axioms ProctorBinarySquareDiscovery.atPair_complete
#print axioms ProctorBinarySquareDiscovery.checked_sound
#print axioms ProctorBinarySquareDiscovery.checked_complete
#print axioms ProctorBinarySquareDiscovery.discover_accepts
#print axioms ProctorBinarySquareDiscovery.discover_complete
#print axioms ProctorBinarySquareDiscovery.discover_iff
