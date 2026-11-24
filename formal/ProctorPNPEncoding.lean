/-! PNP-F006: exact bitmask and local-domain representation theorems.
Replay after F001 and F002-F005 modules. -/
namespace ProctorGF2

def decodeAt : Nat → Nat → Nat → List Bool
  | 0, _, _ => []
  | n+1, a, k => a.testBit k :: decodeAt n a (k+1)

def decode (n a : Nat) : List Bool := decodeAt n a 0

theorem decode_length (n a k : Nat) : (decodeAt n a k).length = n := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih => exact congrArg Nat.succ (ih (k+1))

theorem bool_xor_agrees (a b : Bool) : (a ^^ b) = bx a b := by
  cases a <;> cases b <;> rfl

theorem decode_xor (n a b k : Nat) :
    decodeAt n (a ^^^ b) k = addVec (decodeAt n a k) (decodeAt n b k) := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact (congrArg (fun v : Bool => v :: decodeAt n (a ^^^ b) (k+1))
      ((Nat.testBit_xor a b k).trans (bool_xor_agrees (a.testBit k) (b.testBit k)))).trans
      (congrArg (List.cons (bx (a.testBit k) (b.testBit k))) (ih (k+1)))

def parityAt : Nat → Nat → Nat → Bool
  | 0, _, _ => false
  | n+1, a, k => bx (a.testBit k) (parityAt n a (k+1))

theorem decode_dot (n a b k : Nat) :
    dot (decodeAt n a k) (decodeAt n b k) = parityAt n (a &&& b) k := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact (congrArg (fun z : Bool => bx (a.testBit k && b.testBit k) z) (ih (k+1))).trans
      (congrArg (fun v : Bool => bx v (parityAt n (a &&& b) (k+1))) (Nat.testBit_and a b k).symm)

theorem decode_shift (n a s k : Nat) :
    decodeAt n (a >>> s) k = decodeAt n a (s+k) := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact (congrArg (fun v : Bool => v :: decodeAt n (a >>> s) (k+1))
      (Nat.testBit_shiftRight a)).trans
      (congrArg (List.cons (a.testBit (s+k))) (ih (k+1)))

def maskRow (n : Nat) (r : Nat × Bool) : Row := ⟨decode n r.1,r.2⟩
def maskSat (n : Nat) (r : Nat × Bool) (x : Nat) : Prop :=
  parityAt n (r.1 &&& x) 0 = r.2

theorem maskSat_iff (n : Nat) (r : Nat × Bool) (x : Nat) :
    Sat (maskRow n r) (decode n x) ↔ maskSat n r x :=
  ⟨fun h => (decode_dot n r.1 x 0).symm.trans h,
   fun h => (decode_dot n r.1 x 0).trans h⟩

theorem append_sat (a b : List Row) (x : List Bool) :
    AllSat (a++b) x ↔ AllSat a x ∧ AllSat b x := by
  induction a with
  | nil => exact ⟨fun h => ⟨True.intro,h⟩,fun h => h.right⟩
  | cons r rs ih =>
    exact ⟨fun h => ⟨⟨h.left,(ih.mp h.right).left⟩,(ih.mp h.right).right⟩,
      fun h => ⟨h.left.left,ih.mpr ⟨h.left.right,h.right⟩⟩⟩

def padRow (r : Row) : Row := ⟨false::r.coeff,r.rhs⟩

theorem pad_sat (rs : List Row) (y : Bool) (ys : List Bool) :
    AllSat (rs.map padRow) (y::ys) ↔ AllSat rs ys := by
  induction rs with
  | nil => exact Iff.rfl
  | cons r rs ih =>
    have e : Sat (padRow r) (y::ys) ↔ Sat r ys := by
      cases y <;> exact Iff.rfl
    exact ⟨fun h => ⟨e.mp h.left,ih.mp h.right⟩,fun h => ⟨e.mpr h.left,ih.mpr h.right⟩⟩

def containsBit (y : Bool) : List Bool → Bool
  | [] => false
  | b::bs => match eqBit y b with
    | true => true
    | false => containsBit y bs

theorem containsBit_iff (y : Bool) (bs : List Bool) :
    containsBit y bs = true ↔ y ∈ bs := by
  induction bs with
  | nil =>
    exact ⟨fun h => Bool.noConfusion h,fun h => nomatch h⟩
  | cons b bs ih =>
    cases h : eqBit y b with
    | true =>
      have e := (eqBit_iff y b).mp h
      constructor
      · intro _
        exact e.symm ▸ List.Mem.head bs
      · intro _
        unfold containsBit
        rw [h]
    | false =>
      constructor
      · intro ht
        have q : containsBit y bs = true := by
          unfold containsBit at ht
          rw [h] at ht
          exact ht
        exact List.Mem.tail b (ih.mp q)
      · intro hm
        cases hm with
        | head =>
          exact False.elim (Bool.noConfusion ((eqBit_iff y y).mpr rfl |>.symm.trans h))
        | tail _ ht =>
          unfold containsBit
          rw [h]
          exact ih.mpr ht

-- Empty output domain is encoded as 0=1. Nonempty singleton domains
-- become one unit equation, and the two-output domain adds no constraint.
def flagRows : Bool → Bool → List Row
  | false,false => [⟨[],true⟩]
  | true,false => [⟨[true],false⟩]
  | false,true => [⟨[true],true⟩]
  | true,true => []

theorem flag_spec (f t y : Bool) (ys : List Bool) :
    AllSat (flagRows f t) (y::ys) ↔ (if y then t else f) = true := by
  cases f <;> cases t <;> cases y <;>
    first
    | exact ⟨fun _ => rfl,fun _ => True.intro⟩
    | exact ⟨fun _ => rfl,fun _ => ⟨rfl,True.intro⟩⟩
    | exact ⟨fun h => Bool.noConfusion h.left,fun h => Bool.noConfusion h⟩

end ProctorGF2

namespace ProctorPNP
open ProctorGF2

def localRows (d : List Pair) : List Row :=
  flagRows (containsBit false (d.map gate)) (containsBit true (d.map gate))

theorem local_spec (d : List Pair) (y : Bool) (ys : List Bool) :
    AllSat (localRows d) (y::ys) ↔ y ∈ d.map gate := by
  cases y with
  | false => exact (flag_spec _ _ false ys).trans (containsBit_iff false _)
  | true => exact (flag_spec _ _ true ys).trans (containsBit_iff true _)

def domainRows : Domains → List Row
  | [] => []
  | d::ds => localRows d ++ (domainRows ds).map padRow

theorem projected_length (ds : Domains) (ys : List Bool) (h : Projected ds ys) :
    ys.length = ds.length := by
  induction h with
  | nil => rfl
  | cons _ _ ih => exact congrArg Nat.succ ih

theorem domain_spec (ds : Domains) (ys : List Bool) (h : ys.length = ds.length) :
    AllSat (domainRows ds) ys ↔ Projected ds ys := by
  induction ds generalizing ys with
  | nil =>
    cases ys with
    | nil => exact ⟨fun _ => Projected.nil,fun _ => True.intro⟩
    | cons y ys => exact False.elim (Nat.noConfusion h)
  | cons d ds ih =>
    cases ys with
    | nil => exact False.elim (Nat.noConfusion h)
    | cons y ys =>
      have e := (append_sat (localRows d) ((domainRows ds).map padRow) (y::ys))
      have l := local_spec d y ys
      have r := (pad_sat (domainRows ds) y ys).trans (ih ys (Nat.succ.inj h))
      constructor
      · intro hs
        have hs' := e.mp hs
        exact Projected.cons (l.mp hs'.left) (r.mp hs'.right)
      · intro hp
        cases hp with
        | cons hy ht => exact e.mpr ⟨l.mpr hy,r.mpr ht⟩

/-- Full reduction of disjoint AND block domains plus arbitrary affine coupling. -/
theorem encoded_iff (ds : Domains) (rs : List Row) :
    (∃ ps : List Pair, Allowed ds ps ∧ AllSat rs (ps.map gate)) ↔
    (∃ ys : List Bool, ys.length = ds.length ∧ AllSat (rs ++ domainRows ds) ys) := by
  constructor
  · intro h
    obtain ⟨ys,hp,hr⟩ := (projection_iff ds (AllSat rs)).mp h
    have hn := projected_length ds ys hp
    exact ⟨ys,hn,(append_sat rs (domainRows ds) ys).mpr ⟨hr,(domain_spec ds ys hn).mpr hp⟩⟩
  · intro h
    obtain ⟨ys,hn,hs⟩ := h
    have he := (append_sat rs (domainRows ds) ys).mp hs
    exact (projection_iff ds (AllSat rs)).mpr ⟨ys,(domain_spec ds ys hn).mp he.right,he.left⟩

theorem encoded_unsat (ds : Domains) (rs : List Row) (w : List Bool)
    (h : dualCheck ds.length (rs ++ domainRows ds) w = true) :
    ¬ ∃ ps : List Pair, Allowed ds ps ∧ AllSat rs (ps.map gate) := by
  intro hp
  have d := (dualCheck_iff ds.length (rs ++ domainRows ds) w).mp h
  exact dual_sound ds.length (rs ++ domainRows ds) w d.left d.right ((encoded_iff ds rs).mp hp)

end ProctorPNP
#print axioms ProctorGF2.decode_xor
#print axioms ProctorGF2.decode_dot
#print axioms ProctorGF2.decode_shift
#print axioms ProctorGF2.maskSat_iff
#print axioms ProctorPNP.domain_spec
#print axioms ProctorPNP.encoded_iff
#print axioms ProctorPNP.encoded_unsat
