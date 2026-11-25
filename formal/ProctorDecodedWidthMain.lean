namespace ProctorDecodedWidthMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step)
open ProctorCapacityReplay (RefRow Certificate)
open ProctorUnifiedReplay (Terminal Proof Envelope)
open ProctorCheckedBinaryScanner (cap)

def fits (n : Nat) : Bool := decide (n<cap 512)
def clauseOK (c : Clause) : Bool := c.all (fun l => fits l.1)
def formulaOK (f : Formula) : Bool := f.all clauseOK
def refOK (r : RefRow) : Bool := fits r.index && clauseOK r.row
def groupOK (g : ProctorCapacityDeficiency.Group) : Bool :=
  clauseOK g.literals && fits g.cap
def capacityOK (c : Certificate) : Bool :=
  c.demands.all refOK && c.groups.all groupOK && c.conflicts.all refOK
def blockOK (b : ProctorXorReplay.Block) : Bool :=
  b.support.all fits && b.refs.all refOK
def stepOK (s : Step) : Bool :=
  fits s.left && fits s.right && fits s.pivot && clauseOK s.tail
def terminalOK : Terminal → Bool
  | .empty => true
  | .capacity c => capacityOK c
  | .xor bs => bs.all blockOK
def proofOK (p : Proof) : Bool :=
  p.batches.all (fun b => b.all stepOK) && terminalOK p.terminal
def envelopeOK (e : Envelope) : Bool :=
  fits e.variableBound && formulaOK e.original && proofOK e.proof

def bytes (ts : List Nat) : List Nat :=
  ts.flatMap (fun n => (toString n).toList.map Char.toNat ++ [10])

def expectedCheck (ts : List Nat) (want : Bool) : IO Unit := do
  let bs := bytes ts
  match ProctorDataParser.decodeExpected bs, ProctorFuelFreeDecoder.decodeExpected bs with
  | some (n,f),some (m,g) =>
    if !want || !(fits n && formulaOK f && fits m && formulaOK g) ||
        ProctorWireRoundtrip.encExpected n f != ts ||
        ProctorWireRoundtrip.encExpected m g != ts then
      throw (IO.userError "expected field width mismatch")
  | none,none =>
    if want then throw (IO.userError "expected decode unexpectedly rejected")
  | _,_ => throw (IO.userError "expected decoder disagreement")

def envelopeCheck (ts : List Nat) (want : Bool) : IO Unit := do
  let bs := bytes ts
  match ProctorDataParser.decodeEnvelope bs, ProctorFuelFreeDecoder.decodeEnvelope bs with
  | some e,some f =>
    if !want || !(envelopeOK e && envelopeOK f) ||
        ProctorEnvelopeRoundtrip.encEnvelope e != ts ||
        ProctorEnvelopeRoundtrip.encEnvelope f != ts then
      throw (IO.userError "envelope field width mismatch")
  | none,none =>
    if want then throw (IO.userError "envelope decode unexpectedly rejected")
  | _,_ => throw (IO.userError "envelope decoder disagreement")

def run : IO UInt32 := do
  let w := 10^128-1
  let over := 10^128
  let ex : List (List Nat × Bool) := [
    ([3401,0,0],true),([3401,w,1,1,w,1],true),
    ([3401,1,1,1,1,0],true),([3401,over,0],false),
    ([3401,1,1,1,over,1],false),([3401,1,1,1,1,2],false)]
  -- Explicit large numeric fields in steps, capacity references and
  -- groups, and XOR support/reference rows; syntax, not proof acceptance.
  let pre := [3402,w,1,1,w,1]
  let en : List (List Nat × Bool) := [
    ([3402,0,0,0,0,0],true),
    (pre++[1,1,w,w,w,1,w,0,0,0],true),
    (pre++[0,0,1,1,w,1,w,1,1,1,w,0,w,1,w,0],true),
    (pre++[0,0,2,1,1,w,1,1,w,1,w,0],true),
    ([3402,over,0,0,0,0],false),
    (pre++[1,1,0,0,over,0,0,0],false),
    (pre++[0,0,1,1,over,0,0,0],false),
    (pre++[0,0,2,1,1,over,0,0],false)]
  for (ts,want) in ex do expectedCheck ts want
  for (ts,want) in en do envelopeCheck ts want
  for (ts,want) in [([0],true),([w],true),([over],false),([cap 512],false)] do
    match ProctorDataParser.tokenize (bytes ts) with
    | some out =>
      if !want || out != ts || !(out.all fits) then
        throw (IO.userError "token width mismatch")
    | none =>
      if want then throw (IO.userError "token unexpectedly rejected")
  IO.println "F034_DECODED_WIDTH_OK expected=6 envelope=8 tokens=4"
  pure 0
end ProctorDecodedWidthMain

def main : IO UInt32 := ProctorDecodedWidthMain.run
