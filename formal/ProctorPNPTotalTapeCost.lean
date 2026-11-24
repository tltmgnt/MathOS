/-! F016: total structural Boolean-tape charges for the materialized
disjoint-domain solver. Not a finite-state simulation or a host runtime bound. -/
namespace ProctorPNP
open ProctorGF2

def preTapeCharge (n r scans pads generated : Nat) : Nat :=
  4*scans+4*pads+(4*n+4)*generated+4*n+2*r+2

def preTapeBudget (n r q : Nat) : Nat :=
  preTapeCharge n r (3*q) (n*n) n

def affineTapeBudget (n m : Nat) : Nat :=
  4*m*m+4*m+tapeBudget n m m n

def liftTapeBudget (n q : Nat) : Nat := 4*q+4*n

def totalTapeBudget (n r q m : Nat) : Nat :=
  preTapeBudget n r q + affineTapeBudget n m + liftTapeBudget n q + 5*(2*n+r+1)

theorem preTape_bound (n r q s p g : Nat)
    (hs : s ≤ 3*q) (hp : p ≤ n*n) (hg : g ≤ n) :
    preTapeCharge n r s p g ≤ preTapeBudget n r q := by
  unfold preTapeBudget preTapeCharge
  have a := Nat.mul_le_mul_left 4 hs
  have b := Nat.mul_le_mul_left 4 hp
  have c := Nat.mul_le_mul_left (4*n+4) hg
  omega

theorem affineTape_mono (n N m M : Nat) (hn : n ≤ N) (hm : m ≤ M) :
    affineTapeBudget n m ≤ affineTapeBudget N M := by
  have h1 : 4*m*m ≤ 4*M*M := Nat.mul_le_mul (Nat.mul_le_mul_left 4 hm) hm
  have h2 : 4*m ≤ 4*M := Nat.mul_le_mul_left 4 hm
  have h3 : 2*m ≤ 2*M := Nat.mul_le_mul_left 2 hm
  have h4 : 4*n ≤ 4*N := Nat.mul_le_mul_left 4 hn
  have h5 : 4*(n+m+1)+6 ≤ 4*(N+M+1)+6 := by omega
  have h6 := Nat.mul_le_mul hm h5
  have hc : columnBudget n m m ≤ columnBudget N M M := by
    unfold columnBudget
    omega
  have h7 := Nat.mul_le_mul hn hc
  unfold affineTapeBudget tapeBudget
  omega

theorem totalTape_mono (n r q m S : Nat)
    (hn : n ≤ S) (hr : r ≤ S) (hq : q ≤ S) (hm : m ≤ S) :
    totalTapeBudget n r q m ≤ totalTapeBudget S S S S := by
  have ha := affineTape_mono n S m S hn hm
  have h1 : 4*(3*q) ≤ 4*(3*S) := by omega
  have h2 := Nat.mul_le_mul_left 4 (Nat.mul_le_mul hn hn)
  have h3 : 4*n+4 ≤ 4*S+4 := by omega
  have h4 := Nat.mul_le_mul h3 hn
  unfold totalTapeBudget preTapeBudget preTapeCharge liftTapeBudget
  omega

-- One global marker, one domain header per block, two cells per listed pair,
-- one row header and n+1 payload cells per coupling row.
def inputTapeSize (n r q : Nat) : Nat := 1+n+r+2*q+r*(n+1)

def inputTapePolynomial (S : Nat) : Nat := totalTapeBudget S S S S

structure TotalTapeRun (ds : Domains) (rs : List Row) where
  wire : List Bool
  valid : TapeWireValid ds rs wire
  preprocess : Nat
  affine : Nat
  lifting : Nat
  construction : Nat
  copying : Nat
  preBound : preprocess ≤ preTapeBudget ds.length rs.length (pairCount ds)
  affineBound : affine ≤ affineTapeBudget ds.length (rs.length+ds.length)
  liftBound : lifting ≤ liftTapeBudget ds.length (pairCount ds)
  constructionExact : construction = 3*wire.length
  copyExact : copying = 2*wire.length
  lengthBound : wire.length ≤ 2*ds.length+rs.length+1

def finishTotalTape (ds : Domains) (rs : List Row) (bs : List Bool)
    (v : TapeWireValid ds rs bs) (hl : bs.length ≤ 2*ds.length+rs.length+1)
    (p a l : Nat)
    (hp : p ≤ preTapeBudget ds.length rs.length (pairCount ds))
    (ha : a ≤ affineTapeBudget ds.length (rs.length+ds.length))
    (hL : l ≤ liftTapeBudget ds.length (pairCount ds)) : TotalTapeRun ds rs := by
  let c := copyCells bs
  have e := copyCells_spec bs
  have len : c.value.length = bs.length := congrArg List.length e.left
  exact ⟨c.value,e.left.symm ▸ v,p,a,l,3*bs.length,c.steps,hp,ha,hL,
    by rw [len],e.right.trans (congrArg (fun k => 2*k) len.symm),by rw [len]; exact hl⟩

-- The F012 traversals count actual domain scans, prefix pads and witness
-- visits. Fitting and wire construction use analytical per-length charges.
-- The complete affine phase uses F014's instrumented Boolean tape solver.
def solveTotalTape (ds : Domains) (rs : List Row)
    (h : ExactRows ds.length rs) : TotalTapeRun ds rs := by
  let pre := buildDomains ds
  let orig := rs ++ pre.rows.map (fitRowTape ds.length)
  have eq : orig = augmentedTape ds rs := by
    change rs ++ pre.rows.map (fitRowTape ds.length) = _
    unfold augmentedTape
    rw [pre.same]
  have hw : ExactRows ds.length orig := eq.symm ▸ augmentedTape_exact ds rs h
  have hg : pre.rows.length ≤ ds.length := by rw [pre.same]; exact domain_length ds
  let pc := preTapeCharge ds.length rs.length pre.scans pre.pads pre.rows.length
  have hp : pc ≤ preTapeBudget ds.length rs.length (pairCount ds) :=
    preTape_bound _ _ _ _ _ _ pre.scans_bound pre.pads_bound hg
  let a := initTape ds.length orig hw
  let s := solveTape orig ds.length ds.length id a.tags (Nat.le_refl _)
  have hb := s.bound
  rw [a.size] at hb
  have ha : a.steps+s.steps ≤ affineTapeBudget ds.length orig.length :=
    Nat.add_le_add a.bound hb
  have hm : orig.length ≤ rs.length+ds.length := by rw [eq]; exact augmentedTape_length ds rs
  have hac := Nat.le_trans ha (affineTape_mono ds.length ds.length orig.length
    (rs.length+ds.length) (Nat.le_refl _) hm)
  cases e : s.result with
  | sat x hx hs =>
    have good : AllSat orig x := a.same ▸ hs
    have p := (augmentedTape_sat ds rs x hx).mp (eq ▸ good)
    let l := liftCount ds x p.right
    have valid : OriginalTapeSat ds rs l.result.pairs :=
      ⟨l.result.valid,l.result.output.symm ▸ p.left⟩
    have v : TapeWireValid ds rs (true::pairBits l.result.pairs) :=
      ⟨l.result.pairs,pair_roundtrip _,valid⟩
    have hl : (true::pairBits l.result.pairs).length ≤ 2*ds.length+rs.length+1 := by
      simp only [List.length_cons,pairBits_length,allowed_length ds l.result.pairs l.result.valid]
      omega
    have hL : 4*l.visits+4*ds.length ≤ liftTapeBudget ds.length (pairCount ds) := by
      unfold liftTapeBudget
      have := l.bound
      omega
    exact finishTotalTape ds rs _ v hl pc (a.steps+s.steps) (4*l.visits+4*ds.length) hp hac hL
  | unsat w hw hr hl =>
    have hc : dualCheck ds.length orig w = true := (dualCheck_iff _ _ _).mpr ⟨hr,hl⟩
    have c : dualCheck ds.length (augmentedTape ds rs) w = true := eq ▸ hc
    have v : TapeWireValid ds rs (false::w) :=
      ⟨eq ▸ hw,c,augmentedTape_refutes ds rs w c⟩
    have hlen : (false::w).length ≤ 2*ds.length+rs.length+1 := by
      simp only [List.length_cons,hw]
      omega
    exact finishTotalTape ds rs _ v hlen pc (a.steps+s.steps) 0 hp hac (Nat.zero_le _)

def totalTapeSteps {ds rs} (x : TotalTapeRun ds rs) : Nat :=
  x.preprocess+x.affine+x.lifting+x.construction+x.copying

theorem totalTape_valid (ds : Domains) (rs : List Row) (h : ExactRows ds.length rs) :
    TapeWireValid ds rs (solveTotalTape ds rs h).wire :=
  (solveTotalTape ds rs h).valid

theorem totalTape_bound (ds : Domains) (rs : List Row) (h : ExactRows ds.length rs) :
    totalTapeSteps (solveTotalTape ds rs h) ≤
      totalTapeBudget ds.length rs.length (pairCount ds) (rs.length+ds.length) := by
  let s := solveTotalTape ds rs h
  have p := s.preBound
  have a := s.affineBound
  have l := s.liftBound
  have c := s.constructionExact
  have w := s.copyExact
  have b := s.lengthBound
  change totalTapeSteps s ≤ _
  unfold totalTapeSteps totalTapeBudget
  omega

theorem totalTape_input_bound (ds : Domains) (rs : List Row) (h : ExactRows ds.length rs) :
    totalTapeSteps (solveTotalTape ds rs h) ≤
      inputTapePolynomial (inputTapeSize ds.length rs.length (pairCount ds)) := by
  let S := inputTapeSize ds.length rs.length (pairCount ds)
  have hn : ds.length ≤ S := by unfold S inputTapeSize; omega
  have hr : rs.length ≤ S := by unfold S inputTapeSize; omega
  have hq : pairCount ds ≤ S := by unfold S inputTapeSize; omega
  have hm : rs.length+ds.length ≤ S := by unfold S inputTapeSize; omega
  exact Nat.le_trans (totalTape_bound ds rs h) (totalTape_mono _ _ _ _ S hn hr hq hm)

end ProctorPNP
#print axioms ProctorPNP.preTape_bound
#print axioms ProctorPNP.affineTape_mono
#print axioms ProctorPNP.totalTape_mono
#print axioms ProctorPNP.finishTotalTape
#print axioms ProctorPNP.solveTotalTape
#print axioms ProctorPNP.totalTape_valid
#print axioms ProctorPNP.totalTape_bound
#print axioms ProctorPNP.totalTape_input_bound
