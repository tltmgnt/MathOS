/-! F009: proof-carrying highest-pivot basis insertion and reconstruction.
The basis is represented by descending slots, not a Python dictionary. -/
namespace ProctorGF2

abbrev MRow := Nat × Bool

structure MTag (n : Nat) (orig : List MRow) where
  row : MRow
  weight : Nat
  valid : MaskProvenance n orig row weight

def addMTag {n orig} (p r : MTag n orig) : MTag n orig :=
  ⟨maskAdd p.row r.row,p.weight ^^^ r.weight,
    provenance_xor n orig p.row r.row p.weight r.weight p.valid r.valid⟩

inductive HB (n : Nat) (orig : List MRow) : Nat → Type where
  | empty : HB n orig 0
  | vacant {p : Nat} (tail : HB n orig p) : HB n orig (p+1)
  | occupied {p : Nat} (tag : MTag n orig) (hp : Highest tag.row.1 p)
      (tail : HB n orig p) : HB n orig (p+1)

def blank (n : Nat) (orig : List MRow) : (cap : Nat) → HB n orig cap
  | 0 => .empty
  | p+1 => .vacant (blank n orig p)

def holds {n orig cap} (b : HB n orig cap) (x : Nat) : Prop :=
  match b with
  | .empty => True
  | .vacant t => holds t x
  | .occupied r _ t => maskSat n r.row x ∧ holds t x

theorem blank_holds (n : Nat) (orig : List MRow) (cap x : Nat) :
    holds (blank n orig cap) x := by
  induction cap with
  | zero => exact True.intro
  | succ p ih => exact ih

inductive Ins {n orig cap} (b : HB n orig cap) (r : MTag n orig) : Type where
  | bad (w : Nat) (cert : MaskProvenance n orig (0,true) w) : Ins b r
  | ok (next : HB n orig cap)
      (eqv : ∀ x, holds next x ↔ holds b x ∧ maskSat n r.row x) : Ins b r

def insert {n orig} : {cap : Nat} → (b : HB n orig cap) →
    (r : MTag n orig) → r.row.1 < 2^cap → Ins b r
  | 0, .empty, r, h => by
    have hz : r.row.1 = 0 := by omega
    cases e : r.row.2 with
    | true =>
      have he : r.row = (0,true) := Prod.ext hz e
      exact .bad r.weight (he ▸ r.valid)
    | false =>
      exact .ok .empty (fun x => by
        have hs : maskSat n r.row x := (maskSat_iff n r.row x).mp (by
          change dot (decode n r.row.1) (decode n x) = r.row.2
          rw [hz,e]
          exact zero_mask_dot n (decode n x))
        exact ⟨fun _ => ⟨True.intro,hs⟩,fun _ => True.intro⟩)
  | p+1, .vacant t, r, h =>
    if hp : 2^p ≤ r.row.1 then
      .ok (.occupied r ⟨hp,h⟩ t) (fun _ => and_comm)
    else
      match insert t r (Nat.lt_of_not_ge hp) with
      | .bad w c => .bad w c
      | .ok next e => .ok (.vacant next) e
  | p+1, .occupied q hq t, r, h =>
    if hp : 2^p ≤ r.row.1 then
      match insert t (addMTag q r) (highest_descent q.row.1 r.row.1 p hq ⟨hp,h⟩) with
      | .bad w c => .bad w c
      | .ok next e =>
        .ok (.occupied q hq next) (fun x => by
          constructor
          · intro hs
            have et := (e x).mp hs.right
            have er := (mask_replace n q.row r.row x).mpr ⟨hs.left,et.right⟩
            exact ⟨⟨hs.left,et.left⟩,er.right⟩
          · intro hs
            have er := (mask_replace n q.row r.row x).mp ⟨hs.left.left,hs.right⟩
            exact ⟨hs.left.left,(e x).mpr ⟨hs.left.right,er.right⟩⟩)
    else
      match insert t r (Nat.lt_of_not_ge hp) with
      | .bad w c => .bad w c
      | .ok next e =>
        .ok (.occupied q hq next) (fun x => by
          constructor
          · intro hs
            have et := (e x).mp hs.right
            exact ⟨⟨hs.left,et.left⟩,et.right⟩
          · intro hs
            exact ⟨hs.left.left,(e x).mpr ⟨hs.left.right,hs.right⟩⟩)

theorem back_bound (n : Nat) (r : MRow) (x p : Nat) (h : x < 2^p) :
    backStep n r x p < 2^(p+1) := by
  unfold backStep
  split
  · exact Nat.lt_of_lt_of_le h (Nat.pow_le_pow_of_le_right Nat.zero_lt_two (Nat.le_succ p))
  · apply Nat.lt_pow_two_of_testBit
    intro i hi
    have hpi : p ≤ i := by omega
    have hn : p ≠ i := by omega
    rw [Nat.testBit_xor,Nat.testBit_lt_two_pow
      (Nat.lt_of_lt_of_le h (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hpi)),
      Nat.testBit_two_pow_of_ne hn]
    rfl

theorem lower_basis_preserved {n orig cap} (b : HB n orig cap) (r : MRow) (x p : Nat)
    (hc : cap ≤ p) (hp : p < n) :
    holds b (backStep n r x p) ↔ holds b x := by
  induction b with
  | empty => exact Iff.rfl
  | vacant t ih => exact ih (by omega)
  | @occupied j q hq t ih =>
    have hsmall : q.row.1 < 2^p := Nat.lt_of_lt_of_le hq.right
      (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hc)
    have e := (maskSat_iff n q.row (backStep n r x p)).symm.trans
      ((backstep_preserves_lower n r q.row x p hsmall hp).trans (maskSat_iff n q.row x))
    have et := ih (by omega)
    exact ⟨fun h => ⟨e.mp h.left,et.mp h.right⟩,fun h => ⟨e.mpr h.left,et.mpr h.right⟩⟩

structure Reconstructed {n orig cap} (b : HB n orig cap) where
  value : Nat
  bound : value < 2^cap
  good : holds b value

def reconstruct {n orig} : {cap : Nat} → (b : HB n orig cap) → cap ≤ n → Reconstructed b
  | 0, .empty, _ => ⟨0,by decide,True.intro⟩
  | p+1, .vacant t, h =>
    let a := reconstruct t (by omega)
    ⟨a.value,Nat.lt_of_lt_of_le a.bound
      (Nat.pow_le_pow_of_le_right Nat.zero_lt_two (Nat.le_succ p)),a.good⟩
  | p+1, .occupied r hr t, h =>
    let a := reconstruct t (by omega)
    let y := backStep n r.row a.value p
    ⟨y,back_bound n r.row a.value p a.bound,
      ⟨(maskSat_iff n r.row y).mp (backstep_pivot n r.row a.value p hr (by omega)),
       (lower_basis_preserved t r.row a.value p (Nat.le_refl p) (by omega)).mpr a.good⟩⟩

-- Unit provenance is derived from the existing codec and unit-dot theorems.
theorem encoded_at_append (pre post : List Bool) (b : Bool) :
    (encodeBits (pre ++ b::post)).testBit pre.length = b := by
  induction pre with
  | nil => exact encode_head b post
  | cons a pre ih =>
    exact (encode_tail a (pre++b::post) pre.length).trans ih

theorem select_unit (pre post : List Bool) (b : Bool) :
    dot (decode (pre ++ b::post).length (2^pre.length)) (pre++b::post) = b := by
  let xs := pre++b::post
  have h : pre.length < xs.length := by simp [xs]
  have e := unit_dot xs.length (encodeBits xs) pre.length h
  rw [decode_encode] at e
  exact (dot_commute _ _).trans (e.trans (encoded_at_append pre post b))

theorem original_unit (n : Nat) (pre post : List MRow) (r : MRow) :
    MaskProvenance n (pre++r::post) r (2^pre.length) := by
  constructor
  · intro x
    unfold lhs
    simp only [List.map_append,List.map_cons,List.length_append,List.length_cons]
    have e := select_unit
      ((pre.map (maskRow n)).map (fun r : Row => dot r.coeff x))
      ((post.map (maskRow n)).map (fun r : Row => dot r.coeff x))
      (dot (decode n r.1) x)
    simp only [List.length_append,List.length_cons,List.length_map] at e
    exact e.symm
  · unfold rhs
    simp only [List.map_append,List.map_cons,List.length_append,List.length_cons]
    have e := select_unit ((pre.map (maskRow n)).map Row.rhs)
      ((post.map (maskRow n)).map Row.rhs) r.2
    simp only [List.length_append,List.length_cons,List.length_map] at e
    exact e.symm

def MaskAll (n : Nat) (rs : List MRow) (x : Nat) : Prop :=
  match rs with
  | [] => True
  | r::rs => maskSat n r x ∧ MaskAll n rs x

theorem maskAll_iff (n : Nat) (rs : List MRow) (x : Nat) :
    MaskAll n rs x ↔ AllSat (rs.map (maskRow n)) (decode n x) := by
  induction rs with
  | nil => exact Iff.rfl
  | cons r rs ih =>
    have e := (maskSat_iff n r x).symm
    exact ⟨fun h => ⟨e.mp h.left,ih.mp h.right⟩,fun h => ⟨e.mpr h.left,ih.mpr h.right⟩⟩

def InWidth (n : Nat) (rs : List MRow) : Prop :=
  match rs with
  | [] => True
  | r::rs => r.1 < 2^n ∧ InWidth n rs

inductive Fed (n : Nat) (orig : List MRow) (b : HB n orig n) (rs : List MRow) : Type where
  | bad (w : Nat) (cert : MaskProvenance n orig (0,true) w) : Fed n orig b rs
  | ok (next : HB n orig n)
      (eqv : ∀ x, holds next x ↔ holds b x ∧ MaskAll n rs x) : Fed n orig b rs

def feed (n : Nat) (orig : List MRow) : (rs pre : List MRow) →
    orig = pre++rs → (b : HB n orig n) → InWidth n rs → Fed n orig b rs
  | [], _, _, b, _ => .ok b (fun _ => ⟨fun h => ⟨h,True.intro⟩,fun h => h.left⟩)
  | r::rs, pre, e, b, hw =>
    let tag : MTag n orig := ⟨r,2^pre.length,e.symm ▸ original_unit n pre rs r⟩
    match insert b tag hw.left with
    | .bad w cert => .bad w cert
    | .ok next eqv =>
      match feed n orig rs (pre++[r]) (by simpa [List.append_assoc] using e) next hw.right with
      | .bad w cert => .bad w cert
      | .ok final ef =>
        .ok final (fun x => by
          constructor
          · intro h
            have ht := (ef x).mp h
            have hi := (eqv x).mp ht.left
            exact ⟨hi.left,hi.right,ht.right⟩
          · intro h
            exact (ef x).mpr ⟨(eqv x).mpr ⟨h.left,h.right.left⟩,h.right.right⟩)

inductive HighestResult (n : Nat) (orig : List MRow) : Type where
  | sat (x : Nat) (bound : x < 2^n) (good : MaskAll n orig x) : HighestResult n orig
  | unsat (w : Nat) (cert : MaskProvenance n orig (0,true) w) : HighestResult n orig

def highestSolve (n : Nat) (orig : List MRow) (hw : InWidth n orig) : HighestResult n orig :=
  match feed n orig orig [] rfl (blank n orig n) hw with
  | .bad w cert => .unsat w cert
  | .ok b e =>
    let a := reconstruct b (Nat.le_refl n)
    .sat a.value a.bound ((e a.value).mp a.good).right

def highestOutput (n : Nat) (orig : List MRow) (hw : InWidth n orig) : Bool × Nat :=
  match highestSolve n orig hw with
  | .sat x _ _ => (true,x)
  | .unsat w _ => (false,w)

theorem highest_output_spec (n : Nat) (orig : List MRow) (hw : InWidth n orig) :
    match highestOutput n orig hw with
    | (true,x) => x < 2^n ∧ AllSat (orig.map (maskRow n)) (decode n x)
    | (false,w) => MaskProvenance n orig (0,true) w ∧
      ¬ ∃ x : List Bool, x.length = n ∧ AllSat (orig.map (maskRow n)) x := by
  unfold highestOutput
  cases highestSolve n orig hw with
  | sat x h g => exact ⟨h,(maskAll_iff n orig x).mp g⟩
  | unsat w c => exact ⟨c,provenance_refutes n orig w c⟩

theorem highest_unsat_complete (n : Nat) (orig : List MRow) (hw : InWidth n orig)
    (h : ¬ ∃ x : List Bool, x.length = n ∧ AllSat (orig.map (maskRow n)) x) :
    ∃ w, highestOutput n orig hw = (false,w) ∧ MaskProvenance n orig (0,true) w := by
  unfold highestOutput
  cases highestSolve n orig hw with
  | sat x _ g => exact False.elim (h ⟨decode n x,decode_length n x 0,(maskAll_iff n orig x).mp g⟩)
  | unsat w c => exact ⟨w,rfl,c⟩

end ProctorGF2
#print axioms ProctorGF2.insert
#print axioms ProctorGF2.reconstruct
#print axioms ProctorGF2.original_unit
#print axioms ProctorGF2.feed
#print axioms ProctorGF2.highestSolve
#print axioms ProctorGF2.highest_output_spec
#print axioms ProctorGF2.highest_unsat_complete
