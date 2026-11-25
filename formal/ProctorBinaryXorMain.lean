namespace ProctorBinaryXorMain
open ProctorHallDeficiency
open ProctorXorReplay (Block toggle combine sumSupport blockCheck xorCheck)
open ProctorBinaryXor
open ProctorCheckedBinaryScanner (cap)

def supports : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [0,1,2].flatMap (fun v => (supports k).map (fun vs => v::vs))

def run : IO UInt32 := do
  let ss := (List.range 4).flatMap supports
  let mut toggles : Nat := 0
  let mut pairs : Nat := 0
  for a in ss do
    for v in List.range 3 do
      let m := toggleMeter 2 v a
      if m.1 != toggle v a || m.2>eqBudget 2*a.length then
        throw (IO.userError "binary XOR toggle mismatch")
      toggles := toggles+1
    for b in ss do
      if combineBinary 2 a b != combine a b ||
          sumBinary 2 [⟨a,false,[]⟩,⟨b,true,[]⟩] !=
            sumSupport [⟨a,false,[]⟩,⟨b,true,[]⟩] then
        throw (IO.userError "binary XOR combine mismatch")
      pairs := pairs+1
  let f : Formula := [[(1,true)],[(1,false)],[]]
  let refs : List (List ProctorCapacityReplay.RefRow) :=
    [[],[⟨0,[(1,true)]⟩],[⟨1,[(1,false)]⟩],[⟨2,[]⟩],
      [⟨0,[(1,false)]⟩],[⟨3,[]⟩]]
  let mut blocks : Nat := 0
  for vs in ss do
    for rhs in [false,true] do
      for rs in refs do
        let b : Block := ⟨vs,rhs,rs⟩
        if blockBinary 2 f b != blockCheck f b then
          throw (IO.userError "binary XOR block mismatch")
        blocks := blocks+1
  let left : Block := ⟨[1],true,[⟨0,[(1,true)]⟩]⟩
  let right : Block := ⟨[1],false,[⟨1,[(1,false)]⟩]⟩
  let cases' : List (List Block) := [[],[left],[right],[left,right],
    [left,left],[right,right],[⟨[],true,[⟨2,[]⟩]⟩],
    [⟨[1,1,1,1,1,1],true,[]⟩]]
  for bs in cases' do
    if xorBinary 2 f bs != xorCheck f bs then
      throw (IO.userError "binary XOR terminal mismatch")
  if xorBinary 2 f [left,right] != true then
    throw (IO.userError "positive XOR contradiction rejected")
  let v := cap 512-1
  let wf : Formula := [[(v,true)],[(v,false)]]
  let wb : List Block := [⟨[v],true,[⟨0,[(v,true)]⟩]⟩,
    ⟨[v],false,[⟨1,[(v,false)]⟩]⟩]
  if xorBinary 512 wf wb != true ||
      xorBinary 512 wf wb != xorCheck wf wb then
    throw (IO.userError "wide XOR contradiction rejected")
  if toggles != 120 || pairs != 1600 || blocks != 480 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_XOR_OK toggles=120 pairs=1600 blocks=480 terminals=8 positive=1 wide=1"
  pure 0
end ProctorBinaryXorMain

def main : IO UInt32 := ProctorBinaryXorMain.run
