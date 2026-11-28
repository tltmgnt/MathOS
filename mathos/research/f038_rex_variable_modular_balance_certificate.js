// D7O: independent source reconstruction, modular combination and Boolean residue checking.
function verify(NV,d,r){
 const ok=x=>{if(!x)throw Error("invalid modular certificate");};
 ok(d.m===2&&r);
 if(r.kind==="count-conflict"){ok(r.block?.kind==="strict");NV.checkBlock(d,r.block);return true;}
 ok(r.kind==="modular-conflict"&&[3,5,7,11].includes(r.prime)&&Array.isArray(r.blocks)&&Array.isArray(r.rows)&&Array.isArray(r.combination)&&r.combination.length);
 const p=r.prime,mod=x=>((x%p)+p)%p,allowed=r.blocks.map(b=>{ok(b.kind==="tight"||b.kind==="local");return b.kind==="local"?NV.checkLocal(d,b):NV.checkBlock(d,b);});
 for(const q of r.rows){
  ok(q&&Number.isSafeInteger(q.source)&&q.source>=0&&q.source<r.blocks.length&&Array.isArray(q.h)&&Array.isArray(q.c)&&q.c.length===q.h.length&&q.h.every((x,i)=>Number.isSafeInteger(x)&&x>=0&&x<d.k&&(i===0||q.h[i-1]<x)));
  const b=r.blocks[q.source];
  if(q.rule==="balance"){ok(b.kind==="tight"&&b.coords.length%2===0&&JSON.stringify(q.h)===JSON.stringify(b.coords)&&q.c.every((x,i)=>x===(b.sigma[i]?-1:1))&&q.b===b.coords.length/2-b.sigma.filter(x=>x===1).length);}
  else{ok(q.rule==="parity"&&q.h.length<=2);const t=allowed[q.source].find(t=>JSON.stringify(t.h)===JSON.stringify(q.h)&&t.rhs===q.b);ok(t&&(q.h.length===0?q.b===1:q.c[0]===1)&&(q.h.length!==2||q.c[1]===(q.b?1:-1)));}
 }
 const a=Array(d.k).fill(0),seen=new Set();let rhs=0;
 for(const pair of r.combination){ok(Array.isArray(pair)&&pair.length===2);const [i,v]=pair;ok(Number.isSafeInteger(i)&&i>=0&&i<r.rows.length&&!seen.has(i)&&Number.isSafeInteger(v)&&v>0&&v<p);seen.add(i);const q=r.rows[i];for(let j=0;j<q.h.length;j++)a[q.h[j]]=mod(a[q.h[j]]+v*q.c[j]);rhs=mod(rhs+v*q.b);}
 ok(JSON.stringify(a)===JSON.stringify(r.coefficients)&&rhs===r.rhs);
 let possible=new Set([0]);for(const v of a){const next=new Set(possible);for(const x of possible)next.add(mod(x+v));possible=next;}
 ok(!possible.has(rhs)&&r.residues===[...possible].reduce((s,x)=>s+2**x,0));return true;
}
module.exports={verify};
