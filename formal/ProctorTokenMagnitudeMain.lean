namespace ProctorTokenMagnitudeMain
open ProctorHallDeficiency
open ProctorSerializedTwoCNF (produce tokens check)
open ProctorPathResourceBounds (occurrences)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (n : Nat) (f : Formula) : IO Unit := do
  let l := occurrences f
  let k := 2*l+1
  let cap := max n (max 3402 (max l (max k (f.length+(f.length+k)*k))))
  match produce n f with
  | none => throw (IO.userError "no witness")
  | some w =>
    if !check n f w || (tokens w).any (fun t => t>cap) then
      throw (IO.userError "token magnitude exceeded")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f
    verify 2 (f.reverse.map List.reverse)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]]
  verify big [[(big,true)],[(1,false),(big,false)]]
  verify 0 []
  verify 0 [[]]
  IO.println "F035_TOKEN_MAGNITUDE_OK subsets=512 reversed=512 sparse=2 empty=2"
  pure 0
end ProctorTokenMagnitudeMain
def main : IO UInt32 := ProctorTokenMagnitudeMain.run
