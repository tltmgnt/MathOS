namespace ProctorXorResourceLedgerMain
open ProctorHallDeficiency
open ProctorXorReplay (Block)
open ProctorXorResourceLedger
open ProctorCheckedBinaryScanner (cap)

def supports : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [0,1,2,3].flatMap (fun v => (supports k).map (fun vs => v::vs))

def checkXor (w : Nat) (f : Formula) (bs : List Block) : IO Unit := do
  let m := xorMeter w f bs
  if m.1 != ProctorBinaryXor.xorBinary w f bs ||
      m.2.1>visitBudget w f bs || m.2.2>gateBudget w f bs then
    throw (IO.userError "XOR resource ledger mismatch")

def run : IO UInt32 := do
  let ss := (List.range 3).flatMap supports
  let f : Formula := [[(1,true)],[(1,false)],[]]
  let rs : List (List ProctorCapacityReplay.RefRow) :=
    [[],[⟨0,[(1,true)]⟩],[⟨1,[(1,false)]⟩],[⟨2,[]⟩],
      [⟨0,[(1,false)]⟩],[⟨3,[]⟩]]
  let mut blocks : Nat := 0
  for vs in ss do
    for rhs in [false,true] do
      for refs in rs do
        let b : Block := ⟨vs,rhs,refs⟩
        let m := blockMeter 2 f b
        if m.1 != ProctorBinaryXor.blockBinary 2 f b ||
            m.2.1>blockVisitBudget 2 f b || m.2.2>blockGateBudget 2 f b then
          throw (IO.userError "XOR block ledger mismatch")
        blocks := blocks+1
  let mut pairs : Nat := 0
  for a in ss do
    for b in ss do
      let m := combineMeter 2 a b
      if m.1 != ProctorBinaryXor.combineBinary 2 a b || m.2>combineBudget 2 a b then
        throw (IO.userError "XOR combine ledger mismatch")
      checkXor 2 f [⟨a,false,[]⟩,⟨b,true,[]⟩]
      pairs := pairs+1
  let left : Block := ⟨[1],true,[⟨0,[(1,true)]⟩]⟩
  let right : Block := ⟨[1],false,[⟨1,[(1,false)]⟩]⟩
  for bs in [[],[left],[right],[left,right],[left,left],[right,right]] do
    checkXor 2 f bs
  if (xorMeter 2 f [left,right]).1 != true then
    throw (IO.userError "positive XOR contradiction rejected")
  let oversize : Block := ⟨List.replicate 20 1,true,[⟨0,[(1,true)]⟩]⟩
  if blockMeter 2 f oversize != (false,0,0) then
    throw (IO.userError "oversized block charged pattern enumeration")
  checkXor 2 f [oversize]
  checkXor 2 f [⟨[4,5],true,[⟨4,[(4,true)]⟩]⟩]
  let v := cap 512-1
  let wf : Formula := [[(v,true)],[(v,false)]]
  let wb : List Block := [⟨[v],true,[⟨0,[(v,true)]⟩]⟩,
    ⟨[v],false,[⟨1,[(v,false)]⟩]⟩]
  checkXor 512 wf wb
  if (xorMeter 512 wf wb).1 != true then
    throw (IO.userError "wide XOR contradiction rejected")
  if blocks != 252 || pairs != 441 then throw (IO.userError "control count mismatch")
  IO.println "F034_XOR_RESOURCE_LEDGER_OK blocks=252 pairs=441 terminals=6 positive=1 guards=1 malformed=1 wide=1"
  pure 0
end ProctorXorResourceLedgerMain

def main : IO UInt32 := ProctorXorResourceLedgerMain.run
