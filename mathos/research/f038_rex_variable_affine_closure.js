// D7B: binary affine-hull extraction and rightmost-pivot elimination.
// Host preprocessing; no physical GF(2) implementation claimed.
const bit=i=>1n<<BigInt(i);
function parity(x){let p=0;while(x){p^=1;x&=x-1n;}return p;}
function equations(d){
 if(d.m!==2)throw Error("binary domain");
 const rows=[],affine=[];
 for(let i=0;i<d.F.length;i++){
  const f=d.F[i],r=f.h.length;
  if(!f.S.size){rows.push({mask:0n,rhs:1,factor:i,local:0});affine.push(true);continue;}
  const tuples=[...f.S].map(t=>t.split(",").reduce((n,v,j)=>n+(+v<<j),0)),local=[];
  for(let a=1;a<2**r;a++){
   const b=parity(BigInt(a&tuples[0]));
   if(tuples.every(t=>parity(BigInt(a&t))===b)){
    const mask=f.h.reduce((n,v,j)=>n|(a>>j&1?bit(v):0n),0n);
    rows.push({mask,rhs:b,factor:i,local:a});local.push([a,b]);
   }
  }
  let count=0;for(let t=0;t<2**r;t++)if(local.every(([a,b])=>parity(BigInt(a&t))===b))count++;
  affine.push(count===f.S.size);
 }
 return {rows,affine};
}
function eliminate(d){
 const {rows,affine}=equations(d),work=rows.map(({mask,rhs})=>({mask,rhs})),pivots=Array(d.k).fill(-1),ops=[];
 let contradiction=-1;
 for(let i=0;i<work.length;i++){
  for(let j=d.k-1;j>=0;j--)if(work[i].mask&bit(j)){
   const p=pivots[j];
   if(p<0){pivots[j]=i;break;}
   work[i].mask^=work[p].mask;work[i].rhs^=work[p].rhs;ops.push([i,p]);
  }
  if(work[i].mask===0n&&work[i].rhs){contradiction=i;break;}
 }
 const free=pivots.flatMap((p,i)=>p<0?[i]:[]),forms=[];
 if(contradiction<0)for(let i=0;i<d.k;i++){
  const p=pivots[i];if(p<0){forms.push({mask:bit(free.indexOf(i)),rhs:0});continue;}
  let mask=0n,rhs=work[p].rhs;
  for(let j=0;j<i;j++)if(work[p].mask&bit(j)){mask^=forms[j].mask;rhs^=forms[j].rhs;}
  forms.push({mask,rhs});
 }
 const expand=z=>{if(contradiction>=0||z.length!==free.length)throw Error("affine expansion");const m=z.reduce((a,v,i)=>a|(v?bit(i):0n),0n);return forms.map(f=>parity(f.mask&m)^f.rhs);};
 return {rows,affine,work,pivots,ops,contradiction,free,forms,expand};
}
function reduce(U,d){
 const a=eliminate(d);
 if(a.contradiction>=0)return {a,kind:"contradiction",d:{k:1,m:2,F:[{h:[0],S:new Set()}]},expand:()=>{throw Error("UNSAT");}};
 const n=a.free.length,F=[];let wide=0,maxWidth=0;
 for(let i=0;i<d.F.length;i++){
  if(a.affine[i])continue;
  const f=d.F[i],mask=f.h.reduce((b,v)=>b|a.forms[v].mask,0n),h=a.free.flatMap((_,j)=>mask&bit(j)?[j]:[]);
  maxWidth=Math.max(maxWidth,h.length);
  if(h.length>3){wide++;continue;}
  const S=new Set();for(const z of U.tuples(2,h.length)){
   const w=h.reduce((b,v,j)=>b|(z[j]?bit(v):0n),0n);
   if(f.S.has(f.h.map(v=>parity(a.forms[v].mask&w)^a.forms[v].rhs).join()))S.add(z.join());
  }
  if(!h.length&&!S.size)return {a,kind:"constant-conflict",d:{k:1,m:2,F:[{h:[0],S:new Set()}]},expand:()=>{throw Error("UNSAT");}};
  if(h.length&&S.size!==2**h.length)F.push({h,S});
 }
 if(wide)return {a,kind:"wide-fallback",d,expand:z=>z,wide,maxWidth};
 // Merge duplicate scopes by intersection, preserving the exact relation.
 const merged=new Map();for(const f of F){const id=f.h.join();if(!merged.has(id))merged.set(id,f);else{const g=merged.get(id);for(const t of g.S)if(!f.S.has(t))g.S.delete(t);}}
 const out={k:Math.max(1,n),m:2,F:[...merged.values()]};
 if(!n)out.F.push({h:[0],S:new Set(["0"])});
 return {a,kind:"narrow",d:out,expand:z=>a.expand(n?z:[]),wide,maxWidth};
}
function solve(U,d){
 const r=reduce(U,d);
 if(r.kind==="contradiction"||r.kind==="constant-conflict")return {status:"UNSAT",z:null,used:0n,r};
 if(r.kind==="wide-fallback"){
  let used=0n;for(const t of U.tuples(2,r.a.free.length)){used++;const z=r.a.expand(t);if(d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))return {status:"SAT",z,used,r};}
  return {status:"UNSAT",z:null,used,r};
 }
 if(r.a.affine.every(Boolean))return {status:"SAT",z:r.a.expand(Array(r.a.free.length).fill(0)),used:0n,r};
 const s=U.solve(r.d);return {...s,z:s.z?r.expand(s.z):null,r};
}
function barrier(U,k){
 if(k<5)throw Error("k>=5");
 return {k,m:2,F:[...U.subsets(Array.from({length:k},(_,i)=>i),3)].map(h=>({h,S:new Set([...U.tuples(2,3)].filter(z=>z.some(x=>x!==z[0])).map(z=>z.join()))}))};
}
module.exports={equations,eliminate,reduce,solve,barrier};
