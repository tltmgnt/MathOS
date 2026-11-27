// D6E: automatic physical partition/fallback selection, exact oracle and route trace.
function envelope(V,m,full=false,special=false){
 const e=V.envelope(m),k=BigInt(m),S=e.S,C=special?3n*k**3n:k**9n,N=S+35n*k+1480n,T=262144n*S*(C+(full?k:1n)+1n),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>4194304n*k**(special?3n:9n)*e.L*e.L||special&&total>1024n*e.L**3n)throw Error("envelope");
 return {C,N,T,W,total};
}
function fixtures(E,Barrier,Direct,Base){
 return Base.fixtures(E,Barrier).concat([
 {name:"cross-sat",m:2,B:[[-1,-3]]},
 {name:"triple-2-sat",m:2,B:Direct.family(E,2,3,false)},
 {name:"triple-2-unsat",m:2,B:Direct.family(E,2,3,true)},
 {name:"triple-3-sat",m:3,B:Direct.family(E,3,3,false)}
 ]);
}
function audit(U,E,Barrier,Prev,Prior,Direct,Component,F,V,Base){
 const J=[U.machine(false),U.machine(true)],G=[Prev.machine(false),Prev.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 let cases=0,sat=0,unsat=0,special=0,fallback=0,fallbackSat=0,fallbackUnsat=0,trials=0,conflicts=0,arith=0,improved=0,regressed=0,tied=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){for(const s of [false,true])envelope(V,m,full,s);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){for(const s of [false,true])envelope(V,(1n<<k)+d,full,s);arith++;}
 function test(name,m,B,detail=false){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),exact=Barrier.exact(E,raw),local=Component.admitted(E,raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s];cases++;
  for(let i=0;i<2;i++){
   const full=!!i,domains=Prior.propagate(E,raw,full),o=local?Component.traceOracle(E,raw,domains):Direct.oracle(E,raw,domains),ts=[],cs=[];
   const a=U.executeIR(J[i],I,(pc,T,h)=>{
    const c=["0","1","x"].indexOf(T[15][2]),z=T.slice(1,10).map(a=>a.indexOf("x")-1);
    if(pc===J[i].candidateEntry)ts.push(local?{c,z}:z);
    else{const end=h[13],pair=T[12][2]==="_",len=pair?9:13,bits=T[13].slice(end-len,end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));cs.push(local?{c,scope}:{scope,g:scope.at(-1)});}
   }),e=envelope(V,m,full,local);
   ok(a.tapes[15][0]===(local?"0":"1"),"physical route "+name);
   ok(JSON.stringify(ts)===JSON.stringify(o.trials)&&JSON.stringify(cs)===JSON.stringify(o.conflicts),"trace "+name);
   ok((a.status==="halt")===(exact.status==="SAT")&&a.tapes[0]===(exact.bits||"")&&a.tapes[19]===s&&BigInt(a.steps)<=e.T&&BigInt(ts.length)<=e.C,"exact "+name);
   if(local)special++;else{fallback++;if(a.status==="halt")fallbackSat++;else fallbackUnsat++;}
   trials+=ts.length;conflicts+=cs.length;
   const old=Prev.executeIR(G[i],I);ok(old.status===a.status&&old.tapes[0]===a.tapes[0],"general baseline");
   let clock=null,prior=null;
   if(a.status==="halt"){sat++;ok(E.valid(raw,a.tapes[0]),"witness");const b=F.count(J[i],I);ok(BigInt(b.N)<=e.N&&BigInt(b.clock)<=e.W&&b.steps===a.steps,"clock");clock=b.clock;prior=F.count(G[i],I).clock;if(clock<prior)improved++;else if(clock===prior)tied++;else regressed++;}else unsat++;
   if(detail&&i===0)rows.push({name,m,route:local?"components":"general",solutions:exact.count,trials:ts.length,steps:a.steps,clock,prior});
  }
 }
 for(const f of fixtures(E,Barrier,Direct,Base))test(f.name,f.m,f.B,true);
 for(let v=0;v<256;v++){for(const h of [[0,3,6],[0,1,2]]){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push(h.map((g,j)=>-(2*g+1+((i>>(2-j))&1))));test("mask-"+h.join("-")+"-"+v,2,B);}}
 for(const k of [2,3])for(const h of E.subsets(Array.from({length:9},(_,i)=>i),k))test("scope-"+h.join("-"),2,[h.map(g=>-(2*g+1))]);
 let seed=0xD6E0;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=2+i%3,B=[];for(let j=0;j<20;j++){const pool=i%2?Component.partition[rand(3)]:Array.from({length:9},(_,g)=>g),k=1+rand(3),gs=[];while(gs.length<k){const g=pool[rand(pool.length)];if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 return {cases,sat,unsat,special,fallback,fallbackSat,fallbackUnsat,trials,conflicts,arith,improved,regressed,tied,rows};
}
module.exports={envelope,fixtures,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'component_fallback_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'direct_extension_ir.js'),require(p+'prefix_order_audit.js'),require(p+'direct_extension_audit.js'),require(p+'component_audit.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'),require(p+'complete_odometer_audit.js'))));}
