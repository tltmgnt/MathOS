/-! F035 candidate: unrestricted token roundtrip for every typed formula
and envelope. Does not assert polynomial certificate existence. -/
namespace ProctorUnboundedRoundtrip
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityDeficiency (Group)
open ProctorUnifiedReplay (Proof Terminal Envelope)
open ProctorDataParser (Parser natToken boolToken manyAux)
open ProctorUnboundedCodec (listToken literalToken clauseToken formulaToken refToken groupToken capacityToken blockToken stepToken terminalToken proofToken expectedToken envelopeToken)
open ProctorWireRoundtrip (RoundTrip encNat encBool encItems encList encLiteral encClause encFormula encExpected nat_roundtrip bool_roundtrip items_roundtrip)
open ProctorEnvelopeRoundtrip (encRef encGroup encCapacity encBlock encStep encTerminal encBatch encProof encEnvelope)

private theorem append_assoc_local {α : Type} (a b c : List α) :
    (a++b)++c = a++(b++c) := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

private theorem append_nil_local {α : Type} (a : List α) : a++[] = a := by
  induction a with
  | nil => rfl
  | cons x xs ih => exact congrArg (List.cons x) ih

theorem list_roundtrip {α : Type} (p : Parser α) (enc : α → List Nat)
    (xs : List α) (h : ∀ a ∈ xs, RoundTrip p a (enc a)) :
    RoundTrip (listToken p) xs (encList enc xs) := by
  intro rest
  change manyAux p xs.length (encItems enc xs ++ rest) [] = some (xs,rest)
  exact items_roundtrip p enc xs h rest []

theorem literal_roundtrip (l : Literal) :
    RoundTrip literalToken l (encLiteral l) := by
  intro rest
  cases l with
  | mk v b => cases b <;> rfl

theorem clause_roundtrip (c : Clause) :
    RoundTrip clauseToken c (encClause c) :=
  list_roundtrip literalToken encLiteral c (fun l _ => literal_roundtrip l)

theorem formula_roundtrip (f : Formula) :
    RoundTrip formulaToken f (encFormula f) :=
  list_roundtrip clauseToken encClause f (fun c _ => clause_roundtrip c)

theorem expected_roundtrip (n : Nat) (f : Formula) :
    RoundTrip expectedToken (n,f) (encExpected n f) := by
  intro rest
  change (do
    let (g,ts) ← formulaToken (encFormula f ++ rest)
    some ((n,g),ts)) = some ((n,f),rest)
  rw [formula_roundtrip f rest] <;> rfl

theorem ref_roundtrip (r : RefRow) :
    RoundTrip refToken r (encRef r) := by
  cases r with
  | mk i row =>
    intro rest
    change (do
      let (c,ts) ← clauseToken (encClause row ++ rest)
      some (RefRow.mk i c,ts)) = some (RefRow.mk i row,rest)
    rw [clause_roundtrip row rest] <;> rfl

theorem group_roundtrip (g : Group) :
    RoundTrip groupToken g (encGroup g) := by
  cases g with
  | mk vs cap =>
    intro rest
    change (do
      let (c,ts) ← clauseToken ((encClause vs ++ encNat cap) ++ rest)
      let (k,ts) ← natToken ts
      some (Group.mk c k,ts)) = some (Group.mk vs cap,rest)
    rw [append_assoc_local,clause_roundtrip vs (encNat cap++rest)] <;> rfl

theorem capacity_roundtrip (c : Certificate) :
    RoundTrip capacityToken c (encCapacity c) := by
  cases c with
  | mk ds gs rs =>
    have hd := list_roundtrip refToken encRef ds (fun r _ => ref_roundtrip r)
    have hg := list_roundtrip groupToken encGroup gs (fun g _ => group_roundtrip g)
    have hr := list_roundtrip refToken encRef rs (fun r _ => ref_roundtrip r)
    intro rest
    change (do
      let (d,ts) ← listToken refToken ((encList encRef ds ++
        (encList encGroup gs ++ encList encRef rs)) ++ rest)
      let (g,ts) ← listToken groupToken ts
      let (r,ts) ← listToken refToken ts
      some (Certificate.mk d g r,ts)) = some (Certificate.mk ds gs rs,rest)
    rw [append_assoc_local,append_assoc_local,hd]
    change (do
      let (g,ts) ← listToken groupToken (encList encGroup gs ++ (encList encRef rs ++ rest))
      let (r,ts) ← listToken refToken ts
      some (Certificate.mk ds g r,ts)) = _
    rw [hg]
    change (do
      let (r,ts) ← listToken refToken (encList encRef rs ++ rest)
      some (Certificate.mk ds gs r,ts)) = _
    rw [hr] <;> rfl

theorem block_roundtrip (b : ProctorXorReplay.Block) :
    RoundTrip blockToken b (encBlock b) := by
  cases b with
  | mk vs rhs rs =>
    have hv := list_roundtrip natToken encNat vs (fun v _ => nat_roundtrip v)
    have hr := list_roundtrip refToken encRef rs (fun r _ => ref_roundtrip r)
    intro rest
    change (do
      let (v,ts) ← listToken natToken ((encList encNat vs ++
        (encBool rhs ++ encList encRef rs)) ++ rest)
      let (b,ts) ← boolToken ts
      let (r,ts) ← listToken refToken ts
      some (ProctorXorReplay.Block.mk v b r,ts)) = some (ProctorXorReplay.Block.mk vs rhs rs,rest)
    rw [append_assoc_local,append_assoc_local,hv]
    change (do
      let (b,ts) ← boolToken (encBool rhs ++ (encList encRef rs ++ rest))
      let (r,ts) ← listToken refToken ts
      some (ProctorXorReplay.Block.mk vs b r,ts)) = _
    rw [bool_roundtrip rhs]
    change (do
      let (r,ts) ← listToken refToken (encList encRef rs ++ rest)
      some (ProctorXorReplay.Block.mk vs rhs r,ts)) = _
    rw [hr] <;> rfl

theorem step_roundtrip (s : Step) :
    RoundTrip stepToken s (encStep s) := by
  cases s with
  | mk a b p t =>
    intro rest
    change (do
      let (tail,ts) ← clauseToken (encClause t ++ rest)
      some (Step.mk a b p tail,ts)) = some (Step.mk a b p t,rest)
    rw [clause_roundtrip t rest] <;> rfl

theorem terminal_roundtrip (t : Terminal) :
    RoundTrip terminalToken t (encTerminal t) := by
  cases t with
  | empty => intro rest; rfl
  | capacity c =>
    intro rest
    change (do
      let (v,ts) ← capacityToken (encCapacity c ++ rest)
      some (Terminal.capacity v,ts)) = some (Terminal.capacity c,rest)
    rw [capacity_roundtrip c rest] <;> rfl
  | xor bs =>
    intro rest
    change (do
      let (v,ts) ← listToken blockToken (encList encBlock bs ++ rest)
      some (Terminal.xor v,ts)) = some (Terminal.xor bs,rest)
    rw [list_roundtrip blockToken encBlock bs (fun b _ => block_roundtrip b) rest] <;> rfl

theorem proof_roundtrip (p : Proof) :
    RoundTrip proofToken p (encProof p) := by
  cases p with
  | mk bs aug term =>
    have hb := list_roundtrip (listToken stepToken) encBatch bs
      (fun batch _ => list_roundtrip stepToken encStep batch (fun s _ => step_roundtrip s))
    intro rest
    change (do
      let (b,ts) ← listToken (listToken stepToken) ((encList encBatch bs ++
        (encBool aug ++ encTerminal term)) ++ rest)
      let (a,ts) ← boolToken ts
      let (t,ts) ← terminalToken ts
      some (Proof.mk b a t,ts)) = some (Proof.mk bs aug term,rest)
    rw [append_assoc_local,append_assoc_local,hb]
    change (do
      let (a,ts) ← boolToken (encBool aug ++ (encTerminal term ++ rest))
      let (t,ts) ← terminalToken ts
      some (Proof.mk bs a t,ts)) = _
    rw [bool_roundtrip aug]
    change (do
      let (t,ts) ← terminalToken (encTerminal term ++ rest)
      some (Proof.mk bs aug t,ts)) = _
    rw [terminal_roundtrip term rest] <;> rfl

theorem envelope_roundtrip (e : Envelope) :
    RoundTrip envelopeToken e (encEnvelope e) := by
  cases e with
  | mk n f p =>
    intro rest
    change (do
      let (g,ts) ← formulaToken ((encFormula f ++ encProof p) ++ rest)
      let (q,ts) ← proofToken ts
      some (Envelope.mk n g q,ts)) = some (Envelope.mk n f p,rest)
    rw [append_assoc_local,formula_roundtrip f]
    change (do
      let (q,ts) ← proofToken (encProof p ++ rest)
      some (Envelope.mk n f q,ts)) = _
    rw [proof_roundtrip p rest] <;> rfl

theorem decode_exact {α : Type} (p : Parser α) (a : α) (ts bytes : List Nat)
    (hr : RoundTrip p a ts) (ht : ProctorUnboundedCodec.tokenize bytes=some ts) :
    ProctorUnboundedCodec.decode p bytes=some a := by
  unfold ProctorUnboundedCodec.decode
  rw [ht]
  have h := hr []
  rw [append_nil_local] at h
  change (do
    let (x,rest) ← p ts
    match rest with | [] => some x | _::_ => none)=some a
  rw [h] <;> rfl

theorem expected_exact (n : Nat) (f : Formula) (bytes : List Nat)
    (h : ProctorUnboundedCodec.tokenize bytes=some (encExpected n f)) :
    ProctorUnboundedCodec.decodeExpected bytes=some (n,f) :=
  decode_exact _ _ _ _ (expected_roundtrip n f) h

theorem envelope_exact (e : Envelope) (bytes : List Nat)
    (h : ProctorUnboundedCodec.tokenize bytes=some (encEnvelope e)) :
    ProctorUnboundedCodec.decodeEnvelope bytes=some e :=
  decode_exact _ _ _ _ (envelope_roundtrip e) h

end ProctorUnboundedRoundtrip

#print axioms ProctorUnboundedRoundtrip.list_roundtrip
#print axioms ProctorUnboundedRoundtrip.literal_roundtrip
#print axioms ProctorUnboundedRoundtrip.clause_roundtrip
#print axioms ProctorUnboundedRoundtrip.formula_roundtrip
#print axioms ProctorUnboundedRoundtrip.expected_roundtrip
#print axioms ProctorUnboundedRoundtrip.ref_roundtrip
#print axioms ProctorUnboundedRoundtrip.group_roundtrip
#print axioms ProctorUnboundedRoundtrip.capacity_roundtrip
#print axioms ProctorUnboundedRoundtrip.block_roundtrip
#print axioms ProctorUnboundedRoundtrip.step_roundtrip
#print axioms ProctorUnboundedRoundtrip.terminal_roundtrip
#print axioms ProctorUnboundedRoundtrip.proof_roundtrip
#print axioms ProctorUnboundedRoundtrip.envelope_roundtrip
#print axioms ProctorUnboundedRoundtrip.decode_exact
#print axioms ProctorUnboundedRoundtrip.expected_exact
#print axioms ProctorUnboundedRoundtrip.envelope_exact
