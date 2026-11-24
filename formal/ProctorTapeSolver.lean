/-! F014: complete coordinate-order affine solver on explicit Boolean lists.
Cell charges count the specified scans, gates, writes and list transitions;
not a finite-state Turing machine or host runtime simulation. -/
namespace ProctorGF2

def ExactRows (n : Nat) : List Row → Prop
  | [] => True
  | r::rs => r.coeff.length = n ∧ ExactRows n rs

structure TapeTag (orig : List Row) (shift : List Bool → List Bool) (n : Nat) where
  tag : Tagged orig shift
  coeffWidth : tag.row.coeff.length = n
  weightWidth : tag.weights.length = orig.length

def rawTape {orig shift n} (ts : List (TapeTag orig shift n)) : List Row :=
  ts.map (fun t => t.tag.row)

theorem zeros_left (n : Nat) (xs : List Bool) : dot (zeros n) xs = false := by
  induction n generalizing xs with
  | zero => rfl
  | succ n ih =>
    cases xs with
    | nil => rfl
    | cons b bs => cases b <;> exact ih bs

def fullFirst (n : Nat) (r : Row) (rs : List Row) (h : r.coeff.length = n) :
    TapeTag (r::rs) id n :=
  ⟨⟨r,true::zeros rs.length,fun x => by
      change bx (dot r.coeff x) (dot (zeros rs.length) (rs.map (fun q => dot q.coeff x))) = dot r.coeff x
      rw [zeros_left,bx_zero],
    by
      change bx r.rhs (dot (zeros rs.length) (rs.map Row.rhs)) = r.rhs
      rw [zeros_left,bx_zero]⟩,h,congrArg Nat.succ (zeros_length rs.length)⟩

def fullShift {n} (r : Row) (rs : List Row) (t : TapeTag rs id n) :
    TapeTag (r::rs) id n :=
  ⟨shiftTag r rs t.tag,t.coeffWidth,congrArg Nat.succ t.weightWidth⟩

theorem raw_fullShift {n} (r : Row) (rs : List Row) (ts : List (TapeTag rs id n)) :
    rawTape (ts.map (fullShift r rs)) = rawTape ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => exact congrArg (List.cons t.tag.row) ih

structure TapeInit (n : Nat) (rs : List Row) where
  tags : List (TapeTag rs id n)
  same : rawTape tags = rs
  size : tags.length = rs.length
  steps : Nat
  bound : steps ≤ 4*rs.length*rs.length+4*rs.length

-- One full-width unit row per input. Count construction of the first unit
-- tape and the prefixing pass over all tail tags.
def initTape (n : Nat) : (rs : List Row) → ExactRows n rs → TapeInit n rs
  | [], _ => ⟨[],rfl,rfl,0,Nat.le_refl 0⟩
  | r::rs, h => by
    let a := initTape n rs h.right
    exact ⟨fullFirst n r rs h.left :: a.tags.map (fullShift r rs),
      congrArg (List.cons r) ((raw_fullShift r rs a.tags).trans a.same),
      by simp only [List.length_cons,List.length_map,a.size],
      a.steps+4*rs.length+4,by
        have hb := a.bound
        simp only [List.length_cons,Nat.add_mul,Nat.mul_add,Nat.one_mul,Nat.mul_one]
        omega⟩

theorem xorCells_length (a b : List Bool) (h : a.length = b.length) :
    (xorCells a b).value.length = a.length := by
  induction a generalizing b with
  | nil => rfl
  | cons a as ih =>
    cases b with
    | nil => exact False.elim (Nat.noConfusion h)
    | cons b bs => exact congrArg Nat.succ (ih bs (Nat.succ.inj h))

structure TapeXor {orig shift n} (p t : TapeTag orig shift n) where
  value : TapeTag orig shift n
  row_eq : value.tag.row = addRow p.tag.row t.tag.row
  steps : Nat
  exact_cost : steps = 4*(n+orig.length+1)

def tapeXor {orig shift n} (p t : TapeTag orig shift n) : TapeXor p t := by
  let c := xorCells p.tag.row.coeff t.tag.row.coeff
  let w := xorCells p.tag.weights t.tag.weights
  have hc := xorCells_spec p.tag.row.coeff t.tag.row.coeff (p.coeffWidth.trans t.coeffWidth.symm)
  have hw := xorCells_spec p.tag.weights t.tag.weights (p.weightWidth.trans t.weightWidth.symm)
  let row : Row := ⟨c.value,bx p.tag.row.rhs t.tag.row.rhs⟩
  have er : row = (xorTag p.tag t.tag).row :=
    congrArg (fun a => Row.mk a (bx p.tag.row.rhs t.tag.row.rhs)) hc.left
  have ew : w.value = (xorTag p.tag t.tag).weights := hw.left
  let tag : Tagged orig shift := ⟨row,w.value,fun x => by
    rw [ew,er]; exact (xorTag p.tag t.tag).lhs_ok x,
    by rw [ew,er]; exact (xorTag p.tag t.tag).rhs_ok⟩
  exact ⟨⟨tag,(xorCells_length _ _ (p.coeffWidth.trans t.coeffWidth.symm)).trans p.coeffWidth,
    (xorCells_length _ _ (p.weightWidth.trans t.weightWidth.symm)).trans p.weightWidth⟩,
    er,c.steps+w.steps+4,by
      change (xorCells p.tag.row.coeff t.tag.row.coeff).steps+
        (xorCells p.tag.weights t.tag.weights).steps+4 = _
      rw [hc.right,hw.right,p.coeffWidth,p.weightWidth]
      omega⟩

def tapeStrip {orig shift n} (t : TapeTag orig shift (n+1))
    (h : hd t.tag.row.coeff = false) : TapeTag orig (fun x => tl (shift x)) n :=
  ⟨stripTag t.tag h,tl_length t.tag.row.coeff n t.coeffWidth,t.weightWidth⟩

inductive TapeScan {orig shift n} (ts : List (TapeTag orig shift n)) : Type where
  | pivot (p : TapeTag orig shift n) (hp : hd p.tag.row.coeff = true) : TapeScan ts
  | none (hz : ∀ r, r ∈ rawTape ts → hd r.coeff = false) : TapeScan ts

structure ScanCells {orig shift n} (ts : List (TapeTag orig shift n)) where
  result : TapeScan ts
  steps : Nat
  bound : steps ≤ 2*ts.length

def tapeScan {orig shift n} : (ts : List (TapeTag orig shift n)) → ScanCells ts
  | [] => ⟨.none (fun _ h => nomatch h),0,Nat.le_refl 0⟩
  | t::ts => by
    cases h : hd t.tag.row.coeff with
    | true => exact ⟨.pivot t h,2,by simp only [List.length_cons]; omega⟩
    | false =>
      let a := tapeScan ts
      have hb : a.steps+2 ≤ 2*(t::ts).length := by
        simp only [List.length_cons,Nat.mul_add,Nat.mul_one]
        exact Nat.add_le_add_right a.bound 2
      cases e : a.result with
      | pivot p hp => exact ⟨.pivot p hp,a.steps+2,hb⟩
      | none hz =>
        exact ⟨.none (fun r hr => by
          cases hr with
          | head => exact h
          | tail _ ht => exact hz r ht),a.steps+2,hb⟩

structure TapeUpdate {orig shift n} (p t : TapeTag orig shift (n+1)) where
  value : TapeTag orig (fun x => tl (shift x)) n
  same : value.tag.row = strip (clear p.tag.row t.tag.row)
  steps : Nat
  bound : steps ≤ 4*(n+1+orig.length+1)+4

def tapeUpdate {orig shift n} (p t : TapeTag orig shift (n+1))
    (hp : hd p.tag.row.coeff = true) : TapeUpdate p t := by
  cases h : hd t.tag.row.coeff with
  | false =>
    exact ⟨tapeStrip t h,by change strip t.tag.row = strip (clear p.tag.row t.tag.row); unfold clear; rw [h],
      4,by omega⟩
  | true =>
    let a := tapeXor p t
    have e : a.value.tag.row = clear p.tag.row t.tag.row := by
      unfold clear
      rw [h]
      exact a.row_eq
    have hz : hd a.value.tag.row.coeff = false :=
      (congrArg (fun r : Row => hd r.coeff) e).trans (clear_head p.tag.row t.tag.row hp)
    exact ⟨tapeStrip a.value hz,congrArg strip e,a.steps+4,by rw [a.exact_cost]; exact Nat.le_refl _⟩

structure TapeBatch {orig shift n} (ts : List (TapeTag orig shift (n+1))) (target : List Row) (limit : Nat) where
  tags : List (TapeTag orig (fun x => tl (shift x)) n)
  same : rawTape tags = target
  size : tags.length = ts.length
  steps : Nat
  bound : steps ≤ ts.length*limit

def tapeClearAll {orig shift n} (p : TapeTag orig shift (n+1))
    (hp : hd p.tag.row.coeff = true) :
    (ts : List (TapeTag orig shift (n+1))) →
    TapeBatch ts (reduced p.tag.row (rawTape ts)) (4*(n+1+orig.length+1)+4)
  | [] => ⟨[],rfl,rfl,0,Nat.zero_le _⟩
  | t::ts => by
    let a := tapeUpdate p t hp
    let b := tapeClearAll p hp ts
    exact ⟨a.value::b.tags,
      (congrArg (fun r => r::rawTape b.tags) a.same).trans (congrArg (List.cons (strip (clear p.tag.row t.tag.row))) b.same),
      congrArg Nat.succ b.size,a.steps+b.steps,by
        simp only [List.length_cons,Nat.add_mul,Nat.one_mul]
        have ha := a.bound
        have hb := b.bound
        omega⟩

def tapeStripAll {orig shift n} : (ts : List (TapeTag orig shift (n+1))) →
    (∀ r, r ∈ rawTape ts → hd r.coeff = false) →
    TapeBatch ts ((rawTape ts).map strip) 4
  | [], _ => ⟨[],rfl,rfl,0,Nat.le_refl 0⟩
  | t::ts, hz =>
    let a := tapeStrip t (hz t.tag.row (List.Mem.head _))
    let b := tapeStripAll ts (fun r hr => hz r (List.Mem.tail _ hr))
    ⟨a::b.tags,congrArg (List.cons (strip t.tag.row)) b.same,congrArg Nat.succ b.size,
      4+b.steps,by simp only [List.length_cons,Nat.add_mul,Nat.one_mul]; have := b.bound; omega⟩

inductive TapeResult (orig : List Row) (shift : List Bool → List Bool)
    (n : Nat) (ts : List (TapeTag orig shift n)) : Type where
  | sat (x : List Bool) (hx : x.length = n) (hs : AllSat (rawTape ts) x) : TapeResult orig shift n ts
  | unsat (w : List Bool) (hw : w.length = orig.length) (hr : rhs orig w = true)
      (hl : ∀ x, (shift x).length = n → lhs orig w x = false) : TapeResult orig shift n ts

structure TapeBase {orig shift} (ts : List (TapeTag orig shift 0)) where
  result : TapeResult orig shift 0 ts
  steps : Nat
  bound : steps ≤ 2*ts.length

def tapeBase {orig shift} : (ts : List (TapeTag orig shift 0)) → TapeBase ts
  | [] => ⟨.sat [] rfl True.intro,0,Nat.le_refl 0⟩
  | t::ts => by
    cases h : t.tag.row.rhs with
    | true =>
      exact ⟨.unsat t.tag.weights t.weightWidth (t.tag.rhs_ok.trans h)
        (fun x hx => (t.tag.lhs_ok x).trans ((congrArg (dot t.tag.row.coeff)
          (empty_of_length_zero (shift x) hx)).trans (dot_nil _))),2,by simp only [List.length_cons]; omega⟩
    | false =>
      let a := tapeBase ts
      have hb : a.steps+2 ≤ 2*(t::ts).length := by
        simp only [List.length_cons,Nat.mul_add,Nat.mul_one]
        exact Nat.add_le_add_right a.bound 2
      cases e : a.result with
      | sat x hx hs =>
        exact ⟨.sat x hx ⟨(congrArg (dot t.tag.row.coeff) (empty_of_length_zero x hx)).trans
          ((dot_nil _).trans h.symm),hs⟩,a.steps+2,hb⟩
      | unsat w hw hr hl => exact ⟨.unsat w hw hr hl,a.steps+2,hb⟩

def columnBudget (U M k : Nat) : Nat := k*(4*(U+M+1)+6)+4*U+4
def tapeBudget (U M k n : Nat) : Nat := n*columnBudget U M k + 2*k

structure TapeSolve {orig shift n} (ts : List (TapeTag orig shift n)) (U : Nat) where
  result : TapeResult orig shift n ts
  steps : Nat
  bound : steps ≤ tapeBudget U orig.length ts.length n

-- Count every visited row header, updated row, cell XOR and reconstruction
-- dot product. The common width U is held fixed across recursive calls.
def solveTape (orig : List Row) (U : Nat) :
    (n : Nat) → (shift : List Bool → List Bool) →
    (ts : List (TapeTag orig shift n)) → n ≤ U → TapeSolve ts U
  | 0, _, ts, _ =>
    let a := tapeBase ts
    ⟨a.result,a.steps,by simpa [tapeBudget] using a.bound⟩
  | n+1, shift, ts, hn => by
    let a := tapeScan ts
    have hscan := a.bound
    cases e : a.result with
    | none hz =>
      let b := tapeStripAll ts hz
      let s := solveTape orig U n (fun x => tl (shift x)) b.tags (by omega)
      have hs := s.bound
      rw [b.size] at hs
      have hbatch := b.bound
      have hc : a.steps+b.steps+1 ≤ columnBudget U orig.length ts.length := by
        have hmul := Nat.mul_le_mul_left ts.length (show 6 ≤ 4*(U+orig.length+1)+6 by omega)
        unfold columnBudget
        omega
      have hb : a.steps+b.steps+s.steps+1 ≤ tapeBudget U orig.length ts.length (n+1) := by
        unfold tapeBudget at hs ⊢
        rw [Nat.add_mul,Nat.one_mul]
        omega
      cases se : s.result with
      | sat x hx hsat =>
        exact ⟨.sat (false::x) (congrArg Nat.succ hx)
          ((strip_all (rawTape ts) false x hz).mpr (b.same ▸ hsat)),a.steps+b.steps+s.steps+1,hb⟩
      | unsat w hw hr hl =>
        exact ⟨.unsat w hw hr (fun x hx => hl x (tl_length (shift x) n hx)),
          a.steps+b.steps+s.steps+1,hb⟩
    | pivot p hp =>
      let b := tapeClearAll p hp ts
      let s := solveTape orig U n (fun x => tl (shift x)) b.tags (by omega)
      have hs := s.bound
      rw [b.size] at hs
      have hbatch := b.bound
      have hmul := Nat.mul_le_mul_left ts.length (show 4*(n+1+orig.length+1)+4+2 ≤ 4*(U+orig.length+1)+6 by omega)
      rw [Nat.mul_add] at hmul
      have hc : a.steps+b.steps+4*n+4 ≤ columnBudget U orig.length ts.length := by
        unfold columnBudget
        omega
      cases se : s.result with
      | unsat w hw hr hl =>
        exact ⟨.unsat w hw hr (fun x hx => hl x (tl_length (shift x) n hx)),
          a.steps+b.steps+s.steps+1,by
            unfold tapeBudget at hs ⊢
            rw [Nat.add_mul,Nat.one_mul]
            omega⟩
      | sat x hx hsat =>
        let d := dotCells (tl p.tag.row.coeff) x
        have de := dotCells_spec (tl p.tag.row.coeff) x ((tl_length _ n p.coeffWidth).trans hx.symm)
        let bit := bx p.tag.row.rhs d.value
        have be : bit = pivotBit p.tag.row x := congrArg (bx p.tag.row.rhs) de.left
        have dc : d.steps = 4*n := de.right.trans (congrArg (fun z => 4*z) (tl_length _ n p.coeffWidth))
        have good := (reduce_all p.tag.row (rawTape ts) (pivotBit p.tag.row x) x hp (pivot_sat p.tag.row x hp)).mpr (b.same ▸ hsat)
        exact ⟨.sat (bit::x) (congrArg Nat.succ hx) (be.symm ▸ good),
          a.steps+b.steps+s.steps+d.steps+4,by
            unfold tapeBudget at hs ⊢
            rw [Nat.add_mul,Nat.one_mul,dc]
            omega⟩

structure TapeFinal (n : Nat) (rs : List Row) where
  result : Certified n rs
  steps : Nat
  bound : steps ≤ 4*rs.length*rs.length+4*rs.length+tapeBudget n rs.length rs.length n

def tapeCertify (n : Nat) (rs : List Row) (h : ExactRows n rs) : TapeFinal n rs := by
  let a := initTape n rs h
  let s := solveTape rs n n id a.tags (Nat.le_refl n)
  have hs := s.bound
  rw [a.size] at hs
  have hb := Nat.add_le_add a.bound hs
  cases e : s.result with
  | sat x hx good => exact ⟨.sat x hx (a.same ▸ good),a.steps+s.steps,hb⟩
  | unsat w hw hr hl => exact ⟨.unsat w hr hl,a.steps+s.steps,hb⟩

def tapeOutput (n : Nat) (rs : List Row) (h : ExactRows n rs) : Bool × List Bool :=
  match (tapeCertify n rs h).result with
  | .sat x _ _ => (true,x)
  | .unsat w _ _ => (false,w)

theorem tape_output_valid (n : Nat) (rs : List Row) (h : ExactRows n rs) :
    checkOutput n rs (tapeOutput n rs h) = true := by
  unfold tapeOutput
  cases (tapeCertify n rs h).result with
  | sat x hx hs => exact (primalCheck_iff n rs x).mpr ⟨hx,hs⟩
  | unsat w hr hl => exact (dualCheck_iff n rs w).mpr ⟨hr,hl⟩

theorem tape_cost_bound (n : Nat) (rs : List Row) (h : ExactRows n rs) :
    (tapeCertify n rs h).steps ≤ 4*rs.length*rs.length+4*rs.length+
      tapeBudget n rs.length rs.length n := (tapeCertify n rs h).bound

end ProctorGF2
#print axioms ProctorGF2.initTape
#print axioms ProctorGF2.tapeXor
#print axioms ProctorGF2.tapeScan
#print axioms ProctorGF2.tapeUpdate
#print axioms ProctorGF2.tapeClearAll
#print axioms ProctorGF2.tapeStripAll
#print axioms ProctorGF2.tapeBase
#print axioms ProctorGF2.solveTape
#print axioms ProctorGF2.tapeCertify
#print axioms ProctorGF2.tape_output_valid
#print axioms ProctorGF2.tape_cost_bound
