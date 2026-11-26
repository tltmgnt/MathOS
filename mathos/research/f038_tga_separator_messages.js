// TGA-SEP-001 host semantic audit, not a compiled physical solver.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* perm(a){if(!a.length){yield [];return;}for(let i=0;i<a.length;i++)for(let p of perm(a.filter((_,j)=>i!==j)))yield [a[i],...p];}
 const A=[0,1,2,3],V=[4,5,6,7,8];
 const n={fixtures:0,plans:0,eliminations:0,bagRows:0,conditionings:0,messageChecks:0,keyChecks:0,fullTuples:0,models:0,reconstruction:0,componentWitnesses:0};
 let seed=0x53455001;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 function make(m,h,bad){return {h,S:new Set([...tup(m,h.length)].filter(z=>!bad(z)).map(key))};}
 const pass=(f,z)=>f.S.has(key(f.h.map(g=>z[g])));
 function components(F){
  let G=V.map(v=>new Set([v]));
  for(let f of F)for(let a of f.h.filter(v=>v>=4))for(let b of f.h.filter(v=>v>=4))G[a-4].add(b);
  let seen=new Set(),out=[];
  for(let a of V)if(!seen.has(a)){
   let C=[a];seen.add(a);for(let i=0;i<C.length;i++)for(let v of G[C[i]-4])if(!seen.has(v)){C.push(v);seen.add(v);}
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
   hist.push({v,touched});F=F.filter(f=>!f.h.includes(v));F.push({h,S:T});n.eliminations++;
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
 let cases=[];
 for(let m of [2,3])for(let mode=0;mode<5;mode++){
  n.fixtures++;
  let scopes=mode===0?[[0,4,5],[1,5],[4,5,6],[2,7,8],[3,8],[0,2,3]]:
    mode===1?[[0,4,5],[1,5,6],[2,6,7],[4,7,8],[5,8],[0,1,3]]:
    mode===2?[[0,4],[1,5],[2,6],[4,5,6],[4,6,7],[5,7,8],[6,8],[1,2,3]]:
    mode===3?[[0,4],[0,5],[0,6],[0,7],[0,8],...V.flatMap((v,i)=>V.slice(i+1).map(u=>[v,u]))]:
    [[0,4],[1,5],[2,6],[4,5],[5,6],[6,4],[3],[0,2]];
  let F=scopes.map(h=>make(m,h,()=> (rand()>>>24)<30+mode*9)),C=components(F),M=C.map(c=>message(m,c));
  if(M.some(x=>!x)){cases.push([m,mode,"ineligible"]);continue;}
  for(let j=0;j<C.length;j++)for(let q of tup(m,C[j].B.length)){
   let comp=C[j],z=[];comp.B.forEach((v,i)=>z[v]=q[i]);let truth=false;
   for(let u of tup(m,comp.C.length)){comp.C.forEach((v,i)=>z[v]=u[i]);truth ||= comp.factors.every(f=>pass(f,z));}
   ok(M[j].S.has(key(q))===truth,"exact message");n.messageChecks++;
  }
  let K=F.filter(f=>f.h.every(v=>v<4)).concat(M),truthKeys=new Set(),found=0;
  for(let z of tup(m,9)){n.fullTuples++;if(F.every(f=>pass(f,z))){truthKeys.add(key(z.slice(0,4)));n.models++;}}
  for(let q of tup(m,4)){
   n.keyChecks++;let yes=K.every(f=>pass(f,q));ok(yes===truthKeys.has(key(q)),"exact key projection");
   if(yes){found++;let z=q.slice();for(let j=0;j<C.length;j++)ok(reconstruct(m,C[j],M[j],z),"reconstruct");ok(F.every(f=>pass(f,z)),"original model");n.reconstruction++;}
  }
  cases.push([m,mode,C.map((c,j)=>[c.C.length,c.B.length,M[j].p.S.length,M[j].p.w]),found]);
 }
 // Conditioned K5 from CPR: four-colour abstraction is unnecessary;
 // exact separator messages on actual digits recover two good sources.
 let clique=[];
 for(let m of [4,8]){
  let F=[];for(let i=4;i<=8;i++)for(let j=i+1;j<=8;j++)F.push(i===4&&j===8?make(m,[0,i,j],([a,x,y])=>a>=2&&x%4===y%4):make(m,[i,j],([x,y])=>x%4===y%4));
  let C=components(F),M=message(m,C[0]);ok(M&&M.h.join()==="0"&&M.S.size===2&&M.S.has("0")&&M.S.has("1"),"clique message");
  for(let a of [0,1]){let z=[a,0,0,0];ok(reconstruct(m,C[0],M,z)&&F.every(f=>pass(f,z)),"clique witness");}
  clique.push([m,M.p.S,M.p.w,M.S.size,m**4,2*m**3]);
 }
 // Four-key boundary obstruction: hidden digit encodes three q-ary digits.
 // Fourth visible residue is their negative sum. Every proper projection full.
 let boundary=[];
 for(let q of [2,3,4,5]){
  let m=q**3,hidden=[...tup(q,3)].map(([a,b,c])=>[a,b,c,(3*q-a-b-c)%q]),F=new Set(hidden.map(key)),proj=[];
  for(let drop=0;drop<4;drop++){
   let P=new Set(hidden.map(z=>key(z.filter((_,i)=>i!==drop))));ok(P.size===q**3,"full triple projection");proj.push(P);
  }
  let R=0,actual=0;for(let z of tup(q,4)){R+=+proj.every((P,i)=>P.has(key(z.filter((_,j)=>j!==i))));actual+=+F.has(key(z));}
  ok(R===q**4&&actual===q**3,"arity obstruction");
  let fake=Array.from({length:4},(_,i)=>({h:[i,4],S:new Set()}));let C=components(fake);ok(plan(C[0].C,C[0].B,C[0].factors)===null,"boundary gate");
  // Real visible digits have q^2 copies of each residue. Exact lifted count.
  boundary.push([q,m,actual,R,actual*(q*q)**4,m**4]);
 }
 return {n,cases,clique,boundary};
}
console.log('F038_TGA_SEPARATOR_MESSAGES_OK '+JSON.stringify(audit()));
