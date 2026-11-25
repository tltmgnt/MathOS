namespace ProctorTotalTwoCNFMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorTotalTwoCNF (solve)
open ProctorPathResourceBounds (occurrences steps)
def rows : Formula := [[],[(1,true)],[(1,false)],[(2,true)],[(2,false)],
  [(1,true),(2,true)],[(1,true),(2,false)],[(1,false),(2,true)],[(1,false),(2,false)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)
def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def sat2 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any
    (fun b => eval f (fun i => if i=1 then a else b)))
def check (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match solve n f with
  | .sat x =>
    if !sat || !eval f x then throw (IO.userError "bad model")
  | .unsat p =>
    let cap := 2*occurrences f+1
    if sat || !boundCheck n f ⟨n,f,p⟩ || p.batches.length>cap ||
       steps p.batches>(f.length+cap)*cap then
      throw (IO.userError "bad bounded proof")
    if ProctorExecutableReplay.hasEmpty f && p.batches.length != 0 then
      throw (IO.userError "empty row must use zero batches")
  | _ => throw (IO.userError "unexpected result")
def run : IO UInt32 := do
  for f in subsets rows do
    check 2 f (sat2 f)
    check 2 (f.reverse.map List.reverse) (sat2 f)
  check 0 [] true
  check 0 [[]] false
  check 0 [[],[]] false
  let big := 10^128
  check big [[(big,true)],[(big,false)]] false
  check big [[(big,false),(1,true)],[(big,true)]] true
  match solve 2 [[(0,true)]] with
  | .invalid => pure ()
  | _ => throw (IO.userError "zero identifier")
  match solve 2 [[(3,true)]] with
  | .invalid => pure ()
  | _ => throw (IO.userError "out-of-range identifier")
  match solve 3 [[(1,true),(2,true),(3,true)]] with
  | .unsupported => pure ()
  | _ => throw (IO.userError "wide row accepted")
  match solve 3 [[],[(1,true),(2,true),(3,true)]] with
  | .unsupported => pure ()
  | _ => throw (IO.userError "wide row with empty clause")
  IO.println "F035_TOTAL_TWO_CNF_OK subsets=512 reversed=512 zeroBound=3 sparse=2 rejected=4"
  pure 0
end ProctorTotalTwoCNFMain
def main : IO UInt32 := ProctorTotalTwoCNFMain.run
