/-! F013: sequential Boolean-cell primitives and certified output wire format.
Charges are cell reads/writes and Boolean gates, not host list allocation. -/
namespace ProctorGF2

structure CellRun (α : Type) where
  value : α
  steps : Nat

-- The inputs are explicit bit tapes. Each position reads two cells, XORs,
-- and writes one cell. Padding is not performed by this primitive.
def xorCells : List Bool → List Bool → CellRun (List Bool)
  | a::as,b::bs =>
    let r := xorCells as bs
    ⟨bx a b :: r.value,r.steps+4⟩
  | _,_ => ⟨[],0⟩

theorem xorCells_spec (a b : List Bool) (h : a.length = b.length) :
    (xorCells a b).value = addVec a b ∧ (xorCells a b).steps = 4*a.length := by
  induction a generalizing b with
  | nil =>
    cases b with
    | nil => exact ⟨rfl,rfl⟩
    | cons b bs => exact False.elim (Nat.noConfusion h)
  | cons a as ih =>
    cases b with
    | nil => exact False.elim (Nat.noConfusion h)
    | cons b bs =>
      have e := ih bs (Nat.succ.inj h)
      exact ⟨congrArg (List.cons (bx a b)) e.left,by
        change (xorCells as bs).steps+4 = 4*(as.length+1)
        rw [e.right,Nat.mul_add]⟩

-- Two reads, one AND, one XOR per coordinate; a Boolean accumulator.
def dotCells : List Bool → List Bool → CellRun Bool
  | a::as,b::bs =>
    let r := dotCells as bs
    ⟨bx (a && b) r.value,r.steps+4⟩
  | _,_ => ⟨false,0⟩

theorem dotCells_spec (a b : List Bool) (h : a.length = b.length) :
    (dotCells a b).value = dot a b ∧ (dotCells a b).steps = 4*a.length := by
  induction a generalizing b with
  | nil =>
    cases b with
    | nil => exact ⟨rfl,rfl⟩
    | cons b bs => exact False.elim (Nat.noConfusion h)
  | cons a as ih =>
    cases b with
    | nil => exact False.elim (Nat.noConfusion h)
    | cons b bs =>
      have e := ih bs (Nat.succ.inj h)
      exact ⟨congrArg (bx (a && b)) e.left,by
        change (dotCells as bs).steps+4 = 4*(as.length+1)
        rw [e.right,Nat.mul_add]⟩

theorem mask_xor_cells (n a b : Nat) :
    (xorCells (decode n a) (decode n b)).value = decode n (a ^^^ b) ∧
    (xorCells (decode n a) (decode n b)).steps = 4*n := by
  have ha : (decode n a).length = n := decode_length n a 0
  have hb : (decode n b).length = n := decode_length n b 0
  have e := xorCells_spec (decode n a) (decode n b) (ha.trans hb.symm)
  exact ⟨e.left.trans (decode_xor n a b 0).symm,e.right.trans (congrArg (fun k => 4*k) ha)⟩

theorem mask_dot_cells (n a b : Nat) :
    (dotCells (decode n a) (decode n b)).value = parityAt n (a &&& b) 0 ∧
    (dotCells (decode n a) (decode n b)).steps = 4*n := by
  have ha : (decode n a).length = n := decode_length n a 0
  have hb : (decode n b).length = n := decode_length n b 0
  have e := dotCells_spec (decode n a) (decode n b) (ha.trans hb.symm)
  exact ⟨e.left.trans (decode_dot n a b 0),e.right.trans (congrArg (fun k => 4*k) ha)⟩

-- Sequential address access (prefix traversal); no unit-cost random access.
def readCell : Nat → List Bool → CellRun (Option Bool)
  | _,[] => ⟨none,0⟩
  | 0,b::_ => ⟨some b,1⟩
  | i+1,_::bs => let r := readCell i bs; ⟨r.value,r.steps+1⟩

def writeCell (v : Bool) : Nat → List Bool → CellRun (Option (List Bool))
  | _,[] => ⟨none,0⟩
  | 0,_::bs => ⟨some (v::bs),2⟩
  | i+1,b::bs =>
    let r := writeCell v i bs
    ⟨r.value.map (List.cons b),r.steps+2⟩

theorem readCell_at (pre post : List Bool) (b : Bool) :
    (readCell pre.length (pre++b::post)).value = some b ∧
    (readCell pre.length (pre++b::post)).steps = pre.length+1 := by
  induction pre with
  | nil => exact ⟨rfl,rfl⟩
  | cons a pre ih =>
    exact ⟨ih.left,congrArg Nat.succ ih.right⟩

theorem writeCell_at (pre post : List Bool) (b v : Bool) :
    (writeCell v pre.length (pre++b::post)).value = some (pre++v::post) ∧
    (writeCell v pre.length (pre++b::post)).steps = 2*(pre.length+1) := by
  induction pre with
  | nil => exact ⟨rfl,rfl⟩
  | cons a pre ih =>
    constructor
    · change (writeCell v pre.length (pre++b::post)).value.map (List.cons a) = _
      rw [ih.left]
      rfl
    · change (writeCell v pre.length (pre++b::post)).steps+2 = 2*(pre.length+1+1)
      rw [ih.right,Nat.mul_add]
      rfl

-- Joint coefficient, rhs and provenance XOR on already materialized cells.
def taggedCells (n m a b u v : Nat) (p r : Bool) :
    CellRun (List Bool × Bool × List Bool) :=
  let c := xorCells (decode n a) (decode n b)
  let w := xorCells (decode m u) (decode m v)
  ⟨(c.value,bx p r,w.value),c.steps+w.steps+4⟩

theorem taggedCells_spec (n m a b u v : Nat) (p r : Bool) :
    (taggedCells n m a b u v p r).value = (decode n (a ^^^ b),bx p r,decode m (u ^^^ v)) ∧
    (taggedCells n m a b u v p r).steps = 4*(n+m+1) := by
  have c := mask_xor_cells n a b
  have w := mask_xor_cells m u v
  unfold taggedCells
  constructor
  · change ((xorCells (decode n a) (decode n b)).value,bx p r,(xorCells (decode m u) (decode m v)).value) = _
    rw [c.left,w.left]
  · change (xorCells (decode n a) (decode n b)).steps+
      (xorCells (decode m u) (decode m v)).steps+4 = _
    rw [c.right,w.right]
    omega

-- A bound for these arithmetic events, not for all solver instructions.
def arithmeticCellBudget (n : Nat) {orig : List MRow} (s : CostRun n orig) : Nat :=
  4*s.collisions*(n+orig.length+1)+4*s.evaluations*n

theorem arithmetic_budget_bound (n : Nat) (orig : List MRow) (hw : InWidth n orig) :
    arithmeticCellBudget n (costSolve n orig hw) ≤
      4*(orig.length*n)*(n+orig.length+1)+4*n*n := by
  let s := costSolve n orig hw
  change 4*s.collisions*(n+orig.length+1)+4*s.evaluations*n ≤ _
  have c := Nat.mul_le_mul_right (n+orig.length+1) (Nat.mul_le_mul_left 4 s.collisions_bound)
  have d := Nat.mul_le_mul_right n (Nat.mul_le_mul_left 4 s.evaluations_bound)
  exact Nat.add_le_add c d

def copyCells : List Bool → CellRun (List Bool)
  | [] => ⟨[],0⟩
  | b::bs =>
    let r := copyCells bs
    ⟨b::r.value,r.steps+2⟩

theorem copyCells_spec (bs : List Bool) :
    (copyCells bs).value = bs ∧ (copyCells bs).steps = 2*bs.length := by
  induction bs with
  | nil => exact ⟨rfl,rfl⟩
  | cons b bs ih =>
    exact ⟨congrArg (List.cons b) ih.left,by
      change (copyCells bs).steps+2 = 2*(bs.length+1)
      rw [ih.right,Nat.mul_add]⟩

end ProctorGF2

namespace ProctorPNP
open ProctorGF2

-- Wire protocol: one tag bit followed by 2n original-variable bits (SAT),
-- or M selection bits (UNSAT). Dimensions are supplied by the instance.
def pairBits : List Pair → List Bool
  | [] => []
  | p::ps => p.1::p.2::pairBits ps

def parsePairs : List Bool → Option (List Pair)
  | [] => some []
  | [_] => none
  | a::b::bs => (parsePairs bs).map (List.cons (a,b))

theorem pair_roundtrip (ps : List Pair) : parsePairs (pairBits ps) = some ps := by
  induction ps with
  | nil => rfl
  | cons p ps ih =>
    cases p with
    | mk a b =>
      change (parsePairs (pairBits ps)).map (List.cons (a,b)) = _
      rw [ih]
      rfl

theorem pairBits_length (ps : List Pair) : (pairBits ps).length = 2*ps.length := by
  induction ps with
  | nil => rfl
  | cons p ps ih =>
    change (pairBits ps).length+1+1 = 2*(ps.length+1)
    rw [ih]
    omega

theorem allowed_length (ds : Domains) (ps : List Pair) (h : Allowed ds ps) :
    ps.length = ds.length := by
  induction h with
  | nil => rfl
  | cons _ _ ih => exact congrArg Nat.succ ih

def payloadBits (ds : Domains) (rs : List MRow) (o : BlockOutput) : List Bool :=
  match o with
  | .sat ps => true :: pairBits ps
  | .unsat w => false :: decode (augmented ds rs).length w

def wireRun (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    CellRun (List Bool) :=
  copyCells (payloadBits ds rs (fullOutput ds rs hw))

def WireValid (ds : Domains) (rs : List MRow) : List Bool → Prop
  | [] => False
  | true::bs => ∃ ps, parsePairs bs = some ps ∧ OriginalSat ds rs ps
  | false::bs => bs.length = (augmented ds rs).length ∧
    MaskProvenance ds.length (augmented ds rs) (0,true) (encodeBits bs) ∧
    ¬ ∃ ps, OriginalSat ds rs ps

theorem wire_valid (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    WireValid ds rs (wireRun ds rs hw).value := by
  unfold wireRun
  rw [(copyCells_spec _).left]
  have h := full_output_spec ds rs hw
  cases e : fullOutput ds rs hw with
  | sat ps =>
    rw [e] at h
    exact ⟨ps,pair_roundtrip ps,h⟩
  | unsat w =>
    rw [e] at h
    change (decode (augmented ds rs).length w).length = (augmented ds rs).length ∧ _
    have r := encode_decode_exact (augmented ds rs).length w h.left
    exact ⟨decode_length _ _ 0,r.symm ▸ h.right.left,h.right.right⟩

theorem wire_length_bound (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    (wireRun ds rs hw).value.length ≤ 2*ds.length+rs.length+1 := by
  unfold wireRun
  rw [(copyCells_spec _).left]
  have h := full_output_spec ds rs hw
  cases e : fullOutput ds rs hw with
  | sat ps =>
    rw [e] at h
    change (pairBits ps).length+1 ≤ _
    rw [pairBits_length,allowed_length ds ps h.left]
    omega
  | unsat w =>
    change (decode (augmented ds rs).length w).length+1 ≤ _
    rw [show (decode (augmented ds rs).length w).length = (augmented ds rs).length from decode_length _ _ 0]
    have := augmented_length ds rs
    omega

theorem wire_copy_bound (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    (wireRun ds rs hw).steps ≤ 2*(2*ds.length+rs.length+1) := by
  have h := wire_length_bound ds rs hw
  unfold wireRun at h ⊢
  rw [(copyCells_spec _).left] at h
  rw [(copyCells_spec _).right]
  exact Nat.mul_le_mul_left 2 h

end ProctorPNP
#print axioms ProctorGF2.xorCells_spec
#print axioms ProctorGF2.dotCells_spec
#print axioms ProctorGF2.mask_xor_cells
#print axioms ProctorGF2.mask_dot_cells
#print axioms ProctorGF2.readCell_at
#print axioms ProctorGF2.writeCell_at
#print axioms ProctorGF2.taggedCells_spec
#print axioms ProctorGF2.arithmetic_budget_bound
#print axioms ProctorGF2.copyCells_spec
#print axioms ProctorPNP.pair_roundtrip
#print axioms ProctorPNP.wire_valid
#print axioms ProctorPNP.wire_length_bound
#print axioms ProctorPNP.wire_copy_bound
