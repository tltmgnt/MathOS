/-! F034: a strict comment-free DIMACS CNF subset, with an independent
zero-terminated clause grammar over lexed signed tokens. No solver or
proof producer is involved in decoding the expected input. -/
namespace ProctorDimacsInput
open ProctorHallDeficiency
open ProctorDataParser (byteLimit listLimit tokenize decodeEnvelope)
open ProctorUnifiedReplay (Envelope boundCheck)

def white (b : Nat) : Bool :=
  b == 32 || b == 9 || b == 10 || b == 13

def splitWords : List Nat → List Nat → List (List Nat) → List (List Nat)
  | [], word, acc =>
    (if word.isEmpty then acc else word.reverse::acc).reverse
  | b::bs, word, acc =>
    if white b then
      splitWords bs [] (if word.isEmpty then acc else word.reverse::acc)
    else splitWords bs (b::word) acc

def takeHeader : List Nat → List Nat → Option (List Nat × List Nat)
  | [], _ => none
  | b::bs, acc =>
    if b=10 then some (acc.reverse,bs) else takeHeader bs (b::acc)

def naturalWord (word : List Nat) : Option Nat :=
  match tokenize (word ++ [10]) with
  | some [n] => some n
  | _ => none

def signedWord : List Nat → Option Literal
  | 45::ds => do
    let v ← naturalWord ds
    if v=0 then none else some (v,false)
  | ds => do
    let v ← naturalWord ds
    some (v,true)

def signedWords : List (List Nat) → List Literal → Option (List Literal)
  | [], acc => some acc.reverse
  | w::ws, acc => do
    let l ← signedWord w
    signedWords ws (l::acc)

/-- Require an initial p cnf header ending in LF. Only numeric body
tokens and ASCII whitespace are supported; no comments or extensions. -/
def lexDimacs (bytes : List Nat) : Option (Nat × Nat × List Literal) := do
  if bytes.length > byteLimit then none else
  let (header,body) ← takeHeader bytes []
  match header with
  | 112::32::99::110::102::32::rest =>
    match splitWords rest [] [] with
    | [a,b] =>
      let n ← naturalWord a
      let m ← naturalWord b
      let ts ← signedWords (splitWords body [] []) []
      some (n,m,ts)
    | _ => none
  | _ => none

def parseRow (n : Nat) : List Literal → Option (Clause × List Literal)
  | [] => none
  | l::ls =>
    if l.1=0 then
      if l.2 then some ([],ls) else none
    else if l.1≤n then do
      let (c,rest) ← parseRow n ls
      some (l::c,rest)
    else none

def parseRows (n : Nat) : Nat → List Literal → Option Formula
  | 0, [] => some []
  | 0, _::_ => none
  | k+1, ts => do
    let (c,rest) ← parseRow n ts
    if c.length≤listLimit then do
      let f ← parseRows n k rest
      some (c::f)
    else none

def decodeDimacs (bytes : List Nat) : Option (Nat × Formula) := do
  let (n,m,ts) ← lexDimacs bytes
  if m≤listLimit then do
    let f ← parseRows n m ts
    some (n,f)
  else none

-- Independent token-level grammar. Row preserves literal order and
-- duplicates, consumes exactly one positive zero and returns suffix.
inductive Row (n : Nat) : List Literal → Clause → List Literal → Prop where
  | zero (rest : List Literal) : Row n ((0,true)::rest) [] rest
  | lit {l : Literal} {ts : List Literal} {c : Clause} {rest : List Literal} :
      0 < l.1 → l.1≤n → Row n ts c rest → Row n (l::ts) (l::c) rest

inductive Rows (n : Nat) : Nat → List Literal → Formula → Prop where
  | nil : Rows n 0 [] []
  | cons {k : Nat} {ts rest : List Literal} {c : Clause} {f : Formula} :
      Row n ts c rest → c.length≤listLimit → Rows n k rest f →
      Rows n (k+1) ts (c::f)

theorem row_sound (n : Nat) (ts : List Literal) (c : Clause)
    (rest : List Literal) (h : parseRow n ts = some (c,rest)) :
    Row n ts c rest := by
  induction ts generalizing c rest with
  | nil => cases h
  | cons l ls ih =>
    cases l with
    | mk v sign =>
      change (if v=0 then
        (if sign then some ([],ls) else none)
        else if v≤n then (do
          let (d,tail) ← parseRow n ls
          some ((v,sign)::d,tail))
        else none) = some (c,rest) at h
      by_cases z : v=0
      · cases z
        rw [if_pos rfl] at h
        cases sign with
        | false => cases h
        | true =>
          cases h
          exact Row.zero _
      · rw [if_neg z] at h
        by_cases le : v≤n
        · rw [if_pos le] at h
          cases hp : parseRow n ls with
          | none =>
            rw [hp] at h
            cases h
          | some pair =>
            cases pair with
            | mk d tail =>
              rw [hp] at h
              have eq : ((v,sign)::d,tail) = (c,rest) := Option.some.inj h
              have row := Row.lit (l := (v,sign)) (Nat.lt_of_le_of_ne (Nat.zero_le v)
                (fun e => z e.symm)) le (ih d tail hp)
              cases eq
              exact row
        · rw [if_neg le] at h
          cases h

theorem row_complete (n : Nat) (ts : List Literal) (c : Clause)
    (rest : List Literal) (h : Row n ts c rest) :
    parseRow n ts = some (c,rest) := by
  induction h with
  | zero rest => rfl
  | @lit l ts c rest pos le sub ih =>
    change (if l.1=0 then (if l.2 then some ([],ts) else none)
      else if l.1≤n then (do
        let (d,tail) ← parseRow n ts
        some (l::d,tail)) else none) = some (l::c,rest)
    rw [if_neg (Nat.ne_of_gt pos),if_pos le,ih] <;> rfl

theorem rows_sound (n k : Nat) (ts : List Literal) (f : Formula)
    (h : parseRows n k ts = some f) : Rows n k ts f := by
  induction k generalizing ts f with
  | zero =>
    cases ts with
    | nil =>
      cases h
      exact Rows.nil
    | cons l ls => cases h
  | succ k ih =>
    change (do
      let (c,rest) ← parseRow n ts
      if c.length≤listLimit then (do
        let g ← parseRows n k rest
        some (c::g)) else none) = some f at h
    cases hp : parseRow n ts with
    | none =>
      rw [hp] at h
      cases h
    | some pair =>
      cases pair with
      | mk c rest =>
        rw [hp] at h
        change (if c.length≤listLimit then (do
          let g ← parseRows n k rest
          some (c::g)) else none) = some f at h
        by_cases size : c.length≤listLimit
        · rw [if_pos size] at h
          cases hg : parseRows n k rest with
          | none =>
            rw [hg] at h
            cases h
          | some g =>
            rw [hg] at h
            have eq : c::g = f := Option.some.inj h
            cases eq
            exact Rows.cons (row_sound n ts c rest hp) size (ih rest g hg)
        · rw [if_neg size] at h
          cases h

theorem rows_complete (n k : Nat) (ts : List Literal) (f : Formula)
    (h : Rows n k ts f) : parseRows n k ts = some f := by
  induction h with
  | nil => rfl
  | @cons k ts rest c f row size sub ih =>
    change (do
      let (d,tail) ← parseRow n ts
      if d.length≤listLimit then (do
        let g ← parseRows n k tail
        some (d::g)) else none) = some (c::f)
    rw [row_complete n ts c rest row]
    change (if c.length≤listLimit then (do
      let g ← parseRows n k rest
      some (c::g)) else none) = some (c::f)
    rw [if_pos size,ih] <;> rfl

/-- Byte interpretation uses the explicit lexer and independent
zero-terminated token grammar. Raw-byte lexical completeness is
not claimed here. -/
def Meaning (bytes : List Nat) (n : Nat) (f : Formula) : Prop :=
  ∃ m ts, lexDimacs bytes = some (n,m,ts) ∧
    m≤listLimit ∧ Rows n m ts f

theorem decode_sound (bytes : List Nat) (n : Nat) (f : Formula)
    (h : decodeDimacs bytes = some (n,f)) : Meaning bytes n f := by
  unfold decodeDimacs at h
  cases he : lexDimacs bytes with
  | none =>
    rw [he] at h
    cases h
  | some triple =>
    obtain ⟨v,m,ts⟩ := triple
    rw [he] at h
    change (if m≤listLimit then (do
      let g ← parseRows v m ts
      some (v,g)) else none) = some (n,f) at h
    by_cases size : m≤listLimit
    · rw [if_pos size] at h
      cases hf : parseRows v m ts with
      | none =>
        rw [hf] at h
        cases h
      | some g =>
        rw [hf] at h
        have eq : (v,g) = (n,f) := Option.some.inj h
        have meaning : Meaning bytes v g := ⟨m,ts,he,size,rows_sound v m ts g hf⟩
        cases eq
        exact meaning
    · rw [if_neg size] at h
      cases h

theorem decode_complete (bytes : List Nat) (n : Nat) (f : Formula)
    (h : Meaning bytes n f) : decodeDimacs bytes = some (n,f) := by
  obtain ⟨m,ts,he,size,rows⟩ := h
  unfold decodeDimacs
  rw [he]
  change (if m≤listLimit then (do
    let g ← parseRows n m ts
    some (n,g)) else none) = some (n,f)
  rw [if_pos size,rows_complete n m ts f rows] <;> rfl

def checkDimacs (expected proof : List Nat) : Bool :=
  match decodeDimacs expected, decodeEnvelope proof with
  | some (n,f), some e => boundCheck n f e
  | _, _ => false

theorem accepted_decoded (expected proof : List Nat)
    (h : checkDimacs expected proof = true) :
    ∃ n f e, decodeDimacs expected = some (n,f) ∧
      decodeEnvelope proof = some e ∧ boundCheck n f e = true := by
  unfold checkDimacs at h
  cases he : decodeDimacs expected with
  | none =>
    rw [he] at h
    exact Bool.noConfusion h
  | some nf =>
    cases nf with
    | mk n f =>
      rw [he] at h
      cases hp : decodeEnvelope proof with
      | none =>
        rw [hp] at h
        exact Bool.noConfusion h
      | some e =>
        rw [hp] at h
        exact ⟨n,f,e,rfl,rfl,h⟩

theorem accepted_unsat (expected proof : List Nat)
    (h : checkDimacs expected proof = true) :
    ∃ n f, Meaning expected n f ∧ ¬ ∃ x : Assignment, FormulaSat f x := by
  obtain ⟨n,f,e,he,_,hc⟩ := accepted_decoded expected proof h
  exact ⟨n,f,decode_sound expected n f he,
    ProctorUnifiedReplay.bound_sound n f e hc⟩

theorem accepted_binding (expected proof : List Nat)
    (h : checkDimacs expected proof = true) :
    ∃ n f e, Meaning expected n f ∧ decodeEnvelope proof = some e ∧
      n=e.variableBound ∧ f=e.original := by
  obtain ⟨n,f,e,he,hp,hc⟩ := accepted_decoded expected proof h
  have hb := ProctorUnifiedReplay.binding_exact n f e hc
  exact ⟨n,f,e,decode_sound expected n f he,hp,hb.left,hb.right⟩

end ProctorDimacsInput

#print axioms ProctorDimacsInput.row_sound
#print axioms ProctorDimacsInput.row_complete
#print axioms ProctorDimacsInput.rows_sound
#print axioms ProctorDimacsInput.rows_complete
#print axioms ProctorDimacsInput.decode_sound
#print axioms ProctorDimacsInput.decode_complete
#print axioms ProctorDimacsInput.accepted_decoded
#print axioms ProctorDimacsInput.accepted_unsat
#print axioms ProctorDimacsInput.accepted_binding
