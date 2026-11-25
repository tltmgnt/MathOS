namespace ProctorFuelFreeParserMain
open ProctorFuelFreeParser
open ProctorDataParser (natToken boolToken listToken listLimit)

def bits (n : Nat) : Nat → List Bool
  | 0 => []
  | k+1 => (n%2=1)::bits (n/2) k

def limited (lim n : Nat) : Option Nat :=
  if n<lim then some (n+1) else none

def run : IO UInt32 := do
  let mut words : Nat := 0
  for w in List.range 9 do
    for n in List.range (2^w) do
      for lim in [0,n,n+1] do
        if iterWord (bits n w) (limited lim) 0 != iterNat (limited lim) n 0 then
          throw (IO.userError "word iteration mismatch")
        words := words+1
  let mut small : Nat := 0
  for k in List.range 17 do
    for n in List.range 18 do
      let ts := k::List.replicate n 1
      if listWord natToken ts != listToken natToken ts then
        throw (IO.userError "Nat list mismatch")
      if listWord boolToken ts != listToken boolToken ts then
        throw (IO.userError "Bool list mismatch")
      small := small+2
  let bad : List (List Nat) := [[],[1],[2,0],[1,2],[2,0,2],[0,2]]
  for ts in bad do
    if listWord boolToken ts != listToken boolToken ts then
      throw (IO.userError "malformed list mismatch")
  for k in [listLimit-1,listLimit,listLimit+1] do
    let ts := k::List.replicate listLimit 1
    if listWord natToken ts != listToken natToken ts then
      throw (IO.userError "list limit mismatch")
  let nested : List (List Nat) := [[0],[1,0],[2,1,3,2,4,5],
    [2,1,3,2,4],[1,100001],[2,0,0,9]]
  for ts in nested do
    if listWord (listWord natToken) ts != listToken (listToken natToken) ts then
      throw (IO.userError "nested list mismatch")
  if words != 1533 || small != 612 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_FUEL_FREE_PARSER_OK words=1533 small=612 malformed=6 boundary=3 nested=6"
  pure 0
end ProctorFuelFreeParserMain

def main : IO UInt32 := ProctorFuelFreeParserMain.run
