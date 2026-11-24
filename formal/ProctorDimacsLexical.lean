/-! F034: independent raw-byte grammar for the strict DIMACS subset.
No parser function occurs in the grammar relations. Append after
ProctorEnvelopeRoundtrip and ProctorDimacsInput. -/
namespace ProctorDimacsLexical
open ProctorHallDeficiency
open ProctorDimacsInput
open ProctorDataParser (byteLimit listLimit tokenize)
open ProctorWireRoundtrip (Wire)
open ProctorEnvelopeRoundtrip (wire_iff)

def Space (b : Nat) : Prop := b=32 ∨ b=9 ∨ b=10 ∨ b=13

def flush (word : List Nat) (acc : List (List Nat)) : List (List Nat) :=
  match word with
  | [] => acc
  | _::_ => word.reverse::acc

private theorem flush_eq (word : List Nat) (acc : List (List Nat)) :
    (if word.isEmpty then acc else word.reverse::acc) = flush word acc := by
  cases word <;> rfl

-- State-indexed grammar for maximal non-whitespace runs. Current word
-- and completed words are accumulated in reverse order.
inductive Split : List Nat → List Nat → List (List Nat) → List (List Nat) → Prop where
  | done (w : List Nat) (a : List (List Nat)) :
      Split [] w a (flush w a).reverse
  | sep {b : Nat} {bs w : List Nat} {a out : List (List Nat)} :
      Space b → Split bs [] (flush w a) out → Split (b::bs) w a out
  | char {b : Nat} {bs w : List Nat} {a out : List (List Nat)} :
      ¬ Space b → Split bs (b::w) a out → Split (b::bs) w a out

theorem split_sound (bytes word : List Nat) (acc : List (List Nat)) :
    Split bytes word acc (splitWords bytes word acc) := by
  induction bytes generalizing word acc with
  | nil =>
    change Split [] word acc
      (if word.isEmpty then acc else word.reverse::acc).reverse
    rw [flush_eq]
    exact Split.done _ _
  | cons b bs ih =>
    change Split (b::bs) word acc (if white b then
      splitWords bs [] (if word.isEmpty then acc else word.reverse::acc)
      else splitWords bs (b::word) acc)
    unfold white
    by_cases h : b=32 ∨ b=9 ∨ b=10 ∨ b=13
    · have e : (if b=32 ∨ b=9 ∨ b=10 ∨ b=13 then true else false) = true :=
        if_pos h
      rw [e]
      change Split (b::bs) word acc (splitWords bs [] (if word.isEmpty then acc else word.reverse::acc))
      rw [flush_eq]
      exact Split.sep h (ih [] (flush word acc))
    · have e : (if b=32 ∨ b=9 ∨ b=10 ∨ b=13 then true else false) = false :=
        if_neg h
      rw [e]
      exact Split.char h (ih (b::word) acc)

theorem split_complete (bytes word : List Nat) (acc out : List (List Nat))
    (h : Split bytes word acc out) : splitWords bytes word acc = out := by
  induction h with
  | done w a =>
    change (if w.isEmpty then a else w.reverse::a).reverse = _
    rw [flush_eq]
  | @sep b bs w a out sp sub ih =>
    change (if white b then splitWords bs []
      (if w.isEmpty then a else w.reverse::a) else splitWords bs (b::w) a) = out
    unfold white
    have e : (if b=32 ∨ b=9 ∨ b=10 ∨ b=13 then true else false) = true :=
      if_pos sp
    rw [e]
    change splitWords bs [] (if w.isEmpty then a else w.reverse::a) = out
    rw [flush_eq]
    exact ih
  | @char b bs w a out sp sub ih =>
    change (if white b then splitWords bs []
      (if w.isEmpty then a else w.reverse::a) else splitWords bs (b::w) a) = out
    unfold white
    have e : (if b=32 ∨ b=9 ∨ b=10 ∨ b=13 then true else false) = false :=
      if_neg sp
    rw [e]
    exact ih

-- First LF terminates the header, including for CRLF.
inductive Header : List Nat → List Nat → List Nat → List Nat → Prop where
  | endLine (rest acc : List Nat) : Header (10::rest) acc acc.reverse rest
  | next {b : Nat} {bs acc head body : List Nat} :
      b≠10 → Header bs (b::acc) head body → Header (b::bs) acc head body

theorem header_sound (bytes acc head body : List Nat)
    (h : takeHeader bytes acc = some (head,body)) : Header bytes acc head body := by
  induction bytes generalizing acc head body with
  | nil => cases h
  | cons b bs ih =>
    change (if b=10 then some (acc.reverse,bs) else takeHeader bs (b::acc)) =
      some (head,body) at h
    by_cases e : b=10
    · cases e
      rw [if_pos rfl] at h
      cases h
      exact Header.endLine _ _
    · rw [if_neg e] at h
      exact Header.next e (ih (b::acc) head body h)

theorem header_complete (bytes acc head body : List Nat)
    (h : Header bytes acc head body) : takeHeader bytes acc = some (head,body) := by
  induction h with
  | endLine rest acc => rfl
  | @next b bs acc head body ne sub ih =>
    change (if b=10 then some (acc.reverse,bs) else takeHeader bs (b::acc)) = _
    rw [if_neg ne]
    exact ih

theorem prefix_sound (ps bytes rest : List Nat)
    (h : stripPrefix ps bytes = some rest) : bytes=ps++rest := by
  induction ps generalizing bytes with
  | nil =>
    change some bytes = some rest at h
    exact Option.some.inj h
  | cons p ps ih =>
    cases bytes with
    | nil => cases h
    | cons b bs =>
      change (if p=b then stripPrefix ps bs else none) = some rest at h
      by_cases e : p=b
      · rw [if_pos e] at h
        cases e
        exact congrArg (List.cons p) (ih bs h)
      · rw [if_neg e] at h
        cases h

theorem prefix_complete (ps rest : List Nat) :
    stripPrefix ps (ps++rest) = some rest := by
  induction ps with
  | nil => rfl
  | cons p ps ih =>
    change (if p=p then stripPrefix ps (ps++rest) else none) = some rest
    rw [if_pos rfl]
    exact ih

-- A natural word is precisely a one-token canonical Wire sequence
-- after adding its LF. Wire was specified independently of tokenize.
def Natural (w : List Nat) (v : Nat) : Prop :=
  (w++[10]).length ≤ byteLimit ∧ Wire (w++[10]) [v]

theorem natural_iff (w : List Nat) (v : Nat) :
    naturalWord w = some v ↔ Natural w v := by
  constructor
  · intro h
    unfold naturalWord at h
    cases e : tokenize (w++[10]) with
    | none =>
      rw [e] at h
      cases h
    | some ts =>
      rw [e] at h
      cases ts with
      | nil => cases h
      | cons a as =>
        cases as with
        | nil =>
          change some a = some v at h
          have eq := Option.some.inj h
          cases eq
          exact (wire_iff _ _).mp e
        | cons b bs => cases h
  · intro h
    unfold naturalWord
    rw [(wire_iff _ _).mpr h]

inductive Signed : List Nat → Literal → Prop where
  | pos {b : Nat} {ds : List Nat} {v : Nat} :
      b≠45 → Natural (b::ds) v → Signed (b::ds) (v,true)
  | neg {ds : List Nat} {v : Nat} :
      Natural ds v → v≠0 → Signed (45::ds) (v,false)

theorem signed_sound (w : List Nat) (l : Literal)
    (h : signedWord w = some l) : Signed w l := by
  cases w with
  | nil => cases h
  | cons b ds =>
    change (if b=45 then (do
      let v ← naturalWord ds
      if v=0 then none else some (v,false))
      else (do
        let v ← naturalWord (b::ds)
        some (v,true))) = some l at h
    by_cases e : b=45
    · cases e
      rw [if_pos rfl] at h
      cases hn : naturalWord ds with
      | none =>
        rw [hn] at h
        cases h
      | some v =>
        rw [hn] at h
        change (if v=0 then none else some (v,false)) = some l at h
        by_cases z : v=0
        · rw [if_pos z] at h
          cases h
        · rw [if_neg z] at h
          have result := Signed.neg ((natural_iff ds v).mp hn) z
          cases h
          exact result
    · rw [if_neg e] at h
      cases hn : naturalWord (b::ds) with
      | none =>
        rw [hn] at h
        cases h
      | some v =>
        rw [hn] at h
        have result := Signed.pos e ((natural_iff (b::ds) v).mp hn)
        cases h
        exact result

theorem signed_complete (w : List Nat) (l : Literal)
    (h : Signed w l) : signedWord w = some l := by
  cases h with
  | @pos b ds v ne nat =>
    change (if b=45 then (do
      let k ← naturalWord ds
      if k=0 then none else some (k,false))
      else (do
        let k ← naturalWord (b::ds)
        some (k,true))) = some (v,true)
    rw [if_neg ne,(natural_iff (b::ds) v).mpr nat] <;> rfl
  | @neg ds v nat ne =>
    change (do
      let k ← naturalWord ds
      if k=0 then none else some (k,false)) = some (v,false)
    rw [(natural_iff ds v).mpr nat]
    change (if v=0 then none else some (v,false)) = some (v,false)
    rw [if_neg ne]

inductive SignedSeq : List (List Nat) → List Literal → List Literal → Prop where
  | nil (acc : List Literal) : SignedSeq [] acc acc.reverse
  | cons {w : List Nat} {ws : List (List Nat)} {l : Literal} {acc out : List Literal} :
      Signed w l → SignedSeq ws (l::acc) out → SignedSeq (w::ws) acc out

theorem signed_words_sound (ws : List (List Nat)) (acc out : List Literal)
    (h : signedWords ws acc = some out) : SignedSeq ws acc out := by
  induction ws generalizing acc with
  | nil =>
    change some acc.reverse = some out at h
    cases h
    exact SignedSeq.nil _
  | cons w ws ih =>
    change (do
      let l ← signedWord w
      signedWords ws (l::acc)) = some out at h
    cases e : signedWord w with
    | none =>
      rw [e] at h
      cases h
    | some l =>
      rw [e] at h
      exact SignedSeq.cons (signed_sound w l e) (ih (l::acc) h)

theorem signed_words_complete (ws : List (List Nat)) (acc out : List Literal)
    (h : SignedSeq ws acc out) : signedWords ws acc = some out := by
  induction h with
  | nil acc => rfl
  | @cons w ws l acc out sg sub ih =>
    change (do
      let k ← signedWord w
      signedWords ws (k::acc)) = some out
    rw [signed_complete w l sg]
    exact ih

def Numbers (ws : List (List Nat)) (n m : Nat) : Prop :=
  ∃ a b, ws=[a,b] ∧ Natural a n ∧ Natural b m

theorem numbers_sound (ws : List (List Nat)) (n m : Nat)
    (h : headerNumbers ws = some (n,m)) : Numbers ws n m := by
  cases ws with
  | nil => cases h
  | cons a as =>
    cases as with
    | nil => cases h
    | cons b bs =>
      cases bs with
      | cons c cs => cases h
      | nil =>
        change (do
          let v ← naturalWord a
          let k ← naturalWord b
          some (v,k)) = some (n,m) at h
        cases ha : naturalWord a with
        | none =>
          rw [ha] at h
          cases h
        | some v =>
          rw [ha] at h
          cases hb : naturalWord b with
          | none =>
            rw [hb] at h
            cases h
          | some k =>
            rw [hb] at h
            have result : Numbers [a,b] v k :=
              ⟨a,b,rfl,(natural_iff a v).mp ha,(natural_iff b k).mp hb⟩
            cases h
            exact result

theorem numbers_complete (ws : List (List Nat)) (n m : Nat)
    (h : Numbers ws n m) : headerNumbers ws = some (n,m) := by
  obtain ⟨a,b,e,ha,hb⟩ := h
  rw [e]
  change (do
    let v ← naturalWord a
    let k ← naturalWord b
    some (v,k)) = some (n,m)
  rw [(natural_iff a n).mpr ha,(natural_iff b m).mpr hb] <;> rfl

def magic : List Nat := [112,32,99,110,102,32]

/-- Raw-byte grammar: first LF, fixed magic, two decimal header
fields, maximal whitespace-separated body words and signed tokens. -/
def LexMeaning (bytes : List Nat) (n m : Nat) (ts : List Literal) : Prop :=
  bytes.length ≤ byteLimit ∧
  ∃ head body rest hw bw,
    Header bytes [] head body ∧ head=magic++rest ∧
    Split rest [] [] hw ∧ Numbers hw n m ∧
    Split body [] [] bw ∧ SignedSeq bw [] ts

theorem lex_sound (bytes : List Nat) (n m : Nat) (ts : List Literal)
    (h : lexDimacs bytes = some (n,m,ts)) : LexMeaning bytes n m ts := by
  unfold lexDimacs at h
  by_cases size : bytes.length > byteLimit
  · rw [if_pos size] at h
    cases h
  · rw [if_neg size] at h
    cases he : takeHeader bytes [] with
    | none =>
      rw [he] at h
      cases h
    | some pair =>
      cases pair with
      | mk head body =>
        rw [he] at h
        cases hp : stripPrefix magic head with
        | none =>
          change (do
            let rest ← stripPrefix magic head
            let (v,k) ← headerNumbers (splitWords rest [] [])
            let ls ← signedWords (splitWords body [] []) []
            some (v,k,ls)) = some (n,m,ts) at h
          rw [hp] at h
          cases h
        | some rest =>
          change (do
            let r ← stripPrefix magic head
            let (v,k) ← headerNumbers (splitWords r [] [])
            let ls ← signedWords (splitWords body [] []) []
            some (v,k,ls)) = some (n,m,ts) at h
          rw [hp] at h
          change (do
            let (v,k) ← headerNumbers (splitWords rest [] [])
            let ls ← signedWords (splitWords body [] []) []
            some (v,k,ls)) = some (n,m,ts) at h
          cases hn : headerNumbers (splitWords rest [] []) with
          | none =>
            rw [hn] at h
            cases h
          | some nk =>
            cases nk with
            | mk v k =>
              rw [hn] at h
              change (do
                let ls ← signedWords (splitWords body [] []) []
                some (v,k,ls)) = some (n,m,ts) at h
              cases hs : signedWords (splitWords body [] []) [] with
              | none =>
                rw [hs] at h
                cases h
              | some ls =>
                rw [hs] at h
                have result : LexMeaning bytes v k ls :=
                  ⟨Nat.le_of_not_gt size,head,body,rest,splitWords rest [] [],splitWords body [] [],
                    header_sound _ _ _ _ he,prefix_sound _ _ _ hp,
                    split_sound _ _ _,numbers_sound _ _ _ hn,
                    split_sound _ _ _,signed_words_sound _ _ _ hs⟩
                cases h
                exact result

theorem lex_complete (bytes : List Nat) (n m : Nat) (ts : List Literal)
    (h : LexMeaning bytes n m ts) : lexDimacs bytes = some (n,m,ts) := by
  obtain ⟨size,head,body,rest,hw,bw,hh,hp,hs,hn,hb,ht⟩ := h
  unfold lexDimacs
  rw [if_neg (Nat.not_lt_of_ge size),header_complete _ _ _ _ hh]
  change (do
    let r ← stripPrefix magic head
    let (v,k) ← headerNumbers (splitWords r [] [])
    let ls ← signedWords (splitWords body [] []) []
    some (v,k,ls)) = some (n,m,ts)
  rw [hp,prefix_complete magic rest]
  change (do
    let (v,k) ← headerNumbers (splitWords rest [] [])
    let ls ← signedWords (splitWords body [] []) []
    some (v,k,ls)) = some (n,m,ts)
  rw [split_complete _ _ _ _ hs,numbers_complete _ _ _ hn]
  change (do
    let ls ← signedWords (splitWords body [] []) []
    some (n,m,ls)) = some (n,m,ts)
  rw [split_complete _ _ _ _ hb,signed_words_complete _ _ _ ht] <;> rfl

def RawMeaning (bytes : List Nat) (n : Nat) (f : Formula) : Prop :=
  ∃ m ts, LexMeaning bytes n m ts ∧ m≤listLimit ∧ Rows n m ts f

theorem raw_decode_iff (bytes : List Nat) (n : Nat) (f : Formula) :
    decodeDimacs bytes = some (n,f) ↔ RawMeaning bytes n f := by
  constructor
  · intro h
    obtain ⟨m,ts,he,size,rows⟩ := decode_sound bytes n f h
    exact ⟨m,ts,lex_sound bytes n m ts he,size,rows⟩
  · intro h
    obtain ⟨m,ts,he,size,rows⟩ := h
    exact decode_complete bytes n f ⟨m,ts,lex_complete bytes n m ts he,size,rows⟩

theorem raw_accepted_unsat (expected proof : List Nat)
    (h : checkDimacs expected proof = true) :
    ∃ n f, RawMeaning expected n f ∧ ¬ ∃ x : Assignment, FormulaSat f x := by
  obtain ⟨n,f,e,he,_,hc⟩ := accepted_decoded expected proof h
  exact ⟨n,f,(raw_decode_iff expected n f).mp he,
    ProctorUnifiedReplay.bound_sound n f e hc⟩

end ProctorDimacsLexical

#print axioms ProctorDimacsLexical.split_sound
#print axioms ProctorDimacsLexical.split_complete
#print axioms ProctorDimacsLexical.header_sound
#print axioms ProctorDimacsLexical.header_complete
#print axioms ProctorDimacsLexical.prefix_sound
#print axioms ProctorDimacsLexical.prefix_complete
#print axioms ProctorDimacsLexical.natural_iff
#print axioms ProctorDimacsLexical.signed_sound
#print axioms ProctorDimacsLexical.signed_complete
#print axioms ProctorDimacsLexical.signed_words_sound
#print axioms ProctorDimacsLexical.signed_words_complete
#print axioms ProctorDimacsLexical.numbers_sound
#print axioms ProctorDimacsLexical.numbers_complete
#print axioms ProctorDimacsLexical.lex_sound
#print axioms ProctorDimacsLexical.lex_complete
#print axioms ProctorDimacsLexical.raw_decode_iff
#print axioms ProctorDimacsLexical.raw_accepted_unsat
