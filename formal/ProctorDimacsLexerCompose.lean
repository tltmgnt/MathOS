/-! F034: complete strict DIMACS lexer selected-charge composition.
The production lexer is unchanged; counts are not machine time. -/
namespace ProctorDimacsLexerCompose
open ProctorHallDeficiency
open ProctorDimacsInput (takeHeader splitWords signedWords stripPrefix headerNumbers lexDimacs)
open ProctorDimacsLexical (split_sound header_sound prefix_sound)
open ProctorDimacsLexMeter
open ProctorDataParser (byteLimit)
open ProctorTerminalPolynomial (mul_mono)

abbrev Meter (α : Type) := Option α × Nat

def bindM {α β : Type} (r : Meter α) (f : α → Meter β) : Meter β :=
  match r.1 with
  | none => (none,r.2)
  | some a =>
    let s := f a
    (s.1,r.2+s.2)

def retM {α : Type} (a : α) : Meter α := (some a,0)

def addM {α : Type} (k : Nat) (r : Meter α) : Meter α :=
  (r.1,k+r.2)

theorem bind_value {α β : Type} (r : Meter α) (f : α → Meter β)
    (p : Option α) (q : α → Option β)
    (hr : r.1=p) (hf : ∀ a, (f a).1=q a) :
    (bindM r f).1=(do let a ← p; q a) := by
  unfold bindM
  rw [← hr]
  cases r.1 with
  | none => rfl
  | some a => exact hf a

theorem bind_bound {α β : Type} (r : Meter α) (f : α → Meter β)
    (R K : Nat) (hr : r.2≤R) (hf : ∀ a, r.1=some a → (f a).2≤K) :
    (bindM r f).2≤R+K := by
  unfold bindM
  cases e : r.1 with
  | none => exact Nat.le_trans hr (Nat.le_add_right _ _)
  | some a => exact Nat.add_le_add hr (hf a e)

private theorem len_append {α : Type} (a b : List α) :
    (a++b).length=a.length+b.length := by
  induction a with
  | nil => exact (Nat.zero_add _).symm
  | cons _ xs ih =>
    change (xs++b).length+1=(xs.length+1)+b.length
    rw [ih]
    exact (Nat.succ_add xs.length b.length).symm

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

-- Two additional credits per attempted word (dispatch, reversal).
-- Reversal of initial accumulator cells is not included.
def signedAux : List (List Nat) → List Literal → Nat → Meter (List Literal)
  | [],acc,k => (some acc.reverse,k+1)
  | w::ws,acc,k =>
    let m := signedMeter w
    match m.1 with
    | none => (none,k+(m.2+2))
    | some l => signedAux ws (l::acc) (k+(m.2+2))

def wordBudget : List (List Nat) → Nat
  | [] => 1
  | w::ws => (signedUnit w.length+2)+wordBudget ws

theorem signed_aux_value (ws : List (List Nat)) (acc : List Literal) (k : Nat) :
    (signedAux ws acc k).1=signedWords ws acc := by
  induction ws generalizing acc k with
  | nil => rfl
  | cons w ws ih =>
    change (match (signedMeter w).1 with
      | none => (none,k+((signedMeter w).2+2))
      | some l => signedAux ws (l::acc) (k+((signedMeter w).2+2))).1 =
      (do let l ← ProctorDimacsInput.signedWord w; signedWords ws (l::acc))
    rw [← signed_value w]
    cases (signedMeter w).1 with
    | none => rfl
    | some l => exact ih (l::acc) _

theorem signed_aux_bound (ws : List (List Nat)) (acc : List Literal) (k : Nat) :
    (signedAux ws acc k).2≤k+wordBudget ws := by
  induction ws generalizing acc k with
  | nil => exact Nat.le_refl _
  | cons w ws ih =>
    change (match (signedMeter w).1 with
      | none => (none,k+((signedMeter w).2+2))
      | some l => signedAux ws (l::acc) (k+((signedMeter w).2+2))).2 ≤
      k+((signedUnit w.length+2)+wordBudget ws)
    have h := Nat.add_le_add (signed_bound w) (Nat.le_refl 2)
    cases (signedMeter w).1 with
    | none =>
      exact Nat.add_le_add (Nat.le_refl _)
        (Nat.le_trans h (Nat.le_add_right _ _))
    | some l =>
      calc
        (signedAux ws (l::acc) (k+((signedMeter w).2+2))).2
            ≤ (k+((signedMeter w).2+2))+wordBudget ws := ih (l::acc) _
        _ ≤ (k+(signedUnit w.length+2))+wordBudget ws :=
          Nat.add_le_add (Nat.add_le_add (Nat.le_refl _) h) (Nat.le_refl _)
        _ = k+((signedUnit w.length+2)+wordBudget ws) := Nat.add_assoc _ _ _

private theorem word_charge (n : Nat) : signedUnit n+2=n*4+10 := by
  unfold signedUnit naturalUnit
  change n+((n+2)+(n+2)+(n+1))+1+2+2=0+n+n+n+n+10
  rw [Nat.zero_add]
  calc
    n+((n+2)+(n+2)+(n+1))+1+2+2 =
      n+n+n+n+(2+2+1+1+2+2) := by ac_rfl
    _ = n+n+n+n+10 := rfl

theorem word_budget_linear (ws : List (List Nat)) :
    wordBudget ws=wordMass ws*4+ws.length*10+1 := by
  induction ws with
  | nil => rfl
  | cons w ws ih =>
    change (signedUnit w.length+2)+wordBudget ws =
      (w.length+wordMass ws)*4+(ws.length+1)*10+1
    rw [word_charge,ih,add_mul_local w.length (wordMass ws) 4,
      add_mul_local ws.length 1 10]
    change w.length*4+10+(wordMass ws*4+ws.length*10+1) =
      w.length*4+wordMass ws*4+(ws.length*10+10)+1
    ac_rfl

def signedWordsMeter (ws : List (List Nat)) : Meter (List Literal) :=
  signedAux ws [] 0

theorem signed_words_value (ws : List (List Nat)) :
    (signedWordsMeter ws).1=signedWords ws [] :=
  signed_aux_value ws [] 0

theorem signed_words_bound (ws : List (List Nat)) :
    (signedWordsMeter ws).2≤wordMass ws*4+ws.length*10+1 := by
  have h := signed_aux_bound ws [] 0
  rw [Nat.zero_add,word_budget_linear] at h
  exact h

def splitStage (bytes : List Nat) : Meter (List (List Nat)) :=
  let r := splitMeter bytes
  (some r.1,r.2)

def splitUnit (A : Nat) : Nat := (A+1)+A+A
def bodyUnit (A : Nat) : Nat := splitUnit A+(A*4+A*10+1)

private theorem split_unit_mono (a b : Nat) (h : a≤b) :
    splitUnit a≤splitUnit b :=
  Nat.add_le_add (Nat.add_le_add (Nat.succ_le_succ h) h) h

private theorem body_unit_mono (a b : Nat) (h : a≤b) :
    bodyUnit a≤bodyUnit b :=
  Nat.add_le_add (split_unit_mono a b h)
    (Nat.add_le_add (Nat.add_le_add (mul_mono h (Nat.le_refl 4))
      (mul_mono h (Nat.le_refl 10))) (Nat.le_refl 1))

def bodyMeter (bytes : List Nat) : Meter (List Literal) :=
  bindM (splitStage bytes) signedWordsMeter

theorem body_value (bytes : List Nat) :
    (bodyMeter bytes).1=signedWords (splitWords bytes [] []) [] :=
  bind_value _ _ (some (splitWords bytes [] []))
    (fun ws => signedWords ws []) rfl signed_words_value

theorem body_bound (bytes : List Nat) :
    (bodyMeter bytes).2≤bodyUnit bytes.length := by
  unfold bodyMeter bodyUnit
  apply bind_bound _ _ _ _ (split_bound bytes)
  intro ws h
  change some (splitWords bytes [] [])=some ws at h
  have he := Option.some.inj h
  have hs := split_sound bytes [] []
  have hm : wordMass (splitWords bytes [] [])≤bytes.length := split_mass bytes [] [] _ hs
  have hc : (splitWords bytes [] []).length≤bytes.length :=
    ProctorDimacsSize.split_count bytes [] [] _ hs
  rw [← he]
  exact Nat.le_trans (signed_words_bound _)
    (Nat.add_le_add (Nat.add_le_add (mul_mono hm (Nat.le_refl 4))
      (mul_mono hc (Nat.le_refl 10))) (Nat.le_refl 1))

def numbersMeter : List (List Nat) → Meter (Nat × Nat)
  | [a,b] => addM 1 (bindM (naturalMeter a) (fun n =>
      bindM (naturalMeter b) (fun m => retM (n,m))))
  | _ => (none,1)

theorem numbers_value (ws : List (List Nat)) :
    (numbersMeter ws).1=headerNumbers ws := by
  cases ws with
  | nil => rfl
  | cons a rest =>
    cases rest with
    | nil => rfl
    | cons b tail =>
      cases tail with
      | nil =>
        change (bindM (naturalMeter a) (fun n =>
          bindM (naturalMeter b) (fun m => retM (n,m)))).1 =
          (do let n ← ProctorDimacsInput.naturalWord a
              let m ← ProctorDimacsInput.naturalWord b
              some (n,m))
        apply bind_value _ _ _ _ (natural_value a)
        intro n
        exact bind_value _ _ _ _ (natural_value b) (fun _ => rfl)
      | cons _ _ => rfl

def numbersUnit (A : Nat) : Nat := 1+(naturalUnit A+naturalUnit A)

theorem numbers_bound (ws : List (List Nat)) (A : Nat) (h : wordMass ws≤A) :
    (numbersMeter ws).2≤numbersUnit A := by
  cases ws with
  | nil => exact Nat.le_add_right _ _
  | cons a rest =>
    cases rest with
    | nil => exact Nat.le_add_right _ _
    | cons b tail =>
      cases tail with
      | nil =>
        change a.length+b.length≤A at h
        have ha := Nat.le_trans (Nat.le_add_right _ _) h
        have hb := Nat.le_trans (Nat.le_add_left _ _) h
        have hn := Nat.le_trans (natural_bound a) (natural_mono _ _ ha)
        have hm := Nat.le_trans (natural_bound b) (natural_mono _ _ hb)
        change 1+(bindM (naturalMeter a) (fun n =>
          bindM (naturalMeter b) (fun m => retM (n,m)))).2≤numbersUnit A
        apply Nat.add_le_add (Nat.le_refl 1)
        apply bind_bound _ _ _ _ hn
        intro n _
        exact bind_bound (naturalMeter b) (fun m => retM (n,m))
          (naturalUnit A) 0 hm (fun _ _ => Nat.le_refl 0)
      | cons _ _ => exact Nat.le_add_right _ _

abbrev LexResult := Nat × Nat × List Literal

def restMeter (rest body : List Nat) : Meter LexResult :=
  bindM (splitStage rest) (fun ws =>
    bindM (numbersMeter ws) (fun nm =>
      bindM (bodyMeter body) (fun ts => retM (nm.1,nm.2,ts))))

theorem rest_value (rest body : List Nat) :
    (restMeter rest body).1=(do
      let (n,m) ← headerNumbers (splitWords rest [] [])
      let ts ← signedWords (splitWords body [] []) []
      some (n,m,ts)) := by
  change (bindM (numbersMeter (splitWords rest [] [])) (fun nm =>
    bindM (bodyMeter body) (fun ts => retM (nm.1,nm.2,ts)))).1=_
  apply bind_value _ _ _ _ (numbers_value _)
  intro nm
  cases nm with
  | mk n m => exact bind_value _ _ _ _ (body_value body) (fun _ => rfl)

def restUnit (A : Nat) : Nat :=
  splitUnit A+(numbersUnit A+bodyUnit A)

theorem rest_bound (rest body : List Nat) (A : Nat)
    (hr : rest.length≤A) (hb : body.length≤A) :
    (restMeter rest body).2≤restUnit A := by
  unfold restMeter restUnit
  apply bind_bound _ _ _ _ (Nat.le_trans (split_bound rest) (split_unit_mono _ _ hr))
  intro ws h
  change some (splitWords rest [] [])=some ws at h
  have eq := Option.some.inj h
  have hm : wordMass ws≤A := by
    rw [← eq]
    exact Nat.le_trans (split_mass rest [] [] _ (split_sound rest [] [])) hr
  apply bind_bound _ _ _ _ (numbers_bound ws A hm)
  intro nm _
  exact bind_bound (bodyMeter body) (fun ts => retM (nm.1,nm.2,ts))
    (bodyUnit A) 0 (Nat.le_trans (body_bound body) (body_unit_mono _ _ hb))
    (fun _ _ => Nat.le_refl 0)

def magic : List Nat := [112,32,99,110,102,32]

def prefixStage (header : List Nat) : Meter (List Nat) :=
  (stripPrefix magic header,6)

def afterHeader (h : List Nat × List Nat) : Meter LexResult :=
  bindM (prefixStage h.1) (fun rest => restMeter rest h.2)

theorem after_header_value (h : List Nat × List Nat) :
    (afterHeader h).1=(do
      let rest ← stripPrefix magic h.1
      let (n,m) ← headerNumbers (splitWords rest [] [])
      let ts ← signedWords (splitWords h.2 [] []) []
      some (n,m,ts)) :=
  bind_value _ _ _ _ rfl (fun rest => rest_value rest h.2)

theorem after_header_bound (h : List Nat × List Nat) (A : Nat)
    (hh : h.1.length≤A) (hb : h.2.length≤A) :
    (afterHeader h).2≤6+restUnit A := by
  unfold afterHeader
  apply bind_bound _ _ _ _ (Nat.le_refl 6)
  intro rest he
  change stripPrefix magic h.1=some rest at he
  have hp := prefix_sound magic h.1 rest he
  have hl : rest.length≤h.1.length := by
    rw [hp,len_append]
    exact Nat.le_add_left _ _
  exact rest_bound rest h.2 A (Nat.le_trans hl hh) hb

def lexMeter (bytes : List Nat) : Meter LexResult :=
  if bytes.length>byteLimit then (none,bytes.length+1)
  else addM (bytes.length+1) (bindM (headerMeter bytes) afterHeader)

def lexUnit (A : Nat) : Nat :=
  (A+1)+(((A+1)+A)+(6+restUnit A))

theorem lex_value (bytes : List Nat) :
    (lexMeter bytes).1=lexDimacs bytes := by
  unfold lexMeter lexDimacs
  by_cases h : bytes.length>byteLimit
  · rw [if_pos h,if_pos h]
  · rw [if_neg h,if_neg h]
    change (bindM (headerMeter bytes) afterHeader).1=(do
      let (header,body) ← takeHeader bytes []
      let rest ← stripPrefix magic header
      let (n,m) ← headerNumbers (splitWords rest [] [])
      let ts ← signedWords (splitWords body [] []) []
      some (n,m,ts))
    apply bind_value _ _ _ _ (header_value bytes)
    intro pair
    cases pair with
    | mk header body => exact after_header_value (header,body)

theorem lex_bound (bytes : List Nat) :
    (lexMeter bytes).2≤lexUnit bytes.length := by
  unfold lexMeter lexUnit
  by_cases h : bytes.length>byteLimit
  · rw [if_pos h]
    exact Nat.le_add_right _ _
  · rw [if_neg h]
    change (bytes.length+1)+(bindM (headerMeter bytes) afterHeader).2≤_
    apply Nat.add_le_add (Nat.le_refl _)
    apply bind_bound _ _ _ _ (header_bound bytes)
    intro pair e
    cases pair with
    | mk head body =>
      rw [header_value] at e
      have hh := header_sound bytes [] head body e
      exact after_header_bound (head,body) bytes.length
        (header_length bytes [] head body hh)
        (ProctorDimacsSize.header_body_count bytes [] head body hh)

end ProctorDimacsLexerCompose

#print axioms ProctorDimacsLexerCompose.bind_value
#print axioms ProctorDimacsLexerCompose.bind_bound
#print axioms ProctorDimacsLexerCompose.signed_aux_value
#print axioms ProctorDimacsLexerCompose.signed_aux_bound
#print axioms ProctorDimacsLexerCompose.word_budget_linear
#print axioms ProctorDimacsLexerCompose.signed_words_value
#print axioms ProctorDimacsLexerCompose.signed_words_bound
#print axioms ProctorDimacsLexerCompose.body_value
#print axioms ProctorDimacsLexerCompose.body_bound
#print axioms ProctorDimacsLexerCompose.numbers_value
#print axioms ProctorDimacsLexerCompose.numbers_bound
#print axioms ProctorDimacsLexerCompose.rest_value
#print axioms ProctorDimacsLexerCompose.rest_bound
#print axioms ProctorDimacsLexerCompose.after_header_value
#print axioms ProctorDimacsLexerCompose.after_header_bound
#print axioms ProctorDimacsLexerCompose.lex_value
#print axioms ProctorDimacsLexerCompose.lex_bound
