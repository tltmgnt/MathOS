// D7D: budgeted host inference, fixed-width subsumption closure and tree certificates.
function verifyTree(d,cert){
 const ok=b=>{if(!b)throw Error("invalid tree certificate");};
 ok(d.m===2&&cert.kind==="tree");const z=Array(d.k).fill(-1);
 const value=x=>z[Math.abs(x)-1]<0?-1:+(z[Math.abs(x)-1]===+(x>0));
 function axiom(c,f){ok(Number.isSafeInteger(f)&&f>=0&&f<d.F.length&&Array.isArray(c));const a=d.F[f];ok(c.length===a.h.length&&a.h.every(x=>c.filter(y=>Number.isSafeInteger(y)&&Math.abs(y)===x+1).length===1));ok(!a.S.has(a.h.map(x=>c.includes(x+1)?0:1).join()));}
 function go(n){ok(n&&typeof n==="object");
  if(n.type==="conflict"){axiom(n.c,n.f);ok(n.c.every(x=>value(x)===0));return;}
  if(n.type==="unit"){axiom(n.c,n.f);ok(n.c.includes(n.p)&&value(n.p)===-1&&n.c.every(x=>x===n.p||value(x)===0));const v=Math.abs(n.p)-1;z[v]=+(n.p>0);go(n.child);z[v]=-1;return;}
  ok(n.type==="split"&&Number.isSafeInteger(n.v)&&n.v>=0&&n.v<d.k&&z[n.v]===-1);z[n.v]=0;go(n.zero);z[n.v]=1;go(n.one);z[n.v]=-1;
 }
 go(cert.root);return true;
}

function verifyClosure(d,cert){
 const ok=b=>{if(!b)throw Error("invalid closure witness");};
 const w=cert.width,L=cert.closure;ok(d.m===2&&cert.reason==="saturated"&&[3,4].includes(w)&&Array.isArray(L));
 const keys=new Set();let axioms=0,pairs=0,eligible=0;
 function key(c){return c.slice().sort((a,b)=>Math.abs(a)-Math.abs(b)).join();}
 for(const c of L){ok(Array.isArray(c)&&c.length>0&&c.length<=w&&c.every((x,i)=>Number.isSafeInteger(x)&&x!==0&&Math.abs(x)<=d.k&&(!i||Math.abs(x)>Math.abs(c[i-1]))));ok(!keys.has(c.join()));keys.add(c.join());}
 function covered(c){for(let m=1;m<2**c.length;m++){const s=[];for(let i=0;i<c.length;i++)if(m>>i&1)s.push(c[i]);if(keys.has(key(s)))return true;}return false;}
 for(const f of d.F)for(let m=0;m<2**f.h.length;m++){const row=f.h.map((_,i)=>m>>i&1);if(!f.S.has(row.join())){axioms++;ok(covered(f.h.map((x,i)=>row[i]?-(x+1):x+1)));}}
 // Independent all-pairs scan using two-pointer merge on signed literals sorted by variable.
 for(let i=0;i<L.length;i++)for(let j=0;j<i;j++){pairs++;const a=L[i],b=L[j];let p=0,same=0,x=0,y=0;
  while(x<a.length&&y<b.length){const av=Math.abs(a[x]),bv=Math.abs(b[y]);if(av<bv)x++;else if(av>bv)y++;else{if(a[x]===b[y])same++;else p++;x++;y++;}}
  if(p!==1||a.length+b.length-2-same>w)continue;eligible++;
  const c=[...a.filter(x=>!b.includes(-x)),...b.filter(x=>!a.includes(x)&&!a.includes(-x))];ok(covered(c));
 }
 return {axioms,pairs,eligible,clauses:L.length};
}
module.exports={verifyTree,verifyClosure};
