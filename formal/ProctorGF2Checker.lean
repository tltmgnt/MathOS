/-! PNP-F005: executable primal/dual checker for the F004 semantics. -/
namespace ProctorGF2

def weightedRow : List Row → List Bool → Row
  | [], _ => ⟨[],false⟩
  | _::_, [] => ⟨[],false⟩
  | _::rs, false::ws => weightedRow rs ws
  | r::rs, true::ws => addRow r (weightedRow rs ws)

theorem weighted_lhs (rs : List Row) (w x : List Bool) :
    dot (weightedRow rs w).coeff x = lhs rs w x := by
  induction rs generalizing w with
  | nil => exact (dot_nil w).symm
  | cons r rs ih =>
    cases w with
    | nil => rfl
    | cons b ws =>
      cases b with
      | false => exact ih ws
      | true =>
        exact (dot_add r.coeff (weightedRow rs ws).coeff x).trans
          (congrArg (bx (dot r.coeff x)) (ih ws))

theorem weighted_rhs (rs : List Row) (w : List Bool) :
    (weightedRow rs w).rhs = rhs rs w := by
  induction rs generalizing w with
  | nil => exact (dot_nil w).symm
  | cons r rs ih =>
    cases w with
    | nil => rfl
    | cons b ws =>
      cases b with
      | false => exact ih ws
      | true => exact congrArg (bx r.rhs) (ih ws)

def zeroCheck : Nat → List Bool → Bool
  | 0, _ => true
  | _+1, [] => true
  | n+1, false::as => zeroCheck n as
  | _+1, true::_ => false

def zeros : Nat → List Bool
  | 0 => []
  | n+1 => false :: zeros n

theorem zeros_length (n : Nat) : (zeros n).length = n := by
  induction n with
  | zero => rfl
  | succ n ih => exact congrArg Nat.succ ih

theorem dot_zeros (a : List Bool) (n : Nat) : dot a (zeros n) = false := by
  induction n generalizing a with
  | zero => exact dot_nil a
  | succ n ih =>
    cases a with
    | nil => rfl
    | cons b bs =>
      cases b <;> exact ih bs

theorem zeroCheck_sound (n : Nat) (a x : List Bool)
    (hx : x.length = n) (h : zeroCheck n a = true) : dot a x = false := by
  induction n generalizing a x with
  | zero =>
    exact (congrArg (dot a) (empty_of_length_zero x hx)).trans (dot_nil a)
  | succ n ih =>
    cases a with
    | nil => rfl
    | cons b bs =>
      cases b with
      | true => exact False.elim (Bool.noConfusion h)
      | false =>
        cases x with
        | nil => exact False.elim (Nat.noConfusion hx)
        | cons c cs =>
          cases c <;> exact ih bs cs (Nat.succ.inj hx) h

theorem zeroCheck_complete (n : Nat) (a : List Bool)
    (h : ∀ x : List Bool, x.length = n → dot a x = false) :
    zeroCheck n a = true := by
  induction n generalizing a with
  | zero => rfl
  | succ n ih =>
    cases a with
    | nil => rfl
    | cons b bs =>
      cases b with
      | false =>
        exact ih bs (fun x hx => h (false::x) (congrArg Nat.succ hx))
      | true =>
        have e := h (true::zeros n) (congrArg Nat.succ (zeros_length n))
        have f : true = false :=
          (congrArg (bx true) (dot_zeros bs n)).symm.trans e
        exact False.elim (Bool.noConfusion f)

theorem and_left_true (a b : Bool) (h : (a && b) = true) : a = true := by
  cases a <;> cases b <;> first | rfl | exact Bool.noConfusion h
theorem and_right_true (a b : Bool) (h : (a && b) = true) : b = true := by
  cases a <;> cases b <;> first | rfl | exact Bool.noConfusion h
theorem and_both_true (a b : Bool) (ha : a = true) (hb : b = true) :
    (a && b) = true := by
  cases ha
  cases hb
  rfl

def dualCheck (n : Nat) (rs : List Row) (w : List Bool) : Bool :=
  (weightedRow rs w).rhs && zeroCheck n (weightedRow rs w).coeff

theorem dualCheck_iff (n : Nat) (rs : List Row) (w : List Bool) :
    dualCheck n rs w = true ↔
      rhs rs w = true ∧ ∀ x : List Bool, x.length = n → lhs rs w x = false := by
  constructor
  · intro h
    exact ⟨(weighted_rhs rs w).symm.trans (and_left_true _ _ h),
      fun x hx => (weighted_lhs rs w x).symm.trans
        (zeroCheck_sound n (weightedRow rs w).coeff x hx (and_right_true _ _ h))⟩
  · intro h
    exact and_both_true _ _ ((weighted_rhs rs w).trans h.left)
      (zeroCheck_complete n (weightedRow rs w).coeff
        (fun x hx => (weighted_lhs rs w x).trans (h.right x hx)))

def eqBit (a b : Bool) : Bool :=
  match a,b with
  | false,false => true
  | true,true => true
  | _,_ => false

theorem eqBit_iff (a b : Bool) : eqBit a b = true ↔ a = b := by
  cases a <;> cases b <;>
    first
    | exact ⟨fun _ => rfl, fun _ => rfl⟩
    | exact ⟨fun h => Bool.noConfusion h, fun h => Bool.noConfusion h⟩

def rowsCheck (rs : List Row) (x : List Bool) : Bool :=
  match rs with
  | [] => true
  | r::rs => eqBit (dot r.coeff x) r.rhs && rowsCheck rs x

theorem rowsCheck_iff (rs : List Row) (x : List Bool) :
    rowsCheck rs x = true ↔ AllSat rs x := by
  induction rs with
  | nil => exact ⟨fun _ => True.intro,fun _ => rfl⟩
  | cons r rs ih =>
    exact ⟨fun h => ⟨(eqBit_iff _ _).mp (and_left_true _ _ h),ih.mp (and_right_true _ _ h)⟩,
      fun h => and_both_true _ _ ((eqBit_iff _ _).mpr h.left) (ih.mpr h.right)⟩

def widthCheck : Nat → List Bool → Bool
  | 0, [] => true
  | 0, _::_ => false
  | _+1, [] => false
  | n+1, _::xs => widthCheck n xs

theorem widthCheck_iff (n : Nat) (x : List Bool) :
    widthCheck n x = true ↔ x.length = n := by
  induction n generalizing x with
  | zero =>
    cases x with
    | nil => exact ⟨fun _ => rfl,fun _ => rfl⟩
    | cons b bs => exact ⟨fun h => Bool.noConfusion h,fun h => Nat.noConfusion h⟩
  | succ n ih =>
    cases x with
    | nil => exact ⟨fun h => Bool.noConfusion h,fun h => Nat.noConfusion h⟩
    | cons b bs =>
      exact ⟨fun h => congrArg Nat.succ ((ih bs).mp h),fun h => (ih bs).mpr (Nat.succ.inj h)⟩

def primalCheck (n : Nat) (rs : List Row) (x : List Bool) : Bool :=
  widthCheck n x && rowsCheck rs x

theorem primalCheck_iff (n : Nat) (rs : List Row) (x : List Bool) :
    primalCheck n rs x = true ↔ x.length = n ∧ AllSat rs x :=
  ⟨fun h => ⟨(widthCheck_iff n x).mp (and_left_true _ _ h),
    (rowsCheck_iff rs x).mp (and_right_true _ _ h)⟩,
   fun h => and_both_true _ _ ((widthCheck_iff n x).mpr h.left) ((rowsCheck_iff rs x).mpr h.right)⟩

def checkOutput (n : Nat) (rs : List Row) (o : Bool × List Bool) : Bool :=
  match o with
  | (true,x) => primalCheck n rs x
  | (false,w) => dualCheck n rs w

theorem checkOutput_sound (n : Nat) (rs : List Row) (o : Bool × List Bool)
    (h : checkOutput n rs o = true) :
    match o with
    | (true,x) => x.length = n ∧ AllSat rs x
    | (false,_) => ¬ ∃ x : List Bool, x.length = n ∧ AllSat rs x := by
  cases o with
  | mk b v =>
    cases b with
    | true => exact (primalCheck_iff n rs v).mp h
    | false =>
      have d := (dualCheck_iff n rs v).mp h
      exact dual_sound n rs v d.left d.right

theorem generated_accepted (n : Nat) (rs : List Row) :
    checkOutput n rs (certificateOutput n rs) = true := by
  unfold certificateOutput
  cases certify n rs with
  | sat x hx hs => exact (primalCheck_iff n rs x).mpr ⟨hx,hs⟩
  | unsat w hr hl => exact (dualCheck_iff n rs w).mpr ⟨hr,hl⟩

end ProctorGF2
#print axioms ProctorGF2.weighted_lhs
#print axioms ProctorGF2.weighted_rhs
#print axioms ProctorGF2.dualCheck_iff
#print axioms ProctorGF2.primalCheck_iff
#print axioms ProctorGF2.checkOutput_sound
#print axioms ProctorGF2.generated_accepted
