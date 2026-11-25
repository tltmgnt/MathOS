/-! F035/F038 candidate: constructive unbounded canonical decimal
encoder and ordinary serialized completeness. Fuel is a structural
termination witness, not a proved bit-cost bound. -/
namespace ProctorUnboundedWire
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope Proof boundCheck validFormula)
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)
open ProctorResolutionBridge (Unsat)
open ProctorUnboundedCodec (scan tokenize decodeExpected decodeEnvelope checkBytes)

inductive Word : Nat → Nat → List Nat → Nat → Prop where
  | done (v k : Nat) : k≠0 → Word v k [] v
  | digit {v k b out : Nat} {bs : List Nat} :
      48≤b → b≤57 → (k>0 → v≠0) →
      Word (10*v+(b-48)) (k+1) bs out → Word v k (b::bs) out

private theorem append_assoc_local {α : Type} (a b c : List α) :
    (a++b)++c=a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_nil_local {α : Type} (a : List α) : a++[]=a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem reverseAux_append {α : Type} (a b c : List α) :
    a.reverseAux (b++c)=a.reverseAux b++c := by
  induction a generalizing b with
  | nil => rfl
  | cons x xs ih => exact ih (x::b)

private theorem reverse_cons_local {α : Type} (a : α) (as : List α) :
    (a::as).reverse=as.reverse++[a] :=
  reverseAux_append as [] [a]

theorem scan_word (v k out : Nat) (ds : List Nat)
    (h : Word v k ds out) (rest acc : List Nat) :
    scan (ds++10::rest) v k acc=scan rest 0 0 (out::acc) := by
  induction h with
  | done v k hk =>
    change (if k=0 then none else scan rest 0 0 (v::acc))=_
    rw [if_neg hk]
  | @digit v k b out bs lo hi nonzero sub ih =>
    have notLF : b≠10 := by
      intro eq
      rw [eq] at lo
      exact (Nat.not_le_of_gt (by decide : 10<48)) lo
    have ok : ¬(k>0 ∧ v=0) := fun bad => nonzero bad.left bad.right
    change (if b=10 then
      (if k=0 then none else scan (bs++10::rest) 0 0 (v::acc))
      else if 48≤b ∧ b≤57 then
        (if k>0 ∧ v=0 then none
         else scan (bs++10::rest) (10*v+(b-48)) (k+1) acc)
      else none)=_
    rw [if_neg notLF,if_pos ⟨lo,hi⟩,if_neg ok]
    exact ih

private theorem char_lo (d : Nat) : 48≤48+d := Nat.le_add_right _ _
private theorem char_hi (d : Nat) (h : d<10) : 48+d≤57 :=
  Nat.add_le_add (Nat.le_refl 48) (Nat.le_of_lt_succ h)
private theorem char_value (d : Nat) : 48+d-48=d :=
  Nat.add_sub_cancel_left 48 d

theorem single_word (d : Nat) (h : d<10) : Word 0 0 [48+d] d := by
  apply Word.digit (char_lo d) (char_hi d h)
  · intro hz
    exact (Nat.not_lt_zero _ hz).elim
  · rw [char_value]
    exact Word.done d 1 (by decide)

theorem append_digit (v k out : Nat) (ds : List Nat)
    (h : Word v k ds out) (d : Nat) (hd : d<10) (hn : out≠0) :
    Word v k (ds++[48+d]) (10*out+d) := by
  induction h with
  | done v k hk =>
    change Word v k [48+d] (10*v+d)
    apply Word.digit (char_lo d) (char_hi d hd) (fun _ => hn)
    rw [char_value]
    exact Word.done (10*v+d) (k+1) (Nat.succ_ne_zero k)
  | @digit v k b out bs lo hi nonzero sub ih =>
    exact Word.digit lo hi nonzero ih

def digitsAux : Nat → Nat → List Nat
  | 0,_ => []
  | fuel+1,n =>
    if n<10 then [48+n]
    else digitsAux fuel (n/10)++[48+n%10]

theorem digits_aux_word (fuel n : Nat) (h : n<fuel) :
    Word 0 0 (digitsAux fuel n) n := by
  induction fuel generalizing n with
  | zero => exact (Nat.not_lt_zero n h).elim
  | succ fuel ih =>
    unfold digitsAux
    by_cases small : n<10
    · rw [if_pos small]
      exact single_word n small
    · rw [if_neg small]
      have hn : 0<n := Nat.lt_of_lt_of_le (by decide : 0<10) (Nat.le_of_not_gt small)
      have hq : n/10<fuel := Nat.lt_of_lt_of_le
        (Nat.div_lt_self hn (by decide : 1<10)) (Nat.le_of_lt_succ h)
      have hm : n%10<10 := Nat.mod_lt _ (by decide)
      have he : 10*(n/10)+n%10=n := (Nat.add_comm _ _).trans (Nat.mod_add_div n 10)
      have nz : n/10≠0 := by
        intro z
        rw [z] at he
        have e : n%10=n := (Nat.zero_add _).symm.trans he
        exact small (e ▸ hm)
      have hw := append_digit 0 0 (n/10) (digitsAux fuel (n/10))
        (ih (n/10) hq) (n%10) hm nz
      rw [he] at hw
      exact hw

def digits (n : Nat) : List Nat := digitsAux (n+1) n

theorem digits_word (n : Nat) : Word 0 0 (digits n) n :=
  digits_aux_word (n+1) n (Nat.lt_succ_self n)

def encode : List Nat → List Nat
  | [] => []
  | n::ns => digits n++10::encode ns

theorem scan_encode (ts acc : List Nat) :
    scan (encode ts) 0 0 acc=some (acc.reverse++ts) := by
  induction ts generalizing acc with
  | nil =>
    change some acc.reverse=some (acc.reverse++[])
    rw [append_nil_local]
  | cons n ns ih =>
    change scan (digits n++10::encode ns) 0 0 acc=_
    rw [scan_word 0 0 n (digits n) (digits_word n) (encode ns) acc,ih (n::acc)]
    rw [reverse_cons_local,append_assoc_local] <;> rfl

theorem tokenize_encode (ts : List Nat) : tokenize (encode ts)=some ts := by
  unfold tokenize
  exact scan_encode ts []

def expectedBytes (n : Nat) (f : Formula) : List Nat :=
  encode (encExpected n f)

def envelopeBytes (e : Envelope) : List Nat :=
  encode (encEnvelope e)

theorem expected_roundtrip (n : Nat) (f : Formula) :
    decodeExpected (expectedBytes n f)=some (n,f) :=
  ProctorUnboundedRoundtrip.expected_exact n f _ (tokenize_encode _)

theorem envelope_roundtrip (e : Envelope) :
    decodeEnvelope (envelopeBytes e)=some e :=
  ProctorUnboundedRoundtrip.envelope_exact e _ (tokenize_encode _)

theorem check_encoded (n : Nat) (f : Formula) (e : Envelope) :
    checkBytes (expectedBytes n f) (envelopeBytes e)=boundCheck n f e := by
  unfold checkBytes
  rw [expected_roundtrip,envelope_roundtrip] <;> rfl

theorem byte_complete (n : Nat) (f : Formula)
    (hf : validFormula n f=true) (hu : Unsat f) :
    ∃ b : List Nat, checkBytes (expectedBytes n f) b=true := by
  obtain ⟨p,hp⟩ := ProctorEnvelopeCompleteness.envelope_complete n f hf hu
  exact ⟨envelopeBytes ⟨n,f,p⟩,(check_encoded n f ⟨n,f,p⟩).trans hp⟩

theorem byte_iff (n : Nat) (f : Formula) (hf : validFormula n f=true) :
    (∃ b : List Nat, checkBytes (expectedBytes n f) b=true) ↔ Unsat f := by
  constructor
  · intro h
    obtain ⟨b,hb⟩ := h
    obtain ⟨m,g,hd,hu⟩ := ProctorUnboundedCodec.bytes_sound _ _ hb
    rw [expected_roundtrip] at hd
    cases hd
    exact hu
  · exact byte_complete n f hf

end ProctorUnboundedWire

#print axioms ProctorUnboundedWire.scan_word
#print axioms ProctorUnboundedWire.single_word
#print axioms ProctorUnboundedWire.append_digit
#print axioms ProctorUnboundedWire.digits_aux_word
#print axioms ProctorUnboundedWire.digits_word
#print axioms ProctorUnboundedWire.scan_encode
#print axioms ProctorUnboundedWire.tokenize_encode
#print axioms ProctorUnboundedWire.expected_roundtrip
#print axioms ProctorUnboundedWire.envelope_roundtrip
#print axioms ProctorUnboundedWire.check_encoded
#print axioms ProctorUnboundedWire.byte_complete
#print axioms ProctorUnboundedWire.byte_iff
