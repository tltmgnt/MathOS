namespace ProctorExecutableDiscoveryMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorExecutableDiscovery (generate decide)

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def model (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def checkCase (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  if decide n f != !sat then throw (IO.userError "exhaustive decision mismatch")
  if !sat then
    match generate n f with
    | none => throw (IO.userError "missing certificate")
    | some p =>
      if !boundCheck n f ⟨n,f,p⟩ then throw (IO.userError "generated certificate rejected")

def run : IO UInt32 := do
  let rows : Formula := [[(1,true),(2,true)],[(1,true),(2,false)],
    [(1,false),(2,true)],[(1,false),(2,false)]]
  for f in subsets rows do
    checkCase 2 f ([false,true].any (fun a => [false,true].any
      (fun b => model f (fun i => if i=1 then a else b))))
  for f in subsets [[(1,true)],[(1,false)]] do
    checkCase 1 f ([false,true].any (fun b => model f (fun _ => b)))
  checkCase 0 [[]] false
  checkCase 0 [] true
  checkCase (10^128) [[(10^128,true)],[(10^128,false)]] false
  checkCase 2 [[(1,true),(1,true)],[(1,false)]] false
  checkCase 2 [[(1,true),(1,false)]] true
  IO.println "F035_EXECUTABLE_DISCOVERY_OK pairs=16 singles=4 empty=2 sparse=1 duplicates=2"
  pure 0
end ProctorExecutableDiscoveryMain

def main : IO UInt32 := ProctorExecutableDiscoveryMain.run
