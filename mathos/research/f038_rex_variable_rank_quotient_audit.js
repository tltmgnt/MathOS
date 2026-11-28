// D6Z independent exhaustive model sets and physical-transition replays.
function audit(U,Q,P,K,F,Min){
 const ok=(v,s)=>{if(!v)throw Error(s)},J=P.machine(),dual=K.compile(J),M=P.singleExit(dual),N0=Min.refine(M),N={...M,...N0};
 const stats={modelCases:0,sourceAssignments:0,quotientAssignments:0,quotientModels:0,lexChecks:0,physicalCases:0,physicalSat:0,physicalUnsat:0,physicalTransitions:0,clockChecks:0,quotientReplays:0,cutoffs:0,derivedRounds:0,cycleCases:0,barrierCases:0,reducedPhysical:0,reducedPhysicalTransitions:0,reducedImproved:0,reducedTied:0,reducedRegressed:0,rawProjectionChecks:0,descriptorRows:0};
 // Decode the standard descriptor independently, including every row.
 const desc=Min.encode(N),w=N.q.toString(2).length;
 ok(desc.slice(0,N.q+4)==="111"+"1".repeat(N.q)+"0"&&desc.length===N0.stats.quotientBits,"descriptor header");
 let off=N.q+4;
 for(let i=0;i<N.T.length;i++){const next=parseInt(desc.slice(off,off+w),2),write=parseInt(desc.slice(off+w,off+w+2),2),move=parseInt(desc.slice(off+w+2,off+w+4),2);
  ok(((next<<4)|(write<<2)|move)===N.T[i],"descriptor row");off+=w+4;stats.descriptorRows++;
 }
 ok(off===desc.length,"descriptor length");
 const rows=[];
 function oracle(d){let out=[];for(let i=0;i<d.m**d.k;i++){const z=Array.from({length:d.k},(_,j)=>Math.floor(i/d.m**(d.k-j-1))%d.m);if(d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))out.push(z.join());}return out;}
 function check(d,name,physical=false){
  const expected=oracle(d),q=Q.quotient(U,d),actual=oracle(q.d).map(s=>q.expand(s.split(",").map(Number)).join());
  ok(JSON.stringify(expected)===JSON.stringify(actual),"model bijection "+name);stats.modelCases++;stats.sourceAssignments+=d.m**d.k;stats.quotientAssignments+=q.d.m**q.d.k;stats.quotientModels+=actual.length;
  const r=Q.solve(U,d);ok(r.status===(expected.length?"SAT":"UNSAT")&&(r.z?.join()??null)===(expected[0]??null),"lex "+name);stats.lexChecks++;
  if(r.rounds.filter(x=>x.after<x.before).length>1)stats.derivedRounds++;
  if(q.stats.cycleDeleted)stats.cycleCases++;
  if(physical){
   const s=P.stream(U,d),a=P.run(M,s),b=P.run(N,s,a.t),c=P.run(N,s,a.t-1),f=F.count(J,["",s],M.codes),e=P.run(dual,s,a.t);
   ok(a.status===r.status&&(a.z?.join()??null)===(expected[0]??null),"physical "+name);
   ok(a.t===f.clock&&a.encoded===f.encoded&&a.head===0,"clock and encoding "+name);
   ok(JSON.stringify(a)===JSON.stringify(b)&&JSON.stringify(a)===JSON.stringify(e),"quotient/dual parity "+name);
   ok(c.status==="TIMEOUT"&&c.t===a.t-1&&c.z===null,"cutoff");
   stats.physicalCases++;stats[a.status==="SAT"?"physicalSat":"physicalUnsat"]++;stats.physicalTransitions+=a.t;stats.clockChecks++;stats.quotientReplays++;stats.cutoffs++;
   const reduced=Q.reduce(U,d),rs=P.stream(U,reduced.d),ra=P.run(N,rs),rf=F.count(J,["",rs],M.codes);
   const expanded=ra.z?reduced.expand(ra.z):null;
   ok(ra.status===a.status&&JSON.stringify(expanded)===JSON.stringify(a.z)&&ra.t===rf.clock&&ra.encoded===rf.encoded,"reduced physical "+name);
   stats.reducedPhysical++;stats.reducedPhysicalTransitions+=ra.t;
   stats[ra.t<a.t?"reducedImproved":ra.t===a.t?"reducedTied":"reducedRegressed"]++;
   if(expanded&&d.pins){const bits=U.witness(d.k,d.m,d.pins,expanded);
    ok(U.project(d.k,bits).join()===expected[0],"raw projection");stats.rawProjectionChecks++;
   }
   return {status:r.status,k:d.k,reduced:r.k,models:expected.length,used:String(r.used),physical:a.t,reducedPhysical:ra.t,stream:s.length,reducedStream:rs.length,span:a.span};
  }
  return {status:r.status,k:d.k,reduced:r.k,models:expected.length,used:String(r.used),rounds:r.rounds};
 }
 const c2=[[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]];
 const c3=[...U.tuples(2,3)].map(z=>z.map((a,i)=>a?i+1:-i-1));
 for(const [k,C] of [[2,c2],[3,c3]])for(let i=0;i<256;i++){
  const a=U.lift(k,C.filter((_,j)=>i>>j&1));check(U.decode(k,2,a.raw),"cnf-"+k+"-"+i,true);
 }
 let seed=0xD6A123;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const factor=(h,m,p)=>({h,S:new Set([...U.tuples(m,h.length)].filter(p).map(z=>z.join()))});
 for(let i=0;i<120;i++){
  const k=3+i%4,m=2+i%3,F=[];
  for(let g=1;g<k;g++)if(rand()%3!==0){const off=rand()%m;F.push(factor([g-1,g],m,([a,b])=>b===(a+off)%m));}
  F.push(factor([0,k-1],m,()=>rand()%5!==0));F.push(factor([0,1,2],m,()=>rand()%4!==0));
  check({k,m,F},"mixed-"+i,m===2);
 }
 // Nontrivial cycle: transposition leaves rank2 feasible, not an automatic contradiction.
 {const m=3,k=3,F=[factor([0,1],m,([a,b])=>a===b),factor([1,2],m,([a,b])=>a===b),factor([0,2],m,([a,b])=>b===[1,0,2][a])];const r=check({k,m,F},"cycle-fixed-point");ok(r.models===1&&r.reduced===1,"fixed point");rows.push({name:"cycle-fixed-point",...r});}
 // After first collapse, a ternary factor becomes a newly discovered bijection.
 {const m=3,k=3,F=[factor([0,1],m,([a,b])=>a===b),factor([0,1,2],m,([a,b,c])=>a!==b||c===(a+1)%m)];const r=check({k,m,F},"derived-permutation");ok(r.reduced===1&&r.models===3&&r.rounds.length===3,"iterated");rows.push({name:"derived-permutation",...r});}
 for(const k of [4,6,8,10,12,16]){
  const d=U.decode(k,2,U.encode(k,2,[0,0],U.denseBarrier(k,2))),r=check(d,"equality-barrier",k<=8);ok(r.reduced===1&&r.used==="0"&&!r.models,"old barrier");rows.push({name:"equality-barrier",...r,oldCandidates:String(2n**BigInt(k))});stats.barrierCases++;
 }
 // A residual obstruction with no binary bijections: at most one 1
 // globally, but at least two 1s in the first three coordinates.
 for(const k of [4,6,8,10,12,16]){
  const m=2,F=[...U.subsets(Array.from({length:k},(_,i)=>i),2)].map(h=>factor(h,m,z=>z[0]+z[1]<=1));
  F.push(factor([0,1,2],m,z=>z.reduce((a,b)=>a+b,0)>=2));const d={k,m,F},G=U.gac(d),r=check(d,"residual-barrier",k<=8);
  ok(G.deletions===0&&r.reduced===k&&r.used===String(2n**BigInt(k))&&r.models===0,"residual barrier");rows.push({name:"residual-barrier",...r,gacDeletions:G.deletions});stats.barrierCases++;
 }
 return {stats,resources:{logical:J.ins.length,...N0.stats},rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_variable_rank_reduction.js"),require("./f038_rex_variable_rank_quotient.js"),require("./f038_rex_variable_rank_worker.js"),require("./f038_rex_width_three_local_motion_compiler.js"),require("./f038_rex_width_three_local_motion_clock.js"),require("./f038_rex_width_two_quotient.js"))));
