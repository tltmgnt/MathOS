// D5L dense-equivalence, active index, bounded/full independent support oracle and conditional envelope.
function oracle(E,raw,full=false){
 const d=E.decode(raw),groups=Array.from({length:9},(_,i)=>i),domains=groups.map(g=>Array.from({length:d.m},(_,i)=>i).filter(i=>d.F.every(f=>f.h.length!==1||f.h[0]!==g||f.S.has(String(i)))));
 let rounds=0,deletions=0,stable=false;
 for(let k=0;k<(full?9*d.m+1:4);k++){
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


function envelope(V,m,full=false){
 const e=V.envelope(m),S=e.S,k=BigInt(m),N=S+35n*k+1602n,T=32768n*S*(full?k:1n),W=(20n*N+12n)*T+6n,total=e.P+128n*S*S+W+256n*S*S,ell=full?142287052n:142418000n;
 if(N>2n*S||W>2097152n*S*S*(full?k:1n)||total>65536n*e.L*e.L*(full?k:1n))throw Error("envelope");
 return {N,T,W,total,H0:full?(3n*(ell+12n)+1n)/2n:ell+16n};
}

function audit(U,E,F,V,Old){
 const J=[U.machine(false),U.machine(true)],O=Old.machine(),rows=[];let count=0,arith=0,activeChecks=0,boundedAccepted=0,fullAccepted=0,fullGain=0,fullLoss=0,cap=0,empty=0,clockChecks=0,strictSavings=0;
 const ok=(x,s)=>{if(!x)throw Error(s)};
 for(let m=2;m<=10000;m++){envelope(V,m);envelope(V,m,true);arith+=2;}for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n]){envelope(V,(1n<<k)+d);envelope(V,(1n<<k)+d,true);arith+=2;}
 function test(name,m,c,detail=false){
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,c),d=E.decode(raw),s=U.stream(E,raw),I=[...Array(20).fill(""),s],oldI=[...Array(19).fill(""),s],old=Old.executeIR(O,oldI),groups=[0,1,2,3,4,5,6,7,8],flags=[2,3].flatMap(k=>[...E.subsets(groups,k)].map(h=>{const f=d.F.find(x=>x.h.join()===h.join());return f&&f.S.size<m**k?"1":"0";})).join("");
  const results=J.map((j,i)=>{const full=!!i,r=U.executeIR(j,I),ref=oracle(E,raw,full),b=envelope(V,m,full);ok((r.status==="halt")===(ref.z!==null),"oracle "+name);ok(BigInt(r.steps)<=b.T,"primitive "+name);
   if(r.tapes[19].length){ok(r.tapes[19]===flags,"index "+name);activeChecks++;}
   if(!ref.empty){const domains=r.tapes.slice(1,10).map(s=>[...s].flatMap((x,k)=>x==="1"||x==="x"?[k]:[]));ok(JSON.stringify(domains)===JSON.stringify(ref.domains),"domains "+name);}
   if(ref.z){ok(E.valid(raw,r.tapes[0])&&r.tapes[0]===E.witness(m,pins,ref.z),"witness "+name);const a=F.count(j,I);ok(BigInt(a.clock)<=b.W&&BigInt(a.N)<=b.N&&a.steps===r.steps,"clock");clockChecks++;return {r,ref,clock:a.clock};}
   return {r,ref,clock:null};});
  const [a,b]=results;ok(a.r.status===old.status&&a.r.tapes[0]===old.tapes[0],"dense equivalence "+name);
  count++;if(a.ref.empty)empty++;if(!a.ref.stable&&!a.ref.empty)cap++;if(a.ref.z){boundedAccepted++;const oldClock=F.count(O,oldI).clock;if(a.clock<oldClock)strictSavings++;if(detail)rows.push({name,m,active:flags.split("1").length-1,dense:oldClock,bounded:a.clock,full:b.clock,boundedSteps:a.r.steps,fullSteps:b.r.steps,boundedRounds:a.ref.rounds,fullRounds:b.ref.rounds});}
  if(b.ref.z)fullAccepted++;if(!a.ref.z&&b.ref.z)fullGain++;if(a.ref.z&&!b.ref.z)fullLoss++;
 }
 test("empty",2,[],true);
 test("ternary-chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],true);
 test("ternary-three-rank",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],true);
 test("reverse-chain-cap",2,[[-18],...Array.from({length:8},(_,i)=>[-(2*i+2),-(2*(i+1)+1)])],true);
 test("radius-three-refusal",2,[[-1,-3],[-5,-7],[-9,-11]]);
 test("ternary-empty",2,[[-1],[-3],[-2,-4,-5],[-2,-4,-6]]);
 test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))),true);
 test("empty-unary",2,[[-1],[-2]]);
 let seed=0xD5A110;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=i%3===0?3:2,clauses=[],keys=new Set();for(let j=0;j<18;j++){let k=1+rand(3),g=[];while(g.length<k){let x=rand(9);if(!g.includes(x))g.push(x);}const c=g.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)),key=c.join();if(!keys.has(key)){clauses.push(c);keys.add(key);}}test("random-"+i,m,clauses);}
 return {count,arith,activeChecks,boundedAccepted,fullAccepted,fullGain,fullLoss,cap,empty,clockChecks,strictSavings,thresholds:[envelope(V,2).H0,envelope(V,2,true).H0].map(String),rows};
}
module.exports={oracle,envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_sparse_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Old=require('./f038_rex_width_three_ternary_ir.js');console.log(JSON.stringify(audit(U,E,F,V,Old)));}
