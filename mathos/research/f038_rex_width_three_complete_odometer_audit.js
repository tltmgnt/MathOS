// D5Z: exact host reference vs complete rank odometer. Conditional
// whole-machine resource envelope for genuine fixed-nine selectors.
function envelope(V,m,full=false){
 const e=V.envelope(m),k=BigInt(m),S=e.S,N=S+35n*k+1479n,T=65536n*S*(k**9n+(full?k:1n)),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>1048576n*k**9n*e.L*e.L||k**9n>e.L**3n)throw Error("envelope");
 return {N,T,W,total};
}
function fixtures(E,Barrier){
 const out=[{name:"empty",m:2,B:[]},{name:"radius-three-last",m:2,B:[[-7,-13],[-9,-15],[-11,-17]]},{name:"known-radius-three",m:2,B:[[-1,-3],[-5,-7],[-9,-11]]},{name:"chain",m:2,B:[[-1],[-3],[-2,-4,-5],[-4,-6,-7],[-6,-8,-9]]},{name:"empty-domain",m:2,B:[[-1],[-2]]},{name:"ternary-empty",m:2,B:[[-1],[-3],[-2,-4,-5],[-2,-4,-6]]}];
 for(const unsat of [false,true])out.push({name:unsat?"barrier-unsat":"barrier-sat",m:2,B:Barrier.family(E,2,unsat).B});
 // A GAC-stable SAT instance requiring the third rank in each of
 // three last groups. Earlier groups are free, so lex search is short.
 const m=3,B=[];for(const g of [7,8])for(const [a,b] of E.tup(m,2))if(a!==b)B.push([-(6*m+a+1),-(g*m+b+1)]);
 for(let a=0;a<2;a++)B.push([-(6*m+a+1),-(7*m+a+1),-(8*m+a+1)]);
 out.push({name:"third-rank-barrier",m,B});
 return out;
}
function audit(U,E,Barrier,Old,F,V){
 const J=[U.machine(false),U.machine(true)],O=[Old.machine(false),Old.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 let cases=0,sat=0,unsat=0,gain=0,arith=0,clockChecks=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){envelope(V,m,full);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){envelope(V,(1n<<k)+d,full);arith++;}
 function test(name,m,B,detail=false){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),b=Barrier.exact(E,raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s];
  for(let i=0;i<2;i++){
   const a=U.executeIR(J[i],I),old=Old.executeIR(O[i],I),e=envelope(V,m,!!i);
   ok((a.status==="halt")===(b.status==="SAT")&&BigInt(a.steps)<=e.T&&a.tapes[19]===s,"status "+name);
   if(a.status==="halt"){ok(a.tapes[0]===b.bits&&E.valid(raw,a.tapes[0]),"lex witness "+name);const v=F.count(J[i],I);ok(BigInt(v.N)<=e.N&&BigInt(v.clock)<=e.W&&v.steps===a.steps,"clock");clockChecks++;sat++;if(old.status==="reject")gain++;if(detail&&i===0)rows.push({name,m,count:b.count,rank:b.z,steps:a.steps,clock:v.clock,N:v.N,prior:old.status});}
   else{ok(a.tapes[0]===""&&old.status==="reject","refusal "+name);unsat++;if(detail&&i===0)rows.push({name,m,count:b.count,steps:a.steps,prior:old.status});}
  }cases++;
 }
 for(const f of fixtures(E,Barrier))test(f.name,f.m,f.B,true);
 for(let v=0;v<256;v++){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,B);}
 let seed=0xD5A9;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=i%3===0?3:2,B=[];for(let j=0;j<18;j++){const k=1+rand(3),gs=[];while(gs.length<k){let g=rand(9);if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 return {cases,sat,unsat,gain,arith,clockChecks,rows};
}
module.exports={envelope,fixtures,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'complete_odometer_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'cost_ir.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'))));}
