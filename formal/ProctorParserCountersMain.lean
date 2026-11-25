namespace ProctorParserCountersMain
open ProctorParserCounters
open ProctorDataParser (natToken boolToken listToken listLimit)

def run : IO UInt32 := do
  let mut small : Nat := 0
  for k in List.range 17 do
    for n in List.range 18 do
      let ts := k::List.replicate n 1
      if listBits natToken ts != listToken natToken ts then
        throw (IO.userError "Nat list counter mismatch")
      if listBits boolToken ts != listToken boolToken ts then
        throw (IO.userError "Bool list counter mismatch")
      small := small+2
  let bad : List (List Nat) := [[],[1],[2,0],[1,2],[2,0,2],[0,2]]
  for ts in bad do
    if listBits boolToken ts != listToken boolToken ts then
      throw (IO.userError "list rejection mismatch")
  for k in [listLimit-1,listLimit,listLimit+1] do
    let ts := k::List.replicate listLimit 1
    if listBits natToken ts != listToken natToken ts then
      throw (IO.userError "list limit mismatch")
  let nested : List (List Nat) := [[0],[1,0],[2,1,3,2,4,5],
    [2,1,3,2,4],[1,100001],[2,0,0,9]]
  for ts in nested do
    if listBits (listBits natToken) ts != listToken (listToken natToken) ts then
      throw (IO.userError "nested list counter mismatch")
  if small != 612 then throw (IO.userError "list control count mismatch")
  IO.println "F034_PARSER_COUNTERS_OK small=612 malformed=6 boundary=3 nested=6"
  pure 0
end ProctorParserCountersMain

def main : IO UInt32 := ProctorParserCountersMain.run
