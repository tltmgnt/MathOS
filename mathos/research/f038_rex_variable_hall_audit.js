// D7E: exhaustive small-model oracle, Hall proofs, full predecessor integration and physical replay.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,P,K,F,Min){
 const ok=(b,s)=>{if(!b)throw Error(s);},stats={cases:0,models:0,sat:0,unsat:0,hallRefuted:0,localMasks:0,tamperRejected:0},rows=[];
 const factor=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((a,b,i)=>a+(b<<i),0))&1).map(z=>z.join()))});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 function check(d){
  const m=models(d),h=H.hall(C,d);stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;
  if(h.kind==="hall"){ok(!m.length&&HV.verify(d,h),"Hall soundness");stats.hallRefuted++;}
  return h;
 }
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]});stats.localMasks++;}
 for(let k of [2,3])for(let mask=0;mask<256;mask++){
  const F=[];
  if(k===2){const scopes=[[0],[0],[1],[1],[0,1],[0,1],[0,1],[0,1]];for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor(scopes[j],((1<<(2**scopes[j].length))-1)^(1<<(j<4?j%2:j-4))));}
  else for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor([0,1,2],255^(1<<j)));
  check({k,m:2,F});
 }
 let seed=0xd7e024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}check({k,m:2,F});}
 function graph(E){
  let k=0;const opts=E.map(row=>row.map(h=>({h,x:k++}))),F=opts.map(row=>factor(row.map(a=>a.x),(1<<(2**row.length))-2));
  for(let i=0;i<opts.length;i++)for(let j=0;j<i;j++)for(const x of opts[i])for(const y of opts[j])if(x.h===y.h)F.push(factor([y.x,x.x],7));
  return {k,m:2,F};
 }
 const sparse=graph([[0,1],[0,1],[0,1],[2,3,4]]),small=graph([[0,1],[0,1],[0,1]]),sat=graph([[0,1],[0,1]]);
 const flip=d=>({...d,F:d.F.map(f=>({h:f.h.slice(),S:new Set([...f.S].map(t=>t.split(",").map(x=>1-Number(x)).join()))}))});
 const sparseCert=check(sparse),negative=check(flip(small));ok(sparseCert.kind==="hall"&&sparseCert.groups.length===3&&sparseCert.holes.length===2&&negative.kind==="hall"&&negative.sign===-1&&check(small).kind==="hall"&&check(sat).kind==="unknown","named");
 for(let mask=0;mask<512;mask++){
  const E=Array.from({length:3},(_,i)=>[0,1,2].filter(j=>mask>>(3*i+j)&1));if(E.some(x=>!x.length))continue;
  const d=graph(E),h=check(d),m=models(d);ok((h.kind==="hall")===!m.length,"graph completeness");
 }
 for(const n of [3,5,6,8,12,20]){
  const d=D.php(U,n),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const h=H.hall(C,a.d);
  ok(!p.contradiction&&a.a.rows.length===0&&h.kind==="hall"&&HV.verify(a.d,h)&&h.groups.length===n+1&&h.holes.length===n,"large Hall");
  rows.push({n,k:d.k,factors:d.F.length,groups:h.groups.length,holes:h.holes.length,proof:h.groups.reduce((s,g)=>s+g.proof.length,0),exclusions:h.exclusions.length,steps:h.steps,edgeChecks:h.edgeChecks,searchEdges:h.searchEdges});
 }
 function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
 reject(()=>HV.verify(sparse,{...sparseCert,groups:sparseCert.groups.slice(1)}));
 reject(()=>HV.verify(sparse,{...sparseCert,holes:sparseCert.holes.map((h,i)=>i?h:h.slice(1))}));
 reject(()=>HV.verify(sparse,{...sparseCert,exclusions:sparseCert.exclusions.slice(1)}));
 reject(()=>HV.verify(sparse,{...sparseCert,groups:sparseCert.groups.map((g,i)=>i?g:{...g,proof:[{...g.proof[0],f:-1}]})}));
 reject(()=>HV.verify(sparse,{...sparseCert,holes:[...sparseCert.holes,sparseCert.holes[0]]}));
 reject(()=>HV.verify(sparse,{...sparseCert,groups:sparseCert.groups.map((g,i)=>i?g:{...g,options:g.options.slice(1)})}));
 const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0},physical=[];
 for(const [name,d,compare] of [["small",small,true],["sparse",sparse,true],["sat",sat,true],["PHP5",D.php(U,5),false],["PHP20",D.php(U,20),false]]){
  const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=H.reduce(C,V,D,T,HV,a.d,2000000);
  const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
  ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical replay");
  const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
  if(compare){const os=P.stream(U,a.d),old=P.run(N,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;
   ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]??null)&&(y?.join()??null)===(m[0]??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical compare");row.oldPhysical=old.t;}
  else ok(b.status==="UNSAT"&&b.z===null&&r.cert.kind==="hall","large physical");
  physical.push(row);
 }
 const barrier=D.php(U,6);barrier.F.push({h:[0,7],S:new Set(["0,0","0,1","1,0"])});
 const p=R.reduce(U,Q,barrier),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=H.reduce(C,V,D,T,HV,a.d,2000000);
 ok(!p.contradiction&&p.d.k===63&&a.a.free.length===63&&a.a.rows.length===0&&r.hall.kind==="unknown"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&!r.contradiction&&r.d===a.d,"surviving barrier");
 return {stats,rows,sparse:{totalGroups:4,totalHoles:5,coreGroups:sparseCert.groups.length,coreHoles:sparseCert.holes.length},physical,barrier:{k:barrier.k,factors:barrier.F.length,free:a.a.free.length,equations:a.a.rows.length,hall:r.hall,first:r.first,final:r.cert},resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:8,cutoffs:5}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'))));
