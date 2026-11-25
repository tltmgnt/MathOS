/-! F034: explicit unsigned comparison and decimal shift-add primitives.
Little-endian finite bit lists; zero padding, no truncation.
Only Boolean gate charges, not conversion, allocation or machine costs. -/
namespace ProctorBinaryPrimitives
open ProctorDecimalBitWidth (bitVal bitsValue columnValue rippleMeter ripple_value ripple_length ripple_gates radix digit_step)
open ProctorTerminalPolynomial (mul_mono)

private theorem mul_add_local (n a b : Nat) : n*(a+b)=n*a+n*b := by
  induction b with
  | zero => rfl
  | succ b ih =>
    change n*(a+b)+n=n*a+(n*b+n)
    rw [ih]
    exact Nat.add_assoc _ _ _

private theorem mul_assoc_local (a b c : Nat) : (a*b)*c=a*(b*c) := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change (a*b)*c+a*b=a*(b*c+b)
    rw [ih]
    exact (mul_add_local a (b*c) b).symm

private theorem shuffle_add (a b c d : Nat) :
    (a+b)+(c+d)=(a+c)+(b+d) := by
  calc
    (a+b)+(c+d) = a+(b+(c+d)) := Nat.add_assoc _ _ _
    _ = a+((b+c)+d) := congrArg (fun z => a+z) (Nat.add_assoc _ _ _).symm
    _ = a+((c+b)+d) := congrArg (fun z => a+(z+d)) (Nat.add_comm _ _)
    _ = a+(c+(b+d)) := congrArg (fun z => a+z) (Nat.add_assoc _ _ _)
    _ = (a+c)+(b+d) := (Nat.add_assoc _ _ _).symm

private theorem add_mul_local (a b k : Nat) : (a+b)*k=a*k+b*k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change (a+b)*k+(a+b)=(a*k+a)+(b*k+b)
    rw [ih]
    exact shuffle_add (a*k) (b*k) a b

-- Unsigned subtraction borrow, with one shared NOT, two AND,
-- two OR gates. Final borrow is the unsigned less-than verdict.
def borrowBit (a b c : Bool) : Bool :=
  let na := !a
  (na && b) || ((na || b) && c)

private theorem low_no (x y u v : Nat) (hu : u≤1) (hv : v≤u) :
    (2*x+u<2*y+v) ↔ x<y := by
  constructor
  · intro h
    apply Nat.lt_of_not_ge
    intro ge
    exact Nat.not_lt_of_ge (Nat.add_le_add (mul_mono (Nat.le_refl 2) ge) hv) h
  · intro h
    change (2*x+u)+1≤2*y+v
    calc
      (2*x+u)+1 = 2*x+(u+1) := Nat.add_assoc _ _ _
      _ ≤ 2*x+2 := Nat.add_le_add (Nat.le_refl _) (Nat.succ_le_succ hu)
      _ = 2*(x+1) := rfl
      _ ≤ 2*y := mul_mono (Nat.le_refl 2) h
      _ ≤ 2*y+v := Nat.le_add_right _ _

private theorem low_yes (x y u v : Nat) (hu : u<v) (hv : v≤2) :
    (2*x+u<2*y+v) ↔ x<y+1 := by
  constructor
  · intro h
    apply Nat.lt_of_not_ge
    intro ge
    have bad : 2*y+v≤2*x+u := calc
      2*y+v ≤ 2*y+2 := Nat.add_le_add (Nat.le_refl _) hv
      _ = 2*(y+1) := rfl
      _ ≤ 2*x := mul_mono (Nat.le_refl 2) ge
      _ ≤ 2*x+u := Nat.le_add_right _ _
    exact Nat.not_lt_of_ge bad h
  · intro h
    change (2*x+u)+1≤2*y+v
    calc
      (2*x+u)+1 = 2*x+(u+1) := Nat.add_assoc _ _ _
      _ ≤ 2*y+v := Nat.add_le_add
        (mul_mono (Nat.le_refl 2) (Nat.le_of_succ_le_succ h)) hu

theorem borrow_step (a b c : Bool) (x y : Nat) :
    (2*x+bitVal a < 2*y+bitVal b+bitVal c) ↔
      x<y+bitVal (borrowBit a b c) := by
  rw [Nat.add_assoc (2*y)]
  cases a <;> cases b <;> cases c
  · exact low_no x y 0 0 (by decide) (by decide)
  · exact low_yes x y 0 1 (by decide) (by decide)
  · exact low_yes x y 0 1 (by decide) (by decide)
  · exact low_yes x y 0 2 (by decide) (by decide)
  · exact low_no x y 1 0 (by decide) (by decide)
  · exact low_no x y 1 1 (by decide) (by decide)
  · exact low_no x y 1 1 (by decide) (by decide)
  · exact low_yes x y 1 2 (by decide) (by decide)

def leftValue : List (Bool × Bool) → Nat
  | [] => 0
  | (a,_)::xs => 2*leftValue xs+bitVal a

def rightValue : List (Bool × Bool) → Nat
  | [] => 0
  | (_,b)::xs => 2*rightValue xs+bitVal b

def borrowMeter : List (Bool × Bool) → Bool → Bool × Nat
  | [],c => (c,0)
  | (a,b)::xs,c =>
    let r := borrowMeter xs (borrowBit a b c)
    (r.1,r.2+5)

theorem borrow_value (xs : List (Bool × Bool)) (c : Bool) :
    (borrowMeter xs c).1=true ↔ leftValue xs<rightValue xs+bitVal c := by
  induction xs generalizing c with
  | nil =>
    cases c
    · exact ⟨fun h => Bool.noConfusion h,fun h => False.elim (Nat.not_lt_zero _ h)⟩
    · exact ⟨fun _ => Nat.le_refl 1,fun _ => rfl⟩
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      change (borrowMeter xs (borrowBit a b c)).1=true ↔
        2*leftValue xs+bitVal a<2*rightValue xs+bitVal b+bitVal c
      exact (ih (borrowBit a b c)).trans
        (borrow_step a b c (leftValue xs) (rightValue xs)).symm

theorem borrow_gates (xs : List (Bool × Bool)) (c : Bool) :
    (borrowMeter xs c).2=5*xs.length := by
  induction xs generalizing c with
  | nil => rfl
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      change (borrowMeter xs (borrowBit a b c)).2+5=5*xs.length+5
      rw [ih]

theorem column_sum (xs : List (Bool × Bool)) :
    columnValue xs=leftValue xs+rightValue xs := by
  induction xs with
  | nil => rfl
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      change (bitVal a+bitVal b)+2*columnValue xs=
        (2*leftValue xs+bitVal a)+(2*rightValue xs+bitVal b)
      rw [ih,mul_add_local]
      calc
        (bitVal a+bitVal b)+(2*leftValue xs+2*rightValue xs) =
          (bitVal a+2*leftValue xs)+(bitVal b+2*rightValue xs) :=
            shuffle_add _ _ _ _
        _ = (2*leftValue xs+bitVal a)+(bitVal b+2*rightValue xs) :=
          congrArg (fun n => n+(bitVal b+2*rightValue xs)) (Nat.add_comm _ _)
        _ = (2*leftValue xs+bitVal a)+(2*rightValue xs+bitVal b) :=
          congrArg (fun n => (2*leftValue xs+bitVal a)+n) (Nat.add_comm _ _)

def rightCols : List Bool → List (Bool × Bool)
  | [] => []
  | b::bs => (false,b)::rightCols bs

def padColumns : List Bool → List Bool → List (Bool × Bool)
  | [],bs => rightCols bs
  | a::as,[] => (a,false)::padColumns as []
  | a::as,b::bs => (a,b)::padColumns as bs

private theorem right_values (bs : List Bool) :
    leftValue (rightCols bs)=0 ∧ rightValue (rightCols bs)=bitsValue bs := by
  induction bs with
  | nil => exact ⟨rfl,rfl⟩
  | cons b bs ih =>
    constructor
    · change 2*leftValue (rightCols bs)+0=0
      rw [ih.left] <;> rfl
    · change 2*rightValue (rightCols bs)+bitVal b=bitVal b+2*bitsValue bs
      rw [ih.right]
      exact Nat.add_comm _ _

theorem pad_values (as bs : List Bool) :
    leftValue (padColumns as bs)=bitsValue as ∧
      rightValue (padColumns as bs)=bitsValue bs := by
  induction as generalizing bs with
  | nil => exact right_values bs
  | cons a as ih =>
    cases bs with
    | nil =>
      have h := ih []
      constructor
      · change 2*leftValue (padColumns as [])+bitVal a=bitVal a+2*bitsValue as
        rw [h.left]
        exact Nat.add_comm _ _
      · change 2*rightValue (padColumns as [])+0=0
        rw [h.right] <;> rfl
    | cons b bs =>
      have h := ih bs
      constructor
      · change 2*leftValue (padColumns as bs)+bitVal a=bitVal a+2*bitsValue as
        rw [h.left]
        exact Nat.add_comm _ _
      · change 2*rightValue (padColumns as bs)+bitVal b=bitVal b+2*bitsValue bs
        rw [h.right]
        exact Nat.add_comm _ _

private theorem right_length (bs : List Bool) : (rightCols bs).length=bs.length := by
  induction bs with
  | nil => rfl
  | cons b bs ih => exact congrArg Nat.succ ih

theorem pad_length (as bs : List Bool) (K : Nat)
    (ha : as.length≤K) (hb : bs.length≤K) :
    (padColumns as bs).length≤K := by
  induction as generalizing bs K with
  | nil =>
    change (rightCols bs).length≤K
    rw [right_length]
    exact hb
  | cons a as ih =>
    cases K with
    | zero => cases ha
    | succ K =>
      have h := Nat.le_of_succ_le_succ ha
      cases bs with
      | nil =>
        exact Nat.succ_le_succ (ih [] K h (Nat.zero_le _))
      | cons b bs =>
        exact Nat.succ_le_succ (ih bs K h (Nat.le_of_succ_le_succ hb))

def compareMeter (as bs : List Bool) : Bool × Nat :=
  borrowMeter (padColumns as bs) false

theorem compare_value (as bs : List Bool) :
    (compareMeter as bs).1=true ↔ bitsValue as<bitsValue bs := by
  unfold compareMeter
  have h := pad_values as bs
  have e := borrow_value (padColumns as bs) false
  rw [h.left,h.right] at e
  exact e

theorem compare_gates (as bs : List Bool) (K : Nat)
    (ha : as.length≤K) (hb : bs.length≤K) :
    (compareMeter as bs).2≤5*K := by
  unfold compareMeter
  rw [borrow_gates]
  exact mul_mono (Nat.le_refl 5) (pad_length as bs K ha hb)

def addMeter (as bs : List Bool) : List Bool × Nat :=
  rippleMeter (padColumns as bs) false

theorem add_value (as bs : List Bool) :
    bitsValue (addMeter as bs).1=bitsValue as+bitsValue bs := by
  unfold addMeter
  have h := pad_values as bs
  rw [ripple_value,column_sum,h.left,h.right] <;> rfl

theorem add_length (as bs : List Bool) (K : Nat)
    (ha : as.length≤K) (hb : bs.length≤K) :
    (addMeter as bs).1.length≤K+1 := by
  unfold addMeter
  rw [ripple_length]
  exact Nat.succ_le_succ (pad_length as bs K ha hb)

theorem add_bound (as bs : List Bool) (K : Nat)
    (ha : as.length≤K) (hb : bs.length≤K) :
    (addMeter as bs).2≤5*K := by
  unfold addMeter
  rw [ripple_gates]
  exact mul_mono (Nat.le_refl 5) (pad_length as bs K ha hb)

-- Shift wires are not gate charges. Keep every carry bit; no
-- truncation or canonicalization of output representation.
def decimalMeter (v d : List Bool) : List Bool × Nat :=
  let s := addMeter (false::v) (false::false::false::v)
  let t := addMeter s.1 d
  (t.1,s.2+t.2)

private theorem shift_value (v : List Bool) :
    bitsValue (false::v)=2*bitsValue v := Nat.zero_add _

private theorem ten_times (x : Nat) : 2*x+2*(2*(2*x))=10*x := by
  calc
    2*x+2*(2*(2*x)) = 2*x+8*x :=
      congrArg (fun n => 2*x+n)
        ((mul_assoc_local 2 2 (2*x)).symm.trans (mul_assoc_local 4 2 x).symm)
    _ = 10*x := (add_mul_local 2 8 x).symm

theorem decimal_value (v d : List Bool) :
    bitsValue (decimalMeter v d).1=10*bitsValue v+bitsValue d := by
  change bitsValue (addMeter (addMeter (false::v) (false::false::false::v)).1 d).1=_
  rw [add_value,add_value]
  have h : bitsValue (false::false::false::v)=2*(2*(2*bitsValue v)) := by
    calc
      bitsValue (false::false::false::v) = 2*bitsValue (false::false::v) := shift_value _
      _ = 2*(2*bitsValue (false::v)) := congrArg (fun n => 2*n) (shift_value _)
      _ = 2*(2*(2*bitsValue v)) := congrArg (fun n => 2*(2*n)) (shift_value v)
  rw [h,shift_value,ten_times]

theorem decimal_bound (v d : List Bool) (w : Nat)
    (hv : v.length≤w) (hd : d.length≤4) :
    (decimalMeter v d).1.length≤w+5 ∧
      (decimalMeter v d).2≤5*(w+3)+5*(w+4) := by
  have h1 : (false::v).length≤w+3 :=
    Nat.le_trans (Nat.succ_le_succ hv) (Nat.le_add_right (w+1) 2)
  have h3 : (false::false::false::v).length≤w+3 :=
    Nat.succ_le_succ (Nat.succ_le_succ (Nat.succ_le_succ hv))
  let s := addMeter (false::v) (false::false::false::v)
  have hs : s.1.length≤w+4 := add_length _ _ (w+3) h1 h3
  have hsc : s.2≤5*(w+3) := add_bound _ _ (w+3) h1 h3
  have hdc : d.length≤w+4 := Nat.le_trans hd (Nat.le_add_left _ _)
  change (addMeter s.1 d).1.length≤w+5 ∧ s.2+(addMeter s.1 d).2≤_
  exact ⟨add_length _ _ (w+4) hs hdc,
    Nat.add_le_add hsc (add_bound _ _ (w+4) hs hdc)⟩

-- Connect the arithmetic value to the scanner's local invariant;
-- this is not yet a representation conversion or scanner replacement.
theorem decimal_width_invariant (v d : List Bool) (k b : Nat)
    (hv : bitsValue v+1≤radix k) (hd : bitsValue d=b-48) (hi : b≤57) :
    bitsValue (decimalMeter v d).1+1≤radix (k+1) := by
  rw [decimal_value,hd]
  exact digit_step (bitsValue v) k b hv hi

end ProctorBinaryPrimitives

#print axioms ProctorBinaryPrimitives.borrow_step
#print axioms ProctorBinaryPrimitives.borrow_value
#print axioms ProctorBinaryPrimitives.borrow_gates
#print axioms ProctorBinaryPrimitives.column_sum
#print axioms ProctorBinaryPrimitives.pad_values
#print axioms ProctorBinaryPrimitives.pad_length
#print axioms ProctorBinaryPrimitives.compare_value
#print axioms ProctorBinaryPrimitives.compare_gates
#print axioms ProctorBinaryPrimitives.add_value
#print axioms ProctorBinaryPrimitives.add_length
#print axioms ProctorBinaryPrimitives.add_bound
#print axioms ProctorBinaryPrimitives.decimal_value
#print axioms ProctorBinaryPrimitives.decimal_bound
#print axioms ProctorBinaryPrimitives.decimal_width_invariant
