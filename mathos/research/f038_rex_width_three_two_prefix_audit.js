// D6H independent adaptive prefix oracle, using decoded primal cliques.
const order=(a,b)=>a.h.at(-1)-b.h.at(-1)||a.h.length-b.h.length||a.h.join().localeCompare(b.h.join());
function fixtures(E,Direct,OldAudit){
 const fs=OldAudit.fixtures(E,Direct);
 // Prefix root with eight leaves; equality or disequality forces a
 // nontrivial rank choice in the residual singleton blocks.
 for(const m of [2,3,4])for(const shift of [0,1]){
  const B=[];for(let g=1;g<9;g++)for(const [a,b] of E.tup(m,2))if(b!==(a+shift)%m)B.push([-(a+1),-(g*m+b+1)]);
  fs.push({name:"prefix-star-"+m+"-"+shift,m,B});
 }
 // Only ternary scopes connect 0 and its residual pairs. Deleting the
 // star center without rebuilding the residual pair edge is unsound.
 for(const m of [2,3]){
  const B=[];for(let g=1;g<9;g+=2)for(const [a,b,c] of E.tup(m,3))if(c!==(a+b)%m)B.push([-(a+1),-(g*m+b+1),-((g+1)*m+c+1)]);
  fs.push({name:"residual-pairs-"+m,m,B});
 }
 // Removing 0 from the connected chain of triples must NOT split it.
 const chain=[];for(let g=1;g<8;g++)chain.push([-1,-(2*g+1),-(2*(g+1)+1)]);
 fs.push({name:"residual-connected",m:2,B:chain});
 // Late-center lex trap: fixed prefix 0 is not a useful separator.
 const trap=[];for(let g=0;g<8;g++)for(const [a,b] of [[0,0],[1,1]])trap.push([-(2*g+a+1),-(16+b+1)]);
 fs.push({name:"late-center-trap",m:2,B:trap});
 // Random connected prefix-cut systems, with both binary and ternary
 // relations, unary restrictions and uneven residual block sizes.
 let seed=0xd6c607;function rnd(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let j=0;j<60;j++){const m=2+j%2,B=[],blocks=[];for(let g=1;g<9;){const b=[];for(let k=0,n=1+rnd(Math.min(3,9-g));k<n;k++)b.push(g++);blocks.push(b);}
  for(const b of blocks){for(const g of b)B.push([-(rnd(m)+1),-(g*m+rnd(m)+1)]);for(let i=1;i<b.length;i++)B.push([-(rnd(m)+1),-(b[i-1]*m+rnd(m)+1),-(b[i]*m+rnd(m)+1)]);
   for(let k=0;k<5;k++){const g=b[rnd(b.length)],h=b[rnd(b.length)];B.push(g===h?[-(g*m+rnd(m)+1)]:[-(rnd(m)+1),-(Math.min(g,h)*m+rnd(m)+1),-(Math.max(g,h)*m+rnd(m)+1)]);}
  }fs.push({name:"random-prefix-"+j,m,B});
 }
 // Two-center modular stars; include prefix-only relation and unary restrictions.
 for(const m of [2,3,4]){
  const B=[];for(let g=2;g<9;g++)for(const [a,b,c] of E.tup(m,3))if(c!==(a+b)%m)B.push([-(a+1),-(m+b+1),-(g*m+c+1)]);
  fs.push({name:"two-center-"+m,m,B});
  fs.push({name:"two-center-prefix-pair-"+m,m,B:B.concat([[-1,-(m+1)]])});
  fs.push({name:"two-center-unary-"+m,m,B:B.concat([[-1],[-(m+1)]])});
 }
 // Two-prefix separator with residual pairs retained from ternary scopes
 // and a residual-connected adversary which must use complete fallback.
 for(const m of [2,3]){
  const B=[];for(let g=2;g<9;g++)B.push([-1,-(m+1),-(g*m+1)]);
  for(const g of [2,4,6])B.push([-(m+1),-(g*m+1),-((g+1)*m+1)]);
  fs.push({name:"two-prefix-pairs-"+m,m,B});
  fs.push({name:"two-prefix-chain-"+m,m,B:B.concat(Array.from({length:6},(_,i)=>[-(m+1),-((i+2)*m+1),-((i+3)*m+1)]))});
 }
 for(let j=0;j<80;j++){const m=2+j%2,B=[],blocks=[];for(let g=2;g<9;){const b=[];for(let k=0,n=1+rnd(Math.min(3,9-g));k<n;k++)b.push(g++);blocks.push(b);}
  for(const b of blocks){for(const g of b)B.push([-(rnd(m)+1),-(m+rnd(m)+1),-(g*m+rnd(m)+1)]);for(let i=1;i<b.length;i++)B.push([-(m+rnd(m)+1),-(b[i-1]*m+rnd(m)+1),-(b[i]*m+rnd(m)+1)]);
   for(let k=0;k<3;k++){const g=b[rnd(b.length)];B.push([-(rnd(m)+1),-(m+rnd(m)+1),-(g*m+rnd(m)+1)]);}
  }B.push([-(rnd(m)+1),-(m+rnd(m)+1)]);fs.push({name:"random-two-"+j,m,B});
 }
 return fs;
}
function oracle(d,domains,Ref){
 const out={seps:[],components:[],trials:[],conflicts:[],conditioned:0};if(!domains)return out;
 const vertices=Array.from({length:9},(_,i)=>i),cs=Ref.residual(d,vertices,[]),r1=Ref.residual(d,vertices,[0]),r2=Ref.residual(d,vertices,[0,1]),conditioned=cs.length===1?(r1.length>1?1:r2.length>1?2:0):0,rs=conditioned===2?r2:r1;out.conditioned=conditioned;
 const z=domains.map(a=>a[0]),fs=d.F.filter(f=>f.h.length>1).sort(order);
 const blocks=conditioned?rs:cs;
 function run(){
  for(const c of blocks){
   out.components.push(c);
   if(!conditioned&&c.length===1)continue;
   const factors=fs.filter(f=>f.h.some(v=>c.includes(v))||conditioned===2&&f.h.every(v=>v<2));
   function carry(i){for(;i>=0;i--){const g=c[i],a=domains[g],k=a.indexOf(z[g]);if(k+1<a.length){z[g]=a[k+1];return true;}z[g]=a[0];}return false;}
   for(;;){out.trials.push(z.slice());const f=factors.find(f=>!f.S.has(f.h.map(g=>z[g]).join()));if(!f)break;
    out.conflicts.push(f.h.slice());const g=f.h.at(-1),old=z[g];if(g<conditioned)return false;
    for(const j of c)if(j>g)z[j]=domains[j][0];
    const next=domains[g].find(a=>a>old&&f.S.has(f.h.map(j=>j===g?a:z[j]).join()));
    if(next!==undefined)z[g]=next;else{z[g]=domains[g][0];if(!carry(c.indexOf(g)-1))return false;}
   }
  }return true;
 }
 if(conditioned){outer:for(const root of domains[0])for(const r1 of conditioned===2?domains[1]:[domains[1][0]]){z[0]=root;z[1]=r1;for(let j=conditioned;j<9;j++)z[j]=domains[j][0];out.seps.push(z.slice(0,conditioned));if(run())break outer;}}
 else run();
 return out;
}
function audit(U,E,Barrier,Prior,Direct,OldAudit,Local,F,Ref){
 const J=[U.machine(false),U.machine(true)],O=[Local.machine(false),Local.machine(true)];
 const eq=(a,b,s)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error(s+" "+JSON.stringify({a,b}));},ok=(v,s)=>{if(!v)throw Error(s)};
 let sat=0,unsat=0,conditioned=0,one=0,two=0,twoSat=0,twoUnsat=0,prefixConflicts=0,cacheHits=0,conditionedSat=0,conditionedUnsat=0,fallback=0,early=0,visits=0,conflicts=0,components=0,separators=0,localChecks=0,graphChecks=0,improved=0,regressed=0,tied=0,oldSteps=0,newSteps=0;const rows=[];
 const fs=fixtures(E,Direct,OldAudit);
 for(const f of fs){const raw=E.encode(f.m,Array(f.m).fill(0),f.B),d=E.decode(raw),ref=Barrier.exact(E,raw),stream=U.stream(E,raw),I=[...Array(19).fill(""),stream],original=Ref.residual(d,Array.from({length:9},(_,i)=>i),[]),residual=Ref.residual(d,Array.from({length:9},(_,i)=>i),[0]),residual2=Ref.residual(d,Array.from({length:9},(_,i)=>i),[0,1]);
  for(let i=0;i<2;i++){const j=J[i],domains=Prior.propagate(E,raw,!!i),expected=oracle(d,domains,Ref),actual={seps:[],components:[],trials:[],conflicts:[],conditioned:0};
   const a=U.executeIR(j,I,(pc,T,h)=>{
    if(pc===j.separatorEntry){actual.conditioned=T[15][18]==="1"?2:1;actual.seps.push(T.slice(1,1+actual.conditioned).map(t=>t.indexOf("x")-1));}
    else if(pc===j.componentEntry){const c=T[15].slice(7,16).map((x,g)=>x==="1"?g:-1).filter(g=>g>=0);actual.components.push(c);if(T[15][19]==="x")cacheHits++;
     const edges=d.F.filter(f=>f.h.length>1).sort(order).flatMap(f=>{const h=f.h.filter(g=>g>=actual.conditioned);return h.slice(1).map(g=>[h[0],g]);}).flat().map(g=>g.toString(2).padStart(4,"0")).join("");
     eq(T[16].slice(1).join("").replace(/_+$/,""),edges,"edge list "+f.name);graphChecks++;}
    else if(pc===j.candidateEntry){actual.trials.push(T.slice(1,10).map(t=>t.indexOf("x")-1));
     const c=actual.components.at(-1),fs=d.F.filter(f=>f.h.length>1&&(f.h.some(g=>c.includes(g))||actual.conditioned===2&&T[15][19]==="1"&&f.h.every(g=>g<2))).sort(order);
     const dir=fs.map(f=>f.h.slice(0,2).map(g=>g.toString(2).padStart(4,"0")).join("")+(f.h.length===2?"0":"1"+f.h[2].toString(2).padStart(4,"0"))).join("");
     const mask=fs.map(f=>{const s=[...E.tup(d.m,f.h.length)].map(z=>f.S.has(z.join())?"0":"1").join("");let out="";for(let k=0;k<s.length;){if(s.slice(k,k+4)==="0000"){out+="11";k+=4;}else out+="0"+s[k++];}return out+"10";}).join("");
     eq(T[18].slice(1).join("").replace(/_+$/,""),dir,"local directory "+f.name);eq(T[17].slice(1).join("").replace(/_+$/,""),mask,"local stream "+f.name);localChecks++;
    }else{const pair=T[12][2]==="_",end=h[18],bits=T[18].slice(end-(pair?9:13),end).join(""),scope=[parseInt(bits.slice(0,4),2),parseInt(bits.slice(4,8),2)];if(!pair)scope.push(parseInt(bits.slice(9,13),2));actual.conflicts.push(scope);if(actual.conditioned===2&&scope.every(g=>g<2))prefixConflicts++;}
   });
   eq(actual,expected,"trace "+f.name+"/"+i);
   ok(a.status===(ref.bits?"halt":"reject")&&a.tapes[0]===(ref.bits||"")&&a.tapes[19]===stream,"oracle "+f.name);
   if(ref.bits){sat++;ok(E.valid(raw,a.tapes[0]),"witness");}else unsat++;
   if(actual.conditioned){conditioned++;if(actual.conditioned===1)one++;else{two++;if(ref.bits)twoSat++;else twoUnsat++;}if(ref.bits)conditionedSat++;else conditionedUnsat++;const r=actual.conditioned===2?residual2:residual,m=f.m**actual.conditioned;ok(actual.seps.length<=m&&actual.trials.length<=m*r.reduce((n,c)=>n+f.m**c.length,0),"separator ceiling");}else if(domains){fallback++;ok(actual.trials.length<=original.reduce((n,c)=>n+f.m**c.length,0),"fallback ceiling");}else early++;
   visits+=actual.trials.length;conflicts+=actual.conflicts.length;components+=actual.components.length;separators+=actual.seps.length;
   const old=Local.executeIR(O[i],I);ok(old.status===a.status&&old.tapes[0]===a.tapes[0],"D6G parity");
   oldSteps+=old.steps;newSteps+=a.steps;if(a.steps<old.steps)improved++;else if(a.steps>old.steps)regressed++;else tied++;
   if(i===0&&(f.name.startsWith("family-")||f.name.startsWith("prefix-star")||f.name.startsWith("residual-")||f.name==="late-center-trap"||f.name.startsWith("two-"))){
    let clock=null,oldClock=null;if(ref.bits){clock=F.count(j,I).clock;oldClock=F.count(O[i],I).clock;}
    rows.push({name:f.name,status:ref.status,conditioned:actual.conditioned,rootVisits:actual.seps.length,visits:actual.trials.length,steps:a.steps,oldSteps:old.steps,clock,oldClock,residual:(actual.conditioned===2?residual2:residual).map(c=>c.length)});
   }
  }
 }
 return {cases:fs.length,modes:2*fs.length,sat,unsat,conditioned,one,two,twoSat,twoUnsat,prefixConflicts,cacheHits,conditionedSat,conditionedUnsat,fallback,early,visits,conflicts,components,separators,localChecks,graphChecks,improved,regressed,tied,oldSteps,newSteps,ir:J.map(j=>j.ins.length),rows};
}
module.exports={fixtures,oracle,audit};
if(require.main===module){const p="./f038_rex_width_three_";console.log(JSON.stringify(audit(require(p+"two_prefix_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require(p+"completeness_barrier.js"),require(p+"prefix_order_audit.js"),require(p+"direct_extension_audit.js"),require(p+"auto_component_audit.js"),require(p+"prefix_separator_ir.js"),require(p+"fast_clock.js"),require(p+"separator_reference.js"))));}
