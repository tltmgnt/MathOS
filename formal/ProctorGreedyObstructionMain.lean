namespace ProctorGreedyObstructionMain
open ProctorGreedyObstruction
def run : IO UInt32 := do
  if greedy 5 offered trap != [1,2,3,4,5] then throw (IO.userError "greedy order")
  if counts (greedy 5 offered trap) trap != [12,13,16,22,0,0] then
    throw (IO.userError "greedy counts")
  if counts alternative trap != [12,14,11,14,0,0] then
    throw (IO.userError "alternative counts")
  if peak (counts alternative trap)>=peak (counts (greedy 5 offered trap) trap) then
    throw (IO.userError "peak comparison")
  IO.println "F035_GREEDY_OBSTRUCTION_OK traces=2 comparison=1 order=1"
  pure 0
end ProctorGreedyObstructionMain
def main : IO UInt32 := ProctorGreedyObstructionMain.run
