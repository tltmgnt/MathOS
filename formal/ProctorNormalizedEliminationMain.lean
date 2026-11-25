namespace ProctorNormalizedEliminationMain
open ProctorHallDeficiency
open ProctorNormalizedElimination (normalize normalizedEliminate)
open ProctorOrdinaryCompleteness (update)
open ProctorPathResourceBounds (occurrences)
def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(1,true),(1,false)],
   [(1,true),(1,true),(1,true)],[(2,true),(3,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)],
   [(2,true),(1,true)],[(1,true),(2,true)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def run : IO UInt32 := do
  for f in subsets rows do
    let g := normalize f
    if g.length>f.length || occurrences g>occurrences f then
      throw (IO.userError "normalization growth")
    for v in [1,2,3] do
      let h := normalizedEliminate v f
      for a in [false,true] do
        for b in [false,true] do
          for c in [false,true] do
            let x : Assignment := fun i => if i=1 then a else if i=2 then b else c
            if eval g x != eval f x then throw (IO.userError "normalization")
            if eval h x != (eval f (update x v false) || eval f (update x v true)) then
              throw (IO.userError "normalized elimination")
  IO.println "F035_NORMALIZED_ELIMINATION_OK formulas=4096 projections=12288 assignments=98304"
  pure 0
end ProctorNormalizedEliminationMain
def main : IO UInt32 := ProctorNormalizedEliminationMain.run
