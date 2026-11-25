namespace ProctorBinaryReferencesMain
open ProctorBinaryReferences
open ProctorHallDeficiency
open ProctorCapacityReplay (test RefRow refCheck)
open ProctorExecutableReplay (contains lookup)
open ProctorCheckedBinaryScanner (cap)

def run : IO UInt32 := do
  let ls : List Literal := (List.range 8).flatMap (fun n => [(n,false),(n,true)])
  let rows : List Clause := [] :: ls.map (fun l => [l])
  let mut literals : Nat := 0
  for a in ls do
    for b in ls do
      let r := literalMeter 3 a b
      if r.1 != test (a=b) || r.2>literalBudget 3 then
        throw (IO.userError "literal mismatch")
      literals := literals+1
  let mut rowCount : Nat := 0
  for a in rows do
    for b in rows do
      let r := rowMeter 3 a b
      if r.1 != test (a=b) || r.2>literalBudget 3*a.length then
        throw (IO.userError "row mismatch")
      rowCount := rowCount+1
  let mut membership : Nat := 0
  for l in ls do
    for row in rows do
      let r := containsMeter 3 l row
      if r.1 != contains l row || r.2>literalBudget 3*row.length then
        throw (IO.userError "membership mismatch")
      membership := membership+1
  let mut refs : Nat := 0
  for f in ([[],rows,rows.reverse] : List Formula) do
    for i in List.range 10 do
      for row in rows do
        let ref : RefRow := ⟨i,row⟩
        let r := refMeter 5 f ref
        let len := match lookup f i with | none => 0 | some c => c.length
        if r.1 != refCheck f ref || r.2.1>6*f.length ||
           r.2.2>literalBudget 5*len then
          throw (IO.userError "reference mismatch")
        refs := refs+1
  let big := cap 512-1
  let a : Literal := (big,true)
  let b : Literal := (big,false)
  for (x,y) in [(a,a),(a,b),(b,a),(b,b)] do
    let r := literalMeter 512 x y
    if r.1 != test (x=y) || r.2>literalBudget 512 then
      throw (IO.userError "wide literal mismatch")
  let c : Clause := [(1,true),(2,false),(1,true)]
  for d in [c,c.reverse,[(1,true),(2,true),(1,true)],[(1,true),(2,false)]] do
    let r := rowMeter 3 c d
    if r.1 != test (c=d) || r.2>literalBudget 3*c.length then
      throw (IO.userError "recursive row mismatch")
  if !(containsMeter 3 (2,false) c).1 then
    throw (IO.userError "recursive membership mismatch")
  if (literalMeter 3 (8,true) (8,true)).1 then
    throw (IO.userError "unrepresentable literal accepted")
  if literals != 256 || rowCount != 289 || membership != 272 || refs != 510 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_REFERENCES_OK literals=256 rows=289 membership=272 refs=510 wide=4 extra=6"
  pure 0
end ProctorBinaryReferencesMain

def main : IO UInt32 := ProctorBinaryReferencesMain.run
