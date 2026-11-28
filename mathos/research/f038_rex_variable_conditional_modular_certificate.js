// D7P: component-local bounded modular assumptions and shared-source discharge certificates.
function checkSources(NV,d,blocks,rows){
 const ok=x=>{if(!x)throw Error("invalid shared integer sources");};
 ok(d.m===2&&Array.isArray(blocks)&&Array.isArray(rows));
 const allowed=blocks.map(b=>{ok(b.kind==="tight"||b.kind==="local");return b.kind==="local"?NV.checkLocal(d,b):NV.checkBlock(d,b);});
 for(const q of rows){
  ok(q&&Number.isSafeInteger(q.source)&&q.source>=0&&q.source<blocks.length&&Array.isArray(q.h)&&Array.isArray(q.c)&&q.c.length===q.h.length&&q.h.every((x,i)=>Number.isSafeInteger(x)&&x>=0&&x<d.k&&(i===0||q.h[i-1]<x))&&Number.isSafeInteger(q.b));
  const b=blocks[q.source];
  if(q.rule==="balance")ok(b.kind==="tight"&&b.coords.length%2===0&&JSON.stringify(q.h)===JSON.stringify(b.coords)&&q.c.every((x,i)=>x===1-2*b.sigma[i])&&q.b===b.coords.length/2-b.sigma.reduce((s,x)=>s+x,0));
  else{
   ok(q.rule==="parity"&&q.h.length<=2&&allowed[q.source].some(t=>JSON.stringify(t.h)===JSON.stringify(q.h)&&t.rhs===q.b));
   ok(q.h.length===0?q.b===1:q.c[0]===1);if(q.h.length===2)ok(q.c[1]===(q.b?1:-1));
  }
 }
 return true;
}

function checkRecord(d,rows,r){
 const ok=x=>{if(!x)throw Error("invalid conditional modular record");};
 ok(r&&[3,5,7,11].includes(r.prime)&&Array.isArray(r.assume)&&r.assume.length<=2&&Array.isArray(r.combination)&&r.combination.length);
 for(let i=0;i<r.assume.length;i++){const a=r.assume[i];ok(Array.isArray(a)&&a.length===2&&Number.isSafeInteger(a[0])&&a[0]>=0&&a[0]<d.k&&(a[1]===0||a[1]===1)&&(i===0||r.assume[i-1][0]<a[0]));}
 const p=r.prime,mod=x=>((x%p)+p)%p,coeff=Array(d.k).fill(0),seen=new Set();let rhs=0;
 for(const pair of r.combination){
  ok(Array.isArray(pair)&&pair.length===2);const [i,v]=pair;ok(Number.isSafeInteger(i)&&i>=0&&i<rows.length+r.assume.length&&!seen.has(i)&&Number.isSafeInteger(v)&&v>0&&v<p);seen.add(i);
  if(i<rows.length){const q=rows[i];for(let j=0;j<q.h.length;j++)coeff[q.h[j]]=mod(coeff[q.h[j]]+v*q.c[j]);rhs=mod(rhs+v*q.b);}
  else{const [x,b]=r.assume[i-rows.length];coeff[x]=mod(coeff[x]+v);rhs=mod(rhs+v*b);}
 }
 let possible=new Set([0]);for(const a of coeff){const next=new Set(possible);for(const v of possible)next.add(mod(v+a));possible=next;}
 ok(!possible.has(rhs));return true;
}

function reconstruct(NV,d,p){
 if(!checkSources(NV,d,p.blocks,p.rows)||!Array.isArray(p.records))throw Error("sources");
 const F=d.F.slice(),seen=new Set();
 for(const r of p.records){
  if(!checkRecord(d,p.rows,r)||!r.assume.length)throw Error("assumption discharge");
  const h=r.assume.map(a=>a[0]),bad=r.assume.map(a=>a[1]).join(),key=h.join()+":"+bad;
  if(seen.has(key))throw Error("duplicate consequence");seen.add(key);
  const S=new Set();for(let m=0;m<2**h.length;m++){const z=h.map((_,j)=>Math.floor(m/2**j)%2).join();if(z!==bad)S.add(z);}F.push({h,S});
 }
 return {k:d.k,m:2,F};
}

function verify(NV,IV,PNV,HV,d,p){
 if(p.kind==="count-conflict"){if(p.block?.kind!=="strict")throw Error("strict");NV.checkBlock(d,p.block);return true;}
 if(p.kind==="direct"){checkSources(NV,d,p.blocks,p.rows);if(p.record.assume.length)throw Error("direct assumptions");return checkRecord(d,p.rows,p.record);}
 if(p.kind!=="conditional")throw Error("invalid conditional modular certificate");
 return IV.verify(PNV,HV,reconstruct(NV,d,p),p.proof);
}
module.exports={checkSources,checkRecord,reconstruct,verify};
