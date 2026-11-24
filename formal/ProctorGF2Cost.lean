/-! F010: costed highest-bit solver. Explicit fixed-width bit-operation model,
not a Lean VM or CPython timing theorem. -/
namespace ProctorGF2

theorem xor_width (a b k : Nat) (ha : a < 2^k) (hb : b < 2^k) :
    a ^^^ b < 2^k := by
  apply Nat.lt_pow_two_of_testBit
  intro i hi
  have h := Nat.pow_le_pow_of_le_right Nat.zero_lt_two hi
  rw [Nat.testBit_xor,Nat.testBit_lt_two_pow (Nat.lt_of_lt_of_le ha h),
      Nat.testBit_lt_two_pow (Nat.lt_of_lt_of_le hb h)]
  rfl

def BasisWidth {n orig cap} (b : HB n orig cap) : Prop :=
  match b with
  | .empty => True
  | .vacant t => BasisWidth t
  | .occupied r _ t => r.weight < 2^orig.length ∧ BasisWidth t

theorem blank_width (n : Nat) (orig : List MRow) (cap : Nat) :
    BasisWidth (blank n orig cap) := by
  induction cap with
  | zero => exact True.intro
  | succ p ih => exact ih

structure CountedIns {n orig cap} (b : HB n orig cap) (r : MTag n orig) where
  result : Ins b r
  visits : Nat
  collisions : Nat
  visits_bound : visits ≤ cap+1
  collisions_bound : collisions ≤ cap
  width : match result with
    | .bad w _ => w < 2^orig.length
    | .ok next _ => BasisWidth next

-- Each invocation counts one visited slot (including the terminal zero case).
-- Each occupied-slot collision counts exactly one joint row/provenance XOR.
def insertCount {n orig} : {cap : Nat} → (b : HB n orig cap) →
    (r : MTag n orig) → r.row.1 < 2^cap → BasisWidth b →
    r.weight < 2^orig.length → CountedIns b r
  | 0, .empty, r, h, _, hw => by
    have hz : r.row.1 = 0 := by omega
    cases e : r.row.2 with
    | true =>
      have he : r.row = (0,true) := Prod.ext hz e
      exact ⟨.bad r.weight (he ▸ r.valid),1,0,by decide,by decide,hw⟩
    | false =>
      let result : Ins (HB.empty : HB n orig 0) r := .ok .empty (fun x => by
        have hs : maskSat n r.row x := (maskSat_iff n r.row x).mp (by
          change dot (decode n r.row.1) (decode n x) = r.row.2
          rw [hz,e]
          exact zero_mask_dot n (decode n x))
        exact ⟨fun _ => ⟨True.intro,hs⟩,fun _ => True.intro⟩)
      exact ⟨result,1,0,by decide,by decide,True.intro⟩
  | p+1, .vacant t, r, h, hb, hw => by
    if hp : 2^p ≤ r.row.1 then
      exact ⟨.ok (.occupied r ⟨hp,h⟩ t) (fun _ => and_comm),1,0,by omega,by omega,⟨hw,hb⟩⟩
    else
      obtain ⟨res,v,c,hv,hc,wt⟩ := insertCount t r (Nat.lt_of_not_ge hp) hb hw
      cases res with
      | bad w cert => exact ⟨.bad w cert,v+1,c,by omega,by omega,wt⟩
      | ok next e => exact ⟨.ok (.vacant next) e,v+1,c,by omega,by omega,wt⟩
  | p+1, .occupied q hq t, r, h, hb, hw => by
    if hp : 2^p ≤ r.row.1 then
      obtain ⟨res,v,c,hv,hc,wt⟩ := insertCount t (addMTag q r)
        (highest_descent q.row.1 r.row.1 p hq ⟨hp,h⟩) hb.right
        (xor_width q.weight r.weight orig.length hb.left hw)
      cases res with
      | bad w cert => exact ⟨.bad w cert,v+1,c+1,by omega,by omega,wt⟩
      | ok next e =>
        let result : Ins (.occupied q hq t) r :=
          .ok (.occupied q hq next) (fun x => by
            constructor
            · intro hs
              have et := (e x).mp hs.right
              have er := (mask_replace n q.row r.row x).mpr ⟨hs.left,et.right⟩
              exact ⟨⟨hs.left,et.left⟩,er.right⟩
            · intro hs
              have er := (mask_replace n q.row r.row x).mp ⟨hs.left.left,hs.right⟩
              exact ⟨hs.left.left,(e x).mpr ⟨hs.left.right,er.right⟩⟩)
        exact ⟨result,v+1,c+1,by omega,by omega,⟨hb.left,wt⟩⟩
    else
      obtain ⟨res,v,c,hv,hc,wt⟩ := insertCount t r (Nat.lt_of_not_ge hp) hb.right hw
      cases res with
      | bad w cert => exact ⟨.bad w cert,v+1,c,by omega,by omega,wt⟩
      | ok next e =>
        let result : Ins (.occupied q hq t) r :=
          .ok (.occupied q hq next) (fun x => by
            constructor
            · intro hs
              have et := (e x).mp hs.right
              exact ⟨⟨hs.left,et.left⟩,et.right⟩
            · intro hs
              exact ⟨hs.left.left,(e x).mpr ⟨hs.left.right,hs.right⟩⟩)
        exact ⟨result,v+1,c,by omega,by omega,⟨hb.left,wt⟩⟩

structure CountedFeed (n : Nat) (orig : List MRow) (b : HB n orig n) (rs : List MRow) where
  result : Fed n orig b rs
  visits : Nat
  collisions : Nat
  rowsSeen : Nat
  visits_bound : visits ≤ rs.length*(n+1)
  collisions_bound : collisions ≤ rs.length*n
  rows_bound : rowsSeen ≤ rs.length
  width : match result with
    | .bad w _ => w < 2^orig.length
    | .ok next _ => BasisWidth next

def feedCount (n : Nat) (orig : List MRow) : (rs pre : List MRow) →
    orig = pre++rs → (b : HB n orig n) → InWidth n rs → BasisWidth b →
    CountedFeed n orig b rs
  | [], _, _, b, _, hb =>
    ⟨.ok b (fun _ => ⟨fun h => ⟨h,True.intro⟩,fun h => h.left⟩),0,0,0,
      Nat.zero_le _,Nat.zero_le _,Nat.zero_le _,hb⟩
  | r::rs, pre, e, b, hw, hb => by
    let tag : MTag n orig := ⟨r,2^pre.length,e.symm ▸ original_unit n pre rs r⟩
    have ht : tag.weight < 2^orig.length := by
      change 2^pre.length < 2^orig.length
      rw [e]
      have hl : pre.length+1 ≤ (pre++r::rs).length := by simp; omega
      have hh : 2^pre.length < 2^(pre.length+1) := by rw [Nat.pow_succ]; have := Nat.two_pow_pos pre.length; omega
      exact Nat.lt_of_lt_of_le hh (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hl)
    obtain ⟨res,v,c,hv,hc,wt⟩ := insertCount b tag hw.left hb ht
    cases res with
    | bad w cert =>
      exact ⟨.bad w cert,v,c,1,
        by simp only [List.length_cons,Nat.add_mul,Nat.one_mul]; omega,
        by simp only [List.length_cons,Nat.add_mul,Nat.one_mul]; omega,
        by simp,wt⟩
    | ok next eqv =>
      obtain ⟨res2,v2,c2,k,hv2,hc2,hk,wt2⟩ :=
        feedCount n orig rs (pre++[r]) (by simpa [List.append_assoc] using e) next hw.right wt
      have vb : v+v2 ≤ (r::rs).length*(n+1) := by
        simp only [List.length_cons,Nat.add_mul,Nat.one_mul]
        omega
      have cb : c+c2 ≤ (r::rs).length*n := by
        simp only [List.length_cons,Nat.add_mul,Nat.one_mul]
        omega
      have kb : k+1 ≤ (r::rs).length := by simp only [List.length_cons]; omega
      cases res2 with
      | bad w cert => exact ⟨.bad w cert,v+v2,c+c2,k+1,vb,cb,kb,wt2⟩
      | ok final ef =>
        let result : Fed n orig b (r::rs) := .ok final (fun x => by
          constructor
          · intro h
            have hh := (ef x).mp h
            have hi := (eqv x).mp hh.left
            exact ⟨hi.left,hi.right,hh.right⟩
          · intro h
            exact (ef x).mpr ⟨(eqv x).mpr ⟨h.left,h.right.left⟩,h.right.right⟩)
        exact ⟨result,v+v2,c+c2,k+1,vb,cb,kb,wt2⟩

structure CountedBack {n orig cap} (b : HB n orig cap) where
  result : Reconstructed b
  visits : Nat
  evaluations : Nat
  visits_exact : visits = cap
  evaluations_bound : evaluations ≤ cap

def backCount {n orig} : {cap : Nat} → (b : HB n orig cap) → cap ≤ n → CountedBack b
  | 0, .empty, _ => ⟨⟨0,by decide,True.intro⟩,0,0,rfl,Nat.le_refl 0⟩
  | p+1, .vacant t, h =>
    let a := backCount t (by omega)
    ⟨⟨a.result.value,Nat.lt_of_lt_of_le a.result.bound
      (Nat.pow_le_pow_of_le_right Nat.zero_lt_two (Nat.le_succ p)),a.result.good⟩,
      a.visits+1,a.evaluations,congrArg Nat.succ a.visits_exact,by have := a.evaluations_bound; omega⟩
  | p+1, .occupied r hr t, h =>
    let a := backCount t (by omega)
    let y := backStep n r.row a.result.value p
    ⟨⟨y,back_bound n r.row a.result.value p a.result.bound,
      ⟨(maskSat_iff n r.row y).mp (backstep_pivot n r.row a.result.value p hr (by omega)),
       (lower_basis_preserved t r.row a.result.value p (Nat.le_refl p) (by omega)).mpr a.result.good⟩⟩,
      a.visits+1,a.evaluations+1,congrArg Nat.succ a.visits_exact,by have := a.evaluations_bound; omega⟩

structure CostRun (n : Nat) (orig : List MRow) where
  result : HighestResult n orig
  visits : Nat
  collisions : Nat
  rowsSeen : Nat
  backVisits : Nat
  evaluations : Nat
  visits_bound : visits ≤ orig.length*(n+1)
  collisions_bound : collisions ≤ orig.length*n
  rows_bound : rowsSeen ≤ orig.length
  back_bound : backVisits ≤ n
  evaluations_bound : evaluations ≤ n
  certificate_width : match result with
    | .sat _ _ _ => True
    | .unsat w _ => w < 2^orig.length

def costSolve (n : Nat) (orig : List MRow) (hw : InWidth n orig) : CostRun n orig := by
  obtain ⟨res,v,c,k,hv,hc,hk,wt⟩ :=
    feedCount n orig orig [] rfl (blank n orig n) hw (blank_width n orig n)
  cases res with
  | bad w cert =>
    exact ⟨.unsat w cert,v,c,k,0,0,hv,hc,hk,Nat.zero_le _,Nat.zero_le _,wt⟩
  | ok b e =>
    let a := backCount b (Nat.le_refl n)
    exact ⟨.sat a.result.value a.result.bound ((e a.result.value).mp a.result.good).right,
      v,c,k,a.visits,a.evaluations,hv,hc,hk,Nat.le_of_eq a.visits_exact,a.evaluations_bound,True.intro⟩

def occupiedCount {n orig cap} (b : HB n orig cap) : Nat :=
  match b with
  | .empty => 0
  | .vacant t => occupiedCount t
  | .occupied _ _ t => 1+occupiedCount t

theorem occupied_bound {n orig cap} (b : HB n orig cap) : occupiedCount b ≤ cap := by
  induction b with
  | empty => exact Nat.le_refl 0
  | vacant t ih => exact Nat.le_trans ih (Nat.le_succ _)
  | occupied r hp t ih =>
    change 1+occupiedCount t ≤ _
    omega

-- Fixed-width payload accounting: n coefficient bits, one rhs, m provenance bits.
-- Includes one occupancy bit per slot, not allocator/stack/object overhead.
def payload {n orig cap} (b : HB n orig cap) : Nat :=
  cap + occupiedCount b * (n+1+orig.length)

theorem payload_bound {n orig cap} (b : HB n orig cap) :
    payload b ≤ cap + cap*(n+1+orig.length) :=
  Nat.add_le_add_left (Nat.mul_le_mul_right _ (occupied_bound b)) cap

-- Abstract bit-cost model. L allows fixed-width data, indices and counters.
-- The charge is deliberately conservative per event; no claim about a VM.
def bitCharge (n m v c k b d : Nat) : Nat :=
  let L := n+m+1
  (4*v+2*c+4*k+2*b+6*d+2*n+2*m+1)*L

def polynomial (n m : Nat) : Nat :=
  (4*(m*(n+1))+2*(m*n)+4*m+2*n+6*n+2*n+2*m+1)*(n+m+1)

theorem bitCharge_bound (n m v c k b d : Nat)
    (hv : v ≤ m*(n+1)) (hc : c ≤ m*n) (hk : k ≤ m)
    (hb : b ≤ n) (hd : d ≤ n) :
    bitCharge n m v c k b d ≤ polynomial n m := by
  unfold bitCharge polynomial
  apply Nat.mul_le_mul_right
  omega

theorem costSolve_bound (n : Nat) (orig : List MRow) (hw : InWidth n orig) :
    let s := costSolve n orig hw
    bitCharge n orig.length s.visits s.collisions s.rowsSeen s.backVisits s.evaluations
      ≤ polynomial n orig.length := by
  dsimp
  exact bitCharge_bound n orig.length _ _ _ _ _
    (costSolve n orig hw).visits_bound (costSolve n orig hw).collisions_bound
    (costSolve n orig hw).rows_bound (costSolve n orig hw).back_bound
    (costSolve n orig hw).evaluations_bound

def costOutput (n : Nat) (orig : List MRow) (hw : InWidth n orig) :
    (Bool × Nat) × (Nat × Nat × Nat × Nat × Nat) :=
  let s := costSolve n orig hw
  let ans := match s.result with
    | .sat x _ _ => (true,x)
    | .unsat w _ => (false,w)
  (ans,(s.visits,s.collisions,s.rowsSeen,s.backVisits,s.evaluations))

theorem costOutput_spec (n : Nat) (orig : List MRow) (hw : InWidth n orig) :
    match (costOutput n orig hw).1 with
    | (true,x) => x < 2^n ∧ AllSat (orig.map (maskRow n)) (decode n x)
    | (false,w) => w < 2^orig.length ∧ MaskProvenance n orig (0,true) w ∧
      ¬ ∃ x : List Bool, x.length = n ∧ AllSat (orig.map (maskRow n)) x := by
  unfold costOutput
  generalize h : costSolve n orig hw = s
  obtain ⟨res,v,c,k,b,d,hv,hc,hk,hb,hd,wt⟩ := s
  cases res with
  | sat x hx hs => exact ⟨hx,(maskAll_iff n orig x).mp hs⟩
  | unsat w cert => exact ⟨wt,cert,provenance_refutes n orig w cert⟩

end ProctorGF2
#print axioms ProctorGF2.xor_width
#print axioms ProctorGF2.insertCount
#print axioms ProctorGF2.feedCount
#print axioms ProctorGF2.backCount
#print axioms ProctorGF2.costSolve
#print axioms ProctorGF2.occupied_bound
#print axioms ProctorGF2.payload_bound
#print axioms ProctorGF2.bitCharge_bound
#print axioms ProctorGF2.costSolve_bound
#print axioms ProctorGF2.costOutput_spec
