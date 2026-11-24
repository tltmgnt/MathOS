/-! F034: polynomial terminal budgets under explicit structural caps.
All bounds concern the selected charges, not machine time. -/
namespace ProctorTerminalPolynomial
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group)
open ProctorCapacityReplay (RefRow Certificate getAt demandAt indices)
open ProctorCapacityMeter (visitsBudget distinctBudget conflictBudget tupleBudget wordsBudget groupBudget differentBudget coverageBudget capacityBudget capacityMeter capacity_bound)
open ProctorPolynomialMeter (formulaMass mass_rows lookup_mass visits_uniform words_uniform wordUnit supportMass sum_quadratic)
open ProctorChainMeter (refBudget refsBudget)
open ProctorExecutableReplay (lookup)
open ProctorXorReplay (Block)
open ProctorXorMeter (patternBudget patternsBudget blockBudget xorBudget xorMeter xor_bound sumBudget)

private theorem zero_mul_local (k : Nat) : 0*k=0 := by
  induction k with
  | zero => rfl
  | succ k ih => exact ih

private theorem one_mul_local (k : Nat) : 1*k=k := by
  induction k with
  | zero => rfl
  | succ k ih => exact congrArg Nat.succ ih

private theorem add_mul_local (a b k : Nat) : (a+b)*k=a*k+b*k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change (a+b)*k+(a+b)=(a*k+a)+(b*k+b)
    rw [ih]
    calc
      (a*k+b*k)+(a+b) = a*k+(b*k+(a+b)) := Nat.add_assoc _ _ _
      _ = a*k+((b*k+a)+b) := congrArg (fun z => a*k+z) (Nat.add_assoc _ _ _).symm
      _ = a*k+((a+b*k)+b) := congrArg (fun z => a*k+(z+b)) (Nat.add_comm _ _)
      _ = a*k+(a+(b*k+b)) := congrArg (fun z => a*k+z) (Nat.add_assoc _ _ _)
      _ = (a*k+a)+(b*k+b) := (Nat.add_assoc _ _ _).symm

theorem mul_mono {a b c d : Nat} (h : a≤b) (g : c≤d) :
    a*c≤b*d := by
  have hl : ∀ k : Nat, a*k≤b*k := by
    intro k
    induction k with
    | zero => exact Nat.le_refl 0
    | succ k ih => exact Nat.add_le_add ih h
  have hr : b*c≤b*d := by
    induction g with
    | refl => exact Nat.le_refl _
    | step h ih => exact Nat.le_trans ih (Nat.le_add_right _ _)
  exact Nat.le_trans (hl c) hr

def mass {α : Type} (w : α → Nat) : List α → Nat
  | [] => 0
  | a::as => w a+mass w as

theorem weighted_visits {α : Type} (q w : α → Nat) (xs : List α)
    (K : Nat) (h : ∀ a ∈ xs, q a+1≤w a*K) :
    visitsBudget q xs≤mass w xs*K := by
  induction xs with
  | nil => exact Nat.zero_le _
  | cons a as ih =>
    change q a+visitsBudget q as+1≤(w a+mass w as)*K
    rw [add_mul_local]
    have ha := h a (List.Mem.head _)
    have ht := ih (fun b hb => h b (List.Mem.tail _ hb))
    calc
      q a+visitsBudget q as+1 = (q a+1)+visitsBudget q as := by
        rw [Nat.add_assoc,Nat.add_comm (visitsBudget q as) 1,← Nat.add_assoc]
      _ ≤ w a*K+mass w as*K := Nat.add_le_add ha ht

private theorem member_mass {α : Type} (w : α → Nat) (xs : List α)
    (a : α) (h : a ∈ xs) : w a≤mass w xs := by
  induction xs with
  | nil => cases h
  | cons b bs ih =>
    cases h with
    | head => exact Nat.le_add_right _ _
    | tail _ hm => exact Nat.le_trans (ih hm) (Nat.le_add_left _ _)

private theorem length_mass {α : Type} (w : α → Nat) (xs : List α)
    (h : ∀ a, 1≤w a) : xs.length≤mass w xs := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change as.length+1≤w a+mass w as
    rw [Nat.add_comm (w a) (mass w as)]
    exact Nat.add_le_add ih (h a)

def rowWeight (r : RefRow) : Nat := r.row.length+1
def groupWeight (g : Group) : Nat := g.literals.length+1
def blockWeight (b : Block) : Nat := 1+b.support.length+mass rowWeight b.refs

theorem ref_row_mass (rs : List RefRow) (r : RefRow) (h : r ∈ rs) :
    r.row.length≤mass rowWeight rs :=
  Nat.le_trans (Nat.le_succ _) (member_mass rowWeight rs r h)

theorem refs_poly (f : Formula) (rs : List RefRow) (B : Nat)
    (hf : formulaMass f≤B) (hr : mass rowWeight rs≤B) :
    refsBudget f rs≤B*(B+(B+1)) := by
  have rows := Nat.le_trans (mass_rows f) hf
  have one : ∀ r : RefRow, refBudget f r≤B+(B+1) := by
    intro r
    unfold refBudget
    cases e : lookup f r.index with
    | none =>
      change f.length+0≤B+(B+1)
      exact Nat.le_trans rows (Nat.le_add_right _ _)
    | some row =>
      change f.length+(row.length+1)≤B+(B+1)
      exact Nat.add_le_add rows (Nat.succ_le_succ (Nat.le_trans (lookup_mass f r.index row e) hf))
  have bound : ∀ xs : List RefRow, refsBudget f xs≤xs.length*(B+(B+1)) := by
    intro xs
    induction xs with
    | nil => exact Nat.zero_le _
    | cons r rs ih =>
      change refBudget f r+refsBudget f rs≤(rs.length+1)*(B+(B+1))
      rw [add_mul_local,one_mul_local,Nat.add_comm (rs.length*(B+(B+1))) (B+(B+1))]
      exact Nat.add_le_add (one r) ih
  exact Nat.le_trans (bound rs) (mul_mono
    (Nat.le_trans (length_mass rowWeight rs (fun _ => Nat.succ_le_succ (Nat.zero_le _))) hr)
    (Nat.le_refl _))

theorem distinct_poly (xs : Clause) (B : Nat) (h : xs.length≤B) :
    distinctBudget xs≤xs.length*B := by
  induction xs with
  | nil => exact Nat.zero_le _
  | cons a as ih =>
    have ht := Nat.le_trans (Nat.le_succ as.length) h
    change as.length+distinctBudget as≤(as.length+1)*B
    rw [add_mul_local,one_mul_local,Nat.add_comm (as.length*B) B]
    exact Nat.add_le_add ht (ih ht)

-- Per reference: its literal occurrences each cost at most 2k+1,
-- plus one reference visit. Use row-weight aggregation, not maxima.
theorem conflict_poly (rs : List RefRow) (ys : Clause) (B : Nat)
    (hr : mass rowWeight rs≤B) (hy : ys.length≤3) :
    conflictBudget rs ys≤B*7 := by
  have hi : visitsBudget (fun _ : Literal => 1) ys≤6 :=
    Nat.le_trans (visits_uniform _ ys 1 (fun _ => Nat.le_refl 1))
      (mul_mono hy (Nat.le_refl 2))
  unfold conflictBudget
  apply Nat.le_trans (weighted_visits _ rowWeight rs 7 _)
    (mul_mono hr (Nat.le_refl 7))
  intro r _
  have h := visits_uniform (fun _ : Literal => visitsBudget (fun _ : Literal => 1) ys)
    r.row 6 (fun _ => hi)
  unfold rowWeight
  rw [add_mul_local,one_mul_local]
  exact Nat.add_le_add h (by decide : 1≤7)

def leafUnit (B : Nat) : Nat := 9+B*7

theorem tuple_poly (rs : List RefRow) (ys : Clause) (B : Nat)
    (hr : mass rowWeight rs≤B) (hy : ys.length≤3) :
    tupleBudget rs ys≤leafUnit B :=
  Nat.add_le_add (Nat.le_trans (distinct_poly ys 3 hy)
    (mul_mono hy (Nat.le_refl 3))) (conflict_poly rs ys B hr hy)

-- With g<=B and B>=1, for k=1,2,3 charge g times a
-- quadratic per-symbol factor. A zero-size alphabet is allowed.
def wordFactor (B L : Nat) : Nat := B*(B*(L+1)+1)+1

theorem word_linear (g B L k : Nat) (hg : g≤B)
    (hb : 1≤B) (hk : k≤2) :
    wordUnit g (k+1) L≤g*wordFactor B L := by
  have h1 : L+1≤B*(L+1) := by
    have h := mul_mono hb (Nat.le_refl (L+1))
    rw [one_mul_local] at h
    exact h
  have h2 : B*(L+1)+1≤B*(B*(L+1)+1) := by
    have h := mul_mono hb (Nat.le_refl (B*(L+1)+1))
    rw [one_mul_local] at h
    exact h
  cases k with
  | zero =>
    change g*(L+1)≤g*wordFactor B L
    exact mul_mono (Nat.le_refl _) (Nat.le_trans h1
      (Nat.le_trans (Nat.le_succ _) (Nat.le_trans h2 (Nat.le_succ _))))
  | succ k =>
    cases k with
    | zero =>
      change g*(g*(L+1)+1)≤g*wordFactor B L
      exact mul_mono (Nat.le_refl _) (Nat.le_trans
        (Nat.succ_le_succ (mul_mono hg (Nat.le_refl _)))
        (Nat.le_trans h2 (Nat.le_succ _)))
    | succ k =>
      cases k with
      | zero =>
        change g*(g*(g*(L+1)+1)+1)≤g*wordFactor B L
        exact mul_mono (Nat.le_refl _) (Nat.succ_le_succ
          (mul_mono hg (Nat.succ_le_succ (mul_mono hg (Nat.le_refl _)))))
      | succ k =>
        exact (Nat.not_lt_zero _ (Nat.le_of_succ_le_succ
          (Nat.le_of_succ_le_succ hk))).elim

def groupFactor (B : Nat) : Nat := B+wordFactor B (leafUnit B)+2

theorem group_poly (rs : List RefRow) (g : Group) (B : Nat)
    (hb : 1≤B) (hr : mass rowWeight rs≤B) (hg : g.literals.length≤B) :
    groupBudget rs g+1≤groupWeight g*groupFactor B := by
  unfold groupBudget
  by_cases hc : g.cap≤2
  · rw [if_pos hc]
    have hw := words_uniform g.literals (g.cap+1) (tupleBudget rs) (leafUnit B)
      (fun ys e => tuple_poly rs ys B hr (e.symm ▸ Nat.succ_le_succ hc))
    have hw' := Nat.le_trans hw (word_linear g.literals.length B (leafUnit B) g.cap hg hb hc)
    have hd := distinct_poly g.literals B hg
    -- distribute the outer g+1 over the single shared factor.
    unfold groupWeight groupFactor
    rw [add_mul_local,one_mul_local]
    have ha : g.literals.length*B+g.literals.length*wordFactor B (leafUnit B)≤
        g.literals.length*(B+wordFactor B (leafUnit B)+2) := by
      -- right distributivity is definitional in the second argument.
      change g.literals.length*B+g.literals.length*wordFactor B (leafUnit B)≤
        g.literals.length*(B+wordFactor B (leafUnit B))+g.literals.length+g.literals.length
      have dist : ∀ a b : Nat, g.literals.length*(a+b)=g.literals.length*a+g.literals.length*b := by
        intro a b
        induction b with
        | zero => rfl
        | succ b ih =>
          change g.literals.length*(a+b)+g.literals.length=
            g.literals.length*a+(g.literals.length*b+g.literals.length)
          rw [ih,Nat.add_assoc]
      rw [dist]
      exact Nat.le_trans (Nat.le_add_right _ _) (Nat.le_add_right _ _)
    have htwo : 2≤B+wordFactor B (leafUnit B)+2 :=
      Nat.le_add_left _ _
    have hsum : distinctBudget g.literals+
        wordsBudget g.literals (g.cap+1) (tupleBudget rs) ≤
        g.literals.length*B+g.literals.length*wordFactor B (leafUnit B) :=
      Nat.add_le_add hd hw'
    calc
      distinctBudget g.literals+wordsBudget g.literals (g.cap+1) (tupleBudget rs)+1+1
          ≤ (g.literals.length*B+g.literals.length*wordFactor B (leafUnit B))+2 :=
        Nat.succ_le_succ (Nat.succ_le_succ hsum)
      _ ≤ g.literals.length*(B+wordFactor B (leafUnit B)+2)+
          (B+wordFactor B (leafUnit B)+2) := Nat.add_le_add ha htwo
  · rw [if_neg hc]
    unfold groupWeight groupFactor
    rw [add_mul_local,one_mul_local]
    exact Nat.le_trans (Nat.le_add_left _ _) (Nat.le_add_left _ _)

theorem groups_poly (rs : List RefRow) (gs : List Group) (B : Nat)
    (hb : 1≤B) (hr : mass rowWeight rs≤B) (hg : mass groupWeight gs≤B) :
    visitsBudget (groupBudget rs) gs≤B*groupFactor B :=
  Nat.le_trans (weighted_visits _ groupWeight gs _ (fun g hm =>
    group_poly rs g B hb hr (Nat.le_trans (Nat.le_succ _) (Nat.le_trans
      (member_mass groupWeight gs g hm) hg)))) (mul_mono hg (Nat.le_refl _))

theorem demand_mass (ds : List RefRow) (i : Nat) :
    (demandAt ds i).length≤mass rowWeight ds := by
  unfold demandAt
  cases e : getAt ds i with
  | none => exact Nat.zero_le _
  | some r => exact ref_row_mass ds r (ProctorCapacityReplay.getAt_mem ds i r e)

theorem indices_length (d : Nat) : (indices d).length=d := by
  induction d with
  | zero => rfl
  | succ d ih => exact congrArg Nat.succ ih

def pairUnit (B : Nat) : Nat := B+B+B*(B*2+1)+1

theorem different_poly (ds : List RefRow) (i j B : Nat)
    (hd : mass rowWeight ds≤B) : differentBudget ds i j≤pairUnit B := by
  unfold differentBudget pairUnit
  by_cases e : i=j
  · rw [if_pos e]
    exact Nat.le_add_left _ _
  · rw [if_neg e]
    have hl := Nat.le_trans (length_mass rowWeight ds
      (fun _ => Nat.succ_le_succ (Nat.zero_le _))) hd
    have hi := Nat.le_trans (demand_mass ds i) hd
    have hj := Nat.le_trans (demand_mass ds j) hd
    have hinner : visitsBudget (fun _ : Literal => 1) (demandAt ds j)≤B*2 :=
      Nat.le_trans (visits_uniform _ _ 1 (fun _ => Nat.le_refl 1))
        (mul_mono hj (Nat.le_refl _))
    have hout := Nat.le_trans (visits_uniform _ (demandAt ds i) (B*2)
      (fun _ => hinner)) (mul_mono hi (Nat.le_refl _))
    exact Nat.add_le_add (Nat.add_le_add (Nat.add_le_add hl hl) hout) (Nat.le_refl 1)

theorem pairs_poly (ds : List RefRow) (B : Nat) (hd : mass rowWeight ds≤B) :
    visitsBudget (fun i => visitsBudget (differentBudget ds i) (indices ds.length))
      (indices ds.length)≤B*(B*(pairUnit B+1)+1) := by
  have hl : (indices ds.length).length≤B := by
    rw [indices_length]
    exact Nat.le_trans (length_mass rowWeight ds (fun _ =>
      Nat.succ_le_succ (Nat.zero_le _))) hd
  have hi : ∀ i, visitsBudget (differentBudget ds i) (indices ds.length)≤B*(pairUnit B+1) :=
    fun i => Nat.le_trans (visits_uniform _ _ _ (fun j => different_poly ds i j B hd))
      (mul_mono hl (Nat.le_refl _))
  exact Nat.le_trans (visits_uniform _ _ _ hi) (mul_mono hl (Nat.le_refl _))

theorem coverage_poly (ds : List RefRow) (gs : List Group) (B : Nat)
    (hd : mass rowWeight ds≤B) (hg : mass groupWeight gs≤B) :
    coverageBudget ds gs≤B*(B+2) := by
  have hgroups : visitsBudget (fun g => g.literals.length) gs≤B := by
    have mulOne (a : Nat) : a*1=a := Nat.zero_add a
    have h := weighted_visits (fun g : Group => g.literals.length) groupWeight gs 1
      (fun g _ => by
        change g.literals.length+1≤(g.literals.length+1)*1
        rw [mulOne]
        exact Nat.le_refl _)
    rw [mulOne] at h
    exact Nat.le_trans h hg
  unfold coverageBudget
  apply Nat.le_trans (weighted_visits _ rowWeight ds (B+2) _)
    (mul_mono hd (Nat.le_refl _))
  intro r _
  have h := visits_uniform (fun _ : Literal => visitsBudget (fun g => g.literals.length) gs)
    r.row B (fun _ => hgroups)
  unfold rowWeight
  rw [add_mul_local,one_mul_local]
  exact Nat.add_le_add (Nat.le_trans h (mul_mono (Nat.le_refl _) (Nat.le_succ _)))
    (Nat.le_trans (by decide : 1≤2) (Nat.le_add_left _ _))

def capacityUnit (B : Nat) : Nat :=
  B*(B+(B+1)) + (B*(B+(B+1)) + (B*groupFactor B +
    (B*(B*(pairUnit B+1)+1) + (B*(B+2)+1))))

theorem capacity_poly (f : Formula) (c : Certificate) (B : Nat)
    (hb : 1≤B) (hf : formulaMass f≤B) (hd : mass rowWeight c.demands≤B)
    (hr : mass rowWeight c.conflicts≤B) (hg : mass groupWeight c.groups≤B) :
    capacityBudget f c≤capacityUnit B := by
  unfold capacityBudget capacityUnit
  exact Nat.add_le_add (refs_poly f c.demands B hf hd)
    (Nat.add_le_add (refs_poly f c.conflicts B hf hr)
      (Nat.add_le_add (groups_poly c.conflicts c.groups B hb hr hg)
        (Nat.add_le_add (pairs_poly c.demands B hd)
          (Nat.add_le_add (coverage_poly c.demands c.groups B hd hg) (Nat.le_refl 1)))))

theorem capacity_meter_poly (f : Formula) (c : Certificate) (B : Nat)
    (hb : 1≤B) (hf : formulaMass f≤B) (hd : mass rowWeight c.demands≤B)
    (hr : mass rowWeight c.conflicts≤B) (hg : mass groupWeight c.groups≤B) :
    (capacityMeter f c).2≤capacityUnit B :=
  Nat.le_trans (capacity_bound f c) (capacity_poly f c B hb hf hd hr hg)

theorem xor_visits_eq {α : Type} (q : α → Nat) (xs : List α) :
    ProctorXorMeter.visitsBudget q xs=visitsBudget q xs := by
  induction xs with
  | nil => rfl
  | cons a as ih =>
    change q a+ProctorXorMeter.visitsBudget q as+1=q a+visitsBudget q as+1
    rw [ih]

theorem pattern_poly (b : Block) (ls : Clause) (B : Nat)
    (hr : mass rowWeight b.refs≤B) (hl : ls.length≤5) :
    patternBudget b ls≤6+B*6 := by
  unfold patternBudget
  rw [xor_visits_eq]
  apply Nat.add_le_add (Nat.succ_le_succ hl)
  apply Nat.le_trans (weighted_visits _ rowWeight b.refs 6 _)
    (mul_mono hr (Nat.le_refl _))
  intro r _
  rw [xor_visits_eq]
  have h := visits_uniform (fun _ : Literal => ls.length) r.row 5 (fun _ => hl)
  unfold rowWeight
  rw [add_mul_local,one_mul_local]
  exact Nat.add_le_add h (by decide : 1≤6)

def binaryUnit : Nat → Nat → Nat
  | 0,L => L
  | k+1,L => binaryUnit k L+binaryUnit k L+1

theorem binary_uniform (vs : List Nat) (q : Clause → Nat) (L : Nat)
    (h : ∀ ls, ls.length=vs.length → q ls≤L) :
    patternsBudget vs q≤binaryUnit vs.length L := by
  induction vs generalizing q with
  | nil => exact h [] rfl
  | cons v vs ih =>
    exact Nat.add_le_add (Nat.add_le_add
      (ih (fun ls => q ((v,false)::ls)) (fun ls e => h ((v,false)::ls) (congrArg Nat.succ e)))
      (ih (fun ls => q ((v,true)::ls)) (fun ls e => h ((v,true)::ls) (congrArg Nat.succ e))))
      (Nat.le_refl 1)

theorem binary_five (k L : Nat) (h : k≤5) :
    binaryUnit k L≤binaryUnit 5 L := by
  have step : ∀ n, binaryUnit n L≤binaryUnit (n+1) L :=
    fun n => Nat.le_trans (Nat.le_add_right _ _) (Nat.le_succ _)
  have mono : ∀ j : Nat, k≤j → binaryUnit k L≤binaryUnit j L := by
    intro j hj
    induction hj with
    | refl => exact Nat.le_refl _
    | step _ ih => exact Nat.le_trans ih (step _)
  exact mono 5 h

def blockUnit (B : Nat) : Nat := B*(B+(B+1))+binaryUnit 5 (6+B*6)+1

theorem block_poly (f : Formula) (b : Block) (B : Nat)
    (hf : formulaMass f≤B) (hr : mass rowWeight b.refs≤B) :
    blockBudget f b≤blockUnit B := by
  unfold blockBudget blockUnit
  by_cases h : b.support.length≤5
  · rw [if_pos h]
    have hp := Nat.le_trans (binary_uniform b.support (patternBudget b) (6+B*6)
      (fun ls e => pattern_poly b ls B hr (e.symm ▸ h))) (binary_five _ _ h)
    exact Nat.add_le_add (Nat.add_le_add (refs_poly f b.refs B hf hr) hp) (Nat.le_refl 1)
  · rw [if_neg h]
    exact Nat.le_add_left _ _

def xorUnit (B : Nat) : Nat := B*(blockUnit B+1)+B*B+B+1

theorem xor_poly (f : Formula) (bs : List Block) (B : Nat)
    (hf : formulaMass f≤B) (hb : mass blockWeight bs≤B)
    (hu : supportMass bs≤B) :
    xorBudget f bs≤xorUnit B := by
  have hlen := Nat.le_trans (length_mass blockWeight bs (fun b =>
    Nat.le_trans (Nat.le_add_right 1 b.support.length) (Nat.le_add_right _ _))) hb
  have hblock : ∀ b ∈ bs, blockBudget f b≤blockUnit B := by
    intro b hm
    apply block_poly f b B hf
    exact Nat.le_trans (Nat.le_add_left _ _) (Nat.le_trans (member_mass blockWeight bs b hm) hb)
  have uniform : ∀ xs : List Block, (∀ b ∈ xs, blockBudget f b≤blockUnit B) →
      visitsBudget (blockBudget f) xs≤xs.length*(blockUnit B+1) := by
    intro xs hxs
    induction xs with
    | nil => exact Nat.zero_le _
    | cons b bs ih =>
      change blockBudget f b+visitsBudget (blockBudget f) bs+1≤(bs.length+1)*(blockUnit B+1)
      rw [add_mul_local,one_mul_local]
      calc
        blockBudget f b+visitsBudget (blockBudget f) bs+1≤
            blockUnit B+bs.length*(blockUnit B+1)+1 :=
          Nat.add_le_add (Nat.add_le_add (hxs b (List.Mem.head _))
            (ih (fun a ha => hxs a (List.Mem.tail _ ha)))) (Nat.le_refl 1)
        _ = bs.length*(blockUnit B+1)+(blockUnit B+1) := by
          rw [Nat.add_comm (blockUnit B) (bs.length*(blockUnit B+1)),Nat.add_assoc]
  have hvisit := uniform bs hblock
  unfold xorBudget xorUnit
  rw [xor_visits_eq]
  exact Nat.add_le_add (Nat.add_le_add (Nat.add_le_add
    (Nat.le_trans hvisit (mul_mono hlen (Nat.le_refl _)))
    (Nat.le_trans (sum_quadratic bs) (mul_mono hu hu))) hlen) (Nat.le_refl 1)

theorem xor_meter_poly (f : Formula) (bs : List Block) (B : Nat)
    (hf : formulaMass f≤B) (hb : mass blockWeight bs≤B) (hu : supportMass bs≤B) :
    (xorMeter f bs).2≤xorUnit B :=
  Nat.le_trans (xor_bound f bs) (xor_poly f bs B hf hb hu)

end ProctorTerminalPolynomial

#print axioms ProctorTerminalPolynomial.mul_mono
#print axioms ProctorTerminalPolynomial.weighted_visits
#print axioms ProctorTerminalPolynomial.ref_row_mass
#print axioms ProctorTerminalPolynomial.refs_poly
#print axioms ProctorTerminalPolynomial.distinct_poly
#print axioms ProctorTerminalPolynomial.conflict_poly
#print axioms ProctorTerminalPolynomial.tuple_poly
#print axioms ProctorTerminalPolynomial.word_linear
#print axioms ProctorTerminalPolynomial.group_poly
#print axioms ProctorTerminalPolynomial.groups_poly
#print axioms ProctorTerminalPolynomial.demand_mass
#print axioms ProctorTerminalPolynomial.indices_length
#print axioms ProctorTerminalPolynomial.different_poly
#print axioms ProctorTerminalPolynomial.pairs_poly
#print axioms ProctorTerminalPolynomial.coverage_poly
#print axioms ProctorTerminalPolynomial.capacity_poly
#print axioms ProctorTerminalPolynomial.capacity_meter_poly
#print axioms ProctorTerminalPolynomial.xor_visits_eq
#print axioms ProctorTerminalPolynomial.pattern_poly
#print axioms ProctorTerminalPolynomial.binary_uniform
#print axioms ProctorTerminalPolynomial.binary_five
#print axioms ProctorTerminalPolynomial.block_poly
#print axioms ProctorTerminalPolynomial.xor_poly
#print axioms ProctorTerminalPolynomial.xor_meter_poly
