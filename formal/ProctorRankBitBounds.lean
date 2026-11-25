/-! F035: explicit finite binary rank representation and comparison
equivalence. This proves a bit-width bound and a structural comparison
schedule, not a refinement to Lean's native natural arithmetic. -/
namespace ProctorRankBitBounds
open ProctorHallDeficiency
open ProctorTwoCNFModel (bit rank score R vertices model)
open ProctorImplicationPathDiscovery (arcs)
open ProctorOrdinaryCompleteness (variables)
open ProctorWireTokenBounds (variables_length)
open ProctorPathResourceBounds (occurrences)

theorem bit_le (b : Bool) : bit b≤1 := by
  cases b
  · exact Nat.zero_le _
  · exact Nat.le_refl _

theorem rank_lt_pow (p : Literal → Bool) (vs : List Literal) :
    rank p vs<2^vs.length := by
  induction vs with
  | nil => exact Nat.zero_lt_succ _
  | cons a as ih =>
    change bit (p a)+2*rank p as<2^(as.length+1)
    rw [Nat.pow_succ,Nat.mul_comm (2^as.length) 2]
    have h := Nat.mul_le_mul_left 2 (Nat.succ_le_of_lt ih)
    rw [Nat.mul_succ] at h
    have hb := Nat.add_le_add_right (bit_le (p a)) (2*rank p as)
    have hs : 1+2*rank p as<2*rank p as+2 := by
      rw [Nat.add_comm 1]
      exact Nat.lt_succ_self _
    exact Nat.lt_of_lt_of_le (Nat.lt_of_le_of_lt hb hs) h

theorem vertices_length (vs : List Nat) : (vertices vs).length=2*vs.length := by
  induction vs with
  | nil => rfl
  | cons v vs ih =>
    change (vertices vs).length+2=2*(vs.length+1)
    rw [ih,Nat.mul_succ]

theorem score_lt_pow (f : Formula) (a : Literal) :
    score f a<2^(2*occurrences f) := by
  have h := rank_lt_pow (R (arcs f) a) (vertices (variables f))
  rw [vertices_length,variables_length] at h
  exact h

def bits (p : Literal → Bool) : List Literal → List Bool
  | [] => []
  | a::as => p a::bits p as

def value : List Bool → Nat
  | [] => 0
  | b::bs => bit b+2*value bs

theorem bits_length (p : Literal → Bool) (vs : List Literal) :
    (bits p vs).length=vs.length := by
  induction vs with
  | nil => rfl
  | cons a as ih => exact congrArg Nat.succ ih

theorem bits_value (p : Literal → Bool) (vs : List Literal) :
    value (bits p vs)=rank p vs := by
  induction vs with
  | nil => rfl
  | cons a as ih =>
    change bit (p a)+2*value (bits p as)=bit (p a)+2*rank p as
    rw [ih]

-- Compare equally long little-endian bit lists, tail first. Higher
-- bits override lower bits. None denotes unequal widths.
inductive Order where
  | lt
  | eq
  | gt
  deriving DecidableEq, Repr

def lowCompare (a b : Bool) : Order :=
  match a,b with
  | false,true => .lt
  | true,false => .gt
  | _,_ => .eq

def compareBits : List Bool → List Bool → Option Order
  | [],[] => some .eq
  | a::as,b::bs =>
    match compareBits as bs with
    | none => none
    | some .eq => some (lowCompare a b)
    | some .lt => some .lt
    | some .gt => some .gt
  | _,_ => none

def Meaning (a b : Nat) : Order → Prop
  | .lt => a<b
  | .eq => a=b
  | .gt => b<a

theorem low_meaning (a b : Bool) : Meaning (bit a) (bit b) (lowCompare a b) := by
  cases a <;> cases b <;> first | exact rfl | exact Nat.zero_lt_succ _

theorem low_add_meaning (a b : Bool) (n : Nat) :
    Meaning (bit a+2*n) (bit b+2*n) (lowCompare a b) := by
  cases a <;> cases b
  · rfl
  · exact Nat.add_lt_add_right (Nat.zero_lt_succ 0) _
  · exact Nat.add_lt_add_right (Nat.zero_lt_succ 0) _
  · rfl

theorem high_lt (a b : Bool) (n m : Nat) (h : n<m) :
    bit a+2*n<bit b+2*m := by
  have h1 := Nat.add_le_add_right (bit_le a) (2*n)
  have h2 : 1+2*n<2*n+2 := by
    rw [Nat.add_comm 1]
    exact Nat.lt_succ_self _
  have h3 := Nat.mul_le_mul_left 2 (Nat.succ_le_of_lt h)
  rw [Nat.mul_succ] at h3
  have h4 : 2*m≤bit b+2*m := Nat.le_add_left _ _
  exact Nat.lt_of_lt_of_le (Nat.lt_of_le_of_lt h1 h2) (Nat.le_trans h3 h4)

theorem compare_sound (as bs : List Bool) (o : Order)
    (h : compareBits as bs=some o) : Meaning (value as) (value bs) o := by
  induction as generalizing bs o with
  | nil =>
    cases bs with
    | nil =>
      change some Order.eq=some o at h
      cases h
      rfl
    | cons b bs => cases h
  | cons a as ih =>
    cases bs with
    | nil => cases h
    | cons b bs =>
      unfold compareBits at h
      cases ht : compareBits as bs with
      | none => rw [ht] at h; cases h
      | some q =>
        rw [ht] at h
        have hm := ih bs q ht
        cases q with
        | lt =>
          change some Order.lt=some o at h
          cases h
          exact high_lt a b _ _ hm
        | eq =>
          change some (lowCompare a b)=some o at h
          cases h
          change Meaning (bit a+2*value as) (bit b+2*value bs) (lowCompare a b)
          change value as=value bs at hm
          rw [hm]
          exact low_add_meaning a b _
        | gt =>
          change some Order.gt=some o at h
          cases h
          exact high_lt b a _ _ hm

theorem compare_total (as bs : List Bool) (h : as.length=bs.length) :
    ∃ o, compareBits as bs=some o := by
  induction as generalizing bs with
  | nil =>
    cases bs with
    | nil => exact ⟨.eq,rfl⟩
    | cons b bs => exact (Nat.noConfusion h : False).elim
  | cons a as ih =>
    cases bs with
    | nil => exact (Nat.noConfusion h : False).elim
    | cons b bs =>
      have he : as.length=bs.length := Nat.succ.inj h
      obtain ⟨o,ho⟩ := ih bs he
      change ∃ q, (match compareBits as bs with
        | none => none
        | some .eq => some (lowCompare a b)
        | some .lt => some .lt
        | some .gt => some .gt)=some q
      rw [ho]
      cases o
      · exact ⟨.lt,rfl⟩
      · exact ⟨lowCompare a b,rfl⟩
      · exact ⟨.gt,rfl⟩

def scoreBits (f : Formula) (a : Literal) : List Bool :=
  bits (R (arcs f) a) (vertices (variables f))

theorem score_bits_length (f : Formula) (a : Literal) :
    (scoreBits f a).length=2*occurrences f := by
  unfold scoreBits
  rw [bits_length,vertices_length,variables_length]

theorem score_bits_value (f : Formula) (a : Literal) :
    value (scoreBits f a)=score f a :=
  bits_value _ _

def bitModel (f : Formula) : Assignment :=
  fun v => match compareBits (scoreBits f (v,true)) (scoreBits f (v,false)) with
    | some .lt => true
    | _ => false

theorem bit_model_eq (f : Formula) (v : Nat) : bitModel f v=model f v := by
  have he : (scoreBits f (v,true)).length=(scoreBits f (v,false)).length := by
    rw [score_bits_length,score_bits_length]
  obtain ⟨o,ho⟩ := compare_total _ _ he
  have hm := compare_sound _ _ o ho
  rw [score_bits_value,score_bits_value] at hm
  unfold bitModel model
  rw [ho]
  cases o with
  | lt =>
    change score f (v,true)<score f (v,false) at hm
    rw [if_pos hm] <;> rfl
  | eq =>
    change score f (v,true)=score f (v,false) at hm
    rw [if_neg (fun h => Nat.lt_irrefl _ (hm ▸ h))] <;> rfl
  | gt =>
    change score f (v,false)<score f (v,true) at hm
    rw [if_neg (Nat.not_lt_of_ge (Nat.le_of_lt hm))] <;> rfl

-- One paired position is visited per recursive comparison.
def compareCharge : List Bool → List Bool → Nat
  | _::as,_::bs => 1+compareCharge as bs
  | _,_ => 0

theorem compare_charge (as bs : List Bool) (h : as.length=bs.length) :
    compareCharge as bs=as.length := by
  induction as generalizing bs with
  | nil => rfl
  | cons a as ih =>
    cases bs with
    | nil => cases h
    | cons b bs =>
      change 1+compareCharge as bs=as.length+1
      rw [ih bs (Nat.succ.inj h),Nat.add_comm]

theorem model_compare_charge (f : Formula) (v : Nat) :
    compareCharge (scoreBits f (v,true)) (scoreBits f (v,false))=2*occurrences f := by
  rw [compare_charge,score_bits_length]
  rw [score_bits_length,score_bits_length]

end ProctorRankBitBounds

#print axioms ProctorRankBitBounds.bit_le
#print axioms ProctorRankBitBounds.rank_lt_pow
#print axioms ProctorRankBitBounds.vertices_length
#print axioms ProctorRankBitBounds.score_lt_pow
#print axioms ProctorRankBitBounds.bits_length
#print axioms ProctorRankBitBounds.bits_value
#print axioms ProctorRankBitBounds.low_meaning
#print axioms ProctorRankBitBounds.low_add_meaning
#print axioms ProctorRankBitBounds.high_lt
#print axioms ProctorRankBitBounds.compare_sound
#print axioms ProctorRankBitBounds.compare_total
#print axioms ProctorRankBitBounds.score_bits_length
#print axioms ProctorRankBitBounds.score_bits_value
#print axioms ProctorRankBitBounds.bit_model_eq
#print axioms ProctorRankBitBounds.compare_charge
#print axioms ProctorRankBitBounds.model_compare_charge
