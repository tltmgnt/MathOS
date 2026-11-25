namespace ProctorByteCheckerLedgerMain
open ProctorByteCheckerLedger
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def expectedView (r : Option (Nat × ProctorHallDeficiency.Formula)) :
    Option (List Nat) := r.map (fun (n,f) => encExpected n f)
def envelopeView (r : Option ProctorUnifiedReplay.Envelope) :
    Option (List Nat) := r.map encEnvelope

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
  for ts in ex do
    let a := bytes ts
    let r := expectedBytes a
    if expectedView r.1 != expectedView (ProctorDataParser.decodeExpected a) ||
      r.2>decodeBudget a then
      throw (IO.userError "expected byte meter mismatch")
  for ts in en do
    let b := bytes ts
    let r := envelopeBytes b
    if envelopeView r.1 != envelopeView (ProctorDataParser.decodeEnvelope b) ||
      r.2>decodeBudget b then
      throw (IO.userError "envelope byte meter mismatch")
  let mut pairs : Nat := 0
  for xs in ex do
    for ys in en do
      let a := bytes xs
      let b := bytes ys
      let r := checkMeter a b
      if r.1 != ProctorDataParser.checkBytes a b ||
        r.1 != ProctorFuelFreeDecoder.checkBytes a b || r.2>checkBudget a b then
        throw (IO.userError "byte checker meter mismatch")
      pairs := pairs+1
  let bad : List (List Nat) := [[10],[48],[48,48,10],[45,49,10],
    [49,13,10],[256,10],[49,32,10],List.replicate 129 49++[10]]
  for a in bad do
    let r := checkMeter a a
    if r.1 || (expectedBytes a).1.isSome || (envelopeBytes a).1.isSome ||
      r.2 != (expectedBytes a).2+(envelopeBytes a).2 || r.2>checkBudget a a then
      throw (IO.userError "malformed byte meter mismatch")
  if !(checkMeter (bytes [3401,1,1,0]) (bytes [3402,1,1,0,0,1,0])).1 then
    throw (IO.userError "positive UNSAT control failed")
  if pairs != 96 then throw (IO.userError "control count mismatch")
  IO.println "F034_BYTE_CHECKER_LEDGER_OK expected=8 envelope=12 pairs=96 malformed=8 positive=1"
  pure 0
end ProctorByteCheckerLedgerMain

def main : IO UInt32 := ProctorByteCheckerLedgerMain.run
