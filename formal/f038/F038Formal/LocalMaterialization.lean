import F038Formal.Composition

/-! FV-09: bounded local materialization certificates.
    One residual factor per source factor; explicit support and width cap.
    This checks pointwise affine pullback equivalence without enumerating
    assignments to all free coordinates. Merging/omission is a separate gate. -/
namespace MathOS.F038.LocalMaterialization
open MathOS.F038
open MathOS.F038.Cert
open MathOS.F038.Reduction
open MathOS.F038.Bridge
open MathOS.F038.Composition

def setBit {m : Nat} (z : Assignment m) (v : Fin m) (b : Bool) : Assignment m :=
  fun i => if i = v then b else z i

def localAssignments {m : Nat} : List (Fin m) → List (Assignment m)
  | [] => [fun _ => false]
  | v :: vs =>
    (localAssignments vs).map (fun z => setBit z v false) ++
    (localAssignments vs).map (fun z => setBit z v true)

theorem localAssignments_count {m : Nat} (s : List (Fin m)) :
    (localAssignments s).length = 2 ^ s.length := by
  induction s with
  | nil => rfl
  | cons v vs ih =>
    simp only [localAssignments, List.length_append, List.length_map, ih,
      List.length_cons, Nat.pow_succ, Nat.mul_two]

theorem localAssignments_complete {m : Nat} (s : List (Fin m)) (z : Assignment m) :
    ∃ y ∈ localAssignments s, ∀ i ∈ s, y i = z i := by
  induction s with
  | nil =>
    exact ⟨fun _ => false, by simp [localAssignments], by simp⟩
  | cons v vs ih =>
    obtain ⟨y, hy, ha⟩ := ih
    refine ⟨setBit y v (z v), ?_, ?_⟩
    · simp only [localAssignments, List.mem_append]
      cases hb : z v
      · exact Or.inl (List.mem_map.mpr ⟨y, hy, by simp [hb]⟩)
      · exact Or.inr (List.mem_map.mpr ⟨y, hy, by simp [hb]⟩)
    · intro i hi
      rcases List.mem_cons.mp hi with eq | hm
      · subst i
        simp [setBit]
      · by_cases e : i = v
        · simp [setBit, e]
        · simp [setBit, e, ha i hm]

theorem map_agree {α β : Type} (s : List α) (x y : α → β)
    (h : ∀ i ∈ s, x i = y i) : s.map x = s.map y := by
  induction s with
  | nil => rfl
  | cons v vs ih =>
    simp only [List.map_cons]
    rw [h v (by simp), ih (fun i hi => h i (List.mem_cons.mpr (Or.inr hi)))]

theorem parity_agree {m : Nat} (s : List (Fin m)) (x y : Assignment m)
    (h : ∀ i ∈ s, x i = y i) : parity x s = parity y s := by
  induction s with
  | nil => rfl
  | cons v vs ih =>
    simp only [parity]
    rw [h v (by simp), ih (fun i hi => h i (List.mem_cons.mpr (Or.inr hi)))]

def support {n m : Nat} (a : AffineMap n m) (f : RowFactor n) (r : RowFactor m) :
    List (Fin m) :=
  f.scope.flatMap (fun i => (a.forms i).vars) ++ r.scope

def covered {m : Nat} (needed s : List (Fin m)) : Bool :=
  allCheck (fun i => decide (i ∈ s)) needed

theorem covered_sound {m : Nat} (needed s : List (Fin m))
    (h : covered needed s = true) (i : Fin m) (hi : i ∈ needed) : i ∈ s :=
  of_decide_eq_true (allCheck_sound _ _ h i hi)

def rowOK {m : Nat} (f : RowFactor m) (z : Assignment m) : Bool :=
  decide (f.scope.map z ∈ f.rows)

theorem rowOK_exact {m : Nat} (f : RowFactor m) (z : Assignment m) :
    rowOK f z = true ↔ f.scope.map z ∈ f.rows := by simp [rowOK]

def factorCheck {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (f : RowFactor n) (r : RowFactor m) (s : List (Fin m)) : Bool :=
  decide (s.length ≤ cap) && (covered (support a f r) s &&
    allCheck (fun z => decide (rowOK f (expand a z) = rowOK r z)) (localAssignments s))

theorem factorCheck_exact {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (f : RowFactor n) (r : RowFactor m) (s : List (Fin m))
    (h : factorCheck cap a f r s = true) (z : Assignment m) :
    r.scope.map z ∈ r.rows ↔ f.scope.map (expand a z) ∈ f.rows := by
  obtain ⟨_, ht⟩ := and_parts h
  obtain ⟨hc, he⟩ := and_parts ht
  obtain ⟨y, hy, hagree⟩ := localAssignments_complete s z
  have hs : ∀ i ∈ support a f r, y i = z i :=
    fun i hi => hagree i (covered_sound _ _ hc i hi)
  have hf : f.scope.map (expand a y) = f.scope.map (expand a z) := by
    apply map_agree
    intro i hi
    change bxor (a.forms i).rhs (parity y (a.forms i).vars) =
      bxor (a.forms i).rhs (parity z (a.forms i).vars)
    rw [parity_agree _ _ _ (fun j hj =>
      hs j (List.mem_append.mpr (Or.inl (List.mem_flatMap.mpr ⟨i, hi, hj⟩))))]
  have hr : r.scope.map y = r.scope.map z :=
    map_agree _ _ _ (fun i hi => hs i (List.mem_append.mpr (Or.inr hi)))
  have h1 : rowOK f (expand a y) = rowOK f (expand a z) := by
    unfold rowOK
    rw [hf]
  have h2 : rowOK r y = rowOK r z := by
    unfold rowOK
    rw [hr]
  have eq : rowOK f (expand a y) = rowOK r y :=
    of_decide_eq_true (allCheck_sound _ _ he y hy)
  rw [← rowOK_exact r z, ← rowOK_exact f (expand a z), ← h1, ← h2, eq]

theorem factorCheck_rows_bound {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (f : RowFactor n) (r : RowFactor m) (s : List (Fin m))
    (h : factorCheck cap a f r s = true) :
    (localAssignments s).length ≤ 2 ^ cap := by
  have hl : s.length ≤ cap := of_decide_eq_true (and_parts h).1
  rw [localAssignments_count]
  exact Nat.pow_le_pow_right (by decide) hl

def localCheck {n m : Nat} (cap : Nat) (a : AffineMap n m) :
    List (RowFactor n) → List (RowFactor m) → List (List (Fin m)) → Bool
  | [], [], [] => true
  | f :: fs, r :: rs, s :: ss => factorCheck cap a f r s && localCheck cap a fs rs ss
  | _, _, _ => false

theorem tableModels_cons {m : Nat} (f : RowFactor m) (fs : List (RowFactor m))
    (z : Assignment m) :
    TableModels (f :: fs) z ↔ f.scope.map z ∈ f.rows ∧ TableModels fs z := by
  constructor
  · intro h
    exact ⟨h f (by simp), fun g hg => h g (List.mem_cons.mpr (Or.inr hg))⟩
  · rintro ⟨hf, ht⟩ g hg
    rcases List.mem_cons.mp hg with eq | hm
    · subst g
      exact hf
    · exact ht g hm

theorem localCheck_exact {n m : Nat} (cap : Nat) (a : AffineMap n m)
    (fs : List (RowFactor n)) (rs : List (RowFactor m)) (ss : List (List (Fin m)))
    (h : localCheck cap a fs rs ss = true) (z : Assignment m) :
    TableModels rs z ↔ TableModels fs (expand a z) := by
  induction fs generalizing rs ss with
  | nil =>
    cases rs <;> cases ss <;> simp [localCheck] at h
    simp [TableModels]
  | cons f fs ih =>
    cases rs with
    | nil => cases ss <;> simp [localCheck] at h
    | cons r rs =>
      cases ss with
      | nil => simp [localCheck] at h
      | cons s ss =>
        obtain ⟨hf, ht⟩ := and_parts h
        rw [tableModels_cons, tableModels_cons, factorCheck_exact cap a f r s hf z,
          ih rs ss ht]

theorem local_reduction_exact {n m : Nat} (cap : Nat)
    (fs out : List (RowFactor n)) (steps : List Nat)
    (hr : relationalReplay fs steps = some out) (a : AffineMap n m)
    (ha : affineMapCheck out a = true) (rs : List (RowFactor m))
    (ss : List (List (Fin m))) (hc : localCheck cap a out rs ss = true) :
    (∃ x, TableModels fs x) ↔ (∃ z, TableModels rs z) := by
  constructor
  · rintro ⟨x, hx⟩
    have hm := (relationalReplay_exact fs out steps hr x).mpr hx
    refine ⟨project a x, (localCheck_exact cap a out rs ss hc _).mpr ?_⟩
    rw [affineMap_reconstruct out a ha x hm]
    exact hm
  · rintro ⟨z, hz⟩
    exact ⟨expand a z, (relationalReplay_exact fs out steps hr _).mp
      ((localCheck_exact cap a out rs ss hc z).mp hz)⟩

-- Independent fail-closed alternative for the reduced-Hall release only.
-- No global assignment enumeration occurs in this gate.
def localHall {n m : Nat} (cap : Nat) (fs : List (RowFactor n))
    (steps : List Nat) (a : AffineMap n m) (rs : List (RowFactor m))
    (ss : List (List (Fin m))) (p : Packet m) : Verdict n :=
  match relationalReplay fs steps with
  | none => .unknown
  | some out =>
    if affineMapCheck out a && (localCheck cap a out rs ss && packetCheck rs p)
    then .unsat else .unknown

theorem localHall_sound {n m : Nat} (cap : Nat) (fs : List (RowFactor n))
    (steps : List Nat) (a : AffineMap n m) (rs : List (RowFactor m))
    (ss : List (List (Fin m))) (p : Packet m) :
    Sound fs (localHall cap fs steps a rs ss p) := by
  cases hr : relationalReplay fs steps with
  | none => simp [localHall, hr, Sound]
  | some out =>
    cases hg : (affineMapCheck out a && (localCheck cap a out rs ss && packetCheck rs p)) with
    | false => simp [localHall, hr, hg, Sound]
    | true =>
      obtain ⟨ha, ht⟩ := and_parts hg
      obtain ⟨hc, hp⟩ := and_parts ht
      simp only [localHall, hr, hg, if_true, Sound]
      intro hx
      exact packetCheck_sound rs p hp ((local_reduction_exact cap fs out steps hr a ha rs ss hc).mp hx)

#print axioms localAssignments_complete
#print axioms factorCheck_exact
#print axioms factorCheck_rows_bound
#print axioms localCheck_exact
#print axioms local_reduction_exact
#print axioms localHall_sound

end MathOS.F038.LocalMaterialization
