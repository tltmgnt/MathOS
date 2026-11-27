// D6G hard connected prefix-cut family: GAC-stable incompatible
// pair/ternary constraints in the last residual pair. Earlier blocks
// have free equality ranks, so direct search repeatedly revisits them.
function family(E,m,unsat){
 const B=[];
 for(let g=1;g<9;g+=2){
  for(const [a,b] of E.tup(m,2))if(a!==b)B.push([-(g*m+a+1),-((g+1)*m+b+1)]);
  if(g<7)B.push([-1,-(g*m+1),-((g+1)*m+2)]);
  else for(const [r,a,b] of E.tup(m,3))if(a===b&&(unsat||r!==m-1))B.push([-(r+1),-(g*m+a+1),-((g+1)*m+b+1)]);
 }return B;
}
function audit(U,E,Barrier,Old,F,Prior){
 const J=[U.machine(false),U.machine(true)],O=[Old.machine(false),Old.machine(true)],rows=[];
 for(const m of [2,3])for(const unsat of [false,true]){
  const B=family(E,m,unsat),raw=E.encode(m,Array(m).fill(0),B),ref=Barrier.exact(E,raw),I=[...Array(19).fill(""),U.stream(E,raw)];
  for(let i=0;i<2;i++){
   let visits=0,oldVisits=0,roots=0;const a=U.executeIR(J[i],I,pc=>{if(pc===J[i].candidateEntry)visits++;if(pc===J[i].separatorEntry)roots++;}),b=Old.executeIR(O[i],I,pc=>{if(pc===O[i].candidateEntry)oldVisits++;});
   if((ref.status==="UNSAT")!==unsat||a.status!==b.status||a.tapes[0]!==b.tapes[0]||a.tapes[0]!== (ref.bits||"")||roots!==m||!Prior.propagate(E,raw,!!i))throw Error("hard family");
   rows.push({m,unsat,full:!!i,roots,visits,oldVisits,steps:a.steps,oldSteps:b.steps,clock:unsat?null:F.count(J[i],I).clock,oldClock:unsat?null:F.count(O[i],I).clock});
  }
 }
 return {cases:4,modes:rows.length,rows};
}
module.exports={family,audit};
if(require.main===module){const p="./f038_rex_width_three_";console.log(JSON.stringify(audit(require(p+"prefix_separator_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require(p+"completeness_barrier.js"),require(p+"local_component_ir.js"),require(p+"fast_clock.js"),require(p+"prefix_order_audit.js"))));}
