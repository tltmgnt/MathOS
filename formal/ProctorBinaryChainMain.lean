namespace ProctorBinaryChainMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch shapeCheck stepCheck chainCheck)
open ProctorBinaryChain
open ProctorCheckedBinaryScanner (cap)

def rows : List Clause := [[],[(0,true)],[(1,false)],[(1,true)],[(1,true),(2,false)]]
def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def checkChain (w : Nat) (f : Formula) (bs : List Batch) : IO Unit := do
  let m := chainMeter w f bs
  if m.1 != chainCheck f bs || m.2.1>chainVisitBudget w f bs ||
      m.2.2>chainGateBudget w f bs then
    throw (IO.userError "binary chain mismatch")

def run : IO UInt32 := do
  let mut shapes : Nat := 0
  for row in rows do
    for t in rows do
      for n in List.range 4 do
        for sign in [false,true] do
          let p := (n,sign)
          let m := shapeMeter 2 p t row
          if m.1 != shapeCheck p t row || m.2>shapeBudget 2 t row then
            throw (IO.userError "binary shape mismatch")
          shapes := shapes+1
  let mut steps : Nat := 0
  for a in rows do
    for b in rows do
      let f := [a,b]
      for i in List.range 3 do
        for j in List.range 3 do
          for p in List.range 4 do
            for t in rows do
              let s : Step := ⟨i,j,p,t⟩
              let m := stepMeter 2 f s
              if m.1 != stepCheck f s || m.2.1>stepVisitBudget 2 f ||
                  m.2.2>stepGateBudget 2 f s then
                throw (IO.userError "binary step mismatch")
              steps := steps+1
  let s : Step := ⟨0,1,1,[]⟩
  let f : Formula := [[(1,true)],[(1,false)]]
  let cases' : List (List Batch) := [[],[[]],[[s]],[[s],[⟨0,0,1,[]⟩]],
    [[⟨0,2,1,[]⟩]],[[⟨0,1,2,[]⟩]],[[s,s]],[[s],[],[s]]]
  for bs in cases' do checkChain 2 f bs
  let large := 10^128-1
  let wf : Formula := [[(large,true)],[(large,false)]]
  checkChain 512 wf [[⟨0,1,large,[]⟩]]
  checkChain 512 wf [[⟨cap 512-1,1,large,[]⟩]]
  let a := bytes [3401,1,2,1,1,1,1,1,0]
  let b := bytes [3402,1,2,1,1,1,1,1,0,1,1,0,1,1,0,0,0]
  match ProctorDataParser.decodeExpected a,ProctorDataParser.decodeEnvelope b with
  | some (_,df),some e =>
    checkChain 512 df e.proof.batches
    if (chainMeter 512 df e.proof.batches).1 != true then
      throw (IO.userError "positive decoded chain failed")
  | _,_ => throw (IO.userError "decoded chain fixture rejected")
  if shapes != 200 || steps != 4500 then throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_CHAIN_OK shapes=200 steps=4500 chains=8 wide=2 decoded=1"
  pure 0
end ProctorBinaryChainMain

def main : IO UInt32 := ProctorBinaryChainMain.run
