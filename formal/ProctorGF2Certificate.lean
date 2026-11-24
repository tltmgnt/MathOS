/-! PNP-F004: proof-carrying XOR provenance in the F003 list semantics.
Concatenate ProctorGF2.lean, ProctorGF2Solver.lean (without its import), then this file. -/
namespace ProctorGF2

-- A weight list is a zero-padded vector of original-row selection bits.
def lhs (orig : List Row) (w x : List Bool) : Bool :=
  dot w (orig.map (fun r => dot r.coeff x))
def rhs (orig : List Row) (w : List Bool) : Bool :=
  dot w (orig.map Row.rhs)

structure Tagged (orig : List Row) (shift : List Bool → List Bool) where
  row : Row
  weights : List Bool
  lhs_ok : ∀ x, lhs orig weights x = dot row.coeff (shift x)
  rhs_ok : rhs orig weights = row.rhs

theorem bx_false_right (a : Bool) : bx false a = a := rfl

-- Initialize unit provenance, representing missing trailing weights by zero.
def firstTag (r : Row) (rs : List Row) : Tagged (r::rs) id :=
  ⟨r,[true],fun x => (bx_zero (dot r.coeff x)),bx_zero r.rhs⟩

def shiftTag (r : Row) (rs : List Row) (t : Tagged rs id) :
    Tagged (r::rs) id :=
  ⟨t.row,false::t.weights,fun x => t.lhs_ok x,t.rhs_ok⟩

def initialize : (rs : List Row) → List (Tagged rs id)
  | [] => []
  | r::rs => firstTag r rs :: (initialize rs).map (shiftTag r rs)

def plain {orig shift} (ts : List (Tagged orig shift)) : List Row :=
  ts.map Tagged.row

theorem plain_shift (r : Row) (rs : List Row) (ts : List (Tagged rs id)) :
    plain (ts.map (shiftTag r rs)) = plain ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => exact congrArg (List.cons t.row) ih

theorem plain_initialize (rs : List Row) : plain (initialize rs) = rs := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    exact congrArg (List.cons r) ((plain_shift r rs (initialize rs)).trans ih)

def xorTag {orig shift} (p t : Tagged orig shift) : Tagged orig shift :=
  ⟨addRow p.row t.row,addVec p.weights t.weights,
    fun x => (dot_add p.weights t.weights _).trans
      ((congrArg (fun z => bx z (lhs orig t.weights x)) (p.lhs_ok x)).trans
        (congrArg (bx (dot p.row.coeff (shift x))) (t.lhs_ok x))),
    (dot_add p.weights t.weights _).trans
      ((congrArg (fun z => bx z (rhs orig t.weights)) p.rhs_ok).trans
        (congrArg (bx p.row.rhs) t.rhs_ok))⟩

def clearTag {orig shift} (p t : Tagged orig shift) : Tagged orig shift :=
  match hd t.row.coeff with
  | false => t
  | true => xorTag p t

theorem plain_clear {orig shift} (p t : Tagged orig shift) :
    (clearTag p t).row = clear p.row t.row := by
  unfold clearTag clear
  cases hd t.row.coeff <;> rfl

theorem drop_head_zero (a x : List Bool) (h : hd a = false) :
    dot a x = dot (tl a) (tl x) := by
  cases x with
  | nil => exact (dot_nil a).trans (dot_nil (tl a)).symm
  | cons b bs =>
    exact (dot_split a b bs).trans
      (congrArg (fun v : Bool => bx (v && b) (dot (tl a) bs)) h)

def stripTag {orig shift} (t : Tagged orig shift) (h : hd t.row.coeff = false) :
    Tagged orig (fun x => tl (shift x)) :=
  ⟨strip t.row,t.weights,
    fun x => (t.lhs_ok x).trans (drop_head_zero t.row.coeff (shift x) h),
    t.rhs_ok⟩

def clearStrip {orig shift} (p t : Tagged orig shift) (hp : hd p.row.coeff = true) :
    Tagged orig (fun x => tl (shift x)) :=
  stripTag (clearTag p t) ((congrArg (fun r : Row => hd r.coeff) (plain_clear p t)).trans
    (clear_head p.row t.row hp))

theorem plain_reduced {orig shift} (p : Tagged orig shift)
    (hp : hd p.row.coeff = true) (ts : List (Tagged orig shift)) :
    plain (ts.map (fun t => clearStrip p t hp)) = reduced p.row (plain ts) := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    exact (congrArg (fun r : Row => strip r :: plain (ts.map (fun q => clearStrip p q hp)))
      (plain_clear p t)).trans (congrArg (List.cons (strip (clear p.row t.row))) ih)

-- Scan tags, preserving a proof that the raw pivot is in the raw row list.
inductive TScan {orig shift} (ts : List (Tagged orig shift)) : Type where
  | pivot (p : Tagged orig shift) (hm : p.row ∈ plain ts) (hp : hd p.row.coeff = true) : TScan ts
  | none (hz : ∀ r, r ∈ plain ts → hd r.coeff = false) : TScan ts

def scanTags {orig shift} : (ts : List (Tagged orig shift)) → TScan ts
  | [] => .none (fun _ h => nomatch h)
  | t::ts =>
    match h : hd t.row.coeff with
    | true => .pivot t (List.Mem.head _) h
    | false =>
      match scanTags ts with
      | .pivot p hm hp => .pivot p (List.Mem.tail _ hm) hp
      | .none hz => .none (fun r hr => by
          cases hr with
          | head => exact h
          | tail _ ht => exact hz r ht)

def stripTags {orig shift} : (ts : List (Tagged orig shift)) →
    (∀ r, r ∈ plain ts → hd r.coeff = false) → List (Tagged orig (fun x => tl (shift x)))
  | [], _ => []
  | t::ts, hz => stripTag t (hz t.row (List.Mem.head _)) ::
      stripTags ts (fun r hr => hz r (List.Mem.tail _ hr))

theorem plain_stripped {orig shift} (ts : List (Tagged orig shift))
    (hz : ∀ r, r ∈ plain ts → hd r.coeff = false) :
    plain (stripTags ts hz) = (plain ts).map strip := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    exact congrArg (List.cons (strip t.row)) (ih (fun r hr => hz r (List.Mem.tail _ hr)))

theorem tl_length (x : List Bool) (n : Nat) (h : x.length = n+1) :
    (tl x).length = n := by
  cases x with
  | nil => exact False.elim (Nat.noConfusion h)
  | cons b bs => exact Nat.succ.inj h

theorem empty_of_length_zero (x : List Bool) (h : x.length = 0) : x = [] := by
  cases x with
  | nil => rfl
  | cons b bs => exact False.elim (Nat.noConfusion h)

-- The semantic dual identity is tested on *every* assignment of the declared width.
-- It is equivalent to zero in every column of lambda^T A.
inductive CertResult (orig : List Row) (shift : List Bool → List Bool)
    (n : Nat) (ts : List (Tagged orig shift)) : Type where
  | sat (x : List Bool) (hx : x.length = n) (hs : AllSat (plain ts) x) : CertResult orig shift n ts
  | unsat (w : List Bool) (hr : rhs orig w = true)
      (hl : ∀ x, (shift x).length = n → lhs orig w x = false) : CertResult orig shift n ts

def certBase {orig shift} : (ts : List (Tagged orig shift)) → CertResult orig shift 0 ts
  | [] => .sat [] rfl True.intro
  | t::ts =>
    match h : t.row.rhs with
    | true => .unsat t.weights (t.rhs_ok.trans h) (fun x hx =>
        (t.lhs_ok x).trans ((congrArg (dot t.row.coeff)
          (empty_of_length_zero (shift x) hx)).trans (dot_nil t.row.coeff)))
    | false =>
      match certBase ts with
      | .sat x hx hs =>
        .sat x hx ⟨(congrArg (dot t.row.coeff) (empty_of_length_zero x hx)).trans
          ((dot_nil t.row.coeff).trans h.symm),hs⟩
      | .unsat w hr hl => .unsat w hr hl

def solveCert (orig : List Row) :
    (n : Nat) → (shift : List Bool → List Bool) →
    (ts : List (Tagged orig shift)) → CertResult orig shift n ts
  | 0, _, ts => certBase ts
  | n+1, shift, ts =>
    match scanTags ts with
    | .none hz =>
      match solveCert orig n (fun x => tl (shift x)) (stripTags ts hz) with
      | .sat x hx hs =>
        .sat (false::x) (congrArg Nat.succ hx)
          ((strip_all (plain ts) false x hz).mpr
            ((plain_stripped ts hz) ▸ hs))
      | .unsat w hr hl => .unsat w hr (fun x hx => hl x (tl_length (shift x) n hx))
    | .pivot p _ hp =>
      match solveCert orig n (fun x => tl (shift x)) (ts.map (fun t => clearStrip p t hp)) with
      | .sat x hx hs =>
        .sat (pivotBit p.row x :: x) (congrArg Nat.succ hx)
          ((reduce_all p.row (plain ts) (pivotBit p.row x) x hp (pivot_sat p.row x hp)).mpr
            ((plain_reduced p hp ts) ▸ hs))
      | .unsat w hr hl => .unsat w hr (fun x hx => hl x (tl_length (shift x) n hx))

inductive Certified (n : Nat) (orig : List Row) : Type where
  | sat (x : List Bool) (hx : x.length = n) (hs : AllSat orig x) : Certified n orig
  | unsat (w : List Bool) (hr : rhs orig w = true)
      (hl : ∀ x, x.length = n → lhs orig w x = false) : Certified n orig

def certify (n : Nat) (orig : List Row) : Certified n orig :=
  match solveCert orig n id (initialize orig) with
  | .sat x hx hs => .sat x hx ((plain_initialize orig) ▸ hs)
  | .unsat w hr hl => .unsat w hr hl

-- Independent certificate soundness, requiring only original rows and weights.
theorem values_match (orig : List Row) (x : List Bool) (hs : AllSat orig x) :
    orig.map (fun r => dot r.coeff x) = orig.map Row.rhs := by
  induction orig with
  | nil => rfl
  | cons r rs ih =>
    exact (congrArg (fun b : Bool => b :: rs.map (fun r => dot r.coeff x)) hs.left).trans
      (congrArg (List.cons r.rhs) (ih hs.right))

theorem dual_sound (n : Nat) (orig : List Row) (w : List Bool)
    (hr : rhs orig w = true) (hl : ∀ x, x.length = n → lhs orig w x = false) :
    ¬ ∃ x : List Bool, x.length = n ∧ AllSat orig x := by
  intro hex
  obtain ⟨x,hx,hs⟩ := hex
  exact Bool.noConfusion ((hl x hx).symm.trans
    ((congrArg (dot w) (values_match orig x hs)).trans hr))

-- Constructive alternative: a primal witness or a dual certificate, never both.
theorem dual_complete (n : Nat) (orig : List Row)
    (hn : ¬ ∃ x : List Bool, x.length = n ∧ AllSat orig x) :
    ∃ w : List Bool, rhs orig w = true ∧ ∀ x, x.length = n → lhs orig w x = false := by
  cases certify n orig with
  | sat x hx hs => exact False.elim (hn ⟨x,hx,hs⟩)
  | unsat w hr hl => exact ⟨w,hr,hl⟩

def certificateOutput (n : Nat) (orig : List Row) : Bool × List Bool :=
  match certify n orig with
  | .sat x _ _ => (true,x)
  | .unsat w _ _ => (false,w)

#eval certificateOutput 0 [⟨[],true⟩]
#eval certificateOutput 2 [⟨[true,true],true⟩,⟨[true,true],false⟩]
#eval certificateOutput 2 [⟨[true,false],true⟩,⟨[false,true],true⟩,⟨[true,true],true⟩]
#eval certificateOutput 2 [⟨[true,false],true⟩,⟨[false,true],true⟩]

end ProctorGF2
#print axioms ProctorGF2.certify
#print axioms ProctorGF2.dual_sound
#print axioms ProctorGF2.dual_complete
