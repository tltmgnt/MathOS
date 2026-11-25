namespace ProctorBinaryLookupMain
open ProctorBinaryLookup
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedBinaryScanner (cap)
open ProctorCapacityReplay (getAt)

def words : Nat → List (List Bool)
  | 0 => [[]]
  | w+1 => [false,true].flatMap (fun b => (words w).map (fun bs => b::bs))

def check (xs : List Nat) (c : List Bool) : IO Unit := do
  let r := lookupBits xs c
  if r.1 != getAt xs (bitsValue c) ||
      r.2>(c.length+1)*xs.length || r.2>(c.length+1)*(bitsValue c+1) then
    throw (IO.userError "binary lookup mismatch")

def adapter (w : Nat) (xs : List Nat) (i : Nat) : IO Unit := do
  let r := checkedLookup w xs i
  let want := if i<cap w then getAt xs i else none
  if r.1 != want || r.2>(w+1)*xs.length then
    throw (IO.userError "checked lookup mismatch")

def run : IO UInt32 := do
  let ws := (List.range 8).flatMap words
  let mut small : Nat := 0
  for c in ws do
    for n in List.range 9 do
      check (List.range n) c
      small := small+1
  let mut adapters : Nat := 0
  for w in List.range 7 do
    for i in List.range (2^w+2) do
      for n in List.range 7 do
        adapter w (List.range n) i
        adapters := adapters+1
  let wide := [List.replicate 512 false,List.replicate 512 true,
    true::List.replicate 511 false,List.replicate 511 false++[true]]
  for c in wide do
    for n in [0,1,8] do check (List.range n) c
  for (xs,c,want) in [([],[],0),([9],[],1),([9],[false,false],3),
      ([9,8],[true,false],5),([9],[true,false],2)] do
    if (lookupBits xs c).2 != want then
      throw (IO.userError "exact lookup visit mismatch")
  if small != 2295 || adapters != 987 then throw (IO.userError "control count mismatch")
  IO.println "F034_BINARY_LOOKUP_OK words=2295 adapters=987 wide=12 exact=5"
  pure 0
end ProctorBinaryLookupMain

def main : IO UInt32 := ProctorBinaryLookupMain.run
