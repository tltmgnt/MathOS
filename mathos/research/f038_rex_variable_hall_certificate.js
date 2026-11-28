// D7E: certified extraction of Hall-deficient option systems.
function verify(d,cert){
 const ok=b=>{if(!b)throw Error("invalid Hall certificate");};
 ok(d.m===2&&cert.kind==="hall"&&[1,-1].includes(cert.sign)&&Array.isArray(cert.groups)&&Array.isArray(cert.holes)&&Array.isArray(cert.exclusions));
 function axiom(a){
  ok(a&&Number.isSafeInteger(a.f)&&a.f>=0&&a.f<d.F.length&&Array.isArray(a.c));
  const f=d.F[a.f];ok(a.c.length===f.h.length&&f.h.every(x=>a.c.filter(y=>Number.isSafeInteger(y)&&Math.abs(y)===x+1).length===1));
  ok(!f.S.has(f.h.map(x=>a.c.includes(x+1)?0:1).join()));return a.c;
 }
 const owner=new Map();
 cert.groups.forEach((g,i)=>{
  ok(Array.isArray(g.proof)&&g.proof.length>0&&Array.isArray(g.options)&&g.options.length>0);
  let clause=new Set(axiom(g.proof[0]));ok([...clause].every(x=>x*cert.sign>0));
  for(const a of g.proof.slice(1)){
   const b=axiom(a),opp=b.filter(x=>x*cert.sign<0);
   ok(opp.length===1&&clause.has(-opp[0]));clause.delete(-opp[0]);for(const x of b)if(x!==opp[0])clause.add(x);
  }
  ok(clause.size===g.options.length&&g.options.every(x=>clause.has(x)));
  for(const x of g.options){ok(!owner.has(x));owner.set(x,i);}
 });
 const placed=new Set(),mutex=new Map();
 for(const a of cert.exclusions){const c=axiom(a);ok(c.length===2&&c.every(x=>x*cert.sign<0));const [x,y]=c.map(x=>-x);ok(owner.has(x)&&owner.has(y)&&owner.get(x)!==owner.get(y));if(!mutex.has(x))mutex.set(x,new Set());if(!mutex.has(y))mutex.set(y,new Set());mutex.get(x).add(y);mutex.get(y).add(x);}
 for(const hole of cert.holes){ok(Array.isArray(hole)&&hole.length>0);
  for(let i=0;i<hole.length;i++){const x=hole[i];ok(owner.has(x)&&!placed.has(x));placed.add(x);
   for(let j=0;j<i;j++)if(owner.get(x)!==owner.get(hole[j]))ok(mutex.get(x)?.has(hole[j]));
  }
 }
 ok(placed.size===owner.size&&cert.holes.length<cert.groups.length);return true;
}
module.exports={verify};
