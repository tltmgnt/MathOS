import F038Formal.ResidualRefinement

/-! FV-11: targeted relational deletion replay, derived-factor entailment,
    and composition with the verified affine materialization interface. -/
namespace MathOS.F038.RelationalReplay
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.LocalMaterialization
open MathOS.F038.ResidualRefinement
open MathOS.F038.Bridge

structure Deletion where
  a : Nat
  b : Nat
  removed : List (List Bool)

def replaceAt {α : Type} : List α → Nat → α → List α
  | [], _, _ => []
  | _ :: fs, 0, f => f :: fs
  | g :: gs, i+1, f => g :: replaceAt gs i f

theorem replaceAt_exact {n : Nat} (fs : List (RowFactor n)) (i : Nat)
    (a b : RowFactor n) (ha : lookup fs i = some a)
    (x : Assignment n)
    (he : b.scope.map x ∈ b.rows ↔ a.scope.map x ∈ a.rows) :
    TableModels (replaceAt fs i b) x ↔ TableModels fs x := by
  induction fs generalizing i with
  | nil => simp [lookup] at ha
  | cons f fs ih =>
    cases i with
    | zero =>
      have eq : f = a := by simpa [lookup] using ha
      subst f
      simp only [replaceAt, tableModels_cons, he]
    | succ j =>
      have h : lookup fs j = some a := by simpa [lookup] using ha
      simp only [replaceAt, tableModels_cons, ih j h]

-- A valid model of the original tables satisfies the support factor.
-- In the reverse direction all semijoin rows are original rows.
theorem replaceSemijoin_exact {n : Nat} (fs : List (RowFactor n)) (i : Nat)
    (a b : RowFactor n) (ha : lookup fs i = some a)
    (hb : b ∈ fs) (x : Assignment n) :
    TableModels (replaceAt fs i (semijoin a b)) x ↔ TableModels fs x := by
  have sub : (semijoin a b).scope.map x ∈ (semijoin a b).rows →
      a.scope.map x ∈ a.rows := fun h => (List.mem_filter.mp h).1
  have mono : ∀ (gs : List (RowFactor n)) (j : Nat),
      lookup gs j = some a →
      TableModels (replaceAt gs j (semijoin a b)) x → TableModels gs x := by
    intro gs
    induction gs with
    | nil => intro j h; simp [lookup] at h
    | cons g gs ih =>
      intro j h hm
      cases j with
      | zero =>
        have eq : g = a := by simpa [lookup] using h
        subst g
        exact (tableModels_cons _ _ _).mpr
          ⟨sub ((tableModels_cons _ _ _).mp hm).1, ((tableModels_cons _ _ _).mp hm).2⟩
      | succ j =>
        have ht : lookup gs j = some a := by simpa [lookup] using h
        obtain ⟨hg,hs⟩ := (tableModels_cons _ _ _).mp hm
        exact (tableModels_cons _ _ _).mpr ⟨hg,ih j ht hs⟩
  exact ⟨mono fs i ha, fun hm =>
    (replaceAt_exact fs i a (semijoin a b) ha x
      (semijoin_exact a b x (hm b hb))).mpr hm⟩

def deletionRows {n : Nat} (a b : RowFactor n) : List (List Bool) :=
  a.rows.filter (fun r => decide (r ∉ (semijoin a b).rows))

def overlap {n : Nat} (a b : RowFactor n) : Bool :=
  anyCheck (fun v => decide (v ∈ b.scope)) a.scope

def deletionStep {n : Nat} (fs : List (RowFactor n)) (e : Deletion) :
    Option (List (RowFactor n)) :=
  match lookup fs e.a, lookup fs e.b with
  | some a, some b =>
    if decide (e.a ≠ e.b) && (overlap a b &&
      (decide (e.removed ≠ []) && rowSetCheck e.removed (deletionRows a b))) then
      some (replaceAt fs e.a (semijoin a b))
    else none
  | _, _ => none

theorem deletionStep_exact {n : Nat} (fs out : List (RowFactor n))
    (e : Deletion) (h : deletionStep fs e = some out) (x : Assignment n) :
    TableModels out x ↔ TableModels fs x := by
  cases ha : lookup fs e.a with
  | none => simp [deletionStep, ha] at h
  | some a =>
    cases hb : lookup fs e.b with
    | none => simp [deletionStep, ha, hb] at h
    | some b =>
      -- Keep the Boolean guard intact until its branch is selected.
      simp only [deletionStep, ha, hb] at h
      split at h
      · have eq : replaceAt fs e.a (semijoin a b) = out := Option.some.inj h
        subst out
        exact replaceSemijoin_exact fs e.a a b ha (lookup_mem fs e.b b hb) x
      · contradiction

def replay {n : Nat} (fs : List (RowFactor n)) :
    List Deletion → Option (List (RowFactor n))
  | [] => some fs
  | e :: es => (deletionStep fs e).bind (fun gs => replay gs es)

theorem replay_exact {n : Nat} (fs out : List (RowFactor n))
    (es : List Deletion) (h : replay fs es = some out) (x : Assignment n) :
    TableModels out x ↔ TableModels fs x := by
  induction es generalizing fs with
  | nil =>
    have eq : fs = out := by simpa [replay] using h
    subst out
    exact Iff.rfl
  | cons e es ih =>
    cases hs : deletionStep fs e with
    | none => simp [replay, hs] at h
    | some gs =>
      have ht : replay gs es = some out := by simpa [replay, hs] using h
      exact (ih gs ht).trans (deletionStep_exact fs gs e hs x)

def closureCheck {n : Nat} (fs out : List (RowFactor n)) (es : List Deletion) : Bool :=
  match replay fs es with
  | none => false
  | some gs => tableSetCheck gs out

theorem closureCheck_exact {n : Nat} (fs out : List (RowFactor n))
    (es : List Deletion) (h : closureCheck fs out es = true) (x : Assignment n) :
    TableModels out x ↔ TableModels fs x := by
  cases hr : replay fs es with
  | none => simp [closureCheck, hr] at h
  | some gs =>
    have hc : tableSetCheck gs out = true := by simpa [closureCheck, hr] using h
    exact (tableSetCheck_exact gs out hc x).symm.trans (replay_exact fs gs es hr x)

-- Checked bounded entailment of an added factor by a source factor.
-- No assumption that the added factor is a permutation relation is needed.
def entailCheck {n : Nat} (cap : Nat) (a b : RowFactor n) (s : List (Fin n)) : Bool :=
  decide (s.length ≤ cap) && (covered (a.scope ++ b.scope) s &&
    allCheck (fun x => !rowOK a x || rowOK b x) (localAssignments s))

theorem entailCheck_sound {n : Nat} (cap : Nat) (a b : RowFactor n)
    (s : List (Fin n)) (h : entailCheck cap a b s = true) (x : Assignment n)
    (ha : a.scope.map x ∈ a.rows) : b.scope.map x ∈ b.rows := by
  obtain ⟨_,ht⟩ := and_parts h
  obtain ⟨hc,he⟩ := and_parts ht
  obtain ⟨y,hy,hyx⟩ := localAssignments_complete s x
  have aa : a.scope.map y = a.scope.map x :=
    map_agree _ _ _ (fun i hi => hyx i (covered_sound _ _ hc i
      (List.mem_append.mpr (Or.inl hi))))
  have bb : b.scope.map y = b.scope.map x :=
    map_agree _ _ _ (fun i hi => hyx i (covered_sound _ _ hc i
      (List.mem_append.mpr (Or.inr hi))))
  have hay : rowOK a y = true := (rowOK_exact _ _).mpr (by rw [aa]; exact ha)
  have hh := allCheck_sound _ _ he y hy
  have hby : rowOK b y = true := by simpa [hay] using hh
  have hm := (rowOK_exact _ _).mp hby
  rw [bb] at hm
  exact hm

structure Addition (n : Nat) where
  source : Nat
  factor : RowFactor n
  support : List (Fin n)

def addStep {n : Nat} (cap : Nat) (fs : List (RowFactor n)) (e : Addition n) :
    Option (List (RowFactor n)) :=
  match lookup fs e.source with
  | none => none
  | some a => if entailCheck cap a e.factor e.support then some (e.factor :: fs) else none

theorem addStep_exact {n : Nat} (cap : Nat) (fs out : List (RowFactor n))
    (e : Addition n) (h : addStep cap fs e = some out) (x : Assignment n) :
    TableModels out x ↔ TableModels fs x := by
  cases ha : lookup fs e.source with
  | none => simp [addStep, ha] at h
  | some a =>
    cases hc : entailCheck cap a e.factor e.support with
    | false => simp [addStep, ha, hc] at h
    | true =>
      have eq : e.factor :: fs = out := by simpa [addStep, ha, hc] using h
      subst out
      rw [tableModels_cons]
      exact ⟨And.right, fun hm => ⟨entailCheck_sound cap a e.factor e.support hc x
        (hm a (lookup_mem fs e.source a ha)), hm⟩⟩

theorem emptyFactor_unsat {n : Nat} (fs : List (RowFactor n)) (f : RowFactor n)
    (hf : f ∈ fs) (he : f.rows = []) : ¬ ∃ x, TableModels fs x := by
  rintro ⟨x,hx⟩
  have hm := hx f hf
  simp [he] at hm

theorem closure_affine_exact {n m : Nat} (cap : Nat) (fs mid : List (RowFactor n))
    (es : List Deletion) (hr : closureCheck fs mid es = true) (a : AffineMap n m)
    (ha : affineMapCheck mid a = true) (rs out : List (RowFactor m))
    (ss : List (List (Fin m))) (hl : localCheck cap a mid rs ss = true)
    (hc : tableSetCheck (simplifyResidual cap rs) out = true) :
    (∃ x, TableModels fs x) ↔ (∃ z, TableModels out z) := by
  constructor
  · rintro ⟨x,hx⟩
    have hm := (closureCheck_exact fs mid es hr x).mpr hx
    refine ⟨project a x, (simplified_exact cap a mid rs out ss hl hc _).mpr ?_⟩
    rw [affineMap_reconstruct mid a ha x hm]
    exact hm
  · rintro ⟨z,hz⟩
    exact ⟨expand a z, (closureCheck_exact fs mid es hr _).mp
      ((simplified_exact cap a mid rs out ss hl hc z).mp hz)⟩

#print axioms closureCheck_exact
#print axioms addStep_exact
#print axioms closure_affine_exact
end MathOS.F038.RelationalReplay
