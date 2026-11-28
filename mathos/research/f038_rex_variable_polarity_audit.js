// D7H: sectioned exhaustive polarity and signed Hall audit.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,P,K,F,Min,section="all"){
 const ok=(b,s)=>{if(!b)throw Error(s);},stats={mapCases:0,mapModels:0,localTypes:0,oracleCases:0,oracleModels:0,sat:0,unsat:0,oldHall:0,newHall:0,addedHall:0,tamperRejected:0};
 const factor=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((a,b,i)=>a+(b<<i),0))&1).map(z=>z.join()))});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()))).map(z=>z.join());
 let seed=0xd7b024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 function mapCheck(d,s){const t=N.transform(d,s),m=models(d),actual=models(t.d).map(z=>t.expand(z.split(",").map(Number)).join()).sort();ok(NV.verifyMap(d,s,t.d)&&JSON.stringify(m.slice().sort())===JSON.stringify(actual),"model bijection");ok(NV.verifyMap(d,Array(d.k).fill(0),N.transform(t.d,s).d),"involution");stats.mapCases++;stats.mapModels+=m.length;return t.d;}
 function oracle(d){const m=models(d),old=G.alternative(B,H,C,d),r=N.normalize(G,B,H,C,d);stats.oracleCases++;stats.oracleModels+=m.length;stats[m.length?"sat":"unsat"]++;if(old.kind==="hall"){stats.oldHall++;ok(r.kind==="hall","inherited");}if(r.kind!=="unknown"){ok(!m.length&&NV.verify(HV,d,r),"signed soundness");stats.newHall++;if(old.kind!=="hall")stats.addedHall++;}}
 function graph(E){let k=0;const opts=E.map(row=>row.map(h=>({h,x:k++}))),F=opts.map(row=>factor(row.map(a=>a.x),(1<<(2**row.length))-2));for(let i=0;i<opts.length;i++)for(let j=0;j<i;j++)for(const x of opts[i])for(const y of opts[j])if(x.h===y.h)F.push(factor([y.x,x.x],7));return {k,m:2,F};}
 function fixture(n,type){const d=D.php(U,n),s=Array.from({length:d.k},(_,i)=>+(type==="first"?i<n*(n+1)&&i%n===0:type==="aux"?i>=n*(n+1)&&i%2===0:type==="occupancy"?i%3===0:(i*17+Math.floor(i/3))%7<3));return N.transform(d,s).d;}
 const out={};
 if(section==="all"||section==="oracle"){
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const d={k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]};stats.localTypes++;for(let s=0;s<2**n;s++)mapCheck(d,Array.from({length:n},(_,i)=>s>>i&1));}
  for(let i=0;i<128;i++){const k=3+i%4,F=[];for(let j=0;j<2+i%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}const d={k,m:2,F};oracle(mapCheck(d,Array.from({length:k},()=>rand()>>>31)));}
  for(let mask=0;mask<512;mask++){const E=Array.from({length:3},(_,i)=>[0,1,2].filter(j=>mask>>(3*i+j)&1));if(E.some(x=>!x.length))continue;const d=graph(E);oracle(mapCheck(d,Array.from({length:d.k},()=>rand()>>>31)));}
  for(const E of [[[0,1],[0,1],[0,1]],[[0,1],[0,1]]]){const d=graph(E);for(let s=0;s<2**d.k;s++)oracle(mapCheck(d,Array.from({length:d.k},(_,i)=>s>>i&1)));}
  const d=fixture(6,"all"),cert=N.normalize(G,B,H,C,d);ok(cert.kind==="signed-hall","signed fixture");
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  reject(()=>NV.verify(HV,d,{...cert,sigma:cert.sigma.map((x,i)=>i===0?2:x)}));
  reject(()=>NV.verify(HV,d,{...cert,sigma:cert.sigma.map(x=>1-x)}));
  reject(()=>NV.verify(HV,d,{...cert,hall:{...cert.hall,groups:cert.hall.groups.map((g,i)=>i?g:{...g,proof:g.proof.map((a,j)=>j===1?{...a,p:9999}:a)})}}));
  reject(()=>NV.verify(HV,d,{...cert,hall:{...cert.hall,exclusions:cert.hall.exclusions.slice(1)}}));reject(()=>NV.verifyMap(d,cert.sigma,d));
  out.stats=stats;
 }
 if(section==="all"||section==="masks"){
  const masks={hall:0,"polarity-hall":0,"signed-hall":0},d3=D.php(U,3);
  for(let s=0;s<4096;s++){const d=N.transform(d3,Array.from({length:12},(_,i)=>s>>i&1)).d,r=N.normalize(G,B,H,C,d);ok(r.kind!=="unknown"&&NV.verify(HV,d,r),"complete mask "+s);masks[r.kind]++;}
  out.masks=masks;
 }
 if(section==="all"||section==="large"){
  const rows=[];
  for(const [n,type] of [[3,"occupancy"],[6,"first"],[6,"all"],[6,"aux"],[8,"all"],[12,"all"],[20,"all"]]){const d=fixture(n,type),p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=N.normalize(G,B,H,C,a.d);ok(!p.contradiction&&a.a.rows.length===0&&a.a.free.length===d.k&&r.kind!=="unknown"&&NV.verify(HV,a.d,r),"large signed");rows.push({n,type,k:d.k,factors:d.F.length,kind:r.kind,groups:r.hall.groups.length,holes:r.hall.holes.length,axioms:r.hall.groups.reduce((s,g)=>s+g.proof.length,0),exclusions:r.hall.exclusions.length,search:r.search??null});}
  let relabelled=0;for(let t=0;t<32;t++){const d=D.php(U,4),s=Array.from({length:d.k},()=>rand()>>>31),e=N.transform(d,s).d,perm=Array.from({length:d.k},(_,i)=>i);for(let i=perm.length-1;i>0;i--){const j=rand()%(i+1);[perm[i],perm[j]]=[perm[j],perm[i]];}e.F=e.F.map(f=>({h:f.h.map(x=>perm[x]).reverse(),S:new Set([...f.S].map(t=>t.split(",").reverse().join()))})).reverse();const r=N.normalize(G,B,H,C,e);ok(r.kind!=="unknown"&&NV.verify(HV,e,r),"relabel");relabelled++;}
  out.rows=rows;out.relabelled=relabelled;
 }
 if(section==="all"||section==="physical"){
  const J=P.machine(),M=P.singleExit(K.compile(J)),N0=Min.refine(M),min={...M,...N0},physical=[],sat=graph([[0,1],[0,1]]),sm=graph([[0,1],[0,1],[0,1]]);
  for(const [name,d,compare] of [["mixed-small",N.transform(sm,[1,0,0,1,1,0]).d,true],["mixed-sat",N.transform(sat,[1,0,0,1]).d,true],["PHP6-first",fixture(6,"first"),false],["PHP20-all",fixture(20,"all"),false]]){
   const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=N.reduce(G,B,H,C,V,D,T,HV,NV,a.d,2000000);
   const ns=P.stream(U,r.d),b=P.run(M,ns,300000000),c=P.run(min,ns,b.t),cut=P.run(min,ns,b.t-1),clock=F.count(J,["",ns],M.codes);ok(JSON.stringify(b)===JSON.stringify(c)&&b.t===clock.clock&&b.encoded===clock.encoded&&cut.status==="TIMEOUT"&&cut.t===b.t-1&&cut.z===null,"physical");
   const row={name,status:b.status,kind:r.cert.kind,newPhysical:b.t,stream:ns.length};
   if(compare){const os=P.stream(U,a.d),old=P.run(min,os,300000000),oc=F.count(J,["",os],M.codes),m=models(d),x=old.z?p.expand(a.expand(old.z)):null,y=b.z?p.expand(a.expand(r.expand(b.z))):null;ok(old.status===b.status&&b.status===(m.length?"SAT":"UNSAT")&&(x?.join()??null)===(m[0]??null)&&(y?.join()??null)===(m[0]??null)&&old.t===oc.clock&&old.encoded===oc.encoded,"physical compare");row.oldPhysical=old.t;}
   else ok(b.status==="UNSAT"&&b.z===null&&["hall","polarity-hall","signed-hall"].includes(r.cert.kind),"large physical");physical.push(row);
  }
  out.physical=physical;out.resources={states:N0.stats.quotientStates,bits:N0.stats.quotientBits,clockChecks:6,cutoffs:4};
 }
 if(section==="all"||section==="barrier"){
  const original=D.php(U,6);let k=original.k,fs=[];for(const f of original.F){if(f.h.length!==2){fs.push(f);continue;}const [x,y]=f.h,u=k++;fs.push({h:[x,u],S:new Set(["0,0","0,1","1,1"])},{h:[u,y],S:new Set(["0,0","0,1","1,0"])});}
  const barrier={k,m:2,F:fs},p=R.reduce(U,Q,barrier),a=A.reduce(U,p.d);AV.verify(p.d,a.a);const r=N.reduce(G,B,H,C,V,D,T,HV,NV,a.d,2000000);ok(!p.contradiction&&a.a.free.length===189&&a.a.rows.length===0&&r.polarity.kind==="unknown"&&r.first.reason==="budget"&&r.cert.reason==="budget"&&r.d===a.d&&!r.contradiction,"new barrier");
  out.barrier={k,factors:fs.length,free:a.a.free.length,equations:a.a.rows.length,polarity:r.polarity,first:r.first,final:r.cert};
 }
 return out;
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_rank_worker.js'),require('./f038_rex_width_three_local_motion_compiler.js'),require('./f038_rex_width_three_local_motion_clock.js'),require('./f038_rex_width_two_quotient.js'),process.argv[2]||'all')));
