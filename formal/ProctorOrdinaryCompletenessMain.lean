namespace ProctorOrdinaryCompletenessMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step hasEmpty)
open ProctorOrdinaryCompleteness (update)
open ProctorResolutionBridge (sequentialCheck sequentialFrontier compile)
open ProctorUnifiedReplay (check)

def locate (p : Clause → Bool) : Formula → Nat → Option Nat
  | [],_ => none
  | c::cs,i => if p c then some i else locate p cs (i+1)

-- Executable truth-table prototype for controls; its refinement and
-- cost are not among the audited declarations. No polynomial claim.
def build : List Nat → Formula → Clause → Assignment → Option (List Step × Formula)
  | [],f,path,x => do
    let i ← locate (fun c => !(c.any (fun l => x l.1 == l.2))) f 0
    some ([⟨i,i,0,path⟩],path::f)
  | v::vs,f,path,x => do
    let (left,g) ← build vs f ((v,true)::path) (update x v false)
    let (right,h) ← build vs g ((v,false)::path) (update x v true)
    let i ← locate (fun c => c == (v,true)::path) h 0
    let j ← locate (fun c => c == (v,false)::path) h 0
    some (left++right++[⟨i,j,v,path⟩],path::h)

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def model (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def checkCase (f : Formula) (vs : List Nat) (sat : Bool) : IO Unit := do
  match build vs f [] (fun _ => false) with
  | none =>
    if !sat then throw (IO.userError "finite UNSAT prototype failed")
  | some (ss,g) =>
    if sat || !sequentialCheck f ss || !hasEmpty g ||
        !(sequentialFrontier f ss == g) ||
        !check f ⟨compile 0 f ss,false,.empty⟩ then
      throw (IO.userError "finite refutation prototype mismatch")

def run : IO UInt32 := do
  let rows : Formula := [[(1,true),(2,true)],[(1,true),(2,false)],
    [(1,false),(2,true)],[(1,false),(2,false)]]
  let mut pairs : Nat := 0
  for f in subsets rows do
    let sat := [false,true].any (fun a => [false,true].any
      (fun b => model f (fun i => if i=1 then a else b)))
    checkCase f [1,2] sat
    pairs := pairs+1
  let mut singles : Nat := 0
  for f in subsets [[(1,true)],[(1,false)]] do
    checkCase f [1] ([false,true].any (fun b => model f (fun _ => b)))
    singles := singles+1
  checkCase [[]] [] false
  checkCase [] [] true
  checkCase [[(10^128,true)],[(10^128,false)]] [10^128] false
  checkCase [[(0,true)],[(0,false)]] [0] false
  if pairs != 16 || singles != 4 then throw (IO.userError "control count mismatch")
  IO.println "F035_ORDINARY_COMPLETENESS_OK pairs=16 singles=4 empty=2 sparse=1 zero=1"
  pure 0

end ProctorOrdinaryCompletenessMain

def main : IO UInt32 := ProctorOrdinaryCompletenessMain.run
