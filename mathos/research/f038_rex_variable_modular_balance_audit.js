// D7O: integer source oracle, fixed-prime elimination, split-variable family and conditional experiment.
function audit(U,Q,R,A,AV,L,N,NV,O,OV,PN,C,D,T,I,IV,PNV,HV,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(x=>z[x]).join())));
 const nae=(h,sign=[])=>({h,S:new Set([...U.tuples(2,3)].filter(z=>{const y=z.map((x,j)=>x^+sign.includes(h[j]));return y.some(x=>x!==y[0]);}).map(z=>z.join()))});
 const block=(h,s=[])=>[...U.subsets(h,3)].map(t=>nae(t,s));
 const sig=k=>Array.from({length:k},(_,i)=>+(i*17%7<3));
 function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&4)a^=7;}return r;}
 const lines=[];for(let x=0;x<4;x++)lines.push(Array.from({length:4},(_,y)=>4*x+y));for(let slope=0;slope<3;slope++)for(let b=0;b<4;b++)lines.push(Array.from({length:4},(_,x)=>4*x+(mul(slope,x)^b)));
 const signs=[[],[0,3],[1,3],[],[0,2],[1,2],[2,3],[0,3],[1,2],[0,1],[0,2],[0,3],[],[],[0,1],[]];
 const prior={k:16,m:2,F:lines.flatMap((v,i)=>block(v,signs[i].map(j=>v[j])))};
 const subset=[0,2,3,4,6,8,9,10,11,12,13,14],ss=[[2,3],[0,3],[],[0,1],[],[2,3],[0,3],[1,2],[0,3],[1,2],[1,2],[1,2]],barrier={k:16,m:2,F:subset.flatMap((i,j)=>block(lines[i],ss[j].map(l=>lines[i][l])))};
 function split(len){const F=[],occ=Array.from({length:16},()=>[]);let k=0;for(let i=0;i<lines.length;i++){const v=lines[i].map(x=>{occ[x].push(k);return k++;});F.push(...block(v,signs[i].map(j=>v[j])));}
  for(const a of occ)for(let j=1;j<a.length;j++){let x=a[j-1];for(let l=0;l<len;l++){const y=l===len-1?a[j]:k++;F.push({h:[x,y],S:new Set(["0,0","1,1"])});x=y;}}return {k,m:2,F};
 }
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,rows:0,blocks:0,modular:0,strict:0,unknown:0,localTypes:0,masks:0,residueChecks:0,tamperRejected:0};
  function check(d){const m=models(d),q=O.sources(N,L,A,d),r=O.infer(N,L,A,d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;stats.rows+=q.rows.length;stats.blocks+=q.blocks.length;
   for(const b of q.blocks){if(b.kind==="local")NV.checkLocal(d,b);else NV.checkBlock(d,b);}
   ok(m.every(z=>q.rows.every(q=>q.h.reduce((s,x,j)=>s+q.c[j]*z[x],0)===q.b)),"integer row oracle");
   if(r.kind==="unknown")stats.unknown++;else{stats[r.kind==="modular-conflict"?"modular":"strict"]++;ok(!m.length&&OV.verify(NV,d,r),"soundness");}return r;
  }
  for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){const h=Array.from({length:n},(_,i)=>i),S=new Set([...U.tuples(2,n)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()));check({k:n,m:2,F:[{h,S}]});stats.localTypes++;}
  const b4={k:4,m:2,F:block([0,1,2,3])};for(let mask=0;mask<16;mask++){const d=PN.transform(b4,Array.from({length:4},(_,i)=>mask>>i&1)).d;ok(check(d).kind==="unknown"&&models(d).length===6,"balanced SAT");stats.masks++;}
  const mixed={k:4,m:2,F:[...b4.F,...[1,0,0,0].map((x,i)=>({h:[i],S:new Set([String(x)])}))]};ok(check(mixed).kind==="modular-conflict","mixed");
  const fano={k:7,m:2,F:[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]].map(h=>nae(h))};ok(check(fano).kind==="count-conflict","strict");
  let seed=0xd7e024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let i=0;i<128;i++){const k=3+i%5,F=[];for(let j=0;j<2+i%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b),mask=rand()>>>16;F.push({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});}check({k,m:2,F});}
  const r=check(prior);ok(r.kind==="modular-conflict"&&r.prime===3,"prior");const q=O.sources(N,L,A,prior),p5=O.eliminate(prior.k,q.rows,5);ok(p5.kind==="modular-conflict"&&OV.verify(NV,prior,{...p5,blocks:q.blocks,rows:q.rows}),"independent prime five");
  for(const p of [3,5,7,11])for(let a=0;a<p;a++)for(let b=0;b<p;b++)for(let c=0;c<p;c++){let mask=0;for(const z of U.tuples(2,3))mask|=1<<((a*z[0]+b*z[1]+c*z[2])%p);ok(O.reachable([a,b,c],p)===mask,"residue oracle");stats.residueChecks++;}
  function reject(fn){let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;}
  reject(()=>OV.verify(NV,prior,{...r,rhs:1}));reject(()=>OV.verify(NV,prior,{...r,prime:4}));reject(()=>OV.verify(NV,prior,{...r,combination:r.combination.slice(1)}));reject(()=>OV.verify(NV,prior,{...r,combination:[...r.combination,r.combination[0]]}));reject(()=>OV.verify(NV,prior,{...r,rows:r.rows.map((q,i)=>i?q:{...q,b:q.b+1})}));reject(()=>OV.verify(NV,prior,{...r,blocks:r.blocks.map((b,i)=>i?b:{...b,lower:"999"})}));reject(()=>OV.verify(NV,prior,{...r,residues:7}));
  return {stats,primeFive:{rank:p5.rank,updates:p5.updates,tests:p5.tests,coefficients:p5.coefficients,rhs:p5.rhs,residues:p5.residues,combination:p5.combination.length}};
 }
 if(section==="large"){
  const rows=[];for(const [name,raw,flip,pre] of [["prior",prior,false,true],["signed",prior,true,true],["split1",split(1),true,false],["split4",split(4),true,false],["split16",split(16),true,false]]){
   const d=flip?PN.transform(raw,sig(raw.k)).d:raw,p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(a.a.free.length===d.k&&!a.a.rows.length,"pre");}
   const e=pre?a.d:d,r=O.infer(N,L,A,e);ok(r.kind==="modular-conflict"&&OV.verify(NV,e,r),"large");
   rows.push({name,k:d.k,factors:d.F.length,pre,prime:r.prime,nonzero:r.coefficients.flatMap((v,i)=>v?[[i,v]]:[]),rhs:r.rhs,residues:r.residues,combination:r.combination.length,discovery:r.discovery,metrics:r.metrics});
  }return {rows};
 }
 if(section==="barrier"){
  const d=barrier,p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
  const e=a.d,q=O.sources(N,L,A,e),r=O.infer(N,L,A,e),n=N.infer(L,A,e),t=D.tree(C,e,2000000);
  ok(!models(d).length&&a.a.free.length===16&&!a.a.rows.length&&r.kind==="unknown"&&n.kind==="unknown"&&t.kind==="tree"&&T.verifyTree(e,t),"barrier");
  let singles=0,checked=0,counts={};const F=e.F.slice();
  for(let i=0;i<16;i++)for(let b=0;b<2;b++)for(const prime of [3,5,7,11])if(O.eliminate(16,[...q.rows,{h:[i],c:[1],b}],prime).kind!=="unknown"){singles++;break;}
  for(let i=0;i<16;i++)for(let j=i+1;j<16;j++)for(let a=0;a<2;a++)for(let b=0;b<2;b++)for(const prime of [3,5,7,11]){
   const v=O.eliminate(16,[...q.rows,{h:[i],c:[1],b:a},{h:[j],c:[1],b}],prime);if(v.kind==="unknown")continue;
   const aug={...e,F:[...e.F,{h:[i],S:new Set([String(a)])},{h:[j],S:new Set([String(b)])}]},blocks=[...q.blocks,{kind:"local",factor:e.F.length,h:[i],rhs:a},{kind:"local",factor:e.F.length+1,h:[j],rhs:b}],rows=[...q.rows,{h:[i],c:[1],b:a,source:q.blocks.length,rule:"parity"},{h:[j],c:[1],b,source:q.blocks.length+1,rule:"parity"}];
   ok(OV.verify(NV,aug,{...v,blocks,rows}),"conditional probe");checked++;counts[prime]=(counts[prime]||0)+1;
   F.push({h:[i,j],S:new Set([...U.tuples(2,2)].filter(z=>z[0]!==a||z[1]!==b).map(z=>z.join()))});break;
  }
  const aug={...e,F},v=I.closure(C,aug);ok(singles===0&&checked===172&&v.kind==="binary-contradiction"&&IV.verify(PNV,HV,aug,v),"pair probe experiment");
  return {barrier:{k:d.k,factors:d.F.length,assignments:65536,modular:r,affine:n,tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units},conditional:{singles,checked,counts,paths:v.paths.map(p=>p.steps.length)}}};
 }
 if(section==="adapter"){
  const r=O.reduce(N,L,A,NV,OV,prior),sat={k:4,m:2,F:block([0,1,2,3])},s=O.reduce(N,L,A,NV,OV,sat),w=O.reduce(N,L,A,NV,OV,sat,d=>({d,cert:{kind:"sentinel"},contradiction:false,expand:z=>z}));
  ok(r.contradiction&&r.d.k===1&&!r.d.F[0].S.size&&s.d===sat&&s.cert.kind==="unknown"&&w.d===sat&&w.cert.kind==="sentinel","adapter");
  return {adapter:{kind:r.cert.kind,k:r.d.k,allowed:r.d.F[0].S.size,preserved:s.d===sat,delegated:w.cert.kind}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_balanced_affine.js'),require('./f038_rex_variable_balanced_affine_certificate.js'),require('./f038_rex_variable_modular_balance.js'),require('./f038_rex_variable_modular_balance_certificate.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_hall_certificate.js'),process.argv[2]||'oracle')));
