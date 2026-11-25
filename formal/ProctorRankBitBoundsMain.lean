namespace ProctorRankBitBoundsMain
open ProctorHallDeficiency
open ProctorRankBitBounds (scoreBits value bitModel compareCharge)
open ProctorTwoCNFModel (score model)
open ProctorPathResourceBounds (occurrences)
open ProctorOrdinaryCompleteness (variables)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (f : Formula) (v : Nat) : IO Unit := do
  let width := 2*occurrences f
  let a := scoreBits f (v,true)
  let b := scoreBits f (v,false)
  if a.length != width || b.length != width ||
    value a != score f (v,true) || value b != score f (v,false) ||
    value a >= 2^width || value b >= 2^width ||
    bitModel f v != model f v || compareCharge a b != width then
    throw (IO.userError "rank bit representation disagreement")
def run : IO UInt32 := do
  for f in subsets rows do
    verify f 1
    verify (f.reverse.map List.reverse) 2
  let big := 10^128
  verify [[(big,true)],[(big,false)]] big
  verify [[(big,true)],[(1,false),(big,false)]] big
  verify [] 0
  verify [[]] 0
  IO.println "F035_RANK_BIT_BOUNDS_OK subsets=512 reversed=512 sparse=2 empty=2"
  pure 0
end ProctorRankBitBoundsMain
def main : IO UInt32 := ProctorRankBitBoundsMain.run
