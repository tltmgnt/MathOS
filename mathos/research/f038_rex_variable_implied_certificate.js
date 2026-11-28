// D7I independent replay: no producer graph, reachability or orientation logic.
function reconstruct(d,cert){
 const ok=b=>{if(!b)throw Error("invalid implied-conflict certificate");};
 ok(d.m===2&&Number.isSafeInteger(d.k)&&d.k>=0&&Array.isArray(cert.nonbinary)&&Array.isArray(cert.paths));
 const literal=x=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=d.k;
 const used=new Set(),F=[];
 for(const i of cert.nonbinary){ok(Number.isSafeInteger(i)&&i>=0&&i<d.F.length&&!used.has(i)&&d.F[i].h.length!==2);used.add(i);F.push(d.F[i]);}
 const pairs=new Set();
 for(const p of cert.paths){
  ok(p&&literal(p.x)&&literal(p.y)&&Math.abs(p.x)!==Math.abs(p.y)&&Array.isArray(p.edges)&&p.edges.length>0&&p.edges.length<2*d.k);
  const key=[p.x,p.y].sort((a,b)=>a-b).join();ok(!pairs.has(key));pairs.add(key);
  let at=p.x;const seen=new Set([at]);
  for(const e of p.edges){
   ok(e&&e.from===at&&literal(e.to)&&!seen.has(e.to)&&Math.abs(e.from)!==Math.abs(e.to)&&Number.isSafeInteger(e.f)&&e.f>=0&&e.f<d.F.length);
   const f=d.F[e.f],a=Math.abs(e.from)-1,b=Math.abs(e.to)-1;
   ok(f.h.length===2&&f.h.includes(a)&&f.h.includes(b));
   // Implication from -> to excludes exactly the row from=true,to=false.
   const row=f.h.map(v=>v===a?+(e.from>0):+(e.to<0)).join();
   ok(!f.S.has(row));at=e.to;seen.add(at);
  }
  ok(at===-p.y);
  const h=[Math.abs(p.x)-1,Math.abs(p.y)-1],S=new Set();
  for(let mask=0;mask<4;mask++){
   const a=mask&1,b=mask>>1;
   if(!(a===+(p.x>0)&&b===+(p.y>0)))S.add([a,b].join());
  }
  F.push({h,S});
 }
 return {k:d.k,m:2,F};
}
function verify(NV,HV,d,cert){
 if(cert.kind!=="implied-hall")throw Error("certificate kind");
 return NV.verify(HV,reconstruct(d,cert),cert.hall)===true;
}
module.exports={reconstruct,verify};
