// D7M: tight weighted counting, parity quotient and independent stratum checking.
function candidates(L,d){
 const blocks=[],seen=new Set();let tested=0;
 for(const signed of [false,true]){
  const {rows,sigma}=L.triples(d,signed),by=new Map();
  for(const r of rows)for(const x of r.h){if(!by.has(x))by.set(x,[]);by.get(x).push(r);}
  const visited=new Set(),parts=[];
  for(const x of by.keys())if(!visited.has(x)){const q=[x],part=new Map();visited.add(x);for(let i=0;i<q.length;i++)for(const r of by.get(q[i])){part.set(r.f,r);for(const y of r.h)if(!visited.has(y)){visited.add(y);q.push(y);}}parts.push([...part.values()]);}
  function test(rs){
   if(!rs.length)return;const factors=rs.map(r=>r.f).sort((a,b)=>a-b),key=factors.join()+"|"+sigma.join("");if(seen.has(key))return;seen.add(key);tested++;
   const b=L.bound(rs);if(BigInt(b.lower)<BigInt(rs.length))return;
   const vs=[...new Set(rs.flatMap(r=>r.h))].sort((a,b)=>a-b),w=new Map();
   for(const {h} of rs)for(let i=0;i<3;i++)for(let j=0;j<i;j++){const k=[h[i],h[j]].sort((a,b)=>a-b).join();w.set(k,(w.get(k)||0)+1);}
   const base={factors,sigma,...b};
   if(BigInt(b.lower)>BigInt(rs.length)){blocks.push({kind:"pair-count",...base});return;}
   const equations=[];
   for(let i=0;i<vs.length;i++)for(let j=i+1;j<vs.length;j++){const x=vs[i],y=vs[j],n=w.get([x,y].join())||0;if(n!==b.threshold)equations.push([x,y,sigma[x]^sigma[y]^+(n>b.threshold)]);}
   if(equations.length)blocks.push({kind:"tight",...base,equations});
  }
  for(const rs of parts)test(rs);
  // Closed neighborhoods of each coordinate in the pair-incidence graph.
  for(const [x,rs] of by){
   const vs=new Set([x]);for(const r of rs)for(const y of r.h)vs.add(y);
   const near=new Map();for(const y of vs)for(const r of by.get(y))if(r.h.every(z=>vs.has(z)))near.set(r.f,r);
   test([...near.values()]);
  }
 }
 return {blocks,tested};
}

function quotient(d,blocks){
 const parent=Array.from({length:d.k},(_,i)=>i),p=Array(d.k).fill(0);
 function find(x){let s=0;while(parent[x]!==x){s^=p[x];x=parent[x];}return [x,s];}
 for(const b of blocks)for(const [x,y,c] of b.equations){const [a,u]=find(x),[z,v]=find(y);if(a===z){if((u^v)!==c)return {kind:"parity-conflict"};}else{const lo=Math.min(a,z),hi=Math.max(a,z);parent[hi]=lo;p[hi]=u^v^c;}}
 const roots=parent.flatMap((x,i)=>x===i?[i]:[]),rank=new Map(roots.map((x,i)=>[x,i])),forms=parent.map((_,i)=>{const [r,s]=find(i);return [rank.get(r),s];}),F=[];
 for(const f of d.F){
  const h=[...new Set(f.h.map(x=>forms[x][0]))].sort((a,b)=>a-b),S=new Set();
  for(const row of f.S){const z=row.split(","),v=new Map();let good=true;for(let i=0;i<f.h.length;i++){const [r,s]=forms[f.h[i]],a=Number(z[i])^s;if(v.has(r)&&v.get(r)!==a)good=false;v.set(r,a);}if(good)S.add(h.map(x=>v.get(x)).join());}
  if(!S.size)return {kind:"factor-conflict"};
  if(S.size!==2**h.length)F.push({h,S});
 }
 return {kind:"view",d:{k:roots.length,m:2,F},forms,expand:z=>forms.map(([r,s])=>z[r]^s)};
}

function close(L,d,maxRounds=8){
 if(!Number.isSafeInteger(maxRounds)||maxRounds<0||maxRounds>d.k+8)throw Error("rounds");
 let view=d;const rounds=[],metrics=[];
 for(let i=0;i<maxRounds;i++){
  const {blocks,tested}=candidates(L,view),strict=blocks.find(b=>b.kind==="pair-count");
  metrics.push({k:view.k,factors:view.F.length,tested,blocks:blocks.length,equations:blocks.reduce((s,b)=>s+(b.equations?.length||0),0)});
  if(strict)return {kind:"count-conflict",rounds,proof:strict,metrics};
  if(!blocks.length)return {kind:"view",status:"fixed-point",d:view,rounds,metrics};
  rounds.push(blocks);const r=quotient(view,blocks);
  if(r.kind!=="view")return {kind:r.kind,rounds,metrics};
  if(r.d.k>=view.k)throw Error("no quotient progress");view=r.d;
 }
 return {kind:"view",status:"round-limit",d:view,rounds,metrics};
}

function reduce(L,LV,MV,J,N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,d,budget=2000000,maxRounds=8){
 const r=close(L,d,maxRounds);
 if(r.kind==="view")return {...L.reduce(J,N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,LV,d,budget),tight:r};
 if(MV.verify(LV,d,r)!==true)throw Error("unverified tight proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,tight:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={candidates,quotient,close,reduce};
