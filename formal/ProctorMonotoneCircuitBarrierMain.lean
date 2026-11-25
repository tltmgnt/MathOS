namespace ProctorMonotoneCircuitBarrierMain
open ProctorHallDeficiency
open ProctorMonotoneCircuitBarrier

def rows : Formula :=
  [[],[(1,true)],[(1,false)],[(2,true),(3,true)],
   [(1,true),(1,false)],[(1,true),(1,true),(1,true)],
   [(1,false),(2,false),(3,false)],[(1,false),(2,false),(3,true)],
   [(1,true),(2,true),(3,false)],[(1,true),(2,true),(3,true)],
   [(2,true),(1,true)],[(1,true),(2,true)]]
def subsets : Formula → List Formula
  | [] => [[]]
  | c::cs => let fs := subsets cs; fs++fs.map (fun f => c::f)
def bit (n i : Nat) : Bool := (n / 2^i)%2 == 1
def rassign (n : Nat) : Rails :=
  fun l => bit n (2*(l.1-1)+(if l.2 then 0 else 1))
def assignment (n : Nat) : Assignment := fun v => bit n (v-1)
def truth (x : Assignment) (f : Formula) : Bool :=
  f.all (fun c => c.any (fun l => x l.1 == l.2))
def run : IO UInt32 := do
  let mut sat := 0
  let mut unsat := 0
  let mut witnesses := 0
  for f in subsets rows do
    let expected := (List.range 8).any (fun a => truth (assignment a) f)
    let mut found := false
    for a in List.range 64 do
      let r := rassign a
      if eval r (lhs f) != eval r (rhs f) then
        found := true
        witnesses := witnesses+1
        if !(truth (decode r) f) then throw (IO.userError "bad decoded witness")
    if found != expected then throw (IO.userError "equivalence mismatch")
    if expected then sat := sat+1 else unsat := unsat+1
  if sat != 1280 || unsat != 2816 || witnesses != 6384 then
    throw (IO.userError "fixture totals")
  IO.println "F036_MONOTONE_CIRCUIT_BARRIER_OK formulas=4096 rails=262144 sat=1280 unsat=2816 witnesses=6384"
  pure 0
end ProctorMonotoneCircuitBarrierMain
def main : IO UInt32 := ProctorMonotoneCircuitBarrierMain.run
