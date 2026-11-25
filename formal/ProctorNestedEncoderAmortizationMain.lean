namespace ProctorNestedEncoderAmortizationMain
open ProctorNestedEncoderAmortization
open ProctorParserMeterCompose (ParserMeter natMeter)

def check {α : Type} [BEq α] (p : ParserMeter α)
    (plain : ProctorDataParser.Parser α) (ts : List Nat) : IO Unit := do
  let r := p ts
  if r.1 != plain ts || r.2>512*ts.length+3 then
    throw (IO.userError "charged nested parser bound mismatch")
  match r.1 with
  | none =>
    if r.2+2>512*ts.length+3 then
      throw (IO.userError "charged failure potential mismatch")
  | some (_,rest) =>
    if r.2+2+512*rest.length>512*ts.length then
      throw (IO.userError "charged success potential mismatch")

def run : IO UInt32 := do
  let p := chargedList natMeter
  let q := chargedList p
  let plain := ProctorDataParser.listToken ProctorDataParser.natToken
  let nested := ProctorDataParser.listToken plain
  let mut small : Nat := 0
  for k in List.range 33 do
    for n in List.range 34 do
      check p plain (k::List.replicate n 1)
      small := small+1
  for ts in [[],[0],[1,0],[2,0,0],[2,1,9,1,8],[2,1,9,2,8],
    [2,0,100000],[100000],[100001],[1,100000],[1,100001],[1,1,9,8]] do
    check q nested ts
  for ts in [[],[100000],[100000,1],[99999,1,1],[100001],[131071],[0,9],[1,1,9]] do
    check p plain ts
  if small != 1122 then throw (IO.userError "control count mismatch")
  IO.println "F034_NESTED_ENCODER_AMORTIZATION_OK small=1122 nested=12 boundary=8"
  pure 0
end ProctorNestedEncoderAmortizationMain

def main : IO UInt32 := ProctorNestedEncoderAmortizationMain.run
