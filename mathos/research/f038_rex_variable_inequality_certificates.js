// D7R: local convex support inequalities and bounded nonnegative combination search.
function supports(f){
 const n=f.h.length;if(n>3)throw Error("bounded arity");
 const z=[...f.S].map(s=>n?s.split(",").map(Number):[]);
 if(!z.length)return [{h:[],a:[],b:-1}];
 const rows=[],order=f.h.map((x,i)=>[x,i]).sort((a,b)=>a[0]-b[0]);
 for(let m=0;m<5**n;m++){
  const c=Array.from({length:n},(_,i)=>Math.floor(m/5**i)%5-2);
  if(!c.some(x=>Math.abs(x)===1))continue;
  const b=Math.max(...z.map(v=>v.reduce((s,x,i)=>s+x*c[i],0)));
  const h=[],a=[];for(const [x,i] of order)if(c[i]){h.push(x);a.push(c[i]);}
  rows.push({h,a,b});
 }
 return rows;
}

function discover(d,maxRounds=32){
 if(d.m!==2||!Number.isSafeInteger(maxRounds)||maxRounds<0||maxRounds>256)throw Error("limits");
 const rows=[],by=Array.from({length:d.k},()=>[]),frows=d.F.map((f,i)=>{
  const ids=[];for(const q of supports(f)){ids.push(rows.length);rows.push({...q,f:i});}
  for(const x of f.h)by[x].push(i);return ids;
 });
 const metrics={sources:rows.length,components:0,rounds:0,rowTests:0,selected:0};
 const seen=new Set(),parts=[];
 for(let i=0;i<d.F.length;i++)if(!seen.has(i)){
  const q=[i];seen.add(i);for(let j=0;j<q.length;j++)for(const x of d.F[q[j]].h)for(const f of by[x])if(!seen.has(f)){seen.add(f);q.push(f);}
  parts.push(q.sort((a,b)=>a-b));
 }
 metrics.components=parts.length;
 for(const part of parts){
  const coords=[...new Set(part.flatMap(i=>d.F[i].h))],a=Array(d.k).fill(0n),counts=new Map();let b=0n;
  const point=new Int8Array(d.k);point.fill(1); // twice the box point, initially 1/2
  for(let t=0;t<maxRounds;t++){
   metrics.rounds++;let selected=0;
   for(const f of part){
    let best=-1,margin=0,norm=Infinity;
    for(const i of frows[f]){
     const r=rows[i],v=r.h.reduce((s,x,j)=>s+r.a[j]*point[x],0)-2*r.b,l=r.a.reduce((s,x)=>s+Math.abs(x),0);metrics.rowTests++;
     if(v>margin||v===margin&&v>0&&l<norm){best=i;margin=v;norm=l;}
    }
    if(best<0)continue;const r=rows[best];selected++;metrics.selected++;
    counts.set(best,(counts.get(best)||0)+1);for(let j=0;j<r.h.length;j++)a[r.h[j]]+=BigInt(r.a[j]);b+=BigInt(r.b);
   }
   if(!selected)break;
   const lower=a.reduce((s,x)=>s+(x<0n?x:0n),0n);
   if(lower>b)return {kind:"inequality-conflict",terms:[...counts].map(([i,m])=>({row:rows[i],multiplier:m})),lower:String(lower),rhs:String(b),metrics};
   for(const x of coords)point[x]=a[x]>0n?0:a[x]<0n?2:1;
  }
 }
 return {kind:"unknown",status:"portfolio-exhausted",metrics};
}

function reduce(V,d,fallback,maxRounds=32){
 const r=discover(d,maxRounds);if(r.kind==="unknown")return {...(typeof fallback==="function"?fallback(d):{d,cert:r,contradiction:false,expand:z=>z}),inequality:r};
 if(V.verify(d,r)!==true)throw Error("unverified inequality proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,inequality:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={supports,discover,reduce};
