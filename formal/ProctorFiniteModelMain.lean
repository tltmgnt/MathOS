namespace ProctorFiniteModelMain
open ProctorHallDeficiency
open ProctorFiniteModel (finiteModel checkModel modelTokens checkModelBytes materialize)
open ProctorOrdinaryCompleteness (variables)
open ProctorWireRoundtrip (encExpected)
def rows : Formula := [[(1,true)],[(1,false)],[(2,true)],[(2,false)],
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
  ts.flatMap (fun n => ((toString n).toList.map Char.toNat)++[10])
def check (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  let w := finiteModel f
  if w.length != (variables f).length then throw (IO.userError "materialized length")
  if checkModel f w != sat then throw (IO.userError "model classification")
  if checkModelBytes (bytes (encExpected n f)) (bytes (modelTokens w)) != sat then
    throw (IO.userError "byte model classification")
def run : IO UInt32 := do
  for f in subsets rows do
    check 2 f (sat2 f)
    check 2 (f.reverse.map List.reverse) (sat2 f)
  let big := 10^128
  check big [[(big,false),(1,true)],[(big,true)]] true
  check big [[(big,true)],[(big,false)]] false
  check 0 [] true
  check 0 [[]] false
  let f : Formula := [[(1,true)]]
  let e := bytes (encExpected 1 f)
  if checkModelBytes e (bytes (modelTokens [(1,false)])) then
    throw (IO.userError "false model accepted")
  if checkModelBytes e (bytes (modelTokens [(1,true)])++[48,10]) then
    throw (IO.userError "trailing token accepted")
  if checkModelBytes e [48] then throw (IO.userError "missing LF accepted")
  IO.println "F035_FINITE_MODEL_OK subsets=256 reversed=256 sparse=2 empty=2 rejection=3"
  pure 0
end ProctorFiniteModelMain
def main : IO UInt32 := ProctorFiniteModelMain.run
