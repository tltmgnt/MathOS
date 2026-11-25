namespace ProctorGrammarMeterMain
open ProctorGrammarMeter
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

def expectedView (r : Option ((Nat × ProctorHallDeficiency.Formula) × List Nat)) :
    Option (List Nat × List Nat) :=
  r.map (fun ((n,f),rest) => (encExpected n f,rest))

def envelopeView (r : Option (ProctorUnifiedReplay.Envelope × List Nat)) :
    Option (List Nat × List Nat) :=
  r.map (fun (e,rest) => (encEnvelope e,rest))

def checkExpected (ts : List Nat) : IO Unit := do
  let r := expectedMeter ts
  if expectedView r.1 != expectedView (ProctorDataParser.expectedToken ts) ||
      r.2>expectedBudget then
    throw (IO.userError "expected grammar meter mismatch")

def checkEnvelope (ts : List Nat) : IO Unit := do
  let r := envelopeMeter ts
  if envelopeView r.1 != envelopeView (ProctorDataParser.envelopeToken ts) ||
      r.2>envelopeBudget then
    throw (IO.userError "envelope grammar meter mismatch")

def run : IO UInt32 := do
  let ex : List (List Nat) := [[],[3401,0,0],[3401,1,1,0],
    [3401,1,1,1,1,0],[3401,1,1,1,1,2],[3401,0,100001],
    [3402,0,0],[3401,0,0,9]]
  let en : List (List Nat) := [[],[3402,0,0,0,0,0],
    [3402,0,0,0,0,1,0,0,0],[3402,0,0,0,0,2,0],
    [3402,1,1,0,0,1,0],[3402,0,0,0,0,3],
    [3402,0,0,0,0,1,0,0],[3402,0,0,0,2,0],
    [3402,0,0,0,0,0,9],[3402,0,100001],
    [3402,0,0,1,1,0,0,0,0,0,0],
    [3402,0,0,0,0,2,1,1,1,0,0]]
  for ts in ex do checkExpected ts
  for ts in en do checkEnvelope ts
  for k in [99999,100000,100001] do
    checkExpected ([3401,0,k]++List.replicate 100000 0)
  if (expectedMeter [3401,0,0]).2 != 38 ||
     (envelopeMeter [3402,0,0,0,0,0]).2 != 76 then
    throw (IO.userError "empty grammar selected count mismatch")
  IO.println "F034_GRAMMAR_METER_OK expected=8 envelope=12 boundary=3 exact=2"
  pure 0
end ProctorGrammarMeterMain

def main : IO UInt32 := ProctorGrammarMeterMain.run
