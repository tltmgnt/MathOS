// D7I: certified binary implication paths and anchor-restricted projection.
function factor(c,rank){
 const h=c.map(x=>rank.get(Math.abs(x)-1)),S=new Set();
 for(let mask=0;mask<2**h.length;mask++){const row=h.map((_,i)=>(mask>>i)&1);if(c.some((x,i)=>x>0?row[i]:!row[i]))S.add(row.join());}
 return {h,S};
}

function closure(C,d){
 if(d.m!==2)throw Error("binary");
 const adj=new Map(),literals=[];
 for(let i=1;i<=d.k;i++){literals.push(i,-i);adj.set(i,[]);adj.set(-i,[]);}
 const sources=[],anchorSet=new Set();
 for(let f=0;f<d.F.length;f++){
  if(!d.F[f].S.size)return {kind:"empty-factor",f};
  if(d.F[f].h.length>=3){sources.push(f);d.F[f].h.forEach(x=>anchorSet.add(x));}
 }
 const anchors=[...anchorSet].sort((a,b)=>a-b),rank=new Map(anchors.map((x,i)=>[x,i]));
 let binary=0,units=0,edges=0,searches=0,visits=0,edgeScans=0,pathSteps=0,derived=0;
 const info=()=>({binary,units,edges,searches,visits,edgeScans,pathSteps,derived,anchors:anchors.length});
 function add(x,y,f){adj.get(x).push({to:y,f});edges++;}
 for(const {c,f} of C.clauses(d)){
  if(c.length===1){units++;add(-c[0],c[0],f);}
  if(c.length===2){binary++;add(-c[0],c[1],f);add(-c[1],c[0],f);}
 }
 const paths=[],known=new Set(),opposites=new Map();
 for(const from of literals){
  searches++;
  const pred=new Map([[from,null]]),q=[from];
  for(let i=0;i<q.length;i++){
   const x=q[i];visits++;
   for(const edge of adj.get(x)){edgeScans++;if(!pred.has(edge.to)){pred.set(edge.to,{prev:x,f:edge.f});q.push(edge.to);}}
  }
  function path(to){
   const steps=[];let x=to;
   while(x!==from){const p=pred.get(x);if(!p)throw Error("unreachable");steps.push({to:x,f:p.f});x=p.prev;}
   steps.reverse();pathSteps+=steps.length;return {from,to,steps};
  }
  if(pred.has(-from)){
   const p=path(-from);
   if(opposites.has(-from))return {kind:"binary-contradiction",paths:[opposites.get(-from),p],metrics:info()};
   opposites.set(from,p);
  }
  if(!anchorSet.has(Math.abs(from)-1))continue;
  for(const to of q){
   if(to===from||!anchorSet.has(Math.abs(to)-1))continue;
   const c=[...new Set([-from,to])].sort((a,b)=>Math.abs(a)-Math.abs(b)),key=c.join();
   if(known.has(key))continue;known.add(key);
   const p=path(to);if(p.steps.length>1)derived++;paths.push({c,path:p});
  }
 }
 const F=sources.map(f=>({h:d.F[f].h.map(x=>rank.get(x)),S:new Set(d.F[f].S)}));
 for(const r of paths)F.push(factor(r.c,rank));
 return {kind:"view",d:{k:anchors.length,m:2,F},anchors,sources,paths,metrics:info()};
}

function infer(N,G,B,H,C,d,beam=8){
 const p=closure(C,d);
 if(p.kind!=="view")return p;
 if(p.d.k){
  const h=N.normalize(G,B,H,C,p.d,beam);
  if(h.kind!=="unknown")return {kind:"reach-hall",anchors:p.anchors,sources:p.sources,paths:p.paths,proof:h,metrics:p.metrics};
 }
 // A complete binary projection can omit useful original variables from a structural
 // heuristic; the original representation remains available to the inherited policy.
 const h=N.normalize(G,B,H,C,d,beam);
 if(h.kind!=="unknown")return {kind:"inherited",proof:h,metrics:p.metrics};
 return {kind:"unknown",metrics:p.metrics};
}

function reduce(N,G,B,H,C,V,D,T,HV,NV,IV,d,budget=2000000,beam=8){
 const c=infer(N,G,B,H,C,d,beam);
 if(c.kind==="unknown")return {...D.reduce({...C,cardinality:x=>N.sparseCardinality(C,x)},V,T,d,budget),implication:c};
 if(IV.verify(NV,HV,d,c)!==true)throw Error("unverified implication certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:c,implication:c,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={factor,closure,infer,reduce};
