/-! F011: end-to-end certified disjoint AND-block solver.
The input coupling rows are natural-number masks of declared width. -/
namespace ProctorPNP
open ProctorGF2

def fit : Nat → List Bool → List Bool
  | 0, _ => []
  | n+1, [] => false :: fit n []
  | n+1, a::as => a :: fit n as

theorem fit_length (n : Nat) (a : List Bool) : (fit n a).length = n := by
  induction n generalizing a with
  | zero => rfl
  | succ n ih =>
    cases a with
    | nil => exact congrArg Nat.succ (ih [])
    | cons b bs => exact congrArg Nat.succ (ih bs)

theorem fit_dot (n : Nat) (a x : List Bool) (h : x.length = n) :
    dot (fit n a) x = dot a x := by
  induction n generalizing a x with
  | zero =>
    cases x with
    | nil => exact (dot_nil a).symm
    | cons b bs => exact False.elim (Nat.noConfusion h)
  | succ n ih =>
    cases x with
    | nil => exact False.elim (Nat.noConfusion h)
    | cons b bs =>
      cases a with
      | nil => cases b <;> exact ih [] bs (Nat.succ.inj h)
      | cons c cs =>
        exact congrArg (bx (c && b)) (ih cs bs (Nat.succ.inj h))

def rowMask (n : Nat) (r : Row) : MRow := (encodeBits (fit n r.coeff),r.rhs)

theorem rowMask_width (n : Nat) (r : Row) : (rowMask n r).1 < 2^n := by
  have e := encode_bound (fit n r.coeff)
  rw [fit_length] at e
  exact e

theorem rowMask_decode (n : Nat) (r : Row) :
    maskRow n (rowMask n r) = ⟨fit n r.coeff,r.rhs⟩ := by
  have h := decode_encode (fit n r.coeff)
  rw [fit_length] at h
  exact congrArg (fun a => Row.mk a r.rhs) h

theorem rowMasks_width (n : Nat) (rs : List Row) :
    InWidth n (rs.map (rowMask n)) := by
  induction rs with
  | nil => exact True.intro
  | cons r rs ih => exact ⟨rowMask_width n r,ih⟩

theorem rowMasks_sat (n : Nat) (rs : List Row) (x : List Bool) (hx : x.length = n) :
    AllSat ((rs.map (rowMask n)).map (maskRow n)) x ↔ AllSat rs x := by
  induction rs with
  | nil => exact Iff.rfl
  | cons r rs ih =>
    have e : Sat (maskRow n (rowMask n r)) x ↔ Sat r x := by
      rw [rowMask_decode]
      exact ⟨fun h => (fit_dot n r.coeff x hx).symm.trans h,
        fun h => (fit_dot n r.coeff x hx).trans h⟩
    exact ⟨fun h => ⟨e.mp h.left,ih.mp h.right⟩,fun h => ⟨e.mpr h.left,ih.mpr h.right⟩⟩

theorem width_append (n : Nat) (a b : List MRow)
    (ha : InWidth n a) (hb : InWidth n b) : InWidth n (a++b) := by
  induction a with
  | nil => exact hb
  | cons r rs ih => exact ⟨ha.left,ih ha.right⟩

def augmented (ds : Domains) (rs : List MRow) : List MRow :=
  rs ++ (domainRows ds).map (rowMask ds.length)

theorem augmented_width (ds : Domains) (rs : List MRow) (h : InWidth ds.length rs) :
    InWidth ds.length (augmented ds rs) :=
  width_append ds.length rs _ h (rowMasks_width _ _)

theorem local_length (d : List Pair) : (localRows d).length ≤ 1 := by
  unfold localRows
  cases containsBit false (d.map gate) <;> cases containsBit true (d.map gate) <;> decide

theorem domain_length (ds : Domains) : (domainRows ds).length ≤ ds.length := by
  induction ds with
  | nil => exact Nat.le_refl 0
  | cons d ds ih =>
    have h := local_length d
    simp only [domainRows,List.length_append,List.length_map,List.length_cons]
    omega

theorem augmented_length (ds : Domains) (rs : List MRow) :
    (augmented ds rs).length ≤ rs.length+ds.length := by
  simp only [augmented,List.length_append,List.length_map]
  exact Nat.add_le_add_left (domain_length ds) _

theorem augmented_sat (ds : Domains) (rs : List MRow) (x : List Bool)
    (hx : x.length = ds.length) :
    AllSat ((augmented ds rs).map (maskRow ds.length)) x ↔
      AllSat (rs.map (maskRow ds.length)) x ∧ Projected ds x := by
  unfold augmented
  rw [List.map_append]
  exact (append_sat _ _ x).trans
    ⟨fun h => ⟨h.left,(domain_spec ds x hx).mp ((rowMasks_sat _ _ x hx).mp h.right)⟩,
     fun h => ⟨h.left,(rowMasks_sat _ _ x hx).mpr ((domain_spec ds x hx).mpr h.right)⟩⟩

-- Executable search, not extraction of a witness from a Prop existential.
structure Pick (d : List Pair) (y : Bool) where
  value : Pair
  member : value ∈ d
  output : gate value = y

def pick : (d : List Pair) → (y : Bool) → y ∈ d.map gate → Pick d y
  | [], _, h => nomatch h
  | p::ps, y, h =>
    if e : gate p = y then ⟨p,List.Mem.head _,e⟩
    else
      let q := pick ps y (by
        change y ∈ gate p :: ps.map gate at h
        cases h with
        | head => exact False.elim (e rfl)
        | tail _ ht => exact ht)
      ⟨q.value,List.Mem.tail _ q.member,q.output⟩

structure Lifted (ds : Domains) (ys : List Bool) where
  pairs : List Pair
  valid : Allowed ds pairs
  output : pairs.map gate = ys

def liftExec : (ds : Domains) → (ys : List Bool) → Projected ds ys → Lifted ds ys
  | [], [], _ => ⟨[],Allowed.nil,rfl⟩
  | [], _::_, h => nomatch h
  | _::_, [], h => nomatch h
  | d::ds,y::ys,h =>
    let q := pick d y (by cases h with | cons hy ht => exact hy)
    let rest := liftExec ds ys (by cases h with | cons hy ht => exact ht)
    ⟨q.value::rest.pairs,Allowed.cons q.member rest.valid,
      (congrArg (fun b => b::rest.pairs.map gate) q.output).trans
        (congrArg (List.cons y) rest.output)⟩

def OriginalSat (ds : Domains) (rs : List MRow) (ps : List Pair) : Prop :=
  Allowed ds ps ∧ AllSat (rs.map (maskRow ds.length)) (ps.map gate)

theorem augmented_refutes (ds : Domains) (rs : List MRow) (w : Nat)
    (h : MaskProvenance ds.length (augmented ds rs) (0,true) w) :
    ¬ ∃ ps, OriginalSat ds rs ps := by
  intro he
  obtain ⟨ps,hp,hs⟩ := he
  have pr := project ds ps hp
  have hl := projected_length ds (ps.map gate) pr
  exact provenance_refutes ds.length (augmented ds rs) w h
    ⟨ps.map gate,hl,(augmented_sat ds rs _ hl).mpr ⟨hs,pr⟩⟩

-- The logical certificate is relative to the deterministic augmented row list.
inductive EndResult (ds : Domains) (rs : List MRow) : Type where
  | sat (ps : List Pair) (valid : OriginalSat ds rs ps) : EndResult ds rs
  | unsat (w : Nat) (bound : w < 2^(augmented ds rs).length)
      (cert : MaskProvenance ds.length (augmented ds rs) (0,true) w) : EndResult ds rs

theorem polynomial_rows_mono (n m M : Nat) (h : m ≤ M) :
    polynomial n m ≤ polynomial n M := by
  unfold polynomial
  apply Nat.mul_le_mul
  · have h1 := Nat.mul_le_mul_right (n+1) h
    have h2 := Nat.mul_le_mul_right n h
    omega
  · omega

structure EndRun (ds : Domains) (rs : List MRow) where
  result : EndResult ds rs
  charge : Nat
  charge_bound : charge ≤ polynomial ds.length (rs.length+ds.length)

def solveBlocks (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) : EndRun ds rs := by
  let a := augmented ds rs
  let s := costSolve ds.length a (augmented_width ds rs hw)
  let c := bitCharge ds.length a.length s.visits s.collisions s.rowsSeen s.backVisits s.evaluations
  have cb : c ≤ polynomial ds.length (rs.length+ds.length) :=
    Nat.le_trans (costSolve_bound ds.length a (augmented_width ds rs hw))
      (polynomial_rows_mono _ _ _ (augmented_length ds rs))
  obtain ⟨res,v,k,j,b,d,hv,hk,hj,hb,hd,wt⟩ := s
  cases res with
  | sat x hx hs =>
    have hlen := decode_length ds.length x 0
    have hh := (augmented_sat ds rs (decode ds.length x) hlen).mp ((maskAll_iff ds.length a x).mp hs)
    let p := liftExec ds (decode ds.length x) hh.right
    exact ⟨.sat p.pairs ⟨p.valid,p.output.symm ▸ hh.left⟩,c,cb⟩
  | unsat w cert => exact ⟨.unsat w wt cert,c,cb⟩

inductive BlockOutput where
  | sat (ps : List Pair)
  | unsat (w : Nat)
deriving BEq, Repr

def blockOutput (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) : BlockOutput :=
  match (solveBlocks ds rs hw).result with
  | .sat ps _ => .sat ps
  | .unsat w _ _ => .unsat w

theorem blockOutput_spec (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    match blockOutput ds rs hw with
    | .sat ps => OriginalSat ds rs ps
    | .unsat w => w < 2^(augmented ds rs).length ∧
      MaskProvenance ds.length (augmented ds rs) (0,true) w ∧ ¬ ∃ ps, OriginalSat ds rs ps := by
  unfold blockOutput
  cases (solveBlocks ds rs hw).result with
  | sat ps h => exact h
  | unsat w hb hc => exact ⟨hb,hc,augmented_refutes ds rs w hc⟩

theorem block_unsat_complete (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs)
    (h : ¬ ∃ ps, OriginalSat ds rs ps) :
    ∃ w, blockOutput ds rs hw = .unsat w ∧
      MaskProvenance ds.length (augmented ds rs) (0,true) w := by
  unfold blockOutput
  cases (solveBlocks ds rs hw).result with
  | sat ps hp => exact False.elim (h ⟨ps,hp⟩)
  | unsat w _ hc => exact ⟨w,rfl,hc⟩

-- Explicit polynomial bound for the affine phase, using only original dimensions.
theorem block_charge_bound (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    (solveBlocks ds rs hw).charge ≤ polynomial ds.length (rs.length+ds.length) :=
  (solveBlocks ds rs hw).charge_bound

end ProctorPNP
#print axioms ProctorPNP.rowMasks_sat
#print axioms ProctorPNP.augmented_width
#print axioms ProctorPNP.augmented_length
#print axioms ProctorPNP.augmented_sat
#print axioms ProctorPNP.pick
#print axioms ProctorPNP.liftExec
#print axioms ProctorPNP.augmented_refutes
#print axioms ProctorPNP.solveBlocks
#print axioms ProctorPNP.blockOutput_spec
#print axioms ProctorPNP.block_unsat_complete
#print axioms ProctorPNP.block_charge_bound
