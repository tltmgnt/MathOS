// D6Y: uniform variable-coordinate normalized selector representation.
// Host reference only: does not compile a variable-k physical worker.
const assert=(v,s)=>{if(!v)throw Error(s)};
function dims(k,m){
 assert(Number.isSafeInteger(k)&&k>=1&&Number.isSafeInteger(m)&&m>=2,"dimensions");
 const n=(2n*BigInt(k)+1n)*BigInt(m)-BigInt(k)+2n;assert(n<=BigInt(Number.MAX_SAFE_INTEGER),"n");return Number(n);
}
function length(n){const N=BigInt(n);return N+1n+2n*N*N+8n*N*(N-1n)*(N-2n)/6n;}
function* subsets(a,r,i=0){
 if(!r){yield [];return;}
 for(let j=i;j<=a.length-r;j++)for(const b of subsets(a,r-1,j+1))yield [a[j],...b];
}
function* tuples(m,k){
 const a=Array(k).fill(0);
 for(;;){yield a.slice();let j=k-1;while(j>=0&&++a[j]===m){a[j]=0;j--;}if(j<0)return;}
}
function* pool(n){
 const a=Array.from({length:n},(_,i)=>i+1);
 for(let r=1;r<=3;r++)for(const h of subsets(a,r))for(const z of tuples(2,r))yield h.map((v,i)=>z[i]?v:-v);
}
const key=c=>c.slice().sort((a,b)=>Math.abs(a)-Math.abs(b)).join(",");
function fixed(k,m,pins=null){
 const n=dims(k,m),F=[];
 if(pins!==null)assert(pins.length===m&&pins.every(x=>x===0||x===1),"pins");
 for(let g=0;g<k;g++){
  const X=Array.from({length:m},(_,j)=>g*m+j+1),Y=Array.from({length:m-1},(_,j)=>k*m+g*(m-1)+j+1);
  for(const [a,b] of subsets(X,2))F.push([-a,-b]);
  for(let j=0;j<Y.length;j++){const a=j?Y[j-1]:X[0],b=X[j+1],y=Y[j];F.push([-a,y],[-b,y],[a,b,-y]);}
  F.push([Y.at(-1)]);
 }
 F.push([1-n],[-n]);
 if(pins)for(let i=0;i<m;i++){const p=n-m-1+i;for(const a of [1-n,n-1])for(const z of [-n,n])F.push([pins[i]?p:-p,a,z]);}
 return F;
}
function encode(k,m,pins,B){
 assert(Array.isArray(pins)&&pins.length===m&&pins.every(x=>x===0||x===1),"pins");
 const n=dims(k,m),F=new Set(fixed(k,m,pins).map(key));
 for(const c of B){
  assert(c.length>=1&&c.length<=3&&c.every(x=>Number.isInteger(x)&&x<0&&-x<=k*m),"optional clause");
  assert(new Set(c.map(x=>Math.floor((-x-1)/m))).size===c.length,"scope");
  F.add(key(c));
 }
 const out=["1".repeat(n),"0"];for(const c of pool(n))out.push(F.has(key(c))?"1":"0");
 return out.join("");
}
function decode(k,m,raw){
 const n=dims(k,m);
 if(BigInt(raw.length)!==length(n)||raw.slice(0,n+1)!=="1".repeat(n)+"0"||!/^[01]+$/.test(raw))return null;
 const required=new Set(fixed(k,m).map(key)),pins=Array.from({length:m},()=>[0,0]),F=new Map();let j=n+1;
 for(const c of pool(n)){
  if(raw[j++]==="0")continue;
  if(required.delete(key(c)))continue;
  if(c.length===3&&Math.abs(c[0])>=n-m-1&&Math.abs(c[0])<=n-2&&Math.abs(c[1])===n-1&&Math.abs(c[2])===n){pins[Math.abs(c[0])-(n-m-1)][+(c[0]>0)]++;continue;}
  if(!c.every(x=>x<0&&-x<=k*m))return null;
  const h=c.map(x=>Math.floor((-x-1)/m)),z=c.map(x=>(-x-1)%m);
  if(new Set(h).size!==h.length)return null;
  const id=h.join();if(!F.has(id))F.set(id,{h,bad:new Set()});F.get(id).bad.add(z.join());
 }
 if(required.size||pins.some(([a,b])=>!(a===4&&b===0||a===0&&b===4)))return null;
 return {k,m,n,pins:pins.map(v=>+(v[1]===4)),F:[...F.values()].map(f=>({h:f.h,S:new Set([...tuples(m,f.h.length)].map(z=>z.join()).filter(z=>!f.bad.has(z)))}))};
}
function witness(k,m,pins,z){
 assert(Array.isArray(pins)&&pins.length===m&&pins.every(x=>x===0||x===1),"pins");
 const n=dims(k,m),b=Array(n).fill(0);
 assert(z.length===k&&z.every(v=>Number.isInteger(v)&&v>=0&&v<m),"ranks");
 for(let g=0;g<k;g++){b[g*m+z[g]]=1;for(let j=0;j<m-1;j++)b[k*m+g*(m-1)+j]=+(z[g]<=j+1);}
 for(let i=0;i<m;i++)b[n-m-2+i]=pins[i];
 return b.join("");
}
function lift(k,clauses){
 // Source variables are explicitly indexed 1..k (k part of unary input
 // or renumbered to the occurring variables). Duplicates/tautologies handled.
 dims(k,2);const B=[];
 for(const c of clauses){
  assert(c.length<=3&&c.every(x=>Number.isInteger(x)&&x!==0&&Math.abs(x)<=k),"source clause");
  const u=[...new Set(c)];
  if(u.some(x=>u.includes(-x)))continue;
  if(!u.length){B.push([-1],[-2]);continue;}
  B.push(u.map(x=>-(2*(Math.abs(x)-1)+(x<0?1:0)+1)));
 }
 return {k,m:2,B,raw:encode(k,2,[0,0],B)};
}
function project(k,bits){
 if(bits.length!==dims(k,2)||!/^[01]+$/.test(bits))return null;
 const z=[];for(let g=0;g<k;g++){const s=bits.slice(2*g,2*g+2);if(s!=="10"&&s!=="01")return null;z.push(+(s==="01"));}
 return z;
}
// Uniform source interface: renumber occurring variable identifiers,
// never allocate according to the largest identifier. Signed decimal
// strings allow identifiers larger than machine integers.
function reduce(clauses){
 assert(Array.isArray(clauses),"formula");
 const parse=x=>{assert(typeof x==="string"&&/^-?[1-9][0-9]*$/.test(x)||typeof x==="number"&&Number.isSafeInteger(x)&&x!==0||typeof x==="bigint"&&x!==0n,"literal");return BigInt(x);};
 const C=clauses.map(c=>{assert(Array.isArray(c)&&c.length<=3,"width");return c.map(parse);});
 const abs=x=>x<0n?-x:x,variables=[...new Set(C.flat().map(x=>abs(x)))].sort((a,b)=>a<b?-1:a>b?1:0).map(String);
 const ids=new Map(variables.map((v,i)=>[v,i+1])),k=Math.max(1,variables.length);
 const compact=C.map(c=>c.map(x=>(x<0n?-1:1)*ids.get(String(abs(x)))));
 // Zero-variable case: force a dummy Boolean variable false,
 // preserving one extension of the empty satisfying assignment.
 if(!variables.length)compact.push([-1]);
 return {...lift(k,compact),variables};
}
function projectSource(R,bits){
 const z=project(R.k,bits);if(!z)return null;
 if(!R.variables.length&&z[0]!==0)return null;
 return R.variables.map((id,i)=>({id,value:z[i]}));
}
const pass=(f,z)=>f.S.has(f.h.map(v=>z[v]).join());
function gac(d){
 const D=Array.from({length:d.k},()=>new Set(Array.from({length:d.m},(_,i)=>i)));let passes=0,deletions=0;
 for(;;){let changed=false;passes++;
  for(const f of d.F)for(let i=0;i<f.h.length;i++)for(const a of [...D[f.h[i]]]){
   let support=false;for(const t of f.S){const q=t.split(",").map(Number);if(q[i]===a&&q.every((v,j)=>D[f.h[j]].has(v))){support=true;break;}}
   if(!support){D[f.h[i]].delete(a);deletions++;changed=true;}
  }
  if(!changed||D.some(s=>!s.size))return {D,passes,deletions};
 }
}
function residual(d,vertices,S){
 const removed=new Set(S),adj=new Map(vertices.filter(v=>!removed.has(v)).map(v=>[v,new Set()]));
 for(const f of d.F){const h=f.h.filter(v=>adj.has(v));for(const a of h)for(const b of h)if(a!==b)adj.get(a).add(b);}
 const out=[],seen=new Set();for(const v of adj.keys())if(!seen.has(v)){const b=[v];seen.add(v);for(let i=0;i<b.length;i++)for(const w of adj.get(b[i]))if(!seen.has(w)){seen.add(w);b.push(w);}out.push(b.sort((a,b)=>a-b));}
 return out;
}
function plan(d,c,h=2){
 assert(Number.isInteger(h)&&h>=0&&h<=2,"fixed separator cap");
 const m=BigInt(d.m),base=m**BigInt(c.length);let best={S:[],blocks:[c],bound:base},trials=0;
 for(let r=1;r<=Math.min(h,c.length);r++)for(const S of subsets(c,r)){trials++;const blocks=residual(d,c,S);if(blocks.length<2)continue;
  const bound=m**BigInt(r)*(1n+blocks.reduce((a,b)=>a+m**BigInt(b.length),0n));if(bound<best.bound)best={S,blocks,bound};
 }
 return {...best,trials};
}
function solve(d){
 const z=Array(d.k).fill(0),plans=[];let used=0n,ceiling=0n;
 const cs=residual(d,[...z.keys()],[]);for(const c of cs){const p=plan(d,c);plans.push(p);ceiling+=p.bound;}
 const less=(a,b)=>{if(!b)return true;for(let i=0;i<a.length;i++)if(a[i]!==b[i])return a[i]<b[i];return false;};
 for(let j=0;j<cs.length;j++){
  const c=cs[j],p=plans[j],fs=d.F.filter(f=>c.includes(f.h[0]));let best=null,local=0n;
  if(!p.S.length){
   for(const q of tuples(d.m,c.length)){local++;c.forEach((v,i)=>z[v]=q[i]);if(fs.every(f=>pass(f,z))){best=q;break;}}
  }else{
   const sep=fs.filter(f=>f.h.every(v=>p.S.includes(v))),parts=p.blocks.map(b=>fs.filter(f=>f.h.some(v=>b.includes(v))));
   for(const a of tuples(d.m,p.S.length)){local++;p.S.forEach((v,i)=>z[v]=a[i]);if(!sep.every(f=>pass(f,z)))continue;
    let good=true;for(let i=0;i<p.blocks.length;i++){const b=p.blocks[i];let hit=false;for(const q of tuples(d.m,b.length)){local++;b.forEach((v,j)=>z[v]=q[j]);if(parts[i].every(f=>pass(f,z))){hit=true;break;}}if(!hit){good=false;break;}}
    if(good){const q=c.map(v=>z[v]);if(less(q,best))best=q;}
   }
  }
  assert(local<=p.bound,"candidate ceiling");used+=local;if(!best)return {status:"UNSAT",z:null,used,ceiling,plans};c.forEach((v,i)=>z[v]=best[i]);
 }
 assert(d.F.every(f=>pass(f,z)),"witness");return {status:"SAT",z,used,ceiling,plans};
}
function denseBarrier(k,m){
 assert(k>=4,"barrier k");const B=[];
 for(const [a,b] of subsets(Array.from({length:k},(_,i)=>i),2))for(const [x,y] of tuples(m,2))if(x!==y)B.push([-(a*m+x+1),-(b*m+y+1)]);
 for(let x=0;x<m;x++)B.push([-(x+1),-(m+x+1),-(2*m+x+1)]);
 return B;
}
module.exports={dims,length,pool,subsets,tuples,fixed,encode,decode,witness,lift,project,reduce,projectSource,gac,residual,plan,solve,denseBarrier};
