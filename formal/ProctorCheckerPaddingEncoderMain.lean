namespace ProctorCheckerPaddingEncoderMain
open ProctorCheckerPaddingEncoder
open ProctorCheckerBinaryTests (eqMeter idMeter checkedEq checkedId)
open ProctorCheckedBinaryScanner (cap)
open ProctorEncodeVisits (encodeMeter budget)

def words : Nat → List (List Bool)
  | 0 => [[]]
  | w+1 => [false,true].flatMap (fun b => (words w).map (fun bs => b::bs))

def check (a b : List Bool) : IO Unit := do
  let e := eqResources a b
  let v := idResources a b
  let w := max a.length b.length
  if e.1 != eqMeter a b || v.1 != idMeter a b ||
      e.2 != w+w || v.2 != b.length+w then
    throw (IO.userError "checker circuit resource mismatch")

def adapter (w a b : Nat) : IO Unit := do
  let e := checkedEqResources w a b
  let v := checkedIdResources w a b
  let p := if a<cap w ∧ b<cap w then w+w else 0
  let c := (encodeMeter w a).2+(encodeMeter w b).2
  if e.1.1 != checkedEq w a b || v.1.1 != checkedId w a b ||
      e.1.2 != p || v.1.2 != p || e.2 != c || v.2 != c ||
      c>budget w+budget w || e.1.1.2>10*w+3 || v.1.1.2>10*w+2 then
    throw (IO.userError "checker checked resource mismatch")

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
  for (a,b) in [(0,0),(1,0),(cap 512,1),(1,cap 512)] do adapter 512 a b
  if pairs != 961 || adapters != 1641 then throw (IO.userError "control count mismatch")
  IO.println "F034_CHECKER_PADDING_ENCODER_OK pairs=961 adapters=1641 wide=16 wideAdapters=4"
  pure 0
end ProctorCheckerPaddingEncoderMain

def main : IO UInt32 := ProctorCheckerPaddingEncoderMain.run
