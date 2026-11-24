/-! F034: complete bounded token encoding of proof envelopes and
converse decimal-word grammar for successful tokenization. -/
namespace ProctorEnvelopeRoundtrip
open ProctorHallDeficiency
open ProctorDataParser
open ProctorWireRoundtrip
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Proof Terminal Envelope)

private theorem append_assoc_local {α : Type} (a b c : List α) :
    (a++b)++c = a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_nil_local {α : Type} (a : List α) : a++[] = a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem reverseAux_append_local {α : Type} (a b c : List α) :
    a.reverseAux (b++c) = a.reverseAux b ++ c := by
  induction a generalizing b with
  | nil => rfl
  | cons x xs ih => exact ih (x::b)

private theorem reverse_cons_local {α : Type} (x : α) (xs : List α) :
    (x::xs).reverse = xs.reverse ++ [x] :=
  reverseAux_append_local xs [] [x]

def seq {α β γ : Type} (p : Parser α) (q : Parser β)
    (f : α → β → γ) : Parser γ := fun ts => do
  let (a,ts) ← p ts
  let (b,ts) ← q ts
  some (f a b,ts)

theorem seq_roundtrip {α β γ : Type} (p : Parser α) (q : Parser β)
    (f : α → β → γ) (a : α) (b : β) (as bs : List Nat)
    (ha : RoundTrip p a as) (hb : RoundTrip q b bs) :
    RoundTrip (seq p q f) (f a b) (as++bs) := by
  intro rest
  unfold seq
  rw [append_assoc_local, ha (bs++rest)]
  change (do
    let (v,ts) ← q (bs++rest)
    some (f a v,ts)) = some (f a b,rest)
  rw [hb rest] <;> rfl

def encRef (r : RefRow) : List Nat := encNat r.index ++ encClause r.row
def FitsRef (r : RefRow) : Prop := r.row.length ≤ listLimit

theorem ref_roundtrip (r : RefRow) (h : FitsRef r) :
    RoundTrip refToken r (encRef r) := by
  cases r with
  | mk i row =>
    intro rest
    change (do
      let (c,ts) ← clauseToken (encClause row ++ rest)
      some (RefRow.mk i c,ts)) = some (RefRow.mk i row,rest)
    rw [clause_roundtrip row h rest] <;> rfl

def encGroup (g : ProctorCapacityDeficiency.Group) : List Nat :=
  encClause g.literals ++ encNat g.cap
def FitsGroup (g : ProctorCapacityDeficiency.Group) : Prop :=
  g.literals.length ≤ listLimit

theorem group_roundtrip (g : ProctorCapacityDeficiency.Group) (h : FitsGroup g) :
    RoundTrip groupToken g (encGroup g) := by
  cases g with
  | mk vs cap =>
    intro rest
    change (do
      let (c,ts) ← clauseToken ((encClause vs ++ encNat cap) ++ rest)
      let (k,ts) ← natToken ts
      some (ProctorCapacityDeficiency.Group.mk c k,ts)) = some (ProctorCapacityDeficiency.Group.mk vs cap,rest)
    rw [append_assoc_local, clause_roundtrip vs h (encNat cap ++ rest)] <;> rfl

def encCapacity (c : Certificate) : List Nat :=
  encList encRef c.demands ++ (encList encGroup c.groups ++ encList encRef c.conflicts)
def FitsCapacity (c : Certificate) : Prop :=
  FitsList FitsRef c.demands ∧ FitsList FitsGroup c.groups ∧ FitsList FitsRef c.conflicts

theorem capacity_roundtrip (c : Certificate) (h : FitsCapacity c) :
    RoundTrip capacityToken c (encCapacity c) := by
  cases c with
  | mk ds gs rs =>
    have hd := list_roundtrip refToken encRef ds h.left.left
      (fun r hr => ref_roundtrip r (h.left.right r hr))
    have hg := list_roundtrip groupToken encGroup gs h.right.left.left
      (fun g hg => group_roundtrip g (h.right.left.right g hg))
    have hr := list_roundtrip refToken encRef rs h.right.right.left
      (fun r hr => ref_roundtrip r (h.right.right.right r hr))
    intro rest
    change (do
      let (d,ts) ← listToken refToken ((encList encRef ds ++
        (encList encGroup gs ++ encList encRef rs)) ++ rest)
      let (g,ts) ← listToken groupToken ts
      let (r,ts) ← listToken refToken ts
      some (Certificate.mk d g r,ts)) = some (Certificate.mk ds gs rs,rest)
    rw [append_assoc_local, append_assoc_local, hd]
    change (do
      let (g,ts) ← listToken groupToken (encList encGroup gs ++ (encList encRef rs ++ rest))
      let (r,ts) ← listToken refToken ts
      some (Certificate.mk ds g r,ts)) = _
    rw [hg]
    change (do
      let (r,ts) ← listToken refToken (encList encRef rs ++ rest)
      some (Certificate.mk ds gs r,ts)) = _
    rw [hr] <;> rfl

def encBlock (b : ProctorXorReplay.Block) : List Nat :=
  encList encNat b.support ++ (encBool b.rhs ++ encList encRef b.refs)
def FitsBlock (b : ProctorXorReplay.Block) : Prop :=
  b.support.length ≤ listLimit ∧ FitsList FitsRef b.refs

theorem block_roundtrip (b : ProctorXorReplay.Block) (h : FitsBlock b) :
    RoundTrip blockToken b (encBlock b) := by
  cases b with
  | mk vs rhs rs =>
    have hv := list_roundtrip natToken encNat vs h.left (fun v _ => nat_roundtrip v)
    have hr := list_roundtrip refToken encRef rs h.right.left
      (fun r hr => ref_roundtrip r (h.right.right r hr))
    intro rest
    change (do
      let (v,ts) ← listToken natToken ((encList encNat vs ++
        (encBool rhs ++ encList encRef rs)) ++ rest)
      let (b,ts) ← boolToken ts
      let (r,ts) ← listToken refToken ts
      some (ProctorXorReplay.Block.mk v b r,ts)) = some (ProctorXorReplay.Block.mk vs rhs rs,rest)
    rw [append_assoc_local, append_assoc_local, hv]
    change (do
      let (b,ts) ← boolToken (encBool rhs ++ (encList encRef rs ++ rest))
      let (r,ts) ← listToken refToken ts
      some (ProctorXorReplay.Block.mk vs b r,ts)) = _
    rw [bool_roundtrip rhs]
    change (do
      let (r,ts) ← listToken refToken (encList encRef rs ++ rest)
      some (ProctorXorReplay.Block.mk vs rhs r,ts)) = _
    rw [hr] <;> rfl

def encStep (s : Step) : List Nat :=
  s.left :: s.right :: s.pivot :: encClause s.tail
def FitsStep (s : Step) : Prop := s.tail.length ≤ listLimit

theorem step_roundtrip (s : Step) (h : FitsStep s) :
    RoundTrip stepToken s (encStep s) := by
  cases s with
  | mk a b p t =>
    intro rest
    change (do
      let (tail,ts) ← clauseToken (encClause t ++ rest)
      some (Step.mk a b p tail,ts)) = some (Step.mk a b p t,rest)
    rw [clause_roundtrip t h rest] <;> rfl

def encTerminal : Terminal → List Nat
  | .empty => [0]
  | .capacity c => 1 :: encCapacity c
  | .xor bs => 2 :: encList encBlock bs
def FitsTerminal : Terminal → Prop
  | .empty => True
  | .capacity c => FitsCapacity c
  | .xor bs => FitsList FitsBlock bs

theorem terminal_roundtrip (t : Terminal) (h : FitsTerminal t) :
    RoundTrip terminalToken t (encTerminal t) := by
  cases t with
  | empty => intro rest; rfl
  | capacity c =>
    intro rest
    change (do
      let (v,ts) ← capacityToken (encCapacity c ++ rest)
      some (Terminal.capacity v,ts)) = some (Terminal.capacity c,rest)
    rw [capacity_roundtrip c h rest] <;> rfl
  | xor bs =>
    intro rest
    change (do
      let (v,ts) ← listToken blockToken (encList encBlock bs ++ rest)
      some (Terminal.xor v,ts)) = some (Terminal.xor bs,rest)
    rw [list_roundtrip blockToken encBlock bs h.left
      (fun b hb => block_roundtrip b (h.right b hb)) rest] <;> rfl

def encBatch : Batch → List Nat := encList encStep
def FitsBatch : Batch → Prop := FitsList FitsStep

def encProof (p : Proof) : List Nat :=
  encList encBatch p.batches ++ (encBool p.augmented ++ encTerminal p.terminal)
def FitsProof (p : Proof) : Prop :=
  FitsList FitsBatch p.batches ∧ FitsTerminal p.terminal

theorem proof_roundtrip (p : Proof) (h : FitsProof p) :
    RoundTrip proofToken p (encProof p) := by
  cases p with
  | mk bs aug term =>
    have hb := list_roundtrip (listToken stepToken) encBatch bs h.left.left
      (fun batch hm => list_roundtrip stepToken encStep batch
        (h.left.right batch hm).left
        (fun s hs => step_roundtrip s ((h.left.right batch hm).right s hs)))
    intro rest
    change (do
      let (b,ts) ← listToken (listToken stepToken) ((encList encBatch bs ++
        (encBool aug ++ encTerminal term)) ++ rest)
      let (a,ts) ← boolToken ts
      let (t,ts) ← terminalToken ts
      some (Proof.mk b a t,ts)) = some (Proof.mk bs aug term,rest)
    rw [append_assoc_local, append_assoc_local, hb]
    change (do
      let (a,ts) ← boolToken (encBool aug ++ (encTerminal term ++ rest))
      let (t,ts) ← terminalToken ts
      some (Proof.mk bs a t,ts)) = _
    rw [bool_roundtrip aug]
    change (do
      let (t,ts) ← terminalToken (encTerminal term ++ rest)
      some (Proof.mk bs aug t,ts)) = _
    rw [terminal_roundtrip term h.right rest] <;> rfl

def encEnvelope (e : Envelope) : List Nat :=
  3402 :: e.variableBound :: (encFormula e.original ++ encProof e.proof)
def FitsEnvelope (e : Envelope) : Prop :=
  FitsFormula e.original ∧ FitsProof e.proof

theorem envelope_roundtrip (e : Envelope) (h : FitsEnvelope e) :
    RoundTrip envelopeToken e (encEnvelope e) := by
  cases e with
  | mk n f p =>
    intro rest
    change (do
      let (g,ts) ← formulaToken ((encFormula f ++ encProof p) ++ rest)
      let (q,ts) ← proofToken ts
      some (Envelope.mk n g q,ts)) = some (Envelope.mk n f p,rest)
    rw [append_assoc_local, formula_roundtrip f h.left]
    change (do
      let (q,ts) ← proofToken (encProof p ++ rest)
      some (Envelope.mk n f q,ts)) = _
    rw [proof_roundtrip p h.right rest] <;> rfl

theorem envelope_bytes_roundtrip (e : Envelope) (h : FitsEnvelope e)
    (bytes : List Nat) (grammar : Wire bytes (encEnvelope e))
    (bound : bytes.length ≤ byteLimit) :
    decodeEnvelope bytes = some e := by
  unfold decodeEnvelope decode
  rw [tokenize_words bytes (encEnvelope e) grammar bound]
  have ht := envelope_roundtrip e h []
  rw [append_nil_local] at ht
  change (do
    let (a,rest) ← envelopeToken (encEnvelope e)
    match rest with
    | [] => some a
    | _::_ => none) = some e
  rw [ht] <;> rfl

/-- Partial-word invariant: successful scanning either ends at an
empty boundary or completes a word, then a canonical wire suffix. -/
def ScanWitness (bytes : List Nat) (v k : Nat) (acc out : List Nat) : Prop :=
  (bytes=[] ∧ k=0 ∧ out=acc.reverse) ∨
  ∃ digits rest result suffix,
    bytes=digits++10::rest ∧ Word v k digits result ∧
    Wire rest suffix ∧ out=acc.reverse++result::suffix

theorem scan_converse (bytes : List Nat) (v k : Nat) (acc out : List Nat)
    (h : scan bytes v k acc = some out) :
    ScanWitness bytes v k acc out := by
  induction bytes generalizing v k acc out with
  | nil =>
    change (if k=0 then some acc.reverse else none) = some out at h
    by_cases e : k=0
    · rw [if_pos e] at h
      exact Or.inl ⟨rfl,e,(Option.some.inj h).symm⟩
    · rw [if_neg e] at h
      cases h
  | cons b bs ih =>
    change (if b=10 then
      (if k=0 then none else scan bs 0 0 (v::acc))
      else if 48≤b ∧ b≤57 then
        (if k≥digitLimit ∨ (k>0 ∧ v=0) then none
          else scan bs (10*v+(b-48)) (k+1) acc)
      else none) = some out at h
    by_cases sep : b=10
    · cases sep
      rw [if_pos rfl] at h
      by_cases z : k=0
      · rw [if_pos z] at h
        cases h
      · rw [if_neg z] at h
        cases ih 0 0 (v::acc) out h with
        | inl e =>
          obtain ⟨eb,_,eo⟩ := e
          cases eb
          refine Or.inr ⟨[],[],v,[],rfl,Word.done v k z,Wire.nil,?_⟩
          exact eo.trans (reverse_cons_local v acc)
        | inr e =>
          obtain ⟨ds,rest,r,suffix,eb,word,wire,eo⟩ := e
          refine Or.inr ⟨[],bs,v,r::suffix,rfl,Word.done v k z,?_,?_⟩
          · rw [eb]
            exact Wire.cons word wire
          · rw [eo,reverse_cons_local,append_assoc_local] <;> rfl
    · rw [if_neg sep] at h
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit] at h
        by_cases bad : k≥digitLimit ∨ (k>0 ∧ v=0)
        · rw [if_pos bad] at h
          cases h
        · rw [if_neg bad] at h
          cases ih (10*v+(b-48)) (k+1) acc out h with
          | inl e => exact (Nat.noConfusion e.right.left)
          | inr e =>
            obtain ⟨ds,rest,r,suffix,eb,word,wire,eo⟩ := e
            refine Or.inr ⟨b::ds,rest,r,suffix,?_,?_,wire,eo⟩
            · rw [eb] <;> rfl
            · exact Word.digit digit.left digit.right
                (Nat.lt_of_not_ge (fun he => bad (Or.inl he)))
                (fun hk hv => bad (Or.inr ⟨hk,hv⟩)) word
      · rw [if_neg digit] at h
        cases h

theorem tokenize_converse (bytes tokens : List Nat)
    (h : tokenize bytes = some tokens) :
    bytes.length ≤ byteLimit ∧ Wire bytes tokens := by
  unfold tokenize at h
  by_cases bound : bytes.length ≤ byteLimit
  · rw [if_pos bound] at h
    refine ⟨bound,?_⟩
    cases scan_converse bytes 0 0 [] tokens h with
    | inl e =>
      obtain ⟨eb,_,et⟩ := e
      cases eb
      cases et
      exact Wire.nil
    | inr e =>
      obtain ⟨ds,rest,r,suffix,eb,word,wire,et⟩ := e
      rw [eb,et]
      exact Wire.cons word wire
  · rw [if_neg bound] at h
    cases h

theorem wire_iff (bytes tokens : List Nat) :
    tokenize bytes = some tokens ↔ bytes.length ≤ byteLimit ∧ Wire bytes tokens :=
  ⟨tokenize_converse bytes tokens,
   fun h => tokenize_words bytes tokens h.right h.left⟩

end ProctorEnvelopeRoundtrip

#print axioms ProctorEnvelopeRoundtrip.seq_roundtrip
#print axioms ProctorEnvelopeRoundtrip.ref_roundtrip
#print axioms ProctorEnvelopeRoundtrip.group_roundtrip
#print axioms ProctorEnvelopeRoundtrip.capacity_roundtrip
#print axioms ProctorEnvelopeRoundtrip.block_roundtrip
#print axioms ProctorEnvelopeRoundtrip.step_roundtrip
#print axioms ProctorEnvelopeRoundtrip.terminal_roundtrip
#print axioms ProctorEnvelopeRoundtrip.proof_roundtrip
#print axioms ProctorEnvelopeRoundtrip.envelope_roundtrip
#print axioms ProctorEnvelopeRoundtrip.envelope_bytes_roundtrip
#print axioms ProctorEnvelopeRoundtrip.scan_converse
#print axioms ProctorEnvelopeRoundtrip.tokenize_converse
#print axioms ProctorEnvelopeRoundtrip.wire_iff
