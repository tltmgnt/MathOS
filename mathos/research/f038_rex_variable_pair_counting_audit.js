// D7L: exhaustive numeric bounds, signed NAE, incomplete/weighted coverage and compositional obstruction.
function audit(U,Q,R,A,AV,C,V,D,T,H,HV,B,G,N,NV,I,IV,P,PV,J,JV,L,LV,section="oracle"){
 const ok=(b,s)=>{if(!b)throw Error(s);};
 const S=["0,0,1","0,1,0","0,1,1","1,0,0","1,0,1","1,1,0"],f=h=>({h,S:new Set(S)});
 const models=d=>[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())));
 const relation=(h,mask)=>({h,S:new Set([...U.tuples(2,h.length)].filter(z=>mask>>(z.reduce((s,x,i)=>s+(x<<i),0))&1).map(z=>z.join()))});
 const lines=[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]],fano={k:7,m:2,F:lines.map(f)};
 function bose(q){const F=[];for(let x=0;x<q;x++)F.push(f([3*x,3*x+1,3*x+2]));for(let x=0;x<q;x++)for(let y=x+1;y<q;y++)for(let i=0;i<3;i++)F.push(f([3*x+i,3*y+i,3*(((x+y)*((q+1)/2))%q)+(i+1)%3]));return {k:3*q,m:2,F};}
 const base=bose(7),incomplete={...base,F:base.F.slice(14)},weighted={...base,F:[...base.F,...base.F.slice(10),...base.F.slice(20,25)]},tail={k:41,m:2,F:[...base.F,...Array.from({length:10},(_,i)=>f([i===0?0:20+2*i,21+2*i,22+2*i]))]};
 if(section==="oracle"){
  const stats={cases:0,sat:0,unsat:0,models:0,certified:0,signed:0,localTypes:0,subsets:0,masks:0,weighted:0,random:0,boundChecks:0,tamperRejected:0};
  function check(d){const m=models(d),c=L.discover(d);stats.cases++;stats[m.length?"sat":"unsat"]++;stats.models+=m.length;
   if(c.kind==="pair-count"){ok(!m.length&&LV.verifyCount(d,c),"soundness");stats.certified++;if(c.mode==="signed")stats.signed++;}
   // Independently test the numeric relaxation on all assignments for each eligible orientation.
   for(const signed of [false,true]){
    const {rows,sigma}=L.triples(d,signed);if(!rows.length)continue;const b=L.bound(rows);let min=Infinity;
    for(const z of U.tuples(2,d.k)){let cost=0;for(const {h} of rows)for(let i=0;i<3;i++)for(let j=0;j<i;j++)if((z[h[i]]^sigma[h[i]])===(z[h[j]]^sigma[h[j]]))cost++;min=Math.min(min,cost);}
    ok(BigInt(b.lower)<=BigInt(min),"lower bound");stats.boundChecks++;
   }
  }
  for(let n=1;n<=3;n++)for(let m=0;m<2**(2**n);m++){check({k:n,m:2,F:[relation(Array.from({length:n},(_,i)=>i),m)]});stats.localTypes++;}
  for(let m=0;m<128;m++){check({...fano,F:fano.F.filter((_,i)=>m>>i&1)});stats.subsets++;}
  for(let m=0;m<128;m++){const d=N.transform(fano,Array.from({length:7},(_,i)=>m>>i&1)).d;check(d);ok(L.discover(d).kind==="pair-count","Fano masks");stats.masks++;}
  let seed=0xd7f024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  for(let t=0;t<128;t++){const F=[];for(const h of lines){const w=(rand()>>>16)%4;for(let i=0;i<w;i++)F.push(f(h));}const d=N.transform({k:7,m:2,F},Array.from({length:7},()=>rand()>>>31)).d;check(d);stats.weighted++;}
  for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%9;j++){const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))].sort((a,b)=>a-b);F.push(relation(h,rand()>>>16));}check({k,m:2,F});stats.random++;}
  const c=L.discover(fano),reject=fn=>{let bad=false;try{fn();}catch(e){bad=true;}ok(bad,"tamper");stats.tamperRejected++;};
  reject(()=>LV.verifyCount(fano,{...c,factors:[...c.factors,c.factors[0]]}));
  reject(()=>LV.verifyCount(fano,{...c,sigma:[1,...c.sigma.slice(1)]}));
  reject(()=>LV.verifyCount(fano,{...c,threshold:2}));
  reject(()=>LV.verifyCount(fano,{...c,lower:"999"}));
  reject(()=>LV.verifyCount(fano,{...c,factors:c.factors.slice(1)}));
  reject(()=>LV.verifyCount(fano,{...c,deficit:"1"}));
  return {stats};
 }
 if(section==="large"){
  const rows=[];
  for(const [name,d,pre] of [["STS21",base,true],["incomplete",incomplete,true],["weighted",weighted,false],["tail",tail,false],["signed",N.transform(base,Array.from({length:21},(_,i)=>+(i%3===0))).d,true],["STS93",bose(31),true],["STS303",bose(101),false]]){
   const p=pre?R.reduce(U,Q,d):null,a=pre?A.reduce(U,p.d):null;if(pre){AV.verify(p.d,a.a);ok(!p.contradiction&&a.a.free.length===d.k&&a.a.rows.length===0,"pre");}
   const e=pre?a.d:d,c=L.discover(e);ok(c.kind==="pair-count"&&LV.verifyCount(e,c),"large");
   rows.push({name,k:d.k,factors:d.F.length,pre,mode:c.mode,threshold:c.threshold,lower:c.lower,deficit:c.deficit,vertices:c.vertices,pairs:c.pairs,triples:c.triples,candidates:c.metrics.candidates,peels:c.metrics.peels});
  }return {rows};
 }
 if(section==="barrier"){
  const h=lines.slice(1),map=[0,7,8,9,10,11,12],d={k:13,m:2,F:[...h.map(f),...h.map(x=>f(x.map(y=>map[y]))),f([1,2,7])]},gadget={k:7,m:2,F:h.map(f)},gm=models(gadget);
  ok(gm.length>0&&gm.every(z=>z[0]===z[1]&&z[1]===z[2])&&models(d).length===0,"equality gadget");
  let maxGap=-Infinity,positive=0,subsets=0;for(let m=1;m<8192;m++){const fs=d.F.filter((_,i)=>m>>i&1),v=new Set(fs.flatMap(f=>f.h)).size,gap=2*fs.length-Math.floor(v*v/4);maxGap=Math.max(maxGap,gap);if(gap>0)positive++;subsets++;}
  ok(maxGap===0&&!positive,"all subsets");
  const p=R.reduce(U,Q,d),a=A.reduce(U,p.d);AV.verify(p.d,a.a);
  const r=L.infer(J,N,G,B,H,C,I,P,a.d),t=D.tree(C,a.d,2000000);ok(a.a.free.length===13&&a.a.rows.length===0&&r.kind==="unknown"&&r.iterative.status==="fixed-point"&&r.iterative.rounds===0&&t.kind==="tree"&&T.verifyTree(a.d,t),"barrier");
  const fallback=D.reduce({...C,cardinality:x=>N.sparseCardinality(C,x)},V,T,a.d,2000000);ok(fallback.contradiction&&fallback.cert.kind==="resolution","full fallback");
  return {barrier:{k:d.k,factors:d.F.length,gadgetModels:gm.length,subsets,maxGap,positive,count:r.count,iterative:r.iterative,resolution:{work:fallback.cert.work,nodes:fallback.cert.nodes.length,pairs:fallback.cert.pairs},tree:{work:t.work,nodes:t.nodes,leaves:t.leaves,splits:t.splits,units:t.units}}};
 }
 if(section==="adapter"){
  const d=base,r=L.reduce(J,N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,LV,d),sat={...fano,F:fano.F.slice(1)},s=L.reduce(J,N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,LV,sat);
  ok(r.contradiction&&r.cert.kind==="pair-count"&&r.d.k===1&&r.d.F.length===1&&!r.d.F[0].S.size&&!s.contradiction&&s.d===sat&&s.expand([1,0]).join()==="1,0","adapter");
  return {adapter:{unsat:r.cert.kind,streamFactor:{k:r.d.k,h:r.d.F[0].h,allowed:r.d.F[0].S.size},sat:s.cert.kind,preserved:s.d===sat}};
 }
 throw Error("section");
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_rank_reduction.js'),require('./f038_rex_variable_rank_quotient.js'),require('./f038_rex_variable_relational_closure.js'),require('./f038_rex_variable_affine_closure.js'),require('./f038_rex_variable_affine_certificate.js'),require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'),require('./f038_rex_variable_adaptive_inference.js'),require('./f038_rex_variable_adaptive_certificate.js'),require('./f038_rex_variable_hall_inference.js'),require('./f038_rex_variable_hall_certificate.js'),require('./f038_rex_variable_conflict_cliques.js'),require('./f038_rex_variable_disjunction_alternatives.js'),require('./f038_rex_variable_polarity_normalization.js'),require('./f038_rex_variable_polarity_certificate.js'),require('./f038_rex_variable_implication_closure.js'),require('./f038_rex_variable_implication_certificate.js'),require('./f038_rex_variable_conditional_propagation.js'),require('./f038_rex_variable_conditional_certificate.js'),require('./f038_rex_variable_iterative_consequences.js'),require('./f038_rex_variable_iterative_certificate.js'),require('./f038_rex_variable_pair_counting.js'),require('./f038_rex_variable_pair_counting_certificate.js'),process.argv[2]||'oracle')));
