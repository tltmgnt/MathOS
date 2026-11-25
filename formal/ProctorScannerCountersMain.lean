namespace ProctorScannerCountersMain
open ProctorScannerCounters
open ProctorDataParser (tokenize)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def words : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,58].flatMap (fun b => (words k).map (fun bs => b::bs))

def run : IO UInt32 := do
  for n in List.range 256 do
    let expected := if n<128 then some (bits (n+1) 8) else none
    if nextCount (bits n 8) != expected then
      throw (IO.userError "digit counter mismatch")
  let mut cases : Nat := 0
  for k in List.range 5 do
    for bs in words k do
      if tokenizeCounted bs != tokenize bs then
        throw (IO.userError "scanner short word mismatch")
      cases := cases+1
  let boundary := [List.replicate 127 57++[10],
    List.replicate 128 57++[10],List.replicate 129 57++[10],
    List.replicate 128 57++[10,49,10],
    List.replicate 128 57,List.replicate 129 57,
    [48,10,49,10],[48,49,10]]
  for bs in boundary do
    if tokenizeCounted bs != tokenize bs then
      throw (IO.userError "scanner digit boundary mismatch")
  if cases != 781 then throw (IO.userError "short control count mismatch")
  IO.println "F034_SCANNER_COUNTERS_OK counter=256 short=781 boundary=8"
  pure 0
end ProctorScannerCountersMain

def main : IO UInt32 := ProctorScannerCountersMain.run
