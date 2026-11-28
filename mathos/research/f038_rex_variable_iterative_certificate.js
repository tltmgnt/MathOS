// D7K: monotone stratified consequence closure; proof references only earlier strata.
function reconstruct(PV,d,rounds){
 const ok=b=>{if(!b)throw Error("invalid consequence strata");};
 ok(d.m===2&&Array.isArray(rounds)&&rounds.length<=2*d.k*d.k);
 // Original short clauses are known; no duplicate insertion across strata.
 const known=new Set();
 for(const f of d.F)if(f.h.length<=2)for(let m=0;m<2**f.h.length;m++){
  const row=f.h.map((_,j)=>Math.floor(m/2**j)%2);
  if(!f.S.has(row.join()))known.add(f.h.map((x,j)=>row[j]?-(x+1):x+1).sort((a,b)=>Math.abs(a)-Math.abs(b)).join());
 }
 let view=d;
 for(const batch of rounds){
  ok(Array.isArray(batch)&&batch.length>0);
  for(const r of batch){ok(r&&Array.isArray(r.c)&&!known.has(r.c.join()));known.add(r.c.join());}
  // All steps in this stratum are checked against the SAME earlier view.
  view=PV.reconstruct(view,batch);
 }
 return view;
}

function verify(PV,IV,NV,HV,d,r){
 if(r.kind==="inherited")return IV.verify(NV,HV,d,r.proof);
 const view=reconstruct(PV,d,r.rounds);
 if(r.kind==="conflict"){if(r.trace.assume.length)throw Error("assumptions");return PV.checkTrace(view,r.trace);}
 if(r.kind==="structural")return IV.verify(NV,HV,view,r.proof);
 throw Error("invalid iterative certificate");
}
module.exports={reconstruct,verify};
