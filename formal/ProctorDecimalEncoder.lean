/-! F035: constructive decimal encoder for the unbounded scanner.
Fuel is an upper bound on the natural being encoded. Recursion stops
as soon as the quotient is a single digit, so executable calls follow
the decimal quotient chain rather than enumerate the identifier range.
This is roundtrip correctness, not a machine bit-cost theorem. -/
namespace ProctorDecimalEncoder
open ProctorUnboundedCodec (scan tokenize)

def digits : Nat → Nat → List Nat
  | 0,n => [48+n]
  | fuel+1,n =>
    if n<10 then [48+n]
    else digits fuel (n/10) ++ [48+n%10]

def word (n : Nat) : List Nat := digits (n+1) n

def encode : List Nat → List Nat
  | [] => []
  | n::ns => word n ++ 10::encode ns

private theorem append_assoc' {α : Type} (a b c : List α) :
    (a++b)++c=a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (fun ys => x::ys) ih

private theorem append_nil' {α : Type} (a : List α) : a++[]=a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (fun ys => x::ys) ih

private theorem reverseAux_append' {α : Type} (xs ys zs : List α) :
    xs.reverseAux (ys ++ zs)=xs.reverseAux ys++zs := by
  induction xs generalizing ys with
  | nil => rfl
  | cons x xs ih => exact ih (x::ys)

private theorem reverse_cons' {α : Type} (a : α) (as : List α) :
    (a::as).reverse=as.reverse++[a] :=
  reverseAux_append' as [] [a]

theorem digit_range (d : Nat) (h : d<10) : 48≤48+d ∧ 48+d≤57 :=
  ⟨Nat.le_add_right _ _, Nat.add_le_add_left (Nat.le_of_lt_succ h) 48⟩

theorem digit_value (d : Nat) : 48+d-48=d := by
  have cancel : ∀ a b : Nat, (a+b)-b=a := by
    intro a b
    induction b with
    | zero => rfl
    | succ b ih =>
      change Nat.succ (a+b)-Nat.succ b=a
      rw [Nat.succ_sub_succ_eq_sub]
      exact ih
  rw [Nat.add_comm 48 d]
  exact cancel d 48

theorem scan_digit (v k d : Nat) (h : d<10)
    (hn : k>0 → v≠0) (rest acc : List Nat) :
    scan ((48+d)::rest) v k acc=scan rest (10*v+d) (k+1) acc := by
  have hr := digit_range d h
  have hs : 48+d≠10 := by
    intro e
    rw [e] at hr
    exact (Nat.not_le_of_gt (by decide : 10<48)) hr.left
  have hb : ¬(k>0 ∧ v=0) := fun he => hn he.left he.right
  change (if 48+d=10 then
      (if k=0 then none else scan rest 0 0 (v::acc))
    else if 48≤48+d ∧ 48+d≤57 then
      (if k>0 ∧ v=0 then none else scan rest (10*v+(48+d-48)) (k+1) acc)
    else none)=_
  rw [if_neg hs,if_pos hr,if_neg hb,digit_value]

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

theorem quotient_positive (n : Nat) (h : ¬n<10) : 0<n/10 := by
  have hm := Nat.mod_lt n (by decide : 0<10)
  have he := div_add_mod' n 10
  cases hq : n/10 with
  | zero =>
    rw [hq,Nat.mul_zero,Nat.zero_add] at he
    rw [he] at hm
    exact (h hm).elim
  | succ q => exact Nat.zero_lt_succ q

theorem digits_scan (fuel n : Nat) (h : n<fuel) :
    ∃ k, 0<k ∧ ∀ rest acc,
      scan (digits fuel n++rest) 0 0 acc=scan rest n k acc := by
  induction fuel generalizing n with
  | zero => exact (Nat.not_lt_zero _ h).elim
  | succ fuel ih =>
    by_cases small : n<10
    · refine ⟨1,Nat.zero_lt_succ 0,?_⟩
      intro rest acc
      change scan ((if n<10 then [48+n] else digits fuel (n/10)++[48+n%10])++rest) 0 0 acc=_
      rw [if_pos small]
      have hd := scan_digit 0 0 n small (fun e => (Nat.not_lt_zero _ e).elim) rest acc
      rw [Nat.mul_zero,Nat.zero_add] at hd
      exact hd
    · have hpos := quotient_positive n small
      have hlt : n/10<n := by
        have hmul := Nat.mul_lt_mul_of_pos_right (by decide : 1<10) hpos
        rw [Nat.one_mul] at hmul
        have hh := Nat.le_add_right (10*(n/10)) (n%10)
        rw [div_add_mod' n 10] at hh
        exact Nat.lt_of_lt_of_le hmul hh
      have hf : n/10<fuel := Nat.lt_of_lt_of_le hlt (Nat.le_of_lt_succ h)
      obtain ⟨k,hk,hs⟩ := ih (n/10) hf
      refine ⟨k+1,Nat.zero_lt_succ k,?_⟩
      intro rest acc
      change scan ((if n<10 then [48+n] else digits fuel (n/10)++[48+n%10])++rest) 0 0 acc=_
      rw [if_neg small,append_assoc']
      change scan (digits fuel (n/10)++(48+n%10)::rest) 0 0 acc=_
      rw [hs,scan_digit (n/10) k (n%10) (Nat.mod_lt n (by decide : 0<10))
        (fun _ => Nat.ne_of_gt hpos),div_add_mod']

theorem word_scan (n : Nat) (rest acc : List Nat) :
    scan (word n++10::rest) 0 0 acc=scan rest 0 0 (n::acc) := by
  obtain ⟨k,hk,hs⟩ := digits_scan (n+1) n (Nat.lt_succ_self n)
  unfold word
  rw [hs]
  change (if k=0 then none else scan rest 0 0 (n::acc))=_
  rw [if_neg (Nat.ne_of_gt hk)]

theorem encode_scan (tokens acc : List Nat) :
    scan (encode tokens) 0 0 acc=some (acc.reverse++tokens) := by
  induction tokens generalizing acc with
  | nil =>
    change some acc.reverse=some (acc.reverse++[])
    rw [append_nil']
  | cons n ns ih =>
    change scan (word n++10::encode ns) 0 0 acc=_
    rw [word_scan,ih,reverse_cons',append_assoc']
    rfl

theorem tokenize_encode (tokens : List Nat) :
    tokenize (encode tokens)=some tokens :=
  encode_scan tokens []

theorem expected_bytes (n : Nat) (f : ProctorHallDeficiency.Formula) :
    ProctorUnboundedCodec.decodeExpected (encode (ProctorWireRoundtrip.encExpected n f))=some (n,f) :=
  ProctorUnboundedRoundtrip.expected_exact n f _ (tokenize_encode _)

theorem envelope_bytes (e : ProctorUnifiedReplay.Envelope) :
    ProctorUnboundedCodec.decodeEnvelope (encode (ProctorEnvelopeRoundtrip.encEnvelope e))=some e :=
  ProctorUnboundedRoundtrip.envelope_exact e _ (tokenize_encode _)

theorem proof_bytes_accept (n : Nat) (f : ProctorHallDeficiency.Formula)
    (p : ProctorUnifiedReplay.Proof)
    (h : ProctorUnifiedReplay.boundCheck n f ⟨n,f,p⟩=true) :
    ProctorUnboundedCodec.checkBytes
      (encode (ProctorWireRoundtrip.encExpected n f))
      (encode (ProctorEnvelopeRoundtrip.encEnvelope ⟨n,f,p⟩))=true := by
  unfold ProctorUnboundedCodec.checkBytes
  rw [expected_bytes,envelope_bytes]
  exact h

end ProctorDecimalEncoder

#print axioms ProctorDecimalEncoder.digit_range
#print axioms ProctorDecimalEncoder.digit_value
#print axioms ProctorDecimalEncoder.scan_digit
#print axioms ProctorDecimalEncoder.quotient_positive
#print axioms ProctorDecimalEncoder.digits_scan
#print axioms ProctorDecimalEncoder.word_scan
#print axioms ProctorDecimalEncoder.encode_scan
#print axioms ProctorDecimalEncoder.tokenize_encode
#print axioms ProctorDecimalEncoder.expected_bytes
#print axioms ProctorDecimalEncoder.envelope_bytes
#print axioms ProctorDecimalEncoder.proof_bytes_accept

#print axioms ProctorDecimalEncoder.sub_add_cancel'
#print axioms ProctorDecimalEncoder.div_add_mod'
#print axioms Nat.div_eq
#print axioms Nat.mod_eq
#print axioms Nat.mul_lt_mul_of_pos_right
