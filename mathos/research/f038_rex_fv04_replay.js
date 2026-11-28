// FV-04 executable replay oracle for the raw boundary. Independent from D7I
// graph discovery, original verifiers and exporter. Not a Lean execution.
function replay(data){
 const {n,factors,packet:p}=data;
 const ok=(b,m)=>{if(!b)throw Error("FV04 replay: "+m);};
 const lit=l=>{ok(Number.isSafeInteger(l)&&l!==0&&Math.abs(l)<=n,"literal");return l;};
 const nat=x=>Number.isSafeInteger(x)&&x>=0;
 const key=x=>x.join(",");
 const row=r=>{ok(Array.isArray(r)&&r.every(x=>typeof x==="boolean"),"row");return r;};
 ok(nat(n)&&Array.isArray(factors),"instance");
 const tables=factors.map(f=>{
  ok(Array.isArray(f.scope)&&f.scope.every(x=>nat(x)&&x<n),"scope");
  ok(Array.isArray(f.rows)&&f.rows.every(r=>row(r).length===f.scope.length),"rows");
  return {scope:f.scope,rows:f.rows};
 });
 const get=(fs,i)=>{ok(nat(i)&&i<fs.length,"factor index");return fs[i];};
 function derive(fs,p){
  if(p.kind==="source"){
   const f=get(fs,p.index),r=row(p.row);
   ok(r.length===f.scope.length&&!f.rows.some(x=>key(x)===key(r)),"source");
   return f.scope.map((v,i)=>r[i]?-(v+1):v+1);
  }
  ok(p.kind==="resolution","proof kind");const pivot=lit(p.pivot);
  return derive(fs,p.left).filter(l=>l!==pivot).concat(derive(fs,p.right).filter(l=>l!==-pivot));
 }
 function clause(fs,proof,target){ok(derive(fs,proof).every(l=>target.includes(l)),"clause");}
 function path(fs,c){
  let at=lit(c.left);lit(c.right);
  for(const s of c.steps){const to=lit(s.next);clause(fs,s.proof,[-at,to]);at=to;}
  ok(at===-c.right,"endpoint");
 }
 const projected=p.retained.map(i=>get(tables,i));
 for(const c of p.paths){
  path(tables,c);
  const rows=[];for(const a of [false,true])for(const b of [false,true])if(a!==(c.left>0)||b!==(c.right>0))rows.push([a,b]);
  projected.push({scope:[Math.abs(c.left)-1,Math.abs(c.right)-1],rows});
 }
 ok(nat(p.holeCount)&&p.holeCount<p.groups.length,"deficiency");
 for(const [l,j] of p.placements){lit(l);ok(nat(j)&&j<p.holeCount,"placement");}
 const hole=l=>p.placements.find(q=>q[0]===l)?.[1];
 for(const g of p.groups){g.options.forEach(lit);clause(projected,g.proof,g.options);ok(g.options.every(l=>hole(l)!==undefined),"coverage");}
 for(let i=0;i<p.groups.length;i++)for(let j=0;j<p.groups.length;j++)if(i!==j)
  for(const a of p.groups[i].options)for(const b of p.groups[j].options)if(hole(a)===hole(b)){
   const candidates=p.conflicts.filter(c=>c.left===a&&c.right===b);
   ok(candidates.some(c=>{try{path(projected,c);return true;}catch{return false;}}),"conflict");
  }
 return true;
}
module.exports={replay};
