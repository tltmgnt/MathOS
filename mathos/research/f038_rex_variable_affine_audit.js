// D7B exhaustive model parity, independent algebra certificates, worker replay.
function audit(U,Q,R,A,V,P,K,F,Min){
 const ok=(v,s)=>{if(!v)throw Error(s)},J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0};
 const stats={cases:0,assignments:0,models:0,sat:0,unsat:0,localMasks:0,affineMasks:0,equations:0,rowOps:0,cellOps:0,affineContradictions:0,priorContradictions:0,newAffineContradictions:0,constantConflicts:0,pureAffineSat:0,narrow:0,wideFallback:0,freeRemoved:0,physicalCases:0,oldPhysical:0,newPhysical:0,improved:0,tied:0,regressed:0,clockChecks:0,cutoffs:0,tamperRejected:0},rows=[];
 function oracle(d){const out=[];for(let i=0;i<2**d.k;i++){const z=Array.from({length:d.k},(_,j)=>Math.floor(i/2**(d.k-j-1))%2);if(d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))out.push(z.join());}return out;}
 const factor=(h,fn)=>({h,S:new Set([...U.tuples(2,h.length)].filter(fn).map(z=>z.join()))});
 // Every possible relation of arity 1,2,3, including empty.
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){
  const h=Array.from({length:n},(_,i)=>i),S=new Set([...U.tuples(2,n)].filter((_,j)=>mask>>j&1).map(z=>z.join())),d={k:n,m:2,F:[{h,S}]},a=A.eliminate(d);
  V.verify(d,a);const expected=oracle(d);let closure=[];
  if(a.contradiction<0)closure=[...U.tuples(2,a.free.length)].map(z=>a.expand(z).join());
  ok(expected.every(s=>closure.includes(s))&&a.affine[0]===(expected.length===closure.length),"hull");
  stats.localMasks++;stats.affineMasks+=+a.affine[0];
 }
 function check(d,name,physical=false){
  const expected=oracle(d),pre=R.reduce(U,Q,d),r=A.reduce(U,pre.d),v=V.verify(pre.d,r.a),s=A.solve(U,pre.d);
  const actual=oracle(r.d).map(t=>pre.expand(r.expand(t.split(",").map(Number))).join());
  ok(JSON.stringify(expected)===JSON.stringify(actual),"model set "+name);
  const z=s.z?pre.expand(s.z):null;ok(s.status===(expected.length?"SAT":"UNSAT")&&(z?.join()??null)===(expected[0]??null),"lex "+name);
  stats.cases++;stats.assignments+=2**d.k;stats.models+=actual.length;stats[expected.length?"sat":"unsat"]++;stats.equations+=v.equations;stats.rowOps+=v.ops;stats.cellOps+=v.cellOps;
  stats[r.kind==="contradiction"?"affineContradictions":r.kind==="constant-conflict"?"constantConflicts":r.kind==="narrow"?"narrow":"wideFallback"]++;
  if(pre.contradiction)stats.priorContradictions++;
  if(v.contradiction&&!pre.contradiction)stats.newAffineContradictions++;
  if(s.status==="SAT"&&r.a.affine.every(Boolean)){ok(s.used===0n,"pure affine search");stats.pureAffineSat++;}
  if(!v.contradiction)stats.freeRemoved+=pre.d.k-r.a.free.length;
  const row={name,k:d.k,prior:pre.d.k,free:r.a.free.length,reduced:r.d.k,kind:r.kind,status:s.status,models:actual.length,used:String(s.used),equations:v.equations,rowOps:v.ops};
  if(physical){
   const os=P.stream(U,pre.d),ns=P.stream(U,r.d),a=P.run(N,os,300000000),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1),clock=F.count(J,["",ns],M.codes),oc=F.count(J,["",os],M.codes);
   const x=a.z?pre.expand(a.z):null,y=b.z?pre.expand(r.expand(b.z)):null;
   ok(a.status===s.status&&b.status===s.status&&JSON.stringify(x)===JSON.stringify(y)&&JSON.stringify(y)===JSON.stringify(z),"physical "+name);
   ok(b.t===clock.clock&&b.encoded===clock.encoded&&a.t===oc.clock&&a.encoded===oc.encoded,"clock");ok(JSON.stringify(b)===JSON.stringify(c)&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"cutoff");
   stats.physicalCases++;stats.oldPhysical+=a.t;stats.newPhysical+=b.t;stats[b.t<a.t?"improved":b.t===a.t?"tied":"regressed"]++;stats.clockChecks+=2;stats.cutoffs++;
   Object.assign(row,{oldPhysical:a.t,newPhysical:b.t,oldStream:os.length,newStream:ns.length});
  }
  return row;
 }
 const c2=[[1],[-1],[2],[-2],[1,2],[1,-2],[-1,2],[-1,-2]],c3=[...U.tuples(2,3)].map(z=>z.map((a,i)=>a?i+1:-i-1));
 for(const [k,C] of [[2,c2],[3,c3]])for(let i=0;i<256;i++){const a=U.lift(k,C.filter((_,j)=>i>>j&1));check(U.decode(k,2,a.raw),"cnf-"+k+"-"+i,true);}
 let seed=0xD7B231;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<100;i++){
  const k=3+i%5,F=[];for(let j=0;j<1+i%9;j++){
   const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b),mask=rand()>>>16;
   F.push(factor(h,z=>!!(mask>>z.reduce((a,b)=>2*a+b,0)&1)));
  }
  check({k,m:2,F},"mixed-"+i,i<40);
 }
 for(const k of [6,8,10,12,16]){const d=R.residualBarrier(U,k),r=check(d,"parity-barrier",k===6);ok(r.kind==="contradiction"&&r.used==="0","parity");rows.push(r);
  if(k===6){const a=A.eliminate(d),bad=x=>{let failed=false;try{V.verify(d,x);}catch{failed=true;}ok(failed,"tamper");stats.tamperRejected++;};bad({...a,ops:a.ops.slice(1)});bad({...a,contradiction:0});bad({...a,rows:a.rows.map((x,i)=>i?x:{...x,rhs:x.rhs^1})});}
 }
 // Pure affine SAT with arbitrary k, nontrivial lex order.
 for(const k of [3,6,9]){const d={k,m:2,F:Array.from({length:k-2},(_,i)=>factor([i,i+1,i+2],z=>(z[0]^z[1]^z[2])===1))};rows.push(check(d,"affine-chain",k<=6));}
 // Non-affine factor's support expands to four free coordinates.
 {const d={k:6,m:2,F:[factor([0,1,4],z=>(z[0]^z[1])===z[2]),factor([2,3,5],z=>(z[0]^z[1])===z[2]),factor([4,5],z=>z[0]+z[1]<=1)]};const r=check(d,"wide-mixed",true);ok(r.kind==="wide-fallback"&&r.models===12,"wide");rows.push(r);}
 // Narrow mixed rewrite preserves genuine constraints after substitution.
 {const d={k:4,m:2,F:[factor([0,1,3],z=>(z[0]^z[1])===z[2]),factor([2,3],z=>z[0]+z[1]<=1)]};const r=check(d,"narrow-mixed",true);ok(r.kind==="narrow"&&r.models===6,"narrow");rows.push(r);}
 for(const k of [5,6,8,10,12,16]){const d=A.barrier(U,k),r=check(d,"dense-NAE",k===5);ok(r.kind==="narrow"&&r.free===k&&r.equations===0&&r.used===String(2n**BigInt(k))&&U.gac(d).deletions===0,"NAE");rows.push(r);}
 // Larger pure affine examples without exponential oracle enumeration.
 // The first two ranks determine the rest by a recurrence, giving
 // exactly four solutions. An opposite copy of an equation refutes all.
 const large=[];
 for(const k of [32,64,128]){
  const F=Array.from({length:k-2},(_,i)=>factor([i,i+1,i+2],z=>(z[0]^z[1]^z[2])===1)),d={k,m:2,F},s=A.solve(U,d),v=V.verify(d,s.r.a),z=[0,0];
  while(z.length<k)z.push(1^z[z.length-1]^z[z.length-2]);
  ok(s.status==="SAT"&&s.used===0n&&s.r.a.free.join()==="0,1"&&s.z.join()===z.join(),"large affine");
  const bad={...d,F:[...F,factor([0,1,2],z=>(z[0]^z[1]^z[2])===0)]},b=A.solve(U,bad),bv=V.verify(bad,b.r.a);
  ok(b.status==="UNSAT"&&b.used===0n&&bv.contradiction,"large contradiction");
  large.push({k,free:s.r.a.free.length,equations:v.equations,contradictionOps:bv.ops,used:String(s.used),witness:s.z.join("")});
 }
 return {stats,rows,large,resources:{logical:J.ins.length,...N0.stats}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_variable_rank_reduction.js"),require("./f038_rex_variable_rank_quotient.js"),require("./f038_rex_variable_relational_closure.js"),require("./f038_rex_variable_affine_closure.js"),require("./f038_rex_variable_affine_certificate.js"),require("./f038_rex_variable_rank_worker.js"),require("./f038_rex_width_three_local_motion_compiler.js"),require("./f038_rex_width_three_local_motion_clock.js"),require("./f038_rex_width_two_quotient.js"))));
