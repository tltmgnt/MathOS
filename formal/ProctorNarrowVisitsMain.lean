namespace ProctorNarrowVisitsMain
open ProctorNarrowVisits
open ProctorCheckedBinaryScanner (narrow zeroBits checkedDigit)
open ProctorScannerCounters (nextCount)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | w+1 => (n%2=1)::bits (n/2) w

def run : IO UInt32 := do
  let mut z : Nat := 0
  let mut m : Nat := 0
  for w in List.range 9 do
    for n in List.range (2^w) do
      let xs := bits n w
      let r := zeroMeter xs
      if r.1 != zeroBits xs || r.2>w then
        throw (IO.userError "zero meter mismatch")
      z := z+1
      for k in List.range 10 do
        let q := narrowMeter k xs
        if q.1 != narrow k xs || q.2<k || q.2>max k w then
          throw (IO.userError "narrow meter mismatch")
        m := m+1
  for n in List.range 256 do
    let c := bits n 8
    let r := countNarrowMeter c
    if r.1 != nextCount c || r.2>9 then
      throw (IO.userError "counter narrowing mismatch")
  for v in [0,1,2^511,2^512-1] do
    for b in List.range 10 do
      let x := bits v 512
      let r := digitNarrowMeter x (48+b)
      if r.1 != checkedDigit x (48+b) || r.2>517 then
        throw (IO.userError "decimal narrowing mismatch")
  if z != 511 || m != 5110 then throw (IO.userError "control count mismatch")
  IO.println "F034_NARROW_VISITS_OK zero=511 narrow=5110 counter=256 wide=40"
  pure 0
end ProctorNarrowVisitsMain

def main : IO UInt32 := ProctorNarrowVisitsMain.run
