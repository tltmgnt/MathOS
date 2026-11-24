/-! F034: independently specified token encoding of the expected CNF
and decimal-word grammar. The proof envelope still uses the existing
decoder; its universal encoder theorem is not asserted here. -/
namespace ProctorWireRoundtrip
open ProctorHallDeficiency
open ProctorDataParser

def RoundTrip {α : Type} (p : Parser α) (a : α) (ts : List Nat) : Prop :=
  ∀ rest, p (ts ++ rest) = some (a,rest)

def encNat (n : Nat) : List Nat := [n]
def encBool (b : Bool) : List Nat := [if b then 1 else 0]

theorem nat_roundtrip (n : Nat) : RoundTrip natToken n (encNat n) := by
  intro rest
  rfl

theorem bool_roundtrip (b : Bool) : RoundTrip boolToken b (encBool b) := by
  intro rest
  cases b <;> rfl

def encItems {α : Type} (enc : α → List Nat) : List α → List Nat
  | [] => []
  | a::as => enc a ++ encItems enc as

def encList {α : Type} (enc : α → List Nat) (xs : List α) : List Nat :=
  xs.length :: encItems enc xs

def FitsList {α : Type} (fits : α → Prop) (xs : List α) : Prop :=
  xs.length ≤ listLimit ∧ ∀ a ∈ xs, fits a

-- The library list identities use propext in Lean 4.14.0.
private theorem append_nil_exact {α : Type} (xs : List α) :
    xs ++ [] = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_assoc_exact {α : Type} (xs ys zs : List α) :
    (xs ++ ys) ++ zs = xs ++ (ys ++ zs) := by
  induction xs with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

-- Keep the reverse step constructive for the strict axiom audit.
private theorem reverseAux_append {α : Type} (xs ys zs : List α) :
    xs.reverseAux (ys ++ zs) = xs.reverseAux ys ++ zs := by
  induction xs generalizing ys with
  | nil => rfl
  | cons x xs ih => exact ih (x::ys)

private theorem reverse_cons_exact {α : Type} (x : α) (xs : List α) :
    (x::xs).reverse = xs.reverse ++ [x] :=
  reverseAux_append xs [] [x]

theorem items_roundtrip {α : Type} (p : Parser α) (enc : α → List Nat)
    (xs : List α) (h : ∀ a ∈ xs, RoundTrip p a (enc a))
    (rest : List Nat) (acc : List α) :
    manyAux p xs.length (encItems enc xs ++ rest) acc =
      some (acc.reverse ++ xs,rest) := by
  induction xs generalizing acc with
  | nil =>
    change some (acc.reverse,rest) = some (acc.reverse ++ [],rest)
    exact congrArg (fun xs => some (xs,rest)) (append_nil_exact acc.reverse).symm
  | cons a as ih =>
    change (do
      let (b,ts) ← p ((enc a ++ encItems enc as) ++ rest)
      manyAux p as.length ts (b::acc)) = some (acc.reverse ++ (a::as),rest)
    rw [append_assoc_exact, h a (List.Mem.head _) (encItems enc as ++ rest)]
    change manyAux p as.length (encItems enc as ++ rest) (a::acc) = _
    rw [ih (fun b hb => h b (List.Mem.tail _ hb)) (a::acc)]
    rw [reverse_cons_exact, append_assoc_exact] <;> rfl

theorem list_roundtrip {α : Type} (p : Parser α) (enc : α → List Nat)
    (xs : List α) (bound : xs.length ≤ listLimit)
    (h : ∀ a ∈ xs, RoundTrip p a (enc a)) :
    RoundTrip (listToken p) xs (encList enc xs) := by
  intro rest
  change (if xs.length ≤ listLimit then
    manyAux p xs.length (encItems enc xs ++ rest) [] else none) = some (xs,rest)
  rw [if_pos bound, items_roundtrip p enc xs h rest []] <;> rfl

def encLiteral (l : Literal) : List Nat := encNat l.1 ++ encBool l.2

theorem literal_roundtrip (l : Literal) :
    RoundTrip literalToken l (encLiteral l) := by
  intro rest
  cases l with
  | mk v b =>
    cases b <;> rfl

def encClause : Clause → List Nat := encList encLiteral
def encFormula : Formula → List Nat := encList encClause

def FitsFormula (f : Formula) : Prop :=
  FitsList (fun c => c.length ≤ listLimit) f

theorem clause_roundtrip (c : Clause) (h : c.length ≤ listLimit) :
    RoundTrip clauseToken c (encClause c) :=
  list_roundtrip literalToken encLiteral c h (fun l _ => literal_roundtrip l)

theorem formula_roundtrip (f : Formula) (h : FitsFormula f) :
    RoundTrip formulaToken f (encFormula f) :=
  list_roundtrip clauseToken encClause f h.left
    (fun c hc => clause_roundtrip c (h.right c hc))

def encExpected (n : Nat) (f : Formula) : List Nat :=
  3401 :: n :: encFormula f

theorem expected_roundtrip (n : Nat) (f : Formula) (h : FitsFormula f) :
    RoundTrip expectedToken (n,f) (encExpected n f) := by
  intro rest
  change (do
    let (g,ts) ← formulaToken (encFormula f ++ rest)
    some ((n,g),ts)) = some ((n,f),rest)
  rw [formula_roundtrip f h rest] <;> rfl

theorem expected_exact (n : Nat) (f : Formula) (h : FitsFormula f)
    (bytes : List Nat) (tokens : tokenize bytes = some (encExpected n f)) :
    decodeExpected bytes = some (n,f) := by
  unfold decodeExpected decode
  rw [tokens]
  change (do
    let (a,rest) ← expectedToken (encExpected n f)
    match rest with
    | [] => some a
    | _::_ => none) = some (n,f)
  have ht := expected_roundtrip n f h []
  rw [append_nil_exact] at ht
  rw [ht] <;> rfl

/-- Independent inductive decimal-word grammar with an accumulated
numeric value and digit count. A word contains digits only; the
terminal LF is added separately by wire. -/
inductive Word : Nat → Nat → List Nat → Nat → Prop where
  | done (v k : Nat) : k ≠ 0 → Word v k [] v
  | digit {v k b result : Nat} {bs : List Nat} :
      48 ≤ b → b ≤ 57 → k < digitLimit →
      (k > 0 → v ≠ 0) →
      Word (10*v+(b-48)) (k+1) bs result →
      Word v k (b::bs) result

theorem scan_word (v k result : Nat) (digits : List Nat)
    (h : Word v k digits result) (rest acc : List Nat) :
    scan (digits ++ 10::rest) v k acc =
      scan rest 0 0 (result::acc) := by
  induction h with
  | done v k hk =>
    change (if k=0 then none else scan rest 0 0 (v::acc)) = _
    rw [if_neg hk]
  | @digit v k b result bs lo hi size nonzero sub ih =>
    have notLF : b ≠ 10 := by
      intro eq
      rw [eq] at lo
      exact (Nat.not_le_of_gt (by decide : 10 < 48)) lo
    have allowed : ¬ (k ≥ digitLimit ∨ (k > 0 ∧ v=0)) := by
      intro bad
      cases bad with
      | inl e => exact (Nat.not_le_of_gt size) e
      | inr e => exact nonzero e.left e.right
    change (if b=10 then
      (if k=0 then none else scan (bs ++ 10::rest) 0 0 (v::acc))
      else if 48 ≤ b ∧ b ≤ 57 then
        (if k ≥ digitLimit ∨ (k > 0 ∧ v=0) then none
          else scan (bs ++ 10::rest) (10*v+(b-48)) (k+1) acc)
      else none) = _
    rw [if_neg notLF, if_pos ⟨lo,hi⟩, if_neg allowed]
    exact ih

/-- A sequence of canonical decimal words, one per natural token. -/
inductive Wire : List Nat → List Nat → Prop where
  | nil : Wire [] []
  | cons {digits bytes : List Nat} {v : Nat} {vs : List Nat} :
      Word 0 0 digits v → Wire bytes vs →
      Wire (digits ++ 10::bytes) (v::vs)

theorem scan_words (bytes tokens : List Nat) (h : Wire bytes tokens)
    (acc : List Nat) :
    scan bytes 0 0 acc = some (acc.reverse ++ tokens) := by
  induction h generalizing acc with
  | nil => change some acc.reverse = some (acc.reverse ++ []); rw [append_nil_exact]
  | @cons digits bytes v vs word tail ih =>
    rw [scan_word 0 0 v digits word bytes acc, ih (v::acc)]
    rw [reverse_cons_exact, append_assoc_exact] <;> rfl

theorem tokenize_words (bytes tokens : List Nat) (h : Wire bytes tokens)
    (bound : bytes.length ≤ byteLimit) : tokenize bytes = some tokens := by
  unfold tokenize
  rw [if_pos bound, scan_words bytes tokens h []] <;> rfl

/-- Full byte-to-expected-CNF round trip for an independently
specified canonical wire word sequence and bounded lists/bytes. -/
theorem expected_bytes_roundtrip (n : Nat) (f : Formula)
    (fits : FitsFormula f) (bytes : List Nat)
    (grammar : Wire bytes (encExpected n f))
    (bound : bytes.length ≤ byteLimit) :
    decodeExpected bytes = some (n,f) :=
  expected_exact n f fits bytes (tokenize_words _ _ grammar bound)

end ProctorWireRoundtrip

#print axioms ProctorWireRoundtrip.nat_roundtrip
#print axioms ProctorWireRoundtrip.bool_roundtrip
#print axioms ProctorWireRoundtrip.items_roundtrip
#print axioms ProctorWireRoundtrip.list_roundtrip
#print axioms ProctorWireRoundtrip.literal_roundtrip
#print axioms ProctorWireRoundtrip.clause_roundtrip
#print axioms ProctorWireRoundtrip.formula_roundtrip
#print axioms ProctorWireRoundtrip.expected_roundtrip
#print axioms ProctorWireRoundtrip.expected_exact
#print axioms ProctorWireRoundtrip.scan_word
#print axioms ProctorWireRoundtrip.scan_words
#print axioms ProctorWireRoundtrip.tokenize_words
#print axioms ProctorWireRoundtrip.expected_bytes_roundtrip
