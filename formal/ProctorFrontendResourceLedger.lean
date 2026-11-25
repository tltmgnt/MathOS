/-! F034 candidate: selected front-end resource composition.
The grammar meter is an alternative instrumented parser, not a trace
of the fuel-free parser. Emission arithmetic counts abstract events.
No claim about all decoder costs or actual machine time. -/
namespace ProctorFrontendResourceLedger
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope)
open ProctorDataParser (Parser)
open ProctorParserMeterCompose (ParserMeter)

structure Resources where
  gates : Nat
  narrowVisits : Nat
  prepassVisits : Nat
  paddingVisits : Nat
  encoderEvents : Nat
  emissionEvents : Nat
  grammarEvents : Nat
  deriving Repr, DecidableEq

def Resources.add (a b : Resources) : Resources :=
  ⟨a.gates+b.gates,a.narrowVisits+b.narrowVisits,
    a.prepassVisits+b.prepassVisits,a.paddingVisits+b.paddingVisits,
    a.encoderEvents+b.encoderEvents,a.emissionEvents+b.emissionEvents,
    a.grammarEvents+b.grammarEvents⟩

def Below (a b : Resources) : Prop :=
  a.gates≤b.gates ∧ a.narrowVisits≤b.narrowVisits ∧
  a.prepassVisits≤b.prepassVisits ∧ a.paddingVisits≤b.paddingVisits ∧
  a.encoderEvents≤b.encoderEvents ∧ a.emissionEvents≤b.emissionEvents ∧
  a.grammarEvents≤b.grammarEvents

theorem add_bounds (a b c d : Resources) (ha : Below a c) (hb : Below b d) :
    Below (a.add b) (c.add d) :=
  ⟨Nat.add_le_add ha.left hb.left,
    Nat.add_le_add ha.right.left hb.right.left,
    Nat.add_le_add ha.right.right.left hb.right.right.left,
    Nat.add_le_add ha.right.right.right.left hb.right.right.right.left,
    Nat.add_le_add ha.right.right.right.right.left hb.right.right.right.right.left,
    Nat.add_le_add ha.right.right.right.right.right.left hb.right.right.right.right.right.left,
    Nat.add_le_add ha.right.right.right.right.right.right hb.right.right.right.right.right.right⟩

def budget (B : Nat) : Resources :=
  ⟨5235*B,1046*B+8,20*B,1047*B,21*B,1536*B,64*B+3⟩

-- Decode via the common tokenizer result and metered token grammar.
-- Scanner coordinates are separate conservative reservations.
def parseMeter {α : Type} (m : ParserMeter α) (bytes : List Nat) : Option α × Resources :=
  let r := ProctorScannerPaddingCompose.resources bytes
  let z := ProctorValueProjection.tokenizeEmit bytes
  let p := match z.1 with
    | none => (none,0)
    | some ts => m ts
  let a := match p.1 with
    | some (x,[]) => some x
    | _ => none
  (a,⟨r.1,r.2.1,r.2.2.1,r.2.2.2.1,r.2.2.2.2,z.2,p.2⟩)

theorem parse_value {α : Type} (m : ParserMeter α) (p : Parser α)
    (hp : ∀ ts, (m ts).1=p ts) (bytes : List Nat) :
    (parseMeter m bytes).1=ProctorDataParser.decode p bytes := by
  unfold parseMeter ProctorDataParser.decode
  dsimp only
  rw [ProctorValueProjection.tokenize_refines]
  cases e : ProctorDataParser.tokenize bytes with
  | none => rfl
  | some ts =>
    change (match (m ts).1 with
      | some (x,[]) => some x
      | _ => none) = (do
        let (a,rest) ← p ts
        match rest with | [] => some a | _::_ => none)
    rw [hp ts]
    cases p ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => cases rest <;> rfl

theorem token_length (bytes ts : List Nat)
    (h : ProctorDataParser.tokenize bytes=some ts) : ts.length≤bytes.length :=
  ProctorParserConsumption.wire_length bytes ts
    (ProctorEnvelopeRoundtrip.tokenize_converse bytes ts h).right

def grammarCharge {α : Type} (m : ParserMeter α) (bytes : List Nat) : Nat :=
  match (ProctorValueProjection.tokenizeEmit bytes).1 with
  | none => 0
  | some ts => (m ts).2

theorem grammar_bound {α : Type} (m : ParserMeter α)
    (hm : ∀ ts, (m ts).2≤64*ts.length+3) (bytes : List Nat) :
    grammarCharge m bytes≤64*bytes.length+3 := by
  unfold grammarCharge
  rw [ProctorValueProjection.tokenize_refines]
  cases h : ProctorDataParser.tokenize bytes with
  | none => exact Nat.zero_le _
  | some ts =>
    exact Nat.le_trans (hm ts) (Nat.add_le_add
      (ProctorTerminalPolynomial.mul_mono (Nat.le_refl 64) (token_length bytes ts h))
      (Nat.le_refl 3))

private theorem parse_grammar_charge {α : Type} (m : ParserMeter α)
    (bytes : List Nat) : (parseMeter m bytes).2.grammarEvents=grammarCharge m bytes := by
  unfold parseMeter grammarCharge
  dsimp only
  cases (ProctorValueProjection.tokenizeEmit bytes).1 <;> rfl

theorem parse_bounds {α : Type} (m : ParserMeter α)
    (hm : ∀ ts, (m ts).2≤64*ts.length+3) (bytes : List Nat) :
    Below (parseMeter m bytes).2 (budget bytes.length) := by
  have h := ProctorScannerPaddingCompose.resource_bounds bytes
  have hg : (parseMeter m bytes).2.grammarEvents≤(budget bytes.length).grammarEvents := by
    rw [parse_grammar_charge m bytes]
    exact grammar_bound m hm bytes
  exact ⟨h.left,h.right.left,h.right.right.left,h.right.right.right.left,
    h.right.right.right.right,ProctorValueProjection.tokenize_bound bytes,hg⟩

def expectedMeter := parseMeter ProctorGrammarMeter.expectedMeter
def envelopeMeter := parseMeter ProctorGrammarMeter.envelopeMeter

theorem expected_value (bytes : List Nat) :
    (expectedMeter bytes).1=ProctorFuelFreeDecoder.decodeExpected bytes :=
  (parse_value _ _ ProctorGrammarMeter.expected_refines bytes).trans
    (ProctorFuelFreeDecoder.expected_bytes_refines bytes).symm

theorem envelope_value (bytes : List Nat) :
    (envelopeMeter bytes).1=ProctorFuelFreeDecoder.decodeEnvelope bytes :=
  (parse_value _ _ ProctorGrammarMeter.envelope_refines bytes).trans
    (ProctorFuelFreeDecoder.envelope_bytes_refines bytes).symm

theorem expected_bounds (bytes : List Nat) :
    Below (expectedMeter bytes).2 (budget bytes.length) :=
  parse_bounds _ ProctorAmortizedGrammar.expected_bound bytes

theorem envelope_bounds (bytes : List Nat) :
    Below (envelopeMeter bytes).2 (budget bytes.length) :=
  parse_bounds _ ProctorAmortizedGrammar.envelope_bound bytes

def pairMeter (a b : List Nat) :
    (Option (Nat × Formula) × Option Envelope) × Resources :=
  let x := expectedMeter a
  let y := envelopeMeter b
  ((x.1,y.1),x.2.add y.2)

theorem pair_value (a b : List Nat) :
    (pairMeter a b).1=(ProctorFuelFreeDecoder.decodeExpected a,
      ProctorFuelFreeDecoder.decodeEnvelope b) := by
  unfold pairMeter
  dsimp only
  rw [expected_value,envelope_value]

def pairBudget (B : Nat) : Resources :=
  ⟨5235*B,1046*B+16,20*B,1047*B,21*B,1536*B,64*B+6⟩

private theorem affine_sum (k a b c : Nat) :
    (k*a+c)+(k*b+c)=k*(a+b)+(c+c) := by
  rw [Nat.mul_add]
  calc
    (k*a+c)+(k*b+c) = k*a+(c+(k*b+c)) := Nat.add_assoc _ _ _
    _ = k*a+((c+k*b)+c) := congrArg (fun n => k*a+n) (Nat.add_assoc _ _ _).symm
    _ = k*a+((k*b+c)+c) := congrArg (fun n => k*a+(n+c)) (Nat.add_comm c (k*b))
    _ = k*a+(k*b+(c+c)) := congrArg (fun n => k*a+n) (Nat.add_assoc _ _ _)
    _ = (k*a+k*b)+(c+c) := (Nat.add_assoc _ _ _).symm

theorem pair_budget_value (a b : Nat) :
    (budget a).add (budget b)=pairBudget (a+b) := by
  unfold budget Resources.add pairBudget
  dsimp only
  rw [Nat.mul_add 5235 a b,affine_sum 1046 a b 8,
    Nat.mul_add 20 a b,Nat.mul_add 1047 a b,Nat.mul_add 21 a b,
    Nat.mul_add 1536 a b,affine_sum 64 a b 3] <;> rfl

theorem pair_bounds (a b : List Nat) :
    Below (pairMeter a b).2 (pairBudget (a.length+b.length)) := by
  rw [← pair_budget_value]
  exact add_bounds _ _ _ _ (expected_bounds a) (envelope_bounds b)

end ProctorFrontendResourceLedger

#print axioms ProctorFrontendResourceLedger.add_bounds
#print axioms ProctorFrontendResourceLedger.parse_value
#print axioms ProctorFrontendResourceLedger.token_length
#print axioms ProctorFrontendResourceLedger.grammar_bound
#print axioms ProctorFrontendResourceLedger.parse_bounds
#print axioms ProctorFrontendResourceLedger.expected_value
#print axioms ProctorFrontendResourceLedger.envelope_value
#print axioms ProctorFrontendResourceLedger.expected_bounds
#print axioms ProctorFrontendResourceLedger.envelope_bounds
#print axioms ProctorFrontendResourceLedger.pair_value
#print axioms ProctorFrontendResourceLedger.pair_budget_value
#print axioms ProctorFrontendResourceLedger.pair_bounds
