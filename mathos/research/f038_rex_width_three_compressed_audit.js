// D5M compressed stream equivalence, actual producer, sparse-mode comparison and resource arithmetic.
function envelope(V,m,full=false){
 const e=V.envelope(m),S=e.S,k=BigInt(m),N=S+35n*k+1479n,T=32768n*S*(full?k:1n),W=(20n*N+12n)*T+6n,total=e.P+128n*S*S+W+256n*S*S,ell=full?141067404n:141198352n;
 if(N>2n*S||W>2097152n*S*S*(full?k:1n)||total>65536n*e.L*e.L*(full?k:1n))throw Error("envelope");
 return {N,T,W,total,H0:full?(3n*(ell+12n)+1n)/2n:ell+16n};
}

function audit(U,E,F,V,Old,A,P){
 const J=[U.machine(false),U.machine(true)],O=[Old.machine(false),Old.machine(true)],C=P.compile(),M={...P.decode(C.desc),bridgeReady:C.bridgeReady},rows=[];let cases=0,arith=0,clockChecks=0,accepted=0,refused=0,streamChecks=0,producerChecks=0,producerRefusals=0,savings=0,losses=0;
 const ok=(x,s)=>{if(!x)throw Error(s)};
 for(let m=2;m<=10000;m++){envelope(V,m);envelope(V,m,true);arith+=2;}for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n]){envelope(V,(1n<<k)+d);envelope(V,(1n<<k)+d,true);arith+=2;}
 function test(name,m,c,detail=false,physical=false){
  const pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,c),s=U.stream(E,raw),old=Old.stream(E,raw),I=[...Array(19).fill(""),s],OI=[...Array(20).fill(""),old],fields=[],oldFields=[];
  for(const [str,out] of [[s,fields],[old,oldFields]]){let field="";for(let i=0;i<str.length;i+=2){const tok=str.slice(i,i+2);if(tok==="10"){out.push(field);field="";}else if(tok==="00"||tok==="01")field+=tok[1];else throw Error("token");}ok(!field&&out.length===131,"shape");}
  ok(fields.every((x,i)=>x===(i>=11&&!oldFields[i].includes("1")?"":oldFields[i])),"codec");streamChecks++;
  if(physical){const p=P.run(M,raw,3000000000);ok(p.status==="MASK_STREAM_LOADED"&&p.stream===s,"physical producer "+name);producerChecks++;}
  const result=J.map((j,i)=>{const full=!!i,r=U.executeIR(j,I),prior=Old.executeIR(O[i],OI),ref=A.oracle(E,raw,full),b=envelope(V,m,full);
   ok(r.status===prior.status&&r.tapes[0]===prior.tapes[0]&&(r.status==="halt")===(ref.z!==null),"status/witness "+name);ok(BigInt(r.steps)<=b.T,"steps");
   if(!ref.empty){const domains=r.tapes.slice(1,10).map(s=>[...s].flatMap((x,k)=>x==="1"||x==="x"?[k]:[]));ok(JSON.stringify(domains)===JSON.stringify(ref.domains),"domains "+name);}
   if(ref.z){const a=F.count(j,I),p=F.count(O[i],OI);ok(E.valid(raw,r.tapes[0])&&r.tapes[0]===E.witness(m,pins,ref.z)&&BigInt(a.N)<=b.N&&BigInt(a.clock)<=b.W&&a.steps===r.steps,"clock/witness");clockChecks++;accepted++;if(a.clock<p.clock)savings++;else if(a.clock>p.clock)losses++;return {clock:a.clock,prior:p.clock,steps:a.steps,N:a.N};}
   refused++;return null;
  });
  cases++;if(detail)rows.push({name,m,stream:s.length,dense:old.length,active:fields.slice(11).filter(x=>x.length).length,bounded:result[0],full:result[1]});
 }
 test("empty",2,[],true,true);
 test("ternary-chain",2,[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]],true,true);
 test("ternary-three-rank",3,[[-1],[-2],[-4],[-5],[-3,-6,-7],[-3,-6,-8]],true,true);
 test("reverse-chain-cap",2,[[-18],...Array.from({length:8},(_,i)=>[-(2*i+2),-(2*(i+1)+1)])],true,true);
 test("radius-three-refusal",2,[[-1,-3],[-5,-7],[-9,-11]]);
 test("ternary-empty",2,[[-1],[-3],[-2,-4,-5],[-2,-4,-6]]);
 test("all-active",2,[2,3].flatMap(k=>[...E.subsets([0,1,2,3,4,5,6,7,8],k)].map(h=>h.map(g=>-(2*g+2)))),true,true);
 test("empty-unary",2,[[-1],[-2]]);
 let seed=0xD5A110;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=i%3===0?3:2,c=[],keys=new Set();for(let j=0;j<18;j++){let k=1+rand(3),g=[];while(g.length<k){let x=rand(9);if(!g.includes(x))g.push(x);}const a=g.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)),key=a.join();if(!keys.has(key)){c.push(a);keys.add(key);}}test("random-"+i,m,c);}
 const raw=E.encode(2,[0,0],[]);for(const bad of [raw.slice(0,-1),raw+"0",raw.slice(0,31)+"1"+raw.slice(32)]){ok(P.run(M,bad,3000000000).status==="REFUSAL","malformed");producerRefusals++;}
 return {cases,arith,clockChecks,accepted,refused,streamChecks,producerChecks,producerRefusals,savings,losses,thresholds:[envelope(V,2).H0,envelope(V,2,true).H0].map(String),rows};
}
module.exports={envelope,audit};
if(require.main===module){const U=require('./f038_rex_width_three_compressed_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),F=require('./f038_rex_width_three_fast_clock.js'),V=require('./f038_rex_width_three_singleton_envelope.js'),Old=require('./f038_rex_width_three_sparse_ir.js'),A=require('./f038_rex_width_three_sparse_audit.js'),P=require('./f038_rex_width_three_compressed_producer.js');console.log(JSON.stringify(audit(U,E,F,V,Old,A,P)));}
