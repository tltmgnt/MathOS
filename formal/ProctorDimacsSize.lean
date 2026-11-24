/-! F034: DIMACS input size bridge for selected typed checker charges.
Uses independent lexical/row grammar; no parser runtime claim. -/
namespace ProctorDimacsSize
open ProctorHallDeficiency
open ProctorDimacsInput (Row Rows decodeDimacs checkDimacs)
open ProctorDimacsLexical (Split Header SignedSeq flush RawMeaning raw_decode_iff)
open ProctorWireRoundtrip (encLiteral encClause encFormula encItems encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope encProof)
open ProctorUnifiedReplay (Envelope)
open ProctorPolynomialMeter (formulaMass)
open ProctorTerminalPolynomial (mul_mono)
open ProctorEncodedSize (size globalUnit global_meter)
open ProctorParserConsumption (envelope_bytes global_mono)
open ProctorUnifiedMeter (boundMeter)

private theorem len_append {α : Type} (a b : List α) :
    (a++b).length=a.length+b.length := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs++b).length+1=(xs.length+1)+b.length
    rw [ih]
    exact (Nat.succ_add xs.length b.length).symm

private theorem revAux_len {α : Type} (a b : List α) :
    (a.reverseAux b).length=a.length+b.length := by
  induction a generalizing b with
  | nil => exact (Nat.zero_add _).symm
  | cons x xs ih =>
    change (xs.reverseAux (x::b)).length=(xs.length+1)+b.length
    rw [ih (x::b)]
    exact (Nat.succ_add xs.length b.length).symm

private theorem rev_len {α : Type} (a : List α) :
    a.reverse.length=a.length :=
  revAux_len a []

private theorem flush_count (w : List Nat) (a : List (List Nat)) :
    (flush w a).length≤w.length+a.length := by
  cases w with
  | nil =>
    change a.length≤0+a.length
    rw [Nat.zero_add] <;> exact Nat.le_refl _
  | cons x xs =>
    change a.length+1≤(xs.length+1)+a.length
    rw [Nat.add_comm (xs.length+1) a.length]
    exact Nat.add_le_add (Nat.le_refl _) (Nat.succ_le_succ (Nat.zero_le _))

theorem split_count (bytes word : List Nat) (acc out : List (List Nat))
    (h : Split bytes word acc out) :
    out.length≤bytes.length+word.length+acc.length := by
  induction h with
  | done w a =>
    change (flush w a).reverse.length≤0+w.length+a.length
    rw [rev_len,Nat.zero_add]
    exact flush_count w a
  | @sep b bs w a out sp sub ih =>
    change out.length≤bs.length+(flush w a).length at ih
    change out.length≤(bs.length+1)+w.length+a.length
    calc
      out.length ≤ bs.length+(w.length+a.length) :=
        Nat.le_trans ih (Nat.add_le_add (Nat.le_refl _) (flush_count w a))
      _ = bs.length+w.length+a.length := (Nat.add_assoc _ _ _).symm
      _ ≤ (bs.length+1)+w.length+a.length :=
        Nat.add_le_add (Nat.add_le_add (Nat.le_succ _) (Nat.le_refl _)) (Nat.le_refl _)
  | @char b bs w a out sp sub ih =>
    change out.length≤bs.length+(w.length+1)+a.length at ih
    change out.length≤(bs.length+1)+w.length+a.length
    have eq : (bs.length+1)+w.length=(bs.length+w.length)+1 :=
      Nat.succ_add _ _
    rw [eq]
    exact ih

theorem header_body_count (bytes acc head body : List Nat)
    (h : Header bytes acc head body) : body.length≤bytes.length := by
  induction h with
  | endLine rest acc => exact Nat.le_succ _
  | @next b bs acc head body ne sub ih => exact Nat.le_trans ih (Nat.le_succ _)

theorem signed_count (ws : List (List Nat)) (acc out : List Literal)
    (h : SignedSeq ws acc out) : out.length=ws.length+acc.length := by
  induction h with
  | nil acc =>
    change acc.reverse.length=0+acc.length
    rw [rev_len,Nat.zero_add]
  | @cons w ws l acc out sg sub ih =>
    change out.length=ws.length+(acc.length+1) at ih
    change out.length=(ws.length+1)+acc.length
    exact ih.trans (Nat.succ_add ws.length acc.length).symm

theorem row_count (n : Nat) (ts : List Literal) (c : Clause)
    (rest : List Literal) (h : Row n ts c rest) :
    ts.length=(c.length+1)+rest.length := by
  induction h with
  | zero rest =>
    change rest.length+1=1+rest.length
    exact Nat.add_comm _ _
  | @lit l ts c rest pos le sub ih =>
    change ts.length+1=(c.length+1+1)+rest.length
    rw [ih]
    exact (Nat.succ_add (c.length+1) rest.length).symm

theorem rows_count (n k : Nat) (ts : List Literal) (f : Formula)
    (h : Rows n k ts f) : ts.length=formulaMass f := by
  induction h with
  | nil => rfl
  | @cons k ts rest c f row bound sub ih =>
    change ts.length=(c.length+1)+formulaMass f
    rw [row_count n ts c rest row,ih]

theorem dimacs_mass (bytes : List Nat) (n : Nat) (f : Formula)
    (h : RawMeaning bytes n f) : formulaMass f≤bytes.length := by
  obtain ⟨m,ts,lex,_,rows⟩ := h
  obtain ⟨_,head,body,rest,hw,bw,hh,_,_,_,hb,hs⟩ := lex
  have hs' := signed_count bw [] ts hs
  have hb' := split_count body [] [] bw hb
  change ts.length=bw.length at hs'
  change bw.length≤body.length at hb'
  rw [← rows_count n m ts f rows,hs']
  exact Nat.le_trans hb' (header_body_count bytes [] head body hh)

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

private theorem literal_items_len (c : Clause) :
    (encItems encLiteral c).length=c.length*2 := by
  induction c with
  | nil => rfl
  | cons l ls ih =>
    change (encLiteral l++encItems encLiteral ls).length=(ls.length+1)*2
    rw [len_append,ih,add_mul_local]
    change 2+ls.length*2=ls.length*2+2
    exact Nat.add_comm _ _

theorem clause_tokens (c : Clause) :
    (encClause c).length≤(c.length+1)*2 := by
  change (encItems encLiteral c).length+1≤(c.length+1)*2
  rw [literal_items_len,add_mul_local]
  exact Nat.add_le_add (Nat.le_refl _) (by decide : 1≤1*2)

private theorem formula_items_bound (f : Formula) :
    (encItems encClause f).length≤formulaMass f*2 := by
  induction f with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    change (encClause c++encItems encClause cs).length≤
      ((c.length+1)+formulaMass cs)*2
    rw [len_append,add_mul_local]
    exact Nat.add_le_add (clause_tokens c) ih

theorem formula_tokens (f : Formula) :
    (encFormula f).length≤formulaMass f*2+1 :=
  Nat.succ_le_succ (formula_items_bound f)

theorem expected_tokens (bytes : List Nat) (n : Nat) (f : Formula)
    (h : decodeDimacs bytes=some (n,f)) :
    (encExpected n f).length≤bytes.length*2+3 := by
  have hm := dimacs_mass bytes n f ((raw_decode_iff bytes n f).mp h)
  have hf := Nat.le_trans (formula_tokens f)
    (Nat.succ_le_succ (mul_mono hm (Nat.le_refl 2)))
  exact Nat.succ_le_succ (Nat.succ_le_succ hf)

def pairBound (a b : List Nat) : Nat := a.length*2+3+b.length

def byteCap (a b : List Nat) : Nat :=
  pairBound a b+pairBound a b+1

theorem pair_size (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : decodeDimacs a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    size n f e≤pairBound a b :=
  Nat.add_le_add (expected_tokens a n f ha) (envelope_bytes b e hb).right

theorem byte_budget (a b : List Nat) (n : Nat) (f : Formula) (e : Envelope)
    (ha : decodeDimacs a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e) :
    (boundMeter n f e).2≤globalUnit (byteCap a b) := by
  have hs := pair_size a b n f e ha hb
  exact Nat.le_trans (global_meter n f e)
    (global_mono _ _ (Nat.succ_le_succ (Nat.add_le_add hs hs)))

theorem accepted_byte_sound (a b : List Nat) (h : checkDimacs a b=true) :
    ∃ n f e, RawMeaning a n f ∧ ProctorDataParser.decodeEnvelope b=some e ∧
      (¬ ∃ x : Assignment, FormulaSat f x) ∧
      (boundMeter n f e).2≤globalUnit (byteCap a b) := by
  obtain ⟨n,f,e,ha,hb,hc⟩ := ProctorDimacsInput.accepted_decoded a b h
  exact ⟨n,f,e,(raw_decode_iff a n f).mp ha,hb,
    ProctorUnifiedReplay.bound_sound n f e hc,byte_budget a b n f e ha hb⟩

-- Acceptance binds the original to the copy inside the proof file.
-- A second, stronger bound on selected checking charges uses only
-- proof bytes. This does NOT bound DIMACS parsing or input reading.
theorem accepted_envelope_budget (a b : List Nat) (n : Nat) (f : Formula)
    (e : Envelope) (ha : decodeDimacs a=some (n,f))
    (hb : ProctorDataParser.decodeEnvelope b=some e)
    (h : checkDimacs a b=true) :
    (boundMeter n f e).2≤globalUnit (b.length+b.length+b.length+b.length+1) := by
  have hc : ProctorUnifiedReplay.boundCheck n f e=true := by
    unfold checkDimacs at h
    rw [ha,hb] at h
    exact h
  have bind := ProctorUnifiedReplay.binding_exact n f e hc
  have hf : (encExpected n f).length≤(encEnvelope e).length := by
    rw [bind.left,bind.right]
    unfold encExpected encEnvelope
    change (encFormula e.original).length+1+1≤
      (encFormula e.original++encProof e.proof).length+1+1
    rw [len_append]
    exact Nat.succ_le_succ (Nat.succ_le_succ (Nat.le_add_right _ _))
  have hp := (envelope_bytes b e hb).right
  have hs : size n f e≤b.length+b.length :=
    Nat.add_le_add (Nat.le_trans hf hp) hp
  have hm : ProctorEncodedSize.cap n f e≤(b.length+b.length)+(b.length+b.length)+1 :=
    Nat.succ_le_succ (Nat.add_le_add hs hs)
  have hn : (b.length+b.length)+(b.length+b.length)+1=
      b.length+b.length+b.length+b.length+1 :=
    congrArg Nat.succ (Nat.add_assoc (b.length+b.length) b.length b.length).symm
  rw [hn] at hm
  exact Nat.le_trans (global_meter n f e) (global_mono _ _ hm)

end ProctorDimacsSize

#print axioms ProctorDimacsSize.split_count
#print axioms ProctorDimacsSize.header_body_count
#print axioms ProctorDimacsSize.signed_count
#print axioms ProctorDimacsSize.row_count
#print axioms ProctorDimacsSize.rows_count
#print axioms ProctorDimacsSize.dimacs_mass
#print axioms ProctorDimacsSize.clause_tokens
#print axioms ProctorDimacsSize.formula_tokens
#print axioms ProctorDimacsSize.expected_tokens
#print axioms ProctorDimacsSize.pair_size
#print axioms ProctorDimacsSize.byte_budget
#print axioms ProctorDimacsSize.accepted_byte_sound
#print axioms ProctorDimacsSize.accepted_envelope_budget
