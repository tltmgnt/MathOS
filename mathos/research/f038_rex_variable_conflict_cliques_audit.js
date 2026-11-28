// D7F: independent Hall checks, noise/relabeling oracle and physical replay.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,P,K,F,Min){
 const ok=(b,s)=>{if(!b)throw Error(s);},stats={cases:0,models:0,sat:0,unsat:0,oldHall:0,robustHall:0,addedHall:0,localMasks:0,cleanGraphs:0,noisyGraphs:0,greedyRecovered:0,tamperRejected:0};
 const factor=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((a,b,i)=>a+(b<<i),0))&1).map(z=>z.join()))});
 const excl=h=>({h,S:new Set(["0,0","0,1","1,0"])});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 function check(d){
  const m=models(d),old=H.hall(C,d),h=B.robust(H,C,d);
  stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;
  if(old.kind==="hall"){stats.oldHall++;ok(h.kind==="hall"&&HV.verify(d,old),"baseline");}
  if(h.kind==="hall"){ok(!m.length&&HV.verify(d,h),"soundness");stats.robustHall++;if(old.kind!=="hall")stats.addedHall++;if(h.strategy.startsWith("greedy"))stats.greedyRecovered++;}
  return h;
 }
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]});stats.localMasks++;}
 for(let k of [2,3])for(let mask=0;mask<256;mask++){
  const F=[];
  if(k===2){const scopes=[[0],[0],[1],[1],[0,1],[0,1],[0,1],[0,1]];for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor(scopes[j],((1<<(2**scopes[j].length))-1)^(1<<(j<4?j%2:j-4))));}
  else for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor([0,1,2],255^(1<<j)));
  check({k,m:2,F});
 }
 let seed=0xd7f024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}check({k,m:2,F});}
 function graph(E){
  let k=0;const opts=E.map(row=>row.map(h=>({h,x:k++}))),F=opts.map(row=>factor(row.map(a=>a.x),(1<<(2**row.length))-2));
  for(let i=0;i<opts.length;i++)for(let j=0;j<i;j++)for(const x of opts[i])for(const y of opts[j])if(x.h===y.h)F.push(excl([y.x,x.x]));
  return {k,m:2,F};
 }
 for(let mask=0;mask<512;mask++){
  const E=Array.from({length:3},(_,i)=>[0,1,2].filter(j=>mask>>(3*i+j)&1));if(E.some(x=>!x.length))continue;
  const d=graph(E),h=check(d);ok((h.kind==="hall")===!models(d).length,"clean graphs");stats.cleanGraphs++;
 }
 const cross=[];for(let i=0;i<6;i++)for(let j=i+1;j<6;j++)if((i>>1)!==(j>>1)&&i%2!==j%2)cross.push([i,j]);
 const strategies={};let greedyFixture=null;
 for(let mask=0;mask<64;mask++){
  const d=graph([[0,1],[0,1],[0,1]]);for(let i=0;i<6;i++)if(mask>>i&1)d.F.push(excl(cross[i]));
  const h=check(d);ok(h.kind==="hall","noisy three/two");stats.noisyGraphs++;strategies[h.strategy]=(strategies[h.strategy]||0)+1;
  if(mask===3)greedyFixture=d;
 }
 // Noise on satisfiable or unsatisfiable small matching graphs; compare to actual Boolean models.
 for(let t=0;t<128;t++){
  const E=Array.from({length:3},()=>{const m=1+rand()%7;return [0,1,2].filter(j=>m>>j&1);});
  const d=graph(E),owner=E.flatMap((row,i)=>row.map(()=>i));
  for(let i=0;i<d.k;i++)for(let j=i+1;j<d.k;j++)if(owner[i]!==owner[j]&&(rand()>>>28)<3)d.F.push(excl([i,j]));
  check(d);stats.noisyGraphs++;
 }
 const flip=d=>({...d,F:d.F.map(f=>({h:f.h.slice(),S:new Set([...f.S].map(t=>t.split(",").map(x=>1-Number(x)).join()))}))});
 const neg=check(flip(greedyFixture));ok(neg.kind==="hall"&&neg.sign===-1,"negative polarity");
 function noise(n,type){
  const d=D.php(U,n),pairs=[];
  if(type==="bridge")pairs.push([0,n+1]);
  if(type==="triangle")pairs.push([0,n+1],[0,2*n+1]);
  if(type==="cycle")for(let i=0;i<n;i++)pairs.push([i,n+(i+1)%n]);
  if(type==="many")for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(i!==j)pairs.push([i,n+j]);
  if(type==="ambiguous"){const aux=n*(n+1);d.F.push({h:[aux,2],S:new Set(["0,0","0,1","1,1"])});}
  for(const h of pairs)d.F.push(excl(h));return d;
 }
 const rows=[];
 for(const [n,type] of [[3,"bridge"],[5,"bridge"],[6,"bridge"],[6,"triangle"],[6,"cycle"],[6,"many"],[8,"cycle"],[12,"cycle"],[20,"bridge"]]){
  const d=noise(n,type),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
  const old=H.hall(C,a.d),h=B.robust(H,C,a.d);
  ok(!p.contradiction&&a.a.rows.length===0&&a.a.free.length===d.k&&old.kind==="unknown"&&h.kind==="hall"&&HV.verify(a.d,h)&&h.groups.length===n+1&&h.holes.length===n,"large noisy");
  rows.push({n,type,k:d.k,factors:d.F.length,strategy:h.strategy,attempts:h.attempts,groups:h.groups.length,holes:h.holes.length,exclusions:h.exclusions.length,metrics:h.metrics});
 }
 let relabelled=0;
 for(let t=0;t<32;t++){
  const d=noise(6,"bridge"),perm=Array.from({length:d.k},(_,i)=>i);
  for(let i=perm.length-1;i>0;i--){const j=rand()%(i+1);[perm[i],perm[j]]=[perm[j],perm[i]];}
  const e={...d,F:d.F.map(f=>({h:f.h.map(x=>perm[x]).reverse(),S:new Set([...f.S].map(s=>s.split(",").reverse().join()))})).reverse()};
  const h=B.robust(H,C,e);ok(h.kind==="hall"&&HV.verify(e,h),"relabel");relabelled++;
 }
 const small=greedyFixture,cert=B.robust(H,C,small);
 function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
 reject(()=>HV.verify(small,{...cert,holes:cert.holes.map((h,i)=>i?h:h.slice(1))}));
 reject(()=>HV.verify(small,{...cert,exclusions:cert.exclusions.slice(1)}));
 reject(()=>HV.verify(small,{...cert,groups:cert.groups.map((g,i)=>i?g:{...g,proof:[{...g.proof[0],f:-1}]})}));
 reject(()=>HV.verify(small,{...cert,holes:[...cert.holes,cert.holes[0]]}));
 // Malformed candidate proposals must be ignored, not turned into certificates.
 const malformed=H.hall(C,noise(6,"bridge"),function*(){yield {strategy:"missing",holes:[]};yield {strategy:"duplicate",holes:[[1,1]]};});
 ok(malformed.kind==="unknown","invalid proposals");
 const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),N={...M,...N0},physical=[];
 const sat=graph([[0,1],[0,1]]);sat.F.push(excl([0,3]));
 for(const [name,d,compare] of [["greedy-small",small,true],["noisy-sat",sat,true],["PHP6-bridge",noise(6,"bridge"),false],["PHP20-bridge",noise(20,"bridge"),false]]){
  const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=B.reduce(H,C,V,D,T,HV,a.d,2000000);
  const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(N,ns,b.t),cut=P.run(N,ns,b.t-1),clock=F.count(J,["",ns],M.codes);
  ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
  const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
  if(compare){const os=P.stream(U,a.d),old=P.run(N,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;
   ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]??null)&&(y?.join()??null)===(m[0]??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical compare");row.oldPhysical=old.t;}
  else ok(b.status==="UNSAT"&&b.z===null&&r.cert.kind==="hall","large physical");
  physical.push(row);
 }
 const barrier=noise(6,"ambiguous"),p=R.reduce(U,Q,barrier),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
 const r=B.reduce(H,C,V,D,T,HV,a.d,2000000);
 ok(!p.contradiction&&p.d.k===63&&a.a.free.length===63&&a.a.rows.length===0&&r.hall.kind==="unknown"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&!r.contradiction&&r.d===a.d,"barrier");
 return {stats,strategies,relabelled,rows,physical,barrier:{k:barrier.k,factors:barrier.F.length,free:a.a.free.length,equations:a.a.rows.length,hall:r.hall,first:r.first,final:r.cert},resources:{states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:6,cutoffs:4}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'))));
