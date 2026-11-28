// D7Q: bounded-arity exact integer affine hull and shared modular certificates.
function checkLocal(d,b){
 const ok=x=>{if(!x)throw Error("invalid local integer identity");};
 ok(d.m===2&&b?.kind==="integer-local"&&Number.isSafeInteger(b.factor)&&b.factor>=0&&b.factor<d.F.length&&Array.isArray(b.h)&&Array.isArray(b.c)&&b.h.length===b.c.length&&b.h.length<=3&&Number.isSafeInteger(b.b)&&Math.abs(b.b)<=6);
 const f=d.F[b.factor];ok(b.h.every((x,i)=>Number.isSafeInteger(x)&&f.h.includes(x)&&(i===0||b.h[i-1]<x))&&Array.from(b.c).every(x=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=2));
 for(const s of f.S){const z=f.h.length?s.split(",").map(Number):[];ok(b.h.reduce((a,x,i)=>a+b.c[i]*z[f.h.indexOf(x)],0)===b.b);}
 return true;
}

function checkSources(NV,PV,d,blocks,rows){
 if(!Array.isArray(blocks)||!Array.isArray(rows))throw Error("sources");
 const old=[],oldRows=[],map=new Map();
 for(let i=0;i<blocks.length;i++){const b=blocks[i];if(b.kind==="integer-local")checkLocal(d,b);else{map.set(i,old.length);old.push(b);}}
 for(const q of rows){
  if(!q||!Number.isSafeInteger(q.source)||q.source<0||q.source>=blocks.length)throw Error("source index");
  const b=blocks[q.source];
  if(b.kind==="integer-local"){
   if(q.rule!=="integer-local"||JSON.stringify(q.h)!==JSON.stringify(b.h)||JSON.stringify(q.c)!==JSON.stringify(b.c)||q.b!==b.b)throw Error("identity mismatch");
  }else oldRows.push({...q,source:map.get(q.source)});
 }
 return PV.checkSources(NV,d,old,oldRows);
}

function reconstruct(NV,PV,d,p){
 checkSources(NV,PV,d,p.blocks,p.rows);
 if(!Array.isArray(p.records))throw Error("records");
 const F=d.F.slice(),seen=new Set();
 for(const r of p.records){
  if(!PV.checkRecord(d,p.rows,r)||!r.assume.length)throw Error("discharge");
  const h=r.assume.map(a=>a[0]),bad=r.assume.map(a=>a[1]).join(),key=h.join()+":"+bad;if(seen.has(key))throw Error("duplicate");seen.add(key);
  const S=new Set();for(let i=0;i<2**h.length;i++){const z=h.map((_,j)=>Math.floor(i/2**j)%2).join();if(z!==bad)S.add(z);}F.push({h,S});
 }
 return {k:d.k,m:2,F};
}

function verify(NV,PV,IV,PNV,HV,d,p){
 if(p.kind==="count-conflict")return PV.verify(NV,IV,PNV,HV,d,p);
 if(p.kind==="direct"){checkSources(NV,PV,d,p.blocks,p.rows);if(p.record.assume.length)throw Error("direct assumptions");return PV.checkRecord(d,p.rows,p.record);}
 if(p.kind!=="conditional")throw Error("terminal");
 return IV.verify(PNV,HV,reconstruct(NV,PV,d,p),p.proof);
}
module.exports={checkLocal,checkSources,reconstruct,verify};
