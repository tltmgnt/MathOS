namespace ProctorNestedParserMain
open ProctorNestedParser
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)

-- Canonical small decimal token serialization for controls only.
def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def expectedView (r : Option (Nat × ProctorHallDeficiency.Formula)) : Option (List Nat) :=
  r.map (fun (n,f) => encExpected n f)

def envelopeView (r : Option ProctorUnifiedReplay.Envelope) : Option (List Nat) :=
  r.map encEnvelope

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
    let bs := bytes ts
    if expectedView (decodeExpected bs) != expectedView (ProctorDataParser.decodeExpected bs) then
      throw (IO.userError "expected decoder mismatch")
  for ts in en do
    let bs := bytes ts
    if envelopeView (decodeEnvelope bs) != envelopeView (ProctorDataParser.decodeEnvelope bs) then
      throw (IO.userError "envelope decoder mismatch")
  for e in ex do
    for p in en do
      if checkBytes (bytes e) (bytes p) != ProctorDataParser.checkBytes (bytes e) (bytes p) then
        throw (IO.userError "checker mismatch")
  -- Positive control: an explicit empty clause and empty terminal.
  if checkBytes (bytes [3401,1,1,0]) (bytes [3402,1,1,0,0,1,0]) != true then
    throw (IO.userError "positive empty clause control failed")
  IO.println "F034_NESTED_PARSER_OK expected=8 envelope=12 checker=96 positive=1"
  pure 0
end ProctorNestedParserMain

def main : IO UInt32 := ProctorNestedParserMain.run
