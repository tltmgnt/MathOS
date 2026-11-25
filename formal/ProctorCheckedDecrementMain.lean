namespace ProctorCheckedDecrementMain
open ProctorCheckedDecrement
open ProctorDataParser (digitLimit listLimit byteLimit)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def visits : List Bool → Nat
  | [] => 0
  | true::_ => 1
  | false::xs => visits xs+1

def check (w n : Nat) : IO Unit := do
  let x := bits n w
  let r := decMeter x
  if r.2 != visits x || r.2>w then
    throw (IO.userError "decrement visit mismatch")
  if n=0 then
    if r.1.isSome || r.2 != w then
      throw (IO.userError "decrement underflow mismatch")
  else
    if r.1 != some (bits (n-1) w) then
      throw (IO.userError "decrement result mismatch")

set_option exponentiation.threshold 512 in
def run : IO UInt32 := do
  let mut small : Nat := 0
  for w in List.range 9 do
    for n in List.range (2^w) do
      check w n
      small := small+1
  let mut boundary : Nat := 0
  for (w,limit) in [(8,digitLimit),(17,listLimit),(20,byteLimit)] do
    for n in [0,1,limit-1,limit,2^w-1] do
      check w n
      boundary := boundary+1
  for n in [0,1,2^511,2^512-1] do
    check 512 n
  if small != 511 || boundary != 15 then
    throw (IO.userError "decrement control count mismatch")
  IO.println "F034_CHECKED_DECREMENT_OK small=511 boundaries=15 wide=4"
  pure 0
end ProctorCheckedDecrementMain

def main : IO UInt32 := ProctorCheckedDecrementMain.run
