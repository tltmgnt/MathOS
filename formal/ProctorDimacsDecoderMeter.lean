/-! F034: composition of verified DIMACS lexer and row meters.
Counts only the explicitly selected charges of both stages.
Production parser is unchanged. -/
namespace ProctorDimacsDecoderMeter
open ProctorHallDeficiency
open ProctorDimacsInput (lexDimacs parseRows decodeDimacs)
open ProctorDataParser (listLimit)
open ProctorDimacsLexerCompose (Meter LexResult bindM bind_value bind_bound lexMeter lex_value lex_bound lexUnit)
open ProctorDimacsRowMeter (rowsMeter rows_value rows_bound rowsUnit decodeRowsMeter lex_token_bound)
open ProctorTerminalPolynomial (mul_mono)

def rowsStage (t : LexResult) : Meter (Nat × Formula) :=
  let (n,m,ts) := t
  if m≤listLimit then
    let r := rowsMeter n m ts
    (r.1.map (fun f => (n,f)),r.2+1)
  else (none,1)

def stageValue (t : LexResult) : Option (Nat × Formula) := do
  let (n,m,ts) := t
  if m≤listLimit then
    let f ← parseRows n m ts
    some (n,f)
  else none

theorem stage_value (t : LexResult) :
    (rowsStage t).1=stageValue t := by
  obtain ⟨n,m,ts⟩ := t
  change (if m≤listLimit then
    ((rowsMeter n m ts).1.map (fun f => (n,f)),(rowsMeter n m ts).2+1)
    else (none,1)).1 = (if m≤listLimit then
      (do let f ← parseRows n m ts; some (n,f)) else none)
  by_cases h : m≤listLimit
  · rw [if_pos h,if_pos h]
    change (rowsMeter n m ts).1.map (fun f => (n,f))=_
    rw [rows_value]
    cases parseRows n m ts <;> rfl
  · rw [if_neg h,if_neg h]

theorem stage_bound (t : LexResult) (A : Nat) (h : t.2.2.length≤A) :
    (rowsStage t).2≤rowsUnit A+1 := by
  obtain ⟨n,m,ts⟩ := t
  change ts.length≤A at h
  change (if m≤listLimit then
    ((rowsMeter n m ts).1.map (fun f => (n,f)),(rowsMeter n m ts).2+1)
    else (none,1)).2≤rowsUnit A+1
  by_cases size : m≤listLimit
  · rw [if_pos size]
    exact Nat.succ_le_succ (Nat.le_trans (rows_bound n m ts)
      (Nat.succ_le_succ (mul_mono (Nat.succ_le_succ h) (Nat.le_refl 3))))
  · rw [if_neg size]
    exact Nat.succ_le_succ (Nat.zero_le _)

def decodeMeter (bytes : List Nat) : Meter (Nat × Formula) :=
  bindM (lexMeter bytes) rowsStage

theorem decode_value (bytes : List Nat) :
    (decodeMeter bytes).1=decodeDimacs bytes := by
  unfold decodeMeter decodeDimacs
  exact bind_value _ _ (lexDimacs bytes) stageValue
    (lex_value bytes) stage_value

theorem stage_count (bytes : List Nat) (t : LexResult)
    (h : lexDimacs bytes=some t) :
    (decodeRowsMeter bytes).2=(rowsStage t).2 := by
  unfold decodeRowsMeter
  rw [h]
  obtain ⟨n,m,ts⟩ := t
  rfl

-- Exact additivity: there is no second lexer invocation in decodeMeter.
-- The separate stage meters on the right specify the same selected ledger.
theorem decode_count (bytes : List Nat) :
    (decodeMeter bytes).2=(lexMeter bytes).2+(decodeRowsMeter bytes).2 := by
  unfold decodeMeter bindM
  have hv := lex_value bytes
  cases e : (lexMeter bytes).1 with
  | none =>
    have he : lexDimacs bytes=none := hv.symm.trans e
    have hz : (decodeRowsMeter bytes).2=0 := by
      unfold decodeRowsMeter
      rw [he]
    rw [hz]
  | some t =>
    have he : lexDimacs bytes=some t := hv.symm.trans e
    rw [stage_count bytes t he]

def decoderUnit (A : Nat) : Nat := lexUnit A+(rowsUnit A+1)

theorem decode_bound (bytes : List Nat) :
    (decodeMeter bytes).2≤decoderUnit bytes.length := by
  unfold decodeMeter decoderUnit
  apply bind_bound _ _ _ _ (lex_bound bytes)
  intro t h
  have he := (lex_value bytes).symm.trans h
  obtain ⟨n,m,ts⟩ := t
  exact stage_bound (n,m,ts) bytes.length (lex_token_bound bytes n m ts he)

-- Constructive affine normalization, with no generic AC or ring tactics.
private theorem shuffle_add (a b c d : Nat) :
    (a+b)+(c+d)=(a+c)+(b+d) := by
  calc
    (a+b)+(c+d) = a+(b+(c+d)) := Nat.add_assoc _ _ _
    _ = a+((b+c)+d) := congrArg (fun z => a+z) (Nat.add_assoc _ _ _).symm
    _ = a+((c+b)+d) := congrArg (fun z => a+(z+d)) (Nat.add_comm _ _)
    _ = a+(c+(b+d)) := congrArg (fun z => a+z) (Nat.add_assoc _ _ _)
    _ = (a+c)+(b+d) := (Nat.add_assoc _ _ _).symm

private theorem mul_add_local (n a b : Nat) : n*(a+b)=n*a+n*b := by
  induction b with
  | zero => rfl
  | succ b ih =>
    change n*(a+b)+n=n*a+(n*b+n)
    rw [ih]
    exact Nat.add_assoc _ _ _

private theorem affine_add {A x y a b c d : Nat}
    (h : x=A*a+b) (g : y=A*c+d) :
    x+y=A*(a+c)+(b+d) := by
  rw [h,g,shuffle_add,← mul_add_local]

private theorem var_affine (A : Nat) : A=A*1+0 :=
  (Nat.zero_add A).symm

private theorem const_affine (A k : Nat) : k=A*0+k :=
  (Nat.zero_add k).symm

theorem lex_unit_linear (A : Nat) : lexUnit A=A*31+24 :=
  (affine_add (affine_add (var_affine A) (const_affine A 1)) (affine_add (affine_add (affine_add (var_affine A) (const_affine A 1)) (var_affine A)) (affine_add (const_affine A 6) (affine_add (affine_add (affine_add (affine_add (var_affine A) (const_affine A 1)) (var_affine A)) (var_affine A)) (affine_add (affine_add (const_affine A 1) (affine_add (affine_add (affine_add (var_affine A) (affine_add (affine_add (affine_add (var_affine A) (const_affine A 2)) (affine_add (var_affine A) (const_affine A 2))) (affine_add (var_affine A) (const_affine A 1)))) (const_affine A 1)) (affine_add (affine_add (var_affine A) (affine_add (affine_add (affine_add (var_affine A) (const_affine A 2)) (affine_add (var_affine A) (const_affine A 2))) (affine_add (var_affine A) (const_affine A 1)))) (const_affine A 1)))) (affine_add (affine_add (affine_add (affine_add (var_affine A) (const_affine A 1)) (var_affine A)) (var_affine A)) (affine_add (affine_add (rfl : A*4=A*4+0) (rfl : A*10=A*10+0)) (const_affine A 1))))))))

theorem row_unit_linear (A : Nat) : rowsUnit A+1=A*3+5 :=
  (affine_add (affine_add (affine_add (affine_add (affine_add (const_affine A 0) (affine_add (var_affine A) (const_affine A 1))) (affine_add (var_affine A) (const_affine A 1))) (affine_add (var_affine A) (const_affine A 1))) (const_affine A 1)) (const_affine A 1))

theorem decoder_unit_linear (A : Nat) : decoderUnit A=A*34+29 :=
  affine_add (lex_unit_linear A) (row_unit_linear A)

theorem decode_linear (bytes : List Nat) :
    (decodeMeter bytes).2≤bytes.length*34+29 := by
  have h := decode_bound bytes
  rw [decoder_unit_linear] at h
  exact h

theorem decode_meaning (bytes : List Nat) (n : Nat) (f : Formula)
    (h : (decodeMeter bytes).1=some (n,f)) :
    ProctorDimacsLexical.RawMeaning bytes n f ∧
      (decodeMeter bytes).2≤bytes.length*34+29 := by
  rw [decode_value] at h
  exact ⟨(ProctorDimacsLexical.raw_decode_iff bytes n f).mp h,decode_linear bytes⟩

end ProctorDimacsDecoderMeter

#print axioms ProctorDimacsDecoderMeter.stage_value
#print axioms ProctorDimacsDecoderMeter.stage_bound
#print axioms ProctorDimacsDecoderMeter.decode_value
#print axioms ProctorDimacsDecoderMeter.stage_count
#print axioms ProctorDimacsDecoderMeter.decode_count
#print axioms ProctorDimacsDecoderMeter.decode_bound
#print axioms ProctorDimacsDecoderMeter.lex_unit_linear
#print axioms ProctorDimacsDecoderMeter.row_unit_linear
#print axioms ProctorDimacsDecoderMeter.decoder_unit_linear
#print axioms ProctorDimacsDecoderMeter.decode_linear
#print axioms ProctorDimacsDecoderMeter.decode_meaning
