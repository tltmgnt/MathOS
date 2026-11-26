// SEP-002 host streamed semantic audit, adapted from SEP-001; not physical execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* perm(a){if(!a.length){yield [];return;}for(let i=0;i<a.length;i++)for(let p of perm(a.filter((_,j)=>i!==j)))yield [a[i],...p];}
 let A=[0,1,2,3],V=[4,5,6,7,8];
 const n={fixtures:0,plans:0,eliminations:0,bagRows:0,conditionings:0,messageChecks:0,keyChecks:0,fullTuples:0,models:0,reconstruction:0,componentWitnesses:0,streamBatches:0,streamJoinChecks:0,splitGroups:0,streamOutputs:0};
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
   ok(h.length<=3,"width");let T=new Set();
   for(let q of tup(m,h.length))for(let a=0;a<m;a++){
    let z=[];z[v]=a;h.forEach((g,i)=>z[g]=q[i]);n.bagRows++;if(touched.every(f=>pass(f,z)))T.add(key(q));
   }
   // Independently stream candidate bags in deliberately small chunks.
   // Sequential merge membership on projected factor keys; OR across chunk boundaries.
   let batch=[],cap=Math.max(1,m*m-1),last=null,hit=false,stream=new Set();
   const cmp=(a,b)=>a<b?-1:a>b?1:0;
   function flush(){
    if(!batch.length)return;
    n.streamBatches++;
    if(last!==null&&last===key(batch[0].q))n.splitGroups++;
    for(let f of touched){
     let list=[...f.S].sort(cmp);
     let projected=batch.map((r,i)=>({i,k:key(f.h.map(g=>g===v?r.a:r.q[h.indexOf(g)]))})).sort((a,b)=>cmp(a.k,b.k));
     let j=0;for(let r of projected){while(j<list.length&&list[j]<r.k)j++;batch[r.i].ok &&= j<list.length&&list[j]===r.k;n.streamJoinChecks++;}
    }
    for(let r of batch){let k=key(r.q);if(last!==null&&last!==k){if(hit)stream.add(last);hit=false;}last=k;hit ||= r.ok;}
    batch=[];
   }
   for(let q of tup(m,h.length))for(let a=0;a<m;a++){batch.push({q,a,ok:true});if(batch.length===cap)flush();}
   flush();if(last!==null&&hit)stream.add(last);
   ok(stream.size===T.size&&[...T].every(k=>stream.has(k)),"streamed bag OR");n.streamOutputs+=stream.size;
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

 const extra={partitions:0,slices:0,staticMessages:0,dynamicMessages:0,keyChecks:0,exactKeys:0,fullTuples:0,models:0,componentChecks:0,selectedWitnesses:0};
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
 function structural(F){
  let old=0,now=0,first=null;
  for(let a of subsets(Array.from({length:9},(_,i)=>i),4)){
   setup(a);extra.partitions++;let C=components(F);
   if(C.every(c=>plan(c.C,c.B,c.factors)))old++;
   let p=slicedPlan(C);if(p){now++;if(!first)first=[a,p.Q];}
  }return [old,now,first];
 }
 function solve(m,F,a,reference=true){
  setup(a);let C=components(F),P=slicedPlan(C);ok(P,"admitted");
  let stat=C.map((c,i)=>{if(!P.local[i].static)return null;extra.staticMessages++;return message(m,c);});
  let K=F.filter(f=>f.h.every(g=>A.includes(g))),B=A.filter(g=>!P.Q.includes(g)),found=new Set(),witness=null,first=null;
  function comps(v){return C.map((c,i)=>stat[i]?c:{C:c.C,B:c.B.filter(g=>!P.Q.includes(g)),factors:condition(m,c.factors,P.Q,v)});}
  for(let v of tup(m,P.Q.length)){
   extra.slices++;let cs=comps(v);
   let M=cs.map((c,i)=>{if(stat[i])return stat[i];extra.dynamicMessages++;return message(m,c);});
   ok(M.every(Boolean),"slice messages");
   for(let i=0;i<cs.length;i++)for(let b of tup(m,cs[i].B.length)){
    let z=[];cs[i].B.forEach((g,j)=>z[g]=b[j]);let truth=false;
    for(let u of tup(m,cs[i].C.length)){cs[i].C.forEach((g,j)=>z[g]=u[j]);truth ||= cs[i].factors.every(f=>pass(f,z));}
    ok(M[i].S.has(key(b))===truth,"exact slice message");extra.componentChecks++;
   }
   for(let b of tup(m,B.length)){
    let z=[];P.Q.forEach((g,i)=>z[g]=v[i]);B.forEach((g,i)=>z[g]=b[i]);extra.keyChecks++;
    if(!K.every(f=>pass(f,z))||!M.every(f=>pass(f,z)))continue;
    let k=key(A.map(g=>z[g]));ok(!found.has(k),"disjoint slices");found.add(k);
    if(first===null)first={v:v.slice(),z:z.slice()};
   }
  }
  if(first){
   let z=first.z,cs=comps(first.v);
   for(let i=0;i<cs.length;i++){let M=stat[i]||message(m,cs[i]);ok(reconstruct(m,cs[i],M,z),"regenerated component witness");}
   ok(F.every(f=>pass(f,z)),"full original witness");witness=z;extra.selectedWitnesses++;
  }
  if(reference){
   let expected=new Set();for(let z of tup(m,9)){extra.fullTuples++;if(F.every(f=>pass(f,z))){expected.add(key(A.map(g=>z[g])));extra.models++;}}
   ok(found.size===expected.size&&[...found].every(k=>expected.has(k)),"global exact key set");
  }
  extra.exactKeys+=found.size;
  return {count:found.size,Q:P.Q,static:P.local.filter(v=>v.static).length,dynamic:P.local.filter(v=>!v.static).length,plans:P.local.map(v=>[v.static,v.p.S.length,v.p.w,v.p.cost]),witness,found};
 }
 let scopes=[];for(let a=0;a<4;a++)for(let v=4;v<9;v++)scopes.push([a,v]);
 const graph=structural(scopes.map(h=>({h,S:new Set()})));
 ok(graph[0]===0&&graph[1]>0,"all old partitions fail K4,5");
 const denseScopes=[];for(let a=0;a<9;a++)for(let b=a+1;b<9;b++)denseScopes.push([a,b]);
 const dense=structural(denseScopes.map(h=>({h,S:new Set()})));
 ok(dense[0]===0&&dense[1]===0,"complete graph ineligible");
 let cases=[];
 for(let m of [2,3,4])for(let mode=0;mode<3;mode++){
  let F=scopes.map(h=>make(m,h,([a,b])=>a===m-1&&b===m-1||(a!==0||b!==0)&&(rand()>>>24)<22+mode*8));
  if(mode===2)F.push(make(m,[4],()=>true));
  F.push(make(m,[0,1,2],([a,b,c])=>a===m-1&&b===m-1&&c===m-1));
  let r=solve(m,F,[0,1,2,3]);
  ok(r.Q.length===1&&r.dynamic===5,"sliced star plan");ok(mode===2?r.count===0:r.count>0,"SAT/UNSAT control");
  cases.push([m,mode,r.Q,r.static,r.dynamic,r.count,r.witness]);
 }
 let mixed=[];
 for(let m of [2,3]){
  let F=[...Array.from({length:4},(_,a)=>[a,4]),[0,5],[5,6],[6,7],[7,8],[5,8]].map(h=>make(m,h,([a,b])=>a===m-1&&b===m-1));
  let r=solve(m,F,[0,1,2,3]);ok(r.static===1&&r.dynamic===1&&r.Q[0]===0,"static cache with sliced boundary");
  mixed.push([m,r.count,r.Q,r.plans]);
 }
 let hidden=[];
 for(let q of [2]){
  let m=q**3,rows=[...tup(q,3)].map(([a,b,c])=>[a,b,c,(3*q-a-b-c)%q]);
  let F=Array.from({length:4},(_,a)=>make(m,[a,4],([z,h])=>z%q!==rows[h][a]));
  let r=solve(m,F,[0,1,2,3],false);
  for(let z of tup(m,4))ok(r.found.has(key(z))===(z.reduce((a,b)=>a+b,0)%q===0),"lifted hidden relation");
  ok(r.count===m**4/q&&r.dynamic===1,"width four boundary recovered");
  hidden.push([q,m,r.count,m**4,r.Q,r.plans]);
 }
 let sat=denseScopes.map(h=>make(2,h,([a,b])=>a===0&&b===0));
 setup([0,1,2,3]);ok(!slicedPlan(components(sat))&&sat.every(f=>pass(f,Array(9).fill(1))),"ineligible SAT");
 return {n,extra,graph,dense,cases,mixed,hidden};
}

console.log('F038_TGA_SLICED_SEPARATORS_OK '+JSON.stringify(audit()));
