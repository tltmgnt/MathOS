namespace ProctorValueProjectionMain
open ProctorValueProjection
open ProctorDecimalBitWidth (bitsValue)
open ProctorDataParser (tokenize)

def words : Nat → List (List Bool)
  | 0 => [[]]
  | k+1 => [false,true].flatMap (fun b => (words k).map (fun bs => b::bs))

def byteWords : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,58].flatMap (fun b => (byteWords k).map (fun bs => b::bs))

def checkWord (xs : List Bool) : IO Unit := do
  let r := valueMeter xs
  if r.1 != bitsValue xs || r.2 != 3*xs.length then
    throw (IO.userError "value projection mismatch")

def checkBytes (bs : List Nat) : IO Unit := do
  let r := tokenizeEmit bs
  if r.1 != tokenize bs || r.2>1536*bs.length then
    throw (IO.userError "emission resource mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for k in List.range 9 do
    for xs in words k do
      checkWord xs
      small := small+1
  for xs in [List.replicate 512 false,List.replicate 512 true,
    true::List.replicate 511 false,List.replicate 511 false++[true]] do
    checkWord xs
  let mut scanner : Nat := 0
  for k in List.range 5 do
    for bs in byteWords k do
      checkBytes bs
      scanner := scanner+1
  for bs in [List.replicate 127 57++[10],List.replicate 128 57++[10],
    List.replicate 129 57++[10],List.replicate 128 57++[10,49,10],
    List.replicate 128 57,List.replicate 129 57,[48,10,49,10],[48,49,10]] do
    checkBytes bs
  for (bs,want) in [([],0),([10],0),([49],0),([49,10],1536),
      ([49,10,58],1536),([48,10,49,10],3072)] do
    if (tokenizeEmit bs).2 != want then
      throw (IO.userError "exact emission charge mismatch")
  if small != 511 || scanner != 781 then throw (IO.userError "control count mismatch")
  IO.println "F034_VALUE_PROJECTION_OK words=511 wide=4 scanner=781 boundary=8 exact=6"
  pure 0
end ProctorValueProjectionMain

def main : IO UInt32 := ProctorValueProjectionMain.run
