namespace ProctorTwoCNFModelMain
open ProctorHallDeficiency
open ProctorUnifiedReplay (boundCheck)
open ProctorTwoCNFModel (discover model)

def binary : Formula := [[(1,true),(2,true)],[(1,false),(2,true)],
  [(1,true),(2,false)],[(1,false),(2,false)]]
def units : Formula := [[(1,true)],[(1,false)],[(2,true)],[(2,false)]]

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def eval (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def sat2 (f : Formula) : Bool :=
  [false,true].any (fun a => [false,true].any
    (fun b => eval f (fun i => if i=1 then a else b)))

def checkCase (n : Nat) (f : Formula) (sat : Bool) : IO Unit := do
  match discover n f with
  | none =>
    if !sat || !eval f (model f) then throw (IO.userError "model extraction failed")
  | some p =>
    if sat || !boundCheck n f ⟨n,f,p⟩ then throw (IO.userError "graph proof failed")

def chain (r : Nat) : Formula :=
  (List.range r).map (fun i => [(i+1,false),(i+2,true)])

def run : IO UInt32 := do
  for f in subsets (binary++units) do
    checkCase 2 f (sat2 f)
    checkCase 2 (f.reverse.map List.reverse) (sat2 f)
  for j in List.range 10 do
    let r := j+1
    let f := [[(1,true)]]++chain r
    checkCase (r+1) f true
    checkCase (r+1) (f++[[(r+1,false)]]) false
  let big := 10^128
  checkCase big [[(big,true)],[(big,false)]] false
  checkCase big [[(big,false),(1,true)],[(big,true)]] true
  checkCase 0 [] true
  IO.println "F035_TWO_CNF_MODEL_OK subsets=256 reversed=256 chains=20 sparse=2 emptyFormula=1"
  pure 0
end ProctorTwoCNFModelMain

def main : IO UInt32 := ProctorTwoCNFModelMain.run
