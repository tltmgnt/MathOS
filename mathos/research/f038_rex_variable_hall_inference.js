// D7E: certified extraction of Hall-deficient option systems.
function hall(C,d,alternatives=null){
 if(d.m!==2)throw Error("binary");
 const axioms=C.clauses(d);let chains=0,steps=0,edgeChecks=0,searchEdges=0,attempts=0,strategy=null;
 const info=()=>({chains,steps,edgeChecks,searchEdges,...(alternatives?{attempts,strategy}:{})});
 for(const sign of [1,-1]){
  const next=new Map(),mutex=new Map(),groups=[],taken=new Set();
  for(const a of axioms){
   const opp=a.c.filter(x=>x*sign<0);
   if(opp.length===1&&a.c.length>1){const p=-opp[0];if(!next.has(p))next.set(p,[]);next.get(p).push(a);}
   if(opp.length===2&&a.c.length===2)mutex.set(a.c.map(x=>-x).sort((a,b)=>Math.abs(a)-Math.abs(b)).join(),a);
  }
  for(const a of axioms){
   if(!a.c.length||!a.c.every(x=>x*sign>0))continue;
   chains++;let options=a.c.slice(),proof=[a],used=new Set(),ok=true;
   for(;;){
    const p=options.find(x=>next.has(x));
    if(p===undefined)break;
    if(used.has(p)||next.get(p).length!==1){ok=false;break;}
    used.add(p);const b=next.get(p)[0];proof.push(b);steps++;
    options=[...new Set([...options.filter(x=>x!==p),...b.c.filter(x=>x!==-p)])].sort((a,b)=>Math.abs(a)-Math.abs(b));
   }
   if(!ok||!options.length||options.some(x=>taken.has(x)))continue;
   for(const x of options)taken.add(x);
   groups.push({options,proof});
  }
  const owner=new Map();groups.forEach((g,i)=>g.options.forEach(x=>owner.set(x,i)));
  const adj=new Map([...owner.keys()].map(x=>[x,[]]));
  for(const a of mutex.values()){const [x,y]=a.c.map(v=>-v);if(owner.has(x)&&owner.has(y)&&owner.get(x)!==owner.get(y)){adj.get(x).push(y);adj.get(y).push(x);}}
  const components=[],seen=new Map();
  for(const x of adj.keys())if(!seen.has(x)){
   const q=[x],id=components.length;seen.set(x,id);
   for(let i=0;i<q.length;i++)for(const y of adj.get(q[i]))if(!seen.has(y)){seen.set(y,id);q.push(y);}
   components.push(q);
  }
  function* candidates(){yield {strategy:'components',holes:components};if(alternatives)yield* alternatives(adj,owner);}
  for(const candidate of candidates()){
  const holes=candidate.holes,at=new Map();attempts++;strategy=candidate.strategy;
  let valid=true;
  for(let h=0;h<holes.length;h++){if(!holes[h].length)valid=false;for(const x of holes[h]){if(!owner.has(x)||at.has(x))valid=false;at.set(x,h);}}
  if(!valid||at.size!==owner.size)continue;
  for(const q of holes)for(let i=0;i<q.length;i++)for(let j=0;j<i;j++)if(owner.get(q[i])!==owner.get(q[j])){
   edgeChecks++;if(!mutex.has([q[i],q[j]].sort((a,b)=>Math.abs(a)-Math.abs(b)).join()))valid=false;
  }
  if(!valid)continue;
  const E=groups.map(g=>[...new Set(g.options.map(x=>at.get(x)))]),L=Array(groups.length).fill(-1),H=Array(holes.length).fill(-1);
  for(let s=0;s<groups.length;s++){
   const q=[s],left=new Set(q),parent=new Map();let end=-1;
   for(let i=0;i<q.length&&end<0;i++)for(const h of E[q[i]]){
    searchEdges++;if(parent.has(h))continue;parent.set(h,q[i]);
    if(H[h]<0){end=h;break;}
    const t=H[h];if(!left.has(t)){left.add(t);q.push(t);}
   }
   if(end>=0){for(let h=end;h>=0;){const i=parent.get(h),prev=L[i];L[i]=h;H[h]=i;h=prev;}}
   else {
    const S=[...left].sort((a,b)=>a-b),N=[...parent.keys()].sort((a,b)=>a-b);
    const selected=new Set(S),outHoles=N.map(h=>holes[h].filter(x=>selected.has(owner.get(x)))),exclusions=[];
    for(const q of outHoles)for(let i=0;i<q.length;i++)for(let j=0;j<i;j++)if(owner.get(q[i])!==owner.get(q[j]))exclusions.push(mutex.get([q[i],q[j]].sort((a,b)=>Math.abs(a)-Math.abs(b)).join()));
    return {kind:"hall",sign,groups:S.map(i=>groups[i]),holes:outHoles,exclusions,...info()};
   }
  }
  }
 }
 return {kind:"unknown",...info()};
}

function reduce(C,V,D,T,H,d,budget=2000000){
 const h=hall(C,d);
 if(h.kind==="unknown")return {...D.reduce(C,V,T,d,budget),hall:h};
 if(H.verify(d,h)!==true)throw Error("unverified Hall certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:h,hall:h,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={hall,reduce};
