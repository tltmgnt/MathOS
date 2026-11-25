namespace ProctorAdaptiveEliminationMain
open ProctorHallDeficiency
open ProctorAdaptiveElimination (eliminate choose estimate)
open ProctorSemanticProjection (project)
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
def run : IO UInt32 := do
  for f in subsets rows do
    let u := choose f 1 [2,3]
    for v in [1,2,3] do
      let g := eliminate v f
      let p := project v f
      if g.length != estimate v f || estimate u f > estimate v f then
        throw (IO.userError "local size bound")
      for a in [false,true] do
        for b in [false,true] do
          for c in [false,true] do
            let x : Assignment := fun i => if i=1 then a else if i=2 then b else c
            if eval g x != eval p x then throw (IO.userError "factored projection disagreement")
  IO.println "F035_ADAPTIVE_ELIMINATION_OK formulas=4096 projections=12288 assignments=98304"
  pure 0
end ProctorAdaptiveEliminationMain
def main : IO UInt32 := ProctorAdaptiveEliminationMain.run
