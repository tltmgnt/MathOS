// D7J: sectioned model preservation, conditional traces, nested Hall and residual policy audit.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,I,IV,P,PV,W,K,F,Min,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const factor=c=>({h:c.map(x=>Math.abs(x)-1),S:new Set([...U.tuples(2,c.length)].filter(z=>c.some((x,i)=>x>0?z[i]:!z[i])).map(z=>z.join()))});
 const relation=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 const bin=(k,cs)=>({k,m:2,F:cs.map(factor)});
 function fixture(n,flip=false,guarded=false){
  const d=D.php(U,n);let k=d.k,F=[];
  for(const f of d.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h.map(x=>x+1);
   if(!guarded){const u=++k,v=++k;F.push(factor([-x,-y,u]),factor([-x,-u,v]),factor([-y,-u,-v]));}
   else{const u=++k,a=++k,b=++k,c=++k,e=++k,g=++k;F.push(factor([-x,-y,u]));for(const l of [[-a,b],[-b,c],[-c,-a],[a,e],[-e,g],[-g,a]])F.push(factor([-u,...l]));}
  }const e={k,m:2,F};return flip?N.transform(e,Array.from({length:k},(_,i)=>+(i*17%7<3))).d:e;
 }
 const local=bin(4,[[-1,-2,3],[-1,-3,4],[-2,-3,-4]]);
 let seed=0xd7d024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 if(section==="oracle"){
  const stats={cases:0,localTypes:0,models:0,sat:0,unsat:0,views:0,conflicts:0,derived:0,oldCertified:0,newCertified:0,addedCertified:0,tamperRejected:0};const kinds={};
  function check(d){
   const m=models(d),p=P.discover(C,I,d);
   stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;
   if(p.kind==="conflict"){ok(!m.length&&PV.checkTrace(d,p.trace),"conflict");stats.conflicts++;}
   else{const e=PV.reconstruct(d,p.records);ok(JSON.stringify(models(e))===JSON.stringify(m)&&JSON.stringify(models(p.d))===JSON.stringify(m),"exact models");stats.views++;stats.derived+=p.records.length;}
   const old=I.infer(N,G,B,H,C,d),r=P.infer(N,G,B,H,C,I,d);
   if(old.kind!=="unknown"){stats.oldCertified++;ok(r.kind==="inherited","inherited");}
   if(r.kind!=="unknown"){ok(!m.length&&PV.verify(IV,NV,HV,d,r),"soundness");stats.newCertified++;if(old.kind==="unknown")stats.addedCertified++;}
   kinds[r.kind]=(kinds[r.kind]||0)+1;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[relation(Array.from({length:n},(_,i)=>i),mask)]});stats.localTypes++;}
  const all=[[1],[-1],[2],[-2],[1,2],[-1,2],[1,-2],[-1,-2]];
  for(let m=0;m<256;m++)check(bin(2,all.filter((_,i)=>m>>i&1)));
  for(let t=0;t<384;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b);F.push(relation(h,rand()>>>16));}check({k,m:2,F});}
  for(let s=0;s<16;s++)check(N.transform(local,Array.from({length:4},(_,i)=>s>>i&1)).d);
  const p=P.discover(C,I,local),r=p.records.find(r=>r.c.join()==="-1,-2");ok(r&&PV.checkTrace(local,r.trace)&&models(local).length===10,"local");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  reject(()=>PV.checkTrace(local,{...r.trace,assume:[1,-1]}));
  reject(()=>PV.checkTrace(local,{...r.trace,steps:r.trace.steps.slice(1)}));
  reject(()=>PV.checkTrace(local,{...r.trace,conflict:{...r.trace.conflict,f:999}}));
  reject(()=>PV.reconstruct(local,[{...r,c:[1,-2]}]));
  reject(()=>PV.reconstruct(local,[r,r]));
  const limited=P.discover(C,I,local,1);ok(limited.status==="budget"&&limited.metrics.work===1&&JSON.stringify(models(limited.d))===JSON.stringify(models(local)),"budget");
  const guarded=bin(8,[[-1,-2,3],[-3,-4,5],[-3,-5,6],[-3,-6,-4],[-3,4,7],[-3,-7,8],[-3,-8,4]]);
  const gm=models(guarded),projection=[...new Set(gm.map(z=>z.split(",").slice(0,2).join(",")))].sort(),g=P.discover(C,I,guarded),g2=P.discover(C,I,g.d),ic=I.closure(C,g.d);
  ok(gm.length===96&&JSON.stringify(projection)===JSON.stringify(["0,0","0,1","1,0"])&&g.records.length===10&&!g.records.some(r=>r.c.join()==="-1,-2")&&ic.paths.some(r=>r.c.join()==="-3")&&g2.records.some(r=>r.c.join()==="-1,-2")&&JSON.stringify(models(PV.reconstruct(guarded,g.records)))===JSON.stringify(gm)&&JSON.stringify(models(PV.reconstruct(g.d,g2.records)))===JSON.stringify(gm),"guarded gadget");
  return {stats,kinds,limited:{status:limited.status,work:limited.metrics.work,records:limited.records.length},guarded:{models:gm.length,projection,first:g.records.length,second:g2.records.map(r=>r.c.join())}};
 }
 if(section==="large"||section==="largest"){
  const rows=[],list=section==="largest"?[[20,false,4000000]]:[[3,false,2000000],[6,false,2000000],[6,true,2000000],[8,false,2000000],[12,true,2000000]];
  for(const [n,flip,budget] of list){const d=fixture(n,flip),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=P.infer(N,G,B,H,C,I,a.d,budget);
   ok(!p.contradiction&&a.a.free.length===d.k&&a.a.rows.length===0&&r.kind==="conditional"&&PV.verify(IV,NV,HV,a.d,r),"large");
   rows.push({n,flip,budget,k:d.k,factors:d.F.length,free:a.a.free.length,records:r.records.length,traceSteps:r.records.reduce((s,x)=>s+x.trace.steps.length,0),proof:r.proof.proof.kind,groups:r.proof.proof.hall.groups.length,holes:r.proof.proof.hall.holes.length,metrics:r.metrics});
  }return {rows};
 }
 if(section==="physical"){
  const J=W.machine(),M=W.singleExit(K.compile(J)),N0=Min.refine(M),min={...M,...N0},physical=[];
  const small=bin(4,[[-1,-2,3],[-1,-3,4],[-2,-3,-4],[1],[2]]),sat=local;
  for(const [name,d,compare] of [["small-conflict",small,true],["gadget-sat",sat,true],["PHP6-gadget",fixture(6),false],["PHP6-signed",fixture(6,true),false]]){
   const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=P.reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,PV,a.d);
   const ns=W.stream(U,r.d),b=W.run(M,ns,300000000),c=W.run(min,ns,b.t),cut=W.run(min,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
   ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
   const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
   if(compare){const os=W.stream(U,a.d),old=W.run(min,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]??null)&&(y?.join()??null)===(m[0]??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical oracle");row.oldPhysical=old.t;if(y)row.witness=y.join();}
   else ok(b.status==="UNSAT"&&b.z===null&&r.cert.kind==="conditional","large physical");physical.push(row);
  }return {physical,resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:6,cutoffs:4}};
 }
 if(section==="barrier"){
  const d=fixture(6,false,true),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=P.reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,PV,a.d);
  ok(!p.contradiction&&a.a.free.length===819&&a.a.rows.length===0&&r.conditional.kind==="unknown"&&r.conditional.status==="complete"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&r.d===a.d&&!r.contradiction,"barrier");
  return {barrier:{k:d.k,factors:d.F.length,free:a.a.free.length,equations:a.a.rows.length,conditional:r.conditional,first:r.first,final:r.cert}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_conditional_propagation.js'),require('./f038_rex_variable_conditional_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),process.argv[2]||'oracle')));
