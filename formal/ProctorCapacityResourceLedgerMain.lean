namespace ProctorCapacityResourceLedgerMain
open ProctorHallDeficiency
open ProctorCapacityDeficiency (Group)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorCapacityResourceLedger
open ProctorCheckedBinaryScanner (cap)

def rows : List Clause := [[],[(0,true)],[(1,true)],[(1,false)],[(2,true)],
  [(1,true),(2,true)],[(1,false),(2,false)],[(1,true),(1,true)]]

def checkCapacity (w : Nat) (f : Formula) (c : Certificate) : IO Unit := do
  let m := capacityMeter w f c
  if m.1 != ProctorBinaryCapacity.capacityBinary w f c ||
      m.2.1>visitBudget w f c || m.2.2>gateBudget w f c then
    throw (IO.userError "capacity resource ledger mismatch")

def run : IO UInt32 := do
  let f : Formula := [[(1,true)],[(2,true)],[(1,false),(2,false)]]
  let ds : List RefRow := [⟨0,[(1,true)]⟩,⟨1,[(2,true)]⟩]
  let rs : List RefRow := [⟨2,[(1,false),(2,false)]⟩]
  let good : Certificate := ⟨ds,[⟨[(1,true),(2,true)],1⟩],rs⟩
  let badRefs : List RefRow := [⟨3,[]⟩,⟨0,[(2,true)]⟩]
  let mut groups : Nat := 0
  for row in rows do
    let d := distinctMeter 2 row
    if d.1 != ProctorBinaryCapacity.distinctBinary 2 row || d.2>distinctBudget 2 row then
      throw (IO.userError "distinct ledger mismatch")
    for k in List.range 4 do
      for refs in [[],rs,badRefs] do
        let g : Group := ⟨row,k⟩
        let m := groupMeter 2 refs g
        if m.1 != ProctorBinaryCapacity.groupBinary 2 refs g ||
            m.2.1 != 0 || m.2.2>groupBudget 2 refs g then
          throw (IO.userError "group ledger mismatch")
        groups := groups+1
  let mut pairs : Nat := 0
  for a in rows do
    for b in rows do
      let demands : List RefRow := [⟨0,a⟩,⟨1,b⟩]
      for i in List.range 4 do
        for j in List.range 4 do
          let m := differentMeter 2 demands i j
          if m.1 != ProctorBinaryCapacity.differentBinary 2 demands i j ||
              m.2.1>pairVisitBudget 2 demands ||
              m.2.2>pairGateBudget 2 demands i j then
            throw (IO.userError "demand pair ledger mismatch")
          pairs := pairs+1
  let cases' : List Certificate := [good,⟨[],[],[]⟩,
    ⟨ds,[],rs⟩,⟨ds,[⟨[(1,true),(2,true)],2⟩],rs⟩,
    ⟨ds,[⟨[(1,true),(2,true)],3⟩],rs⟩,
    ⟨ds,good.groups,[]⟩,⟨badRefs,good.groups,rs⟩,
    ⟨ds,good.groups,badRefs⟩]
  for c in cases' do checkCapacity 2 f c
  if (capacityMeter 2 f good).1 != true then
    throw (IO.userError "positive capacity contradiction rejected")
  let oversized : Group := ⟨[(1,true),(2,true)],100000⟩
  if groupMeter 2 rs oversized != (false,0,0) then
    throw (IO.userError "capacity guard failed")
  checkCapacity 2 f ⟨[⟨4,[(4,true)]⟩],[⟨[(4,true)],0⟩],[]⟩
  let v := cap 512-1
  let wf : Formula := [[(v,true)],[(v,false)]]
  let wc : Certificate := ⟨[⟨0,[(v,true)]⟩],[⟨[(v,true)],0⟩],
    [⟨1,[(v,false)]⟩]⟩
  checkCapacity 512 wf wc
  if (capacityMeter 512 wf wc).1 != true then
    throw (IO.userError "wide capacity contradiction rejected")
  if groups != 96 || pairs != 1024 then throw (IO.userError "control count mismatch")
  IO.println "F034_CAPACITY_RESOURCE_LEDGER_OK distinct=8 groups=96 pairs=1024 terminals=8 positive=1 guards=1 malformed=1 wide=1"
  pure 0
end ProctorCapacityResourceLedgerMain

def main : IO UInt32 := ProctorCapacityResourceLedgerMain.run
