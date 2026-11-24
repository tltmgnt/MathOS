import Init

/-! PNP-B006 GF(2) row calculus. Lists use zero padding. -/
namespace ProctorGF2

def bx : Bool → Bool → Bool
  | false, b => b
  | true, b => !b

def addVec : List Bool → List Bool → List Bool
  | [], ys => ys
  | x::xs, [] => x::xs
  | x::xs, y::ys => bx x y :: addVec xs ys

def dot : List Bool → List Bool → Bool
  | [], _ => false
  | _::_, [] => false
  | a::as, x::xs => bx (a && x) (dot as xs)

theorem bx_zero (b : Bool) : bx b false = b := by cases b <;> rfl

theorem bx_cancel (a b c : Bool) (h : bx a b = bx a c) : b = c := by
  cases a <;> cases b <;> cases c <;> first | rfl | exact Bool.noConfusion h

theorem mix (a b x u v : Bool) :
    bx (bx a b && x) (bx u v) = bx (bx (a && x) u) (bx (b && x) v) := by
  cases a <;> cases b <;> cases x <;> cases u <;> cases v <;> rfl

theorem dot_add (a b x : List Bool) :
    dot (addVec a b) x = bx (dot a x) (dot b x) := by
  induction a generalizing b x with
  | nil => rfl
  | cons u us ih =>
    cases b with
    | nil => exact (bx_zero (dot (u::us) x)).symm
    | cons v vs =>
      cases x with
      | nil => rfl
      | cons w ws =>
        exact (congrArg (fun z : Bool => bx (bx u v && w) z) (ih vs ws)).trans
          (mix u v w (dot us ws) (dot vs ws))

structure Row where
  coeff : List Bool
  rhs : Bool

def Sat (r : Row) (x : List Bool) : Prop := dot r.coeff x = r.rhs

def addRow (p r : Row) : Row := ⟨addVec p.coeff r.coeff, bx p.rhs r.rhs⟩

theorem add_sound (p r : Row) (x : List Bool) (hp : Sat p x) (hr : Sat r x) :
    Sat (addRow p r) x :=
  (dot_add p.coeff r.coeff x).trans
    ((congrArg (fun v : Bool => bx v (dot r.coeff x)) hp).trans
      (congrArg (bx p.rhs) hr))

theorem add_reverse (p r : Row) (x : List Bool) (hp : Sat p x)
    (ha : Sat (addRow p r) x) : Sat r x :=
  bx_cancel p.rhs (dot r.coeff x) r.rhs
    ((congrArg (fun v : Bool => bx v (dot r.coeff x)) hp).symm.trans
      ((dot_add p.coeff r.coeff x).symm.trans ha))

theorem row_replace (p r : Row) (x : List Bool) :
    (Sat p x ∧ Sat r x) ↔ (Sat p x ∧ Sat (addRow p r) x) :=
  ⟨fun h => ⟨h.left, add_sound p r x h.left h.right⟩,
   fun h => ⟨h.left, add_reverse p r x h.left h.right⟩⟩

def AllSat : List Row → List Bool → Prop
  | [], _ => True
  | r::rs, x => Sat r x ∧ AllSat rs x

def sumRows : List Row → Row
  | [] => ⟨[], false⟩
  | r::rs => addRow r (sumRows rs)

theorem sum_sound (rs : List Row) (x : List Bool) (h : AllSat rs x) :
    Sat (sumRows rs) x := by
  induction rs with
  | nil => rfl
  | cons r rs ih => exact add_sound r (sumRows rs) x h.left (ih h.right)

theorem selected_sat (orig sel : List Row) (x : List Bool)
    (h : ∀ r, r ∈ orig → Sat r x) (hs : ∀ r, r ∈ sel → r ∈ orig) :
    AllSat sel x := by
  induction sel with
  | nil => exact True.intro
  | cons r rs ih =>
    exact ⟨h r (hs r (List.Mem.head _)),
      ih (fun q hq => hs q (List.Mem.tail _ hq))⟩

inductive ZeroVec : List Bool → Prop where
  | nil : ZeroVec []
  | cons {xs : List Bool} : ZeroVec xs → ZeroVec (false::xs)

theorem zero_dot (a : List Bool) (h : ZeroVec a) (x : List Bool) :
    dot a x = false := by
  induction h generalizing x with
  | nil => rfl
  | cons _ ih =>
    cases x with
    | nil => rfl
    | cons b bs =>
      cases b with
      | false => exact ih bs
      | true => exact ih bs

/-- Soundness of a row-subset inconsistency certificate, with zero padding. -/
theorem certificate_sound (orig sel : List Row)
    (hs : ∀ r, r ∈ sel → r ∈ orig)
    (hz : ZeroVec (sumRows sel).coeff) (hr : (sumRows sel).rhs = true) :
    ¬ (∃ x : List Bool, ∀ r, r ∈ orig → Sat r x) := by
  intro h
  obtain ⟨x, hx⟩ := h
  have e := sum_sound sel x (selected_sat orig sel x hx hs)
  exact Bool.noConfusion ((zero_dot (sumRows sel).coeff hz x).symm.trans (e.trans hr))

def hd : List Bool → Bool
  | [] => false
  | a::_ => a

def tl : List Bool → List Bool
  | [] => []
  | _::as => as

def strip (r : Row) : Row := ⟨tl r.coeff,r.rhs⟩

theorem dot_split (a : List Bool) (b : Bool) (x : List Bool) :
    dot a (b::x) = bx (hd a && b) (dot (tl a) x) := by
  cases a <;> rfl

theorem hd_add (a b : List Bool) : hd (addVec a b) = bx (hd a) (hd b) := by
  cases a with
  | nil => rfl
  | cons u us =>
    cases b with
    | nil => exact (bx_zero u).symm
    | cons v vs => rfl

def clear (p r : Row) : Row :=
  match hd r.coeff with
  | false => r
  | true => addRow p r

theorem clear_head (p r : Row) (hp : hd p.coeff = true) :
    hd (clear p r).coeff = false := by
  cases h : hd r.coeff with
  | false =>
    unfold clear
    rw [h]
  | true =>
    unfold clear
    rw [h]
    exact (hd_add p.coeff r.coeff).trans
      ((congrArg (fun v : Bool => bx v (hd r.coeff)) hp).trans
        (congrArg (bx true) h))

theorem clear_sat (p r : Row) (x : List Bool) (hp : Sat p x) :
    Sat r x ↔ Sat (clear p r) x := by
  cases h : hd r.coeff with
  | false =>
    unfold clear
    rw [h]
  | true =>
    unfold clear
    rw [h]
    exact ⟨fun hr => add_sound p r x hp hr, fun ha => add_reverse p r x hp ha⟩

theorem strip_sat (r : Row) (b : Bool) (x : List Bool)
    (h : hd r.coeff = false) : Sat r (b::x) ↔ Sat (strip r) x := by
  have e : dot r.coeff (b::x) = dot (tl r.coeff) x :=
    (dot_split r.coeff b x).trans (congrArg (fun v : Bool => bx (v && b) (dot (tl r.coeff) x)) h)
  exact ⟨fun hs => e.symm.trans hs, fun hs => e.trans hs⟩

def reduced (p : Row) (rs : List Row) : List Row :=
  rs.map (fun r => strip (clear p r))

theorem reduce_all (p : Row) (rs : List Row) (b : Bool) (x : List Bool)
    (hp : hd p.coeff = true) (hs : Sat p (b::x)) :
    AllSat rs (b::x) ↔ AllSat (reduced p rs) x := by
  induction rs with
  | nil => exact ⟨fun _ => True.intro, fun _ => True.intro⟩
  | cons r rs ih =>
    have e := (clear_sat p r (b::x) hs).trans
      (strip_sat (clear p r) b x (clear_head p r hp))
    exact ⟨fun h => ⟨e.mp h.left, ih.mp h.right⟩,
           fun h => ⟨e.mpr h.left, ih.mpr h.right⟩⟩

theorem bx_solve (a b : Bool) : bx (bx a b) b = a := by
  cases a <;> cases b <;> rfl

def pivotBit (p : Row) (x : List Bool) : Bool := bx p.rhs (dot (tl p.coeff) x)

theorem pivot_sat (p : Row) (x : List Bool) (hp : hd p.coeff = true) :
    Sat p (pivotBit p x :: x) :=
  (dot_split p.coeff (pivotBit p x) x).trans
    ((congrArg (fun v : Bool => bx (v && pivotBit p x) (dot (tl p.coeff) x)) hp).trans
      (bx_solve p.rhs (dot (tl p.coeff) x)))

/-- One full pivot step, including constructive back substitution for every tail. -/
theorem elimination_step (p : Row) (rs : List Row) (x : List Bool)
    (hp : hd p.coeff = true) :
    (∃ b : Bool, Sat p (b::x) ∧ AllSat rs (b::x)) ↔
    AllSat (reduced p rs) x := by
  constructor
  · intro h
    obtain ⟨b,hp',hr⟩ := h
    exact (reduce_all p rs b x hp hp').mp hr
  · intro h
    have hs := pivot_sat p x hp
    exact ⟨pivotBit p x, hs, (reduce_all p rs (pivotBit p x) x hp hs).mpr h⟩

end ProctorGF2
#print axioms ProctorGF2.dot_add
#print axioms ProctorGF2.row_replace
#print axioms ProctorGF2.certificate_sound
#print axioms ProctorGF2.elimination_step
