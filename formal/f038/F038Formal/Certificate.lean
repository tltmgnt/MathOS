import F038Formal

/-! FV-02: executable, finite table / resolution / path / Hall certificate checker.
    This is a typed reference kernel, not yet a refinement proof of the JS checker. -/
namespace MathOS.F038.Cert

open MathOS.F038

structure RowFactor (n : Nat) where
  scope : List (Fin n)
  rows : List (List Bool)

def TableModels {n : Nat} (fs : List (RowFactor n)) (x : Assignment n) : Prop :=
  ∀ f ∈ fs, f.scope.map x ∈ f.rows

def CSat {n : Nat} (x : Assignment n) (c : List (Lit n)) : Prop :=
  ∃ l ∈ c, holds x l

def forbiddenClause {n : Nat} : List (Fin n) → List Bool → List (Lit n)
  | v :: vs, b :: bs => ⟨v, !b⟩ :: forbiddenClause vs bs
  | _, _ => []

theorem row_eq_of_no_clause {n : Nat} (x : Assignment n)
    (scope : List (Fin n)) (row : List Bool)
    (hlen : row.length = scope.length)
    (hn : ¬ CSat x (forbiddenClause scope row)) : scope.map x = row := by
  induction scope generalizing row with
  | nil =>
    cases row with
    | nil => rfl
    | cons b bs => simp at hlen
  | cons v vs ih =>
    cases row with
    | nil => simp at hlen
    | cons b bs =>
      have head : x v = b := by
        by_contra hne
        have hh : holds x (⟨v, !b⟩ : Lit n) := by
          change x v = !b
          cases b <;> cases hx : x v <;> simp_all
        exact hn ⟨_, by simp [forbiddenClause], hh⟩
      have tail : ¬ CSat x (forbiddenClause vs bs) := by
        rintro ⟨l, hl, ht⟩
        exact hn ⟨l, by simp [forbiddenClause, hl], ht⟩
      have len : bs.length = vs.length := by simpa using hlen
      change x v :: vs.map x = b :: bs
      rw [head, ih bs len tail]

theorem forbidden_sound {n : Nat} (x : Assignment n) (f : RowFactor n)
    (row : List Bool) (hlen : row.length = f.scope.length)
    (forbidden : row ∉ f.rows) (accepted : f.scope.map x ∈ f.rows) :
    CSat x (forbiddenClause f.scope row) := by
  classical
  by_contra hn
  rw [row_eq_of_no_clause x f.scope row hlen hn] at accepted
  exact forbidden accepted

def lookup {α : Type} : List α → Nat → Option α
  | [], _ => none
  | a :: _, 0 => some a
  | _ :: as, i+1 => lookup as i

theorem lookup_mem {α : Type} (xs : List α) (i : Nat) (a : α)
    (h : lookup xs i = some a) : a ∈ xs := by
  induction xs generalizing i with
  | nil => simp [lookup] at h
  | cons b bs ih =>
    cases i with
    | zero =>
      have eq : b = a := by simpa [lookup] using h
      subst a
      simp
    | succ j =>
      exact List.mem_cons.mpr (Or.inr (ih j (by simpa [lookup] using h)))

def resolveList {n : Nat} (a b : List (Lit n)) (p : Lit n) : List (Lit n) :=
  a.filter (fun l => decide (l ≠ p)) ++ b.filter (fun l => decide (l ≠ neg p))

theorem resolveList_sound {n : Nat} (x : Assignment n) (a b : List (Lit n))
    (p : Lit n) (ha : CSat x a) (hb : CSat x b) : CSat x (resolveList a b p) := by
  rcases ha with ⟨l, hl, ht⟩
  by_cases eq : l = p
  · subst l
    rcases hb with ⟨q, hq, hqt⟩
    have ne : q ≠ neg p := by
      intro e
      subst q
      exact (neg_holds_iff x p).mp hqt ht
    exact ⟨q, by simp [resolveList, hq, ne], hqt⟩
  · exact ⟨l, by simp [resolveList, hl, eq], ht⟩

inductive RowProof (n : Nat) where
  | source (index : Nat) (row : List Bool)
  | resolution (left right : RowProof n) (pivot : Lit n)

def deriveClause {n : Nat} (fs : List (RowFactor n)) :
    RowProof n → Option (List (Lit n))
  | .source i row =>
    match lookup fs i with
    | none => none
    | some f =>
      if row.length = f.scope.length ∧ row ∉ f.rows then
        some (forbiddenClause f.scope row)
      else none
  | .resolution a b p =>
    match deriveClause fs a, deriveClause fs b with
    | some ca, some cb => some (resolveList ca cb p)
    | _, _ => none

theorem derive_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (p : RowProof n) :
    ∀ c, deriveClause fs p = some c → CSat x c := by
  induction p with
  | source i row =>
    intro c h
    cases hf : lookup fs i with
    | none => simp [deriveClause, hf] at h
    | some f =>
      by_cases hc : row.length = f.scope.length ∧ row ∉ f.rows
      · have eq : forbiddenClause f.scope row = c := by
          simpa [deriveClause, hf, hc] using h
        rw [← eq]
        exact forbidden_sound x f row hc.1 hc.2 (hm f (lookup_mem fs i f hf))
      · simp [deriveClause, hf, hc] at h
  | resolution a b p ia ib =>
    intro c h
    cases ha : deriveClause fs a with
    | none => simp [deriveClause, ha] at h
    | some ca =>
      cases hb : deriveClause fs b with
      | none => simp [deriveClause, ha, hb] at h
      | some cb =>
        have eq : resolveList ca cb p = c := by simpa [deriveClause, ha, hb] using h
        rw [← eq]
        exact resolveList_sound x ca cb p (ia ca ha) (ib cb hb)

-- Explicit finite Boolean folds, with no assignment enumeration in the checker.
def allCheck {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | a :: as => p a && allCheck p as

def anyCheck {α : Type} (p : α → Bool) : List α → Bool
  | [] => false
  | a :: as => p a || anyCheck p as

theorem and_parts {a b : Bool} (h : (a && b) = true) : a = true ∧ b = true := by
  cases a <;> cases b <;> simp_all

theorem or_parts {a b : Bool} (h : (a || b) = true) : a = true ∨ b = true := by
  cases a <;> cases b <;> simp_all

theorem allCheck_sound {α : Type} (p : α → Bool) (xs : List α)
    (h : allCheck p xs = true) (a : α) (ha : a ∈ xs) : p a = true := by
  induction xs with
  | nil => simp at ha
  | cons b bs ih =>
    have hp := and_parts (show (p b && allCheck p bs) = true from h)
    rcases List.mem_cons.mp ha with eq | hm
    · subst a
      exact hp.1
    · exact ih hp.2 hm

theorem anyCheck_sound {α : Type} (p : α → Bool) (xs : List α)
    (h : anyCheck p xs = true) : ∃ a ∈ xs, p a = true := by
  induction xs with
  | nil => simp [anyCheck] at h
  | cons b bs ih =>
    rcases or_parts (show (p b || anyCheck p bs) = true from h) with hb | ht
    · exact ⟨b, by simp, hb⟩
    · obtain ⟨a, ha, hp⟩ := ih ht
      exact ⟨a, List.mem_cons.mpr (Or.inr ha), hp⟩

-- A derived clause can be weakened to the declared target, never strengthened.
def clauseCheck {n : Nat} (fs : List (RowFactor n)) (p : RowProof n)
    (target : List (Lit n)) : Bool :=
  match deriveClause fs p with
  | none => false
  | some c => allCheck (fun l => decide (l ∈ target)) c

theorem clauseCheck_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (p : RowProof n) (target : List (Lit n))
    (h : clauseCheck fs p target = true) : CSat x target := by
  cases hc : deriveClause fs p with
  | none => simp [clauseCheck, hc] at h
  | some c =>
    have hsub : allCheck (fun l => decide (l ∈ target)) c = true := by
      simpa [clauseCheck, hc] using h
    obtain ⟨l, hl, ht⟩ := derive_sound fs x hm p c hc
    exact ⟨l, of_decide_eq_true (allCheck_sound _ _ hsub l hl), ht⟩

abbrev Steps (n : Nat) := List (Lit n × RowProof n)

def pathCheck {n : Nat} (fs : List (RowFactor n)) :
    Lit n → Lit n → Steps n → Bool
  | start, finish, [] => decide (start = finish)
  | start, finish, (next, proof) :: rest =>
    clauseCheck fs proof [neg start, next] && pathCheck fs next finish rest

theorem pathCheck_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (start finish : Lit n) (steps : Steps n)
    (h : pathCheck fs start finish steps = true) (hs : holds x start) :
    holds x finish := by
  induction steps generalizing start with
  | nil =>
    have eq : start = finish := of_decide_eq_true (by simpa only [pathCheck] using h)
    simpa only [← eq] using hs
  | cons step rest ih =>
    obtain ⟨next, proof⟩ := step
    have hp := and_parts (show
      (clauseCheck fs proof [neg start, next] && pathCheck fs next finish rest) = true from h)
    obtain ⟨l, hl, ht⟩ := clauseCheck_sound fs x hm proof [neg start, next] hp.1
    have eq : l = neg start ∨ l = next := by simpa using hl
    have hn : holds x next := by
      rcases eq with e | e
      · subst l
        exact False.elim ((neg_holds_iff x start).mp ht hs)
      · subst l
        exact ht
    exact ih next hp.2 hn

structure Conflict (n : Nat) where
  left : Lit n
  right : Lit n
  steps : Steps n

def conflictCheck {n : Nat} (fs : List (RowFactor n)) (cs : List (Conflict n))
    (a b : Lit n) : Bool :=
  anyCheck (fun c => decide (c.left = a ∧ c.right = b) &&
    pathCheck fs a (neg b) c.steps) cs

theorem conflictCheck_sound {n : Nat} (fs : List (RowFactor n)) (x : Assignment n)
    (hm : TableModels fs x) (cs : List (Conflict n)) (a b : Lit n)
    (h : conflictCheck fs cs a b = true) : ¬ (holds x a ∧ holds x b) := by
  obtain ⟨c, _, hc⟩ := anyCheck_sound _ cs h
  intro ht
  exact (neg_holds_iff x b).mp
    (pathCheck_sound fs x hm a (neg b) c.steps (and_parts hc).2 ht.1) ht.2

structure Group (n : Nat) where
  options : List (Lit n)
  proof : RowProof n

structure HallCert (n : Nat) where
  groupCount : Nat
  holeCount : Nat
  groups : Fin groupCount → Group n
  placements : List (Lit n × Fin holeCount)
  conflicts : List (Conflict n)

def holeOf {n h : Nat} (l : Lit n) : List (Lit n × Fin h) → Option (Fin h)
  | [] => none
  | (a, j) :: rest => if l = a then some j else holeOf l rest

def groupCheck {n : Nat} (fs : List (RowFactor n)) (c : HallCert n)
    (i : Fin c.groupCount) : Bool :=
  clauseCheck fs (c.groups i).proof (c.groups i).options &&
    allCheck (fun l => (holeOf l c.placements).isSome) (c.groups i).options

def pairCheck {n : Nat} (fs : List (RowFactor n)) (c : HallCert n)
    (i j : Fin c.groupCount) : Bool :=
  if i = j then true else
    allCheck (fun a => allCheck (fun b =>
      if holeOf a c.placements = holeOf b c.placements then
        conflictCheck fs c.conflicts a b else true)
      (c.groups j).options) (c.groups i).options

def hallCheck {n : Nat} (fs : List (RowFactor n)) (c : HallCert n) : Bool :=
  decide (c.holeCount < c.groupCount) &&
    (allCheck (groupCheck fs c) (List.finRange c.groupCount) &&
     allCheck (fun i => allCheck (pairCheck fs c i) (List.finRange c.groupCount))
       (List.finRange c.groupCount))

theorem hallCheck_sound {n : Nat} (fs : List (RowFactor n)) (c : HallCert n)
    (h : hallCheck fs c = true) : ¬ ∃ x, TableModels fs x := by
  obtain ⟨hd, hrest⟩ := and_parts (show
    (decide (c.holeCount < c.groupCount) &&
      (allCheck (groupCheck fs c) (List.finRange c.groupCount) &&
        allCheck (fun i => allCheck (pairCheck fs c i) (List.finRange c.groupCount))
          (List.finRange c.groupCount))) = true from h)
  obtain ⟨hg, hp⟩ := and_parts hrest
  rintro ⟨x, hm⟩
  apply hall_deficiency_sound x (fun i => {l | l ∈ (c.groups i).options})
    (fun l => holeOf l c.placements) (of_decide_eq_true hd)
  · intro i
    have hi := allCheck_sound _ _ hg i (by simp)
    have hgroup := and_parts (show
      (clauseCheck fs (c.groups i).proof (c.groups i).options &&
       allCheck (fun l => (holeOf l c.placements).isSome) (c.groups i).options) = true from hi)
    obtain ⟨l, hl, ht⟩ := clauseCheck_sound fs x hm _ _ hgroup.1
    have placed := allCheck_sound _ _ hgroup.2 l hl
    cases he : holeOf l c.placements with
    | none => simp [he] at placed
    | some j => exact ⟨l, j, hl, ht, he⟩
  · intro i j a b ne ha hb same
    have hi := allCheck_sound _ _ hp i (by simp)
    have hij := allCheck_sound _ _ hi j (by simp)
    have check : allCheck (fun a => allCheck (fun b =>
      if holeOf a c.placements = holeOf b c.placements then
        conflictCheck fs c.conflicts a b else true)
      (c.groups j).options) (c.groups i).options = true := by
      simpa [pairCheck, ne] using hij
    have h1 := allCheck_sound _ _ check a ha
    have h2 := allCheck_sound _ _ h1 b hb
    exact conflictCheck_sound fs x hm c.conflicts a b (by simpa [same] using h2)

-- Finite list-backed entry point: raw natural-number hole IDs are checked
-- before constructing the dependent certificate; no modular Fin coercion.
def decodePlacements {n : Nat} (h : Nat) :
    List (Lit n × Nat) → Option (List (Lit n × Fin h))
  | [] => some []
  | (l, j) :: rest =>
    if hj : j < h then
      match decodePlacements h rest with
      | none => none
      | some ps => some ((l, ⟨j, hj⟩) :: ps)
    else none

def hallOfLists {n h : Nat} (gs : List (Group n))
    (ps : List (Lit n × Fin h)) (cs : List (Conflict n)) : HallCert n :=
  { groupCount := gs.length
    holeCount := h
    groups := fun i => gs.get i
    placements := ps
    conflicts := cs }

def checkHallLists {n : Nat} (fs : List (RowFactor n)) (h : Nat)
    (gs : List (Group n)) (ps : List (Lit n × Nat)) (cs : List (Conflict n)) : Bool :=
  match decodePlacements h ps with
  | none => false
  | some placed => hallCheck fs (hallOfLists gs placed cs)

theorem checkHallLists_sound {n : Nat} (fs : List (RowFactor n)) (h : Nat)
    (gs : List (Group n)) (ps : List (Lit n × Nat)) (cs : List (Conflict n))
    (ok : checkHallLists fs h gs ps cs = true) : ¬ ∃ x, TableModels fs x := by
  cases he : decodePlacements h ps with
  | none => simp [checkHallLists, he] at ok
  | some placed =>
    exact hallCheck_sound fs (hallOfLists gs placed cs)
      (by simpa [checkHallLists, he] using ok)

#print axioms forbidden_sound
#print axioms derive_sound
#print axioms clauseCheck_sound
#print axioms pathCheck_sound
#print axioms hallCheck_sound
#print axioms checkHallLists_sound

end MathOS.F038.Cert
