namespace ProctorPathCompilerCompletenessMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorImplicationPathDiscovery (arcs reach compilePair tryVar)
open ProctorBinarySquareDiscovery (checked)

def chainCore (r : Nat) : Formula :=
  [[(1,false),(2,true)]] ++
  (List.range (r-1)).map (fun i => [(i+2,false),(i+3,true)]) ++
  [[(r+1,false),(1,false)],[(1,true),(r+2,true)]] ++
  (List.range (r-1)).map (fun i => [(r+i+2,false),(r+i+3,true)]) ++
  [[(2*r+1,false),(1,true)]]

def checkPair (n v : Nat) (f : Formula) (expected : Nat) : IO Unit := do
  match reach (arcs f) (v,true) (v,false),reach (arcs f) (v,false) (v,true) with
  | some ps,some qs =>
    match compilePair f v ps qs,checked n f (tryVar f (arcs f) v) with
    | some p,some q =>
      if !boundCheck n f ⟨n,f,p⟩ || !boundCheck n f ⟨n,f,q⟩ ||
          p.batches.length != expected || q.batches.length != expected ||
          ps.length+qs.length+1 != expected then
        throw (IO.userError "witness compilation mismatch")
    | _,_ => throw (IO.userError "witness compilation failed")
  | _,_ => throw (IO.userError "missing complementary paths")

def run : IO UInt32 := do
  for j in List.range 20 do
    let r := j+1
    let f := chainCore r
    checkPair (2*r+1) 1 f (2*r+3)
    checkPair (2*r+1) 1 (f.reverse.map List.reverse) (2*r+3)
  checkPair 1 1 [[(1,true)],[(1,false)]] 3
  let big := 10^128
  checkPair big big [[(big,true)],[(big,false)]] 3
  let f := chainCore 2
  match compilePair f 1 [] [(1,true)] with
  | none => pure ()
  | some _ => throw (IO.userError "empty first route accepted")
  match compilePair f 1 [(999,true)] [(1,true)] with
  | none => pure ()
  | some p =>
    if boundCheck 5 f ⟨5,f,p⟩ then
      throw (IO.userError "bad route accepted")
  IO.println "F035_PATH_COMPILER_COMPLETENESS_OK chains=20 reversed=20 units=1 sparse=1 rejection=2"
  pure 0
end ProctorPathCompilerCompletenessMain

def main : IO UInt32 := ProctorPathCompilerCompletenessMain.run
