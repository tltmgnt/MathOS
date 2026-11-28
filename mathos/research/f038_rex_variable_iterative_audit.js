// D7K: stratified oracle, guarded families, linear NAE fixed-point obstruction and replay.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,I,IV,P,PV,J,JV,W,K,F,Min,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const factor=c=>({h:c.map(x=>Math.abs(x)-1),S:new Set([...U.tuples(2,c.length)].filter(z=>c.some((x,i)=>x>0?z[i]:!z[i])).map(z=>z.join()))});
 const bin=(k,cs)=>({k,m:2,F:cs.map(factor)});
 const relation=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 function fixture(n,flip=false){
  const d=D.php(U,n);let k=d.k,F=[];
  for(const f of d.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h.map(x=>x+1),u=++k,a=++k,b=++k,c=++k,e=++k,g=++k;
   F.push(factor([-x,-y,u]));for(const l of [[-a,b],[-b,c],[-c,-a],[a,e],[-e,g],[-g,a]])F.push(factor([-u,...l]));
  }const e={k,m:2,F};return flip?N.transform(e,Array.from({length:k},(_,i)=>+(i*17%7<3))).d:e;
 }
 const local=bin(8,[[-1,-2,3],[-3,-4,5],[-3,-5,6],[-3,-6,-4],[-3,4,7],[-3,-7,8],[-3,-8,4]]);
 let seed=0xd7e024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 if(section==="oracle"){
  const stats={cases:0,models:0,sat:0,unsat:0,localTypes:0,views:0,conflicts:0,records:0,nonemptyRounds:0,maxRounds:0,oldCertified:0,newCertified:0,addedCertified:0,tamperRejected:0};
  const kinds={};
  function check(d){
   const m=models(d),r=J.close(P,C,I,d),v=JV.reconstruct(PV,d,r.rounds);
   stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;stats.nonemptyRounds+=r.rounds.length;stats.maxRounds=Math.max(stats.maxRounds,r.rounds.length);stats.records+=r.rounds.reduce((s,x)=>s+x.length,0);
   ok(JSON.stringify(models(v))===JSON.stringify(m),"strata model preservation");
   if(r.kind==="conflict"){stats.conflicts++;ok(!m.length&&JV.verify(PV,IV,NV,HV,d,r),"conflict");}
   else{stats.views++;ok(r.status==="fixed-point"&&JSON.stringify(models(r.d))===JSON.stringify(m),"fixed point");
    const p=P.discover(C,I,v);ok(p.kind==="view"&&p.status==="complete"&&!p.records.length,"fixed point repeat");}
   const old=P.infer(N,G,B,H,C,I,d),h=J.infer(N,G,B,H,C,I,P,d);
   if(old.kind!=="unknown"){stats.oldCertified++;ok(h.kind!=="unknown","inherited");}
   if(h.kind!=="unknown"){stats.newCertified++;ok(!m.length&&JV.verify(PV,IV,NV,HV,d,h),"soundness");if(old.kind==="unknown")stats.addedCertified++;}
   kinds[h.kind]=(kinds[h.kind]||0)+1;
  }
  for(let n=1;n<=3;n++)for(let m=0;m<2**(2**n);m++){check({k:n,m:2,F:[relation(Array.from({length:n},(_,i)=>i),m)]});stats.localTypes++;}
  const all=[[1],[-1],[2],[-2],[1,2],[-1,2],[1,-2],[-1,-2]];
  for(let m=0;m<256;m++)check(bin(2,all.filter((_,i)=>m>>i&1)));
  for(let t=0;t<192;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b);F.push(relation(h,rand()>>>16));}check({k,m:2,F});}
  for(let s=0;s<256;s++)check(N.transform(local,Array.from({length:8},(_,i)=>s>>i&1)).d);
  const r=J.close(P,C,I,local),lim=J.close(P,C,I,local,2000000,1),budget=J.close(P,C,I,local,1),zero=J.close(P,C,I,local,0,0);
  ok(r.kind==="view"&&r.rounds.length===2&&r.rounds[1].some(x=>x.c.join()==="-1,-2")&&lim.status==="round-limit"&&budget.status==="budget"&&zero.status==="round-limit","limits");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  reject(()=>JV.reconstruct(PV,local,r.rounds.slice().reverse()));
  reject(()=>JV.reconstruct(PV,local,[...r.rounds,r.rounds[0]]));
  reject(()=>JV.reconstruct(PV,local,[r.rounds.flat()]));
  reject(()=>JV.reconstruct(PV,local,[[{...r.rounds[0][0],trace:{...r.rounds[0][0].trace,conflict:{...r.rounds[0][0].trace.conflict,f:999}}}]]));
  reject(()=>JV.reconstruct(PV,local,[[]]));
  return {stats,kinds,local:{models:models(local).length,rounds:r.rounds.map(x=>x.length),work:r.work,limit:lim.status,budget:budget.status,zero:zero.status}};
 }
 if(section==="large"||section==="largest"){
  const rows=[],list=section==="largest"?[[20,false,8000000]]:[[3,false,2000000],[6,false,2000000],[6,true,2000000],[8,false,2000000],[12,true,2000000]];
  for(const [n,flip,budget] of list){const d=fixture(n,flip),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=J.infer(N,G,B,H,C,I,P,a.d,budget);
   ok(!p.contradiction&&a.a.free.length===d.k&&a.a.rows.length===0&&r.kind==="structural"&&JV.verify(PV,IV,NV,HV,a.d,r),"large");
   rows.push({n,flip,budget,k:d.k,factors:d.F.length,rounds:r.rounds.map(x=>x.length),work:r.work,metrics:r.metrics,proof:r.proof.proof.kind,groups:r.proof.proof.hall.groups.length,holes:r.proof.proof.hall.holes.length});
  }return {rows};
 }
 if(section==="barrier"){
  const q=7,k=3*q,fs=[],S=["0,0,1","0,1,0","0,1,1","1,0,0","1,0,1","1,1,0"],add=h=>fs.push({h,S:new Set(S)});
  for(let x=0;x<q;x++)add([3*x,3*x+1,3*x+2]);
  for(let x=0;x<q;x++)for(let y=x+1;y<q;y++)for(let i=0;i<3;i++)add([3*x+i,3*y+i,3*(((x+y)*((q+1)/2))%q)+(i+1)%3]);
  const pairs=new Set();for(const f of fs)for(let i=0;i<3;i++)for(let j=0;j<i;j++){const key=[f.h[i],f.h[j]].sort((a,b)=>a-b).join();ok(!pairs.has(key),"linear");pairs.add(key);}
  ok(pairs.size===k*(k-1)/2,"Steiner coverage");
  const d={k,m:2,F:fs},p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=J.reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,a.d);
  ok(a.a.rows.length===0&&a.a.free.length===k&&r.iterative.kind==="unknown"&&r.iterative.status==="fixed-point"&&r.iterative.rounds===0&&r.first.reason==="budget"&&r.cert.kind==="tree"&&T.verifyTree(a.d,r.cert),"structural obstruction and tree fallback");
  const min=Math.floor(k/2)*(Math.floor(k/2)-1)/2+Math.ceil(k/2)*(Math.ceil(k/2)-1)/2;ok(min>fs.length,"counting contradiction");
  return {barrier:{k,factors:fs.length,pairs:pairs.size,minMonochromaticPairs:min,iterative:r.iterative,first:r.first,tree:{work:r.cert.work,nodes:r.cert.nodes,leaves:r.cert.leaves,splits:r.cert.splits,units:r.cert.units}}};
 }
 if(section==="physical"){
  const J0=W.machine(),M=W.singleExit(K.compile(J0)),N0=Min.refine(M),min={...M,...N0},physical=[];
  for(const [name,d,compare] of [["local-sat",local,true],["PHP3-guarded",fixture(3),false],["PHP6-guarded",fixture(6),false],["PHP6-signed",fixture(6,true),false]]){
   const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=J.reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,a.d);
   const ns=W.stream(U,r.d),b=W.run(M,ns,300000000),c=W.run(min,ns,b.t),cut=W.run(min,ns,b.t-1),clock=F.count(J0,["",ns],M.codes);
   ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
   const row={name,status:b.status,kind:r.cert.kind,transitions:b.t,stream:ns.length};
   if(compare){const os=W.stream(U,a.d),old=W.run(min,os,300000000),oc=F.count(J0,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;ok(old.status===b.status&&b.status==="SAT"&&x.join()===m[0]&&y.join()===m[0]&&old.t===oc.clock&&old.encoded===oc.encoded,"witness");row.oldPhysical=old.t;row.witness=y.join();}
   else ok(b.status==="UNSAT"&&r.cert.kind==="structural","large physical");physical.push(row);
  }return {physical,resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:5,cutoffs:4}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_conditional_propagation.js'),require('./f038_rex_variable_conditional_certificate.js'),require('./f038_rex_variable_iterative_consequences.js'),require('./f038_rex_variable_iterative_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),process.argv[2]||'oracle')));
