namespace ProctorSymbolicEliminationMain
open ProctorSymbolicElimination (words equalBits paired)
def run : IO UInt32 := do
  for k in List.range 9 do
    let xs := words k
    if xs.length != 2^k then throw (IO.userError "word count")
    for a in xs do
      for b in xs do
        if equalBits a b != decide (a=b) then throw (IO.userError "equality")
        if paired (List.zip a b) != equalBits a b then throw (IO.userError "paired order")
  IO.println "F035_SYMBOLIC_ELIMINATION_OK widths=9 pairs=87381"
  pure 0
end ProctorSymbolicEliminationMain
def main : IO UInt32 := ProctorSymbolicEliminationMain.run
