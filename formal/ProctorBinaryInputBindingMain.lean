namespace ProctorBinaryInputBindingMain
open ProctorHallDeficiency
open ProctorBinaryInputBinding
open ProctorBinaryReferences (literalBudget)
open ProctorCapacityReplay (test)
open ProctorUnifiedReplay (Envelope validFormula)
open ProctorCheckedBinaryScanner (cap)

def rows : List Clause := [[],[(0,true)],[(1,false)],[(1,true),(2,false)]]
def formulas : Nat → List Formula
  | 0 => [[]]
  | k+1 => rows.flatMap (fun c => (formulas k).map (fun f => c::f))

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def run : IO UInt32 := do
  let fs := (List.range 3).flatMap formulas
  let mut pairs : Nat := 0
  let mut ranges : Nat := 0
  let mut bindings : Nat := 0
  for a in fs do
    for b in fs do
      let x := formulaEq 2 a b
      if x.1 != test (a=b) || x.2>literalBudget 2*literalCount a then
        throw (IO.userError "ordered formula equality mismatch")
      pairs := pairs+1
      let e : Envelope := ⟨2,b,⟨[],false,.empty⟩⟩
      let m := bindingMeter 2 2 a e
      if m.1 != (test (a=b) && validFormula 2 a) ||
          m.2>23+literalBudget 2*literalCount a+idBudget 2*literalCount a then
        throw (IO.userError "binding resource mismatch")
      bindings := bindings+1
    for n in List.range 4 do
      let x := formulaRange 2 n a
      if x.1 != validFormula n a || x.2>idBudget 2*literalCount a then
        throw (IO.userError "formula range mismatch")
      ranges := ranges+1
  let w := 10^128-1
  let ex : List (List Nat) := [[],[3401,1,1,0],[3401,2,1,1,2,1],
    [3401,2,1,1,0,1],[3401,w,1,1,w,0],[3401,cap 512,0]]
  let en : List (List Nat) := [[],[3402,1,1,0,0,1,0],
    [3402,2,1,0,0,1,0],[3402,2,1,1,2,1,0,0,0],
    [3402,2,1,1,2,0,0,0,0],[3402,w,1,1,w,0,0,0,0],
    [3402,1,1,0,0,1,0,9]]
  for a in ex do
    for b in en do
      if checkBytes (bytes a) (bytes b) != ProctorDataParser.checkBytes (bytes a) (bytes b) then
        throw (IO.userError "decoded binary input binding mismatch")
  if checkBytes (bytes [3401,1,1,0]) (bytes [3402,1,1,0,0,1,0]) != true then
    throw (IO.userError "positive empty clause replay rejected")
  if pairs != 441 || ranges != 84 || bindings != 441 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_INPUT_BINDING_OK pairs=441 ranges=84 bindings=441 decoded=42 positive=1"
  pure 0
end ProctorBinaryInputBindingMain

def main : IO UInt32 := ProctorBinaryInputBindingMain.run
