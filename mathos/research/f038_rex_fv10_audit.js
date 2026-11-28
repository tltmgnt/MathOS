// FV-10: exercise actual D7B logs, check their semantic claims independently,
// and export real fixtures for the Lean Proctor.
const U=require('./f038_rex_variable_rank_reduction.js');
const A=require('./f038_rex_variable_affine_closure.js');
const V=require('./f038_rex_variable_affine_certificate.js');
const L=require('./f038_rex_fv09_local.js');
const E=require('./f038_rex_fv10_export.js');
const ok=(b,s)=>{if(!b)throw Error("FV10 "+s);};
const f=(h,rows)=>({h,S:new Set(rows)});
const d=(k,F)=>({k,m:2,F});
const eq=["0,0","1,1"],ne=["0,1","1,0"],non=["0,0","0,1","1,0"],other=["0,1","1,0","1,1"];
const fixtures={
 merge:d(4,[f([0,1],eq),f([1,2],ne),f([0,3],non),f([0,3],other)]),
 chain:d(5,[f([0,1],eq),f([1,2],ne),f([2,3],eq),f([3,4],ne)]),
 zero:d(3,[f([0],["1"]),f([0,1],eq),f([1,2],ne)]),
 contradiction:d(3,[f([0,1],eq),f([1,2],eq),f([0,2],ne)]),
 empty:d(1,[f([0],[])])
};
function semantic(input,log){
 let models=0,checks=0;
 for(const x of U.tuples(2,input.k))if(input.F.every(f=>f.S.has(f.h.map(i=>x[i]).join()))){
  models++;
  for(const row of log.history){ok(row.vars.reduce((s,i)=>s^x[i],0)===row.rhs,"false equation");checks++;}
 }
 if(log.contradiction)ok(!models,"false contradiction");
 return {models,checks};
}
function load(name){
 const input=fixtures[name];ok(input,"fixture");
 const r=A.reduce(U,input);V.verify(input,r.a);
 const log=E.translate(input,r.a),local=L.replay(input,r);
 ok(log.contradiction||local,"local proof");
 return {input,r,log,local};
}
function audit(){
 const rows=[];let checks=0;
 for(const name of Object.keys(fixtures)){
  const {input,r,log,local}=load(name),s=semantic(input,log);
  checks+=s.checks;
  const src=E.lean(input,r,local,name);ok(src.includes("logCheck source claims = true"),"Lean export");
  rows.push({name,kind:r.kind,ops:r.a.ops.length,claims:log.history.length,models:s.models,free:r.a.free.length,chars:src.length});
 }
 let seed=314159,random=0,contradictions=0,claims=0;
 const rnd=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;};
 for(let t=0;t<128;t++){
  const k=1+t%5,fs=[];
  for(let j=0;j<1+t%7;j++){
   const width=1+rnd(Math.min(k,3)),h=[];
   while(h.length<width){const v=rnd(k);if(!h.includes(v))h.push(v);}
   h.sort((a,b)=>a-b);
   fs.push(f(h,[...U.tuples(2,width)].filter(()=>rnd(5)>0).map(x=>x.join())));
  }
  const input=d(k,fs),r=A.reduce(U,input),log=E.translate(input,r.a);
  const s=semantic(input,log);checks+=s.checks;claims+=log.history.length;
  if(log.contradiction)contradictions++;random++;
 }
 const {input,r}=load("merge"),bad=[
  {...r.a,ops:[[0,0],...r.a.ops]},
  {...r.a,work:r.a.work.map((e,i)=>i?e:{...e,rhs:e.rhs^1})},
  {...r.a,forms:r.a.forms.map((e,i)=>i?e:{...e,rhs:e.rhs^1})},
  {...r.a,rows:r.a.rows.map((e,i)=>i?e:{...e,local:999})}
 ];
 let rejected=0;
 for(const a of bad){try{E.translate(input,a);}catch{rejected++;}}
 ok(rejected===bad.length,"corrupt log accepted");
 return {rows,random,contradictions,claims,checks,rejected};
}
module.exports={audit,load};
if(require.main===module){
 if(process.argv[2]==="lean"){
  const name=process.argv[3],{input,r,local}=load(name);console.log(E.lean(input,r,local,name));
 }else console.log(JSON.stringify(audit()));
}
