namespace ProctorBinaryCapacityMain
open ProctorHallDeficiency
open ProctorCapacityReplay (RefRow Certificate distinctCheck groupCheck different capacityCheck)
open ProctorCapacityDeficiency (Group)
open ProctorBinaryCapacity
open ProctorCheckedBinaryScanner (cap)

def rows : List Clause := [[],[(0,true)],[(1,true)],[(1,false)],[(2,true)],
  [(1,true),(2,true)],[(1,false),(2,false)],[(1,true),(1,true)]]

def run : IO UInt32 := do
  let f : Formula := [[(1,true)],[(2,true)],[(1,false),(2,false)]]
  let ds : List RefRow := [⟨0,[(1,true)]⟩,⟨1,[(2,true)]⟩]
  let rs : List RefRow := [⟨2,[(1,false),(2,false)]⟩]
  let good : Certificate := ⟨ds,[⟨[(1,true),(2,true)],1⟩],rs⟩
  let badRefs : List RefRow := [⟨3,[]⟩,⟨0,[(2,true)]⟩]
  let mut groups : Nat := 0
  for row in rows do
    if distinctBinary 2 row != distinctCheck row then
      throw (IO.userError "capacity distinct mismatch")
    for k in List.range 4 do
      for refs in [[],rs,badRefs] do
        let g : Group := ⟨row,k⟩
        if groupBinary 2 refs g != groupCheck refs g then
          throw (IO.userError "capacity group mismatch")
        groups := groups+1
  let mut pairs : Nat := 0
  for a in rows do
    for b in rows do
      let demands : List RefRow := [⟨0,a⟩,⟨1,b⟩]
      for i in List.range 4 do
        for j in List.range 4 do
          if differentBinary 2 demands i j != different demands i j then
            throw (IO.userError "capacity disjointness mismatch")
          pairs := pairs+1
      for i in List.range 4 do
        if demandBinary 2 demands i != ProctorCapacityReplay.demandAt demands i then
          throw (IO.userError "demand selection mismatch")
  let cases' : List Certificate := [good,⟨[],[],[]⟩,
    ⟨ds,[],rs⟩,⟨ds,[⟨[(1,true),(2,true)],2⟩],rs⟩,
    ⟨ds,[⟨[(1,true),(2,true)],3⟩],rs⟩,
    ⟨ds,good.groups,[]⟩,⟨badRefs,good.groups,rs⟩,
    ⟨ds,good.groups,badRefs⟩]
  for c in cases' do
    if capacityBinary 2 f c != capacityCheck f c then
      throw (IO.userError "capacity terminal mismatch")
  if capacityBinary 2 f good != true then
    throw (IO.userError "positive capacity contradiction rejected")
  let v := cap 512-1
  let wf : Formula := [[(v,true)],[(v,false)]]
  let wc : Certificate := ⟨[⟨0,[(v,true)]⟩],[⟨[(v,true)],0⟩],
    [⟨1,[(v,false)]⟩]⟩
  if capacityBinary 512 wf wc != true ||
      capacityBinary 512 wf wc != capacityCheck wf wc then
    throw (IO.userError "wide capacity contradiction rejected")
  if groups != 96 || pairs != 1024 then throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_CAPACITY_OK distinct=8 groups=96 pairs=1024 demands=256 terminals=8 positive=1 wide=1"
  pure 0
end ProctorBinaryCapacityMain

def main : IO UInt32 := ProctorBinaryCapacityMain.run
