namespace ProctorBinaryScannerGatesMain
open ProctorBinaryScannerGates
open ProctorDataParser (tokenize)

def words : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,58].flatMap (fun b => (words k).map (fun bs => b::bs))

def check (bs : List Nat) : IO Unit := do
  let r := tokenizeGates bs
  if r.1 != tokenize bs || r.2>5235*bs.length then
    throw (IO.userError "binary scanner gate meter mismatch")

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
  for (bs,want) in [([],0),([10],0),([49,10],5235),
      ([48,49,10],10470),([49,58,49,10],5235),
      (List.replicate 129 57++[10],675315)] do
    if (tokenizeGates bs).2 != want then
      throw (IO.userError "gate reservation mismatch")
  if small != 781 then throw (IO.userError "small control count mismatch")
  IO.println "F034_BINARY_SCANNER_GATES_OK small=781 boundary=8 exact=6"
  pure 0
end ProctorBinaryScannerGatesMain

def main : IO UInt32 := ProctorBinaryScannerGatesMain.run
