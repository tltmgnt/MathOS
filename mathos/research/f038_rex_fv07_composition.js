// FV-07: fail-closed composition adapter for actual D7I and physical worker.
// A terminal status is never sufficient evidence of original UNSAT.
const {replay}=require('./f038_rex_fv04_replay.js');
const MAX_EXACT_COORDS=10;
function raw(d){
 if(!d||d.m!==2||!Number.isSafeInteger(d.k)||d.k<1||!Array.isArray(d.F))throw Error("instance");
 return {n:d.k,factors:d.F.map(f=>{
  if(!Array.isArray(f.h)||new Set(f.h).size!==f.h.length||f.h.length<1||f.h.length>3||
     !f.h.every(x=>Number.isSafeInteger(x)&&x>=0&&x<d.k)||!(f.S instanceof Set))throw Error("factor");
  const rows=[...f.S].map(s=>{
   if(typeof s!=="string")throw Error("row");
   const t=s.split(",");if(t.length!==f.h.length||t.some(x=>x!=="0"&&x!=="1"))throw Error("row");
   return t.map(x=>x==="1");
  });
  return {scope:f.h.slice(),rows};
 })};
}
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function model(d,z){
 return Array.isArray(z)&&z.length===d.k&&Array.from(z).every(x=>x===0||x===1)&&
  d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join()));
}
function* assignments(n){
 for(let mask=0;mask<2**n;mask++)yield Array.from({length:n},(_,j)=>Math.floor(mask/2**(n-1-j))%2);
}
// Finite verification of exact witness-image equality. It intentionally
// enumerates both model sets and refuses dimensions above the fixed cap.
function exactImage(original,residual,expand){
 if(original.k>MAX_EXACT_COORDS||residual.k>MAX_EXACT_COORDS)return false;
 const image=new Set();
 for(const z of assignments(residual.k))if(model(residual,z)){
  const x=expand(z);if(!model(original,x))return false;image.add(x.join());
 }
 for(const x of assignments(original.k))if(model(original,x)&&!image.has(x.join()))return false;
 return true;
}
function boundPacket(d,data){
 const r=raw(d);
 if(!data||data.n!==r.n||!equal(data.factors,r.factors))return false;
 // Source tables come from the caller's instance, not the proof payload.
 return replay({...r,packet:data.packet})===true;
}
function release(original,residual,expand,observation,evidence=null){
 const unknown=reason=>({status:"UNKNOWN",witness:null,reason});
 try{
  raw(original);raw(residual);
  if(!observation||observation.status==="TIMEOUT")return unknown("physical-timeout");
  if(observation.status==="SAT"){
   if(!model(residual,observation.z))return unknown("invalid-residual-witness");
   const x=expand(observation.z);
   if(!model(original,x))return unknown("invalid-original-witness");
   return {status:"SAT",witness:x.slice(),reason:"original-model-checked"};
  }
  if(observation.status!=="UNSAT")return unknown("invalid-observation");
  if(!evidence)return unknown("missing-certificate");
  if(evidence.kind==="direct"&&boundPacket(original,evidence.data))
   return {status:"UNSAT",witness:null,reason:"original-certificate-checked"};
  if(evidence.kind==="residual"&&exactImage(original,residual,expand)&&boundPacket(residual,evidence.data))
   return {status:"UNSAT",witness:null,reason:"residual-certificate-and-exact-image-checked"};
  return unknown("unverified-transfer");
 }catch{return unknown("rejected-evidence");}
}
module.exports={raw,model,assignments,exactImage,boundPacket,release,MAX_EXACT_COORDS};
