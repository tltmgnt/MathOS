namespace ProctorParserMeterComposeMain
open ProctorParserMeterCompose
open ProctorDataParser (natToken boolToken listToken listLimit)

def run : IO UInt32 := do
  let mut small : Nat := 0
  for k in List.range 17 do
    for n in List.range 18 do
      let ts := k::List.replicate n 1
      let a := listMeter natMeter ts
      let b := listMeter boolMeter ts
      if a.1 != listToken natToken ts || a.2>3*k+36 then
        throw (IO.userError "Nat list meter mismatch")
      if b.1 != listToken boolToken ts || b.2>3*k+36 then
        throw (IO.userError "Bool list meter mismatch")
      small := small+2
  let bad : List (List Nat) := [[],[1],[2,0],[1,2],[2,0,2],[0,2]]
  for ts in bad do
    let r := listMeter boolMeter ts
    if r.1 != listToken boolToken ts || r.2>listBudget 1 then
      throw (IO.userError "malformed list meter mismatch")
  for k in [listLimit-1,listLimit,listLimit+1] do
    let ts := k::List.replicate listLimit 1
    let r := listMeter natMeter ts
    if r.1 != listToken natToken ts || r.2>listBudget 1 then
      throw (IO.userError "list limit meter mismatch")
  let nested : List (List Nat) := [[0],[1,0],[2,1,3,2,4,5],
    [2,1,3,2,4],[1,100001],[2,0,0,9]]
  -- Independent explicit selected totals: includes nested work even
  -- when a child fails. Each successful 17-bit word has overhead 35.
  let totals : List Nat := [36,73,118,54,4,111]
  for (ts,want) in List.zip nested totals do
    let r := listMeter (listMeter natMeter) ts
    if r.1 != listToken (listToken natToken) ts ||
       r.2>listBudget (listBudget 1) || r.2 != want then
      throw (IO.userError s!"nested list meter mismatch {ts}: {r.2} expected {want}")
  for ts in bad do
    let r := seqMeter natMeter (fun _ => boolMeter) ts
    let plain := (do
      let (_,rest) ← natToken ts
      boolToken rest)
    if r.1 != plain || r.2>2 then
      throw (IO.userError "sequence meter mismatch")
  if small != 612 then throw (IO.userError "control count mismatch")
  IO.println "F034_PARSER_METER_COMPOSE_OK small=612 malformed=6 boundary=3 nested=6 sequence=6"
  pure 0
end ProctorParserMeterComposeMain

def main : IO UInt32 := ProctorParserMeterComposeMain.run
