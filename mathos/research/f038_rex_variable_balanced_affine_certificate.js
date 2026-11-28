// D7N: locally oriented tight balance equations and GF(2) contradiction certificates.
function checkBlock(d,b){
 const ok=x=>{if(!x)throw Error("invalid balanced block");};
 ok(d.m===2&&b&&["tight","strict"].includes(b.kind)&&Array.isArray(b.factors)&&b.factors.length&&Array.isArray(b.coords)&&Array.isArray(b.sigma)&&b.sigma.length===b.coords.length&&Array.from(b.sigma).every(x=>x===0||x===1)&&Number.isSafeInteger(b.threshold)&&b.threshold>0);
 const vs=new Set(),seen=new Set(),weights=new Map(),sign=new Map();
 for(let j=0;j<b.coords.length;j++){const x=b.coords[j];ok(Number.isSafeInteger(x)&&x>=0&&x<d.k&&(j===0||b.coords[j-1]<x));sign.set(x,b.sigma[j]);}
 for(const i of b.factors){ok(Number.isSafeInteger(i)&&i>=0&&i<d.F.length&&!seen.has(i));seen.add(i);const {h,S}=d.F[i];ok(h.length===3&&new Set(h).size===3&&h.every(x=>sign.has(x)));const z=h.map(x=>sign.get(x));ok(!S.has(z.join())&&!S.has(z.map(x=>1-x).join()));for(const x of h){vs.add(x);if(!weights.has(x))weights.set(x,new Map());}for(let a=0;a<3;a++)for(let c=a+1;c<3;c++){const x=Math.min(h[a],h[c]),y=Math.max(h[a],h[c]),m=weights.get(x);m.set(y,(m.get(y)||0)+1);}}
 ok(vs.size===b.coords.length);
 const v=BigInt(vs.size),a=v/2n,c=v-a,t=BigInt(b.threshold),pairs=[];let deficit=0n;
 for(let i=0;i<b.coords.length;i++)for(let j=i+1;j<b.coords.length;j++){const x=b.coords[i],y=b.coords[j],w=BigInt(weights.get(x).get(y)||0);if(w<t)deficit+=t-w;if(w!==t)pairs.push({h:[x,y],rhs:sign.get(x)^sign.get(y)^+(w>t)});}
 const lower=t*(a*(a-1n)/2n+c*(c-1n)/2n)-deficit;
 ok(b.lower===String(lower)&&b.deficit===String(deficit)&&(b.kind==="strict"?lower>BigInt(seen.size):lower===BigInt(seen.size)));
 if(b.kind==="strict")return [];
 if(v%2n===0n)pairs.push({h:b.coords,rhs:Number(a%2n)^b.sigma.reduce((s,x)=>s^x,0)});
 return pairs;
}

function checkLocal(d,b){
 const ok=x=>{if(!x)throw Error("invalid local affine row");};ok(b&&b.kind==="local"&&Number.isSafeInteger(b.factor)&&b.factor>=0&&b.factor<d.F.length&&Array.isArray(b.h)&&(b.rhs===0||b.rhs===1));
 const f=d.F[b.factor];ok(b.h.every((x,i)=>f.h.includes(x)&&(i===0||b.h[i-1]<x)));
 for(const s of f.S){const z=s.split(",").map(Number);ok(b.h.reduce((a,x)=>a^z[f.h.indexOf(x)],0)===b.rhs);}
 return [{h:b.h,rhs:b.rhs}];
}

function verify(d,r){
 const ok=x=>{if(!x)throw Error("invalid balanced affine certificate");};ok(d.m===2&&r);
 if(r.kind==="count-conflict"){ok(r.block.kind==="strict");checkBlock(d,r.block);return true;}
 ok(r.kind==="affine-conflict"&&Array.isArray(r.blocks)&&Array.isArray(r.rows)&&Array.isArray(r.combination)&&r.combination.length>0);
 const allowed=r.blocks.map(b=>{ok(b.kind!=="strict");return (b.kind==="local"?checkLocal(d,b):checkBlock(d,b)).map(q=>q.h.join()+":"+q.rhs);});
 for(const q of r.rows){ok(q&&Number.isSafeInteger(q.source)&&q.source>=0&&q.source<allowed.length&&Array.isArray(q.h)&&(q.rhs===0||q.rhs===1)&&q.h.every((x,i)=>Number.isSafeInteger(x)&&x>=0&&x<d.k&&(i===0||q.h[i-1]<x))&&allowed[q.source].includes(q.h.join()+":"+q.rhs));}
 const bits=new Uint8Array(d.k),seen=new Set();let rhs=0;
 for(const i of r.combination){ok(Number.isSafeInteger(i)&&i>=0&&i<r.rows.length&&!seen.has(i));seen.add(i);const q=r.rows[i];for(const x of q.h)bits[x]^=1;rhs^=q.rhs;}
 ok(rhs===1&&bits.every(x=>x===0));return true;
}
module.exports={checkBlock,checkLocal,verify};
