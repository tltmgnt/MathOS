namespace ProctorAmortizedParserMain
open ProctorAmortizedParser (potential)
open ProctorParserMeterCompose (ParserMeter listMeter natMeter)
open ProctorDataParser (listToken natToken)

def check {α : Type} (p : ParserMeter α) (ts : List Nat) : IO Unit := do
  let r := p ts
  match r.1 with
  | none =>
    if r.2+2>potential ts+3 then
      throw (IO.userError "rejecting amortized contract mismatch")
  | some (_,rest) =>
    if r.2+2+potential rest>potential ts then
      throw (IO.userError "successful amortized contract mismatch")

def run : IO UInt32 := do
  let p := listMeter natMeter
  let q := listMeter p
  let mut small : Nat := 0
  for k in List.range 33 do
    for n in List.range 34 do
      let ts := k::List.replicate n 1
      check p ts
      if (p ts).1 != listToken natToken ts then
        throw (IO.userError "list result mismatch")
      small := small+1
  let nested : List (List Nat) := [[],[0],[1,0],[2,1,3,2,4,5],
    [2,1,3,2,4],[1,100001],[2,0,0,9],[100000],[100000,0],
    [2,100000,1,0],[100001],[1,100000]]
  for ts in nested do
    check q ts
    if (q ts).1 != listToken (listToken natToken) ts then
      throw (IO.userError "nested result mismatch")
  for (k,n) in [(100000,0),(100000,1),(100000,3),(99999,0),
    (99999,99999),(100000,100000),(100001,100000),(131071,0)] do
    check p (k::List.replicate n 1)
  if small != 1122 then throw (IO.userError "control count mismatch")
  IO.println "F034_AMORTIZED_PARSER_OK small=1122 nested=12 boundary=8"
  pure 0
end ProctorAmortizedParserMain

def main : IO UInt32 := ProctorAmortizedParserMain.run
