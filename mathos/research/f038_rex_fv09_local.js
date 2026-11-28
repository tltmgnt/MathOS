// FV-09: independent local replay of actual D7B narrow materialization.
// This is an executable audit, not a proved JS refinement. It does not trust
// the producer's affine/nonaffine flags or its residual table contents.
const insist=(b,s)=>{if(!b)throw Error(s);};
const bits=(x,n)=>Array.from({length:n},(_,i)=>Number((x>>BigInt(i))&1n));
const tuple=(mask,n)=>Array.from({length:n},(_,i)=>(mask>>i)&1);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function valid(d){
 insist(d&&d.m===2&&Number.isSafeInteger(d.k)&&d.k>=1&&Array.isArray(d.F),"dimension");
 for(const f of d.F){
  insist(Array.isArray(f.h)&&f.h.length>=1&&f.h.length<=3&&new Set(f.h).size===f.h.length&&
   f.h.every(i=>Number.isSafeInteger(i)&&i>=0&&i<d.k)&&f.S instanceof Set,"scope");
  for(const s of f.S)insist(typeof s==="string"&&s.split(",").length===f.h.length&&
   s.split(",").every(b=>b==="0"||b==="1"),"row");
 }
}
function canonical(fs){
 const map=new Map();
 for(const f of fs){
  const key=f.h.join(),prior=map.get(key);
  if(prior){for(const t of prior)if(!f.S.has(t))prior.delete(t);}
  else map.set(key,new Set(f.S));
 }
 return [...map].map(([k,s])=>[k,[...s].sort()]).sort((a,b)=>a[0].localeCompare(b[0]));
}
// Check pointwise pullback for every factor, then check the concrete
// tautology omission / duplicate-scope intersection and zero-free padding.
function replay(d,r,cap=8){
 try{
  valid(d);valid(r.d);
  insist(Number.isSafeInteger(cap)&&cap>=0&&cap<=16&&r.kind==="narrow","unsupported");
  const a=r.a,m=a.free.length;
  insist(a.contradiction===-1&&r.d.k===Math.max(1,m)&&a.forms.length===d.k&&
   new Set(a.free).size===m&&a.free.every(i=>Number.isSafeInteger(i)&&i>=0&&i<d.k),"map");
  const forms=a.forms.map(f=>{
   insist(typeof f.mask==="bigint"&&f.mask>=0n&&(f.mask>>BigInt(m))===0n&&(f.rhs===0||f.rhs===1),"form");
   return {vars:bits(f.mask,m).flatMap((b,i)=>b?[i]:[]),rhs:f.rhs};
  });
  let rows=0,maxWidth=0;const expected=[],local=[];
  for(const f of d.F){
   const scope=[...new Set(f.h.flatMap(i=>forms[i].vars))].sort((x,y)=>x-y);
   insist(scope.length<=cap,"local cap");
   maxWidth=Math.max(maxWidth,scope.length);
   const S=new Set();
   for(let mask=0;mask<2**scope.length;mask++){
    const t=tuple(mask,scope.length),z=new Map(scope.map((v,i)=>[v,t[i]]));
    const x=f.h.map(i=>forms[i].vars.reduce((sum,v)=>(sum+z.get(v))%2,forms[i].rhs));
    if(f.S.has(x.join()))S.add(t.join());rows++;
   }
   local.push({scope,rows:[...S].sort()});
   if(S.size===2**scope.length)continue;
   insist(scope.length>=1&&scope.length<=3,"not narrow");
   expected.push({h:scope,S});
  }
  if(m===0)expected.push({h:[0],S:new Set(["0"])});
  insist(same(canonical(expected),canonical(r.d.F)),"residual mismatch");
  return {rows,maxWidth,free:m,local};
 }catch{return null;}
}
module.exports={replay};
