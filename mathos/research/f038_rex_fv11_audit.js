// FV-11: concrete D7A closure logs, independent direct matching audit,
// actual derived-pair export, and Lean proof generation.
const U=require('./f038_rex_variable_rank_reduction.js');
const R=require('./f038_rex_variable_relational_closure.js');
const V=require('./f038_rex_variable_relational_certificate.js');
const A=require('./f038_rex_variable_affine_closure.js');
const L=require('./f038_rex_fv09_local.js');
const E=require('./f038_rex_fv10_export.js');
const ok=(b,s)=>{if(!b)throw Error("FV11 "+s);};
const f=(h,rows)=>({h,S:new Set(rows)});
const d=(k,F)=>({k,m:2,F});
const eq=["0,0","1,1"],ne=["0,1","1,0"],non=["0,0","0,1","1,0"];
const fixtures={
 chain:d(3,[f([0,1],eq),f([1,2],ne),f([2],["1"])]),
 contradiction:d(2,[f([0,1],eq),f([0],["0"]),f([1],["1"])]),
 empty:d(1,[f([0],[])]),
 stable:d(3,[f([0,1],non),f([1,2],non)]),
 derived:d(3,[f([0,1,2],["0,0,0","0,0,1","1,1,0","1,1,1"])]),
};
const list=xs=>"["+xs.join(",")+"]";
const row=t=>list(t.split(",").map(b=>b==="1"?"true":"false"));
const factor=f=>`⟨${list(f.h)}, ${list([...f.S].map(row))}⟩`;
const tables=fs=>list(fs.map(factor));
const steps=log=>list(log.map(e=>`⟨${e.a},${e.b},${list(e.removed.map(row))}⟩`));
const model=(d,z)=>d.F.every(f=>f.S.has(f.h.map(i=>z[i]).join()));
function load(name){
 const input=fixtures[name];ok(input,"fixture");
 const c=R.close(input,true),v=V.verify(input,c.d,c.log);
 const extra=R.derivedPairs(U,c.d);
 return {input,c,v,extra};
}
function lean(name){
 const {input,c,extra}=load(name),k=input.k,N="MathOS.F038.RelationalReplay.Generated_"+name;
 let s=`import F038Formal.RelationalReplay
namespace ${N}
open MathOS.F038 MathOS.F038.Cert MathOS.F038.Reduction
open MathOS.F038.RelationalReplay
def input : List (RowFactor ${k}) := ${tables(input.F)}
def output : List (RowFactor ${k}) := ${tables(c.d.F)}
def steps : List Deletion := ${steps(c.log)}
example : closureCheck input output steps = true := by decide
theorem exported_exact (x : Assignment ${k}) :
    TableModels output x ↔ TableModels input x :=
  closureCheck_exact input output steps (by decide) x
#print axioms exported_exact
`;
 if(c.contradiction){
  const i=c.d.F.findIndex(f=>!f.S.size);
  s+=`theorem exported_unsat : ¬ ∃ x, TableModels input x := by
  rintro ⟨x,hx⟩
  exact emptyFactor_unsat output (${factor(c.d.F[i])}) (by simp [output]) rfl
    ⟨x,(exported_exact x).mpr hx⟩
#print axioms exported_unsat
`;
 }
 if(extra.length){
  const g=extra[0],i=c.d.F.findIndex(f=>g.h.every(v=>f.h.includes(v))&&[...f.S].every(t=>g.S.has(g.h.map(v=>t.split(",")[f.h.indexOf(v)]).join())));
  ok(i>=0,"derived source");
  s+=`def addition : Addition ${k} := ⟨${i},${factor(g)},${list(c.d.F[i].h)}⟩
def augmented : List (RowFactor ${k}) := addition.factor :: output
example : addStep 3 output addition = some augmented := by rfl
theorem exported_added (x : Assignment ${k}) :
    TableModels augmented x ↔ TableModels input x :=
  (addStep_exact 3 output augmented addition (by rfl) x).trans (exported_exact x)
#print axioms exported_added
`;
 }
 return s+`end ${N}\n`;
}
// Generate actual D7A closure followed by D7B affine reduction. The FV10
// exporter binds its affine proofs to the closed source; append the
// original-table equivalence theorem using the separately checked log.
function composed(){
 const {input,c}=load("chain"),r=A.reduce(U,c.d),local=L.replay(c.d,r);
 ok(r.kind==="narrow"&&local&&r.a.free.length===0,"composition fixture");
 const N="MathOS.F038.AffineReplay.Generated_relational";
 let s=E.lean(c.d,r,local,"relational").replace("import F038Formal.AffineReplay","import F038Formal.AffineReplay\nimport F038Formal.RelationalReplay");
 s=s.replace("end "+N,`open MathOS.F038.RelationalReplay
def original : List (RowFactor ${input.k}) := ${tables(input.F)}
def deletions : List Deletion := ${steps(c.log)}
example : closureCheck original source deletions = true := by decide
theorem composed_exact :
    (∃ z, TableModels out z) ↔ (∃ x, TableModels original x) := by
  rw [exported_exact]
  constructor
  · rintro ⟨x,hx⟩
    exact ⟨x,(closureCheck_exact original source deletions (by decide) x).mp hx⟩
  · rintro ⟨x,hx⟩
    exact ⟨x,(closureCheck_exact original source deletions (by decide) x).mpr hx⟩
#print axioms composed_exact
end ${N}`);
 return s;
}
function audit(){
 let seed=271828,instances=0,models=0,comparisons=0,deletions=0,events=0,contradictions=0,derived=0;
 const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;};
 function check(input){
  const c=R.close(input,true),v=V.verify(input,c.d,c.log),extra=R.derivedPairs(U,c.d);
  comparisons+=v.comparisons;deletions+=v.deleted;events+=c.log.length;contradictions+=+v.contradiction;derived+=extra.length;
  for(const x of U.tuples(2,input.k)){
   const m=model(input,x);models+=+m;
   ok(m===model(c.d,x),"closure semantics");
   ok(m===model({...c.d,F:[...c.d.F,...extra]},x),"derived semantics");
  }
  instances++;
  return c;
 }
 for(let t=0;t<128;t++){
  const k=1+t%5,fs=[];
  for(let j=0;j<1+t%7;j++){
   const width=1+rnd(Math.min(k,3)),h=[];
   while(h.length<width){const v=rnd(k);if(!h.includes(v))h.push(v);}
   h.sort((a,b)=>a-b);
   fs.push(f(h,[...U.tuples(2,width)].filter(()=>rnd(5)>0).map(x=>x.join())));
  }
  check(d(k,fs));
 }
 const random={instances,models,comparisons,deletions,events,contradictions,derived};
 const rows=Object.keys(fixtures).map(name=>{
  const {input,c,extra}=load(name);check(input);
  ok(lean(name).includes("closureCheck"),"export");
  return {name,events:c.log.length,deleted:c.stats.deleted,contradiction:c.contradiction,derived:extra.length};
 });
 const {input,c}=load("chain"),first=c.log[0],bad=[
  [c.d,[{...first,a:first.b},...c.log.slice(1)]],
  [c.d,[{...first,removed:[]},...c.log.slice(1)]],
  [c.d,[{...first,removed:["1,1","0,0"]},...c.log.slice(1)]],
  [c.d,c.log.slice(1)],
  [c.d,[...c.log,first]],
  [input,c.log]
 ];
 let rejected=0;
 for(const [out,log] of bad){try{V.verify(input,out,log);}catch{rejected++;}}
 ok(rejected===bad.length,"corrupt log accepted");
 ok(composed().includes("theorem composed_exact"),"composed export");
 return {random,rows,rejected,generated:6};
}
module.exports={audit,lean,composed};
if(require.main===module){
 if(process.argv[2]==="lean")console.log(process.argv[3]==="composed"?composed():lean(process.argv[3]));
 else console.log(JSON.stringify(audit()));
}
