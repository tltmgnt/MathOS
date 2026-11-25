namespace ProctorEndToEndBytesMain
open ProctorHallDeficiency
open ProctorEndToEndBytes (produceBytes witnessBytes)
open ProctorSerializedTwoCNF (Witness witnessToken checkBytes)
open ProctorDecimalEncoder (encode)
open ProctorWireRoundtrip (encExpected)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def sat2 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any
    (fun b => eval f (fun i => if i=1 then a else b)))
def verify (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  let expected := encode (encExpected n f)
  match produceBytes expected with
  | none => throw (IO.userError "no bytes produced")
  | some out =>
    if !checkBytes expected out then throw (IO.userError "bytes rejected")
    match ProctorUnboundedCodec.decode witnessToken out with
    | none => throw (IO.userError "bad tag payload")
    | some (.sat _) => if !sat then throw (IO.userError "false SAT")
    | some (.unsat _) => if sat then throw (IO.userError "false UNSAT")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f (sat2 f)
    verify 2 (f.reverse.map List.reverse) (sat2 f)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]] false
  verify big [[(big,true)],[(1,false),(big,false)]] true
  verify 0 [] true
  verify 0 [[]] false
  for bad in [[],[48],[48,48,10],encode [3401,1,0,0],
    encode (encExpected 1 [[(0,true)]]),
    encode (encExpected 3 [[(1,true),(2,true),(3,true)]])] do
    if (produceBytes bad).isSome then throw (IO.userError "bad input produced witness")
  IO.println "F035_END_TO_END_BYTES_OK subsets=512 reversed=512 sparse=2 empty=2 rejection=6"
  pure 0
end ProctorEndToEndBytesMain
def main : IO UInt32 := ProctorEndToEndBytesMain.run
