namespace ProctorScannerPaddingComposeMain
open ProctorScannerPaddingCompose
open ProctorBinaryScannerGates (tokenizeGates)
open ProctorDataParser (tokenize)

def words : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,58].flatMap (fun b => (words k).map (fun bs => b::bs))

def check (bs : List Nat) : IO Unit := do
  let p := tokenizePadding bs
  let e := tokenizeEncoder bs
  let g := tokenizeGates bs
  let v := ProctorScannerResourceCompose.tokenizeVisits bs
  let (gc,vc,pc,pad,enc) := resources bs
  if p.1 != tokenize bs || e.1 != p.1 || g.1 != p.1 || v.1 != p.1 ||
      gc>5235*bs.length || vc>1046*bs.length+8 || pc>20*bs.length ||
      pad>1047*bs.length || enc>21*bs.length then
    throw (IO.userError "scanner padding resource mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for k in List.range 5 do
    for bs in words k do
      check bs
      small := small+1
  let boundary := [List.replicate 127 57++[10],
    List.replicate 128 57++[10],List.replicate 129 57++[10],
    List.replicate 128 57++[10,49,10],
    List.replicate 128 57,List.replicate 129 57,
    [48,10,49,10],[48,49,10]]
  for bs in boundary do check bs
  for (bs,want) in [([],0),([10],0),([58],0),([49,10],1047),
      ([49,50,10],2094),([48,49,10],2094)] do
    if (tokenizePadding bs).2 != want then
      throw (IO.userError "padding reservation mismatch")
  if small != 781 then throw (IO.userError "control count mismatch")
  IO.println "F034_SCANNER_PADDING_COMPOSE_OK small=781 boundary=8 exact=6"
  pure 0
end ProctorScannerPaddingComposeMain

def main : IO UInt32 := ProctorScannerPaddingComposeMain.run
