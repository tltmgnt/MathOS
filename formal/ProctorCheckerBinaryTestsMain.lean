namespace ProctorCheckerBinaryTestsMain
open ProctorCheckerBinaryTests
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedBinaryScanner (cap)
open ProctorCapacityReplay (test)
open ProctorUnifiedReplay (validId)

def words : Nat → List (List Bool)
  | 0 => [[]]
  | w+1 => [false,true].flatMap (fun b => (words w).map (fun bs => b::bs))

def check (a b : List Bool) : IO Unit := do
  let e := eqMeter a b
  let v := idMeter a b
  let w := max a.length b.length
  if e.1 != test (bitsValue a=bitsValue b) ||
     v.1 != validId (bitsValue a) (bitsValue b) ||
     e.2>10*w+3 || v.2>10*w+2 then
    throw (IO.userError "binary checker test mismatch")

def adapter (w a b : Nat) : IO Unit := do
  let e := checkedEq w a b
  let v := checkedId w a b
  let ee := if a<cap w ∧ b<cap w then some (test (a=b)) else none
  let vv := if a<cap w ∧ b<cap w then some (validId a b) else none
  if e.1 != ee || v.1 != vv || e.2>10*w+3 || v.2>10*w+2 then
    throw (IO.userError "checked adapter mismatch")

def run : IO UInt32 := do
  let ws := (List.range 5).flatMap words
  let mut pairs : Nat := 0
  for a in ws do
    for b in ws do
      check a b
      pairs := pairs+1
  let mut adapters : Nat := 0
  for w in List.range 6 do
    for a in List.range (2^w+2) do
      for b in List.range (2^w+2) do
        adapter w a b
        adapters := adapters+1
  let wide := [List.replicate 512 false,List.replicate 512 true,
    true::List.replicate 511 false,List.replicate 511 false++[true]]
  for a in wide do
    for b in wide do check a b
  if pairs != 961 || adapters != 1641 then throw (IO.userError "control count mismatch")
  IO.println "F034_CHECKER_BINARY_TESTS_OK pairs=961 adapters=1641 wide=16"
  pure 0
end ProctorCheckerBinaryTestsMain

def main : IO UInt32 := ProctorCheckerBinaryTestsMain.run
