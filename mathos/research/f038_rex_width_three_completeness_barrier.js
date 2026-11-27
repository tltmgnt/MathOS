// D5Z: explicit infinite family separating full GAC and radius-two
// repair from completeness; host reference search, not physical solver.
function family(E,m,unsat=false){
 const B=[],groups=Array.from({length:9},(_,i)=>i);
 // Equality star forces every rank equal to group 0.
 for(let g=1;g<9;g++)for(const [a,b] of E.tup(m,2))if(a!==b)B.push([-(a+1),-(g*m+b+1)]);
 // Separate ternary factor forbids diagonal ranks except the last
 // (or all diagonals in the unsatisfiable variant).
 for(let a=0;a<m-(unsat?0:1);a++)B.push([-(a+1),-(m+a+1),-(2*m+a+1)]);
 return {m,B,pins:Array.from({length:m},(_,i)=>i%2),expected:unsat?null:groups.map(()=>m-1)};
}
// Complete host search of fixed-nine normalized family. Reject a partial
// assignment only once all variables of one factor are assigned.
function exact(E,raw){
 const d=E.decode(raw);if(!d)return {status:"OUTSIDE_NORMALIZED"};
 const by=Array.from({length:9},(_,i)=>d.F.filter(f=>Math.max(...f.h)===i)),z=[],out={status:"UNSAT",count:0,nodes:0,z:null,bits:null};
 function visit(i){
  if(i===9){out.count++;if(out.z===null)out.z=z.slice();return;}
  for(let a=0;a<d.m;a++){z[i]=a;out.nodes++;if(by[i].every(f=>f.S.has(f.h.map(g=>z[g]).join())))visit(i+1);}
 }
 visit(0);if(out.z){out.status="SAT";out.bits=E.witness(d.m,d.pins,out.z);if(!E.valid(raw,out.bits))throw Error("original witness");}
 return out;
}
function audit(E,Oracle,Old,U,W,Gap){
 const ok=(x,s)=>{if(!x)throw Error(s)},J=[U.machine(W,Gap,false),U.machine(W,Gap,true)],O=[Old.machine(false),Old.machine(true)];let cases=0,bruteTuples=0,refusals=0,satFalseNegatives=0,unsatRefusals=0,localChecks=0;const rows=[];
 for(let m=2;m<=5;m++)for(const unsat of [false,true]){
  const f=family(E,m,unsat),raw=E.encode(m,f.pins,f.B),d=E.decode(raw),r=exact(E,raw),s=Old.stream(E,raw);
  ok(d&&r.count===(unsat?0:1)&&JSON.stringify(r.z)===JSON.stringify(f.expected),"exact family");
  if(m<=4){let n=0;for(const z of E.tup(m,9)){if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join())))n++;bruteTuples++;}ok(n===r.count,"brute");}
  for(const f of d.F)for(let j=0;j<f.h.length;j++)for(let a=0;a<m;a++){ok([...f.S].some(s=>Number(s.split(",")[j])===a),"local support");localChecks++;}
  const ref=Oracle.oracle(E,raw,true);
  ok(ref.stable&&ref.rounds===1&&ref.deletions===0&&!ref.empty&&ref.z===null&&ref.domains.every(a=>a.length===m),"GAC barrier");
  for(let i=0;i<2;i++){const a=Old.executeIR(J[i],[...Array(21).fill(""),s]),b=Old.executeIR(O[i],[...Array(19).fill(""),s]);ok(a.status==="reject"&&b.status==="reject"&&a.tapes[0]===""&&b.tapes[0]==="","physical IR refusal");refusals++;if(unsat)unsatRefusals++;else satFalseNegatives++;}
  cases++;rows.push({m,unsat,clauses:f.B.length,L:raw.length,solutions:r.count,nodes:r.nodes,stable:ref.stable,rounds:ref.rounds,domains:ref.domains,rank:r.z});
 }
 return {cases,bruteTuples,localChecks,refusals,satFalseNegatives,unsatRefusals,rows};
}
module.exports={family,exact,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require('./f038_tga_normalized_integration.js').engine(),require(p+'sparse_audit.js'),require(p+'cost_ir.js'),require(p+'short_probe_ir.js'),require(p+'inplace_hybrid_gac_ir.js'),require(p+'persistent_gap_encoder.js'))));}
