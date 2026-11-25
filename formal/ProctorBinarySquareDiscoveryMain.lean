namespace ProctorBinarySquareDiscoveryMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorBinarySquareDiscovery (squareProof scan checked discover)

def core (v w : Nat) : Formula :=
  [[(v,true),(w,true)],[(v,false),(w,true)],
   [(v,true),(w,false)],[(v,false),(w,false)]]

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def model (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def checkCase (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match discover n f with
  | none =>
    if !sat then throw (IO.userError "missing UNSAT certificate")
  | some p =>
    if sat || !boundCheck n f ⟨n,f,p⟩ then
      throw (IO.userError "incorrect or rejected certificate")

def checkSquare (n : Nat) (f : Formula) : IO Unit := do
  if !f.all (fun c => c.length == 2) then
    throw (IO.userError "nonbinary padding")
  match scan f f, discover n f with
  | some candidate,some p =>
    if !boundCheck n f ⟨n,f,candidate⟩ ||
       !boundCheck n f ⟨n,f,p⟩ ||
       candidate.batches.map List.length != [2,1] ||
       p.batches.map List.length != [2,1] then
      throw (IO.userError "binary-square fast path mismatch")
  | _,_ => throw (IO.userError "missing binary-square certificate")

def run : IO UInt32 := do
  for f in subsets (core 1 2) do
    checkCase 2 f ([false,true].any (fun a => [false,true].any
      (fun b => model f (fun i => if i=1 then a else b))))
  for f in subsets [[(1,true)],[(1,false)]] do
    checkCase 1 f ([false,true].any (fun b => model f (fun _ => b)))
  checkCase 0 [[]] false
  checkCase 0 [] true
  checkSquare (10^128) (core 1 (10^128))
  for k in List.range 21 do
    let padding : Formula := (List.range k).map (fun i => [(1,true),(i+3,true)])
    let f := core 1 2 ++ padding
    checkSquare (k+2) f
  let f := core 1 2
  let p := squareProof 1 2 0 1 2 3
  if !boundCheck 2 f ⟨2,f,p⟩ || boundCheck 2 f.reverse ⟨2,f,p⟩ then
    throw (IO.userError "input binding rejection failed")
  match checked 2 f (some (squareProof 1 2 999 1 2 3)) with
  | some _ => throw (IO.userError "bad reference accepted")
  | none => pure ()
  IO.println "F035_BINARY_SQUARE_DISCOVERY_OK pairs=16 singles=4 empty=2 sparse=1 padded=21 rejection=2"
  pure 0
end ProctorBinarySquareDiscoveryMain

def main : IO UInt32 := ProctorBinarySquareDiscoveryMain.run
