namespace ProctorIteratorOverheadMain
open ProctorIteratorOverhead
open ProctorIteratorDispatch (wordMeter liftStep)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def limited (lim n : Nat) : Option Nat :=
  if n<lim then some (n+1) else none

-- Independent structural expectation: the first failing set-bit block
-- is entered, but no next wrapper is created. Success visits all bits
-- and the empty terminator. On failure the remaining demand is > lim.
def expectedOverhead : List Bool → Nat → Nat → Nat
  | [],_,_ => 1
  | false::bs,p,lim => 2+expectedOverhead bs (p+p) lim
  | true::bs,p,lim =>
    if lim<p then 1 else 2+expectedOverhead bs (p+p) (lim-p)

def check (w n lim : Nat) : IO Unit := do
  let bs := bits n w
  let step := liftStep (limited lim)
  let r := ledger bs step 0
  if r.1 != wordMeter bs step 0 then
    throw (IO.userError "dispatch projection mismatch")
  if r.2 != expectedOverhead bs 1 lim || r.2>2*w+1 then
    throw (IO.userError "structural overhead mismatch")
  if selectedTotal bs step 0>2*n+(2*w+1) then
    throw (IO.userError "joint bound mismatch")
  if n≤lim then
    if r.1.1 != some n || r.2 != 2*w+1 then
      throw (IO.userError "successful overhead mismatch")

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
  if small != 2044 then throw (IO.userError "overhead control count mismatch")
  IO.println "F034_ITERATOR_OVERHEAD_OK small=2044 boundary=8"
  pure 0
end ProctorIteratorOverheadMain

def main : IO UInt32 := ProctorIteratorOverheadMain.run
