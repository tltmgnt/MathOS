/-! F034: zero-terminated DIMACS clause parser selected-charge meter.
Counts attempted signed-token reads, row traversal/reversal credits,
length-guard and outer reversal credits, and final remainder test.
The production parser is unchanged. -/
namespace ProctorDimacsRowMeter
open ProctorHallDeficiency
open ProctorDimacsInput (parseRow parseRows lexDimacs decodeDimacs row_sound)
open ProctorDataParser (listLimit)
open ProctorTerminalPolynomial (mul_mono)

private theorem append_assoc_local {α : Type} (a b c : List α) :
    (a++b)++c=a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_nil_local {α : Type} (a : List α) : a++[]=a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem reverseAux_append_local {α : Type} (a b c : List α) :
    a.reverseAux (b++c)=a.reverseAux b++c := by
  induction a generalizing b with
  | nil => rfl
  | cons x xs ih => exact ih (x::b)

private theorem reverse_cons_local {α : Type} (x : α) (xs : List α) :
    (x::xs).reverse=xs.reverse++[x] :=
  reverseAux_append_local xs [] [x]

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

abbrev RowResult := Clause × List Literal
abbrev Meter (α : Type) := Option α × Nat

-- The row scan charges one attempted token read, including EOF.
-- The accumulator is reversed only at a valid positive zero.
def rowAux (n : Nat) : List Literal → Clause → Nat → Meter RowResult
  | [],_,k => (none,k+1)
  | l::ls,acc,k =>
    if l.1=0 then
      if l.2 then (some (acc.reverse,ls),k+1) else (none,k+1)
    else if l.1≤n then rowAux n ls (l::acc) (k+1)
    else (none,k+1)

def prependRow (p : Clause) (r : Option RowResult) : Option RowResult :=
  match r with
  | none => none
  | some (c,rest) => some (p++c,rest)

theorem row_aux_value (n : Nat) (ts : List Literal) (acc : Clause) (k : Nat) :
    (rowAux n ts acc k).1=prependRow acc.reverse (parseRow n ts) := by
  induction ts generalizing acc k with
  | nil => rfl
  | cons l ls ih =>
    change (if l.1=0 then
      (if l.2 then (some (acc.reverse,ls),k+1) else (none,k+1))
      else if l.1≤n then rowAux n ls (l::acc) (k+1)
      else (none,k+1)).1=prependRow acc.reverse
      (if l.1=0 then (if l.2 then some ([],ls) else none)
       else if l.1≤n then (do let (c,rest) ← parseRow n ls; some (l::c,rest))
       else none)
    by_cases z : l.1=0
    · rw [if_pos z,if_pos z]
      cases l.2 with
      | false => rfl
      | true =>
        change some (acc.reverse,ls)=some (acc.reverse++[],ls)
        rw [append_nil_local]
    · rw [if_neg z,if_neg z]
      by_cases le : l.1≤n
      · rw [if_pos le,if_pos le,ih (l::acc) (k+1),reverse_cons_local]
        cases parseRow n ls with
        | none => rfl
        | some pair =>
          cases pair with
          | mk c rest =>
            change some ((acc.reverse++[l])++c,rest)=some (acc.reverse++(l::c),rest)
            rw [append_assoc_local] <;> rfl
      · rw [if_neg le,if_neg le]

def RowGood (ts : List Literal) (k : Nat) (r : Meter RowResult) : Prop :=
  match r with
  | (none,j) => j≤k+ts.length+1
  | (some (_,rest),j) => j+rest.length=k+ts.length

private theorem fail_read (k t : Nat) : k+1≤k+(t+1)+1 :=
  Nat.le_trans (Nat.add_le_add (Nat.le_refl k)
    (Nat.succ_le_succ (Nat.zero_le t))) (Nat.le_succ _)

theorem row_aux_good (n : Nat) (ts : List Literal) (acc : Clause) (k : Nat) :
    RowGood ts k (rowAux n ts acc k) := by
  induction ts generalizing acc k with
  | nil => exact Nat.le_refl _
  | cons l ls ih =>
    change RowGood (l::ls) k (if l.1=0 then
      (if l.2 then (some (acc.reverse,ls),k+1) else (none,k+1))
      else if l.1≤n then rowAux n ls (l::acc) (k+1)
      else (none,k+1))
    by_cases z : l.1=0
    · rw [if_pos z]
      cases l.2 with
      | false => exact fail_read k ls.length
      | true => exact Nat.succ_add k ls.length
    · rw [if_neg z]
      by_cases le : l.1≤n
      · rw [if_pos le]
        have h := ih (l::acc) (k+1)
        unfold RowGood at h ⊢
        cases rowAux n ls (l::acc) (k+1) with
        | mk r j =>
          cases r with
          | none =>
            change j≤(k+1)+ls.length+1 at h
            change j≤k+(ls.length+1)+1
            rw [Nat.succ_add k ls.length] at h
            exact h
          | some pair =>
            cases pair with
            | mk _ rest =>
              change j+rest.length=(k+1)+ls.length at h
              change j+rest.length=k+(ls.length+1)
              rw [Nat.succ_add k ls.length] at h
              exact h
      · rw [if_neg le]
        exact fail_read k ls.length

def rowMeter (n : Nat) (ts : List Literal) : Meter RowResult :=
  rowAux n ts [] 0

theorem row_value (n : Nat) (ts : List Literal) :
    (rowMeter n ts).1=parseRow n ts := by
  unfold rowMeter
  rw [row_aux_value]
  cases parseRow n ts with
  | none => rfl
  | some pair => cases pair <;> rfl

theorem row_good (n : Nat) (ts : List Literal) :
    RowGood ts 0 (rowMeter n ts) := row_aux_good n ts [] 0

theorem row_bound (n : Nat) (ts : List Literal) :
    (rowMeter n ts).2≤ts.length+1 := by
  have h := row_good n ts
  unfold RowGood at h
  cases e : rowMeter n ts with
  | mk r j =>
    rw [e] at h
    cases r with
    | none =>
      change j≤0+ts.length+1 at h
      rw [Nat.zero_add] at h
      exact h
    | some pair =>
      cases pair with
      | mk _ rest =>
        change j+rest.length=0+ts.length at h
        rw [Nat.zero_add] at h
        exact Nat.le_trans (Nat.le_trans (Nat.le_add_right _ _) (Nat.le_of_eq h)) (Nat.le_succ _)

theorem row_count (n : Nat) (ts : List Literal) (c : Clause) (rest : List Literal)
    (h : (rowMeter n ts).1=some (c,rest)) :
    (rowMeter n ts).2+rest.length=ts.length := by
  have hg := row_good n ts
  unfold RowGood at hg
  cases e : rowMeter n ts with
  | mk r j =>
    rw [e] at hg
    change r=some (c,rest) at h
    cases h
    change j+rest.length=0+ts.length at hg
    rw [Nat.zero_add] at hg
    exact hg

-- Three credits per attempted row read. On successful row
-- length c, exactly c+1 reads by the independent row grammar,
-- so 3(c+1) covers reads, two c-cell traversals (length and
-- reversal), one length guard and one outer reversal credit.
-- Failed rows are conservatively tripled. One final shape test.
def rowsAux (n : Nat) : Nat → List Literal → Formula → Nat → Meter Formula
  | 0,ts,acc,k =>
    match ts with
    | [] => (some acc.reverse,k+1)
    | _::_ => (none,k+1)
  | m+1,ts,acc,k =>
    let r := rowMeter n ts
    let next := k+r.2*3
    match r.1 with
    | none => (none,next)
    | some (c,rest) =>
      if c.length≤listLimit then rowsAux n m rest (c::acc) next
      else (none,next)

def prependFormula (p : Formula) (r : Option Formula) : Option Formula :=
  match r with
  | none => none
  | some f => some (p++f)

theorem rows_aux_value (n m : Nat) (ts : List Literal) (acc : Formula) (k : Nat) :
    (rowsAux n m ts acc k).1=prependFormula acc.reverse (parseRows n m ts) := by
  induction m generalizing ts acc k with
  | zero =>
    cases ts with
    | nil =>
      change some acc.reverse=some (acc.reverse++[])
      rw [append_nil_local]
    | cons _ _ => rfl
  | succ m ih =>
    change (match (rowMeter n ts).1 with
      | none => (none,k+(rowMeter n ts).2*3)
      | some (c,rest) =>
        if c.length≤listLimit then rowsAux n m rest (c::acc) (k+(rowMeter n ts).2*3)
        else (none,k+(rowMeter n ts).2*3)).1 =
      prependFormula acc.reverse (do
        let (c,rest) ← parseRow n ts
        if c.length≤listLimit then (do let f ← parseRows n m rest; some (c::f)) else none)
    rw [← row_value n ts]
    cases (rowMeter n ts).1 with
    | none => rfl
    | some pair =>
      cases pair with
      | mk c rest =>
        change (if c.length≤listLimit then
          rowsAux n m rest (c::acc) (k+(rowMeter n ts).2*3)
          else (none,k+(rowMeter n ts).2*3)).1 =
          prependFormula acc.reverse (if c.length≤listLimit then
            (do let f ← parseRows n m rest; some (c::f)) else none)
        by_cases size : c.length≤listLimit
        · rw [if_pos size,if_pos size,ih rest (c::acc) _,reverse_cons_local]
          cases parseRows n m rest with
          | none => rfl
          | some f =>
            change some ((acc.reverse++[c])++f)=some (acc.reverse++(c::f))
            rw [append_assoc_local] <;> rfl
        · rw [if_neg size,if_neg size]

def rowsUnit (T : Nat) : Nat := (T+1)*3+1

private theorem unit_mono (a b : Nat) (h : a≤b) : rowsUnit a≤rowsUnit b :=
  Nat.succ_le_succ (mul_mono (Nat.succ_le_succ h) (Nat.le_refl 3))

theorem rows_aux_bound (n m : Nat) (ts : List Literal) (acc : Formula) (k : Nat) :
    (rowsAux n m ts acc k).2≤k+rowsUnit ts.length := by
  induction m generalizing ts acc k with
  | zero =>
    cases ts with
    | nil =>
      exact Nat.add_le_add (Nat.le_refl _) (by decide : 1≤rowsUnit 0)
    | cons l ls =>
      exact Nat.add_le_add (Nat.le_refl _)
        (Nat.le_trans (by decide : 1≤rowsUnit 0) (unit_mono 0 (l::ls).length (Nat.zero_le _)))
  | succ m ih =>
    change (match (rowMeter n ts).1 with
      | none => (none,k+(rowMeter n ts).2*3)
      | some (c,rest) =>
        if c.length≤listLimit then rowsAux n m rest (c::acc) (k+(rowMeter n ts).2*3)
        else (none,k+(rowMeter n ts).2*3)).2≤k+rowsUnit ts.length
    have h := Nat.add_le_add (Nat.le_refl k)
      (Nat.le_trans (mul_mono (row_bound n ts) (Nat.le_refl 3)) (Nat.le_succ _))
    cases e : (rowMeter n ts).1 with
    | none => exact h
    | some pair =>
      cases pair with
      | mk c rest =>
        by_cases size : c.length≤listLimit
        · rw [if_pos size]
          have hc := row_count n ts c rest e
          calc
            (rowsAux n m rest (c::acc) (k+(rowMeter n ts).2*3)).2 ≤
                (k+(rowMeter n ts).2*3)+rowsUnit rest.length := ih rest (c::acc) _
            _ = k+rowsUnit ts.length := by
              unfold rowsUnit
              rw [← hc]
              have eq : ((rowMeter n ts).2+rest.length)+1 =
                  (rowMeter n ts).2+(rest.length+1) := Nat.add_assoc _ _ _
              rw [eq,add_mul_local (rowMeter n ts).2 (rest.length+1) 3]
              rw [Nat.add_assoc k ((rowMeter n ts).2*3),
                Nat.add_assoc ((rowMeter n ts).2*3)]
        · rw [if_neg size]
          exact h

def rowsMeter (n m : Nat) (ts : List Literal) : Meter Formula :=
  rowsAux n m ts [] 0

theorem rows_value (n m : Nat) (ts : List Literal) :
    (rowsMeter n m ts).1=parseRows n m ts := by
  unfold rowsMeter
  rw [rows_aux_value]
  cases parseRows n m ts <;> rfl

theorem rows_bound (n m : Nat) (ts : List Literal) :
    (rowsMeter n m ts).2≤rowsUnit ts.length := by
  have h := rows_aux_bound n m ts [] 0
  rw [Nat.zero_add] at h
  exact h

-- Byte correspondence holds even if the token-level clause parser
-- subsequently rejects. This does not count lexer work.
theorem lex_token_bound (bytes : List Nat) (n m : Nat) (ts : List Literal)
    (h : lexDimacs bytes=some (n,m,ts)) : ts.length≤bytes.length := by
  obtain ⟨_,head,body,rest,hw,bw,hh,_,_,_,hb,ht⟩ :=
    ProctorDimacsLexical.lex_sound bytes n m ts h
  have eq := ProctorDimacsSize.signed_count bw [] ts ht
  change ts.length=bw.length at eq
  have hs := ProctorDimacsSize.split_count body [] [] bw hb
  change bw.length≤body.length at hs
  rw [eq]
  exact Nat.le_trans hs (ProctorDimacsSize.header_body_count bytes [] head body hh)

-- Charge one declared-row-count guard if lexing succeeds.
-- No charge for lexing itself; no production parser is modified.
def decodeRowsMeter (bytes : List Nat) : Meter (Nat × Formula) :=
  match lexDimacs bytes with
  | none => (none,0)
  | some (n,m,ts) =>
    if m≤listLimit then
      let r := rowsMeter n m ts
      (r.1.map (fun f => (n,f)),r.2+1)
    else (none,1)

theorem decode_rows_value (bytes : List Nat) :
    (decodeRowsMeter bytes).1=decodeDimacs bytes := by
  unfold decodeRowsMeter decodeDimacs
  cases lexDimacs bytes with
  | none => rfl
  | some triple =>
    obtain ⟨n,m,ts⟩ := triple
    change (if m≤listLimit then
      ((rowsMeter n m ts).1.map (fun f => (n,f)),(rowsMeter n m ts).2+1)
      else (none,1)).1=(if m≤listLimit then
        (do let f ← parseRows n m ts; some (n,f)) else none)
    by_cases size : m≤listLimit
    · rw [if_pos size,if_pos size]
      change (rowsMeter n m ts).1.map (fun f => (n,f))=_
      rw [rows_value]
      cases parseRows n m ts <;> rfl
    · rw [if_neg size,if_neg size]

theorem decode_rows_bound (bytes : List Nat) :
    (decodeRowsMeter bytes).2≤rowsUnit bytes.length+1 := by
  unfold decodeRowsMeter
  cases e : lexDimacs bytes with
  | none => exact Nat.zero_le _
  | some triple =>
    obtain ⟨n,m,ts⟩ := triple
    change (if m≤listLimit then
      ((rowsMeter n m ts).1.map (fun f => (n,f)),(rowsMeter n m ts).2+1)
      else (none,1)).2≤rowsUnit bytes.length+1
    by_cases size : m≤listLimit
    · rw [if_pos size]
      exact Nat.succ_le_succ (Nat.le_trans (rows_bound n m ts)
        (unit_mono _ _ (lex_token_bound bytes n m ts e)))
    · rw [if_neg size]
      exact Nat.succ_le_succ (Nat.zero_le _)

end ProctorDimacsRowMeter

#print axioms ProctorDimacsRowMeter.row_aux_value
#print axioms ProctorDimacsRowMeter.row_aux_good
#print axioms ProctorDimacsRowMeter.row_value
#print axioms ProctorDimacsRowMeter.row_good
#print axioms ProctorDimacsRowMeter.row_bound
#print axioms ProctorDimacsRowMeter.row_count
#print axioms ProctorDimacsRowMeter.rows_aux_value
#print axioms ProctorDimacsRowMeter.rows_aux_bound
#print axioms ProctorDimacsRowMeter.rows_value
#print axioms ProctorDimacsRowMeter.rows_bound
#print axioms ProctorDimacsRowMeter.lex_token_bound
#print axioms ProctorDimacsRowMeter.decode_rows_value
#print axioms ProctorDimacsRowMeter.decode_rows_bound
