namespace ProctorWireTokenBoundsMain
open ProctorHallDeficiency
open ProctorSerializedTwoCNF (produce tokens check)
open ProctorPathResourceBounds (occurrences steps)
open ProctorWireRoundtrip (encExpected)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (n : Nat) (f : Formula) : IO Unit := do
  let l := occurrences f
  let m := f.length
  let b := 2*l+1
  if (encExpected n f).length != 2*l+m+3 then throw (IO.userError "input length")
  match produce n f with
  | none => throw (IO.userError "missing witness")
  | some w =>
    if !check n f w then throw (IO.userError "witness rejected")
    match w with
    | .sat _ =>
      if (tokens w).length != 2*l+2 then throw (IO.userError "SAT length")
    | .unsat e =>
      if (tokens w).length > 2*l+m+1+(8*((m+b)*b)+b+3)+3 then
        throw (IO.userError "UNSAT length")
      if e.proof.batches.any (fun batch => batch.any (fun s => s.tail.length>2)) then
        throw (IO.userError "wide inference")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f
    verify 2 (f.reverse.map List.reverse)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]]
  verify big [[(big,true)],[(1,false),(big,false)]]
  verify 0 []
  verify 0 [[]]
  IO.println "F035_WIRE_TOKEN_BOUNDS_OK subsets=512 reversed=512 sparse=2 empty=2"
  pure 0
end ProctorWireTokenBoundsMain
def main : IO UInt32 := ProctorWireTokenBoundsMain.run
