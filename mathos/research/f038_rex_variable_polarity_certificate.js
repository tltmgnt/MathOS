// D7H: certified coordinate complements and mixed intermediate resolution chains.
function verifyMap(d,sigma,e){
 const ok=b=>{if(!b)throw Error("invalid polarity map");};
 ok(d.m===2&&e.m===2&&d.k===e.k&&Array.isArray(sigma)&&sigma.length===d.k&&sigma.every(x=>x===0||x===1)&&e.F.length===d.F.length);
 for(let i=0;i<d.F.length;i++){
  const a=d.F[i],b=e.F[i];ok(a.h.length===b.h.length&&a.h.every((x,j)=>x===b.h[j])&&a.S.size===b.S.size);
  for(let n=0;n<2**a.h.length;n++){const y=a.h.map((_,j)=>(n>>j)&1),x=y.map((v,j)=>(v+sigma[a.h[j]])%2);ok(a.S.has(x.join())===b.S.has(y.join()));}
 }return true;
}

function verify(HV,d,cert){
 const ok=b=>{if(!b)throw Error("invalid signed Hall certificate");};
 if(cert.kind==="hall")return HV.verify(d,cert.hall);
 ok(["polarity-hall","signed-hall"].includes(cert.kind)&&Array.isArray(cert.sigma)&&cert.sigma.length===d.k&&cert.sigma.every(x=>x===0||x===1));
 const h=cert.hall,s=cert.sigma;
 // Reconstruct normalized factor truth tables independently of the producer.
 const e={k:d.k,m:2,F:d.F.map(f=>{const S=new Set();for(let n=0;n<2**f.h.length;n++){const y=f.h.map((_,j)=>(n>>j)&1);if(f.S.has(y.map((v,j)=>(v+s[f.h[j]])%2).join()))S.add(y.join());}return {h:f.h.slice(),S};})};
 ok(verifyMap(d,s,e));
 if(cert.kind==="polarity-hall")return HV.verify(e,h);
 ok(h.kind==="hall"&&h.sign===1&&Array.isArray(h.groups)&&Array.isArray(h.holes)&&Array.isArray(h.exclusions));
 function axiom(a){
  ok(a&&Number.isSafeInteger(a.f)&&a.f>=0&&a.f<d.F.length&&Array.isArray(a.c));
  const f=d.F[a.f];ok(a.c.length===f.h.length&&f.h.every(x=>a.c.filter(y=>Number.isSafeInteger(y)&&Math.abs(y)===x+1).length===1));
  // Test the raw forbidden row rather than trusting a normalized producer table.
  ok(!f.S.has(f.h.map(x=>((a.c.includes(x+1)?0:1)+s[x])%2).join()));return a.c;
 }
 const owner=new Map();
 for(let i=0;i<h.groups.length;i++){
  const g=h.groups[i];ok(Array.isArray(g.proof)&&g.proof.length>0&&Array.isArray(g.options)&&g.options.length>0);
  let clause=new Set(axiom(g.proof[0]));
  for(const a of g.proof.slice(1)){const b=axiom(a),p=a.p;ok(Number.isSafeInteger(p)&&clause.has(p)&&b.includes(-p));clause.delete(p);for(const x of b)if(x!==-p)clause.add(x);ok([...clause].every(x=>!clause.has(-x)));}
  ok(clause.size===g.options.length&&g.options.every(x=>x>0&&clause.has(x)));
  for(const x of g.options){ok(!owner.has(x));owner.set(x,i);}
 }
 const placed=new Set(),mutex=new Map();
 for(const a of h.exclusions){const c=axiom(a);ok(c.length===2&&c.every(x=>x<0));const [x,y]=c.map(x=>-x);ok(owner.has(x)&&owner.has(y)&&owner.get(x)!==owner.get(y));if(!mutex.has(x))mutex.set(x,new Set());if(!mutex.has(y))mutex.set(y,new Set());mutex.get(x).add(y);mutex.get(y).add(x);}
 for(const q of h.holes){ok(Array.isArray(q)&&q.length>0);for(let i=0;i<q.length;i++){const x=q[i];ok(owner.has(x)&&!placed.has(x));placed.add(x);for(let j=0;j<i;j++)if(owner.get(x)!==owner.get(q[j]))ok(mutex.get(x)?.has(q[j]));}}
 ok(placed.size===owner.size&&h.holes.length<h.groups.length);return true;
}
module.exports={verifyMap,verify};
