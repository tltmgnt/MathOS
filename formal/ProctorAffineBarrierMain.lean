namespace ProctorAffineBarrierMain
open ProctorHallDeficiency
open ProctorAffineBarrier
open ProctorXorReplay (evalSupport bx)
def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(2,true),(3,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,false),(2,true),(3,false)],[(1,false),(2,true),(3,true)],
   [(1,true),(2,false),(3,false)],[(1,true),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)]]
def subsets {α : Type} : List α → List (List α)
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def assignments : List Assignment :=
  [false,true].flatMap (fun a => [false,true].flatMap (fun b =>
    [false,true].map (fun c => fun v => if v=1 then a else if v=2 then b else c)))
def run : IO UInt32 := do
  for f in subsets rows do
    for x in assignments do
      let p := f.all (fun c => !(falseProduct x c))
      let q := f.all (fun c => c.any (fun l => x l.1 == l.2))
      if p != q then throw (IO.userError "polynomial encoding")
  for vs in subsets [1,2,3] do
    for x in assignments do
      for y in assignments do
        for z in assignments do
          if evalSupport (mix x y z) vs != bx (evalSupport x vs) (bx (evalSupport y vs) (evalSupport z vs)) then
            throw (IO.userError "affine closure")
  if falseProduct (mix one two both) positiveThree != true then
    throw (IO.userError "non-affine witness")
  IO.println "F035_AFFINE_BARRIER_OK polynomial=32768 closure=4096 witness=1"
  pure 0
end ProctorAffineBarrierMain
def main : IO UInt32 := ProctorAffineBarrierMain.run
