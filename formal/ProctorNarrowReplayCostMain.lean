namespace ProctorNarrowReplayCostMain
open ProctorHallDeficiency
open ProctorNarrowReplayCost (chainMeter modelMeter)
open ProctorExecutableReplay (chainCheck)
open ProctorFiniteModel (checkModel)
open ProctorSerializedTwoCNF (produce)
open ProctorPathResourceBounds (occurrences steps)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def verify (n : Nat) (f : Formula) : IO Unit := do
  let l := occurrences f
  let k := 2*l+1
  let s := (f.length+k)*k
  let cap := f.length+s
  match produce n f with
  | none => throw (IO.userError "missing witness")
  | some (.sat rs) =>
    let a := modelMeter rs f
    if a.1 != checkModel f rs || !a.1 || a.2>l*(l+1) then
      throw (IO.userError "model meter")
  | some (.unsat e) =>
    let a := chainMeter f e.proof.batches
    if a.1 != chainCheck f e.proof.batches || !a.1 || a.2>s*(cap+cap+12) then
      throw (IO.userError "chain meter")
def run : IO UInt32 := do
  for f in subsets rows do
    verify 2 f
    verify 2 (f.reverse.map List.reverse)
  let big := 10^128
  verify big [[(big,true)],[(big,false)]]
  verify big [[(big,true)],[(1,false),(big,false)]]
  verify 0 []
  verify 0 [[]]
  let f : Formula := [[(1,true)]]
  let bad : ProctorExecutableReplay.Step := ⟨99,0,1,[]⟩
  if (chainMeter f [[bad]]).1 then throw (IO.userError "bad parent")
  if (modelMeter [(1,false)] f).1 then throw (IO.userError "bad assignment")
  IO.println "F035_NARROW_REPLAY_COST_OK subsets=512 reversed=512 sparse=2 empty=2 rejection=2"
  pure 0
end ProctorNarrowReplayCostMain
def main : IO UInt32 := ProctorNarrowReplayCostMain.run
