namespace ProctorImplicationPathDiscoveryMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorImplicationPathDiscovery (arcs reach candidate discover)
open ProctorBinarySquareDiscovery (checked)

def binary : Formula :=
  [[(1,true),(2,true)],[(1,false),(2,true)],
   [(1,true),(2,false)],[(1,false),(2,false)]]

def units : Formula := [[(1,true)],[(1,false)],[(2,true)],[(2,false)]]

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def model (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def sat2 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any
    (fun b => model f (fun i => if i=1 then a else b)))

def checkGraph (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match checked n f (candidate f) with
  | none =>
    if !sat then throw (IO.userError "standalone graph missed UNSAT")
  | some p =>
    if sat || !boundCheck n f ⟨n,f,p⟩ then
      throw (IO.userError "standalone graph false positive")
  match discover n f with
  | none => if !sat then throw (IO.userError "fallback missed UNSAT")
  | some p =>
    if sat || !boundCheck n f ⟨n,f,p⟩ then
      throw (IO.userError "fallback false positive")

def chainCore (r : Nat) : Formula :=
  [[(1,false),(2,true)]] ++
  (List.range (r-1)).map (fun i => [(i+2,false),(i+3,true)]) ++
  [[(r+1,false),(1,false)],[(1,true),(r+2,true)]] ++
  (List.range (r-1)).map (fun i => [(r+i+2,false),(r+i+3,true)]) ++
  [[(2*r+1,false),(1,true)]]

def checkFallback (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match checked n f (candidate f) with
  | some _ => throw (IO.userError "fixture should not trigger graph")
  | none => pure ()
  match discover n f with
  | none => if !sat then throw (IO.userError "fallback missed UNSAT")
  | some p =>
    if sat || !boundCheck n f ⟨n,f,p⟩ then
      throw (IO.userError "fallback false positive")

def run : IO UInt32 := do
  for f in subsets (binary++units) do
    checkGraph 2 f (sat2 f)
  for f in subsets (binary.map List.reverse) do
    checkGraph 2 f (sat2 f)
  for j in List.range 20 do
    let r := j+1
    let f := chainCore r
    match checked (2*r+1) f (candidate f) with
    | none => throw (IO.userError "long implication paths missing")
    | some p =>
      if p.batches.length != 2*r+3 then
        throw (IO.userError "chain batch count mismatch")
  let big := 10^128
  let sparse : Formula := [[(1,true),(big,true)],[(1,false),(big,true)],
    [(1,true),(big,false)],[(1,false),(big,false)]]
  checkGraph big sparse false
  checkFallback 0 [[]] false
  checkFallback 0 [] true
  let mixed : Formula := [[(1,true)],[(2,true)],[(1,false),(2,false),(3,true)]]
  checkFallback 3 mixed true
  checkFallback 3 (mixed++[[(3,false)]]) false
  match checked 1 sparse (candidate sparse) with
  | some _ => throw (IO.userError "out-of-range graph accepted")
  | none => pure ()
  match checked 2 binary (candidate binary) with
  | none => throw (IO.userError "expected graph proof")
  | some p =>
    if boundCheck 2 binary.reverse ⟨2,binary,p⟩ then
      throw (IO.userError "changed formula accepted")
  IO.println "F035_IMPLICATION_PATH_DISCOVERY_OK subsets=256 reversed=16 chains=20 sparse=1 empty=2 mixed=2 rejection=2"
  pure 0
end ProctorImplicationPathDiscoveryMain

def main : IO UInt32 := ProctorImplicationPathDiscoveryMain.run
