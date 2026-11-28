// D7R: local convex support inequalities and bounded nonnegative combination search.
function checkRow(d,r){
 const ok=x=>{if(!x)throw Error("invalid local inequality");};
 ok(d.m===2&&r&&Number.isSafeInteger(r.f)&&r.f>=0&&r.f<d.F.length&&Array.isArray(r.h)&&Array.isArray(r.a)&&r.h.length===r.a.length&&r.h.length<=3&&Number.isSafeInteger(r.b)&&Math.abs(r.b)<=6);
 const f=d.F[r.f];ok(Array.from(r.h).every((x,i)=>Number.isSafeInteger(x)&&f.h.includes(x)&&(i===0||r.h[i-1]<x))&&Array.from(r.a).every(x=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=2));
 for(const s of f.S){const z=f.h.length?s.split(",").map(Number):[];ok(r.h.reduce((v,x,i)=>v+r.a[i]*z[f.h.indexOf(x)],0)<=r.b);}
 return true;
}

function verify(d,p){
 const ok=x=>{if(!x)throw Error("invalid inequality certificate");};
 ok(d.m===2&&p?.kind==="inequality-conflict"&&Array.isArray(p.terms)&&p.terms.length>0);
 const a=new Map();let b=0n;
 for(const t of p.terms){ok(t&&Number.isSafeInteger(t.multiplier)&&t.multiplier>0&&checkRow(d,t.row));const r=t.row,m=BigInt(t.multiplier);
  for(let i=0;i<r.h.length;i++)a.set(r.h[i],(a.get(r.h[i])||0n)+m*BigInt(r.a[i]));b+=m*BigInt(r.b);
 }
 let lower=0n;for(const x of a.values())if(x<0n)lower+=x;
 ok(lower>b&&p.lower===String(lower)&&p.rhs===String(b));return true;
}
module.exports={checkRow,verify};
