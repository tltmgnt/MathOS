// D6B: independent prefix DFS oracle and functional-root certificates.
const order=(a,b)=>a.h.at(-1)-b.h.at(-1)||a.h.length-b.h.length||a.h.join().localeCompare(b.h.join());
function propagate(E,raw,full){
 const d=E.decode(raw),domains=Array.from({length:9},(_,g)=>Array.from({length:d.m},(_,i)=>i).filter(i=>d.F.every(f=>f.h.length!==1||f.h[0]!==g||f.S.has(String(i))))),factors=d.F.filter(f=>f.h.length>1).sort(order);
 for(let round=0;round<(full?9*d.m+1:4);round++){
  if(domains.some(a=>!a.length))return null;let changed=false;
  for(const f of factors){const sup=f.h.map(()=>new Set());
   for(const key of f.S){const z=key.split(",").map(Number);if(z.every((x,i)=>domains[f.h[i]].includes(x)))z.forEach((x,i)=>sup[i].add(x));}
   for(let i=0;i<f.h.length;i++){const g=f.h[i],v=domains[g].filter(x=>sup[i].has(x));if(v.length!==domains[g].length)changed=true;domains[g]=v;}
   if(domains.some(a=>!a.length))return null;
  }if(!changed)break;
 }return domains;
}
function prefixOracle(E,raw,domains){
 const d=E.decode(raw),by=Array.from({length:9},(_,g)=>d.F.filter(f=>f.h.length>1&&f.h.at(-1)===g).sort(order)),z=[],trials=[],conflicts=[];let nodes=0;
 function dfs(g){
  if(g===9){trials.push(z.slice());return true;}
  for(const a of domains[g]){
   z[g]=a;nodes++;const f=by[g].find(f=>!f.S.has(f.h.map(j=>z[j]).join()));
   if(f){trials.push(z.slice(0,g+1).concat(domains.slice(g+1).map(a=>a[0])));conflicts.push({scope:f.h.slice(),g});}
   else if(dfs(g+1))return true;
  }return false;
 }
 if(domains)dfs(0);return {trials,conflicts,nodes};
}
// A factor is a certificate of a functional extension at its last group
// if every assignment to the earlier groups allows at most one last rank.
function roots(E,raw){
 const d=E.decode(raw),cert=Array(9).fill(null);
 for(const f of d.F){
  const seen=new Set();let functional=true;
  for(const key of f.S){const prefix=key.split(",").slice(0,-1).join(",");if(seen.has(prefix)){functional=false;break;}seen.add(prefix);}
  if(functional)cert[f.h.at(-1)]=f.h.slice();
 }
 return {cert,r:cert.filter(x=>x===null).length};
}
function family(E,m,r,unsat=false){
 const B=[];
 if(r===1){for(const [a,b] of E.tup(m,2))if(a!==b)B.push([-(a+1),-(m+b+1)]);
  for(let j=2;j<9;j++)for(const [a,b,c] of E.tup(m,3))if(c!==b)B.push([-((j-2)*m+a+1),-((j-1)*m+b+1),-(j*m+c+1)]);
  for(let a=0;a<m-(unsat?0:1);a++)B.push([-(7*m+a+1),-(8*m+a+1)]);
 }else if(r===2){
  for(let j=2;j<9;j++)for(const [a,b,c] of E.tup(m,3))if(c!==(a+b)%m)B.push([-((j-2)*m+a+1),-((j-1)*m+b+1),-(j*m+c+1)]);
  for(const [a,b] of E.tup(m,2))if(unsat||a!==m-1||b!==m-1)B.push([-(a+1),-(m+b+1),-(8*m+(13*a+21*b)%m+1)]);
 }else throw Error("roots");
 return B;
}
function envelope(V,m,full=false,r=9){
 const e=V.envelope(m),k=BigInt(m),S=e.S,C=r>=9?k**9n:1n+9n*k**BigInt(r+1),N=S+35n*k+1479n,T=131072n*S*(C+(full?k:1n)),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>2097152n*(r>=9?k**9n:k**BigInt(r+1))*e.L*e.L)throw Error("envelope");
 if(r===1&&total**3n> (8192n**3n)*e.L**8n||r===2&&total>512n*e.L**3n)throw Error("root envelope");
 return {C,N,T,W,total};
}
function audit(U,P,E,Barrier,Prev,F,V,OldAudit){
 const J=[U.machine(false),U.machine(true)],O=[Prev.machine(false),Prev.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)},PC=P.compile(),PM={...P.decode(PC.desc),bridgeReady:PC.bridgeReady};
 let cases=0,sat=0,unsat=0,traceTrials=0,traceConflicts=0,improved=0,tied=0,regressed=0,arith=0,producerChecks=0,certified=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){for(const r of [1,2,9])envelope(V,m,full,r);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){for(const r of [1,2,9])envelope(V,(1n<<k)+d,full,r);arith++;}
 function test(name,m,B,detail=false,compare=true,physicalProducer=false,expectedRoots=null){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),exact=Barrier.exact(E,raw),s=U.stream(E,raw),oldS=Prev.stream(E,raw),I=[...Array(19).fill(""),s],II=[...Array(19).fill(""),oldS],certificate=roots(E,raw);
  if(expectedRoots!==null){ok(certificate.r<=expectedRoots&&exact.count===(name.endsWith("unsat")?0:1),"family "+name);certified++;}
  if(physicalProducer){const a=P.run(PM,raw,1000000000);ok(a.status==="MASK_STREAM_LOADED"&&a.stream===s,"physical producer "+name);producerChecks++;}
  for(let i=0;i<2;i++){
   const full=!!i,domains=propagate(E,raw,full),o=prefixOracle(E,raw,domains),trials=[],conflicts=[];
   const a=U.executeIR(J[i],I,(pc,T,h)=>{
    if(pc===J[i].candidateEntry)trials.push(T.slice(1,10).map(a=>a.indexOf("x")-1));
    else{const end=h[13],pair=T[12][2]==="_",len=pair?9:13,bits=T[13].slice(end-len,end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));conflicts.push({scope,g:scope.at(-1)});}
   }),e=envelope(V,m,full,expectedRoots===null?9:expectedRoots);
   ok(JSON.stringify(trials)===JSON.stringify(o.trials)&&JSON.stringify(conflicts)===JSON.stringify(o.conflicts),"prefix DFS trace "+name);
   ok((a.status==="halt")===(exact.status==="SAT")&&a.tapes[0]===(exact.bits||"")&&a.tapes[19]===s&&BigInt(a.steps)<=e.T&&BigInt(trials.length)<=e.C,"exact "+name);
   if(domains)ok(JSON.stringify(a.tapes.slice(1,10).map(w=>[...w].flatMap((x,j)=>x==="0"?[]:[j])))===JSON.stringify(domains),"domains "+name);
   traceTrials+=trials.length;traceConflicts+=conflicts.length;
   let old=null,oldTrials=0,clock=null,prior=null;if(compare){old=Prev.executeIR(O[i],II,pc=>{if(pc===O[i].candidateEntry)oldTrials++;});ok(old.status===a.status&&old.tapes[0]===a.tapes[0],"prior "+name);}
   if(a.status==="halt"){sat++;ok(E.valid(raw,a.tapes[0]),"witness");const b=F.count(J[i],I);ok(BigInt(b.N)<=e.N&&BigInt(b.clock)<=e.W&&b.steps===a.steps,"clock");clock=b.clock;
    if(old){prior=F.count(O[i],II).clock;if(clock<prior)improved++;else if(clock===prior)tied++;else regressed++;}
   }else unsat++;
   if(detail&&i===0)rows.push({name,m,roots:certificate.r,count:exact.count,trials:trials.length,oldTrials:compare?oldTrials:null,steps:a.steps,oldSteps:old?.steps??null,clock,prior});
  }cases++;
 }
 for(const f of OldAudit.fixtures(E,Barrier))test(f.name,f.m,f.B,true,true,f.m===2);
 for(let v=0;v<256;v++){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,B);}
 let seed=0xD6B0;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=i%3===0?3:2,B=[];for(let j=0;j<18;j++){const k=1+rand(3),gs=[];while(gs.length<k){let g=rand(9);if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 for(let m=2;m<=4;m++)for(const r of [1,2])for(const unsat of [false,true])test("functional-"+r+"-"+m+"-"+(unsat?"unsat":"sat"),m,family(E,m,r,unsat),true,m===2,m===2,r);
 return {cases,sat,unsat,traceTrials,traceConflicts,improved,tied,regressed,arith,producerChecks,certified,rows};
}
module.exports={propagate,prefixOracle,roots,family,envelope,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'prefix_order_ir.js'),require(p+'prefix_order_producer.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'conflict_pruning_ir.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'),require(p+'complete_odometer_audit.js'))));}
