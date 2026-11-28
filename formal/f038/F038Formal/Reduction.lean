import F038Formal.Certificate

/-! FV-03: exact semijoins and proof-carrying GF(2) affine reconstruction.
    Reference definitions; not a refinement of the JavaScript reduction pipeline. -/
namespace MathOS.F038.Reduction
open MathOS.F038
open MathOS.F038.Cert

theorem allCheck_complete {α : Type} (p : α → Bool) (xs : List α)
    (h : ∀ a ∈ xs, p a = true) : allCheck p xs = true := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    have ha : p a = true := h a (by simp)
    have ht : allCheck p as = true :=
      ih (fun b hb => h b (List.mem_cons.mpr (Or.inr hb)))
    simp [allCheck, ha, ht]

theorem anyCheck_complete {α : Type} (p : α → Bool) (xs : List α)
    (a : α) (ha : a ∈ xs) (h : p a = true) : anyCheck p xs = true := by
  induction xs with
  | nil => simp at ha
  | cons b bs ih =>
    rcases List.mem_cons.mp ha with eq | hm
    · subst b
      simp [anyCheck, h]
    · simp [anyCheck, ih hm]

-- All pairs of bindings on a common coordinate must agree.
def compatible {n : Nat} (a b : List (Fin n × Bool)) : Bool :=
  allCheck (fun p => allCheck
    (fun q => decide (p.1 ≠ q.1 ∨ p.2 = q.2)) b) a

theorem binding_sound {n : Nat} (x : Assignment n) (scope : List (Fin n))
    (p : Fin n × Bool) (hp : p ∈ scope.zip (scope.map x)) : p.2 = x p.1 := by
  induction scope with
  | nil => simp at hp
  | cons v vs ih =>
    change p ∈ (v, x v) :: vs.zip (vs.map x) at hp
    rcases List.mem_cons.mp hp with eq | hm
    · subst p
      rfl
    · exact ih hm

theorem compatible_models {n : Nat} (x : Assignment n) (a b : List (Fin n)) :
    compatible (a.zip (a.map x)) (b.zip (b.map x)) = true := by
  apply allCheck_complete
  intro p hp
  apply allCheck_complete
  intro q hq
  apply decide_eq_true
  by_cases eq : p.1 = q.1
  · exact Or.inr ((binding_sound x a p hp).trans
      ((congrArg x eq).trans (binding_sound x b q hq).symm))
  · exact Or.inl eq

def semijoin {n : Nat} (a b : RowFactor n) : RowFactor n :=
  ⟨a.scope, a.rows.filter (fun r =>
    anyCheck (fun s => compatible (a.scope.zip r) (b.scope.zip s)) b.rows)⟩

theorem semijoin_exact {n : Nat} (a b : RowFactor n) (x : Assignment n)
    (hb : b.scope.map x ∈ b.rows) :
    (semijoin a b).scope.map x ∈ (semijoin a b).rows ↔
      a.scope.map x ∈ a.rows := by
  change a.scope.map x ∈ a.rows.filter _ ↔ a.scope.map x ∈ a.rows
  constructor
  · intro h
    exact (List.mem_filter.mp h).1
  · intro h
    apply List.mem_filter.mpr
    exact ⟨h, anyCheck_complete _ _ _ hb (compatible_models x a.scope b.scope)⟩

-- Apply a semijoin to every factor using an existing support factor.
def pruneAgainst {n : Nat} (fs : List (RowFactor n)) (b : RowFactor n) :
    List (RowFactor n) := fs.map (fun a => semijoin a b)

theorem pruneAgainst_exact {n : Nat} (fs : List (RowFactor n)) (b : RowFactor n)
    (hb : b ∈ fs) (x : Assignment n) :
    TableModels (pruneAgainst fs b) x ↔ TableModels fs x := by
  constructor
  · intro h a ha
    have h' := h (semijoin a b) (List.mem_map.mpr ⟨a, ha, rfl⟩)
    exact (List.mem_filter.mp h').1
  · intro h a ha
    obtain ⟨orig, horig, rfl⟩ := List.mem_map.mp ha
    exact (semijoin_exact orig b x (h b hb)).mpr (h orig horig)

def relationalReplay {n : Nat} (fs : List (RowFactor n)) :
    List Nat → Option (List (RowFactor n))
  | [] => some fs
  | i :: rest =>
    match lookup fs i with
    | none => none
    | some b => relationalReplay (pruneAgainst fs b) rest

theorem relationalReplay_exact {n : Nat} (fs out : List (RowFactor n))
    (steps : List Nat) (h : relationalReplay fs steps = some out) (x : Assignment n) :
    TableModels out x ↔ TableModels fs x := by
  induction steps generalizing fs with
  | nil =>
    have eq : fs = out := by simpa [relationalReplay] using h
    subst out
    exact Iff.rfl
  | cons i rest ih =>
    cases hb : lookup fs i with
    | none => simp [relationalReplay, hb] at h
    | some b =>
      have hr : relationalReplay (pruneAgainst fs b) rest = some out := by
        simpa [relationalReplay, hb] using h
      exact (ih _ hr).trans (pruneAgainst_exact fs b (lookup_mem fs i b hb) x)

-- GF(2) arithmetic on Boolean values. Duplicate coordinates are allowed;
-- concatenation represents addition, with cancellation at evaluation time.
def bxor (a b : Bool) : Bool := if a then !b else b

theorem bxor_assoc (a b c : Bool) :
    bxor (bxor a b) c = bxor a (bxor b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem bxor_swap (a b c : Bool) :
    bxor a (bxor b c) = bxor b (bxor a c) := by
  cases a <;> cases b <;> cases c <;> rfl

def parity {α : Type} (x : α → Bool) : List α → Bool
  | [] => false
  | a :: as => bxor (x a) (parity x as)

theorem parity_append {α : Type} (x : α → Bool) (a b : List α) :
    parity x (a ++ b) = bxor (parity x a) (parity x b) := by
  induction a with
  | nil => rfl
  | cons v vs ih =>
    change bxor (x v) (parity x (vs ++ b)) =
      bxor (bxor (x v) (parity x vs)) (parity x b)
    rw [ih, bxor_assoc]

def select {α : Type} : List Bool → List α → List α
  | b :: bs, a :: as => if b then a :: select bs as else select bs as
  | _, _ => []

theorem select_map {α β : Type} (mask : List Bool) (xs : List α) (f : α → β) :
    select mask (xs.map f) = (select mask xs).map f := by
  induction mask generalizing xs with
  | nil => rfl
  | cons b bs ih =>
    cases xs with
    | nil => rfl
    | cons a as => cases b <;> simp [select, ih]

theorem parity_map {α β : Type} (f : α → β) (x : β → Bool) (xs : List α) :
    parity x (xs.map f) = parity (fun a => x (f a)) xs := by
  induction xs with
  | nil => rfl
  | cons a as ih => simp [parity, ih]

structure Equation (n : Nat) where
  vars : List (Fin n)
  rhs : Bool
  deriving DecidableEq

def EqHolds {n : Nat} (x : Assignment n) (e : Equation n) : Prop :=
  parity x e.vars = e.rhs

def addEq {n : Nat} (a b : Equation n) : Equation n :=
  ⟨a.vars ++ b.vars, bxor a.rhs b.rhs⟩

theorem addEq_sound {n : Nat} (x : Assignment n) (a b : Equation n)
    (ha : EqHolds x a) (hb : EqHolds x b) : EqHolds x (addEq a b) := by
  change parity x (a.vars ++ b.vars) = bxor a.rhs b.rhs
  change parity x a.vars = a.rhs at ha
  change parity x b.vars = b.rhs at hb
  rw [parity_append, ha, hb]

-- Checked cancellation of two occurrences, via removal of the first match.
def removeOnce {α : Type} [DecidableEq α] (v : α) : List α → Option (List α)
  | [] => none
  | a :: as => if a = v then some as else (removeOnce v as).map (List.cons a)

theorem removeOnce_parity {α : Type} [DecidableEq α] (x : α → Bool)
    (v : α) (xs ys : List α) (h : removeOnce v xs = some ys) :
    parity x xs = bxor (x v) (parity x ys) := by
  induction xs generalizing ys with
  | nil => simp [removeOnce] at h
  | cons a as ih =>
    by_cases eq : a = v
    · subst a
      have e : as = ys := by simpa [removeOnce] using h
      subst ys
      rfl
    · cases hr : removeOnce v as with
      | none => simp [removeOnce, eq, hr] at h
      | some zs =>
        have e : a :: zs = ys := by simpa [removeOnce, eq, hr] using h
        subst ys
        change bxor (x a) (parity x as) = bxor (x v) (bxor (x a) (parity x zs))
        rw [ih zs hr, bxor_swap]

theorem cancel_sound {α : Type} [DecidableEq α] (x : α → Bool)
    (v : α) (xs ys zs : List α)
    (h1 : removeOnce v xs = some ys) (h2 : removeOnce v ys = some zs) :
    parity x xs = parity x zs := by
  rw [removeOnce_parity x v xs ys h1, removeOnce_parity x v ys zs h2]
  cases x v <;> cases parity x zs <;> rfl

inductive EqProof (n : Nat) where
  | source (factor : Nat) (mask : List Bool) (rhs : Bool)
  | add (left right : EqProof n)
  | cancel (proof : EqProof n) (var : Fin n)

def eqDerive {n : Nat} (fs : List (RowFactor n)) : EqProof n → Option (Equation n)
  | .source i mask rhs =>
    match lookup fs i with
    | none => none
    | some f =>
      if mask.length = f.scope.length then
        if allCheck (fun row => decide (parity id (select mask row) = rhs)) f.rows then
          some ⟨select mask f.scope, rhs⟩
        else none
      else none
  | .add a b =>
    match eqDerive fs a, eqDerive fs b with
    | some ea, some eb => some (addEq ea eb)
    | _, _ => none
  | .cancel p v =>
    match eqDerive fs p with
    | none => none
    | some e =>
      match removeOnce v e.vars with
      | none => none
      | some ys => (removeOnce v ys).map (fun zs => ⟨zs, e.rhs⟩)

theorem eqDerive_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (p : EqProof n) :
    ∀ e, eqDerive fs p = some e → EqHolds x e := by
  induction p with
  | source i mask rhs =>
    intro e h
    cases hf : lookup fs i with
    | none => simp [eqDerive, hf] at h
    | some f =>
      by_cases hl : mask.length = f.scope.length
      · cases hc : allCheck (fun row => decide (parity id (select mask row) = rhs)) f.rows with
        | false => simp [eqDerive, hf, hl, hc] at h
        | true =>
          have he : (⟨select mask f.scope, rhs⟩ : Equation n) = e := by
            simpa [eqDerive, hf, hl, hc] using h
          subst e
          have hp := allCheck_sound _ _ hc _ (hm f (lookup_mem fs i f hf))
          have hv : parity id (select mask (f.scope.map x)) = rhs := of_decide_eq_true hp
          rw [select_map, parity_map] at hv
          exact hv
      · simp [eqDerive, hf, hl] at h
  | add a b ia ib =>
    intro e h
    cases ha : eqDerive fs a with
    | none => simp [eqDerive, ha] at h
    | some ea =>
      cases hb : eqDerive fs b with
      | none => simp [eqDerive, ha, hb] at h
      | some eb =>
        have he : addEq ea eb = e := by simpa [eqDerive, ha, hb] using h
        subst e
        exact addEq_sound x ea eb (ia ea ha) (ib eb hb)
  | cancel p v ih =>
    intro e h
    cases hp : eqDerive fs p with
    | none => simp [eqDerive, hp] at h
    | some ep =>
      cases h1 : removeOnce v ep.vars with
      | none => simp [eqDerive, hp, h1] at h
      | some ys =>
        cases h2 : removeOnce v ys with
        | none => simp [eqDerive, hp, h1, h2] at h
        | some zs =>
          have he : (⟨zs, ep.rhs⟩ : Equation n) = e := by
            simpa [eqDerive, hp, h1, h2] using h
          subst e
          change parity x zs = ep.rhs
          rw [← cancel_sound x v ep.vars ys zs h1 h2]
          exact ih ep hp

def equationCheck {n : Nat} (fs : List (RowFactor n)) (p : EqProof n)
    (e : Equation n) : Bool :=
  match eqDerive fs p with
  | none => false
  | some a => decide (a = e)

theorem equationCheck_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (p : EqProof n) (e : Equation n)
    (h : equationCheck fs p e = true) : EqHolds x e := by
  cases he : eqDerive fs p with
  | none => simp [equationCheck, he] at h
  | some a =>
    have eq : a = e := of_decide_eq_true (by simpa [equationCheck, he] using h)
    subst e
    exact eqDerive_sound fs x hm p a he

theorem affine_contradiction_sound {n : Nat} (fs : List (RowFactor n)) (p : EqProof n)
    (h : equationCheck fs p ⟨[], true⟩ = true) : ¬ ∃ x, TableModels fs x := by
  rintro ⟨x, hm⟩
  have he := equationCheck_sound fs x hm p ⟨[], true⟩ h
  change false = true at he
  contradiction

-- A checked equation for each original coordinate supplies a reconstruction
-- over free coordinates. This does not assume the producer's pivot choices.
structure AffineMap (n m : Nat) where
  free : Fin m → Fin n
  forms : Fin n → Equation m
  proofs : Fin n → EqProof n

def expand {n m : Nat} (a : AffineMap n m) (z : Assignment m) : Assignment n :=
  fun i => bxor (a.forms i).rhs (parity z (a.forms i).vars)

def project {n m : Nat} (a : AffineMap n m) (x : Assignment n) : Assignment m :=
  fun i => x (a.free i)

def formEquation {n m : Nat} (a : AffineMap n m) (i : Fin n) : Equation n :=
  ⟨i :: (a.forms i).vars.map a.free, (a.forms i).rhs⟩

def affineMapCheck {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m) : Bool :=
  allCheck (fun i => equationCheck fs (a.proofs i) (formEquation a i)) (List.finRange n)

theorem affineMap_reconstruct {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m)
    (h : affineMapCheck fs a = true) (x : Assignment n) (hm : TableModels fs x) :
    expand a (project a x) = x := by
  funext i
  have hi := allCheck_sound _ _ h i (by simp)
  have he := equationCheck_sound fs x hm (a.proofs i) (formEquation a i) hi
  change bxor (x i) (parity x ((a.forms i).vars.map a.free)) = (a.forms i).rhs at he
  rw [parity_map] at he
  change bxor (a.forms i).rhs (parity (project a x) (a.forms i).vars) = x i
  change bxor (x i) (parity (project a x) (a.forms i).vars) = (a.forms i).rhs at he
  rw [← he]
  cases x i <;> cases parity (project a x) (a.forms i).vars <;> rfl

-- Executable residual predicate, with exact substitution into every original
-- table. This is not the narrower materialized factor output of D7B.
def pullbackCheck {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m)
    (z : Assignment m) : Bool :=
  allCheck (fun f => decide (f.scope.map (expand a z) ∈ f.rows)) fs

theorem pullback_exact {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m)
    (z : Assignment m) : pullbackCheck fs a z = true ↔ TableModels fs (expand a z) := by
  constructor
  · intro h f hf
    exact of_decide_eq_true (allCheck_sound _ _ h f hf)
  · intro h
    exact allCheck_complete _ _ (fun f hf => decide_eq_true (h f hf))

theorem affine_reduction_exact {n m : Nat} (fs : List (RowFactor n)) (a : AffineMap n m)
    (h : affineMapCheck fs a = true) :
    (∃ x, TableModels fs x) ↔ (∃ z, pullbackCheck fs a z = true) := by
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨project a x, (pullback_exact fs a _).mpr ?_⟩
    rw [affineMap_reconstruct fs a h x hx]
    exact hx
  · rintro ⟨z, hz⟩
    exact ⟨expand a z, (pullback_exact fs a z).mp hz⟩

theorem relational_affine_compose {n m : Nat} (fs out : List (RowFactor n))
    (steps : List Nat) (hr : relationalReplay fs steps = some out)
    (a : AffineMap n m) (ha : affineMapCheck out a = true) :
    (∃ x, TableModels fs x) ↔ (∃ z, pullbackCheck out a z = true) := by
  constructor
  · rintro ⟨x, hx⟩
    exact (affine_reduction_exact out a ha).mp ⟨x, (relationalReplay_exact fs out steps hr x).mpr hx⟩
  · intro h
    obtain ⟨x, hx⟩ := (affine_reduction_exact out a ha).mpr h
    exact ⟨x, (relationalReplay_exact fs out steps hr x).mp hx⟩

#print axioms semijoin_exact
#print axioms relationalReplay_exact
#print axioms eqDerive_sound
#print axioms affine_contradiction_sound
#print axioms affineMap_reconstruct
#print axioms affine_reduction_exact
#print axioms relational_affine_compose

end MathOS.F038.Reduction
