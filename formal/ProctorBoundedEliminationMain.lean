namespace ProctorBoundedEliminationMain
open ProctorHallDeficiency
open ProctorAdaptiveElimination (eliminate)
open ProctorBoundedElimination (weight predicted run)
open ProctorGeneralBranching (decideCNF)
def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(2,true),(3,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,false),(2,true),(3,false)],[(1,false),(2,true),(3,true)],
   [(1,true),(2,false),(3,false)],[(1,true),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def check (f : Formula) : IO Unit := do
  for v in [1,2,3] do
    if weight (eliminate v f) != predicted v f then
      throw (IO.userError "size prediction")
  let expected := decideCNF 3 f
  if run 3 1000000 [1,2,3] f != expected then
    throw (IO.userError "bounded decision")
  for cap in [0,4,16,64] do
    match run 3 cap [1,2,3] f with
    | none => pure ()
    | some b =>
      if some b != expected then throw (IO.userError "unsound bounded decision")
def main : IO UInt32 := do
  for f in subsets rows do check f
  let f : Formula := [[(1,true),(2,true),(3,true)],[(1,false),(2,true),(3,true)]]
  if (run 3 0 [1,2,3] f).isSome then throw (IO.userError "zero budget")
  if (run 3 1000000 [] f).isSome then throw (IO.userError "incomplete schedule")
  IO.println "F035_BOUNDED_ELIMINATION_OK formulas=4096 predictions=12288 decisions=20480 rejection=2"
  pure 0
end ProctorBoundedEliminationMain
def main : IO UInt32 := ProctorBoundedEliminationMain.main
