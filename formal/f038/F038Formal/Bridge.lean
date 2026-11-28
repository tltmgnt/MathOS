import F038Formal.Reduction

/-! FV-04: checked raw-data boundary and implication projection replay.
    The JS exporter is untrusted; this module checks its finite payload. -/
namespace MathOS.F038.Bridge
open MathOS.F038
open MathOS.F038.Cert

structure RawFactor where
  scope : List Nat
  rows : List (List Bool)

def RawModels (fs : List RawFactor) (x : Nat → Bool) : Prop :=
  ∀ f ∈ fs, f.scope.map x ∈ f.rows

def decodeScope (n : Nat) : List Nat → Option (List (Fin n))
  | [] => some []
  | i :: rest =>
    if hi : i < n then
      match decodeScope n rest with
      | none => none
      | some tail => some (⟨i, hi⟩ :: tail)
    else none

theorem decodeScope_eval (n : Nat) (s : List Nat) (t : List (Fin n))
    (h : decodeScope n s = some t) (x : Nat → Bool) :
    t.map (fun i => x i.val) = s.map x := by
  induction s generalizing t with
  | nil =>
    have he : ([] : List (Fin n)) = t := by simpa [decodeScope] using h
    subst t
    rfl
  | cons i rest ih =>
    by_cases hi : i < n
    · cases hr : decodeScope n rest with
      | none => simp [decodeScope, hi, hr] at h
      | some tail =>
        have he : (⟨i, hi⟩ :: tail : List (Fin n)) = t := by
          simpa [decodeScope, hi, hr] using h
        subst t
        simp only [List.map_cons]
        rw [ih tail hr]
    · simp [decodeScope, hi] at h

def decodeFactors (n : Nat) : List RawFactor → Option (List (RowFactor n))
  | [] => some []
  | f :: rest =>
    match decodeScope n f.scope, decodeFactors n rest with
    | some scope, some tail =>
      if allCheck (fun row => decide (row.length = f.scope.length)) f.rows then
        some (⟨scope, f.rows⟩ :: tail)
      else none
    | _, _ => none

theorem decodeFactors_models (n : Nat) (fs : List RawFactor) (out : List (RowFactor n))
    (h : decodeFactors n fs = some out) (x : Nat → Bool) (hm : RawModels fs x) :
    TableModels out (fun i => x i.val) := by
  induction fs generalizing out with
  | nil =>
    have he : ([] : List (RowFactor n)) = out := by simpa [decodeFactors] using h
    subst out
    intro f hf
    simp at hf
  | cons f rest ih =>
    cases hs : decodeScope n f.scope with
    | none => simp [decodeFactors, hs] at h
    | some scope =>
      cases hr : decodeFactors n rest with
      | none => simp [decodeFactors, hs, hr] at h
      | some tail =>
        cases hw : allCheck (fun row => decide (row.length = f.scope.length)) f.rows with
        | false => simp [decodeFactors, hs, hr, hw] at h
        | true =>
          have he : (⟨scope, f.rows⟩ :: tail : List (RowFactor n)) = out := by
            simpa [decodeFactors, hs, hr, hw] using h
          subst out
          intro g hg
          rcases List.mem_cons.mp hg with eq | hg
          · subst g
            change scope.map (fun i => x i.val) ∈ f.rows
            rw [decodeScope_eval n f.scope scope hs x]
            exact hm f (by simp)
          · exact ih tail hr (fun a ha => hm a (List.mem_cons.mpr (Or.inr ha))) g hg

-- JS literal convention: +/- (zero-based coordinate + 1); zero rejected.
def decodeLit (n : Nat) (z : Int) : Option (Lit n) :=
  if h : 0 < z.natAbs ∧ z.natAbs ≤ n then
    some ⟨⟨z.natAbs - 1, by omega⟩, decide (0 < z)⟩
  else none

inductive RawProof where
  | source (index : Nat) (row : List Bool)
  | resolution (left right : RawProof) (pivot : Int)

def decodeProof (n : Nat) : RawProof → Option (RowProof n)
  | .source i row => some (.source i row)
  | .resolution a b p => do
    let a' ← decodeProof n a
    let b' ← decodeProof n b
    let p' ← decodeLit n p
    return .resolution a' b' p'

structure RawConflict where
  left : Int
  right : Int
  steps : List (Int × RawProof)

def decodeConflict (n : Nat) (c : RawConflict) : Option (Conflict n) := do
  let a ← decodeLit n c.left
  let b ← decodeLit n c.right
  let s ← c.steps.mapM (fun (l,p) => do
    let l' ← decodeLit n l
    let p' ← decodeProof n p
    return (l',p'))
  return ⟨a,b,s⟩

structure RawGroup where
  options : List Int
  proof : RawProof

def decodeGroup (n : Nat) (g : RawGroup) : Option (Group n) := do
  let opts ← g.options.mapM (decodeLit n)
  let p ← decodeProof n g.proof
  return ⟨opts,p⟩

structure RawPacket where
  retained : List Nat
  paths : List RawConflict
  holeCount : Nat
  groups : List RawGroup
  placements : List (Int × Nat)
  conflicts : List RawConflict

structure Packet (n : Nat) where
  retained : List Nat
  paths : List (Conflict n)
  holeCount : Nat
  groups : List (Group n)
  placements : List (Lit n × Nat)
  conflicts : List (Conflict n)

def decodePacket (n : Nat) (c : RawPacket) : Option (Packet n) := do
  let paths ← c.paths.mapM (decodeConflict n)
  let groups ← c.groups.mapM (decodeGroup n)
  let places ← c.placements.mapM (fun (l,j) => do
    let l' ← decodeLit n l
    return (l',j))
  let conflicts ← c.conflicts.mapM (decodeConflict n)
  return ⟨c.retained, paths, c.holeCount, groups, places, conflicts⟩

def retain {n : Nat} (fs : List (RowFactor n)) :
    List Nat → Option (List (RowFactor n))
  | [] => some []
  | i :: rest => do
    let f ← lookup fs i
    let tail ← retain fs rest
    return f :: tail

theorem retain_models {n : Nat} (fs out : List (RowFactor n))
    (ids : List Nat) (h : retain fs ids = some out) (x : Assignment n)
    (hm : TableModels fs x) : TableModels out x := by
  induction ids generalizing out with
  | nil =>
    have he : ([] : List (RowFactor n)) = out := by simpa [retain] using h
    subst out
    intro f hf
    simp at hf
  | cons i rest ih =>
    cases hf : lookup fs i with
    | none => simp [retain, hf] at h
    | some f =>
      cases hr : retain fs rest with
      | none => simp [retain, hf, hr] at h
      | some tail =>
        have he : f :: tail = out := by simpa [retain, hf, hr] using h
        subst out
        intro g hg
        rcases List.mem_cons.mp hg with eq | hg
        · subst g
          exact hm f (lookup_mem fs i f hf)
        · exact ih tail hr g hg

def exclusionFactor {n : Nat} (a b : Lit n) : RowFactor n :=
  ⟨[a.var,b.var], [[false,false],[true,false],[false,true],[true,true]].filter
    (fun r => decide (r ≠ [a.positive,b.positive]))⟩

theorem exclusionFactor_models {n : Nat} (x : Assignment n) (a b : Lit n)
    (h : ¬ (holds x a ∧ holds x b)) :
    (exclusionFactor a b).scope.map x ∈ (exclusionFactor a b).rows := by
  change [x a.var, x b.var] ∈
    ([[false,false],[true,false],[false,true],[true,true]].filter
      (fun r => decide (r ≠ [a.positive,b.positive])))
  apply List.mem_filter.mpr
  constructor
  · cases (x a.var) <;> cases (x b.var) <;> simp
  · apply decide_eq_true
    intro eq
    apply h
    simpa [holds] using eq

def validPath {n : Nat} (fs : List (RowFactor n)) (p : Conflict n) : Bool :=
  pathCheck fs p.left (neg p.right) p.steps

def projectTables {n : Nat} (fs : List (RowFactor n)) (c : Packet n) :
    Option (List (RowFactor n)) :=
  match retain fs c.retained with
  | none => none
  | some kept =>
    if allCheck (validPath fs) c.paths then
      some (kept ++ c.paths.map (fun p => exclusionFactor p.left p.right))
    else none

theorem projection_preserves_models {n : Nat} (fs out : List (RowFactor n))
    (c : Packet n) (h : projectTables fs c = some out)
    (x : Assignment n) (hm : TableModels fs x) : TableModels out x := by
  cases hk : retain fs c.retained with
  | none => simp [projectTables, hk] at h
  | some kept =>
    cases hp : allCheck (validPath fs) c.paths with
    | false => simp [projectTables, hk, hp] at h
    | true =>
      have he : kept ++ c.paths.map (fun p => exclusionFactor p.left p.right) = out := by
        simpa [projectTables, hk, hp] using h
      subst out
      intro f hf
      rcases List.mem_append.mp hf with hf | hf
      · exact retain_models fs kept c.retained hk x hm f hf
      · obtain ⟨p, hmemb, rfl⟩ := List.mem_map.mp hf
        apply exclusionFactor_models
        intro both
        have pv := allCheck_sound _ _ hp p hmemb
        exact (neg_holds_iff x p.right).mp
          (pathCheck_sound fs x hm p.left (neg p.right) p.steps pv both.1) both.2

def packetCheck {n : Nat} (fs : List (RowFactor n)) (c : Packet n) : Bool :=
  match projectTables fs c with
  | none => false
  | some out => checkHallLists out c.holeCount c.groups c.placements c.conflicts

theorem packetCheck_sound {n : Nat} (fs : List (RowFactor n)) (c : Packet n)
    (h : packetCheck fs c = true) : ¬ ∃ x, TableModels fs x := by
  cases hp : projectTables fs c with
  | none => simp [packetCheck, hp] at h
  | some out =>
    have hc : checkHallLists out c.holeCount c.groups c.placements c.conflicts = true := by
      simpa [packetCheck, hp] using h
    rintro ⟨x, hm⟩
    exact checkHallLists_sound out c.holeCount c.groups c.placements c.conflicts hc
      ⟨x, projection_preserves_models fs out c hp x hm⟩

def rawCheck (n : Nat) (fs : List RawFactor) (c : RawPacket) : Bool :=
  match decodeFactors n fs, decodePacket n c with
  | some f, some p => packetCheck f p
  | _, _ => false

theorem rawCheck_sound (n : Nat) (fs : List RawFactor) (c : RawPacket)
    (h : rawCheck n fs c = true) : ¬ ∃ x, RawModels fs x := by
  cases hf : decodeFactors n fs with
  | none => simp [rawCheck, hf] at h
  | some f =>
    cases hp : decodePacket n c with
    | none => simp [rawCheck, hf, hp] at h
    | some p =>
      have hc : packetCheck f p = true := by simpa [rawCheck, hf, hp] using h
      rintro ⟨x, hm⟩
      exact packetCheck_sound f p hc
        ⟨fun i => x i.val, decodeFactors_models n fs f hf x hm⟩

#print axioms decodeFactors_models
#print axioms projection_preserves_models
#print axioms packetCheck_sound
#print axioms rawCheck_sound

end MathOS.F038.Bridge
