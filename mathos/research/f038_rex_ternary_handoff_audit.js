// F038-REX-022B5: complete same-tape differential audit.
function audit(H,P,A,E,R,suite="small"){
 const M=H.compile(P,A),J=A.worker(),W=A.compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 function test(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),ref=R.producer(raw),r=H.run(P,M,raw,3000000000,true);
  ok(r.status==="WORKER_"+want,"status "+name+" "+r.status);
  const N=ref.prepared.length,origin=r.entry.head+(M.shiftCount+1)*N+3;
  ok(r.entry.prepared===ref.prepared&&r.entry.workerInput===ref.prepared&&r.entry.isolated&&r.workerOrigin===origin,"isolated entry");
  ok(r.protectedUnchanged&&r.workerMin>r.entry.head,"protected data");
  const K=M.shiftCount;ok(r.handoffTransitions===2*(K+1)*N*N+(2*K+9)*N+6,"exact isolation clock");
  ok(r.workerMin>=origin-(W.width+2)*(N+2),"worker span bound");
  const iso=A.physical(W,ref.prepared,120000000);
  ok(iso.state===W.q&&iso.t===r.workerTransitions&&iso.head===r.head-origin,"worker clock/head");
  const sorted=[...iso.tape].sort((a,b)=>a[0]-b[0]);ok(JSON.stringify(sorted)===JSON.stringify(r.workerTape),"worker tape differential");
  const D=E.decode(raw),allowed=[];
  for(let j=0;j<7;j++){const F=D.F.filter(f=>f.h.every(g=>g>=j&&g<=j+2));allowed.push([...E.tup(m,3)].filter(z=>F.every(f=>f.S.has(f.h.map(g=>z[g-j]).join(",")))));}
  const models=[...E.tup(m,9)].filter(z=>D.F.every(f=>f.S.has(f.h.map(g=>z[g]).join(","))));
  ok(!!models.length===(want==="SAT"),"independent exhaustive models");
  let witness=null,z=null;
  if(want==="SAT"){
   z=Array(9).fill(-1);let at=0;for(let j=0;j<7;j++){
    let bits=r.certificate.slice(at,at+allowed[j].length);at+=allowed[j].length;ok(bits.length===allowed[j].length&&bits.split("1").length===2,"onehot row");
    let row=allowed[j][bits.indexOf("1")];for(let k=0;k<3;k++){ok(z[j+k]===-1||z[j+k]===row[k],"separator");z[j+k]=row[k];}
   }ok(at===r.certificate.length,"certificate size");witness=E.witness(m,pins,z);ok(E.valid(raw,witness),"original witness");
  }
  rows.push({name,m,L:raw.length,N,allowedRows:allowed.map(x=>x.length),models:models.length,status:r.status,t:r.t,producer:r.producerTransitions,handoff:r.handoffTransitions,worker:r.workerTransitions,workerOrigin:origin,workerMin:r.workerMin,margin:r.workerMin-r.entry.head,certificate:r.certificate,witnessVerified:!!witness,ranks:z});
  return{raw,r};
 }
 const force=(m,z)=>Array.from({length:9},(_,g)=>Array.from({length:m},(_,i)=>i===z[g]?null:[-(g*m+i+1)]).filter(Boolean)).flat();
 if(suite==="small"){
  test("forced",2,[1,0],force(2,Array(9).fill(1)),"SAT");
  let B=force(2,[0,1,0,1,0,1,0,1,0]).filter(c=>c[0]!==-2&&c[0]!==-17);
  test("multirow",2,[0,1],B,"SAT");
  test("empty-bag",2,[1,1],[[-1],[-2]],"UNSAT");
  let C=[[-2],[-17]];for(let g=0;g<8;g++){C.push([-(2*g+1),-(2*(g+1)+2)],[-(2*g+2),-(2*(g+1)+1)]);}
  test("nonempty-inconsistent",2,[0,0],C,"UNSAT");
 }else if(suite==="three")test("rank-two",3,[1,0,1],force(3,Array(9).fill(2)),"SAT");
 else if(suite==="controls"){
  let raw=E.encode(2,[1,0],force(2,Array(9).fill(1))),r=H.run(P,M,raw,100000000,true),controls=[];
  for(let limit of [0,1,r.bridgeAt-1,r.bridgeAt,r.bridgeAt+1,r.workerAt-1,r.workerAt,r.workerAt+1,r.t-1]){
   let x=H.run(P,M,raw,limit);ok(x.status==="TIMEOUT"&&x.t===limit,"cutoff "+limit);controls.push(limit);
  }
  ok(H.run(P,M,raw,r.t).status==="WORKER_SAT","exact clock");
  let bad=raw.slice(0,-1),outside=E.encode(2,[1,0],[[-1,-17]]),rejects=[];
  for(let [input,want] of [["","OUTSIDE_NORMALIZED"],[bad,"OUTSIDE_NORMALIZED"],[outside,"OUTSIDE_FIXED_PATH"]]){
   let v=H.run(P,M,input,100000000);ok(v.status===want&&v.bridgeAt===null&&v.workerAt===null,"producer rejection");rejects.push({status:v.status,t:v.t});
  }
  return{suite,q:M.q,descriptorBits:M.desc.length,controls,rejects,exactBudget:r.t};
 }else throw Error("suite");
 return{suite,q:M.q,descriptorBits:M.desc.length,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,preparedBits:a.preparedBits+r.N,producer:a.producer+r.producer,handoff:a.handoff+r.handoff,worker:a.worker+r.worker,transitions:a.transitions+r.t,witnesses:a.witnesses+Number(r.witnessVerified)}),{rawBits:0,preparedBits:0,producer:0,handoff:0,worker:0,transitions:0,witnesses:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_TERNARY_HANDOFF_OK '+JSON.stringify(audit(require('./f038_rex_ternary_handoff.js'),require('./f038_rex_ternary_bags.js'),require('./f038_rex_nested_variable_overlap.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_multitape_producer.js'),process.argv[2]||'small')));
