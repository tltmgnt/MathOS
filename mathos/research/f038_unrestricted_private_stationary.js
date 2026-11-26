// Host semantic reference; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],P=[0,1,2,3,4,5],V=[6,7,8],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(A,k,i=0,p=[]){if(p.length===k){yield p;return;}for(let j=i;j<=A.length-k+p.length;j++)yield* sub(A,k,j+1,p.concat(A[j]));}
 const H=[...sub(G,1),...sub(G,2),...sub(G,3)],proj=(z,h)=>h.map(i=>z[i]);
 const intern=rows=>{let D=new Map(),R=[],ids=[];for(let row of rows){let k=key(row);if(!D.has(k)){D.set(k,R.length);R.push(row);}ids.push(D.get(k));}return {R,ids};};
 let stats=Array(14).fill(0),fixtures=0,failedCert=0;
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
   if(mode===7)return h.length===2&&z[0]===z[1];
   return false;
  }).map(key))}));
  let W=F.find(s=>key(s.h)==="0,4,5"),privateF=F.filter(s=>s.h.every(g=>V.includes(g))),res=F.filter(s=>!s.h.every(g=>V.includes(g)));
  const raw=(a,x,y)=>+W.B.has(key([a,x,y])),p=(a,d,e,t)=>(d+e+t+1)%m;
  const E=z=>z.every(a=>a<m)&&!raw(z[0],z[4],z[5])&&!!raw(p(...z.slice(0,4)),z[4],z[5]);
  const pv=z=>z.every(a=>a<m)&&privateF.every(s=>!s.B.has(key(s.h.map(g=>z[g-6]))));
  const orig=z=>z.every(a=>a<m)&&F.every(s=>!s.B.has(key(proj(z,s.h))));
  let records=res.flatMap(s=>[...s.B].map(v=>({h:s.h,z:v.split(",").map(Number)})));
  for(let g of P)for(let a=m;a<M;a++)records.push({h:[g],z:[a]});
  for(let t=1;t<=M;t*=2)for(let q of tup(M/t,2)){
   let rows=Array.from({length:m},(_,a)=>[...tup(t,2)].map(z=>raw(a,z[0]+q[0]*t,z[1]+q[1]*t)));
   let n=intern(rows).R.length;stats[0]++;if(n>2*t*t)failedCert++;
  }
  let expected=new Set(),got=new Set();
  for(let z of tup(m,9)){stats[1]++;if(E(z.slice(0,6))&&orig(z))expected.add(key(z));}
  function tree(t,o){
   let flag=[...tup(t,3)].some(z=>pv(z.map((a,i)=>a+o[i])));stats[2]++;
   let cap=20*t**4,ch=[];
   if(flag&&t>1)for(let d of tup(2,3))ch.push(tree(t/2,o.map((a,i)=>a+d[i]*t/2)));
   let extent=1+(flag?cap:0)+ch.reduce((s,c)=>s+c.extent,0);
   ok(extent<=100*t**4,"private tree extent");return {flag,cap,ch,extent,active:false};
  }
  function local(o,t){
   let {R,ids}=intern(Array.from({length:m},(_,a)=>[...tup(t,2)].map(z=>raw(a,z[0]+o[4],z[1]+o[5]))));
   let A=[];for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.every(a=>a<m))A.push({z,l:ids[x[0]],r:ids[p(...x)]});}
   return {R,A};
  }
  function child(D,d,t){
   let u=t/2,o=d.map(a=>a*u);
   let {R,ids}=intern(D.R.map(row=>[...tup(u,2)].map(z=>row[(z[0]+o[4])*t+z[1]+o[5]])));
   let A=D.A.filter(a=>a.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(a=>({z:a.z.map((v,i)=>v-o[i]),l:ids[a.l],r:ids[a.r]}));
   stats[3]+=D.R.length;return {R,A};
  }
  function visit(node,D,C,o,t){
   if(!node.flag)return;
   ok(!node.active,"exclusive frame");node.active=true;stats[4]++;
   ok(D.R.length<=2*t*t&&D.A.length<=t**4&&C.length<=130*t**3,"local cap");
   let matrix=D.R.map(x=>D.R.map(y=>x.some((v,i)=>!v&&y[i])));
   let live=D.A.some(a=>matrix[a.l][a.r]);stats[5]++;
   let direct=[...tup(t,6)].some(z=>E(z.map((a,i)=>a+o[i])));ok(live===direct,"factorized positivity");
   for(let a of D.A)for(let [x,y] of tup(t,2)){
    let z=[...a.z,x,y].map((v,i)=>v+o[i]);ok((!D.R[a.l][x*t+y]&&!!D.R[a.r][x*t+y])===E(z),"local membership");stats[6]++;
   }
   if(live){
    stats[7]++;
    if(t===1){stats[8]++;let pass=C.length===0;ok(pass===(orig(o)&&E(o.slice(0,6))),"leaf");if(pass){ok(!got.has(key(o)),"disjoint");got.add(key(o));}}
    else for(let d of tup(2,9)){
     let idx=d.slice(6).reduce((s,x)=>2*s+x,0),ch=node.ch[idx];stats[9]++;
     if(!ch.flag)continue;
     let u=t/2,off=d.map(x=>x*u),cc=C.map(r=>({h:r.h,z:r.z.map((x,i)=>x-off[r.h[i]])})).filter(r=>r.z.every(x=>x>=0&&x<u));
     let X=child(D,d,t);stats[10]++;visit(ch,X,cc,o.map((x,i)=>x+off[i]),u);ok(!ch.active&&node.active,"reuse");
    }
   }
   node.active=false;
  }
  for(let q of tup(M/b,6)){
   let po=q.map(a=>a*b),D=local(po,b);
   for(let v of tup(M/b,3)){
    let o=[...po,...v.map(a=>a*b)],root=tree(b,o.slice(6)),C=records.map(r=>({h:r.h,z:r.z.map((x,i)=>x-o[r.h[i]])})).filter(r=>r.z.every(x=>x>=0&&x<b));
    stats[11]++;visit(root,D,C,o,b);
   }
  }
  ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact models");
  stats[12]+=got.size;stats[13]+=expected.size;fixtures++;
 }
 let controls=[];
 for(let m of [4,8,16,32,64]){
  let max=0,cubes=0,forbidden=0;
  for(let t=1;t<=m;t*=2)for(let q of tup(m/t,2)){
   let R=intern(Array.from({length:m},(_,a)=>[...tup(t,2)].map(z=>+(a===z[1]+q[1]*t&&a!==z[0]+q[0]*t)))).R;
   ok(R.length<=t+1&&R.length<=2*t*t,"row certificate");max=Math.max(max,R.length);cubes++;
  }
  for(let z of tup(m,3))forbidden+=((z[0]^z[1]^z[2])&1);
  ok(forbidden===m**3/2,"private parity mass");
  controls.push([m,max,cubes,forbidden]);
 }
 let bad=intern(Array.from({length:16},(_,a)=>Array.from({length:4},(_,i)=>(a>>i)&1))).R.length;
 ok(bad===16&&bad>2*2*2,"certificate rejection control");
 return {fixtures,stats,failedCert,controls,bad};
}
console.log('F038_PRIVATE_STATIONARY_OK '+JSON.stringify(audit()));
