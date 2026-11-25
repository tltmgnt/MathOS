namespace ProctorEncoderGrammarMain
open ProctorNestedEncoderAmortization (potential)
open ProctorParserMeterCompose (ParserMeter)
open ProctorEncoderGrammar (expectedMeter envelopeMeter)

def check {α : Type} (p : ParserMeter α) (ts : List Nat) : IO Unit := do
  let r := p ts
  if r.2>512*ts.length+3 then
    throw (IO.userError "grammar linear bound mismatch")
  match r.1 with
  | none =>
    if r.2+2>potential ts+3 then
      throw (IO.userError "grammar reject potential mismatch")
  | some (_,rest) =>
    if r.2+2+potential rest>potential ts then
      throw (IO.userError "grammar success potential mismatch")

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
  for ts in ex do check expectedMeter ts
  for ts in en do check envelopeMeter ts
  for k in [99999,100000,100001] do
    check expectedMeter ([3401,0,k]++List.replicate 100000 0)
  let mut short : Nat := 0
  for k in [0,1,2,99999,100000,100001] do
    for n in List.range 9 do
      check expectedMeter ([3401,0,k]++List.replicate n 0)
      check envelopeMeter ([3402,0,0,k]++List.replicate n 0)
      short := short+2
  if short != 108 then throw (IO.userError "control count mismatch")
  IO.println "F034_ENCODER_GRAMMAR_OK expected=8 envelope=12 boundary=3 short=108"
  pure 0
end ProctorEncoderGrammarMain

def main : IO UInt32 := ProctorEncoderGrammarMain.run
