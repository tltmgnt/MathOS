// D7I: exact projected model oracle, implication certificates and physical replay.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,I,IV,P,K,F,Min,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const factor=c=>({h:c.map(x=>Math.abs(x)-1),S:new Set([...U.tuples(2,c.length)].filter(z=>c.some((x,i)=>x>0?z[i]:!z[i])).map(z=>z.join()))});
 const relation=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())));
 const bin=(k,cs)=>({k,m:2,F:cs.map(factor)});
 const cycle=bin(5,[[-1,2],[-2,3],[-3,-1],[1,4],[-4,5],[-5,1]]);
 const sat=bin(6,[[-1,2],[-2,3],[-3,-4],[1,4,6],[-4,5]]);
 let seed=0xd7c024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const sign=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 function fixture(n,len,flip=false){
  const original=D.php(U,n);let k=original.k,F=[];
  for(const f of original.F){
   if(f.h.length!==2){F.push(f);continue;}
   const [x,y]=f.h;let last=x;
   for(let j=1;j<len;j++){const u=k++;F.push(factor([-(last+1),u+1]));last=u;}
   F.push(factor([-(last+1),-(y+1)]));
  }
  const d={k,m:2,F};return flip?N.transform(d,sign(k)).d:d;
 }
 function gadget(n){
  const original=D.php(U,n);let k=original.k,F=[];
  for(const f of original.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h,u=k++,v=k++;
   F.push(factor([-(x+1),-(y+1),u+1]),factor([-(x+1),-(u+1),v+1]),factor([-(y+1),-(u+1),-(v+1)]));
  }return {k,m:2,F};
 }
 if(section==="oracle"){
  const stats={cases:0,localTypes:0,binaryCases:0,mixedCases:0,originalModels:0,sat:0,unsat:0,emptyFactors:0,binaryContradictions:0,views:0,projectedModels:0,pathClauses:0,derivedClauses:0,pathSteps:0,oldHall:0,newCertified:0,addedCertified:0,tamperRejected:0};
  const kinds={};function check(d){
   const m=models(d),p=I.closure(C,d);
   stats.cases++;stats.originalModels+=m.length;stats[m.length?"sat":"unsat"]++;
   const binary=d.F.every(f=>f.h.length<=2);stats[binary?"binaryCases":"mixedCases"]++;
   if(p.kind==="empty-factor"){stats.emptyFactors++;ok(!m.length&&IV.verify(NV,HV,d,p),"empty");}
   else if(p.kind==="binary-contradiction"){stats.binaryContradictions++;ok(!m.length&&IV.verify(NV,HV,d,p),"cycle");}
   else{
    stats.views++;const view=IV.reconstruct(d,p),vm=models(view).map(x=>x.join()).sort(),pm=[...new Set(m.map(z=>p.anchors.map(x=>z[x]).join()))].sort();
    ok(JSON.stringify(vm)===JSON.stringify(pm),"exact projection");
    ok(JSON.stringify(view.F.map(f=>[f.h,[...f.S].sort()]))===JSON.stringify(p.d.F.map(f=>[f.h,[...f.S].sort()])),"independent view");
    if(binary)ok(m.length>0,"2-CNF completeness");
    stats.projectedModels+=vm.length;stats.pathClauses+=p.paths.length;stats.derivedClauses+=p.metrics.derived;stats.pathSteps+=p.paths.reduce((s,r)=>s+r.path.steps.length,0);
   }
   const old=N.normalize(G,B,H,C,d),r=I.infer(N,G,B,H,C,d);
   if(old.kind!=="unknown"){stats.oldHall++;ok(r.kind!=="unknown","inherited retained");}
   if(r.kind!=="unknown"){ok(!m.length&&IV.verify(NV,HV,d,r),"inference soundness");stats.newCertified++;if(old.kind==="unknown")stats.addedCertified++;}
   kinds[r.kind]=(kinds[r.kind]||0)+1;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[relation(Array.from({length:n},(_,i)=>i),mask)]});stats.localTypes++;}
  const all=[[1],[-1],[2],[-2],[1,2],[-1,2],[1,-2],[-1,-2]];
  for(let m=0;m<256;m++)check(bin(2,all.filter((_,i)=>m>>i&1)));
  for(let t=0;t<256;t++){const k=3+t%2,cs=[];for(let j=0;j<2+t%13;j++){let a=1+(rand()>>>16)%k,b=1+(rand()>>>16)%k;if(a===b)b=b%k+1;cs.push([(rand()>>>31)?a:-a,(rand()>>>31)?b:-b]);}check(bin(k,cs));}
  for(let t=0;t<384;t++){const k=4+t%4,F=[relation([0,1,2],1+(rand()>>>16)%254)];for(let j=0;j<2+t%9;j++){const a=(rand()>>>16)%k,b=(a+1+(rand()>>>16)%(k-1))%k;F.push(relation([a,b],1+(rand()>>>16)%14));}check({k,m:2,F});}
  for(let s=0;s<64;s++)check(N.transform(sat,Array.from({length:6},(_,i)=>s>>i&1)).d);
  check({k:1,m:2,F:[relation([],0)]});check({k:1,m:2,F:[relation([],1)]});
  const cc=I.closure(C,cycle),p=I.closure(C,sat),hidden=fixture(3,2),hc=I.infer(N,G,B,H,C,hidden);
  ok(cc.kind==="binary-contradiction"&&p.kind==="view"&&p.paths.length>0&&hc.kind==="reach-hall","named fixtures");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  reject(()=>IV.verify(NV,HV,cycle,{...cc,paths:[cc.paths[0],cc.paths[0]]}));
  reject(()=>IV.checkPath(cycle,{...cc.paths[0],steps:cc.paths[0].steps.map((s,i)=>i?s:{...s,f:999})}));
  reject(()=>IV.checkPath(cycle,{...cc.paths[0],to:2}));
  reject(()=>IV.reconstruct(sat,{...p,anchors:p.anchors.slice(1)}));
  reject(()=>IV.reconstruct(sat,{...p,paths:p.paths.map((r,i)=>i?r:{...r,c:[-r.c[0]]})}));
  reject(()=>IV.verify(NV,HV,hidden,{...hc,proof:{...hc.proof,hall:{...hc.proof.hall,exclusions:hc.proof.hall.exclusions.slice(1)}}}));
  return {stats,kinds};
 }
 if(section==="large"||section==="largest"){
  const rows=[],list=section==="largest"?[[20,2,false]]:[[3,2,false],[6,2,false],[6,3,true],[8,2,false],[12,2,true]];
  for(const [n,len,flip] of list){const d=fixture(n,len,flip),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
   const c=I.infer(N,G,B,H,C,a.d);
   ok(!p.contradiction&&a.a.free.length===d.k&&a.a.rows.length===0&&c.kind==="reach-hall"&&IV.verify(NV,HV,a.d,c),"large");
   rows.push({n,len,flip,k:d.k,factors:d.F.length,free:a.a.free.length,proof:c.proof.kind,groups:c.proof.hall.groups.length,holes:c.proof.hall.holes.length,groupAxioms:c.proof.hall.groups.reduce((s,g)=>s+g.proof.length,0),exclusions:c.proof.hall.exclusions.length,paths:c.paths.length,metrics:c.metrics});
  }return {rows};
 }
 if(section==="physical"){
  const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),min={...M,...N0},physical=[];
  for(const [name,d,compare] of [["binary-cycle",cycle,true],["mixed-sat",sat,true],["PHP6-path2",fixture(6,2),false],["PHP6-path3-signed",fixture(6,3,true),false]]){
   const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=I.reduce(N,G,B,H,C,V,D,T,HV,NV,IV,a.d,2000000);
   const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(min,ns,b.t),cut=P.run(min,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
   ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
   const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
   if(compare){const os=P.stream(U,a.d),old=P.run(min,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;
    ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]?.join()??null)&&(y?.join()??null)===(m[0]?.join()??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical compare");row.oldPhysical=old.t;if(y)row.witness=y.join();
   }else ok(b.status==="UNSAT"&&b.z===null&&r.cert.kind==="reach-hall","large physical");physical.push(row);
  }return {physical,resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:6,cutoffs:4}};
 }
 if(section==="barrier"){
  const d=gadget(6),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
  const r=I.reduce(N,G,B,H,C,V,D,T,HV,NV,IV,a.d,2000000);
  ok(!p.contradiction&&a.a.free.length===315&&a.a.rows.length===0&&r.implication.kind==="unknown"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&r.d===a.d&&!r.contradiction,"new barrier");
  return {barrier:{k:d.k,factors:d.F.length,free:a.a.free.length,equations:a.a.rows.length,implication:r.implication,first:r.first,final:r.cert}};
 }
 throw Error("unknown audit section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),process.argv[2]||'oracle')));
