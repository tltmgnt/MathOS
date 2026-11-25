namespace ProctorComponentFactorizationMain
open ProctorHallDeficiency
open ProctorComponentFactorization (disjointCheck)
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def sat4 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any (fun b =>
    [false,true].any (fun c => [false,true].any (fun d =>
      eval f (fun v => if v=1 then a else if v=2 then b else if v=3 then c else d)))))
def rows (a b : Nat) : Formula :=
  [[],[(a,true)],[(a,false)],[(b,true)],[(b,false)],[(a,true),(b,false)]]
def run : IO UInt32 := do
  for f in subsets (rows 1 2) do
    for g in subsets (rows 3 4) do
      if !disjointCheck f g || sat4 (f++g) != (sat4 f && sat4 g) then
        throw (IO.userError "factorization")
  let f : Formula := [[(1,true)]]
  let g : Formula := [[(1,false)]]
  if disjointCheck f g || !sat4 f || !sat4 g || sat4 (f++g) then
    throw (IO.userError "overlap control")
  IO.println "F035_COMPONENT_FACTORIZATION_OK pairs=4096 overlap=1"
  pure 0
end ProctorComponentFactorizationMain
def main : IO UInt32 := ProctorComponentFactorizationMain.run
