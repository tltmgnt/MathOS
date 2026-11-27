// D5K independent bounded sequential GAC and candidate oracle.
function oracle(E,raw){
 const d=E.decode(raw),groups=Array.from({length:9},(_,i)=>i),domains=groups.map(g=>Array.from({length:d.m},(_,i)=>i).filter(i=>d.F.every(f=>f.h.length!==1||f.h[0]!==g||f.S.has(String(i)))));
 let rounds=0,deletions=0,stable=false;
 for(let k=0;k<4;k++){
  if(domains.some(a=>!a.length))return {domains,rounds,deletions,empty:true,z:null,stable:false};
  let removed=0;rounds++;
  for(let arity=2;arity<=3;arity++)for(const h of E.subsets(groups,arity)){
   const f=d.F.find(f=>f.h.join()===h.join());if(!f)continue;
   const support=h.map(()=>new Set());
   for(const z of E.tup(d.m,arity))if(z.every((x,j)=>domains[h[j]].includes(x))&&f.S.has(z.join()))z.forEach((x,j)=>support[j].add(x));
   for(let j=0;j<h.length;j++){let g=h[j],next=domains[g].filter(x=>support[j].has(x));removed+=domains[g].length-next.length;domains[g]=next;}
   if(domains.some(a=>!a.length))return {domains,rounds,deletions:deletions+removed,empty:true,z:null,stable:false};
  }
  deletions+=removed;if(!removed){stable=true;break;}
 }
 for(let mask=0;mask<512;mask++){if(mask.toString(2).replaceAll("0","").length>2)continue;const z=domains.map((a,g)=>a[(mask>>g)&1]);if(z.every(x=>x!==undefined)&&d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join())))return {domains,rounds,deletions,empty:false,z,mask,stable};}
 return {domains,rounds,deletions,empty:false,z:null,stable};
}

function envelope(V,m){
 const e=V.envelope(m),S=e.S,m0=BigInt(m),N=S+35n*m0+1479n,T=16384n*S,W=(20n*N+12n)*T+6n,total=e.P+128n*S*S+W+256n*S*S,pass=64n*(36n*m0*m0+84n*m0**3n)+120n*(512n*(m0+1n)+64n)+16n*S;
 if(N>2n*S||pass>256n*S||W>1048576n*S*S||total>65536n*e.L*e.L)throw Error("bound");return {N,T,W,total,H0:139950752n};
}

function audit(U,E,F,V,Old){
 const J=U.machine(),old=Old.machine(),rows=[];let count=0,accepted=0,refused=0,gains=0,losses=0,falseNeg=0,empty=0,maxSteps=0,maxRounds=0,arith=0,cap=0;
 const ok=(x,s)=>{if(!x)throw Error(s)};
 for(let m=2;m<=10000;m++){envelope(V,m);arith++;}for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n]){envelope(V,(1n<<k)+d);arith++;}
 const test=(name,m,c,detail=false)=>{
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,c),d=E.decode(raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s],r=U.executeIR(J,I),ref=oracle(E,raw),before=Old.executeIR(old,[...Array(18).fill(""),s]),v=envelope(V,m);
  ok((r.status==="halt")===(ref.z!==null),"status "+name);count++;maxRounds=Math.max(maxRounds,ref.rounds);maxSteps=Math.max(maxSteps,r.steps);ok(BigInt(r.steps)<=v.T,"primitive");
  if(ref.empty){empty++;let sat=false;for(const z of E.tup(m,9)){if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join()))){sat=true;break;}}ok(!sat,"sound empty");}
  else {if(!ref.stable)cap++;const actual=r.tapes.slice(1,10).map(s=>[...s].flatMap((x,i)=>x==="1"||x==="x"?[i]:[]));ok(JSON.stringify(actual)===JSON.stringify(ref.domains),"domains "+name);}
  if(ref.z){accepted++;if(before.status!=="halt")gains++;ok(r.tapes[0]===E.witness(m,pins,ref.z)&&E.valid(raw,r.tapes[0]),"witness "+name);const a=F.count(J,I);ok(BigInt(a.N)<=v.N&&BigInt(a.clock)<=v.W&&a.steps===r.steps,"physical accounting");if(detail)rows.push({name,m,steps:a.steps,N:a.N,worker:a.clock,mask:ref.mask,deletions:ref.deletions,rounds:ref.rounds,stable:ref.stable,old:before.status});}
  else{refused++;if(before.status==="halt")losses++;if(!ref.empty&&m<=3){for(const z of E.tup(m,9)){if(d.F.every(f=>f.S.has(f.h.map(g=>z[g]).join()))){falseNeg++;break;}}}}
 };
 test("empty",2,[],true);
 test("ternary-forced",2,[[-1],[-3],[-2,-4,-5]],true);
 test("ternary-three-rank",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],true);
 test("ternary-empty",2,[[-1],[-3],[-2,-4,-5],[-2,-4,-6]],true);
 test("two-disjoint",2,[[-1,-3],[-5,-7]],true);
 test("radius-three-refusal",2,[[-1,-3],[-5,-7],[-9,-11]],true);
 test("reverse-chain-cap",2,[[-18],...Array.from({length:8},(_,i)=>[-(2*i+2),-(2*(i+1)+1)])],true);
 test("ternary-chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],true);
 let seed=0xD5A110;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){
  const m=i%3===0?3:2,clauses=[],keys=new Set();for(let j=0;j<18;j++){let k=1+rand(3),g=[];while(g.length<k){let x=rand(9);if(!g.includes(x))g.push(x);}const c=g.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)),key=c.join();if(!keys.has(key)){clauses.push(c);keys.add(key);}}
  test("random-"+i,m,clauses);
 }
 return {count,accepted,refused,gains,losses,falseNeg,empty,maxSteps,maxRounds,arith,cap,rows};
}
module.exports={oracle,envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_ternary_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Old=require('./f038_rex_width_three_propagation_ir.js');console.log(JSON.stringify(audit(U,E,F,V,Old)));}
