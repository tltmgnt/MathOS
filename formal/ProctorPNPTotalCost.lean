/-! F012: end-to-end abstract event accounting, not host runtime accounting. -/
namespace ProctorPNP
open ProctorGF2

def domainSize : Domains → Nat
  | [] => 0
  | d::ds => d.length + domainSize ds

structure ScanCount (y : Bool) (bs : List Bool) where
  value : Bool
  visits : Nat
  agrees : value = containsBit y bs
  bound : visits ≤ bs.length

def scanCount (y : Bool) : (bs : List Bool) → ScanCount y bs
  | [] => ⟨false,0,rfl,Nat.le_refl 0⟩
  | b::bs => by
    cases e : eqBit y b with
    | true =>
      exact ⟨true,1,by unfold containsBit; rw [e],by simp⟩
    | false =>
      let q := scanCount y bs
      exact ⟨q.value,q.visits+1,by unfold containsBit; rw [e]; exact q.agrees,
        by have := q.bound; simp only [List.length_cons]; omega⟩

structure DomainCount (ds : Domains) where
  rows : List Row
  work : Nat
  agrees : rows = domainRows ds
  bound : work ≤ 3*domainSize ds + ds.length*(ds.length+3)

def domainCount : (ds : Domains) → DomainCount ds
  | [] => ⟨[],0,rfl,by decide⟩
  | d::ds => by
    let bs := d.map gate
    let f := scanCount false bs
    let t := scanCount true bs
    let localR := flagRows f.value t.value
    let tail := domainCount ds
    have el : localR = localRows d := by
      change flagRows f.value t.value = localRows d
      rw [f.agrees,t.agrees]
      rfl
    have hl : localR.length ≤ 1 := by rw [el]; exact local_length d
    have ht : tail.rows.length ≤ ds.length := by rw [tail.agrees]; exact domain_length ds
    have hf : f.visits ≤ d.length := by simpa [bs] using f.bound
    have hh : t.visits ≤ d.length := by simpa [bs] using t.bound
    refine ⟨localR ++ tail.rows.map padRow,
      tail.work+d.length+f.visits+t.visits+1+tail.rows.length+localR.length+1,?_,?_⟩
    · rw [el,tail.agrees]
      rfl
    · have hb := tail.bound
      simp only [domainSize,List.length_cons,Nat.add_mul,Nat.mul_add,Nat.one_mul,Nat.mul_one] at *
      omega

-- Fit and encode each row at the declared width. Count two width-n traversals
-- plus one row event, not the internal cost of Lean's natural-number operations.
structure PackCount (n : Nat) (rs : List Row) where
  masks : List MRow
  work : Nat
  agrees : masks = rs.map (rowMask n)
  exactWork : work = rs.length*(2*n+1)

def packCount (n : Nat) : (rs : List Row) → PackCount n rs
  | [] => ⟨[],0,rfl,by simp⟩
  | r::rs =>
    let q := packCount n rs
    ⟨rowMask n r :: q.masks,q.work+(2*n+1),
      congrArg (List.cons (rowMask n r)) q.agrees,
      by rw [q.exactWork,List.length_cons,Nat.add_mul,Nat.one_mul]⟩

structure PrepCount (ds : Domains) (rs : List MRow) where
  rows : List MRow
  work : Nat
  agrees : rows = augmented ds rs
  bound : work ≤ 3*domainSize ds + ds.length*(ds.length+3) +
    ds.length*(2*ds.length+1)+rs.length

def prepCount (ds : Domains) (rs : List MRow) : PrepCount ds rs := by
  let d := domainCount ds
  let p := packCount ds.length d.rows
  have hd : d.rows.length ≤ ds.length := by rw [d.agrees]; exact domain_length ds
  have hp : p.work ≤ ds.length*(2*ds.length+1) := by
    rw [p.exactWork]
    exact Nat.mul_le_mul_right _ hd
  refine ⟨rs++p.masks,d.work+p.work+rs.length,?_,?_⟩
  · rw [p.agrees,d.agrees]
    rfl
  · have h := d.bound
    omega

structure PickCount (d : List Pair) (y : Bool) where
  result : Pick d y
  visits : Nat
  bound : visits ≤ d.length

def pickCount : (d : List Pair) → (y : Bool) → y ∈ d.map gate → PickCount d y
  | [], _, h => nomatch h
  | p::ps, y, h =>
    if e : gate p = y then ⟨⟨p,List.Mem.head _,e⟩,1,by simp⟩
    else
      let q := pickCount ps y (by
        change y ∈ gate p :: ps.map gate at h
        cases h with
        | head => exact False.elim (e rfl)
        | tail _ ht => exact ht)
      ⟨⟨q.result.value,List.Mem.tail _ q.result.member,q.result.output⟩,q.visits+1,
        by have := q.bound; simp only [List.length_cons]; omega⟩

structure LiftCount (ds : Domains) (ys : List Bool) where
  result : Lifted ds ys
  visits : Nat
  bound : visits ≤ domainSize ds

def liftCount : (ds : Domains) → (ys : List Bool) → Projected ds ys → LiftCount ds ys
  | [], [], _ => ⟨⟨[],Allowed.nil,rfl⟩,0,Nat.le_refl 0⟩
  | [], _::_, h => nomatch h
  | _::_, [], h => nomatch h
  | d::ds,y::ys,h =>
    let q := pickCount d y (by cases h with | cons hy _ => exact hy)
    let t := liftCount ds ys (by cases h with | cons _ ht => exact ht)
    ⟨⟨q.result.value::t.result.pairs,Allowed.cons q.result.member t.result.valid,
      (congrArg (fun b => b::t.result.pairs.map gate) q.result.output).trans
        (congrArg (List.cons y) t.result.output)⟩,
      q.visits+t.visits,
      Nat.add_le_add q.bound t.bound⟩

-- Charge one explicit common width per non-affine event, with fixed overhead
-- for reading dimensions, decoding the solution and copying the output.
-- The affine charge remains F010's model. No machine-runtime claim is made.
def totalCharge (n m s prep affine lift : Nat) : Nat :=
  affine + (prep+lift+4*n+2*m+1)*(n+m+s+1)

def totalPolynomial (n m s : Nat) : Nat :=
  polynomial n (m+n) +
    (4*s+n*(n+3)+n*(2*n+1)+3*m+4*n+1)*(n+m+s+1)

theorem totalCharge_bound (n m s prep affine lift : Nat)
    (hp : prep ≤ 3*s+n*(n+3)+n*(2*n+1)+m)
    (ha : affine ≤ polynomial n (m+n)) (hl : lift ≤ s) :
    totalCharge n m s prep affine lift ≤ totalPolynomial n m s := by
  unfold totalCharge totalPolynomial
  apply Nat.add_le_add ha
  apply Nat.mul_le_mul_right
  omega

structure TotalRun (ds : Domains) (rs : List MRow) where
  result : EndResult ds rs
  preprocessing : Nat
  affine : Nat
  lifting : Nat
  prep_bound : preprocessing ≤ 3*domainSize ds + ds.length*(ds.length+3) +
    ds.length*(2*ds.length+1)+rs.length
  affine_bound : affine ≤ polynomial ds.length (rs.length+ds.length)
  lift_bound : lifting ≤ domainSize ds

def totalSolve (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    TotalRun ds rs := by
  let p := prepCount ds rs
  let a := p.rows
  have wa : InWidth ds.length a := by
    change InWidth ds.length p.rows
    rw [p.agrees]
    exact augmented_width ds rs hw
  let s := costSolve ds.length a wa
  let c := bitCharge ds.length a.length s.visits s.collisions s.rowsSeen s.backVisits s.evaluations
  have la : a.length ≤ rs.length+ds.length := by
    change p.rows.length ≤ _
    rw [p.agrees]
    exact augmented_length ds rs
  have cb : c ≤ polynomial ds.length (rs.length+ds.length) :=
    Nat.le_trans (costSolve_bound ds.length a wa) (polynomial_rows_mono _ _ _ la)
  obtain ⟨res,v,k,j,b,d,hv,hk,hj,hb,hd,wt⟩ := s
  cases res with
  | sat x hx hs =>
    have hlen := decode_length ds.length x 0
    have hsat : AllSat ((augmented ds rs).map (maskRow ds.length)) (decode ds.length x) :=
      by
        rw [← p.agrees]
        exact (maskAll_iff ds.length a x).mp hs
    have hh := (augmented_sat ds rs (decode ds.length x) hlen).mp hsat
    let q := liftCount ds (decode ds.length x) hh.right
    exact ⟨.sat q.result.pairs ⟨q.result.valid,q.result.output.symm ▸ hh.left⟩,
      p.work,c,q.visits,p.bound,cb,q.bound⟩
  | unsat w cert =>
    have wb : w < 2^(augmented ds rs).length := by
      rw [← p.agrees]
      exact wt
    have wc : MaskProvenance ds.length (augmented ds rs) (0,true) w := by
      rw [← p.agrees]
      exact cert
    exact ⟨.unsat w wb wc,p.work,c,0,p.bound,cb,Nat.zero_le _⟩

theorem totalSolve_bound (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    let t := totalSolve ds rs hw
    totalCharge ds.length rs.length (domainSize ds) t.preprocessing t.affine t.lifting ≤
      totalPolynomial ds.length rs.length (domainSize ds) := by
  dsimp
  exact totalCharge_bound _ _ _ _ _ _ (totalSolve ds rs hw).prep_bound
    (totalSolve ds rs hw).affine_bound (totalSolve ds rs hw).lift_bound

def totalOutput (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    BlockOutput × (Nat × Nat × Nat × Nat) :=
  let t := totalSolve ds rs hw
  let ans := match t.result with
    | .sat ps _ => BlockOutput.sat ps
    | .unsat w _ _ => BlockOutput.unsat w
  (ans,(t.preprocessing,t.affine,t.lifting,
    totalCharge ds.length rs.length (domainSize ds) t.preprocessing t.affine t.lifting))

theorem totalOutput_spec (ds : Domains) (rs : List MRow) (hw : InWidth ds.length rs) :
    match (totalOutput ds rs hw).1 with
    | .sat ps => OriginalSat ds rs ps
    | .unsat w => w < 2^(augmented ds rs).length ∧
      MaskProvenance ds.length (augmented ds rs) (0,true) w ∧ ¬ ∃ ps, OriginalSat ds rs ps := by
  unfold totalOutput
  generalize h : totalSolve ds rs hw = t
  obtain ⟨res,p,a,l,hp,ha,hl⟩ := t
  cases res with
  | sat ps h => exact h
  | unsat w hb hc => exact ⟨hb,hc,augmented_refutes ds rs w hc⟩

end ProctorPNP
#print axioms ProctorPNP.scanCount
#print axioms ProctorPNP.domainCount
#print axioms ProctorPNP.packCount
#print axioms ProctorPNP.prepCount
#print axioms ProctorPNP.pickCount
#print axioms ProctorPNP.liftCount
#print axioms ProctorPNP.totalCharge_bound
#print axioms ProctorPNP.totalSolve
#print axioms ProctorPNP.totalSolve_bound
#print axioms ProctorPNP.totalOutput_spec
