// D6H hard connected two-prefix family. Host fixture generation only.
function family(E,m,unsat){
 const B=[];
 // Connect both prefix vertices to each residual coordinate. These
 // factors retain support at each rank but keep vertex 1 connected
 // to every residual block when only vertex 0 is removed.
 for(let g=2;g<9;g++)B.push([-1,-(m+1),-(g*m+2)]);
 for(const g of [2,4,7])for(const [a,b] of E.tup(m,2))if(a!==b)B.push([-(g*m+a+1),-((g+1)*m+b+1)]);
 for(const root of [0,1])for(const [r,a,b] of E.tup(m,3))if(a===b&&(unsat||r!==m-1))B.push([-(root*m+r+1),-(7*m+a+1),-(8*m+b+1)]);
 return B;
}
function audit(U,E,Barrier,Old,F,Prior,Ref){
 const J=[U.machine(false),U.machine(true)],O=[Old.machine(false),Old.machine(true)],rows=[];
 for(const m of [2,3])for(const unsat of [false,true]){
  const B=family(E,m,unsat),raw=E.encode(m,Array(m).fill(0),B),d=E.decode(raw),ref=Barrier.exact(E,raw),I=[...Array(19).fill(""),U.stream(E,raw)],vs=Array.from({length:9},(_,i)=>i);
  if(Ref.residual(d,vs,[]).length!==1||Ref.residual(d,vs,[0]).length!==1||Ref.residual(d,vs,[0,1]).length!==4)throw Error("hard graph");
  for(let i=0;i<2;i++){
   let visits=0,oldVisits=0,roots=0;const a=U.executeIR(J[i],I,(pc,T)=>{if(pc===J[i].candidateEntry)visits++;if(pc===J[i].separatorEntry){if(T[15][18]!=="1")throw Error("not two-prefix");roots++;}}),b=Old.executeIR(O[i],I,pc=>{if(pc===O[i].candidateEntry)oldVisits++;});
   if((ref.status==="UNSAT")!==unsat||a.status!==b.status||a.tapes[0]!==b.tapes[0]||a.tapes[0]!== (ref.bits||"")||roots!==m*m||!Prior.propagate(E,raw,!!i))throw Error("hard family");
   rows.push({m,unsat,full:!!i,roots,visits,oldVisits,steps:a.steps,oldSteps:b.steps,clock:unsat?null:F.count(J[i],I).clock,oldClock:unsat?null:F.count(O[i],I).clock});
  }
 }
 return {cases:4,modes:rows.length,rows};
}
module.exports={family,audit};
if(require.main===module){const p="./f038_rex_width_three_";console.log(JSON.stringify(audit(require(p+"two_prefix_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require(p+"completeness_barrier.js"),require(p+"prefix_separator_ir.js"),require(p+"fast_clock.js"),require(p+"prefix_order_audit.js"),require(p+"separator_reference.js"))));}
