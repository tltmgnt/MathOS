namespace ProctorSerializedTwoCNFMain
open ProctorHallDeficiency
open ProctorSerializedTwoCNF (Witness produce tokens check checkBytes)
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
def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])
def verify (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match produce n f with
  | none => throw (IO.userError "missing witness")
  | some w =>
    match w with
    | .sat _ => if !sat then throw (IO.userError "false SAT")
    | .unsat _ => if sat then throw (IO.userError "false UNSAT")
    if !check n f w || !checkBytes (bytes (encExpected n f)) (bytes (tokens w)) then
      throw (IO.userError "witness rejected")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f (sat2 f)
    verify 2 (f.reverse.map List.reverse) (sat2 f)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]] false
  verify big [[(big,true)],[(1,false),(big,false)]] true
  verify 0 [] true
  verify 0 [[]] false
  let f : Formula := [[(1,true)]]
  let e := bytes (encExpected 1 f)
  if checkBytes e (bytes [2,0]) then throw (IO.userError "unknown tag")
  if checkBytes e (bytes (tokens (.sat [(1,false)]))) then throw (IO.userError "false model")
  if checkBytes e (bytes (tokens (.sat [(1,true)])) ++ [48,10]) then throw (IO.userError "trailing token")
  if checkBytes e (bytes (tokens (.unsat ⟨0,[[]],⟨[],false,.empty⟩⟩))) then
    throw (IO.userError "foreign envelope")
  if (produce 1 [[(0,true)]]).isSome then throw (IO.userError "invalid input")
  if (produce 3 [[(1,true),(2,true),(3,true)]]).isSome then throw (IO.userError "unsupported input")
  IO.println "F035_SERIALIZED_TWO_CNF_OK subsets=512 reversed=512 sparse=2 empty=2 rejection=6"
  pure 0
end ProctorSerializedTwoCNFMain
def main : IO UInt32 := ProctorSerializedTwoCNFMain.run
