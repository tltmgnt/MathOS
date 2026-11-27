// D6E: independent relation oracle for graph discovery and component traces.
const order=(a,b)=>a.h.at(-1)-b.h.at(-1)||a.h.length-b.h.length||a.h.join().localeCompare(b.h.join());
function components(d){
 const adj=Array.from({length:9},()=>new Set());
 for(const f of d.F)for(const a of f.h)for(const b of f.h)if(a!==b){adj[a].add(b);adj[b].add(a);}
 const seen=new Set(),out=[];
 for(let i=0;i<9;i++)if(!seen.has(i)){const c=[i];seen.add(i);for(let j=0;j<c.length;j++)for(const g of adj[c[j]])if(!seen.has(g)){seen.add(g);c.push(g);}out.push(c.sort((a,b)=>a-b));}
 return out;
}
function oracle(d,domains){
 const out={components:[],trials:[],conflicts:[]};if(!domains)return out;
 const z=domains.map(a=>a[0]),fs=d.F.filter(f=>f.h.length>1).sort(order);
 for(const c of components(d)){
  out.components.push(c);if(c.length===1)continue;
  const factors=fs.filter(f=>c.includes(f.h[0]));
  function carry(i){for(;i>=0;i--){const g=c[i],a=domains[g],k=a.indexOf(z[g]);if(k+1<a.length){z[g]=a[k+1];return true;}z[g]=a[0];}return false;}
  for(;;){out.trials.push(z.slice());const f=factors.find(f=>!f.S.has(f.h.map(g=>z[g]).join()));if(!f)break;
   out.conflicts.push(f.h.slice());const g=f.h.at(-1),old=z[g];
   for(const j of c)if(j>g)z[j]=domains[j][0];
   const next=domains[g].find(a=>a>old&&f.S.has(f.h.map(j=>j===g?a:z[j]).join()));
   if(next!==undefined)z[g]=next;else{z[g]=domains[g][0];if(!carry(c.indexOf(g)-1))return out;}
  }
 }
 return out;
}
function fixtures(E,Direct){
 const out=[{name:"empty",m:2,B:[]},{name:"empty-domain",m:2,B:[[-1],[-2]]}];
 for(const k of [2,3])for(const h of E.subsets(Array.from({length:9},(_,i)=>i),k))out.push({name:"scope-"+h.join("-"),m:2,B:[h.map(g=>-(2*g+1))]});
 for(let m=2;m<=3;m++)for(let r=1;r<=3;r++)for(const unsat of [false,true])out.push({name:"family-"+r+"-"+m+"-"+(unsat?"unsat":"sat"),m,B:Direct.family(E,m,r,unsat)});
 for(let mask=0;mask<256;mask++){const B=[];for(let i=0;i<8;i++)if(mask>>i&1)B.push([-(1+(i>>2)),-(5+((i>>1)&1)),-(11+(i&1))]);out.push({name:"mask-"+mask,m:2,B});}
 // Every integer partition of nine, with interleaved labels; force each
 // nontrivial block connected via equality edges.
 function parts(n,lo=1,p=[]){if(n===0){const labels=[0,4,8,3,7,2,6,1,5],B=[];let at=0;for(const k of p){const c=labels.slice(at,at+k).sort((a,b)=>a-b);at+=k;for(let j=1;j<c.length;j++)for(const [a,b] of [[0,1],[1,0]])B.push([-(2*c[j-1]+a+1),-(2*c[j]+b+1)]);}out.push({name:"partition-"+p.join("-"),m:2,B});return;}for(let k=lo;k<=n;k++)parts(n-k,k,p.concat(k));}
 parts(9);
 let seed=0xD6E0;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let i=0;i<90;i++){const m=2+i%2,B=[],perm=Array.from({length:9},(_,j)=>j);for(let j=8;j>0;j--){const k=rand(j+1);[perm[j],perm[k]]=[perm[k],perm[j]];}const cs=[];while(perm.length)cs.push(perm.splice(0,1+rand(perm.length)));for(let j=0;j<12;j++){const c=cs[rand(cs.length)],k=1+rand(Math.min(3,c.length)),h=[];while(h.length<k){const g=c[rand(c.length)];if(!h.includes(g))h.push(g);}B.push(h.sort((a,b)=>a-b).map(g=>-(g*m+rand(m)+1)));}out.push({name:"random-"+i,m,B});}
 return out;
}
function audit(U,E,Barrier,Prior,Direct,Old,Fixed,F){
 const J=[U.machine(false),U.machine(true)],O=[Old.machine(false),Old.machine(true)],P=[Fixed.machine(false),Fixed.machine(true)];
 const eq=(a,b,s)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(s+" "+JSON.stringify({a,b}));},ok=(v,s)=>{if(!v)throw Error(s)};
 let sat=0,unsat=0,cases=0,visits=0,conflicts=0,discoveries=0,singletons=0,crossingSat=0,crossingUnsat=0,connected=0,graphChecks=0;const rows=[],widths=Array(10).fill(0);
 for(const f of fixtures(E,Direct)){
  cases++;const raw=E.encode(f.m,Array(f.m).fill(0),f.B),d=E.decode(raw),ref=Barrier.exact(E,raw),cs=components(d),w=Math.max(...cs.map(c=>c.length)),cross=d.F.some(f=>f.h.some(g=>g%3!==f.h[0]%3));
  widths[w]++;const expectedGraph=d.F.filter(f=>f.h.length>1).sort(order).flatMap(f=>f.h.slice(1).map(g=>[f.h[0],g])).flat().map(g=>g.toString(2).padStart(4,"0")).join("");
  const stream=U.stream(E,raw),I=[...Array(19).fill(""),stream];
  for(let i=0;i<2;i++){
   const j=J[i],actual={components:[],trials:[],conflicts:[]};
   const a=U.executeIR(j,I,(pc,T,h)=>{
    if(pc===j.componentEntry){const c=T[15].slice(7,16).map((x,g)=>x==="1"?g:-1).filter(g=>g>=0);actual.components.push(c);eq(T[16].slice(1).join("").replace(/_+$/,""),expectedGraph,"edge list "+f.name);graphChecks++;}
    else if(pc===j.candidateEntry)actual.trials.push(T.slice(1,10).map(t=>t.indexOf("x")-1));
    else {const pair=T[12][2]==="_",end=h[13],bits=T[13].slice(end-(pair?9:13),end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));actual.conflicts.push(scope);}
   });
   eq(actual,oracle(d,Prior.propagate(E,raw,!!i)),"trace "+f.name+"/"+i);
   ok(a.status===(ref.status==="SAT"?"halt":"reject")&&a.tapes[0]===(ref.bits||"")&&a.tapes[19]===stream,"result "+f.name);
   ok(actual.trials.length<=cs.filter(c=>c.length>1).reduce((n,c)=>n+f.m**c.length,0),"component ceiling");
   if(ref.bits){sat++;ok(E.valid(raw,a.tapes[0]),"witness");if(cross)crossingSat++;}else{unsat++;if(cross)crossingUnsat++;}
   if(w===9)connected++;visits+=actual.trials.length;conflicts+=actual.conflicts.length;discoveries+=actual.components.length;singletons+=actual.components.filter(c=>c.length===1).length;
   if(i===0&&(f.name==="empty"||f.name==="scope-0-1"||f.name.startsWith("family-"))){const prior=Old.executeIR(O[i],I),fixed=cross?null:Fixed.executeIR(P[i],I);
    let clock=null,priorClock=null,fixedClock=null;if(ref.bits){clock=F.count(j,I).clock;priorClock=F.count(O[i],I).clock;if(fixed)fixedClock=F.count(P[i],I).clock;}
    rows.push({name:f.name,width:w,steps:a.steps,priorSteps:prior.steps,fixedSteps:fixed?.steps??null,visits:actual.trials.length,clock,priorClock,fixedClock});
   }
  }
 }
 return {cases,modes:2*cases,sat,unsat,crossingSat,crossingUnsat,connected,visits,conflicts,discoveries,singletons,graphChecks,widths,ir:J.map(j=>j.ins.length),rows};
}
module.exports={components,oracle,fixtures,audit};
if(require.main===module){const p="./f038_rex_width_three_";console.log(JSON.stringify(audit(require(p+"auto_component_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require(p+"completeness_barrier.js"),require(p+"prefix_order_audit.js"),require(p+"direct_extension_audit.js"),require(p+"direct_extension_ir.js"),require(p+"component_ir.js"),require(p+"fast_clock.js"))));}
