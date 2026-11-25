/-! F034 candidate: explicit structural column-construction visits
for zero-padded comparison and addition. Keep circuit gates separate
from padding visits. One selected construction event per output
column; not an allocation or complete machine-runtime ledger. -/
namespace ProctorPaddingVisits
open ProctorDecimalBitWidth (bitsValue rippleMeter)
open ProctorBinaryPrimitives (rightCols padColumns pad_length borrowMeter
  compareMeter compare_value compare_gates addMeter add_value add_bound add_length
  decimalMeter decimal_value decimal_bound)
open ProctorTerminalPolynomial (mul_mono)

def rightMeter : List Bool → List (Bool × Bool) × Nat
  | [] => ([],0)
  | b::bs => let r := rightMeter bs; ((false,b)::r.1,r.2+1)

def padMeter : List Bool → List Bool → List (Bool × Bool) × Nat
  | [],bs => rightMeter bs
  | a::as,[] => let r := padMeter as []; ((a,false)::r.1,r.2+1)
  | a::as,b::bs => let r := padMeter as bs; ((a,b)::r.1,r.2+1)

theorem right_projection (bs : List Bool) : (rightMeter bs).1=rightCols bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    change (false,b)::(rightMeter bs).1=(false,b)::rightCols bs
    rw [ih]

theorem right_exact (bs : List Bool) : (rightMeter bs).2=(rightMeter bs).1.length := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    change (rightMeter bs).2+1=(rightMeter bs).1.length+1
    rw [ih]

theorem pad_projection (as bs : List Bool) : (padMeter as bs).1=padColumns as bs := by
  induction as generalizing bs with
  | nil => exact right_projection bs
  | cons a as ih =>
    cases bs with
    | nil =>
      change (a,false)::(padMeter as []).1=(a,false)::padColumns as []
      rw [ih []]
    | cons b bs =>
      change (a,b)::(padMeter as bs).1=(a,b)::padColumns as bs
      rw [ih bs]

theorem pad_exact (as bs : List Bool) : (padMeter as bs).2=(padMeter as bs).1.length := by
  induction as generalizing bs with
  | nil => exact right_exact bs
  | cons a as ih =>
    cases bs with
    | nil =>
      change (padMeter as []).2+1=(padMeter as []).1.length+1
      rw [ih []]
    | cons b bs =>
      change (padMeter as bs).2+1=(padMeter as bs).1.length+1
      rw [ih bs]

theorem pad_bound (as bs : List Bool) (w : Nat)
    (ha : as.length≤w) (hb : bs.length≤w) :
    (padMeter as bs).2≤w := by
  rw [pad_exact,pad_projection]
  exact pad_length as bs w ha hb

-- Actual column-builder substitution; pair the original circuit
-- result and gate count with the column construction visit count.
def compareResources (as bs : List Bool) : (Bool × Nat) × Nat :=
  let p := padMeter as bs
  (borrowMeter p.1 false,p.2)

def addResources (as bs : List Bool) : (List Bool × Nat) × Nat :=
  let p := padMeter as bs
  (rippleMeter p.1 false,p.2)

theorem compare_projection (as bs : List Bool) :
    (compareResources as bs).1=compareMeter as bs := by
  change borrowMeter (padMeter as bs).1 false=borrowMeter (padColumns as bs) false
  rw [pad_projection]

theorem add_projection (as bs : List Bool) :
    (addResources as bs).1=addMeter as bs := by
  change rippleMeter (padMeter as bs).1 false=rippleMeter (padColumns as bs) false
  rw [pad_projection]

theorem compare_bounds (as bs : List Bool) (w : Nat)
    (ha : as.length≤w) (hb : bs.length≤w) :
    (compareResources as bs).1.2≤5*w ∧ (compareResources as bs).2≤w := by
  constructor
  · rw [compare_projection]
    exact compare_gates as bs w ha hb
  · exact pad_bound as bs w ha hb

theorem add_bounds (as bs : List Bool) (w : Nat)
    (ha : as.length≤w) (hb : bs.length≤w) :
    (addResources as bs).1.2≤5*w ∧ (addResources as bs).2≤w := by
  constructor
  · rw [add_projection]
    exact add_bound as bs w ha hb
  · exact pad_bound as bs w ha hb

def decimalResources (v d : List Bool) : (List Bool × Nat) × Nat :=
  let s := addResources (false::v) (false::false::false::v)
  let t := addResources s.1.1 d
  ((t.1.1,s.1.2+t.1.2),s.2+t.2)

theorem decimal_projection (v d : List Bool) :
    (decimalResources v d).1=decimalMeter v d := by
  change ((addResources (addResources (false::v) (false::false::false::v)).1.1 d).1.1,
    (addResources (false::v) (false::false::false::v)).1.2+
      (addResources (addResources (false::v) (false::false::false::v)).1.1 d).1.2)=_
  rw [add_projection,add_projection]

theorem decimal_bounds (v d : List Bool) (w : Nat)
    (hv : v.length≤w) (hd : d.length≤4) :
    (decimalResources v d).1.2≤5*(w+3)+5*(w+4) ∧
      (decimalResources v d).2≤(w+3)+(w+4) := by
  constructor
  · rw [decimal_projection]
    exact (decimal_bound v d w hv hd).right
  · have h1 : (false::v).length≤w+3 :=
      Nat.le_trans (Nat.succ_le_succ hv) (Nat.le_add_right (w+1) 2)
    have h3 : (false::false::false::v).length≤w+3 :=
      Nat.succ_le_succ (Nat.succ_le_succ (Nat.succ_le_succ hv))
    have hs : (addResources (false::v) (false::false::false::v)).1.1.length≤w+4 := by
      rw [add_projection]
      exact add_length _ _ (w+3) h1 h3
    have hdc : d.length≤w+4 := Nat.le_trans hd (Nat.le_add_left _ _)
    exact Nat.add_le_add (pad_bound _ _ (w+3) h1 h3) (pad_bound _ _ (w+4) hs hdc)

end ProctorPaddingVisits

#print axioms ProctorPaddingVisits.right_projection
#print axioms ProctorPaddingVisits.right_exact
#print axioms ProctorPaddingVisits.pad_projection
#print axioms ProctorPaddingVisits.pad_exact
#print axioms ProctorPaddingVisits.pad_bound
#print axioms ProctorPaddingVisits.compare_projection
#print axioms ProctorPaddingVisits.add_projection
#print axioms ProctorPaddingVisits.compare_bounds
#print axioms ProctorPaddingVisits.add_bounds
#print axioms ProctorPaddingVisits.decimal_projection
#print axioms ProctorPaddingVisits.decimal_bounds
