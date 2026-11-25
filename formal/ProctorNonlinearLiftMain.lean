namespace ProctorNonlinearLiftMain
open ProctorHallDeficiency
open ProctorAffineBarrier (falseProduct)
open ProctorNonlinearLift
def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(1,true),(1,false)],
   [(1,true),(1,true),(1,true)],[(2,true),(3,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)],
   [(2,true),(1,true)],[(1,true),(2,true)]]
def run : IO UInt32 := do
  for c in rows do
    for a in [false,true] do
      for b in [false,true] do
        for d in [false,true] do
          let x : Assignment := fun v => if v=1 then a else if v=2 then b else d
          if evaluate (monomial x) (expand c) != falseProduct x c then
            throw (IO.userError "expansion disagreement")
  if !(trap.all (fun c => !(evaluate pseudo (expand c)))) then
    throw (IO.userError "pseudo-moment witness")
  IO.println "F035_NONLINEAR_LIFT_OK expansion=96 pseudo=1"
  pure 0
end ProctorNonlinearLiftMain
def main : IO UInt32 := ProctorNonlinearLiftMain.run
