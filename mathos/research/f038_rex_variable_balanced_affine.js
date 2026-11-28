// D7N: locally oriented tight balance equations and GF(2) contradiction certificates.
function discover(L,A,d,retainEven=false){
 if(d.m!==2)throw Error("binary");
 const eligible=[],by=Array.from({length:d.k},()=>[]),byPair=new Map();
 for(let i=0;i<d.F.length;i++){
  const {h,S}=d.F[i];if(h.length!==3||!["0,0,0","0,0,1","0,1,0","0,1,1"].some(b=>!S.has(b)&&!S.has(b.split(",").map(x=>1-Number(x)).join())))continue;
  eligible.push(i);for(const x of h)by[x].push(i);
  for(let a=0;a<3;a++)for(let b=0;b<a;b++){const key=[h[a],h[b]].sort((x,y)=>x-y).join();if(!byPair.has(key))byPair.set(key,[]);byPair.get(key).push(i);}
 }
 const blocks=[],seen=new Set(),accepted=new Set(),rows=[],rowKeys=new Set();let tested=0,orientations=0,seedPairs=0;
 function row(h,rhs,source){const key=h.join()+":"+rhs;if(!rowKeys.has(key)){rowKeys.add(key);rows.push({h,rhs,source});}}
 function test(vs){
  const v=[...vs].sort((a,b)=>a-b),key=v.join();if(seen.has(key))return;seen.add(key);tested++;
  const set=new Set(v),idx=new Set();for(const x of v)for(const i of by[x])if(d.F[i].h.every(y=>set.has(y)))idx.add(i);
  if(!idx.size)return;
  const ids=[...idx].sort((a,b)=>a-b),rank=new Map(v.map((x,i)=>[x,i])),local={k:v.length,m:2,F:ids.map(i=>({h:d.F[i].h.map(x=>rank.get(x)),S:d.F[i].S}))};
  for(const signed of [false,true]){
   orientations++;
   const p=L.triples(local,signed);if(!p.rows.length)continue;
   const b=L.bound(p.rows);if(BigInt(b.lower)<BigInt(p.rows.length))continue;
   const factors=p.rows.map(r=>ids[r.f]),coords=[...new Set(p.rows.flatMap(r=>r.h))].sort((a,b)=>a-b).map(i=>v[i]),sigma=coords.map(x=>p.sigma[rank.get(x)]);
   // Global complement does not change any local equation or NAE obligation.
   if(sigma[0])for(let i=0;i<sigma.length;i++)sigma[i]^=1;
   const k=factors.join()+"|"+sigma.join("");if(accepted.has(k))continue;accepted.add(k);
   const block={factors,coords,sigma,threshold:b.threshold,lower:b.lower,deficit:b.deficit};
   if(BigInt(b.lower)>BigInt(factors.length)){blocks.push({...block,kind:"strict"});continue;}
   const w=new Map();for(const i of factors){const h=d.F[i].h.slice().sort((a,b)=>a-b);for(let j=0;j<3;j++)for(let l=0;l<j;l++){const k=[h[l],h[j]].join();w.set(k,(w.get(k)||0)+1);}}
   const source=blocks.length,old=rows.length;
   if(coords.length%2===0)row(coords,(coords.length/2%2)^sigma.reduce((s,x)=>s^x,0),source);
   for(let i=0;i<coords.length;i++)for(let j=i+1;j<coords.length;j++){const x=coords[i],y=coords[j],n=w.get([x,y].join())||0;if(n!==b.threshold)row([x,y],sigma[i]^sigma[j]^+(n>b.threshold),source);}
   if(rows.length>old||retainEven&&coords.length%2===0)blocks.push({...block,kind:"tight"});
  }
 }
 const visited=new Set();for(const x of eligible.flatMap(i=>d.F[i].h))if(!visited.has(x)){const q=[x];visited.add(x);for(let j=0;j<q.length;j++)for(const i of by[q[j]])for(const y of d.F[i].h)if(!visited.has(y)){visited.add(y);q.push(y);}test(q);}
 for(let x=0;x<d.k;x++)if(by[x].length)test(new Set(by[x].flatMap(i=>d.F[i].h)));
 // All four-coordinate supports formed by two triples sharing a pair.
 for(const ids of byPair.values())for(let i=0;i<ids.length;i++)for(let j=0;j<i;j++){seedPairs++;const v=new Set([...d.F[ids[i]].h,...d.F[ids[j]].h]);if(v.size===4)test(v);}
 for(const a of A.equations(d).rows){const h=[];for(let i=0;i<d.k;i++)if(a.mask&(1n<<BigInt(i)))h.push(i);const source=blocks.length,old=rows.length;row(h,a.rhs,source);if(rows.length>old)blocks.push({kind:"local",factor:a.factor,h,rhs:a.rhs});}
 return {blocks,rows,metrics:{eligible:eligible.length,tested,orientations,seedPairs,blocks:blocks.length,rows:rows.length}};
}

function eliminate(k,rows){
 const pivots=Array(k).fill(null);let xors=0;
 for(let i=0;i<rows.length;i++){
  const r=rows[i];let mask=r.h.reduce((a,x)=>a|(1n<<BigInt(x)),0n),rhs=r.rhs,proof=1n<<BigInt(i);
  for(let j=k-1;j>=0;j--)if(mask&(1n<<BigInt(j))){const p=pivots[j];if(!p){pivots[j]={mask,rhs,proof};break;}mask^=p.mask;rhs^=p.rhs;proof^=p.proof;xors++;}
  if(!mask&&rhs)return {kind:"affine-conflict",combination:rows.flatMap((_,j)=>proof&(1n<<BigInt(j))?[j]:[]),rank:pivots.filter(Boolean).length,xors};
 }
 return {kind:"unknown",rank:pivots.filter(Boolean).length,xors};
}

function infer(L,A,d){
 const p=discover(L,A,d),strict=p.blocks.find(b=>b.kind==="strict");
 if(strict)return {kind:"count-conflict",block:strict,metrics:p.metrics};
 const e=eliminate(d.k,p.rows);return e.kind==="unknown"?{...e,metrics:p.metrics}:{...e,blocks:p.blocks,rows:p.rows,metrics:p.metrics};
}

function reduce(L,A,NV,M,LV,MV,J,N,G,B,H,C,V,D,T,HV,PNV,I,IV,P,PV,JV,d,budget=2000000){
 const r=infer(L,A,d);if(r.kind==="unknown")return {...M.reduce(L,LV,MV,J,N,G,B,H,C,V,D,T,HV,PNV,I,IV,P,PV,JV,d,budget),balanced:r};
 if(NV.verify(d,r)!==true)throw Error("unverified balanced certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,balanced:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={discover,eliminate,infer,reduce};
