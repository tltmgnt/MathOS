// Standalone hybrid GF(2)/dictionary reference; no physical tape measurements.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],V=[6,7,8],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(i=>z[i]),xor=(x,y)=>x.map((v,i)=>v^y[i]);
 let rankChecks=0,encodingChecks=0,rebases=0;
 function factor(rows,n){
  let B=[];
  for(let row of rows){let w=row.slice();for(let v of B)if(w[v.p])w=xor(w,v.row);let p=w.indexOf(1);if(p>=0){B.push({p,row:w});B.sort((a,b)=>a.p-b.p);}}
  let basis=B.map(v=>v.row),coeff=rows.map(row=>{let w=row.slice(),c=[];for(let v of B){let bit=w[v.p];c.push(bit);if(bit)w=xor(w,v.row);}ok(w.every(v=>!v),"span");return c;});
  for(let i=0;i<rows.length;i++){ok(key(decode(basis,coeff[i],n))===key(rows[i]),"exact encoding");encodingChecks++;}
  ok(B.every((v,i)=>v.row.indexOf(1)===v.p&&(!i||B[i-1].p<v.p)),"echelon");rankChecks++;
  return {basis,coeff};
 }
 function decode(B,c,n){let w=Array(n).fill(0);for(let i=0;i<B.length;i++)if(c[i])w=xor(w,B[i]);return w;}
 const dot=(B,c,j)=>B.reduce((v,row,i)=>v^(row[j]&c[i]),0);
 let fixtures=0,stats=Array(11).fill(0),kinds=[0,0,0,0],dictChecks=0,relabels=0;
 function intern(rows){let M=new Map(),R=[],ids=[];for(let row of rows){let k=key(row);if(!M.has(k)){M.set(k,R.length);R.push(row);}ids.push(M.get(k));}for(let i=0;i<rows.length;i++){ok(key(R[ids[i]])===key(rows[i]),"dictionary exact");dictChecks++;}return {R,ids};}
 const evalRow=(D,a,j)=>a.kind===0?dot(D.B,a.c,j):D.R[a.id][j];
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let M=1;while(M<m)M*=2;let b=2;
  let F=H.map(h=>({h,B:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){
    if(mode===0)return false;
    if(mode===1||mode===2)return z[0]===z[2]&&z[1]!==z[2];
    if(mode===3)return z[0]===1&&z[1]===0;
    return (z[0]+z[1])%m===z[2];
   }
   if(key(h)==="6,7,8")return mode===2?(z[0]^z[1]^z[2])&1:mode===3?true:mode===4?(z[0]+z[1])%m===z[2]:mode===5?(z[0]+2*z[1]+z[2])%3===0:false;
   if(mode===5)return h.length===3&&(h.reduce((s,x)=>s+x,0)+z.reduce((s,x,i)=>s+(i+2)*x,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   if(mode===7)return h.length===2&&z[0]===z[1];return false;
  }).map(key))}));
  let W=F.find(s=>key(s.h)==="0,4,5"),privateF=F.filter(s=>s.h.every(g=>V.includes(g))),res=F.filter(s=>!s.h.every(g=>V.includes(g)));
  const raw=(a,x,y)=>+W.B.has(key([a,x,y])),p=(a,d,e,t)=>(d+e+t+1)%m;
  const E=z=>z.every(a=>a<m)&&!raw(z[0],z[4],z[5])&&!!raw(p(...z.slice(0,4)),z[4],z[5]);
  const pv=z=>z.every(a=>a<m)&&privateF.every(s=>!s.B.has(key(s.h.map(g=>z[g-6]))));
  const orig=z=>z.every(a=>a<m)&&F.every(s=>!s.B.has(key(proj(z,s.h))));
  let records=res.flatMap(s=>[...s.B].map(v=>({h:s.h,z:v.split(",").map(Number)})));
  for(let g of G.slice(0,6))for(let a=m;a<M;a++)records.push({h:[g],z:[a]});
  let expected=new Set(),got=new Set();
  for(let z of tup(m,9)){stats[0]++;if(E(z.slice(0,6))&&orig(z))expected.add(key(z));}
  function tree(t,o){let flag=[...tup(t,3)].some(z=>pv(z.map((a,i)=>a+o[i])));stats[1]++;let ch=[];if(flag&&t>1)for(let d of tup(2,3))ch.push(tree(t/2,o.map((a,i)=>a+d[i]*t/2)));return {flag,ch,active:false};}
  function local(o,t){
   let rows=Array.from({length:m},(_,a)=>[...tup(t,2)].map(z=>raw(a,z[0]+o[4],z[1]+o[5])));
   let {basis,coeff}=factor(rows.filter((_,a)=>a%2===0),t*t),{R,ids}=intern(rows.filter((_,a)=>a%2===1));
   const label=a=>a%2===0?{kind:0,c:coeff[a/2]}:{kind:1,id:ids[(a-1)/2]};
   let A=[];for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.every(a=>a<m))A.push({z,l:label(x[0]),r:label(p(...x))});}
   return {B:basis,R,A};
  }
  function child(D,d,t){
   let u=t/2,o=d.map(a=>a*u);
   const restrict=row=>[...tup(u,2)].map(z=>row[(z[0]+o[4])*t+z[1]+o[5]]);
   let {basis,coeff}=factor(D.B.map(restrict),u*u),{R,ids}=intern(D.R.map(restrict));
   const change=a=>{if(a.kind===0){rebases++;return {kind:0,c:decode(coeff,a.c,basis.length)};}relabels++;return {kind:1,id:ids[a.id]};};
   let A=D.A.filter(a=>a.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(a=>({z:a.z.map((v,i)=>v-o[i]),l:change(a.l),r:change(a.r)}));
   return {B:basis,R,A};
  }
  function visit(node,D,C,o,t){
   if(!node.flag)return;ok(!node.active,"exclusive frame");node.active=true;stats[2]++;
   ok(D.B.length**8<=4**8*t**3&&D.R.length<=2*t*t&&D.A.length<=t**4&&C.length<=130*t**3,"rank and frame cap");
   let live=false;
   for(let a of D.A)for(let [x,y] of tup(t,2)){
    let z=[...a.z,x,y].map((v,i)=>v+o[i]),v=!evalRow(D,a.l,x*t+y)&&!!evalRow(D,a.r,x*t+y);kinds[2*a.l.kind+a.r.kind]++;
    ok(v===E(z),"local coefficient membership");stats[3]++;live ||=v;
   }
   ok(live===[...tup(t,6)].some(z=>E(z.map((a,i)=>a+o[i]))),"positivity");stats[4]++;
   if(live){
    stats[5]++;
    if(t===1){stats[6]++;let pass=C.length===0;ok(pass===(orig(o)&&E(o.slice(0,6))),"leaf");if(pass){ok(!got.has(key(o)),"disjoint");got.add(key(o));}}
    else for(let d of tup(2,9)){
     let idx=d.slice(6).reduce((s,x)=>2*s+x,0),ch=node.ch[idx];stats[7]++;
     if(!ch.flag)continue;
     let u=t/2,off=d.map(x=>x*u),cc=C.map(r=>({h:r.h,z:r.z.map((x,i)=>x-off[r.h[i]])})).filter(r=>r.z.every(x=>x>=0&&x<u));
     visit(ch,child(D,d,t),cc,o.map((x,i)=>x+off[i]),u);ok(!ch.active&&node.active,"reuse");
    }
   }
   node.active=false;
  }
  for(let q of tup(M/b,6)){
   let po=q.map(a=>a*b),D=local(po,b);
   for(let v of tup(M/b,3)){
    let o=[...po,...v.map(a=>a*b)],root=tree(b,o.slice(6)),C=records.map(r=>({h:r.h,z:r.z.map((x,i)=>x-o[r.h[i]])})).filter(r=>r.z.every(x=>x>=0&&x<b));
    stats[8]++;visit(root,D,C,o,b);
   }
  }
  ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact models");stats[9]+=got.size;stats[10]+=expected.size;fixtures++;
 }
 let controls=[];
 for(let m of [4,8,16,32,64]){
  let d=Math.log2(m),k=Math.min(Math.floor(Math.log2(d-1)),Math.floor((d-1)/3)+1),f=u=>{let n=0;for(let j=0;j<k;j++)n|=((u>>(3*j))&1)<<j;return n;};
  let raw=(a,u,v)=>a%2?+(v===a&&u!==a):((a>>(1+f(u)))&1);
  let checks=0,maxRank=0,maxDict=0;
  for(let t=1;t<=m;t*=2)for(let q of tup(m/t,2)){
   let rows=Array.from({length:m},(_,a)=>[...tup(t,2)].map(z=>raw(a,z[0]+q[0]*t,z[1]+q[1]*t)));
   let X=factor(rows.filter((_,a)=>!(a%2)),t*t),Y=intern(rows.filter((_,a)=>a%2));
   ok(X.basis.length**8<=4**8*t**3&&Y.R.length<=2*t*t,"hybrid certificate");maxRank=Math.max(maxRank,X.basis.length);maxDict=Math.max(maxDict,Y.R.length);checks++;
  }
  let all=factor(Array.from({length:m},(_,a)=>[...tup(m,2)].map(z=>raw(a,...z))),m*m);
  ok(all.basis.length>=m/2,"independent dictionary rows");
  controls.push([m,maxRank,maxDict,all.basis.length,checks]);
 }
 let symbolic=[];
 for(let d of [64,128,256,512,1024]){
  let k=Math.floor(Math.log2(d-1)),q=2**k,logt=3*k;ok(logt<d&&q<=d-1,"feature realization");
  symbolic.push([d,q,logt,q>1+2*logt,d-1>Math.log2(4)+d/3]);
 }
 ok(kinds.every(x=>x>0),"all four tag pairs");
 return {fixtures,stats,rankChecks,encodingChecks,rebases,dictChecks,relabels,kinds,controls,symbolic};
}
console.log('F038_HYBRID_ROW_FACTORS_OK '+JSON.stringify(audit()));
