// D6D: independent connected-component reference, fixed partition guard,
// exact per-component candidate trace and conditional resource accounting.
const partition=[[0,3,6],[1,4,7],[2,5,8]],order=(a,b)=>a.h.at(-1)-b.h.at(-1)||a.h.length-b.h.length||a.h.join().localeCompare(b.h.join());
function admitted(E,raw){const d=E.decode(raw);return !!d&&d.F.every(f=>f.h.every(g=>g%3===f.h[0]%3));}
function exactComponents(E,raw){
 const d=E.decode(raw),parent=Array.from({length:9},(_,i)=>i),root=i=>parent[i]===i?i:root(parent[i]);
 for(const f of d.F)for(const g of f.h)parent[root(g)]=root(f.h[0]);
 const cs=[];for(let g=0;g<9;g++){let c=cs.find(c=>root(c[0])===root(g));if(!c){c=[];cs.push(c);}c.push(g);}
 const z=Array(9).fill(0),sizes=[],counts=[];let count=1,visits=0;
 for(const c of cs){const fs=d.F.filter(f=>c.includes(f.h[0])),first=[];let n=0;
  for(const a of E.tup(d.m,c.length)){visits++;if(fs.every(f=>f.S.has(f.h.map(g=>a[c.indexOf(g)]).join()))){if(!n)first.push(...a);n++;}}
  if(n)c.forEach((g,i)=>z[g]=first[i]);count*=n;sizes.push(c.length);counts.push(n);
 }
 const bits=count?E.witness(d.m,d.pins,z):null;if(bits&&!E.valid(raw,bits))throw Error("component witness");return {components:cs,sizes,counts,count,z:count?z:null,bits,visits};
}
function traceOracle(E,raw,domains){
 const out={trials:[],conflicts:[],per:[0,0,0]};if(!domains)return out;
 const fs=E.decode(raw).F.filter(f=>f.h.length>1).sort(order),z=domains.map(a=>a[0]);
 for(let c=0;c<3;c++){const gs=partition[c],factors=fs.filter(f=>f.h[0]%3===c);
  function carry(j){for(let i=gs.indexOf(j);i>=0;i--){const g=gs[i],a=domains[g],k=a.indexOf(z[g]);if(k+1<a.length){z[g]=a[k+1];return true;}z[g]=a[0];}return false;}
  while(true){out.trials.push({c,z:z.slice()});out.per[c]++;const f=factors.find(f=>!f.S.has(f.h.map(g=>z[g]).join()));if(!f)break;
   const g=f.h.at(-1),old=z[g];out.conflicts.push({c,scope:f.h.slice()});
   for(const j of gs)if(j>g)z[j]=domains[j][0];
   const next=domains[g].find(a=>a>old&&f.S.has(f.h.map(j=>j===g?a:z[j]).join()));
   if(next!==undefined)z[g]=next;else{z[g]=domains[g][0];const i=gs.indexOf(g);if(i===0||!carry(gs[i-1]))return out;}
  }
 }return out;
}
function envelope(V,m,full=false){
 const e=V.envelope(m),k=BigInt(m),S=e.S,C=3n*k**3n,N=S+35n*k+1479n,T=131072n*S*(C+(full?k:1n)+1n),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>2097152n*k**3n*e.L*e.L||total>512n*e.L**3n)throw Error("envelope");return {C,N,T,W,total};
}
// D6C first-factor certificates restricted to each admitted component.
// Every component has three coordinates; the trial bound adds across
// components rather than multiplying their root assignments.
function rootEnvelope(V,m,full=false,r=3){
 const e=V.envelope(m),k=BigInt(m),S=e.S,rr=BigInt(Math.max(1,r)),bound=3n+27n*k**rr,C=bound<3n*k**3n?bound:3n*k**3n,N=S+35n*k+1479n,T=131072n*S*(C+(full?k:1n)+1n),W=(20n*N+12n)*T+6n,total=4n*e.P+32n*e.L+384n*S*S+W;
 if(N>2n*S||total>2097152n*k**rr*e.L*e.L)throw Error("root envelope");
 if(r<=1&&total**3n>131072n**3n*e.L**7n||r===2&&total**3n>8192n**3n*e.L**8n||r===3&&total>512n*e.L**3n)throw Error("root class");
 return {C,N,T,W,total};
}
function audit(U,E,Barrier,Prev,Prior,Direct,F,V){
 const J=[U.machine(false),U.machine(true)],O=[Prev.machine(false),Prev.machine(true)],ok=(x,s)=>{if(!x)throw Error(s)};
 let rootChecks=0,rootClasses=[0,0,0,0],cases=0,accepted=0,outside=0,sat=0,unsat=0,trials=0,conflicts=0,arith=0,improved=0,regressed=0,tied=0;const rows=[];
 for(let m=2;m<=10000;m++)for(const full of [false,true]){envelope(V,m,full);for(const r of [1,2,3])rootEnvelope(V,m,full,r);arith++;}
 for(const k of [20n,30n,40n,50n,100n,1024n])for(const d of [-1n,0n,1n])for(const full of [false,true]){envelope(V,(1n<<k)+d,full);for(const r of [1,2,3])rootEnvelope(V,(1n<<k)+d,full,r);arith++;}
 function test(name,m,B,detail=false,compare=true){
  const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),d=admitted(E,raw),exact=Barrier.exact(E,raw),co=exactComponents(E,raw),s=U.stream(E,raw),I=[...Array(19).fill(""),s];
  ok(co.count===exact.count&&co.bits===exact.bits,"component exact "+name);cases++;
  for(let i=0;i<2;i++){
   const full=!!i,ts=[],cs=[],a=U.executeIR(J[i],I,(pc,T,h)=>{
    const c=["0","1","x"].indexOf(T[15][1]);if(pc===J[i].candidateEntry)ts.push({c,z:T.slice(1,10).map(a=>a.indexOf("x")-1)});
    else{const end=h[13],pair=T[12][2]==="_",len=pair?9:13,bits=T[13].slice(end-len,end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));cs.push({c,scope});}
   });
   if(!d){outside++;ok(a.status==="reject"&&a.tapes[0]===""&&ts.length===0&&a.tapes.slice(1,10).every(x=>x===""),"cross guard "+name);continue;}
   accepted++;const e=envelope(V,m,full),o=traceOracle(E,raw,Prior.propagate(E,raw,full));
   const cert=Direct.certificate(E,raw),rs=partition.map(c=>c.filter(g=>!cert.determined[g]).length),r=Math.max(...rs),re=rootEnvelope(V,m,full,r);
   for(let c=0;c<3;c++)ok(BigInt(o.per[c])<=1n+9n*BigInt(m)**BigInt(rs[c]),"component root bound");
   ok(BigInt(ts.length)<=re.C&&BigInt(a.steps)<=re.T,"max-root bound");rootChecks++;rootClasses[r]++;
   ok(JSON.stringify(ts)===JSON.stringify(o.trials)&&JSON.stringify(cs)===JSON.stringify(o.conflicts),"trace "+name);
   ok((a.status==="halt")===(exact.status==="SAT")&&a.tapes[0]===(exact.bits||"")&&a.tapes[19]===s&&BigInt(a.steps)<=e.T&&BigInt(ts.length)<=e.C,"exact "+name);trials+=ts.length;conflicts+=cs.length;
   let old=null,oldTrials=0,clock=null,prior=null;if(compare){old=Prev.executeIR(O[i],I,pc=>{if(pc===O[i].candidateEntry)oldTrials++;});ok(old.status===a.status&&old.tapes[0]===a.tapes[0],"prior");}
   if(a.status==="halt"){sat++;ok(E.valid(raw,a.tapes[0]),"witness");const b=F.count(J[i],I);ok(BigInt(b.N)<=e.N&&BigInt(b.clock)<=e.W&&b.steps===a.steps,"clock");ok(BigInt(b.clock)<=re.W&&BigInt(b.N)<=re.N,"max-root clock");clock=b.clock;if(old){prior=F.count(O[i],I).clock;if(clock<prior)improved++;else if(clock===prior)tied++;else regressed++;}}else unsat++;
   if(detail&&i===0)rows.push({name,m,count:co.count,components:co.sizes,roots:rs,trials:ts.length,per:o.per,oldTrials:compare?oldTrials:null,steps:a.steps,oldSteps:old?.steps??null,clock,prior});
  }
 }
 test("empty",2,[],true);test("empty-domain",2,[[-1],[-2]],true);
 for(let m=2;m<=5;m++)for(const unsat of [false,true])test("triple-"+m+(unsat?"-unsat":"-sat"),m,Direct.family(E,m,3,unsat),true,m<=4);
 for(let v=0;v<256;v++){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(7+((i>>1)&1)),-(13+(i&1))]);test("mask-"+v,2,B);}
 for(const k of [2,3])for(const h of E.subsets(Array.from({length:9},(_,i)=>i),k))if(h.some(g=>g%3!==h[0]%3))test("cross-"+h.join("-"),2,[h.map(g=>-(2*g+1))],false,false);
 let seed=0xD6D0;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<60;i++){const m=2+i%3,B=[];for(let j=0;j<20;j++){const c=partition[rand(3)],k=1+rand(3),gs=[];while(gs.length<k){const g=c[rand(3)];if(!gs.includes(g))gs.push(g);}B.push(gs.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}test("random-"+i,m,B);}
 return {rootChecks,rootClasses,cases,accepted,outside,sat,unsat,trials,conflicts,arith,improved,regressed,tied,rows};
}
module.exports={partition,admitted,exactComponents,traceOracle,envelope,rootEnvelope,audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'component_ir.js'),require('./f038_tga_normalized_integration.js').engine(),require(p+'completeness_barrier.js'),require(p+'direct_extension_ir.js'),require(p+'prefix_order_audit.js'),require(p+'direct_extension_audit.js'),require(p+'fast_clock.js'),require(p+'singleton_envelope.js'))));}
