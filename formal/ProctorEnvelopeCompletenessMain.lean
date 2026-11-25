namespace ProctorEnvelopeCompletenessMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step hasEmpty)
open ProctorOrdinaryCompleteness (update)
open ProctorResolutionBridge (sequentialCheck sequentialFrontier compile)
open ProctorUnifiedReplay (check validFormula boundCheck Proof)
open ProctorWireRoundtrip (encExpected)
open ProctorEnvelopeRoundtrip (encEnvelope)
open ProctorUnifiedReplay (Envelope)

def bytes (ts : List Nat) : List Nat := ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def locate (p : Clause → Bool) : Formula → Nat → Option Nat
  | [],_ => none
  | c::cs,i => if p c then some i else locate p cs (i+1)

-- Executable truth-table prototype for controls; its refinement and
-- cost are not among the audited declarations. No polynomial claim.
def build (q : Nat) : List Nat → Formula → Clause → Assignment → Option (List Step × Formula)
  | [],f,path,x => do
    let i ← locate (fun c => !(c.any (fun l => x l.1 == l.2))) f 0
    some ([⟨i,i,q,path⟩],path::f)
  | v::vs,f,path,x => do
    let (left,g) ← build q vs f ((v,true)::path) (update x v false)
    let (right,h) ← build q vs g ((v,false)::path) (update x v true)
    let i ← locate (fun c => c == (v,true)::path) h 0
    let j ← locate (fun c => c == (v,false)::path) h 0
    some (left++right++[⟨i,j,v,path⟩],path::h)

def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let rs := subsets cs; rs++rs.map (fun r => c::r)

def model (f : Formula) (x : Assignment) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))

def checkCase (n : Nat) (f : Formula) (vs : List Nat) (sat : Bool) : IO Unit := do
  match build 1 vs f [] (fun _ => false) with
  | none =>
    if !sat then throw (IO.userError "finite UNSAT prototype failed")
  | some (ss,g) =>
    if sat || !sequentialCheck f ss || !hasEmpty g ||
        !(sequentialFrontier f ss == g) ||
        !check f ⟨compile 1 f ss,false,.empty⟩ then
      throw (IO.userError "finite refutation prototype mismatch")
    let p : Proof := if n=0 then ⟨[],false,.empty⟩ else ⟨compile 1 f ss,false,.empty⟩
    let e : Envelope := ⟨n,f,p⟩
    if !validFormula n f || !boundCheck n f e ||
        !ProctorUnboundedCodec.checkBytes (bytes (encExpected n f)) (bytes (encEnvelope e)) then
      throw (IO.userError "valid envelope rejected")

def run : IO UInt32 := do
  let rows : Formula := [[(1,true),(2,true)],[(1,true),(2,false)],
    [(1,false),(2,true)],[(1,false),(2,false)]]
  let mut pairs : Nat := 0
  for f in subsets rows do
    let sat := [false,true].any (fun a => [false,true].any
      (fun b => model f (fun i => if i=1 then a else b)))
    checkCase 2 f [1,2] sat
    pairs := pairs+1
  let mut singles : Nat := 0
  for f in subsets [[(1,true)],[(1,false)]] do
    checkCase 1 f [1] ([false,true].any (fun b => model f (fun _ => b)))
    singles := singles+1
  checkCase 0 [[]] [] false
  checkCase 0 [] [] true
  checkCase (10^128) [[(10^128,true)],[(10^128,false)]] [10^128] false
  let bad : Formula := [[(0,true)],[(0,false)]]
  let e : Envelope := ⟨1,bad,⟨[],false,.empty⟩⟩
  if validFormula 1 bad || boundCheck 1 bad e then throw (IO.userError "invalid zero identifier accepted")
  if pairs != 16 || singles != 4 then throw (IO.userError "control count mismatch")
  IO.println "F035_ENVELOPE_COMPLETENESS_OK pairs=16 singles=4 empty=2 sparse=1 zero=1"
  pure 0

end ProctorEnvelopeCompletenessMain

def main : IO UInt32 := ProctorEnvelopeCompletenessMain.run
