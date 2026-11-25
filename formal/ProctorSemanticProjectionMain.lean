namespace ProctorSemanticProjectionMain
open ProctorHallDeficiency
open ProctorSemanticProjection (project)
open ProctorOrdinaryCompleteness (update)
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
def verify (f : Formula) (v : Nat) : IO Unit := do
  let g := project v f
  if g.any (fun c => c.any (fun l => l.1==v)) then throw (IO.userError "variable retained")
  for a in [false,true] do
    for b in [false,true] do
      for c in [false,true] do
        let x : Assignment := fun i => if i=1 then a else if i=2 then b else c
        if eval g x != (eval f (update x v false) || eval f (update x v true)) then
          throw (IO.userError "projection disagreement")
def run : IO UInt32 := do
  for f in subsets rows do
    for v in [1,2,3] do
      verify f v
  IO.println "F035_SEMANTIC_PROJECTION_OK formulas=4096 projections=12288 assignments=98304"
  pure 0
end ProctorSemanticProjectionMain
def main : IO UInt32 := ProctorSemanticProjectionMain.run
