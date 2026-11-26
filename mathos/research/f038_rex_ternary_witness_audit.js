// F038-REX-022B6: same-machine Boolean witness differential audit.
function audit(V,P,H,A,E,R,suite="small"){
 const M=V.compile(P,H,A),J=A.worker(),W=A.compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 ok(W.q===126995&&W.desc.length===8127684,"original one-bit worker unchanged");
 const force=(m,z)=>Array.from({length:9},(_,g)=>Array.from({length:m},(_,i)=>i===z[g]?null:[-(g*m+i+1)]).filter(Boolean)).flat();
 function check(name,m,pins,B,want){
  const raw=E.encode(m,pins,B),D=E.decode(raw),ref=R.producer(raw),iso=A.physical(W,ref.prepared,120000000),r=V.run(P,M,raw,3000000000,true);
  ok(r.status===want,"status "+name+" "+JSON.stringify(r));ok(iso.state===W.q&&iso.tape.has(iso.head)===(want==="SAT"),"reference worker");
  let models=0;for(let z of E.tup(m,9))if(D.F.every(f=>f.S.has(f.h.map(g=>z[g]).join(","))))models++;
  ok(!!models===(want==="SAT"),"model oracle");
  let expected=null,z=null,certificate=null,tokens=null;
  if(want==="SAT"){
   certificate="";for(let i=iso.head;iso.tape.has(i);i++)certificate+=iso.tape.get(i);
   z=Array(9).fill(-1);let at=0;
   for(let j=0;j<7;j++){
    const F=D.F.filter(f=>f.h.every(g=>g>=j&&g<=j+2)),allowed=[...E.tup(m,3)].filter(a=>F.every(f=>f.S.has(f.h.map(g=>a[g-j]).join(","))));
    let bits=certificate.slice(at,at+allowed.length);at+=allowed.length;ok(bits.split("1").length===2,"row selection");
    let a=allowed[bits.indexOf("1")];for(let k=0;k<3;k++){ok(z[j+k]===-1||z[j+k]===a[k],"row compatibility");z[j+k]=a[k];}
   }ok(at===certificate.length,"row length");
   expected=E.witness(m,pins,z);tokens=z.map(a=>a.toString(2).padStart(Math.ceil(Math.log2(m)),"0").split("").map(b=>"0"+b).join("")+"11").join("");
   ok(r.rankTokens===tokens&&r.protectedUnchanged,"rank tokens / storage isolation");
   ok(r.bits===expected&&r.bits.length===19*m-7&&E.valid(raw,r.bits),"original Boolean witness");
  }else ok(r.bits===null&&r.markAt===null&&r.rankAt===null&&r.translateAt===null,"no recovery on UNSAT");
  rows.push({name,m,L:raw.length,N:ref.prepared.length,models,status:r.status,t:r.t,head:r.head,producer:r.bridgeAt,handoff:r.workerAt-r.bridgeAt,eliminate:want==="SAT"?r.markAt-r.workerAt:r.t-r.workerAt,markProject:want==="SAT"?r.rankAt-r.markAt:0,relocate:want==="SAT"?r.translateAt-r.rankAt:0,reconstruct:want==="SAT"?r.t-r.translateAt:0,rankAt:r.rankAt,translateAt:r.translateAt,joinAt:r.joinAt,certificate,ranks:z,tokens,witness:r.bits,verified:want==="SAT"});
  return{raw,r};
 }
 if(suite==="small"){
  check("forced-ones",2,[1,0],force(2,Array(9).fill(1)),"SAT");
  check("forced-zeros",2,[0,0],force(2,Array(9).fill(0)),"SAT");
  let B=force(2,[0,1,0,1,0,1,0,1,0]).filter(c=>c[0]!==-2&&c[0]!==-17);check("multirow",2,[0,1],B,"SAT");
  check("empty-bag",2,[1,1],[[-1],[-2]],"UNSAT");
  let C=[[-2],[-17]];for(let g=0;g<8;g++)C.push([-(2*g+1),-(2*(g+1)+2)],[-(2*g+2),-(2*(g+1)+1)]);
  check("nonempty-inconsistent",2,[0,0],C,"UNSAT");
 }else if(suite==="three"){
  check("mixed-ranks",3,[1,0,1],force(3,[0,1,2,0,2,1,2,0,1]),"SAT");
 }else if(suite==="controls"){
  let raw=E.encode(2,[1,0],force(2,Array(9).fill(1))),r=V.run(P,M,raw,100000000,true),controls=[];
  for(let limit of [0,1,r.markAt-1,r.markAt,r.rankAt-1,r.rankAt,r.translateAt-1,r.translateAt,r.joinAt-1,r.joinAt,r.t-1]){
   let x=V.run(P,M,raw,limit);ok(x.status==="TIMEOUT"&&x.t===limit,"cutoff "+limit);controls.push(limit);
  }
  ok(V.run(P,M,raw,r.t).bits===r.bits,"exact clock");
  const outside=E.encode(2,[1,0],[[-1,-17]]),rejects=[];
  for(let [name,s] of [["empty",""],["original-n1","1000"],["original-n2","110"+"0".repeat(8)],["truncated",raw.slice(0,-1)],["outside",outside]]){
   let x=V.run(P,M,s,100000000);ok(x.status==="OUTSIDE"&&x.bits===null&&x.workerAt===null,"blank refusal "+name);rejects.push({name,t:x.t});
  }
  return{suite,q:M.q,descriptorBits:M.desc.length,controls,rejects,exactBudget:r.t};
 }else throw Error("suite");
 return{suite,q:M.q,descriptorBits:M.desc.length,rows,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,preparedBits:a.preparedBits+r.N,transitions:a.transitions+r.t,producer:a.producer+r.producer,handoff:a.handoff+r.handoff,eliminate:a.eliminate+r.eliminate,markProject:a.markProject+r.markProject,relocate:a.relocate+r.relocate,reconstruct:a.reconstruct+r.reconstruct,witnessBits:a.witnessBits+(r.witness?.length||0),verified:a.verified+Number(r.verified)}),{rawBits:0,preparedBits:0,transitions:0,producer:0,handoff:0,eliminate:0,markProject:0,relocate:0,reconstruct:0,witnessBits:0,verified:0})};
}
module.exports={audit};
if(require.main===module)console.log('F038_REX_TERNARY_WITNESS_OK '+JSON.stringify(audit(require('./f038_rex_ternary_witness.js'),require('./f038_rex_ternary_bags.js'),require('./f038_rex_ternary_handoff.js'),require('./f038_rex_nested_variable_overlap.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_multitape_producer.js'),process.argv[2]||'small')));
