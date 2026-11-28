// D7L: exact weighted NAE pair-count bounds, signed selection and independent checking.
function verifyCount(d,c){
 const ok=b=>{if(!b)throw Error("invalid pair-count certificate");};
 ok(d.m===2&&c.kind==="pair-count"&&Array.isArray(c.factors)&&c.factors.length>0&&Array.isArray(c.sigma)&&c.sigma.length===d.k&&Array.from(c.sigma).every(x=>x===0||x===1)&&Number.isSafeInteger(c.threshold)&&c.threshold>0);
 const chosen=new Set(),vertices=new Set(),weights=new Map();
 for(const f of c.factors){
  ok(Number.isSafeInteger(f)&&f>=0&&f<d.F.length&&!chosen.has(f));chosen.add(f);
  const a=d.F[f],h=a.h;ok(h.length===3&&new Set(h).size===3&&h.every(x=>Number.isSafeInteger(x)&&x>=0&&x<d.k));
  const b=h.map(x=>c.sigma[x]);ok(!a.S.has(b.join())&&!a.S.has(b.map(x=>1-x).join()));
  for(const x of h){vertices.add(x);if(!weights.has(x))weights.set(x,new Map());}
  for(let i=0;i<3;i++)for(let j=i+1;j<3;j++){const x=Math.min(h[i],h[j]),y=Math.max(h[i],h[j]),m=weights.get(x);m.set(y,(m.get(y)||0)+1);}
 }
 const t=BigInt(c.threshold),vs=[...vertices];let deficit=0n,nonzero=0;
 for(let i=0;i<vs.length;i++)for(let j=i+1;j<vs.length;j++){
  const w=BigInt(weights.get(Math.min(vs[i],vs[j])).get(Math.max(vs[i],vs[j]))||0);if(w>0n)nonzero++;if(w<t)deficit+=t-w;
 }
 const v=BigInt(vs.length),a=v/2n,b=v-a,min=a*(a-1n)/2n+b*(b-1n)/2n,lower=t*min-deficit;
 ok(c.vertices===vs.length&&c.pairs===nonzero&&c.triples===chosen.size&&c.deficit===String(deficit)&&c.lower===String(lower)&&lower>BigInt(chosen.size));return true;
}

function verify(JV,PV,IV,NV,HV,d,c){
 if(c.kind==="pair-count")return verifyCount(d,c);
 if(c.kind==="inherited")return JV.verify(PV,IV,NV,HV,d,c.proof);
 throw Error("invalid pair counting certificate");
}
module.exports={verifyCount,verify};
