// D5J independent simultaneous binary AC oracle, bounded candidate oracle and resource ledger.
function oracle(E,raw){
 const d=E.decode(raw),groups=Array.from({length:9},(_,i)=>i),domains=groups.map(g=>Array.from({length:d.m},(_,i)=>i).filter(i=>d.F.every(f=>f.h.length!==1||f.h[0]!==g||f.S.has(String(i))))),binary=d.F.filter(f=>f.h.length===2);
 let rounds=0,deletions=0;
 while(true){
  if(domains.some(a=>!a.length))return {domains,rounds,deletions,empty:true,z:null};
  const next=domains.map((a,g)=>a.filter(x=>binary.every(f=>!f.h.includes(g)||domains[f.h.find(h=>h!==g)].some(y=>f.S.has(f.h.map(h=>h===g?x:y).join())))));
  const removed=domains.reduce((n,a,g)=>n+a.length-next[g].length,0);rounds++;deletions+=removed;
  for(let g=0;g<9;g++)domains[g]=next[g];if(!removed)break;
 }
 for(let mask=0;mask<512;mask++){if(mask.toString(2).replaceAll("0","").length>2)continue;const z=domains.map((a,g)=>a[(mask>>g)&1]);if(z.every(x=>x!==undefined)&&d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join())))return {domains,rounds,deletions,empty:false,z,mask};}
 return {domains,rounds,deletions,empty:false,z:null};
}

function envelope(V,m){
 const e=V.envelope(m),S=e.S,N=S+34n*BigInt(m)+504n,T=8192n*S,W=(26n*N+16n)*T+8n,total=e.P+128n*S*S+W+256n*S*S;
 if(N>2n*S||W>524288n*S*S||total>65536n*e.L*e.L)throw Error("bound");return {N,T,W,total,H0:165869289n};
}

function audit(U,E,F,V,Old){
 const J=U.machine(),old=Old.machine(),rows=[];let count=0,accepted=0,refused=0,gains=0,falseNeg=0,empty=0,maxSteps=0,maxRounds=0,arith=0;
 const ok=(x,s)=>{if(!x)throw Error(s)};
 for(let m=2;m<=10000;m++){envelope(V,m);arith++;}for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n]){envelope(V,(1n<<k)+d);arith++;}
 const test=(name,m,c,detail=false)=>{
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,c),d=E.decode(raw),s=U.stream(E,raw),I=[...Array(18).fill(""),s],r=U.executeIR(J,I),ref=oracle(E,raw),before=Old.executeIR(old,[...Array(16).fill(""),s]),v=envelope(V,m);
  ok((r.status==="halt")===(ref.z!==null),"status "+name);count++;maxRounds=Math.max(maxRounds,ref.rounds);maxSteps=Math.max(maxSteps,r.steps);ok(BigInt(r.steps)<=v.T,"primitive");
  if(ref.empty){empty++;let sat=false;for(const z of E.tup(m,9)){if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join()))){sat=true;break;}}ok(!sat,"sound empty");}
  else {const actual=r.tapes.slice(1,10).map(s=>[...s].flatMap((x,i)=>x==="1"||x==="x"?[i]:[]));ok(JSON.stringify(actual)===JSON.stringify(ref.domains),"fixed point "+name);}
  if(ref.z){accepted++;if(before.status!=="halt")gains++;ok(r.tapes[0]===E.witness(m,pins,ref.z)&&E.valid(raw,r.tapes[0]),"witness "+name);const a=F.count(J,I);ok(BigInt(a.N)<=v.N&&BigInt(a.clock)<=v.W&&a.steps===r.steps,"physical accounting");if(detail)rows.push({name,m,steps:a.steps,N:a.N,worker:a.clock,mask:ref.mask,deletions:ref.deletions,rounds:ref.rounds,old:before.status});}
  else{refused++;if(!ref.empty&&m<=3){for(const z of E.tup(m,9)){if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join()))){falseNeg++;break;}}}}
 };
 test("empty",2,[],true);
 test("chain",2,[[-1],[-2,-3],[-4,-5],[-6,-7]],true);
 test("reverse-chain",2,[[-8],[-7,-6],[-5,-4],[-3,-2]],true);
 test("two-disjoint",2,[[-1,-3],[-5,-7]],true);
 test("radius-three-refusal",2,[[-1,-3],[-5,-7],[-9,-11]],true);
 test("third-rank-required",3,[[-1],[-2],[-3,-4],[-3,-5]],true);
 test("binary-empty",2,[[-1],[-2,-3],[-2,-4]],true);
 test("ternary-repair",2,[[-1,-3,-5],[-7,-9,-11]],true);
 let seed=0xD5A110;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){
  const m=i%3===0?3:2,clauses=[],keys=new Set();for(let j=0;j<18;j++){let k=1+rand(3),g=[];while(g.length<k){let x=rand(9);if(!g.includes(x))g.push(x);}const c=g.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)),key=c.join();if(!keys.has(key)){clauses.push(c);keys.add(key);}}
  test("random-"+i,m,clauses);
 }
 return {count,accepted,refused,gains,falseNeg,empty,maxSteps,maxRounds,arith,rows};
}
module.exports={oracle,envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_propagation_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Old=require('./f038_rex_width_three_repair_ir.js');console.log(JSON.stringify(audit(U,E,F,V,Old)));}
