namespace ProctorGeneralBranchingMain
open ProctorHallDeficiency
open ProctorGeneralBranching (decideCNF branch leafCalls restrict)
open ProctorOrdinaryCompleteness (variables)
def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(2,true),(3,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,false),(2,true),(3,false)],[(1,false),(2,true),(3,true)],
   [(1,true),(2,false),(3,false)],[(1,true),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def sat3 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any (fun b =>
    [false,true].any (fun c => eval f (fun v => if v=1 then a else if v=2 then b else c))))
def verify (f : Formula) : IO Unit := do
  if decideCNF 3 f != some (sat3 f) then throw (IO.userError "general decision disagrees")
  if leafCalls 3 (variables f) f > 2^(variables f).length then throw (IO.userError "leaf bound")
def run : IO UInt32 := do
  for f in subsets rows do
    verify f
  let big := 10^128
  let f : Formula := [[(big,true),(1,true),(2,true)],[(big,false)],[(1,false)],[(2,false)]]
  if decideCNF big f != some false then throw (IO.userError "sparse unsat")
  if decideCNF big [[(big,true),(1,true),(2,true)]] != some true then throw (IO.userError "sparse sat")
  IO.println "F035_GENERAL_BRANCHING_OK subsets=4096 sparse=2"
  pure 0
end ProctorGeneralBranchingMain
def main : IO UInt32 := ProctorGeneralBranchingMain.run
