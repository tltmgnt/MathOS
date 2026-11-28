// Independent dense-array certificate verifier, no BigInt XOR algebra.
function verify(d,a){
 const ok=(v,s)=>{if(!v)throw Error(s)},rows=[],affine=[];
 const dot=(mask,z)=>z.reduce((n,b,i)=>(n+(Math.floor(mask/2**i)%2)*b)%2,0);
 for(let i=0;i<d.F.length;i++){
  const f=d.F[i],z=[...f.S].map(t=>t.split(",").map(Number)),r=f.h.length,local=[];
  if(!z.length){rows.push({v:Array(d.k).fill(0),b:1,factor:i,local:0});affine.push(true);continue;}
  for(let s=1;s<2**r;s++){const b=dot(s,z[0]);if(z.every(t=>dot(s,t)===b)){const v=Array(d.k).fill(0);f.h.forEach((g,j)=>v[g]=Math.floor(s/2**j)%2);rows.push({v,b,factor:i,local:s});local.push([s,b]);}}
  let count=0;for(let n=0;n<2**r;n++){const t=Array.from({length:r},(_,j)=>Math.floor(n/2**j)%2);if(local.every(([s,b])=>dot(s,t)===b))count++;}affine.push(count===z.length);
 }
 const digits=n=>Array.from({length:d.k},(_,i)=>Number((n>>BigInt(i))&1n));
 ok(rows.length===a.rows.length&&JSON.stringify(affine)===JSON.stringify(a.affine),"extraction");
 for(let i=0;i<rows.length;i++){const r=rows[i],s=a.rows[i];ok(r.v.join()===digits(s.mask).join()&&r.b===s.rhs&&r.factor===s.factor&&r.local===s.local,"equation");}
 let cellOps=0;
 for(const [i,j] of a.ops){ok(Number.isInteger(i)&&Number.isInteger(j)&&j>=0&&i>j&&i<rows.length,"operation indices");const r=rows[i],s=rows[j];r.v=r.v.map((b,k)=>(b+s.v[k])%2);r.b=(r.b+s.b)%2;cellOps+=d.k+1;}
 for(let i=0;i<rows.length;i++)ok(rows[i].v.join()===digits(a.work[i].mask).join()&&rows[i].b===a.work[i].rhs,"final matrix");
 if(a.contradiction>=0){const r=rows[a.contradiction];ok(r&&r.b===1&&r.v.every(x=>!x),"false contradiction");}
 else{
  const used=new Set();for(let j=0;j<d.k;j++)if(a.pivots[j]>=0){const i=a.pivots[j],r=rows[i];ok(r&&!used.has(i)&&r.v[j]===1&&r.v.slice(j+1).every(x=>!x),"pivot");used.add(i);}
  rows.forEach((r,i)=>ok(used.has(i)||(!r.b&&r.v.every(x=>!x)),"unaccounted equation"));
  ok(a.free.join()===a.pivots.flatMap((p,j)=>p<0?[j]:[]).join(),"free columns");
  // Independently check the affine maps at zero and every unit vector.
  for(let i=-1;i<a.free.length;i++){const z=Array.from({length:a.free.length},(_,j)=>+(i===j)),w=a.expand(z);
   ok(a.free.every((g,j)=>w[g]===z[j]),"free identity");for(const r of rows)ok(r.v.reduce((s,v,j)=>(s+v*w[j])%2,0)===r.b,"expansion equation");}
 }
 return {equations:rows.length,ops:a.ops.length,cellOps,contradiction:a.contradiction>=0};
}
module.exports={verify};
