/-! Typed parser meter checks including early rejection. -/
namespace ProctorTypedParserMeterMain
open ProctorDataParser
open ProctorTypedParserMeter

def readData (file : String) : IO (List Nat) := do
  let b ← IO.FS.readBinFile (System.FilePath.mk file)
  pure (b.data.toList.map (fun c => c.toNat))

def one {α : Type} [DecidableEq α] (m : MeterParser α) (p : Parser α)
    (bytes : List Nat) : IO (Bool × Nat) := do
  let r := decodeMeter m bytes
  if r.1 != decode p bytes || r.2 > decodeBudget bytes then
    throw (IO.userError "typed parser decode mismatch")
  match tokenize bytes with
  | none => pure ()
  | some ts =>
    let t := m ts
    if t.1 != p ts || t.2 > ts.length+1 then
      throw (IO.userError "typed parser token mismatch")
    match t.1 with
    | none => pure ()
    | some (_,rest) =>
      if t.2+rest.length != ts.length then
        throw (IO.userError "typed parser consumption mismatch")
  pure (r.1.isSome,r.2)

-- Envelopes do not have a DecidableEq instance. Compare the canonical
-- encodings, using the verified successful decoder converse.
def envelopeOne (bytes : List Nat) : IO (Bool × Nat) := do
  let r := decodeMeter envelopeMeter bytes
  let enc := ProctorEnvelopeRoundtrip.encEnvelope
  if r.1.map enc != (decodeEnvelope bytes).map enc || r.2 > decodeBudget bytes then
    throw (IO.userError "envelope meter mismatch")
  match tokenize bytes with
  | none => pure ()
  | some ts =>
    let t := envelopeMeter ts
    let normalize := fun v : ProctorUnifiedReplay.Envelope × List Nat => (enc v.1,v.2)
    if t.1.map normalize != (envelopeToken ts).map normalize ||
        t.2 > ts.length+1 then
      throw (IO.userError "envelope token mismatch")
    match t.1 with
    | none => pure ()
    | some (_,rest) =>
      if t.2+rest.length != ts.length then
        throw (IO.userError "envelope consumption mismatch")
  pure (r.1.isSome,r.2)

def run (dir : String) : IO UInt32 := do
  if natMeter [] != (none,1) ||
      natMeter [9,8] != (some (9,[8]),1) ||
      boolMeter [2] != (none,1) ||
      literalMeter [9] != (none,2) ||
      clauseMeter [2,1,1] != (none,4) ||
      clauseMeter [100001] != (none,1) ||
      clauseMeter [0,9] != (some ([],[9]),1) ||
      expectedMeter [3401,0,0] != (some ((0,[]),[]),3) then
    throw (IO.userError "typed parser hand-count mismatch")
  let mut expectedOk : Nat := 0
  let mut envelopeOk : Nat := 0
  let mut bothOk : Nat := 0
  let mut count : Nat := 0
  for i in List.range 67 do
    let stem := dir ++ "/" ++ toString i
    let a ← readData (stem ++ ".cnfdata")
    let b ← readData (stem ++ ".proofdata")
    let (ha,ca) ← one expectedMeter expectedToken a
    let (hb,cb) ← envelopeOne b
    if ha then expectedOk := expectedOk+1
    if hb then envelopeOk := envelopeOk+1
    if ha && hb then bothOk := bothOk+1
    count := count+ca+cb
  if bothOk != 53 then throw (IO.userError "typed decode pair mismatch")
  IO.println ("F034_TYPED_PARSER_TOTAL expected_ok=" ++ toString expectedOk ++
    " envelope_ok=" ++ toString envelopeOk ++ " selected=" ++ toString count)
  IO.println "F034_TYPED_PARSER_METER_OK files=134 decoded_pairs=53 hand_controls=8"
  pure 0
end ProctorTypedParserMeterMain

def main (args : List String) : IO UInt32 := do
  match args with
  | [dir] => ProctorTypedParserMeterMain.run dir
  | _ => pure 2
