// D7M: tight weighted counting, parity quotient and independent stratum checking.
function verifyTight(d,c){
 const ok=b=>{if(!b)throw Error("invalid tight certificate");};
 ok(d.m===2&&c.kind==="tight"&&Array.isArray(c.factors)&&c.factors.length>0&&Array.isArray(c.sigma)&&c.sigma.length===d.k&&Array.from(c.sigma).every(x=>x===0||x===1)&&Number.isSafeInteger(c.threshold)&&c.threshold>0);
 const vs=new Set(),seen=new Set(),w=new Map();
 for(const i of c.factors){ok(Number.isSafeInteger(i)&&i>=0&&i<d.F.length&&!seen.has(i));seen.add(i);const {h,S}=d.F[i];ok(h.length===3&&new Set(h).size===3&&h.every(x=>Number.isSafeInteger(x)&&x>=0&&x<d.k));const b=h.map(x=>c.sigma[x]);ok(!S.has(b.join())&&!S.has(b.map(x=>1-x).join()));h.forEach(x=>vs.add(x));for(let a=0;a<3;a++)for(let b=a+1;b<3;b++){const x=Math.min(h[a],h[b]),y=Math.max(h[a],h[b]);if(!w.has(x))w.set(x,new Map());const m=w.get(x);m.set(y,(m.get(y)||0)+1);}}
 const a=[...vs].sort((x,y)=>x-y),v=BigInt(a.length),lo=v/2n,hi=v-lo,t=BigInt(c.threshold);let deficit=0n,nonzero=0;const eq=[];
 for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){const x=a[i],y=a[j],n=BigInt(w.get(x)?.get(y)||0);if(n)nonzero++;if(n<t)deficit+=t-n;if(n!==t)eq.push([x,y,c.sigma[x]^c.sigma[y]^+(n>t)]);}
 const lower=t*(lo*(lo-1n)/2n+hi*(hi-1n)/2n)-deficit;
 ok(lower===BigInt(seen.size)&&c.lower===String(lower)&&c.deficit===String(deficit)&&c.vertices===a.length&&c.pairs===nonzero&&c.triples===seen.size&&eq.length>0&&JSON.stringify(c.equations)===JSON.stringify(eq));return eq;
}

function reconstruct(d,blocks){
 if(!Array.isArray(blocks)||!blocks.length)throw Error("empty stratum");
 const adj=Array.from({length:d.k},()=>[]);
 for(const b of blocks)for(const [x,y,c] of verifyTight(d,b)){adj[x].push([y,c]);adj[y].push([x,c]);}
 const root=Array(d.k).fill(-1),sign=Array(d.k).fill(0);let n=0;
 for(let i=0;i<d.k;i++)if(root[i]<0){root[i]=n++;const q=[i];for(let j=0;j<q.length;j++){const x=q[j];for(const [y,c] of adj[x]){if(root[y]<0){root[y]=root[x];sign[y]=sign[x]^c;q.push(y);}else if(sign[y]!== (sign[x]^c))return {kind:"parity-conflict"};}}}
 const F=[];
 for(const f of d.F){const h=[...new Set(f.h.map(x=>root[x]))].sort((a,b)=>a-b),S=new Set();for(let m=0;m<2**h.length;m++){const z=h.map((_,i)=>Math.floor(m/2**i)%2);if(f.S.has(f.h.map(x=>z[h.indexOf(root[x])]^sign[x]).join()))S.add(z.join());}
  if(!S.size)return {kind:"factor-conflict"};if(S.size!==2**h.length)F.push({h,S});}
 return {kind:"view",d:{k:n,m:2,F},forms:root.map((r,i)=>[r,sign[i]])};
}

function verify(LV,d,r){
 if(!Array.isArray(r.rounds)||r.rounds.length>d.k)throw Error("round count");
 let view=d;
 for(let i=0;i<r.rounds.length;i++){const q=reconstruct(view,r.rounds[i]);if(q.kind!=="view"){if(i!==r.rounds.length-1||q.kind!==r.kind)throw Error("terminal");return true;}if(q.d.k>=view.k)throw Error("no progress");view=q.d;}
 if(r.kind==="count-conflict")return LV.verifyCount(view,r.proof);
 throw Error("no contradiction");
}
module.exports={verifyTight,reconstruct,verify};
