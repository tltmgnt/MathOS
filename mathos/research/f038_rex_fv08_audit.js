// FV-08 adversarial finite oracle: independent truth-table enumeration and
// complete (exponential) resolution-tree certificates for small UNSAT cases.
const F=require('./f038_rex_fv07_composition.js');
const {replay}=require('./f038_rex_fv04_replay.js');
const ok=(b,m)=>{if(!b)throw Error("FV08: "+m);};
const clone=x=>JSON.parse(JSON.stringify(x));
const factor=(h,rows)=>({h,S:new Set(rows)});
function* assignments(n){for(let i=0;i<2**n;i++)yield Array.from({length:n},(_,j)=>(i>>j)&1);}
function truth(d,z){return d.F.every(f=>[...f.S].some(r=>r===f.h.map(i=>z[i]).join(",")));}
function tree(d,i,z){
 if(i===d.k){
  const j=d.F.findIndex(f=>!f.S.has(f.h.map(v=>z[v]).join(",")));
  if(j<0)throw Error("model in refutation");
  return {kind:"source",index:j,row:d.F[j].h.map(v=>Boolean(z[v]))};
 }
 // The false branch's source clauses contain positive pivots, the true
 // branch's negative pivots. Resolution (even if a pivot is absent)
 // leaves a clause false under the common prefix.
 return {kind:"resolution",left:tree(d,i+1,[...z,0]),right:tree(d,i+1,[...z,1]),pivot:i+1};
}
function evidence(d){
 const raw=F.raw(d);
 return {kind:"direct",data:{...raw,packet:{retained:d.F.map((_,i)=>i),paths:[],holeCount:0,
  groups:[{options:[],proof:tree(d,0,[])}],placements:[],conflicts:[]}}};
}
function audit(){
 let seed=0x080f038,instances=0,sat=0,unsat=0,models=0,positive=0,invalidWitness=0,falseUnsat=0,corrupt=0,cutoffs=0;
 const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const empty={k:1,m:2,F:[factor([0],[])]};
 const forged=evidence(empty);
 for(let t=0;t<384;t++){
  const k=1+t%5,fs=[];
  for(let j=0;j<t%9;j++){
   const h=[...new Set(Array.from({length:1+(rnd()>>>16)%3},()=> (rnd()>>>16)%k))];
   const mask=rnd()>>>16;
   fs.push(factor(h,[...assignments(h.length)].filter((_,i)=>mask>>i&1).map(r=>r.join(","))));
  }
  const d={k,m:2,F:fs},zs=[...assignments(k)],ms=zs.filter(z=>truth(d,z));
  instances++;models+=ms.length;
  for(const z of zs){
   const r=F.release(d,d,x=>x,{status:"SAT",z});
   if(truth(d,z)){ok(r.status==="SAT"&&truth(d,r.witness),"valid witness");positive++;}
   else{ok(r.status==="UNKNOWN","invalid witness");invalidWitness++;}
  }
  ok(F.release(d,d,x=>x,{status:"TIMEOUT"}).status==="UNKNOWN","timeout");cutoffs++;
  if(ms.length){
   sat++;
   const fake=clone(forged);Object.assign(fake.data,F.raw(d));
   ok(F.release(d,empty,x=>x,{status:"UNSAT"},fake).status==="UNKNOWN","forged proof on SAT");
   ok(F.release(d,empty,x=>x,{status:"UNSAT"},{kind:"residual",data:forged.data}).status==="UNKNOWN","false residual transfer");
   falseUnsat+=2;
  }else{
   unsat++;
   const ev=evidence(d);
   ok(replay(ev.data)&&F.release(d,d,x=>x,{status:"UNSAT"},ev).status==="UNSAT","valid refutation");
   for(const mut of [e=>{e.data.packet.groups[0].proof={kind:"source",index:999,row:[]};},
    e=>{e.data.packet.holeCount=1;},e=>{e.data.packet.retained=[];},e=>{e.data.n++;}]){
    const e=clone(ev);mut(e);ok(F.release(d,d,x=>x,{status:"UNSAT"},e).status==="UNKNOWN","corrupted proof");corrupt++;
   }
  }
 }
 return {instances,sat,unsat,models,positive,invalidWitness,falseUnsat,corrupt,cutoffs};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit()));
