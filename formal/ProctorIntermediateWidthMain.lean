namespace ProctorIntermediateWidthMain
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch tails frontier)
open ProctorUnifiedReplay (Proof target)
open ProctorXorReplay (Block toggle combine sumSupport falseLits)
open ProctorCapacityDeficiency (Group totalCapacity)
open ProctorCapacityReplay (indices groupCheck)
open ProctorCheckedBinaryScanner (cap)

def lists : Nat → List (List Nat)
  | 0 => [[]]
  | k+1 => [0,1,2,3].flatMap (fun n => (lists k).map (fun ns => n::ns))

def supportOK (K : Nat) (xs : List Nat) : Bool :=
  xs.all (fun n => decide (n<K))
def clauseOK (K : Nat) (c : Clause) : Bool :=
  c.all (fun l => decide (l.1<K))
def formulaOK (K : Nat) (f : Formula) : Bool := f.all (clauseOK K)

def run : IO UInt32 := do
  let ws := (List.range 4).flatMap lists
  let mut pairs : Nat := 0
  let mut toggles : Nat := 0
  let mut projections : Nat := 0
  for a in ws do
    for b in ws do
      if !(supportOK 4 (combine a b)) ||
          !(supportOK 4 (sumSupport [⟨a,false,[]⟩,⟨b,true,[]⟩])) then
        throw (IO.userError "XOR width closure mismatch")
      pairs := pairs+1
    for v in List.range 4 do
      if !(supportOK 4 (toggle v a)) then
        throw (IO.userError "toggle width closure mismatch")
      toggles := toggles+1
    if !(clauseOK 4 (falseLits (fun _ => false) a)) then
      throw (IO.userError "literal projection width mismatch")
    let c := a.map (fun v => (v,true))
    let b : Batch := [⟨0,0,0,c⟩]
    let f : Formula := [[(3,false)]]
    for aug in [false,true] do
      let p : Proof := ⟨[b],aug,.empty⟩
      if !(formulaOK 4 (tails b) && formulaOK 4 (frontier f [b]) &&
          formulaOK 4 (target f p)) then
        throw (IO.userError "frontier width closure mismatch")
      projections := projections+1
  let mut capacities : Nat := 0
  for n in List.range 101 do
    let gs : List Group := List.replicate n ⟨[],2⟩
    if totalCapacity gs != 2*n || !(supportOK (cap 17) (indices n)) then
      throw (IO.userError "bounded capacity or index mismatch")
    capacities := capacities+1
  for k in [0,1,2,3,cap 512] do
    let g : Group := ⟨[],k⟩
    if groupCheck [] g && k>2 then
      throw (IO.userError "capacity guard mismatch")
  if !(supportOK (cap 17) (indices 100000)) ||
      !(decide (totalCapacity (List.replicate 100000 (⟨[],2⟩ : Group))<cap 18)) then
    throw (IO.userError "wide structural bounds mismatch")
  if pairs != 7225 || toggles != 340 || projections != 170 || capacities != 101 then
    throw (IO.userError "control count mismatch")
  IO.println "F034_INTERMEDIATE_WIDTH_OK pairs=7225 toggles=340 projections=170 capacities=101 guards=5 wide=2"
  pure 0
end ProctorIntermediateWidthMain

def main : IO UInt32 := ProctorIntermediateWidthMain.run
