import Init

namespace ProctorGF2

/-- A decidable search result with a proof of pivot membership or zero heads. -/
inductive Scan (rs : List Row) : Type where
  | pivot (p : Row) (member : p ∈ rs) (head : hd p.coeff = true) : Scan rs
  | none (zero : ∀ r, r ∈ rs → hd r.coeff = false) : Scan rs

def scan : (rs : List Row) → Scan rs
  | [] => .none (fun _ h => nomatch h)
  | r::rs =>
    match h : hd r.coeff with
    | true => .pivot r (List.Mem.head _) h
    | false =>
      match scan rs with
      | .pivot p hp ht => .pivot p (List.Mem.tail _ hp) ht
      | .none hz => .none (fun q hq => by
          cases hq with
          | head => exact h
          | tail _ ht => exact hz q ht)

theorem all_member (rs : List Row) (x : List Bool) (h : AllSat rs x)
    (r : Row) (hr : r ∈ rs) : Sat r x := by
  induction rs with
  | nil => cases hr
  | cons p ps ih =>
    cases hr with
    | head => exact h.left
    | tail _ ht => exact ih h.right ht

theorem strip_all (rs : List Row) (b : Bool) (x : List Bool)
    (hz : ∀ r, r ∈ rs → hd r.coeff = false) :
    AllSat rs (b::x) ↔ AllSat (rs.map strip) x := by
  induction rs with
  | nil => exact ⟨fun _ => True.intro, fun _ => True.intro⟩
  | cons r rs ih =>
    have e := strip_sat r b x (hz r (List.Mem.head _))
    have et := ih (fun q hq => hz q (List.Mem.tail _ hq))
    exact ⟨fun h => ⟨e.mp h.left, et.mp h.right⟩,
           fun h => ⟨e.mpr h.left, et.mpr h.right⟩⟩

theorem dot_nil (a : List Bool) : dot a [] = false := by
  cases a <;> rfl

/-- Explicit witness, or a constructive proof that no n-bit witness exists. -/
inductive Result (n : Nat) (rs : List Row) : Type where
  | sat (x : List Bool) (length_ok : x.length = n) (holds : AllSat rs x) : Result n rs
  | unsat (impossible : ¬ ∃ x : List Bool, x.length = n ∧ AllSat rs x) : Result n rs

def baseDecision : (rs : List Row) → Decidable (AllSat rs [])
  | [] => isTrue True.intro
  | r::rs =>
    match h : r.rhs with
    | true => isFalse (fun hs => Bool.noConfusion ((dot_nil r.coeff).symm.trans (hs.left.trans h)))
    | false =>
      match baseDecision rs with
      | isTrue ht => isTrue ⟨(dot_nil r.coeff).trans h.symm, ht⟩
      | isFalse ht => isFalse (fun hs => ht hs.right)

/-- Total recursive solver. n decreases in both branches, no pivot is retained as an assumption. -/
def solve : (n : Nat) → (rs : List Row) → Result n rs
  | 0, rs =>
    match baseDecision rs with
    | isTrue h => .sat [] rfl h
    | isFalse h => .unsat (by
        intro hex
        obtain ⟨x, hx, hs⟩ := hex
        cases x with
        | nil => exact h hs
        | cons b bs => exact Nat.noConfusion hx)
  | n+1, rs =>
    match scan rs with
    | .none hz =>
      match solve n (rs.map strip) with
      | .sat x hx hs =>
        .sat (false::x) (congrArg Nat.succ hx) ((strip_all rs false x hz).mpr hs)
      | .unsat hu => .unsat (by
          intro hex
          obtain ⟨y, hy, hs⟩ := hex
          cases y with
          | nil => exact Nat.noConfusion hy
          | cons b x => exact hu ⟨x, Nat.succ.inj hy, (strip_all rs b x hz).mp hs⟩)
    | .pivot p hm hp =>
      match solve n (reduced p rs) with
      | .sat x hx hs =>
        .sat (pivotBit p x :: x) (congrArg Nat.succ hx)
          ((reduce_all p rs (pivotBit p x) x hp (pivot_sat p x hp)).mpr hs)
      | .unsat hu => .unsat (by
          intro hex
          obtain ⟨y, hy, hs⟩ := hex
          cases y with
          | nil => exact Nat.noConfusion hy
          | cons b x =>
            exact hu ⟨x, Nat.succ.inj hy,
              (reduce_all p rs b x hp (all_member rs (b::x) hs p hm)).mp hs⟩)

/-- An executable interface, with proof fields erased. -/
def witness (n : Nat) (rs : List Row) : Option (List Bool) :=
  match solve n rs with
  | .sat x _ _ => some x
  | .unsat _ => none

theorem witness_spec (n : Nat) (rs : List Row) :
    match witness n rs with
    | some x => x.length = n ∧ AllSat rs x
    | none => ¬ ∃ x : List Bool, x.length = n ∧ AllSat rs x := by
  unfold witness
  cases solve n rs with
  | sat x hx hs => exact ⟨hx,hs⟩
  | unsat hu => exact hu

theorem none_iff (n : Nat) (rs : List Row) :
    witness n rs = none ↔ ¬ ∃ x : List Bool, x.length = n ∧ AllSat rs x := by
  have h := witness_spec n rs
  cases e : witness n rs with
  | none =>
    rw [e] at h
    exact ⟨fun _ => h, fun _ => rfl⟩
  | some x =>
    rw [e] at h
    exact ⟨fun hn => Option.noConfusion hn,
           fun hn => False.elim (hn ⟨x,h.left,h.right⟩)⟩

-- Exact dimension: width-n systems use n-bit assignments; ragged rows use zero padding.
#eval witness 0 []
#eval witness 0 [⟨[],true⟩]
#eval witness 3 [⟨[false,true,false],true⟩]
#eval witness 2 [⟨[true,true],true⟩,⟨[false,true],false⟩]
#eval witness 2 [⟨[true,true],true⟩,⟨[true,true],false⟩]

end ProctorGF2

#print axioms ProctorGF2.scan
#print axioms ProctorGF2.solve
#print axioms ProctorGF2.witness_spec
#print axioms ProctorGF2.none_iff
