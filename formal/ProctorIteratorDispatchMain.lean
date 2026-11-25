namespace ProctorIteratorDispatchMain
open ProctorIteratorDispatch
open ProctorFuelFreeParser (iterWord)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def ones : List Bool → Nat
  | [] => 0
  | false::bs => ones bs
  | true::bs => ones bs+1

def limited (lim n : Nat) : Option Nat :=
  if n<lim then some (n+1) else none

def check (w n lim : Nat) : IO Unit := do
  let bs := bits n w
  let step := limited lim
  let r := wordMeter bs (liftStep step) 0
  if r.1 != iterWord bs step 0 || r.2>2*n then
    throw (IO.userError "dispatch refinement or bound mismatch")
  if n≤lim then
    if r.1 != some n || r.2+ones bs != 2*n then
      throw (IO.userError "successful dispatch exact count mismatch")
  else if r.1.isSome then
    throw (IO.userError "short circuit mismatch")

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
  if small != 2044 then throw (IO.userError "dispatch control count mismatch")
  IO.println "F034_ITERATOR_DISPATCH_OK small=2044 boundary=8"
  pure 0
end ProctorIteratorDispatchMain

def main : IO UInt32 := ProctorIteratorDispatchMain.run
