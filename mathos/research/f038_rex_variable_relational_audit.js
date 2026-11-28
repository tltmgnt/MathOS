// D7A independent model-set, deletion-certificate and physical execution audit.
function audit(U,Q,R,V,P,K,F,Min){
 const ok=(v,s)=>{if(!v)throw Error(s)},J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0};
 const stats={cases:0,sourceAssignments:0,finalAssignments:0,models:0,sat:0,unsat:0,lexChecks:0,certificateRounds:0,certificateOperations:0,certifiedDeletions:0,certificateComparisons:0,closurePasses:0,projectionRows:0,testedRows:0,derivedPairs:0,contradictions:0,physicalCases:0,oldPhysical:0,newPhysical:0,improved:0,tied:0,regressed:0,exactClocks:0,quotientReplays:0,cutoffs:0,tamperRejected:0};
 const rows=[];
 function oracle(d){const out=[];for(let i=0;i<d.m**d.k;i++){const z=Array.from({length:d.k},(_,j)=>Math.floor(i/d.m**(d.k-j-1))%d.m);if(d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))out.push(z.join());}return out;}
 function check(d,name,physical=false){
  const expected=oracle(d),r=R.reduce(U,Q,d,true),actual=oracle(r.d).map(s=>r.expand(s.split(",").map(Number)).join());
  ok(JSON.stringify(expected)===JSON.stringify(actual),"models "+name);stats.cases++;stats.sourceAssignments+=d.m**d.k;stats.finalAssignments+=r.d.m**r.d.k;stats.models+=actual.length;stats[expected.length?"sat":"unsat"]++;
  const s=R.solve(U,Q,d);ok(s.status===(expected.length?"SAT":"UNSAT")&&(s.z?.join()??null)===(expected[0]??null),"lex "+name);stats.lexChecks++;
  let deleted=0,derived=0,passes=0;
  for(const x of r.rounds){const v=V.verify(x.closureInput,x.closureOutput,x.log);ok(v.deleted===x.closure.deleted,"deleted");
   stats.certificateRounds++;stats.certificateOperations+=x.log.length;stats.certifiedDeletions+=v.deleted;stats.certificateComparisons+=v.comparisons;stats.closurePasses+=x.closure.passes;stats.projectionRows+=x.closure.projectionRows;stats.testedRows+=x.closure.testedRows;stats.derivedPairs+=x.closure.derived;
   deleted+=v.deleted;derived+=x.closure.derived;passes+=x.closure.passes;
  }
  if(r.contradiction)stats.contradictions++;
  const result={name,k:d.k,m:d.m,reduced:r.d.k,models:actual.length,status:s.status,used:String(s.used),deleted,derived,passes,rounds:r.rounds.length};
  if(physical){
   const old=Q.reduce(U,d),os=P.stream(U,old.d),ns=P.stream(U,r.d),a=P.run(N,os,300000000),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1);
   const x=a.z?old.expand(a.z):null,y=b.z?r.expand(b.z):null,clock=F.count(J,["",ns],M.codes),oc=F.count(J,["",os],M.codes);
   ok(a.status===s.status&&b.status===s.status&&JSON.stringify(x)===JSON.stringify(y)&&(y?.join()??null)===(expected[0]??null),"physical witness "+name);
   ok(b.t===clock.clock&&b.encoded===clock.encoded&&a.t===oc.clock&&a.encoded===oc.encoded&&b.head===0,"clock "+name);
   ok(JSON.stringify(b)===JSON.stringify(c)&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"quotient/cutoff "+name);
   stats.physicalCases++;stats.oldPhysical+=a.t;stats.newPhysical+=b.t;stats[b.t<a.t?"improved":b.t===a.t?"tied":"regressed"]++;stats.exactClocks+=2;stats.quotientReplays++;stats.cutoffs++;
   Object.assign(result,{oldPhysical:a.t,newPhysical:b.t,oldStream:os.length,newStream:ns.length});
  }
  return result;
 }
 const c2=[[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]],c3=[...U.tuples(2,3)].map(z=>z.map((a,i)=>a?i+1:-i-1));
 for(const [k,C] of [[2,c2],[3,c3]])for(let i=0;i<256;i++){const a=U.lift(k,C.filter((_,j)=>i>>j&1));check(U.decode(k,2,a.raw),"cnf-"+k+"-"+i,true);}
 let seed=0xD6A123;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const factor=(h,m,p)=>({h,S:new Set([...U.tuples(m,h.length)].filter(p).map(z=>z.join()))});
 for(let i=0;i<120;i++){
  const k=3+i%4,m=2+i%3,F=[];
  for(let g=1;g<k;g++)if(rand()%3!==0){const off=rand()%m;F.push(factor([g-1,g],m,([a,b])=>b===(a+off)%m));}
  F.push(factor([0,k-1],m,()=>rand()%5!==0));F.push(factor([0,1,2],m,()=>rand()%4!==0));
  check({k,m,F},"mixed-"+i,m===2);
 }
 {const m=3,k=3,F=[factor([0,1],m,([a,b])=>a===b),factor([1,2],m,([a,b])=>a===b),factor([0,2],m,([a,b])=>b===[1,0,2][a])];rows.push(check({k,m,F},"cycle-fixed-point"));}
 {const m=3,k=3,F=[factor([0,1],m,([a,b])=>a===b),factor([0,1,2],m,([a,b,c])=>a!==b||c===(a+1)%m)];rows.push(check({k,m,F},"derived-permutation"));}
 for(const k of [4,6,8,10,12,16]){
  const d=U.decode(k,2,U.encode(k,2,[0,0],U.denseBarrier(k,2)));const r=check(d,"equality-barrier",k<=8);ok(r.used==="0","equality");rows.push(r);
 }
 for(const k of [4,6,8,10,12,16]){
  const m=2,F=[...U.subsets(Array.from({length:k},(_,i)=>i),2)].map(h=>factor(h,m,z=>z[0]+z[1]<=1));F.push(factor([0,1,2],m,z=>z.reduce((a,b)=>a+b,0)>=2));const d={k,m,F};
  const r=check(d,"pair-triple-barrier",k<=8);ok(r.used==="0"&&r.deleted>0&&r.models===0,"old obstruction");rows.push(r);
  if(k===4){const c=R.close(d,true),tryBad=log=>{let failed=false;try{V.verify(d,c.d,log);}catch{failed=true;}ok(failed,"tamper accepted");stats.tamperRejected++;};
   tryBad(c.log.slice(1));tryBad(c.log.map((x,i)=>i?x:{...x,removed:[]}));tryBad(c.log.map((x,i)=>i?x:{...x,b:x.a}));
  }
 }
 const inherited={...stats};
 // New independent projection-discovered permutation (no original binary factor).
 for(const m of [2,3,4]){const d={k:3,m,F:[factor([0,1,2],m,([a,b,c])=>b===(a+1)%m&&c!==a)]},r=check(d,"projected-permutation",m===2);ok(r.derived>=1&&r.reduced<3&&r.models===m*(m-1),"projection contraction");rows.push(r);}
 // Contradiction requires information propagated along overlapping scopes.
 {const m=2,k=5,F=[factor([0],m,([a])=>a===0),factor([0,1],m,([a,b])=>a<=b),factor([1,2],m,([a,b])=>a<=b),factor([2,3],m,([a,b])=>a<=b),factor([3,4],m,([a,b])=>a<=b),factor([4],m,([a])=>a===1)];rows.push(check({k,m,F},"overlap-chain",true));}
 // Dense XOR relations: each proper projection universal, yet a four-row
 // linear dependency has odd RHS. Semijoin and permutation quotient fail.
 for(const k of [6,8,10,12,16]){
  const d=R.residualBarrier(U,k),r=check(d,"dense-parity-barrier",k===6);
  ok(r.used===String(2n**BigInt(k))&&r.deleted===0&&r.derived===0&&r.reduced===k&&r.models===0&&U.gac(d).deletions===0,"new obstruction");rows.push(r);
 }
 return {stats,inherited,resources:{logical:J.ins.length,...N0.stats},rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_variable_rank_reduction.js"),require("./f038_rex_variable_rank_quotient.js"),require("./f038_rex_variable_relational_closure.js"),require("./f038_rex_variable_relational_certificate.js"),require("./f038_rex_variable_rank_worker.js"),require("./f038_rex_width_three_local_motion_compiler.js"),require("./f038_rex_width_three_local_motion_clock.js"),require("./f038_rex_width_two_quotient.js"))));
