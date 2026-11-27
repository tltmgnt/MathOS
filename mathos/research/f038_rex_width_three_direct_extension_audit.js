// D6C: independent direct-extension oracle, certificate-first admission,
// and exact resource arithmetic for the fixed-nine normalized family.
const order=(a,b)=>a.h.at(-1)-b.h.at(-1)||a.h.length-b.h.length||a.h.join().localeCompare(b.h.join());
function functional(f){
 const seen=new Set();for(const key of f.S){const p=key.split(",").slice(0,-1).join(",");if(seen.has(p))return false;seen.add(p);}return true;
}
function certificate(E,raw){
 const d=E.decode(raw),first=Array(9).fill(null),determined=Array(9).fill(false);
 for(const f of d.F.slice().sort(order)){
  const g=f.h.at(-1);
  if(f.h.length===1){if(functional(f))determined[g]=true;continue;}
  if(!first[g]){first[g]=f.h.slice();if(functional(f))determined[g]=true;}
 }
 return {first,determined,r:determined.filter(x=>!x).length};
}
// Host oracle uses decoded relations, not the physical run tokens.
function oracle(E,raw,domains){
 const factors=E.decode(raw).F.filter(f=>f.h.length>1).sort(order),out={trials:[],conflicts:[],skipped:0,leaps:0};
 if(!domains)return out;
 const z=domains.map(a=>a[0]),ordinal=()=>z.reduce((v,a,j)=>v*domains[j].length+domains[j].indexOf(a),0),total=domains.reduce((v,a)=>v*a.length,1);
 function advance(j){for(;j>=0;j--){const a=domains[j],k=a.indexOf(z[j]);if(k+1<a.length){z[j]=a[k+1];return true;}z[j]=a[0];}return false;}
 while(true){
  out.trials.push(z.slice());const f=factors.find(f=>!f.S.has(f.h.map(g=>z[g]).join()));if(!f)return out;
  const g=f.h.at(-1),old=ordinal(),prior=z[g];out.conflicts.push({scope:f.h.slice(),g});
  for(let j=g+1;j<9;j++)z[j]=domains[j][0];
  const next=domains[g].find(a=>a>prior&&f.S.has(f.h.map(j=>j===g?a:z[j]).join()));
  if(next!==undefined)z[g]=next;
  else{z[g]=domains[g][0];if(!advance(g-1)){out.skipped+=total-old-1;return out;}}
  const jump=ordinal()-old;out.skipped+=jump-1;
  if(next!==undefined&&domains[g].indexOf(next)>domains[g].indexOf(prior)+1||next===undefined&&domains[g].indexOf(prior)<domains[g].length-1)out.leaps++;
 }
}
function family(E,m,r,unsat=false){
 const B=[],factor=(h,allowed)=>{for(const z of E.tup(m,h.length))if(!allowed(z))B.push(h.map((g,i)=>-(g*m+z[i]+1)));};
 if(r===1){for(let j=1;j<9;j++)factor([0,j],([a,b])=>a===b);factor([0,1,8],([a,b,c])=>a!==b||b!==c||(!unsat&&a===m-1));}
 else if(r===2){factor([0,2],([a,c])=>a===c);factor([1,3],([b,c])=>b===c);for(let j=4;j<9;j++)factor([0,1,j],([a,b,c])=>c===(a+b)%m);factor([2,3,8],([a,b,c])=>c!==(a+b)%m||(!unsat&&a===m-1&&b===m-1));}
 else if(r===3){for(let j=3;j<9;j++)factor([(j-3)%3,j],([a,b])=>a===b);factor([3,4,5],z=>!unsat&&z.every(a=>a===m-1));}
 else throw Error("roots");
 return B;
}
function envelope(V,m,full=false,r=9){
 const e=V.envelope(m),k=BigInt(m),S=e.S,C=r>=9?k**9n:1n+27n*k**BigInt(Math.max(1,r)),N=S+35n*k+1479n,T=131072n*S*(C+(full?k:1n)),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>2097152n*k**BigInt(Math.max(1,r))*e.L*e.L)throw Error("envelope");
 if(r===1&&total**3n>131072n**3n*e.L**7n||r===2&&total**3n>8192n**3n*e.L**8n||r===3&&total>512n*e.L**3n)throw Error("class envelope");
 return {C,N,T,W,total};
}
function fixtures(E,Barrier,Prior,Base){
 const fs=Base.fixtures(E,Barrier);
 for(const r of [1,2,3])for(const unsat of [false,true])fs.push({name:"cert-"+r+"-"+(unsat?"unsat":"sat"),m:2,B:family(E,2,r,unsat),r});
 fs.push({name:"cert-1-m3-sat",m:3,B:family(E,3,1),r:1});
 return fs;
}
function audit(U,E,Barrier,Prev,Prior,F,V,Base){
 const J=[U.machine(false),U.machine(true)],O=[Prev.machine(false),Prev.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 let cases=0,sat=0,unsat=0,trials=0,conflicts=0,skipped=0,leaps=0,improved=0,tied=0,regressed=0,arith=0,certified=0,trialGains=0,trialLosses=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){for(const r of [1,2,3,9])envelope(V,m,full,r);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){for(const r of [1,2,3,9])envelope(V,(1n<<k)+d,full,r);arith++;}
 function test(name,m,B,detail=false,expectedRoots=null,compare=true){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),exact=Barrier.exact(E,raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s],cert=certificate(E,raw);
  if(expectedRoots!==null){ok(cert.r<=expectedRoots&&exact.count===(name.endsWith("unsat")?0:1),"certificate "+name);certified++;}
  for(let i=0;i<2;i++){
   const full=!!i,domains=Prior.propagate(E,raw,full),o=oracle(E,raw,domains),ts=[],cs=[],a=U.executeIR(J[i],I,(pc,T,h)=>{
    if(pc===J[i].candidateEntry)ts.push(T.slice(1,10).map(a=>a.indexOf("x")-1));
    else{const end=h[13],pair=T[12][2]==="_",len=pair?9:13,bits=T[13].slice(end-len,end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));cs.push({scope,g:scope.at(-1)});}
   }),e=envelope(V,m,full,expectedRoots===null?9:expectedRoots);
   ok(JSON.stringify(ts)===JSON.stringify(o.trials)&&JSON.stringify(cs)===JSON.stringify(o.conflicts),"trace "+name);
   ok((a.status==="halt")===(exact.status==="SAT")&&a.tapes[0]===(exact.bits||"")&&a.tapes[19]===s&&BigInt(a.steps)<=e.T&&BigInt(ts.length)<=e.C,"exact "+name);
   trials+=ts.length;conflicts+=cs.length;skipped+=o.skipped;leaps+=o.leaps;
   let old=null,oldTrials=0,clock=null,prior=null;if(compare){old=Prev.executeIR(O[i],I,pc=>{if(pc===O[i].candidateEntry)oldTrials++;});ok(old.status===a.status&&old.tapes[0]===a.tapes[0],"baseline");if(ts.length<oldTrials)trialGains++;else if(ts.length>oldTrials)trialLosses++;}
   if(a.status==="halt"){sat++;ok(E.valid(raw,a.tapes[0]),"witness");const b=F.count(J[i],I);ok(BigInt(b.N)<=e.N&&BigInt(b.clock)<=e.W&&b.steps===a.steps,"clock");clock=b.clock;
    if(old){prior=F.count(O[i],I).clock;if(clock<prior)improved++;else if(clock===prior)tied++;else regressed++;}
   }else unsat++;
   if(detail&&i===0)rows.push({name,m,roots:cert.r,count:exact.count,trials:ts.length,oldTrials:compare?oldTrials:null,leaps:o.leaps,steps:a.steps,oldSteps:old?.steps??null,clock,prior});
  }cases++;
 }
 for(const f of Base.fixtures(E,Barrier))test(f.name,f.m,f.B,true);
 for(let v=0;v<256;v++){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);test("mask-"+v,2,B);}
 let seed=0xD6C0;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<90;i++){const m=2+i%3,B=[];for(let j=0;j<24;j++){const k=1+rand(3),gs=[];while(gs.length<k){let g=rand(9);if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 for(let m=2;m<=4;m++)for(const r of [1,2])for(const unsat of [false,true])test("prior-"+r+"-"+m+"-"+(unsat?"unsat":"sat"),m,Prior.family(E,m,r,unsat),true);
 for(let m=2;m<=4;m++)for(const r of [1,2,3])for(const unsat of [false,true])test("cert-"+r+"-"+m+"-"+(unsat?"unsat":"sat"),m,family(E,m,r,unsat),true,r);
 return {cases,sat,unsat,trials,conflicts,skipped,leaps,improved,tied,regressed,arith,certified,trialGains,trialLosses,rows};
}
module.exports={certificate,oracle,family,envelope,fixtures,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'direct_extension_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'prefix_order_ir.js'),require(p+'prefix_order_audit.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'),require(p+'complete_odometer_audit.js'))));}
