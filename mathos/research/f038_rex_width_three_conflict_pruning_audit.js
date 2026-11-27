// D6A independent conflict-prefix oracle, exact trace verification,
// complete search comparison, and conditional worst-case accounting.
function oracle(E,raw,domains){
 const d=E.decode(raw),z=domains.map(a=>a[0]),out={trials:[],conflicts:[],z:null,skipped:0};
 if(domains.some(a=>!a.length))return out;
 const factors=d.F.filter(f=>f.h.length>1).sort((a,b)=>a.h.length-b.h.length||a.h.join().localeCompare(b.h.join()));
 const suffix=g=>domains.slice(g+1).reduce((v,a)=>v*a.length,1);
 const ordinal=z=>z.reduce((v,a,g)=>v*domains[g].length+domains[g].indexOf(a),0);
 const total=suffix(-1);
 while(true){
  out.trials.push(z.slice());const f=factors.find(f=>!f.S.has(f.h.map(g=>z[g]).join()));
  if(!f){out.z=z.slice();return out;}
  const g=f.h.at(-1),old=ordinal(z);out.conflicts.push({scope:f.h.slice(),g});
  for(let j=g+1;j<9;j++)z[j]=domains[j][0];
  let j=g;while(j>=0&&domains[j].indexOf(z[j])===domains[j].length-1){z[j]=domains[j][0];j--;}
  if(j<0){out.skipped+=total-old-1;return out;}
  z[j]=domains[j][domains[j].indexOf(z[j])+1];out.skipped+=ordinal(z)-old-1;
 }
}
function envelope(V,m,full=false){const e=V.envelope(m),k=BigInt(m),S=e.S,N=S+35n*k+1479n,T=131072n*S*(k**9n+(full?k:1n)),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;if(N>2n*S||total>2097152n*k**9n*e.L*e.L)throw Error("envelope");return {N,T,W,total};}
function audit(U,E,Barrier,Prev,Prop,F,V,OldAudit){
 const J=[U.machine(false),U.machine(true)],O=[Prev.machine(false),Prev.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 let cases=0,sat=0,unsat=0,traceTrials=0,traceConflicts=0,skipped=0,improved=0,tied=0,regressed=0,arith=0;const rows=[];

 for(let m=2;m<=10000;m++)for(const full of [false,true]){envelope(V,m,full);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){envelope(V,(1n<<k)+d,full);arith++;}
 function test(name,m,B,detail=false,compare=true){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),exact=Barrier.exact(E,raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s];
  for(let i=0;i<2;i++){
   const full=!!i,ref=Prop.oracle(E,raw,full),o=ref.empty?{trials:[],conflicts:[],z:null,skipped:0}:oracle(E,raw,ref.domains),trials=[],conflicts=[];
   const r=U.executeIR(J[i],I,(pc,T,h)=>{
    if(pc===J[i].candidateEntry)trials.push(T.slice(1,10).map(a=>a.indexOf("x")-1));
    else{const end=h[13],pair=T[12][2]==="_",len=pair?9:13,bits=T[13].slice(end-len,end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));conflicts.push({scope,g:scope.at(-1)});}
   }),e=envelope(V,m,full);
   ok(JSON.stringify(trials)===JSON.stringify(o.trials)&&JSON.stringify(conflicts)===JSON.stringify(o.conflicts),"trace "+name);
   ok((r.status==="halt")===(exact.status==="SAT")&&r.tapes[0]===(exact.bits||"")&&r.tapes[19]===s&&BigInt(r.steps)<=e.T,"exact "+name);
   traceTrials+=trials.length;traceConflicts+=conflicts.length;skipped+=o.skipped;
   const old=compare?Prev.executeIR(O[i],I):null;
   if(old){ok(old.status===r.status&&old.tapes[0]===r.tapes[0],"baseline");}
   let clock=null,prior=null;
   if(r.status==="halt"){sat++;ok(E.valid(raw,r.tapes[0]),"witness");const f=F.count(J[i],I);ok(BigInt(f.N)<=e.N&&BigInt(f.clock)<=e.W&&f.steps===r.steps,"clock");clock=f.clock;
    if(compare){prior=F.count(O[i],I).clock;if(clock<prior)improved++;else if(clock===prior)tied++;else regressed++;}
   }else unsat++;
   if(detail&&i===0)rows.push({name,m,solutionCount:exact.count,trials:trials.length,conflicts:conflicts.length,skipped:o.skipped,steps:r.steps,oldSteps:old?.steps??null,clock,prior});
   if(name.startsWith("star-"))ok(trials.length<=8*m*(m-1)+m,"star trial bound");
  }cases++;
 }
 for(const f of OldAudit.fixtures(E,Barrier))test(f.name,f.m,f.B,true);
 for(let v=0;v<256;v++){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,B);}
 let seed=0xD5A9;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=i%3===0?3:2,B=[];for(let j=0;j<18;j++){const k=1+rand(3),gs=[];while(gs.length<k){let g=rand(9);if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 for(let m=2;m<=6;m++)for(const unsat of [false,true])test("star-"+m+(unsat?"-unsat":"-sat"),m,Barrier.family(E,m,unsat).B,true,m===2);
 return {cases,sat,unsat,traceTrials,traceConflicts,skipped,improved,tied,regressed,arith,rows};
}
module.exports={oracle,envelope,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'conflict_pruning_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'complete_odometer_ir.js'),require(p+'sparse_audit.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'),require(p+'complete_odometer_audit.js'))));}
