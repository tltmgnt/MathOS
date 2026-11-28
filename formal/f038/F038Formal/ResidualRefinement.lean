import F038Formal.LocalMaterialization

/-! FV-10: exact residual simplification and checked padding.
    The replay is a typed specification for concrete producer operations.
    It is not a verification of the JavaScript interpreter. -/
namespace MathOS.F038.ResidualRefinement
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.LocalMaterialization
open MathOS.F038.Composition
open MathOS.F038.Bridge

def tautCheck {m : Nat} (cap : Nat) (f : RowFactor m) : Bool :=
  decide (f.scope.length ≤ cap) &&
    allCheck (rowOK f) (localAssignments f.scope)

theorem tautCheck_sound {m : Nat} (cap : Nat) (f : RowFactor m)
    (h : tautCheck cap f = true) (z : Assignment m) :
    f.scope.map z ∈ f.rows := by
  obtain ⟨y, hy, ha⟩ := localAssignments_complete f.scope z
  have hm := (rowOK_exact f y).mp (allCheck_sound _ _ (and_parts h).2 y hy)
  rw [map_agree _ _ _ ha] at hm
  exact hm

def dropTautologies {m : Nat} (cap : Nat) (fs : List (RowFactor m)) :
    List (RowFactor m) :=
  fs.filter (fun f => !tautCheck cap f)

theorem dropTautologies_exact {m : Nat} (cap : Nat) (fs : List (RowFactor m))
    (z : Assignment m) :
    TableModels (dropTautologies cap fs) z ↔ TableModels fs z := by
  constructor
  · intro h f hf
    cases ht : tautCheck cap f with
    | true => exact tautCheck_sound cap f ht z
    | false =>
      apply h f
      apply List.mem_filter.mpr
      exact ⟨hf, by simp [ht]⟩
  · intro h f hf
    exact h f (List.mem_filter.mp hf).1

def intersectRows {m : Nat} (f g : RowFactor m) : RowFactor m :=
  ⟨f.scope, f.rows.filter (fun r => decide (r ∈ g.rows))⟩

theorem intersectRows_exact {m : Nat} (f g : RowFactor m)
    (h : f.scope = g.scope) (z : Assignment m) :
    (intersectRows f g).scope.map z ∈ (intersectRows f g).rows ↔
      f.scope.map z ∈ f.rows ∧ g.scope.map z ∈ g.rows := by
  change f.scope.map z ∈ f.rows.filter _ ↔ _
  rw [List.mem_filter]
  simp [h]

-- Merge into the first equal ordered scope, otherwise append.
def insertFactor {m : Nat} (f : RowFactor m) :
    List (RowFactor m) → List (RowFactor m)
  | [] => [f]
  | g :: gs =>
    if g.scope = f.scope then intersectRows g f :: gs
    else g :: insertFactor f gs

theorem insertFactor_exact {m : Nat} (f : RowFactor m)
    (gs : List (RowFactor m)) (z : Assignment m) :
    TableModels (insertFactor f gs) z ↔
      f.scope.map z ∈ f.rows ∧ TableModels gs z := by
  induction gs with
  | nil => simp [insertFactor, tableModels_cons, TableModels]
  | cons g gs ih =>
    by_cases h : g.scope = f.scope
    · simp only [insertFactor, h, if_true, tableModels_cons, intersectRows_exact g f h z]
      tauto
    · simp only [insertFactor, h, if_false, tableModels_cons, ih]
      tauto

def mergeFactors {m : Nat} : List (RowFactor m) → List (RowFactor m)
  | [] => []
  | f :: fs => insertFactor f (mergeFactors fs)

theorem mergeFactors_exact {m : Nat} (fs : List (RowFactor m))
    (z : Assignment m) : TableModels (mergeFactors fs) z ↔ TableModels fs z := by
  induction fs with
  | nil => rfl
  | cons f fs ih =>
    rw [mergeFactors, insertFactor_exact, tableModels_cons, ih]

def simplifyResidual {m : Nat} (cap : Nat) (fs : List (RowFactor m)) :
    List (RowFactor m) :=
  mergeFactors (dropTautologies cap fs)

theorem simplifyResidual_exact {m : Nat} (cap : Nat) (fs : List (RowFactor m))
    (z : Assignment m) : TableModels (simplifyResidual cap fs) z ↔ TableModels fs z :=
  (mergeFactors_exact _ z).trans (dropTautologies_exact cap fs z)

-- Equality of ordered rows is not required: compare membership both ways.
def rowSetCheck (a b : List (List Bool)) : Bool :=
  allCheck (fun r => decide (r ∈ b)) a && allCheck (fun r => decide (r ∈ a)) b

theorem rowSetCheck_exact (a b : List (List Bool))
    (h : rowSetCheck a b = true) (r : List Bool) : r ∈ a ↔ r ∈ b := by
  obtain ⟨ha,hb⟩ := and_parts h
  exact ⟨fun hr => of_decide_eq_true (allCheck_sound _ _ ha r hr),
    fun hr => of_decide_eq_true (allCheck_sound _ _ hb r hr)⟩

def sameFactor {m : Nat} (f g : RowFactor m) : Bool :=
  decide (f.scope = g.scope) && rowSetCheck f.rows g.rows

theorem sameFactor_exact {m : Nat} (f g : RowFactor m)
    (h : sameFactor f g = true) (z : Assignment m) :
    f.scope.map z ∈ f.rows ↔ g.scope.map z ∈ g.rows := by
  obtain ⟨hs,hr⟩ := and_parts h
  have eq : f.scope = g.scope := of_decide_eq_true hs
  rw [eq]
  exact rowSetCheck_exact f.rows g.rows hr _

def included {m : Nat} (fs gs : List (RowFactor m)) : Bool :=
  allCheck (fun f => anyCheck (sameFactor f) gs) fs

theorem included_models {m : Nat} (fs gs : List (RowFactor m))
    (h : included fs gs = true) (z : Assignment m)
    (hm : TableModels gs z) : TableModels fs z := by
  intro f hf
  obtain ⟨g,hg,he⟩ := anyCheck_sound _ _ (allCheck_sound _ _ h f hf)
  exact (sameFactor_exact f g he z).mpr (hm g hg)

def tableSetCheck {m : Nat} (fs gs : List (RowFactor m)) : Bool :=
  included fs gs && included gs fs

theorem tableSetCheck_exact {m : Nat} (fs gs : List (RowFactor m))
    (h : tableSetCheck fs gs = true) (z : Assignment m) :
    TableModels fs z ↔ TableModels gs z := by
  obtain ⟨ha,hb⟩ := and_parts h
  exact ⟨included_models gs fs hb z, included_models fs gs ha z⟩

-- Compose with the verified FV-09 interface. The local list may include
-- tautologies, zero-arity factors and duplicate ordered scopes.
theorem simplified_exact {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (fs : List (RowFactor n)) (rs out : List (RowFactor m))
    (ss : List (List (Fin m))) (hl : localCheck cap a fs rs ss = true)
    (hc : tableSetCheck (simplifyResidual cap rs) out = true)
    (z : Assignment m) :
    TableModels out z ↔ TableModels fs (expand a z) :=
  ((tableSetCheck_exact _ _ hc z).symm.trans
    (simplifyResidual_exact cap rs z)).trans (localCheck_exact cap a fs rs ss hl z)

-- Lift zero-dimensional tables to a single dummy coordinate fixed to false.
def padFactor (f : RowFactor 0) : RowFactor 1 :=
  ⟨f.scope.map Fin.elim0, f.rows⟩

def zeroAssignment : Assignment 0 := fun i => Fin.elim0 i
def dummyZero : RowFactor 1 := ⟨[0], [[false]]⟩
def padZero (fs : List (RowFactor 0)) : List (RowFactor 1) :=
  dummyZero :: fs.map padFactor

theorem zero_scope_empty (s : List (Fin 0)) : s = [] := by
  cases s with
  | nil => rfl
  | cons i is => exact Fin.elim0 i

theorem padFactor_exact (f : RowFactor 0) (z : Assignment 1) :
    (padFactor f).scope.map z ∈ (padFactor f).rows ↔
      f.scope.map zeroAssignment ∈ f.rows := by
  simp [padFactor, zero_scope_empty f.scope]

theorem padZero_exact (fs : List (RowFactor 0)) (z : Assignment 1) :
    TableModels (padZero fs) z ↔ z 0 = false ∧ TableModels fs zeroAssignment := by
  rw [padZero, tableModels_cons]
  constructor
  · rintro ⟨hd,hm⟩
    refine ⟨?_, ?_⟩
    · simpa [dummyZero] using hd
    · intro f hf
      exact (padFactor_exact f z).mp (hm (padFactor f) (List.mem_map.mpr ⟨f,hf,rfl⟩))
  · rintro ⟨hd,hm⟩
    refine ⟨?_, ?_⟩
    · simp [dummyZero, hd]
    · intro g hg
      obtain ⟨f,hf,rfl⟩ := List.mem_map.mp hg
      exact (padFactor_exact f z).mpr (hm f hf)

theorem padZero_satisfiable (fs : List (RowFactor 0)) :
    (∃ z, TableModels (padZero fs) z) ↔ (∃ x, TableModels fs x) := by
  constructor
  · rintro ⟨z,hz⟩
    exact ⟨zeroAssignment, ((padZero_exact fs z).mp hz).2⟩
  · rintro ⟨x,hx⟩
    have he : x = zeroAssignment := by
      funext i
      exact Fin.elim0 i
    subst x
    exact ⟨fun _ => false, (padZero_exact fs _).mpr ⟨rfl,hx⟩⟩

theorem simplifiedHall_sound {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (fs : List (RowFactor n)) (rs out : List (RowFactor m))
    (ss : List (List (Fin m))) (ha : affineMapCheck fs a = true)
    (hl : localCheck cap a fs rs ss = true)
    (hc : tableSetCheck (simplifyResidual cap rs) out = true)
    (p : Packet m) (hp : packetCheck out p = true) : ¬ ∃ x, TableModels fs x := by
  rintro ⟨x,hx⟩
  apply packetCheck_sound out p hp
  refine ⟨project a x, (simplified_exact cap a fs rs out ss hl hc _).mpr ?_⟩
  rw [affineMap_reconstruct fs a ha x hx]
  exact hx

#print axioms simplifyResidual_exact
#print axioms tableSetCheck_exact
#print axioms simplified_exact
#print axioms padZero_satisfiable
#print axioms simplifiedHall_sound

end MathOS.F038.ResidualRefinement
