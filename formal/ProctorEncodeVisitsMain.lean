namespace ProctorEncodeVisitsMain
open ProctorEncodeVisits
open ProctorCheckedBinaryScanner (encode)

def check (w n : Nat) : IO Unit := do
  let r := encodeMeter w n
  if r.1 != encode w n || r.2>budget w then
    throw (IO.userError "encoder selected resource mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for w in List.range 9 do
    for n in List.range (2^w+3) do
      check w n
      small := small+1
  for n in [0,1,9,15,16,17,100000,131071,131072,2^512-1] do
    check 4 n
    check 17 n
  for (w,n,want) in [(0,0,1),(0,1,1),(1,0,2),(1,1,3),
      (1,2,3),(2,0,5),(2,3,7),(2,4,6),(4,9,19)] do
    if (encodeMeter w n).2 != want then
      throw (IO.userError "encoder exact resource mismatch")
  if small != 538 then throw (IO.userError "control count mismatch")
  IO.println "F034_ENCODE_VISITS_OK small=538 boundary=20 exact=9"
  pure 0
end ProctorEncodeVisitsMain

def main : IO UInt32 := ProctorEncodeVisitsMain.run
