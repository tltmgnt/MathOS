// FV-04: translate actual D7I proof packets to the untrusted raw Lean boundary.
// No producer, JS verifier, or exporter is trusted by the Lean acceptance theorem.
const IV=require('./f038_rex_variable_implied_certificate.js');
const NV=require('./f038_rex_variable_polarity_certificate.js');
const HV=require('./f038_rex_variable_hall_certificate.js');
function exportPacket(d,cert){
 const check=(b,m)=>{if(!b)throw Error("FV04 export: "+m);};
 check(d&&d.m===2&&Number.isSafeInteger(d.k)&&d.k>=0&&Array.isArray(d.F),"instance");
 const lit=l=>{check(Number.isSafeInteger(l)&&l!==0&&Math.abs(l)<=d.k,"literal");return l;};
 const rawFactor=f=>{
  check(Array.isArray(f.h)&&new Set(f.h).size===f.h.length&&f.h.every(i=>Number.isSafeInteger(i)&&i>=0&&i<d.k)&&f.S instanceof Set,"scope");
  const rows=[...f.S].map(s=>{
   check(typeof s==="string","row");
   const a=s===""?[]:s.split(",");
   check(a.length===f.h.length&&a.every(v=>v==="0"||v==="1"),"row");
   return a.map(v=>v==="1");
  });
  return {scope:f.h.slice(),rows};
 };
 const factors=d.F.map(rawFactor);
 check(cert&&cert.kind==="implied-hall"&&IV.verify(NV,HV,d,cert)===true,"D7I certificate");
 const projected=IV.reconstruct(d,cert);
 const pFactors=projected.F.map(rawFactor);
 const source=(index,row)=>({kind:"source",index,row});
 const paths=cert.paths.map(p=>({
  left:lit(p.x),right:lit(p.y),
  steps:p.edges.map(e=>({
   next:lit(e.to),proof:source(e.f,d.F[e.f].h.map(v=>v===Math.abs(e.from)-1?e.from>0:e.to<0))
  }))
 }));
 const wrapper=cert.hall,h=wrapper.hall;
 const sigma=wrapper.kind==="hall"?Array(d.k).fill(0):wrapper.sigma;
 const signed=wrapper.kind==="signed-hall";
 const unflip=l=>{lit(l);return sigma[Math.abs(l)-1]?-l:l;};
 // Convert every normalized clause and pivot back to original coordinates.
 const axiom=a=>{
  const f=pFactors[a.f],c=a.c.map(unflip);
  check(f&&c.length===f.scope.length&&f.scope.every(v=>c.filter(l=>Math.abs(l)===v+1).length===1),"axiom");
  return source(a.f,f.scope.map(v=>!c.includes(v+1)));
 };
 const groups=h.groups.map(g=>{
  let proof=axiom(g.proof[0]);
  for(const a of g.proof.slice(1)){
   const pivot=signed?a.p:-a.c.find(l=>l*h.sign<0);
   proof={kind:"resolution",left:proof,right:axiom(a),pivot:unflip(pivot)};
  }
  return {options:g.options.map(unflip),proof};
 });
 const placements=h.holes.flatMap((q,j)=>q.map(l=>[unflip(l),j]));
 const conflicts=h.exclusions.flatMap(a=>{
  const [l,r]=a.c.map(x=>-unflip(x)),proof=axiom(a);
  return [{left:l,right:r,steps:[{next:-r,proof}]},{left:r,right:l,steps:[{next:-l,proof}]}];
 });
 return {n:d.k,factors,packet:{retained:cert.nonbinary.slice(),paths,holeCount:h.holes.length,groups,placements,conflicts}};
}
// Serialize only validated numeric/Boolean data and fixed constructors, not user code.
function leanFixture(data,name="Generated"){
 if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(name))throw Error("Lean identifier");
 const num=x=>{if(!Number.isSafeInteger(x))throw Error("integer");return x<0?"("+x+")":String(x);};
 const nat=x=>{if(x<0)throw Error("natural");return num(x);};
 const bool=x=>{if(typeof x!=="boolean")throw Error("Boolean");return String(x);};
 const list=(xs,f)=>"["+xs.map(f).join(", ")+"]";
 const row=r=>list(r,bool);
 const proof=p=>p.kind==="source"?"(.source "+nat(p.index)+" "+row(p.row)+")":
  p.kind==="resolution"?"(.resolution "+proof(p.left)+" "+proof(p.right)+" "+num(p.pivot)+")":(()=>{throw Error("proof");})();
 const conflict=c=>"⟨"+num(c.left)+", "+num(c.right)+", "+list(c.steps,s=>"("+num(s.next)+", "+proof(s.proof)+")")+"⟩";
 const group=g=>"⟨"+list(g.options,num)+", "+proof(g.proof)+"⟩";
 const f=data.factors.map(x=>"  ⟨"+list(x.scope,nat)+", "+list(x.rows,row)+"⟩").join(",\n");
 const p=data.packet;
 return "import F038Formal.Bridge\n\nnamespace MathOS.F038.Bridge."+name+"\nopen MathOS.F038.Bridge\nset_option maxRecDepth 10000\nset_option maxHeartbeats 0\n\ndef factors : List RawFactor := [\n"+f+"\n]\n\ndef packet : RawPacket := {\n  retained := "+list(p.retained,nat)+"\n  paths := "+list(p.paths,conflict)+"\n  holeCount := "+nat(p.holeCount)+"\n  groups := "+list(p.groups,group)+"\n  placements := "+list(p.placements,([l,j])=>"("+num(l)+", "+nat(j)+")")+"\n  conflicts := "+list(p.conflicts,conflict)+"\n}\n\nexample : rawCheck "+nat(data.n)+" factors packet = true := by decide\ntheorem exported_unsat : ¬ ∃ x, RawModels factors x := rawCheck_sound "+nat(data.n)+" factors packet (by decide)\n#print axioms exported_unsat\nend MathOS.F038.Bridge."+name+"\n";
}
module.exports={exportPacket,leanFixture};
