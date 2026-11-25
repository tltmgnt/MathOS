namespace ProctorPaddingVisitsMain
open ProctorPaddingVisits
open ProctorBinaryPrimitives (padColumns compareMeter addMeter decimalMeter)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def check (a b : List Bool) : IO Unit := do
  let p := padMeter a b
  let c := compareResources a b
  let s := addResources a b
  let w := max a.length b.length
  if p.1 != padColumns a b || p.2 != w ||
    c.1 != compareMeter a b || c.2 != w || c.1.2 != 5*w ||
    s.1 != addMeter a b || s.2 != w || s.1.2 != 5*w then
    throw (IO.userError "padding resource mismatch")

def run : IO UInt32 := do
  let mut pairs : Nat := 0
  let mut decimal : Nat := 0
  for wa in List.range 5 do
    for wb in List.range 5 do
      for a in List.range (2^wa) do
        for b in List.range (2^wb) do
          check (bits a wa) (bits b wb)
          pairs := pairs+1
  for a in List.range 256 do
    for d in List.range 10 do
      let v := bits a 8
      let digit := bits d 4
      let r := decimalResources v digit
      if r.1 != decimalMeter v digit || r.2 != 23 then
        throw (IO.userError "decimal padding resource mismatch")
      decimal := decimal+1
  let v := List.replicate 512 true
  let z := List.replicate 512 false
  check v z
  check z v
  check v []
  let r := decimalResources v (bits 9 4)
  if r.1 != decimalMeter v (bits 9 4) || r.2 != 1031 then
    throw (IO.userError "wide decimal padding mismatch")
  if pairs != 961 || decimal != 2560 then throw (IO.userError "control count mismatch")
  IO.println "F034_PADDING_VISITS_OK pairs=961 decimal=2560 wide=4"
  pure 0
end ProctorPaddingVisitsMain

def main : IO UInt32 := ProctorPaddingVisitsMain.run
