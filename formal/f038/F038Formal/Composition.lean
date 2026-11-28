import F038Formal.Physical

/-! FV-07: fail-closed composition of the reference certificate interfaces.
    Residual equivalence is checked by finite enumeration; this is not
    a polynomial-time residual checker or a proof of the JS compiler. -/
namespace MathOS.F038.Composition
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.Bridge

def tableCheck {n : Nat} (fs : List (RowFactor n)) (x : Assignment n) : Bool :=
  allCheck (fun f => decide (f.scope.map x ∈ f.rows)) fs

theorem tableCheck_exact {n : Nat} (fs : List (RowFactor n)) (x : Assignment n) :
    tableCheck fs x = true ↔ TableModels fs x := by
  constructor
  · intro h f hf
    exact of_decide_eq_true (allCheck_sound _ _ h f hf)
  · intro h
    exact allCheck_complete _ _ (fun f hf => decide_eq_true (h f hf))

-- Explicit finite enumeration is deliberately exponential. It is a
-- correctness reference for materialized residuals, not a fast algorithm.
def assignments : (n : Nat) → List (Assignment n)
  | 0 => [fun i => Fin.elim0 i]
  | n+1 => (assignments n).flatMap (fun z => [Fin.cases false z, Fin.cases true z])

theorem assignments_complete (n : Nat) (x : Assignment n) : x ∈ assignments n := by
  induction n with
  | zero =>
    have h : x = (fun i : Fin 0 => Fin.elim0 i) := by
      funext i
      exact Fin.elim0 i
    rw [h]
    simp [assignments]
  | succ n ih =>
    let tail : Assignment n := fun i => x i.succ
    have ht : tail ∈ assignments n := ih tail
    have he : Fin.cases (x 0) tail = x := by
      funext i
      refine Fin.cases ?_ ?_ i
      · rfl
      · intro j
        rfl
    rw [← he]
    change Fin.cases (x 0) tail ∈
      (assignments n).flatMap (fun z => [Fin.cases false z, Fin.cases true z])
    apply List.mem_flatMap.mpr
    refine ⟨tail, ht, ?_⟩
    cases (x 0) <;> simp

def materializedCheck {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m)
    (residual : List (RowFactor m)) : Bool :=
  allCheck (fun z => decide (tableCheck residual z = pullbackCheck fs a z))
    (assignments m)

theorem materializedCheck_exact {n m : Nat} (fs : List (RowFactor n))
    (a : AffineMap n m) (residual : List (RowFactor m))
    (h : materializedCheck fs a residual = true) (z : Assignment m) :
    TableModels residual z ↔ TableModels fs (expand a z) := by
  have he : tableCheck residual z = pullbackCheck fs a z :=
    of_decide_eq_true (allCheck_sound _ _ h z (assignments_complete m z))
  rw [← tableCheck_exact residual z, he]
  exact pullback_exact fs a z

theorem residual_models_of_source {n m : Nat} (fs out : List (RowFactor n))
    (steps : List Nat) (hr : relationalReplay fs steps = some out)
    (a : AffineMap n m) (ha : affineMapCheck out a = true)
    (residual : List (RowFactor m)) (hm : materializedCheck out a residual = true)
    (x : Assignment n) (hx : TableModels fs x) :
    TableModels residual (project a x) := by
  have hx' := (relationalReplay_exact fs out steps hr x).mpr hx
  apply (materializedCheck_exact out a residual hm (project a x)).mpr
  rw [affineMap_reconstruct out a ha x hx']
  exact hx'

theorem residual_witness_sound {n m : Nat} (fs out : List (RowFactor n))
    (steps : List Nat) (hr : relationalReplay fs steps = some out)
    (a : AffineMap n m) (residual : List (RowFactor m))
    (hm : materializedCheck out a residual = true)
    (z : Assignment m) (hz : TableModels residual z) :
    TableModels fs (expand a z) :=
  (relationalReplay_exact fs out steps hr _).mp
    ((materializedCheck_exact out a residual hm z).mp hz)

inductive Evidence (n m : Nat) where
  | unknown
  | directSat (x : Assignment n)
  | reducedSat (z : Assignment m)
  | directHall (p : Packet n)
  | affineUnsat (p : EqProof n)
  | reducedHall (p : Packet m)

inductive Verdict (n : Nat) where
  | unknown
  | sat (x : Assignment n)
  | unsat

def Sound {n : Nat} (fs : List (RowFactor n)) : Verdict n → Prop
  | .unknown => True
  | .sat x => TableModels fs x
  | .unsat => ¬ ∃ x, TableModels fs x

-- A SAT witness is checked against the original factors, even if all
-- preprocessing was untrusted. For residual UNSAT every transfer gate
-- must succeed; a worker's terminal status alone is never evidence.
def certify {n m : Nat} (fs : List (RowFactor n)) (steps : List Nat)
    (a : AffineMap n m) (residual : List (RowFactor m)) :
    Evidence n m → Verdict n
  | .unknown => .unknown
  | .directSat x => if tableCheck fs x then .sat x else .unknown
  | .reducedSat z =>
    if tableCheck fs (expand a z) then .sat (expand a z) else .unknown
  | .directHall p => if packetCheck fs p then .unsat else .unknown
  | .affineUnsat p =>
    match relationalReplay fs steps with
    | none => .unknown
    | some out => if equationCheck out p ⟨[],true⟩ then .unsat else .unknown
  | .reducedHall p =>
    match relationalReplay fs steps with
    | none => .unknown
    | some out =>
      if affineMapCheck out a && (materializedCheck out a residual && packetCheck residual p)
      then .unsat else .unknown

theorem certify_sound {n m : Nat} (fs : List (RowFactor n)) (steps : List Nat)
    (a : AffineMap n m) (residual : List (RowFactor m)) (ev : Evidence n m) :
    Sound fs (certify fs steps a residual ev) := by
  cases ev with
  | unknown => trivial
  | directSat x =>
    cases hx : tableCheck fs x with
    | false => simp [certify, hx, Sound]
    | true => simpa [certify, hx, Sound] using (tableCheck_exact fs x).mp hx
  | reducedSat z =>
    cases hz : tableCheck fs (expand a z) with
    | false => simp [certify, hz, Sound]
    | true => simpa [certify, hz, Sound] using (tableCheck_exact fs (expand a z)).mp hz
  | directHall p =>
    cases hp : packetCheck fs p with
    | false => simp [certify, hp, Sound]
    | true => simpa [certify, hp, Sound] using packetCheck_sound fs p hp
  | affineUnsat p =>
    cases hr : relationalReplay fs steps with
    | none => simp [certify, hr, Sound]
    | some out =>
      cases hp : equationCheck out p ⟨[],true⟩ with
      | false => simp [certify, hr, hp, Sound]
      | true =>
        simp only [certify, hr, hp, if_true, Sound]
        rintro ⟨x,hx⟩
        exact affine_contradiction_sound out p hp
          ⟨x,(relationalReplay_exact fs out steps hr x).mpr hx⟩
  | reducedHall p =>
    cases hr : relationalReplay fs steps with
    | none => simp [certify, hr, Sound]
    | some out =>
      cases hg : (affineMapCheck out a &&
          (materializedCheck out a residual && packetCheck residual p)) with
      | false => simp [certify, hr, hg, Sound]
      | true =>
        obtain ⟨ha,hrest⟩ := and_parts hg
        obtain ⟨hm,hp⟩ := and_parts hrest
        simp only [certify, hr, hg, if_true, Sound]
        rintro ⟨x,hx⟩
        exact packetCheck_sound residual p hp
          ⟨project a x, residual_models_of_source fs out steps hr a ha residual hm x hx⟩

inductive Observation (m : Nat) where
  | timeout
  | sat (z : Assignment m)
  | unsat

def release {n m : Nat} (fs : List (RowFactor n)) (steps : List Nat)
    (a : AffineMap n m) (residual : List (RowFactor m)) (ev : Evidence n m) :
    Observation m → Verdict n
  | .timeout => .unknown
  | .sat z => certify fs steps a residual (.reducedSat z)
  | .unsat =>
    match certify fs steps a residual ev with
    | .unsat => .unsat
    | _ => .unknown

theorem release_sound {n m : Nat} (fs : List (RowFactor n)) (steps : List Nat)
    (a : AffineMap n m) (residual : List (RowFactor m)) (ev : Evidence n m)
    (obs : Observation m) : Sound fs (release fs steps a residual ev obs) := by
  cases obs with
  | timeout => trivial
  | sat z => exact certify_sound fs steps a residual (.reducedSat z)
  | unsat =>
    have hs := certify_sound fs steps a residual ev
    cases hc : certify fs steps a residual ev with
    | unknown => simp [release, hc, Sound]
    | sat x => simp [release, hc, Sound]
    | unsat => simpa [release, hc, Sound] using hs

open MathOS.F038.Physical

-- The observation function can be arbitrary: the release gate still checks
-- mathematical evidence. Quotient equivalence only needs identical head/tape.
def observe {q m : Nat} (machine : Machine q)
    (decode : Int → (Int → Symbol) → Observation m) (c : Config q) : Observation m :=
  if c.state = machine.halt then decode c.head c.tape else .timeout

theorem observations_equal {q r m : Nat} (a : Machine q) (b : Machine r)
    (mapping : Fin q → Option (Fin r)) (c : Config q) (d : Config r)
    (hr : related mapping c d) (hh : c.state = a.halt ↔ d.state = b.halt)
    (decode : Int → (Int → Symbol) → Observation m) :
    observe a decode c = observe b decode d := by
  by_cases hc : c.state = a.halt
  · have hd := hh.mp hc
    simp [observe, hc, hd, hr.2.1, hr.2.2]
  · have hd : d.state ≠ b.halt := fun e => hc (hh.mpr e)
    simp [observe, hc, hd]

theorem composed_physical_release {n m q r : Nat}
    (fs : List (RowFactor n)) (steps : List Nat) (a : AffineMap n m)
    (residual : List (RowFactor m)) (ev : Evidence n m)
    (original : Machine q) (quotient : Machine r)
    (mapping : Fin q → Option (Fin r))
    (ok : quotientCheck original quotient mapping = true)
    (fuel : Nat) (head : Int) (tape : Int → Symbol)
    (decode : Int → (Int → Symbol) → Observation m) :
    let o := run original fuel (initialConfig original head tape)
    let p := run quotient fuel (initialConfig quotient head tape)
    let vo := release fs steps a residual ev (observe original decode o.1)
    let vp := release fs steps a residual ev (observe quotient decode p.1)
    Sound fs vo ∧ vo = vp ∧ o.2 = p.2 := by
  obtain ⟨hr,hclock,hh⟩ := checked_simulation original quotient mapping ok fuel head tape
  have ho := observations_equal original quotient mapping _ _ hr hh decode
  exact ⟨release_sound fs steps a residual ev _, congrArg (release fs steps a residual ev) ho, hclock⟩

#print axioms assignments_complete
#print axioms materializedCheck_exact
#print axioms residual_models_of_source
#print axioms residual_witness_sound
#print axioms certify_sound
#print axioms release_sound
#print axioms composed_physical_release

end MathOS.F038.Composition
