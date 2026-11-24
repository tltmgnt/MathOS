/-! F015: disjoint-domain integration with explicit Boolean coupling rows.
The affine and serialization charges are reported separately; preprocessing
and witness lifting are not yet charged in a finite-state model. -/
namespace ProctorPNP
open ProctorGF2

def fitRowTape (n : Nat) (r : Row) : Row :=
  ⟨fit n r.coeff,r.rhs⟩

theorem fitRowsTape_exact (n : Nat) (rs : List Row) :
    ExactRows n (rs.map (fitRowTape n)) := by
  induction rs with
  | nil => exact True.intro
  | cons r rs ih => exact ⟨fit_length n r.coeff,ih⟩

theorem fitRowsTape_sat (n : Nat) (rs : List Row) (x : List Bool)
    (hx : x.length = n) :
    AllSat (rs.map (fitRowTape n)) x ↔ AllSat rs x := by
  induction rs with
  | nil => exact Iff.rfl
  | cons r rs ih =>
    have e := fit_dot n r.coeff x hx
    exact ⟨fun h => ⟨e.symm.trans h.left,ih.mp h.right⟩,
      fun h => ⟨e.trans h.left,ih.mpr h.right⟩⟩

theorem exactRows_append (n : Nat) (a b : List Row)
    (ha : ExactRows n a) (hb : ExactRows n b) : ExactRows n (a++b) := by
  induction a with
  | nil => exact hb
  | cons r rs ih => exact ⟨ha.left,ih ha.right⟩

def augmentedTape (ds : Domains) (rs : List Row) : List Row :=
  rs ++ (domainRows ds).map (fitRowTape ds.length)

theorem augmentedTape_exact (ds : Domains) (rs : List Row)
    (h : ExactRows ds.length rs) : ExactRows ds.length (augmentedTape ds rs) :=
  exactRows_append _ _ _ h (fitRowsTape_exact _ _)

theorem augmentedTape_length (ds : Domains) (rs : List Row) :
    (augmentedTape ds rs).length ≤ rs.length+ds.length := by
  simp only [augmentedTape,List.length_append,List.length_map]
  exact Nat.add_le_add_left (domain_length ds) _

theorem augmentedTape_sat (ds : Domains) (rs : List Row) (x : List Bool)
    (hx : x.length = ds.length) :
    AllSat (augmentedTape ds rs) x ↔ AllSat rs x ∧ Projected ds x := by
  have e := (fitRowsTape_sat _ (domainRows ds) x hx).trans (domain_spec ds x hx)
  exact (append_sat rs _ x).trans
    ⟨fun h => ⟨h.left,e.mp h.right⟩,fun h => ⟨h.left,e.mpr h.right⟩⟩

def OriginalTapeSat (ds : Domains) (rs : List Row) (ps : List Pair) : Prop :=
  Allowed ds ps ∧ AllSat rs (ps.map gate)

theorem augmentedTape_refutes (ds : Domains) (rs : List Row) (w : List Bool)
    (hc : dualCheck ds.length (augmentedTape ds rs) w = true) :
    ¬ ∃ ps, OriginalTapeSat ds rs ps := by
  intro h
  obtain ⟨ps,hp,hs⟩ := h
  have p := project ds ps hp
  have hn := projected_length ds (ps.map gate) p
  have d := (dualCheck_iff _ _ _).mp hc
  exact dual_sound ds.length (augmentedTape ds rs) w d.left d.right
    ⟨ps.map gate,hn,(augmentedTape_sat ds rs _ hn).mpr ⟨hs,p⟩⟩

def TapeWireValid (ds : Domains) (rs : List Row) : List Bool → Prop
  | [] => False
  | true::bs => ∃ ps, parsePairs bs = some ps ∧ OriginalTapeSat ds rs ps
  | false::bs => bs.length = (augmentedTape ds rs).length ∧
      dualCheck ds.length (augmentedTape ds rs) bs = true ∧
      ¬ ∃ ps, OriginalTapeSat ds rs ps

structure BlockTapeRun (ds : Domains) (rs : List Row) where
  wire : List Bool
  valid : TapeWireValid ds rs wire
  affineSteps : Nat
  affineBound : affineSteps ≤ 4*(augmentedTape ds rs).length*(augmentedTape ds rs).length+
    4*(augmentedTape ds rs).length+
    tapeBudget ds.length (augmentedTape ds rs).length (augmentedTape ds rs).length ds.length
  wireSteps : Nat
  wireExact : wireSteps = 2*wire.length

def solveBlockTape (ds : Domains) (rs : List Row)
    (h : ExactRows ds.length rs) : BlockTapeRun ds rs := by
  let orig := augmentedTape ds rs
  let a := initTape ds.length orig (augmentedTape_exact ds rs h)
  let s := solveTape orig ds.length ds.length id a.tags (Nat.le_refl _)
  have hb := s.bound
  rw [a.size] at hb
  have bound := Nat.add_le_add a.bound hb
  cases e : s.result with
  | sat x hx hs =>
    have good : AllSat orig x := a.same ▸ hs
    have p := (augmentedTape_sat ds rs x hx).mp good
    let lift := liftExec ds x p.right
    have valid : OriginalTapeSat ds rs lift.pairs := ⟨lift.valid,lift.output.symm ▸ p.left⟩
    let c := copyCells (true::pairBits lift.pairs)
    have spec := copyCells_spec (true::pairBits lift.pairs)
    have v : TapeWireValid ds rs (true::pairBits lift.pairs) :=
      ⟨lift.pairs,pair_roundtrip _,valid⟩
    exact ⟨c.value,spec.left.symm ▸ v,a.steps+s.steps,bound,c.steps,
      spec.right.trans (congrArg (fun n => 2*n) (congrArg List.length spec.left).symm)⟩
  | unsat w hw hr hl =>
    have hc : dualCheck ds.length orig w = true := (dualCheck_iff _ _ _).mpr ⟨hr,hl⟩
    let c := copyCells (false::w)
    have spec := copyCells_spec (false::w)
    have v : TapeWireValid ds rs (false::w) :=
      ⟨hw,hc,augmentedTape_refutes ds rs w hc⟩
    exact ⟨c.value,spec.left.symm ▸ v,a.steps+s.steps,bound,c.steps,
      spec.right.trans (congrArg (fun n => 2*n) (congrArg List.length spec.left).symm)⟩

theorem blockTape_valid (ds : Domains) (rs : List Row) (h : ExactRows ds.length rs) :
    TapeWireValid ds rs (solveBlockTape ds rs h).wire :=
  (solveBlockTape ds rs h).valid

end ProctorPNP
#print axioms ProctorPNP.fitRowsTape_exact
#print axioms ProctorPNP.fitRowsTape_sat
#print axioms ProctorPNP.augmentedTape_exact
#print axioms ProctorPNP.augmentedTape_length
#print axioms ProctorPNP.augmentedTape_sat
#print axioms ProctorPNP.augmentedTape_refutes
#print axioms ProctorPNP.solveBlockTape
#print axioms ProctorPNP.blockTape_valid
