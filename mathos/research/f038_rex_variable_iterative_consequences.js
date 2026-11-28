// D7K: monotone stratified consequence closure; proof references only earlier strata.
function close(P,C,I,d,budget=2000000,maxRounds=2*d.k*d.k+1,afterRound=null){
 if(!Number.isSafeInteger(budget)||budget<0||!Number.isSafeInteger(maxRounds)||maxRounds<0)throw Error("limits");
 let view=d,work=0;const rounds=[],metrics=[];
 for(let r=0;r<maxRounds;r++){
  const p=P.discover(C,I,view,budget-work);work+=p.metrics.work;metrics.push(p.metrics);
  if(p.kind==="conflict")return {kind:"conflict",rounds,trace:p.trace,work,metrics};
  if(p.records.length){rounds.push(p.records);view=p.d;
   if(afterRound){const proof=afterRound(view);if(proof.kind!=="unknown")return {kind:"structural",rounds,proof,work,metrics};}
  }
  if(p.status==="budget")return {kind:"view",status:"budget",d:view,rounds,work,metrics};
  if(!p.records.length)return {kind:"view",status:"fixed-point",d:view,rounds,work,metrics};
 }
 return {kind:"view",status:"round-limit",d:view,rounds,work,metrics};
}

function infer(N,G,B,H,C,I,P,d,budget=2000000,maxRounds=2*d.k*d.k+1,beam=8){
 const base=I.infer(N,G,B,H,C,d,beam);
 if(base.kind!=="unknown")return {kind:"inherited",proof:base,work:0,metrics:[],rounds:[]};
 const r=close(P,C,I,d,budget,maxRounds,e=>I.infer(N,G,B,H,C,e,beam));
 if(r.kind==="view")return {kind:"unknown",status:r.status,work:r.work,metrics:r.metrics,rounds:r.rounds.length};
 return r;
}

function reduce(N,G,B,H,C,V,D,T,HV,NV,I,IV,P,PV,JV,d,budget=2000000,maxRounds=2*d.k*d.k+1,beam=8){
 const r=infer(N,G,B,H,C,I,P,d,budget,maxRounds,beam);
 if(r.kind==="unknown")return {...D.reduce({...C,cardinality:x=>N.sparseCardinality(C,x)},V,T,d,budget),iterative:r};
 if(JV.verify(PV,IV,NV,HV,d,r)!==true)throw Error("unverified iterative proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:r,iterative:r,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={close,infer,reduce};
