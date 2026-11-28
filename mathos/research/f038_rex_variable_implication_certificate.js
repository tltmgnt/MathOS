// D7I: certified binary implication paths and anchor-restricted projection.
function checkPath(d,p){
 const ok=b=>{if(!b)throw Error("invalid implication path");};
 const lit=x=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=d.k;
 ok(p&&lit(p.from)&&lit(p.to)&&Array.isArray(p.steps)&&p.steps.length>0&&p.steps.length<2*d.k);
 let x=p.from;const seen=new Set([x]);
 for(const step of p.steps){
  ok(step&&lit(step.to)&&Number.isSafeInteger(step.f)&&step.f>=0&&step.f<d.F.length&&!seen.has(step.to));
  const y=step.to,f=d.F[step.f],c=[...new Set([-x,y])];
  ok(c.length===f.h.length&&c.length<=2&&f.h.every(v=>c.filter(z=>Math.abs(z)===v+1).length===1));
  const row=f.h.map(v=>c.includes(v+1)?0:1);ok(!f.S.has(row.join()));
  seen.add(y);x=y;
 }
 ok(x===p.to);return true;
}

function reconstruct(d,p){
 const ok=b=>{if(!b)throw Error("invalid implication projection");};
 ok(d.m===2&&Array.isArray(p.anchors)&&Array.isArray(p.sources)&&Array.isArray(p.paths));
 const sources=[],coords=new Set();
 for(let i=0;i<d.F.length;i++)if(d.F[i].h.length>=3){sources.push(i);d.F[i].h.forEach(x=>coords.add(x));}
 const anchors=[...coords].sort((a,b)=>a-b);
 ok(p.anchors.length===anchors.length&&anchors.every((v,i)=>v===p.anchors[i])&&p.sources.length===sources.length&&sources.every((v,i)=>v===p.sources[i]));
 const rank=new Map(anchors.map((x,i)=>[x,i]));
 const F=sources.map(i=>({h:d.F[i].h.map(x=>rank.get(x)),S:new Set(d.F[i].S)})),seen=new Set();
 for(const r of p.paths){
  ok(r&&checkPath(d,r.path)&&Array.isArray(r.c));
  const c=[...new Set([-r.path.from,r.path.to])].sort((a,b)=>Math.abs(a)-Math.abs(b));
  ok(c.length===r.c.length&&c.every((x,i)=>x===r.c[i]&&rank.has(Math.abs(x)-1))&&!c.some(x=>c.includes(-x))&&!seen.has(c.join()));seen.add(c.join());
  const h=c.map(x=>rank.get(Math.abs(x)-1)),S=new Set();
  for(let mask=0;mask<2**h.length;mask++){
   const row=h.map((_,j)=>Math.floor(mask/2**j)%2);
   // Independent forbidden-row construction rather than evaluating disjunction.
   if(!row.every((v,j)=>v===(c[j]>0?0:1)))S.add(row.join());
  }
  F.push({h,S});
 }
 return {k:anchors.length,m:2,F};
}

function verify(NV,HV,d,cert){
 const ok=b=>{if(!b)throw Error("invalid implication certificate");};
 ok(d.m===2&&cert);
 if(cert.kind==="empty-factor"){ok(Number.isSafeInteger(cert.f)&&cert.f>=0&&cert.f<d.F.length&&d.F[cert.f].S.size===0);return true;}
 if(cert.kind==="binary-contradiction"){
  ok(Array.isArray(cert.paths)&&cert.paths.length===2);
  const [a,b]=cert.paths;ok(checkPath(d,a)&&checkPath(d,b)&&a.from===-a.to&&b.from===a.to&&b.to===a.from);return true;
 }
 if(cert.kind==="inherited")return NV.verify(HV,d,cert.proof);
 ok(cert.kind==="reach-hall");return NV.verify(HV,reconstruct(d,cert),cert.proof);
}
module.exports={checkPath,reconstruct,verify};
