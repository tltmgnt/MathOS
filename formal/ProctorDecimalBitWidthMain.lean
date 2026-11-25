namespace ProctorDecimalBitWidthMain
open ProctorDecimalBitWidth
open ProctorDataParser (tokenize)

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def columns (a b : Nat) : Nat → List (Bool × Bool)
  | 0 => []
  | k+1 => (a%2=1,b%2=1)::columns (a/2) (b/2) k

def checkWord (a : List Nat) : IO Bool := do
  match tokenize a with
  | none => pure false
  | some ts =>
    if ts.any (fun v => v>=ceiling) then
      throw (IO.userError "decimal operand width mismatch")
    pure true

def run (dir : String) : IO UInt32 := do
  if ceiling != 2^512 then throw (IO.userError "ceiling mismatch")
  let maxWord := List.replicate 128 57 ++ [10]
  let tooLong := List.replicate 129 57 ++ [10]
  if !(← checkWord maxWord) || (← checkWord tooLong) ||
      !(← checkWord [48,10]) then
    throw (IO.userError "decimal boundary mismatch")
  let mut tests : Nat := 0
  for a in List.range 16 do
    for b in List.range 16 do
      for c in [false,true] do
        let cols := columns a b 4
        let r := rippleMeter cols c
        if bitsValue r.1 != a+b+bitVal c || r.1.length != 5 || r.2 != 20 then
          throw (IO.userError "ripple four-bit mismatch")
        tests := tests+1
  let wide := rippleMeter (List.replicate 512 (true,false)) true
  if wide.1 != List.replicate 512 false ++ [true] || wide.2 != 2560 ||
      bitsValue wide.1 != ceiling then
    throw (IO.userError "ripple wide carry mismatch")
  let mut yes : Nat := 0
  let mut no : Nat := 0
  for i in List.range 67 do
    let stem := dir ++ "/" ++ toString i
    for ext in [".cnfdata",".proofdata"] do
      if ← checkWord (← readData (stem++ext)) then yes := yes+1 else no := no+1
  if yes != 127 || no != 7 || tests != 512 then
    throw (IO.userError "decimal bit-width fixture mismatch")
  IO.println "F034_DECIMAL_BIT_WIDTH_OK files=134 lexical_accept=127 lexical_reject=7 ripple=512 wide=1 word_controls=3"
  pure 0
end ProctorDecimalBitWidthMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorDecimalBitWidthMain.run dir
  | _ => pure 2
