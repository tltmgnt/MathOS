// SEP-003 raw normalized selector host solver; not compiled U transitions.
function engine(useSmallBatches=false){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* perm(a){if(!a.length){yield [];return;}for(let i=0;i<a.length;i++)for(let p of perm(a.filter((_,j)=>i!==j)))yield [a[i],...p];}
 let A=[0,1,2,3],V=[4,5,6,7,8];
 const n={fixtures:0,plans:0,eliminations:0,bagRows:0,conditionings:0,messageChecks:0,keyChecks:0,fullTuples:0,models:0,reconstruction:0,componentWitnesses:0,streamBatches:0,streamJoinChecks:0,splitGroups:0,streamOutputs:0,peakBagBatch:0};
 let seed=0x53455001;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 function make(m,h,bad){return {h,S:new Set([...tup(m,h.length)].filter(z=>!bad(z)).map(key))};}
 const pass=(f,z)=>f.S.has(key(f.h.map(g=>z[g])));
 function components(F){
  let G=V.map(v=>new Set([v]));
  for(let f of F)for(let a of f.h.filter(v=>V.includes(v)))for(let b of f.h.filter(v=>V.includes(v)))G[V.indexOf(a)].add(b);
  let seen=new Set(),out=[];
  for(let a of V)if(!seen.has(a)){
   let C=[a];seen.add(a);for(let i=0;i<C.length;i++)for(let v of G[V.indexOf(C[i])])if(!seen.has(v)){C.push(v);seen.add(v);}
   C.sort((a,b)=>a-b);let factors=F.filter(f=>f.h.some(v=>C.includes(v))),B=A.filter(v=>factors.some(f=>f.h.includes(v)));
   out.push({C,B,factors});
  }return out;
 }
 function plan(C,B,F){
  if(B.length>3)return null;
  let best=null;
  for(let mask=0;mask<1<<C.length;mask++){
   let S=C.filter((_,i)=>mask>>i&1);if(S.length>2)continue;
   for(let order of perm(C.filter(v=>!S.includes(v)))){
    let scopes=F.map(f=>f.h.filter(v=>!S.includes(v))),w=0;
    for(let v of order){
     let U=[...new Set(scopes.filter(h=>h.includes(v)).flat())].filter(u=>u!==v).sort((a,b)=>a-b);
     w=Math.max(w,U.length);scopes=scopes.filter(h=>!h.includes(v));scopes.push(U);
    }
    n.plans++;if(w>3||S.length+Math.max(3,w+1)>5)continue;
    let p={S,order,w,cost:S.length+Math.max(3,w+1)};if(!best||p.cost<best.cost||p.cost===best.cost&&S.length<best.S.length)best=p;
   }
  }return best;
 }
 function condition(m,F,S,values){
  return F.map(f=>{let h=f.h.filter(v=>!S.includes(v)),T=new Set();
   for(let q of tup(m,h.length)){let z=[];S.forEach((v,i)=>z[v]=values[i]);h.forEach((v,i)=>z[v]=q[i]);if(pass(f,z))T.add(key(q));}
   return {h,S:T};});
 }
 function eliminate(m,F,order){
  let hist=[];
  for(let v of order){
   let touched=F.filter(f=>f.h.includes(v)),h=[...new Set(touched.flatMap(f=>f.h))].filter(g=>g!==v).sort((a,b)=>a-b);
   ok(h.length<=3,"width");// Stream candidate bags in deliberately small chunks.
   // Sequential merge membership on projected factor keys; OR across chunk boundaries.
   let batch=[],cap=useSmallBatches?Math.max(1,m*m-1):m**3,last=null,hit=false,stream=new Set();
   const cmp=(a,b)=>a<b?-1:a>b?1:0;
   function flush(){
    if(!batch.length)return;
    n.streamBatches++;n.peakBagBatch=Math.max(n.peakBagBatch,batch.length);
    if(last!==null&&last===key(batch[0].q))n.splitGroups++;
    for(let f of touched){
     let list=[...f.S].sort(cmp);
     let projected=batch.map((r,i)=>({...r,i,k:key(f.h.map(g=>g===v?r.a:r.q[h.indexOf(g)]))})).sort((a,b)=>cmp(a.k,b.k));
     let j=0;for(let r of projected){while(j<list.length&&list[j]<r.k)j++;r.ok &&= j<list.length&&list[j]===r.k;n.streamJoinChecks++;}
     batch=projected.sort((a,b)=>a.i-b.i);
    }
    for(let r of batch){let k=key(r.q);if(last!==null&&last!==k){if(hit)stream.add(last);hit=false;}last=k;hit ||= r.ok;}
    batch=[];
   }
   for(let q of tup(m,h.length))for(let a=0;a<m;a++){batch.push({q,a,ok:true});if(batch.length===cap)flush();}
   flush();if(last!==null&&hit)stream.add(last);
   n.streamOutputs+=stream.size;
   hist.push({v,touched});F=F.filter(f=>!f.h.includes(v));F.push({h,S:stream});n.eliminations++;
  }return {F,hist};
 }
 function message(m,comp){
  let {C,B,factors}=comp,p=plan(C,B,factors);if(!p)return null;
  let out=new Set();
  for(let values of tup(m,p.S.length)){
   n.conditionings++;let {F}=eliminate(m,condition(m,factors,p.S,values),p.order);
   for(let q of tup(m,B.length)){let z=[];B.forEach((v,i)=>z[v]=q[i]);if(F.every(f=>pass(f,z)))out.add(key(q));}
  }
  return {h:B,S:out,p};
 }
 function reconstruct(m,comp,msg,z){
  let {p}=msg;
  for(let values of tup(m,p.S.length)){
   let {F,hist}=eliminate(m,condition(m,comp.factors,p.S,values),p.order);
   if(!F.every(f=>pass(f,z)))continue;
   p.S.forEach((v,i)=>z[v]=values[i]);
   for(let {v,touched} of hist.reverse()){
    let found=false;for(let a=0;a<m;a++){z[v]=a;if(touched.every(f=>pass(f,z))){found=true;break;}}
    ok(found,"backtrack");
   }
   ok(comp.factors.every(f=>pass(f,z)),"component witness");n.componentWitnesses++;return true;
  }return false;
 }

 const extra={partitions:0,slices:0,staticMessages:0,dynamicMessages:0,keyChecks:0,exactKeys:0,fullTuples:0,models:0,componentChecks:0,selectedWitnesses:0,reducedChecks:0};
 function* subsets(a,k){if(k===0){yield [];return;}for(let i=0;i<=a.length-k;i++)for(let b of subsets(a.slice(i+1),k-1))yield [a[i],...b];}
 function setup(a){A=a;V=Array.from({length:9},(_,i)=>i).filter(i=>!a.includes(i));}
 function slicedPlan(C){
  const stat=C.map(c=>plan(c.C,c.B,c.factors));
  for(let q=0;q<=2;q++)for(let Q of subsets(A,q)){
   let local=C.map((c,i)=>{
    if(stat[i])return {static:true,p:stat[i]};
    let B=c.B.filter(g=>!Q.includes(g)),F=c.factors.map(f=>({h:f.h.filter(g=>!Q.includes(g))}));
    let p=plan(c.C,B,F);
    return p&&q+p.cost<=5?{static:false,p}:null;
   });
   if(local.every(Boolean))return {Q,local};
  }return null;
 }
 function reduced(C){
  let stat=C.map(c=>plan(c.C,c.B,c.factors));
  if(stat.every(Boolean))return true;
  for(let a of A){
   let good=true;
   for(let i=0;i<C.length;i++)if(!stat[i]){
    let c=C[i],B=c.B.filter(g=>g!==a);
    if(B.length>3){good=false;break;}
    let found=false;
    for(let order of perm(c.C)){
     let scopes=c.factors.map(f=>f.h.filter(g=>g!==a)),w=0;
     for(let v of order){let U=[...new Set(scopes.filter(h=>h.includes(v)).flat())].filter(g=>g!==v);w=Math.max(w,U.length);scopes=scopes.filter(h=>!h.includes(v));scopes.push(U);}
     if(w<=3){found=true;break;}
    }
    if(!found){good=false;break;}
   }
   if(good)return true;
  }return false;
 }

 function* pool(n){
  for(let a=1;a<=n;a++)for(let x of [-1,1])yield [a*x];
  for(let a=1;a<=n;a++)for(let b=a+1;b<=n;b++)for(let x of [-1,1])for(let y of [-1,1])yield [a*x,b*y];
  for(let a=1;a<=n;a++)for(let b=a+1;b<=n;b++)for(let c=b+1;c<=n;c++)for(let x of [-1,1])for(let y of [-1,1])for(let z of [-1,1])yield [a*x,b*y,c*z];
 }
 function length(n){return n+1+2*n*n+8*n*(n-1)*(n-2)/6;}
 const norm=c=>c.slice().sort((a,b)=>Math.abs(a)-Math.abs(b));
 function fixed(m,pins){
  let n=19*m-7,F=[];
  for(let g=0;g<9;g++){
   let X=Array.from({length:m},(_,j)=>g*m+j+1),Y=Array.from({length:m-1},(_,j)=>9*m+g*(m-1)+j+1);
   for(let [a,b] of subsets(X,2))F.push([-a,-b]);
   for(let j=0;j<Y.length;j++){let a=j?Y[j-1]:X[0],b=X[j+1],y=Y[j];F.push([-a,y],[-b,y],[a,b,-y]);}F.push([Y[Y.length-1]]);
  }
  F.push([1-n],[-n]);
  if(pins)for(let i=0;i<m;i++){let p=n-m-1+i;for(let a of [1-n,n-1])for(let z of [-n,n])F.push([pins[i]?p:-p,a,z]);}
  return F.map(norm);
 }
 function encode(m,pins,B){
  let n=19*m-7,S=new Set(fixed(m,pins).concat(B).map(c=>key(norm(c)))),out=["1".repeat(n),"0"];
  for(let c of pool(n))out.push(S.has(key(c))?"1":"0");return out.join("");
 }
 function decode(raw){
  let n=0;while(n<raw.length&&raw[n]==="1")n++;
  let m=(n+7)/19;
  if(!Number.isInteger(m)||m<2||raw[n]!=="0"||raw.length!==length(n))return null;
  // Exact validation of required fixed non-pin clauses and each four-lift pin group.
  let required=new Set(fixed(m,null).map(key)),pins=Array.from({length:m},()=>[0,0]),B=new Map(),j=n+1,selected=0;
  for(let c of pool(n)){
   let b=raw[j++];if(b==="0")continue;if(b!=="1")return null;selected++;
   let k=key(c);if(required.delete(k))continue;
   if(c.length===3&&Math.abs(c[0])>=n-m-1&&Math.abs(c[0])<=n-2&&Math.abs(c[1])===n-1&&Math.abs(c[2])===n){
    pins[Math.abs(c[0])-(n-m-1)][+(c[0]>0)]++;continue;
   }
   if(c.every(x=>x<0&&-x<=9*m)){
    let g=c.map(x=>Math.floor((-x-1)/m)),d=c.map(x=>(-x-1)%m);
    if(new Set(g).size===g.length){let h=key(g);if(!B.has(h))B.set(h,{h:g,bad:new Set()});B.get(h).bad.add(key(d));continue;}
   }
   return null;
  }
  if(required.size||pins.some(([a,b])=>!(a===4&&b===0||a===0&&b===4)))return null;
  let F=[...B.values()].map(f=>({h:f.h,S:new Set([...tup(m,f.h.length)].map(key).filter(k=>!f.bad.has(k)))}));
  return {n,m,pins:pins.map(v=>+(v[1]===4)),F,selected};
 }
 function witness(m,pins,z){
  let n=19*m-7,b=Array(n).fill(0);
  for(let g=0;g<9;g++){b[g*m+z[g]]=1;for(let j=0;j<m-1;j++)b[9*m+g*(m-1)+j]=+(z[g]<=j+1);}
  for(let i=0;i<m;i++)b[n-m-2+i]=pins[i];
  return b.join("");
 }
 function valid(raw,bits){
  let n=bits.length,j=n+1;if(!/^[01]+$/.test(bits)||raw.slice(0,j)!=="1".repeat(n)+"0")return false;
  for(let c of pool(n)){if(raw[j++]==="1"&&!c.some(x=>(bits[Math.abs(x)-1]==="1")===(x>0)))return false;}
  return j===raw.length;
 }
 function solveRaw(raw){
  let D=decode(raw);if(!D)return {status:"OUTSIDE_NORMALIZED"};
  let {m,F}=D,P=null,C=null;
  for(let a of subsets(Array.from({length:9},(_,i)=>i),4)){setup(a);C=components(F);P=slicedPlan(C);if(P)break;}
  if(!P)return {status:"INELIGIBLE"};
  let stat=C.map((c,i)=>P.local[i].static?message(m,c):null),K=F.filter(f=>f.h.every(g=>A.includes(g))),B=A.filter(g=>!P.Q.includes(g));
  function comps(v){return C.map((c,i)=>stat[i]?c:{C:c.C,B:c.B.filter(g=>!P.Q.includes(g)),factors:condition(m,c.factors,P.Q,v)});}
  let count=0,first=null,slices=0,peakBatch=0,keyJoins=0;
  for(let v of tup(m,P.Q.length)){
   slices++;let cs=comps(v),M=cs.map((c,i)=>stat[i]||message(m,c)),batch=[],cap=m**3;
   function flush(){
    if(!batch.length)return;
    peakBatch=Math.max(peakBatch,batch.length);
    for(let f of K.concat(M)){
     let list=[...f.S].sort(),r=batch.map((x,i)=>({...x,i,k:key(f.h.map(g=>x.z[g]))})).sort((a,b)=>a.k<b.k?-1:a.k>b.k?1:0);
     let j=0;for(let x of r){while(j<list.length&&list[j]<x.k)j++;x.ok &&= j<list.length&&list[j]===x.k;keyJoins++;}
     batch=r.sort((a,b)=>a.i-b.i);
    }
    for(let x of batch)if(x.ok){count++;if(!first)first={v:v.slice(),z:x.z.slice()};}batch=[];
   }
   for(let b of tup(m,B.length)){let z=[];P.Q.forEach((g,i)=>z[g]=v[i]);B.forEach((g,i)=>z[g]=b[i]);batch.push({z,ok:true});if(batch.length===cap)flush();}flush();
  }
  if(!first)return {status:"UNSAT",count,slices,peakBatch,keyJoins,A:A.slice(),Q:P.Q};
  let z=first.z,cs=comps(first.v);
  for(let i=0;i<cs.length;i++)ok(reconstruct(m,cs[i],stat[i]||message(m,cs[i]),z),"reconstruct raw");
  let bits=witness(m,D.pins,z);ok(valid(raw,bits),"raw clause witness");
  return {status:"SAT",count,slices,peakBatch,keyJoins,A:A.slice(),Q:P.Q,z,bits};
 }
 return {pool,length,fixed,encode,decode,witness,valid,solveRaw,tup,subsets,n};
}
function audit(includeFixtures=false){
 const E=engine(true),P=engine(),ok=(v,s)=>{if(!v)throw Error(s)},fixtures=[],rows=[];
 let counts={rawBits:0,selectedClauses:0,referenceTuples:0,feasibleKeys:0,validWitnesses:0,unsat:0,ineligible:0,malformed:0,keyJoins:0,peakBatch:0};
 let seed=0x4e4f524d;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 for(let m of [2,3,4])for(let mode=0;mode<4;mode++){
  let B=[],scopes=[];
  if(mode===3){for(let h of E.subsets([...Array(9).keys()],2))scopes.push(h);}else{for(let a=0;a<4;a++)for(let b=4;b<9;b++)scopes.push([a,b]);scopes.push([0,1,2]);}
  for(let h of scopes)for(let d of E.tup(m,h.length))if(mode===3?d.every(x=>x===0):d.every(x=>x===m-1)||d.some(x=>x!==0)&&(rand()>>>24)<28)B.push(h.map((g,i)=>-(g*m+d[i]+1)));
  if(mode===1)for(let a=0;a<m;a++)B.push([-(4*m+a+1)]);
  if(mode===2)for(let a=0;a<m-1;a++)B.push([-(a+1)]);
  let pins=Array.from({length:m},(_,i)=>(i+mode)%2),raw=E.encode(m,pins,B),D=E.decode(raw);ok(D&&D.pins.join()===pins.join(),"pin decode");
  let r=E.solveRaw(raw);ok(JSON.stringify(r)===JSON.stringify(P.solveRaw(raw)),"production cap equivalence");counts.rawBits+=raw.length;counts.selectedClauses+=D.selected;
  if(mode===3){ok(r.status==="INELIGIBLE"&&E.valid(raw,E.witness(m,pins,Array(9).fill(1))),"ineligible SAT");counts.ineligible++;}
  else{
   let keys=new Set();
   for(let z of E.tup(m,9)){counts.referenceTuples++;if(B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m)))keys.add(r.A.map(g=>z[g]).join(","));}
   ok(r.count===keys.size&&r.status===(keys.size?"SAT":"UNSAT"),"raw exact keys");counts.feasibleKeys+=keys.size;counts.keyJoins+=r.keyJoins;counts.peakBatch=Math.max(counts.peakBatch,r.peakBatch);
   if(r.status==="SAT"){ok(E.valid(raw,r.bits)&&r.z.every((v,i)=>r.bits[i*m+v]==="1"),"raw witness");counts.validWitnesses++;}else counts.unsat++;
  }
  rows.push([m,mode,raw.length,D.selected,r.status,r.count??null,r.Q??null,r.z??null]);
  if(includeFixtures&&m===2)fixtures.push({raw,bits:r.bits??null,status:r.status});
 }
 // Exercise static-only, mixed static/dynamic, and empty selected cross support.
 let integration=[];
 for(let m of [2,3])for(let mode=0;mode<3;mode++){
  let B=[],H=mode===0?[]:mode===1?[[0,4],[1,4],[2,4],[3,4],[0,5],[5,6],[6,7],[7,8],[5,8]]:[[0,4],[1,5],[2,6],[4,5,6],[5,6,7],[6,7,8]];
  for(let h of H)B.push(h.map(g=>-(g*m+m)));
  let pins=Array.from({length:m},(_,i)=>+(i%2===0)),raw=E.encode(m,pins,B),r=E.solveRaw(raw),K=new Set();
  ok(JSON.stringify(r)===JSON.stringify(P.solveRaw(raw)),"production cap equivalence supplemental");ok(r.status==="SAT","integration SAT");
  for(let z of E.tup(m,9)){counts.referenceTuples++;if(B.every(c=>!c.every(x=>z[Math.floor((-x-1)/m)]===(-x-1)%m)))K.add(r.A.map(g=>z[g]).join(","));}
  ok(r.count===K.size&&E.valid(raw,r.bits),"integration exact keys");
  ok(mode===1?r.Q.length===1:r.Q.length===0,"static or mixed route");
  counts.rawBits+=raw.length;counts.selectedClauses+=E.decode(raw).selected;counts.feasibleKeys+=r.count;counts.validWitnesses++;counts.keyJoins+=r.keyJoins;counts.peakBatch=Math.max(counts.peakBatch,r.peakBatch);
  integration.push([m,mode,r.count,r.A,r.Q,r.z]);
  if(includeFixtures&&m===2)fixtures.push({raw,bits:r.bits,status:r.status});
 }
 let raw=E.encode(2,[0,1],[]),n=31;let selected=[],unselected=[];
 for(let i=n+1;i<raw.length;i++)(raw[i]==="1"?selected:unselected).push(i);
 for(let i of selected){let bad=raw.slice(0,i)+"0"+raw.slice(i+1);ok(E.decode(bad)===null,"missing fixed record");counts.malformed++;}
 let pos=n+1,added=0,opposite=[];
 for(let c of E.pool(n)){
  if(c.length===1&&c[0]>=1&&c[0]<=12){
   ok(raw[pos]==="0"&&E.solveRaw(raw.slice(0,pos)+"1"+raw.slice(pos+1)).status==="OUTSIDE_NORMALIZED","unsupported positive unit");added++;counts.malformed++;
  }
  if(c.length===3&&c[0]===n-3&&Math.abs(c[1])===n-1&&Math.abs(c[2])===n)opposite.push(pos);
  pos++;
 }
 ok(added===12&&opposite.length===4,"adversarial positions");
 for(let i of opposite){ok(raw[i]==="0"&&E.decode(raw.slice(0,i)+"1"+raw.slice(i+1))===null,"mixed pin sign");counts.malformed++;}
 let both=raw.split("");for(let i of opposite)both[i]="1";ok(E.decode(both.join(""))===null,"both full pin signs");counts.malformed++;
 // A complete valid input with a different variable count is outside the family, not UNSAT.
 ok(E.solveRaw("100").status==="OUTSIDE_NORMALIZED","outside normalized dimension");counts.malformed++;

 for(let bad of [raw.slice(1),raw+"0",raw.slice(0,-1),raw.slice(0,-1)+"2","", "10"]){ok(E.solveRaw(bad).status==="OUTSIDE_NORMALIZED","malformed status");counts.malformed++;}
 return includeFixtures?fixtures:{counts,rows,integration,machineHostCounters:E.n,productionHostCounters:P.n};
}

if(process.argv.includes('--solve')) console.log(JSON.stringify(engine().solveRaw(require('fs').readFileSync(0,'utf8'))));
else console.log(process.argv.includes('--fixtures')?JSON.stringify(audit(true)):'F038_TGA_NORMALIZED_INTEGRATION_OK '+JSON.stringify(audit()));
