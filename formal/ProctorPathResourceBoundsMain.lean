namespace ProctorPathResourceBoundsMain
open ProctorHallDeficiency
open ProctorImplicationPathDiscovery (Arc arcs reach saturate tryVar)
open ProctorPathResourceBounds (occurrences steps triangular)
open ProctorUnifiedReplay (boundCheck)
def chain (r : Nat) : Formula :=
  [[(1,false),(2,true)]] ++
  (List.range (r-1)).map (fun i => [(i+2,false),(i+3,true)]) ++
  [[(r+1,false),(1,false)],[(1,true),(r+2,true)]] ++
  (List.range (r-1)).map (fun i => [(r+i+2,false),(r+i+3,true)]) ++
  [[(2*r+1,false),(1,true)]]
def checkCase (n v : Nat) (f : Formula) : IO Unit := do
  let es := arcs f
  let cap := 2*occurrences f+1
  for a in [(v,true),(v,false)] do
    let rs := saturate es es.length [(a,[])]
    if rs.length>es.length+1 || rs.any (fun e => e.2.length>es.length) then
      throw (IO.userError "route table bound")
  match tryVar f es v with
  | none => throw (IO.userError "missing path proof")
  | some p =>
    let b := p.batches.length
    if !boundCheck n f ⟨n,f,p⟩ || b>cap ||
       steps p.batches != f.length*b+triangular b ||
       steps p.batches>(f.length+cap)*cap then
      throw (IO.userError "certificate count bound")
def run : IO UInt32 := do
  for j in List.range 20 do
    let r := j+1
    checkCase (2*r+1) 1 (chain r)
    checkCase (2*r+1) 1 ((chain r).reverse.map List.reverse)
  let big := 10^128
  checkCase big big [[(big,true)],[(big,false)]]
  checkCase 1 1 [[(1,true)],[(1,false)],[(1,true)],[(1,false)]]
  IO.println "F035_PATH_RESOURCE_BOUNDS_OK chains=20 reversed=20 sparse=1 duplicates=1"
  pure 0
end ProctorPathResourceBoundsMain
def main : IO UInt32 := ProctorPathResourceBoundsMain.run
