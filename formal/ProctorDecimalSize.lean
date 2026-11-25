/-! F035: decimal word length and encoded byte accounting.
No unit-cost assumption about natural-number operations is made.
The upper bound is parameterized by a common decimal magnitude bound,
and the lower bound connects canonical input tokens to encoded length. -/
namespace ProctorDecimalSize
open ProctorDecimalEncoder (digits word encode quotient_positive)

private theorem len_append {α : Type} (xs ys : List α) :
    (xs++ys).length=xs.length+ys.length := by
  induction xs with
  | nil => exact (Nat.zero_add _).symm
  | cons a as ih =>
    change (as++ys).length+1=as.length+1+ys.length
    rw [ih,Nat.add_assoc as.length 1 ys.length,Nat.add_comm 1 ys.length,← Nat.add_assoc]

-- Same constructive identities as the verified decimal encoder.
private theorem sub_add_cancel' (a b : Nat) (h : a≤b) : b-a+a=b := by
  induction a generalizing b with
  | zero => rfl
  | succ a ih =>
    cases b with
    | zero => exact (Nat.not_succ_le_zero a h).elim
    | succ b =>
      rw [Nat.succ_sub_succ_eq_sub]
      exact congrArg Nat.succ (ih b (Nat.le_of_succ_le_succ h))

private theorem div_add_mod' (x y : Nat) : y*(x/y)+x%y=x := by
  induction x,y using Nat.div.inductionOn with
  | base x y h =>
    rw [Nat.div_eq x y,Nat.mod_eq x y,if_neg h,if_neg h,Nat.mul_zero,Nat.zero_add]
  | ind x y h ih =>
    rw [Nat.div_eq x y,Nat.mod_eq x y,if_pos h,if_pos h,Nat.mul_succ]
    rw [Nat.add_assoc,Nat.add_comm y ((x-y)%y),← Nat.add_assoc,ih]
    exact sub_add_cancel' y x h.right

theorem quotient_bound (n p : Nat) (h : n<10*p) : n/10<p := by
  by_cases e : n/10<p
  · exact e
  · have hh := Nat.mul_le_mul_left 10 (Nat.le_of_not_gt e)
    have hr := Nat.le_add_right (10*(n/10)) (n%10)
    rw [div_add_mod' n 10] at hr
    exact (Nat.not_le_of_gt h (Nat.le_trans hh hr)).elim

theorem quotient_strict (n : Nat) (h : ¬n<10) : n/10<n := by
  have hmul := Nat.mul_lt_mul_of_pos_right (by decide : 1<10) (quotient_positive n h)
  rw [Nat.one_mul] at hmul
  have hr := Nat.le_add_right (10*(n/10)) (n%10)
  rw [div_add_mod' n 10] at hr
  exact Nat.lt_of_lt_of_le hmul hr

theorem digits_length_bound (d fuel n : Nat) (h : n<10^(d+1)) :
    (digits fuel n).length≤d+1 := by
  induction d generalizing fuel n with
  | zero =>
    have hs : n<10 := h
    cases fuel with
    | zero => exact Nat.le_refl _
    | succ k =>
      change (if n<10 then [48+n] else digits k (n/10)++[48+n%10]).length≤1
      rw [if_pos hs]
      exact Nat.le_refl _
  | succ d ih =>
    cases fuel with
    | zero => exact Nat.succ_le_succ (Nat.zero_le _)
    | succ k =>
      change (if n<10 then [48+n] else digits k (n/10)++[48+n%10]).length≤d+1+1
      by_cases small : n<10
      · rw [if_pos small]
        exact Nat.succ_le_succ (Nat.zero_le _)
      · rw [if_neg small,len_append]
        have hp : n<10*(10^(d+1)) := by
          rw [Nat.mul_comm 10]
          exact h
        exact Nat.succ_le_succ (ih k (n/10) (quotient_bound n _ hp))

theorem word_length_bound (n d : Nat) (h : n<10^(d+1)) :
    (word n).length≤d+1 :=
  digits_length_bound d (n+1) n h

theorem digits_magnitude (fuel n : Nat) (h : n<fuel) :
    n<10^(digits fuel n).length := by
  induction fuel generalizing n with
  | zero => exact (Nat.not_lt_zero _ h).elim
  | succ k ih =>
    change n<10^(if n<10 then [48+n] else digits k (n/10)++[48+n%10]).length
    by_cases small : n<10
    · rw [if_pos small]
      exact small
    · rw [if_neg small,len_append]
      have hf := Nat.lt_of_lt_of_le (quotient_strict n small) (Nat.le_of_lt_succ h)
      have hq := ih (n/10) hf
      have hm := Nat.mod_lt n (by decide : 0<10)
      have hs := Nat.add_lt_add_left hm (10*(n/10))
      have hb := Nat.mul_le_mul_left 10 (Nat.succ_le_of_lt hq)
      rw [Nat.mul_succ] at hb
      rw [div_add_mod' n 10] at hs
      have he := Nat.lt_of_lt_of_le hs hb
      change n<10^((digits k (n/10)).length+1)
      rw [Nat.pow_succ,Nat.mul_comm]
      exact he

theorem word_magnitude (n : Nat) : n<10^(word n).length :=
  digits_magnitude (n+1) n (Nat.lt_succ_self n)

theorem pow_mono (a b : Nat) (h : a≤b) : 10^a≤10^b := by
  induction h with
  | refl => exact Nat.le_refl _
  | step h ih =>
    apply Nat.le_trans ih
    rw [Nat.pow_succ]
    have hh := Nat.mul_le_mul_left (10^_) (by decide : 1≤10)
    rw [Nat.mul_one] at hh
    exact hh

def byteCount : List Nat → Nat
  | [] => 0
  | n::ns => (word n).length+1+byteCount ns

theorem encode_length (ts : List Nat) : (encode ts).length=byteCount ts := by
  induction ts with
  | nil => rfl
  | cons n ns ih =>
    change (word n++10::encode ns).length=(word n).length+1+byteCount ns
    rw [len_append]
    change (word n).length+((encode ns).length+1)=_
    rw [ih,Nat.add_comm (byteCount ns) 1,← Nat.add_assoc]

theorem token_word_le (ts : List Nat) (n : Nat) (h : n∈ts) :
    (word n).length≤(encode ts).length := by
  rw [encode_length]
  induction ts with
  | nil => cases h
  | cons a as ih =>
    cases h with
    | head =>
      exact Nat.le_trans (Nat.le_succ _) (Nat.le_add_right _ _)
    | tail _ hm =>
      exact Nat.le_trans (ih hm) (Nat.le_add_left _ _)

theorem encoded_token_magnitude (ts : List Nat) (n : Nat) (h : n∈ts) :
    n<10^(encode ts).length :=
  Nat.lt_of_lt_of_le (word_magnitude n) (pow_mono _ _ (token_word_le ts n h))

theorem bytes_bounded (ts : List Nat) (d : Nat)
    (h : ∀ n∈ts, n<10^(d+1)) :
    (encode ts).length≤ts.length*(d+2) := by
  rw [encode_length]
  induction ts with
  | nil => exact Nat.zero_le _
  | cons n ns ih =>
    change (word n).length+1+byteCount ns≤(ns.length+1)*(d+2)
    have hn := Nat.add_le_add_right (word_length_bound n d (h n (List.Mem.head _))) 1
    have ht := ih (fun a ha => h a (List.Mem.tail _ ha))
    have hh := Nat.add_le_add hn ht
    rw [Nat.add_one_mul,Nat.add_comm (ns.length*(d+2))]
    exact hh

theorem byte_budget (ts : List Nat) (k d : Nat)
    (ht : ts.length≤k) (h : ∀ n∈ts, n<10^(d+1)) :
    (encode ts).length≤k*(d+2) :=
  Nat.le_trans (bytes_bounded ts d h) (Nat.mul_le_mul_right _ ht)

end ProctorDecimalSize

#print axioms ProctorDecimalSize.quotient_bound
#print axioms ProctorDecimalSize.quotient_strict
#print axioms ProctorDecimalSize.digits_length_bound
#print axioms ProctorDecimalSize.word_length_bound
#print axioms ProctorDecimalSize.digits_magnitude
#print axioms ProctorDecimalSize.word_magnitude
#print axioms ProctorDecimalSize.pow_mono
#print axioms ProctorDecimalSize.encode_length
#print axioms ProctorDecimalSize.token_word_le
#print axioms ProctorDecimalSize.encoded_token_magnitude
#print axioms ProctorDecimalSize.bytes_bounded
#print axioms ProctorDecimalSize.byte_budget
