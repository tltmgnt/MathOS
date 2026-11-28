// D7J: bounded source-clause conditional propagation with independent trace replay.
function checkTrace(d,t){
 const ok=b=>{if(!b)throw Error("invalid propagation trace");};
 const lit=x=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=d.k;
 ok(d.m===2&&t&&Array.isArray(t.assume)&&t.assume.length<=2&&Array.isArray(t.steps)&&t.steps.length<=d.k);
 const z=new Map();
 for(const x of t.assume){ok(lit(x)&&!z.has(Math.abs(x)));z.set(Math.abs(x),x);}
 function ax(a){
  ok(a&&Number.isSafeInteger(a.f)&&a.f>=0&&a.f<d.F.length&&Array.isArray(a.c));
  const f=d.F[a.f];ok(a.c.length===f.h.length&&f.h.every(v=>a.c.filter(x=>lit(x)&&Math.abs(x)===v+1).length===1));
  ok(!f.S.has(f.h.map(v=>a.c.includes(v+1)?0:1).join()));return a.c;
 }
 for(const a of t.steps){const c=ax(a),p=a.p;ok(lit(p)&&c.includes(p)&&!z.has(Math.abs(p))&&c.every(x=>x===p||z.get(Math.abs(x))===-x));z.set(Math.abs(p),p);}
 ok(ax(t.conflict).every(x=>z.get(Math.abs(x))===-x));return true;
}

function reconstruct(d,records){
 const ok=b=>{if(!b)throw Error("invalid conditional view");};ok(Array.isArray(records));const F=d.F.slice(),seen=new Set();
 for(const r of records){
  ok(r&&checkTrace(d,r.trace)&&r.trace.assume.length>=1&&Array.isArray(r.c));
  const c=r.trace.assume.map(x=>-x).sort((a,b)=>Math.abs(a)-Math.abs(b));
  ok(c.length===r.c.length&&c.every((x,i)=>x===r.c[i])&&!seen.has(c.join()));seen.add(c.join());
  const h=c.map(x=>Math.abs(x)-1),S=new Set();
  for(let i=0;i<2**h.length;i++){const row=h.map((_,j)=>Math.floor(i/2**j)%2);if(!row.every((v,j)=>v===(c[j]>0?0:1)))S.add(row.join());}
  F.push({h,S});
 }
 return {k:d.k,m:2,F};
}

function verify(IV,NV,HV,d,p){
 if(p.kind==="inherited")return IV.verify(NV,HV,d,p.proof);
 if(p.kind==="propagation-conflict"){if(p.trace.assume.length)throw Error("nonempty assumptions");return checkTrace(d,p.trace);}
 if(p.kind!=="conditional")throw Error("invalid conditional certificate");
 return IV.verify(NV,HV,reconstruct(d,p.records),p.proof);
}
module.exports={checkTrace,reconstruct,verify};
