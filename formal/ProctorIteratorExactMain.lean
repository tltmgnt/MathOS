namespace ProctorIteratorExactMain
open ProctorIteratorExact
open ProctorIteratorOverhead (ledger selectedTotal)
open ProctorIteratorDispatch (wordMeter liftStep)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def limited (lim n : Nat) : Option Nat :=
  if n<lim then some (n+1) else none

def check (w n lim : Nat) : IO Unit := do
  let bs := bits n w
  let step := liftStep (limited lim)
  let r := ledger bs step 0
  if r.1 != wordMeter bs step 0 then
    throw (IO.userError "projection mismatch")
  if n≤lim then
    if r.1.1 != some n || r.1.2+ones bs != 2*n ||
       selectedTotal bs step 0+ones bs != 2*n+(2*w+1) then
      throw (IO.userError "successful exact count mismatch")
  else
    if r.1.1.isSome || selectedTotal bs step 0>2*n+(2*w+1) then
      throw (IO.userError "rejecting resource bound mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for w in List.range 9 do
    for n in List.range (2^w) do
      for lim in [0,n/2,n,n+1] do
        check w n lim
        small := small+1
  for (n,lim) in [(0,0),(1,0),(99999,99999),(100000,100000),
    (100000,0),(100000,99999),(131071,131071),(131071,65535)] do
    check 17 n lim
  if small != 2044 then throw (IO.userError "exact count control count mismatch")
  IO.println "F034_ITERATOR_EXACT_OK small=2044 boundary=8"
  pure 0
end ProctorIteratorExactMain

def main : IO UInt32 := ProctorIteratorExactMain.run
