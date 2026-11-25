namespace ProctorEncoderIntegrationMain
open ProctorEncoderIntegration
open ProctorParserMeterCompose (listMeter natMeter)
open ProctorDataParser (tokenize)

def words : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [10,48,49,57,58].flatMap (fun b => (words k).map (fun bs => b::bs))

def scanCheck (bs : List Nat) : IO Unit := do
  let r := tokenizeEncode bs
  if r.1 != tokenize bs || r.2>21*bs.length then
    throw (IO.userError "scanner encode reservation mismatch")

def listCheck (ts : List Nat) : IO Unit := do
  let r := listEncodeMeter natMeter ts
  let q := listMeter natMeter ts
  if r.1 != q.1 || r.2 != q.2+headerEvents ts ||
      r.2>64*ts.length+310 || headerEvents ts>307 then
    throw (IO.userError "list header accounting mismatch")

def run : IO UInt32 := do
  let mut small : Nat := 0
  for w in List.range 5 do
    for bs in words w do
      scanCheck bs
      small := small+1
  for bs in [List.replicate 127 57++[10],List.replicate 128 57++[10],
    List.replicate 129 57++[10],List.replicate 128 57++[10,49,10],
    List.replicate 128 57,List.replicate 129 57,[48,10,49,10],[48,49,10]] do
    scanCheck bs
  let mut lists : Nat := 0
  for k in List.range 33 do
    for n in List.range 34 do
      listCheck (k::List.replicate n 1)
      lists := lists+1
  for ts in [[],[100000],[100000,1],[99999,1,1],[100001],[131071],[0,9],[1,1,9]] do
    listCheck ts
  for (bs,want) in [([],0),([10],0),([49,10],18),([48,49,10],35)] do
    if (tokenizeEncode bs).2 != want then
      throw (IO.userError "exact encoder reservation mismatch")
  if small != 781 || lists != 1122 then throw (IO.userError "control count mismatch")
  IO.println "F034_ENCODER_INTEGRATION_OK scanner=781 boundary=8 lists=1122 headers=8 exact=4"
  pure 0
end ProctorEncoderIntegrationMain

def main : IO UInt32 := ProctorEncoderIntegrationMain.run
