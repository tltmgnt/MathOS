// D7P: component-local bounded modular assumptions and shared-source discharge certificates.
function discover(O,N,L,A,d,maxProbes=4096,maxWork=200000000){
 if(d.m!==2||!Number.isSafeInteger(maxProbes)||maxProbes<0||!Number.isSafeInteger(maxWork)||maxWork<0)throw Error("limits");
 const s=O.sources(N,L,A,d),strict=s.blocks.find(b=>b.kind==="strict");
 if(strict)return {kind:"count-conflict",block:strict,discovery:s.discovery};
 const {blocks,rows}=s,records=[],metrics={components:0,probes:0,primeCalls:0,work:0,updates:0,residueTests:0,derived:0,primes:{3:0,5:0,7:0,11:0}};
 const by=Array.from({length:d.k},()=>[]),parts=[],visited=new Set();
 for(let i=0;i<rows.length;i++)for(const x of rows[i].h)by[x].push(i);
 for(let x=0;x<d.k;x++)if(by[x].length&&!visited.has(x)){
  const q=[x],ids=new Set();visited.add(x);
  for(let j=0;j<q.length;j++)for(const i of by[q[j]]){ids.add(i);for(const y of rows[i].h)if(!visited.has(y)){visited.add(y);q.push(y);}}
  parts.push({coords:q.sort((a,b)=>a-b),ids:[...ids].sort((a,b)=>a-b)});
 }
 const empty=rows.flatMap((r,i)=>r.h.length?[]:[i]);if(empty.length)parts.unshift({coords:[],ids:empty});
 metrics.components=parts.length;
 const stop={};let status="complete";
 try{
  for(const {coords,ids} of parts){
   const rank=new Map(coords.map((x,i)=>[x,i])),base=ids.map(i=>({...rows[i],h:rows[i].h.map(x=>rank.get(x))})),n=coords.length;
   function probe(assume){
    if(metrics.probes===maxProbes)throw stop;metrics.probes++;
    const ext=[...base,...assume.map(([x,b])=>({h:[rank.get(x)],c:[1],b}))],m=ext.length;
    // Charge a deterministic dense-matrix size proxy BEFORE each prime call.
    const cost=BigInt(n+1)*BigInt(m+1)*BigInt(n+m+1);
    for(const p of [3,5,7,11]){
     if(cost>BigInt(maxWork-metrics.work))throw stop;metrics.work+=Number(cost);metrics.primeCalls++;
     const r=O.eliminate(n,ext,p);metrics.updates+=r.updates;metrics.residueTests+=r.tests;
     if(r.kind==="modular-conflict"){
      metrics.primes[p]++;
      return {assume,prime:p,combination:r.combination.map(([i,v])=>[i<ids.length?ids[i]:rows.length+i-ids.length,v])};
     }
    }return null;
   }
   const direct=probe([]);if(direct)return {kind:"direct",blocks,rows,record:direct,metrics,discovery:s.discovery};
   const units=new Set();
   for(const x of coords)for(const b of [0,1]){const t=probe([[x,b]]);if(t){records.push(t);units.add(x+":"+b);metrics.derived++;}}
   for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)for(const a of [0,1])for(const b of [0,1]){
    const x=coords[i],y=coords[j];if(units.has(x+":"+a)||units.has(y+":"+b))continue;
    const t=probe([[x,a],[y,b]]);if(t){records.push(t);metrics.derived++;}
   }
  }
 }catch(e){if(e!==stop)throw e;status="budget";}
 const F=d.F.slice();
 for(const r of records){const h=r.assume.map(a=>a[0]),S=new Set();for(let m=0;m<2**h.length;m++){const z=h.map((_,j)=>m>>j&1);if(z.some((x,i)=>x!==r.assume[i][1]))S.add(z.join());}F.push({h,S});}
 return {kind:"view",status,d:{k:d.k,m:2,F},blocks,rows,records,metrics,discovery:s.discovery};
}

function infer(O,N,L,A,d,structural,maxProbes=4096,maxWork=200000000){
 const p=discover(O,N,L,A,d,maxProbes,maxWork);
 if(p.kind!=="view")return p;
 if(p.records.length&&typeof structural==="function"){
  const proof=structural(p.d);
  if(proof.kind!=="unknown")return {kind:"conditional",blocks:p.blocks,rows:p.rows,records:p.records,proof,status:p.status,metrics:p.metrics,discovery:p.discovery};
 }
 return {kind:"unknown",status:p.status,metrics:p.metrics,discovery:p.discovery};
}

function reduce(O,N,L,A,NV,PV,IV,PNV,HV,d,structural,fallback,maxProbes=4096,maxWork=200000000){
 const p=infer(O,N,L,A,d,structural,maxProbes,maxWork);
 if(p.kind==="unknown")return {...(typeof fallback==="function"?fallback(d):{d,cert:p,contradiction:false,expand:z=>z}),conditionalModular:p};
 if(PV.verify(NV,IV,PNV,HV,d,p)!==true)throw Error("unverified conditional modular proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:p,conditionalModular:p,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={discover,infer,reduce};
