namespace ProctorPolynomialWireSizeMain
open ProctorHallDeficiency
open ProctorDecimalEncoder (encode)
open ProctorEndToEndBytes (produceBytes)
open ProctorSerializedTwoCNF (checkBytes)
open ProctorWireRoundtrip (encExpected)
open ProctorPolynomialWireSize (outputBudget)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (n : Nat) (f : Formula) : IO Unit := do
  let input := encode (encExpected n f)
  match produceBytes input with
  | none => throw (IO.userError "no witness")
  | some out =>
    if !checkBytes input out || out.length>outputBudget input.length then
      throw (IO.userError "byte budget")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f
    verify 2 (f.reverse.map List.reverse)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]]
  verify big [[(big,true)],[(1,false),(big,false)]]
  verify 0 []
  verify 0 [[]]
  IO.println "F035_POLYNOMIAL_WIRE_SIZE_OK subsets=512 reversed=512 sparse=2 empty=2"
  pure 0
end ProctorPolynomialWireSizeMain
def main : IO UInt32 := ProctorPolynomialWireSizeMain.run
