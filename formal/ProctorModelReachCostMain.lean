namespace ProctorModelReachCostMain
open ProctorHallDeficiency
open ProctorModelReachCost (totalCharge queryCap)
open ProctorPathResourceBounds (occurrences)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (f : Formula) (v : Nat) : IO Unit := do
  let l := occurrences f
  let q := queryCap l
  if totalCharge f v > l*(2*q)+l*(2*((2*l)*q))+2*q then
    throw (IO.userError "aggregate comparison bound")
def run : IO UInt32 := do
  for f in subsets rows do
    verify f 1
    verify (f.reverse.map List.reverse) 2
  let big := 10^128
  verify [[(big,true)],[(big,false)]] big
  verify [[(big,true)],[(1,false),(big,false)]] big
  verify [] 0
  verify [[]] 0
  IO.println "F035_MODEL_REACH_COST_OK subsets=512 reversed=512 sparse=2 empty=2"
  pure 0
end ProctorModelReachCostMain
def main : IO UInt32 := ProctorModelReachCostMain.run
