namespace ProctorBinaryProofRangeMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch)
open ProctorCapacityReplay (RefRow)
open ProctorUnifiedReplay (Proof Terminal validProof)
open ProctorBinaryProofRange
open ProctorCheckedBinaryScanner (cap)

def rows : List Clause := [[],[(0,true)],[(1,true)],[(2,false)],[(3,true)],
  [(1,true),(2,false)]]

def checkProof (w n : Nat) (p : Proof) : IO Unit := do
  let r := proofRange w n p
  if r.1 != validProof n p || r.2>proofBudget w p then
    throw (IO.userError "proof range projection or bound mismatch")

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def run : IO UInt32 := do
  let mut steps : Nat := 0
  for n in List.range 4 do
    for pivot in List.range 4 do
      for row in rows do
        let s : Step := ⟨0,1,pivot,row⟩
        checkProof 2 n ⟨[[s]],false,.empty⟩
        steps := steps+1
  let mut terminals : Nat := 0
  for n in List.range 4 do
    for a in rows do
      for b in rows do
        let t : Terminal := .capacity ⟨[⟨0,a⟩],[⟨b,1⟩],[⟨1,b⟩]⟩
        checkProof 2 n ⟨[],true,t⟩
        let x : Terminal := .xor [⟨a.map Prod.fst,true,[⟨0,b⟩]⟩]
        checkProof 2 n ⟨[],false,x⟩
        terminals := terminals+2
  let mut mixed : Nat := 0
  for n in List.range 4 do
    for a in rows do
      for b in rows do
        let s : Step := ⟨0,1,1,a⟩
        let t : Terminal := .xor [⟨[1,2],false,[⟨0,b⟩]⟩]
        checkProof 2 n ⟨[[s],[],[s]],false,t⟩
        mixed := mixed+1
  let v := cap 512-1
  for n in [v-1,v] do
    checkProof 512 n ⟨[[⟨0,1,v,[(v,false)]⟩]],false,
      .xor [⟨[v],true,[⟨0,[(v,true)]⟩]⟩]⟩
  let ex : List (List Nat) := [[],[3401,1,1,0],[3401,2,1,1,2,1],
    [3401,1,2,1,1,1,1,1,0]]
  let en : List (List Nat) := [[],[3402,1,1,0,0,1,0],
    [3402,1,1,0,0,1,0,9],[3402,2,1,1,2,1,0,0,0],
    [3402,1,2,1,1,1,1,1,0,1,1,0,1,1,0,0,0]]
  for a in ex do
    for b in en do
      if checkBytes (bytes a) (bytes b) != ProctorDataParser.checkBytes (bytes a) (bytes b) then
        throw (IO.userError "decoded proof-range checker mismatch")
  if checkBytes (bytes [3401,1,1,0]) (bytes [3402,1,1,0,0,1,0]) != true then
    throw (IO.userError "positive empty-clause fixture rejected")
  if steps != 96 || terminals != 288 || mixed != 144 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_PROOF_RANGE_OK steps=96 terminals=288 mixed=144 wide=2 decoded=20 positive=1"
  pure 0
end ProctorBinaryProofRangeMain

def main : IO UInt32 := ProctorBinaryProofRangeMain.run
