// REX-007 host producer/merge with actual REX-006 worker modes; not a fixed physical producer.
const R=require("./f038_rex_batched_elimination.js"),{engine:E}=require("./f038_tga_normalized_integration.js");
function makeAdapter(R,mode="host"){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=x=>x.join(","),bits=(v,n)=>n?v.toString(2).padStart(n,"0"):"";
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const stats={bags:0,batches:0,candidates:0,requests:0,factorCopies:0,positiveCandidateOccurrences:0,positiveGroupOccurrences:0,crossBatchGroups:0,peakCandidates:0,peakBits:0,totalBits:0,physicalTransitions:0,logicalTransitions:0,physicalBatches:0,logicalBatches:0,unsafeRepresentative:0};
 let J=null,M=null;
 function parse(raw){
  let rows=[],k="",p="",inKey=true;
  ok(raw.length%2===0,"raw parity");
  for(let i=0;i<raw.length;i+=2){let t=raw.slice(i,i+2);
   if(t[0]==="0"){if(inKey)k+=t[1];else p+=t[1];}
   else if(t==="10"){ok(inKey&&k.length,"divider");inKey=false;}
   else {ok(t==="11"&&!inKey,"end");rows.push([k,p]);k="";p="";inKey=true;}
  }ok(inKey&&!k&&!p,"truncated");return rows;
 }
 function run(rows){
  let raw=R.encode(rows),out;
  stats.peakBits=Math.max(stats.peakBits,raw.length);stats.totalBits+=raw.length;
  if(mode==="host")return R.refEliminate(rows);
  J??=R.eliminationWorker();
  if(mode==="logical"){
   let r=R.logicalRun(J,raw,30000000);ok(r.state==="ready","logical batch halt");out=r.out;stats.logicalTransitions+=r.steps;stats.logicalBatches++;
  }else{
   M??=R.compile(J.rules,J.symbols,J.projection);
   let r=R.physicalRun(M,raw,300000000);ok(r.state===M.q&&r.tape.size===raw.length,"physical batch halt");
   out=Array.from({length:raw.length},(_,i)=>String(r.tape.get(r.head+i))).join("");ok(/^[01]+$/.test(out),"physical output");
   stats.physicalTransitions+=r.t;stats.logicalTransitions+=r.logical;stats.physicalBatches++;
  }
  ok(out===R.encode(R.refEliminate(rows)),"worker reference");return parse(out);
 }
 function bag(m,touched,v,h,cap){
  ok(Number.isInteger(m)&&m>=2&&Number.isInteger(cap)&&cap>=1&&h.length<=3&&new Set([...h,v]).size===h.length+1,"dimensions");
  const F=touched.length?touched:[{h:[],S:new Set([""])}],d=Math.ceil(Math.log2(m)),ns=Math.ceil(Math.log2(F.length)),b=h.length+1;
  let w=Math.max(b*d,ns+Math.max(...F.map(f=>f.h.length))*d),k=w+1;
  const pad=s=>s.padEnd(w,"0"),tuple=x=>x.map(a=>bits(a,d)).join(""),lookup=(i,x)=>pad(bits(i,ns)+tuple(x)),cid=x=>"1"+pad(tuple(x)),gid=x=>"1"+pad(tuple(x)),zero="0".repeat(k);
  const factorRows=[];
  for(let i=0;i<F.length;i++){
   const f=F[i];ok(f.h.length<=3&&new Set(f.h).size===f.h.length&&f.h.every(g=>g===v||h.includes(g)),"scope");
   for(let t of f.S){let x=t===""?[]:t.split(",").map(Number);ok(x.length===f.h.length&&x.every(a=>Number.isInteger(a)&&a>=0&&a<m)&&key(x)===t,"factor digit");factorRows.push(R.makeRecord(lookup(i,x),"0",zero,zero,""));}
  }
  function decodeTuple(s,n){let a=Array.from({length:n},(_,j)=>parseInt(s.slice(1+j*d,1+(j+1)*d),2));ok(a.every(x=>x<m),"output digit");return a;}
  let S=new Set(),witness=new Map(),batch=[],seenGroups=new Set();stats.bags++;
  function flush(){
   if(!batch.length)return;
   stats.batches++;stats.peakCandidates=Math.max(stats.peakCandidates,batch.length);stats.candidates+=batch.length;
   const rows=factorRows.slice();
   for(let z of batch){let [q,a]=[z.slice(0,-1),z[b-1]];
    for(let i=0;i<F.length;i++){let x=F[i].h.map(g=>g===v?a:q[h.indexOf(g)]);rows.push(R.makeRecord(lookup(i,x),"1",cid(z),gid(q),bits(i,ns)));stats.requests++;}
   }
   stats.factorCopies+=factorRows.length;
   const out=run(rows.reverse()),groups=new Set(),positive=new Set(),localWitness=new Map();
   ok(out.length===rows.length,"row count");
   for(let [g,p] of out)if(g[0]==="1"){
    let q=decodeTuple(g,h.length),qk=key(q);groups.add(qk);
    if(p[2]==="1"){positive.add(qk);stats.positiveGroupOccurrences++;if(p[1]!=="1")stats.unsafeRepresentative++;}
    if(p[1]==="1"){
     let start=3+2*k+2,cs="";for(let j=0;j<k;j++)cs+=p[start+2*j+1];
     let z=decodeTuple(cs,b),a=z[b-1];ok(key(z.slice(0,-1))===qk,"candidate group");
     stats.positiveCandidateOccurrences++;
     if(!localWitness.has(qk)||a<localWitness.get(qk))localWitness.set(qk,a);
    }
   }
   ok(positive.size===localWitness.size&&[...positive].every(q=>localWitness.has(q)),"message/witness agreement");
   for(let g of groups){if(seenGroups.has(g))stats.crossBatchGroups++;seenGroups.add(g);}
   for(let g of positive){S.add(g);let a=localWitness.get(g);if(!witness.has(g)||a<witness.get(g))witness.set(g,a);}
   batch=[];
  }
  for(let q of tup(m,h.length))for(let a=0;a<m;a++){batch.push([...q,a]);if(batch.length===cap)flush();}
  flush();return {S,witness};
 }
 return {bag,stats};
}
function audit(R,E){
 const ok=(v,s)=>{if(!v)throw Error(s)},eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),key=x=>x.join(",");
 const H=makeAdapter(R),L=makeAdapter(R,"logical"),P=makeAdapter(R,"physical");
 let direct={cases:0,candidateAssignments:0,positiveGroups:0,emptyFactorCases:0,splitCases:0},seed=0x52455807;
 const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 function check(A,m,F,v,h,cap){
  let got=A.bag(m,F,v,h,cap),expect=new Map();
  for(let q of E().tup(m,h.length))for(let a=0;a<m;a++){if(F.every(f=>f.S.has(key(f.h.map(g=>g===v?a:q[h.indexOf(g)]))))&&!expect.has(key(q)))expect.set(key(q),a);}
  ok(eq([...got.S].sort(),[...expect.keys()].sort())&&eq([...got.witness].sort(),[...expect].sort()),"direct bag oracle");
  direct.cases++;direct.candidateAssignments+=m**(h.length+1);direct.positiveGroups+=expect.size;direct.emptyFactorCases+=+(F.length===0||F.some(f=>!f.S.size));direct.splitCases+=+(cap%m!==0&&cap<m**(h.length+1));
  return got;
 }
 const f=(h,S)=>({h,S:new Set(S)});
 // Actual physical worker, two whole-candidate batches; one positive and one negative.
 check(P,2,[f([0],["0"])],0,[],1);
 // Same outgoing OR can reside on an infeasible last candidate.
 const before=P.stats.unsafeRepresentative;check(P,2,[f([0],["0"])],0,[],2);ok(P.stats.unsafeRepresentative>before,"OR representative is not a witness");
 // Two namespaces with disjoint supports cannot substitute for one another.
 check(P,2,[f([0],["0"]),f([0],["1"])],0,[],2);
 check(L,2,[],0,[],1);
 check(L,2,[f([0,1],["0,0","1,1"]),f([0],["1"])],0,[1],3);
 check(H,2,[f([],[])],0,[],1);
 check(H,2,[f([],[""])],0,[],1);
 for(let m of [2,3,4])for(let w=0;w<=3;w++)for(let j=0;j<3;j++){
  let h=Array.from({length:w},(_,i)=>i+1),F=[];
  for(let i=0;i<1+j;i++){
   let scope=[0,...h.filter((_,k)=>(i+k)%2===0).slice(0,2)];
   F.push(f(scope,[...E().tup(m,scope.length)].filter(()=>rand()>>>29).map(key)));
  }
  for(let cap of [Math.max(1,m*m-1),m**3])check(H,m,F,0,h,cap);
 }
 // Use the actual SEP-003 decoder, planner, elimination history and witness verifier.
 let normalized={cases:0,sat:0,unsat:0,ineligible:0,rawBits:0,exactKeys:0,verifiedWitnesses:0,referenceTuples:0,ineligibleSatControls:0,malformedControls:0},details=[];
 for(let m of [2,3,4])for(let j=0;j<4;j++){
  let base=E(),pins=Array.from({length:m},(_,i)=>(i+j)%2),B=[];
  let scopes=j===3?[...base.subsets([...Array(9).keys()],2)]:j===2?[[0,4],[1,4],[2,4],[3,4],[0,5],[5,6],[6,7],[7,8],[5,8]]:[[0,4],[1,4],[2,5],[3,6],[0,1,2]];
  for(let h of scopes)B.push(h.map(g=>-(g*m+m)));
  if(j===1)for(let a=0;a<m;a++)B.push([-(4*m+a+1)]);
  let raw=base.encode(m,pins,B),a=base.solveRaw(raw),b=E(false,(...args)=>H.bag(...args).S).solveRaw(raw);
  ok(eq(a,b),"normalized full record equality "+JSON.stringify([m,j,a,b]));
  if(b.status==="INELIGIBLE"){ok(base.valid(raw,base.witness(m,pins,Array(9).fill(0))),"ineligible SAT control");normalized.ineligibleSatControls++;}
  else {
   let keys=new Set();
   for(let z of base.tup(m,9)){
    normalized.referenceTuples++;
    if(B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m)))keys.add(key(b.A.map(g=>z[g])));
   }
   ok(keys.size===b.count&&b.status===(keys.size?"SAT":"UNSAT"),"independent normalized enumeration");
  }
  if(m===2&&j===0){
   let prior=H.stats.bags;
   for(let invalid of [raw.slice(0,-1),raw+"0",raw.slice(1),"100",""]){
    let c=E(false,(...args)=>H.bag(...args).S).solveRaw(invalid);ok(c.status==="OUTSIDE_NORMALIZED","malformed status");normalized.malformedControls++;
   }
   ok(H.stats.bags===prior,"no bag processing on malformed");
  }
  normalized.cases++;normalized.rawBits+=raw.length;normalized.exactKeys+=b.count??0;
  if(b.status==="SAT"){ok(base.valid(raw,b.bits),"original witness");normalized.sat++;normalized.verifiedWitnesses++;}
  else if(b.status==="UNSAT")normalized.unsat++;else normalized.ineligible++;
  details.push([m,j,b.status,b.count??null,b.Q??null]);
 }
 return {direct,normalized,details,host:H.stats,logical:L.stats,physical:P.stats};
}
module.exports={makeAdapter,audit};
if(require.main===module)console.log('F038_REX_CANDIDATE_COMPLETE_OK '+JSON.stringify(audit(R,E)));
