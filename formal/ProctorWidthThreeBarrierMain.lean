namespace ProctorWidthThreeBarrierMain
open ProctorHallDeficiency
open ProctorWidthThreeBarrier
open ProctorImplicationPathDiscovery (arcs)
open ProctorTwoCNFModel (findConflict)
open ProctorOrdinaryCompleteness (variables)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def run : IO UInt32 := do
  let mut satCount := 0
  for a in [false,true] do
    for b in [false,true] do
      for c in [false,true] do
        let x : Assignment := fun v => if v=1 then a else if v=2 then b else c
        if eval cube x then throw (IO.userError "cube is satisfiable")
        if eval single x then satCount := satCount+1
  if satCount != 7 then throw (IO.userError "single clause control")
  if arcs cube != arcs single then throw (IO.userError "graph mismatch")
  if (findConflict cube (variables cube)).isSome then throw (IO.userError "unexpected conflict")
  if (ProctorBinaryByteSolver.produceBitsBytes
      (ProctorDecimalEncoder.encode (ProctorWireRoundtrip.encExpected 3 cube))).isSome then
    throw (IO.userError "width gate bypassed")
  IO.println "F035_WIDTH_THREE_BARRIER_OK assignments=8 single=8 graph=1 conflict=1 gate=1"
  pure 0
end ProctorWidthThreeBarrierMain
def main : IO UInt32 := ProctorWidthThreeBarrierMain.run
