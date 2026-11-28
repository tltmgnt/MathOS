// D7C finite host audit, independent exhaustive model oracle.
function audit(P,V){
 const ok=(b,msg)=>{if(!b)throw Error(msg);},stats={cases:0,models:0,sat:0,unsat:0,refuted:0,unknownUnsat:0,localMasks:0,tamperRejected:0},rows=[];
 function* subsets(n,r,start=0){if(r===0){yield [];return;}for(let i=start;i<=n-r;i++)for(const t of subsets(n,r-1,i+1))yield [i,...t];}
 function factor(h,mask){const S=new Set();for(let j=0;j<2**h.length;j++)if(mask>>j&1)S.add(h.map((_,i)=>j>>i&1).join());return {h,S};}
 function models(d){const m=[];for(let j=0;j<2**d.k;j++){const z=Array.from({length:d.k},(_,i)=>j>>i&1);if(d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join())))m.push(z.join());}return m.sort();}
 function check(d){
  const m=models(d),r=P.reduce(d,V.verify),out=models(r.d).map(t=>r.expand(t.split(",").map(Number)).join()).sort();
  ok(JSON.stringify(m)===JSON.stringify(out),"model preservation");stats.cases++;stats.models+=m.length;stats[m.length?"sat":"unsat"]++;
  if(r.contradiction){ok(!m.length&&V.verify(d,r.cert),"sound");stats.refuted++;}
  else if(!m.length)stats.unknownUnsat++;
  return r;
 }
 for(let n=1;n<=3;n++)for(let mask=0;mask<2**(2**n);mask++){check({k:n,m:2,F:[factor(Array.from({length:n},(_,i)=>i),mask)]});stats.localMasks++;}
 for(let k of [2,3])for(let mask=0;mask<256;mask++){
  const F=[];
  if(k===2){const scopes=[[0],[0],[1],[1],[0,1],[0,1],[0,1],[0,1]];for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor(scopes[j],((1<<(2**scopes[j].length))-1)^(1<<(j<4?j%2:j-4))));}
  else for(let j=0;j<8;j++)if(mask>>j&1)F.push(factor([0,1,2],255^(1<<j)));
  check({k,m:2,F});
 }
 let seed=0xd7c024;const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let t=0;t<128;t++){const k=3+t%4,F=[];for(let j=0;j<2+t%11;j++){const h=[...new Set(Array.from({length:1+rand()%3},()=>rand()%k))].sort((a,b)=>a-b);F.push(factor(h,rand()>>>16));}check({k,m:2,F});}
 const dense=k=>({k,m:2,F:[...subsets(k,3)].map(h=>factor(h,126))});
 const d5=dense(5),r3=P.resolution(d5,3),r4=P.resolution(d5,4);
 ok(r3.kind==="unknown"&&r3.clauses===20&&r4.kind==="resolution"&&V.verify(d5,r4),"width separation");
 ok(models(dense(4)).length===6&&check(dense(4)).cert.kind==="unknown","NAE4 SAT");
 for(let k of [5,6,8,10,12,16,32]){
  const d=dense(k),r=P.reduce(d,V.verify);
  ok(r.contradiction&&r.cert.kind==="cardinality"&&V.verify(d,r.cert),"dense certificate");
  if(k<=16)check(d);
  rows.push({k,factors:d.F.length,certificateFactors:r.cert.factors.length,trials:r.cert.trials,candidates:0});
 }
 const sparse=[];
 for(const [name,k,hs] of [["Fano",7,[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]]],["affine-plane-9",9,[...subsets(9,3)].filter(h=>h.reduce((s,i)=>s+Math.floor(i/3),0)%3===0&&h.reduce((s,i)=>s+i%3,0)%3===0)]]){
  const d={k,m:2,F:hs.map(h=>factor(h,126))},r3=P.resolution(d,3),r=check(d);
  ok(r3.kind==="unknown"&&P.cardinality(d).kind==="unknown"&&r.cert.kind==="resolution"&&V.verify(d,r.cert),"sparse resolution");
  sparse.push({name,k,factors:hs.length,width3Clauses:r3.clauses,width4Nodes:r.cert.nodes.length,pairs:r.cert.pairs});
 }
 function bad(d,c){let rejected=false;try{V.verify(d,c);}catch{rejected=true;}ok(rejected,"tamper accepted");stats.tamperRejected++;}
 const card=P.cardinality(d5);bad(d5,{...card,v:[0,1,2,3,3]});bad(d5,{...card,factors:card.factors.slice(1)});bad(d5,{...card,factors:card.factors.map(()=>0)});
 bad(d5,{...r4,nodes:r4.nodes.slice(0,-1)});bad(d5,{...r4,nodes:r4.nodes.map((n,i)=>i===0?{...n,f:-1}:n)});bad(d5,{...r4,nodes:r4.nodes.map((n,i)=>i===r4.nodes.length-1?{...n,p:0}:n)});
 return {stats,rows,sparse,width3:{clauses:r3.clauses,pairs:r3.pairs},width4:{nodes:r4.nodes.length,pairs:r4.pairs}};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require('./f038_rex_variable_resolution_closure.js'),require('./f038_rex_variable_resolution_certificate.js'))));
