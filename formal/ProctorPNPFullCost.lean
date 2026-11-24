/-! F012: instrumented end-to-end abstract cost model, including
local domain scanning, row assembly and executable pair lifting. -/
namespace ProctorPNP
open ProctorGF2

def pairCount : Domains → Nat
  | [] => 0
  | d::ds => d.length + pairCount ds

structure ContainsRun (y : Bool) (bs : List Bool) where
  value : Bool
  same : value = containsBit y bs
  visits : Nat
  bound : visits ≤ bs.length

def containsCount (y : Bool) : (bs : List Bool) → ContainsRun y bs
  | [] => ⟨false,rfl,0,Nat.le_refl 0⟩
  | b::bs => by
    cases e : eqBit y b with
    | true =>
      exact ⟨true,by unfold containsBit; rw [e],1,by simp⟩
    | false =>
      let r := containsCount y bs
      exact ⟨r.value,by unfold containsBit; rw [e]; exact r.same,
        r.visits+1,by exact Nat.succ_le_succ r.bound⟩

structure LocalBuild (d : List Pair) where
  rows : List Row
  same : rows = localRows d
  scans : Nat
  bound : scans ≤ 3*d.length

def buildLocal (d : List Pair) : LocalBuild d := by
  let ys := d.map gate
  let f := containsCount false ys
  let t := containsCount true ys
  exact ⟨flagRows f.value t.value,by unfold localRows; rw [f.same,t.same],
    d.length+f.visits+t.visits,by
      have hf := f.bound
      have ht := t.bound
      change f.visits ≤ (d.map gate).length at hf
      change t.visits ≤ (d.map gate).length at ht
      rw [List.length_map] at hf ht
      omega⟩

structure DomainBuild (ds : Domains) where
  rows : List Row
  same : rows = domainRows ds
  scans : Nat
  pads : Nat
  scans_bound : scans ≤ 3*pairCount ds
  pads_bound : pads ≤ ds.length*ds.length

-- Count a visit for every mapped pair and each membership comparison;
-- count one padding event for each shifted tail row.
def buildDomains : (ds : Domains) → DomainBuild ds
  | [] => ⟨[],rfl,0,0,Nat.le_refl 0,Nat.le_refl 0⟩
  | d::ds => by
    let a := buildLocal d
    let b := buildDomains ds
    have hb : b.rows.length ≤ ds.length := by
      rw [b.same]
      exact domain_length ds
    exact ⟨a.rows ++ b.rows.map padRow,
      by unfold domainRows; rw [a.same,b.same],
      a.scans+b.scans,b.pads+b.rows.length,
      by have h1 := a.bound; have h2 := b.scans_bound; change _ ≤ 3*(d.length+pairCount ds); omega,
      by
        have h := b.pads_bound
        simp only [List.length_cons,Nat.add_mul,Nat.mul_add,Nat.one_mul,Nat.mul_one]
        omega⟩

structure PickRun (d : List Pair) (y : Bool) where
  result : Pick d y
  visits : Nat
  bound : visits ≤ d.length

def pickCount : (d : List Pair) → (y : Bool) → y ∈ d.map gate → PickRun d y
  | [], _, h => nomatch h
  | p::ps, y, h =>
    if e : gate p = y then
      ⟨⟨p,List.Mem.head _,e⟩,1,by simp⟩
    else
      let q := pickCount ps y (by
        change y ∈ gate p :: ps.map gate at h
        cases h with
        | head => exact False.elim (e rfl)
        | tail _ ht => exact ht)
      ⟨⟨q.result.value,List.Mem.tail _ q.result.member,q.result.output⟩,
        q.visits+1,Nat.succ_le_succ q.bound⟩

structure LiftRun (ds : Domains) (ys : List Bool) where
  result : Lifted ds ys
  visits : Nat
  bound : visits ≤ pairCount ds

def liftCount : (ds : Domains) → (ys : List Bool) → Projected ds ys → LiftRun ds ys
  | [], [], _ => ⟨⟨[],Allowed.nil,rfl⟩,0,Nat.le_refl 0⟩
  | [], _::_, h => nomatch h
  | _::_, [], h => nomatch h
  | d::ds,y::ys,h =>
    let q := pickCount d y (by cases h with | cons hy ht => exact hy)
    let rest := liftCount ds ys (by cases h with | cons hy ht => exact ht)
    ⟨⟨q.result.value::rest.result.pairs,Allowed.cons q.result.member rest.result.valid,
      (congrArg (fun b => b::rest.result.pairs.map gate) q.result.output).trans
        (congrArg (List.cons y) rest.result.output)⟩,
      q.visits+rest.visits,Nat.add_le_add q.bound rest.bound⟩

-- The extra model accounts for fixed-width payload operations, not compiler
-- allocation or runtime. Each unit charge has width L=n+m+q+1.
-- Conversion of each generated row charges n fit and n encode positions.
-- Input/output terms include domain headers, original-row assembly, decode
-- and serialization of a bounded primal or dual payload.
def extraCharge (n m q scans pads generated lifted : Nat) : Nat :=
  (8*scans+4*pads+(4*n+4)*generated+8*lifted+8*n+4*m+4)*(n+m+q+1)

def fullPolynomial (n m q : Nat) : Nat :=
  polynomial n (m+n) + extraCharge n m q (3*q) (n*n) n q

theorem extra_bound (n m q s p g l : Nat)
    (hs : s ≤ 3*q) (hp : p ≤ n*n) (hg : g ≤ n) (hl : l ≤ q) :
    extraCharge n m q s p g l ≤ extraCharge n m q (3*q) (n*n) n q := by
  unfold extraCharge
  apply Nat.mul_le_mul_right
  have h := Nat.mul_le_mul_left (4*n+4) hg
  omega

structure FullRun (ds : Domains) (rs : List MRow) where
  result : EndResult ds rs
  affineCharge : Nat
  scans : Nat
  pads : Nat
  generated : Nat
  lifted : Nat
  affine_bound : affineCharge ≤ polynomial ds.length (rs.length+ds.length)
  scans_bound : scans ≤ 3*pairCount ds
  pads_bound : pads ≤ ds.length*ds.length
  generated_bound : generated ≤ ds.length
  lifted_bound : lifted ≤ pairCount ds

def solveFull (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) : FullRun ds rs := by
  let pre := buildDomains ds
  let a := rs ++ pre.rows.map (rowMask ds.length)
  have eq : a = augmented ds rs := by
    change rs ++ pre.rows.map (rowMask ds.length) = rs ++ (domainRows ds).map (rowMask ds.length)
    rw [pre.same]
  have wa : InWidth ds.length a := eq.symm ▸ augmented_width ds rs hw
  have ng : pre.rows.length ≤ ds.length := by rw [pre.same]; exact domain_length ds
  let s := costSolve ds.length a wa
  let c := bitCharge ds.length a.length s.visits s.collisions s.rowsSeen s.backVisits s.evaluations
  have la : a.length ≤ rs.length+ds.length := by rw [eq]; exact augmented_length ds rs
  have cb : c ≤ polynomial ds.length (rs.length+ds.length) :=
    Nat.le_trans (costSolve_bound ds.length a wa) (polynomial_rows_mono _ _ _ la)
  obtain ⟨res,v,k,j,b,d,hv,hk,hj,hb,hd,wt⟩ := s
  cases res with
  | sat x hx hs =>
    have hlen := decode_length ds.length x 0
    have he : AllSat ((augmented ds rs).map (maskRow ds.length)) (decode ds.length x) :=
      eq ▸ (maskAll_iff ds.length a x).mp hs
    have hh := (augmented_sat ds rs _ hlen).mp he
    let p := liftCount ds (decode ds.length x) hh.right
    exact ⟨.sat p.result.pairs ⟨p.result.valid,p.result.output.symm ▸ hh.left⟩,
      c,pre.scans,pre.pads,pre.rows.length,p.visits,cb,pre.scans_bound,pre.pads_bound,ng,p.bound⟩
  | unsat w cert =>
    exact ⟨.unsat w (eq ▸ wt) (eq ▸ cert),c,pre.scans,pre.pads,pre.rows.length,0,
      cb,pre.scans_bound,pre.pads_bound,ng,Nat.zero_le _⟩

def totalCharge {ds rs} (r : FullRun ds rs) : Nat :=
  r.affineCharge + extraCharge ds.length rs.length (pairCount ds) r.scans r.pads r.generated r.lifted

theorem full_charge_bound (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    totalCharge (solveFull ds rs hw) ≤ fullPolynomial ds.length rs.length (pairCount ds) := by
  let r := solveFull ds rs hw
  exact Nat.add_le_add r.affine_bound
    (extra_bound _ _ _ _ _ _ _ r.scans_bound r.pads_bound r.generated_bound r.lifted_bound)

def fullOutput (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) : BlockOutput :=
  match (solveFull ds rs hw).result with
  | .sat ps _ => .sat ps
  | .unsat w _ _ => .unsat w

theorem full_output_spec (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    match fullOutput ds rs hw with
    | .sat ps => OriginalSat ds rs ps
    | .unsat w => w < 2^(augmented ds rs).length ∧
      MaskProvenance ds.length (augmented ds rs) (0,true) w ∧ ¬ ∃ ps, OriginalSat ds rs ps := by
  unfold fullOutput
  cases (solveFull ds rs hw).result with
  | sat ps h => exact h
  | unsat w hb hc => exact ⟨hb,hc,augmented_refutes ds rs w hc⟩

theorem full_unsat_complete (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs)
    (h : ¬ ∃ ps, OriginalSat ds rs ps) :
    ∃ w, fullOutput ds rs hw = .unsat w ∧ MaskProvenance ds.length (augmented ds rs) (0,true) w := by
  unfold fullOutput
  cases (solveFull ds rs hw).result with
  | sat ps hp => exact False.elim (h ⟨ps,hp⟩)
  | unsat w _ hc => exact ⟨w,rfl,hc⟩

def fullStats (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    Nat × Nat × Nat × Nat × Nat × Nat :=
  let r := solveFull ds rs hw
  (r.scans,r.pads,r.generated,r.lifted,r.affineCharge,totalCharge r)

end ProctorPNP
#print axioms ProctorPNP.containsCount
#print axioms ProctorPNP.buildLocal
#print axioms ProctorPNP.buildDomains
#print axioms ProctorPNP.pickCount
#print axioms ProctorPNP.liftCount
#print axioms ProctorPNP.extra_bound
#print axioms ProctorPNP.solveFull
#print axioms ProctorPNP.full_charge_bound
#print axioms ProctorPNP.full_output_spec
#print axioms ProctorPNP.full_unsat_complete
