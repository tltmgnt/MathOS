namespace ProctorStructuralCountersMain
open ProctorStructuralCounters
open ProctorCheckedBinaryScanner (cap)
open ProctorDataParser (digitLimit listLimit byteLimit)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def check (w n limit : Nat) : IO Unit := do
  let x := bits n w
  let l := bits limit w
  let r := bumpBelow w x l
  if n<limit then
    if r != some (bits (n+1) w) then
      throw (IO.userError "counter increment mismatch")
  else if r.isSome then
    throw (IO.userError "counter limit rejection mismatch")
  if bumpBudget x l != 5*w+5*w then
    throw (IO.userError "counter gate mismatch")

def run : IO UInt32 := do
  let mut guards : Nat := 0
  let mut increments : Nat := 0
  for w in List.range 9 do
    if w>0 then
      for n in List.range (cap w) do
        let r := increment w (bits n w)
        if n+1<cap w then
          if r != some (bits (n+1) w) then
            throw (IO.userError "checked increment mismatch")
        else if r.isSome then
          throw (IO.userError "increment overflow mismatch")
        increments := increments+1
  for w in [1,2,3,4,5] do
    for n in List.range (cap w) do
      for limit in List.range (cap w) do
        check w n limit
        guards := guards+1
  let mut boundaries : Nat := 0
  for (w,limit) in [(8,digitLimit),(17,listLimit),(20,byteLimit)] do
    for n in [0,limit-1,limit,limit+1,cap w-1] do
      check w n limit
      if bumpNatLimit w limit (bits n w) != bumpBelow w (bits n w) (bits limit w) then
        throw (IO.userError "encoded limit mismatch")
      boundaries := boundaries+1
  if guards != 1364 || increments != 510 || boundaries != 15 then
    throw (IO.userError "counter control count mismatch")
  IO.println "F034_STRUCTURAL_COUNTERS_OK increments=510 guards=1364 boundaries=15"
  pure 0
end ProctorStructuralCountersMain

def main : IO UInt32 := ProctorStructuralCountersMain.run
