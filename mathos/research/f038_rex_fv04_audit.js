// FV-04: use actual D7I producer output; test the portable packet and emit Lean.
const C=require('./f038_rex_variable_resolution_closure.js'),D=require('./f038_rex_variable_adaptive_inference.js'),H=require('./f038_rex_variable_hall_inference.js'),B=require('./f038_rex_variable_conflict_cliques.js'),G=require('./f038_rex_variable_disjunction_alternatives.js'),N=require('./f038_rex_variable_polarity_normalization.js'),I=require('./f038_rex_variable_implied_conflicts.js');
const {exportPacket,leanFixture}=require('./f038_rex_fv04_export.js'),{replay}=require('./f038_rex_fv04_replay.js');
const U={*tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**j)%m);}};
function split(d){let k=d.k;const F=[];for(const f of d.F){if(f.h.length!==2){F.push(f);continue;}const [x,y]=f.h,u=k++;F.push({h:[x,u],S:new Set(["0,0","0,1","1,1"])},{h:[u,y],S:new Set(["0,0","0,1","1,0"])});}return {k,m:2,F};}
function fixture(holes,mode){
 let d=split(D.php(U,holes));
 if(mode==="mixed")d=N.transform(d,Array.from({length:d.k},(_,i)=>+(i%3===0))).d;
 if(mode==="negative")d=N.transform(d,Array(d.k).fill(1)).d;
 const cert=I.infer(N,G,B,H,C,d);
 if(cert.kind!=="implied-hall")throw Error("expected D7I certificate: "+holes+" "+mode);
 const data=exportPacket(d,cert);
 if(!replay(data))throw Error("portable replay");
 return {data,kind:cert.hall.kind};
}
function audit(){
 const rows=[];
 for(const [holes,mode] of [[3,"plain"],[3,"mixed"],[3,"negative"],[4,"mixed"],[6,"plain"],[8,"plain"]]){
  const {data,kind}=fixture(holes,mode),p=data.packet;
  rows.push({holes,mode,kind,k:data.n,factors:data.factors.length,paths:p.paths.length,groups:p.groups.length,conflicts:p.conflicts.length});
 }
 const {data}=fixture(3,"plain");
 const mutate=f=>{const t=JSON.parse(JSON.stringify(data));f(t);let rejected=false;try{replay(t);}catch{rejected=true;}if(!rejected)throw Error("corruption accepted");};
 mutate(t=>t.packet.paths[0].steps[0].proof.index=9999);
 mutate(t=>t.packet.paths[0].steps.pop());
 mutate(t=>t.packet.paths[0].left=0);
 mutate(t=>t.packet.paths[0].steps[0].next=t.n+1);
 mutate(t=>t.packet.placements[0][1]=t.packet.holeCount);
 mutate(t=>t.packet.conflicts=[]);
 mutate(t=>t.packet.groups[0].proof={kind:"source",index:0,row:[]});
 mutate(t=>t.factors[0].scope[0]=t.n);
 mutate(t=>t.factors[0].rows[0].push(true));
 return {rows,tamperRejected:9};
}
module.exports={audit,fixture};
if(require.main===module){
 if(process.argv[2]==="lean"){const mode=process.argv[3]||"plain";process.stdout.write(leanFixture(fixture(3,mode).data,"Generated_"+mode));}
 else console.log(JSON.stringify(audit()));
}
