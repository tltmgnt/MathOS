/-! F035: bridge canonical input byte size to a polynomial output budget.
Integrates the separately verified generated token magnitude specification. -/
namespace ProctorPolynomialWireSize
open ProctorHallDeficiency
open ProctorDecimalEncoder (encode word digits)
open ProctorDecimalSize (byteCount encode_length encoded_token_magnitude byte_budget pow_mono)
open ProctorWireRoundtrip (encExpected)
open ProctorWireTokenBounds (expected_length sat_tokens_length solve_unsat_tokens)
open ProctorPathResourceBounds (occurrences)
open ProctorSerializedTwoCNF (Witness produce tokens)
open ProctorOrdinaryCompleteness (variables)
open ProctorFiniteModel (materialize)
open ProctorTotalTwoCNF (solve)

def inputSize (n : Nat) (f : Formula) : Nat := (encode (encExpected n f)).length
def tokenBudget (N : Nat) : Nat := N+(8*(N*N)+N+3)+3
def outputBudget (N : Nat) : Nat := tokenBudget N*(2*N+5)

theorem token_count_le_bytes (ts : List Nat) : ts.length≤(encode ts).length := by
  rw [encode_length]
  induction ts with
  | nil => exact Nat.le_refl _
  | cons t ts ih =>
    change ts.length+1≤(word t).length+1+byteCount ts
    have h := Nat.add_le_add (Nat.le_refl 1) ih
    change 1+ts.length≤1+byteCount ts at h
    rw [Nat.add_comm 1 ts.length] at h
    exact Nat.le_trans h (Nat.add_le_add_right (Nat.succ_le_succ (Nat.zero_le _)) _)

theorem input_counts (n : Nat) (f : Formula) :
    2*occurrences f+f.length+3≤inputSize n f := by
  have h := token_count_le_bytes (encExpected n f)
  rw [expected_length] at h
  exact h

theorem input_identifier (n : Nat) (f : Formula) : n<10^(inputSize n f) :=
  encoded_token_magnitude (encExpected n f) n (List.Mem.tail _ (List.Mem.head _))

theorem structural_counts (n : Nat) (f : Formula) :
    let N := inputSize n f
    occurrences f≤N ∧ 2*occurrences f+1≤N ∧
      f.length+(2*occurrences f+1)≤N ∧ f.length≤N := by
  have h := input_counts n f
  have hL : occurrences f≤2*occurrences f := by
    have hh := Nat.mul_le_mul_right (occurrences f) (by decide : 1≤2)
    rw [Nat.one_mul] at hh
    exact hh
  have hbase := Nat.le_trans (Nat.le_add_right (2*occurrences f+f.length) 3) h
  have h2 := Nat.le_trans (Nat.le_add_right (2*occurrences f) f.length) hbase
  have hk : 2*occurrences f+1≤inputSize n f := by
    apply Nat.le_trans (Nat.add_le_add (Nat.le_refl (2*occurrences f)) (Nat.le_trans (by decide : 1≤3) (Nat.le_add_left 3 f.length)))
    rw [← Nat.add_assoc]
    exact h
  have hmk : f.length+(2*occurrences f+1)≤inputSize n f := by
    rw [← Nat.add_assoc,Nat.add_comm f.length (2*occurrences f)]
    exact Nat.le_trans (Nat.add_le_add_left (by decide : 1≤3) _) h
  exact ⟨Nat.le_trans hL h2,hk,hmk,
    Nat.le_trans (Nat.le_add_left f.length (2*occurrences f)) hbase⟩

theorem structural_budget (n : Nat) (f : Formula) :
    f.length+(f.length+(2*occurrences f+1))*(2*occurrences f+1)
      ≤inputSize n f+inputSize n f*inputSize n f := by
  have h := structural_counts n f
  exact Nat.add_le_add h.2.2.2 (Nat.mul_le_mul h.2.2.1 h.2.1)

theorem successor_pow (N : Nat) : N+1≤10^N := by
  induction N with
  | zero => exact Nat.le_refl _
  | succ N ih =>
    rw [Nat.pow_succ]
    have h : N+2≤(N+1)*10 := by
      have h1 : N+2≤(N+1)+(N+1) :=
        Nat.add_le_add_left (Nat.succ_le_succ (Nat.zero_le N)) (N+1)
      have h2 : (N+1)+(N+1)=(N+1)*2 := by rw [Nat.mul_succ,Nat.mul_one]
      rw [h2] at h1
      exact Nat.le_trans h1 (Nat.mul_le_mul_left _ (by decide : 2≤10))
    exact Nat.le_trans h (Nat.mul_le_mul_right 10 ih)

private theorem mul_add' (a b c : Nat) : a*(b+c)=a*b+a*c := by
  induction c with
  | zero => rfl
  | succ c ih =>
    change a*(b+c+1)=a*b+a*(c+1)
    rw [Nat.mul_succ,Nat.mul_succ,ih,Nat.add_assoc]

private theorem mul_assoc' (a b c : Nat) : (a*b)*c=a*(b*c) := by
  induction c with
  | zero => rfl
  | succ c ih =>
    rw [Nat.mul_succ (a*b),Nat.mul_succ b,ih,mul_add']

private theorem pow_add' (a b : Nat) : 10^(a+b)=10^a*10^b := by
  induction b with
  | zero => change 10^a=10^a*1; rw [Nat.mul_one]
  | succ b ih =>
    change 10^(a+b+1)=10^a*10^(b+1)
    rw [Nat.pow_succ,Nat.pow_succ,ih,mul_assoc']

theorem structural_pow (N : Nat) : N+N*N<10^(2*N+4) := by
  have h0 : N+N*N≤(N+1)*(N+1) := by
    rw [Nat.mul_succ,Nat.add_one_mul]
    have h := Nat.le_add_right (N*N+N) (N+1)
    rw [Nat.add_comm N (N*N)]
    exact h
  have h1 := Nat.mul_le_mul (successor_pow N) (successor_pow N)
  rw [← pow_add'] at h1
  have h2 : N+N=2*N := by
    rw [Nat.mul_comm 2,Nat.mul_succ,Nat.mul_one]
  rw [h2] at h1
  have hp : 0<10^(2*N) := Nat.lt_of_lt_of_le (Nat.zero_lt_succ _) (successor_pow (2*N))
  have hh := Nat.mul_lt_mul_of_pos_left (by decide : 1<10^4) hp
  rw [Nat.mul_one,← pow_add'] at hh
  exact Nat.lt_of_le_of_lt (Nat.le_trans h0 h1) hh

theorem constants_pow (N : Nat) : 3402<10^(2*N+4) :=
  Nat.lt_of_lt_of_le (by decide : 3402<10^4)
    (pow_mono 4 _ (Nat.le_add_left 4 (2*N)))

theorem identifier_pow (n : Nat) (f : Formula) : n<10^(2*inputSize n f+4) := by
  let N := inputSize n f
  have h : N≤2*N := by
    have hh := Nat.mul_le_mul_right N (by decide : 1≤2)
    rw [Nat.one_mul] at hh
    exact hh
  exact Nat.lt_of_lt_of_le (input_identifier n f)
    (pow_mono N _ (Nat.le_trans h (Nat.le_add_right _ 4)))

theorem producer_token_budget (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w) : (tokens w).length≤tokenBudget (inputSize n f) := by
  let N := inputSize n f
  have hc := structural_counts n f
  unfold produce at h
  cases e : solve n f with
  | invalid => rw [e] at h; cases h
  | unsupported => rw [e] at h; cases h
  | internalError => rw [e] at h; cases h
  | sat x =>
    rw [e] at h
    cases h
    rw [sat_tokens_length]
    have hh : 2*occurrences f+2≤N := by
      apply Nat.le_trans _ (input_counts n f)
      rw [Nat.add_assoc]
      exact Nat.add_le_add_left (Nat.le_trans (by decide : 2≤3) (Nat.le_add_left 3 f.length)) _
    exact Nat.le_trans hh (Nat.le_trans (Nat.le_add_right N _) (Nat.le_add_right _ 3))
  | unsat p =>
    rw [e] at h
    cases h
    have hh := solve_unsat_tokens n f p e
    have hbase : 2*occurrences f+f.length+1≤N :=
      Nat.le_trans (Nat.add_le_add_left (by decide : 1≤3) _) (input_counts n f)
    have hs := Nat.mul_le_mul hc.2.2.1 hc.2.1
    exact Nat.le_trans hh (Nat.add_le_add_right (Nat.add_le_add hbase
      (Nat.add_le_add_right (Nat.add_le_add (Nat.mul_le_mul_left 8 hs) hc.2.1) 3)) 3)

theorem output_budget_of_magnitude (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w)
    (hm : ∀ t∈tokens w, t<10^(2*inputSize n f+4)) :
    (encode (tokens w)).length≤outputBudget (inputSize n f) := by
  exact byte_budget _ _ (2*inputSize n f+3) (producer_token_budget n f w h) hm

theorem producer_magnitude_pow (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w) :
    ∀ t∈tokens w, t<10^(2*inputSize n f+4) := by
  let N := inputSize n f
  let cap := max n (max 3402 (N+N*N))
  have hc := structural_counts n f
  have hs : N≤N+N*N := Nat.le_add_right _ _
  have hcap : N+N*N≤cap :=
    Nat.le_trans (Nat.le_max_right 3402 _) (Nat.le_max_right n _)
  have hm := ProctorTokenMagnitude.producer_bound n cap f w
    (Nat.le_max_left n _) (Nat.le_trans (Nat.le_max_left 3402 _) (Nat.le_max_right n _))
    (Nat.le_trans hc.1 (Nat.le_trans hs hcap))
    (Nat.le_trans hc.2.1 (Nat.le_trans hs hcap))
    (Nat.le_trans (structural_budget n f) hcap) h
  have hlt : cap<10^(2*N+4) := by
    have max_lt' : ∀ a b c : Nat, a<c → b<c → max a b<c := by
      intro a b c ha hb
      by_cases hab : a≤b
      · rw [Nat.max_eq_right hab]
        exact hb
      · rw [Nat.max_eq_left (Nat.le_of_not_ge hab)]
        exact ha
    exact max_lt' _ _ _ (identifier_pow n f)
      (max_lt' _ _ _ (constants_pow N) (structural_pow N))
  intro t ht
  exact Nat.lt_of_le_of_lt (hm t ht) hlt

theorem producer_byte_budget (n : Nat) (f : Formula) (w : Witness)
    (h : produce n f=some w) :
    (encode (tokens w)).length≤outputBudget (inputSize n f) :=
  output_budget_of_magnitude n f w h (producer_magnitude_pow n f w h)

theorem canonical_byte_budget (n : Nat) (f : Formula) (out : List Nat)
    (h : ProctorEndToEndBytes.produceBytes (encode (encExpected n f))=some out) :
    out.length≤outputBudget (inputSize n f) := by
  unfold ProctorEndToEndBytes.produceBytes at h
  rw [ProctorDecimalEncoder.expected_bytes] at h
  change (do
    let w ← produce n f
    some (encode (tokens w)))=some out at h
  cases hw : produce n f with
  | none => rw [hw] at h; cases h
  | some w =>
    rw [hw] at h
    change some (encode (tokens w))=some out at h
    cases h
    exact producer_byte_budget n f w hw

end ProctorPolynomialWireSize

#print axioms ProctorPolynomialWireSize.token_count_le_bytes
#print axioms ProctorPolynomialWireSize.input_counts
#print axioms ProctorPolynomialWireSize.input_identifier
#print axioms ProctorPolynomialWireSize.structural_counts
#print axioms ProctorPolynomialWireSize.structural_budget
#print axioms ProctorPolynomialWireSize.successor_pow
#print axioms ProctorPolynomialWireSize.structural_pow
#print axioms ProctorPolynomialWireSize.constants_pow
#print axioms ProctorPolynomialWireSize.identifier_pow
#print axioms ProctorPolynomialWireSize.producer_token_budget
#print axioms ProctorPolynomialWireSize.output_budget_of_magnitude

#print axioms ProctorPolynomialWireSize.producer_magnitude_pow
#print axioms ProctorPolynomialWireSize.producer_byte_budget
#print axioms ProctorPolynomialWireSize.canonical_byte_budget

#print axioms ProctorPolynomialWireSize.pow_add'
#print axioms Nat.pow_succ
#print axioms Nat.mul_assoc
#print axioms Nat.add_one_mul
