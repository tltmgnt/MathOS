// Host semantic audit of exact directed differences; not physical tape execution.
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
 let fixtures=0,stats=Array(11).fill(0),dictChecks=0,relabels=0,heavyModels=0,lightModels=0,heavyEntries=0,lightEntries=0,maskChecks=0,recoveryChecks=0,types=[0,0];
 function intern(rows){let R=[],ids=[],D=new Map();for(let row of rows){let k=key(row);if(!D.has(k)){D.set(k,R.length);R.push(row);}ids.push(D.get(k));}for(let i=0;i<rows.length;i++){ok(key(R[ids[i]])===key(rows[i]),"dictionary exact");dictChecks++;}return {R,ids};}
 const evalRow=(D,a,j)=>D.kind===0?dot(D.B,a,j):D.R[a][j];
 for(let m of [2,3])for(let mode=0;mode<8;mode++)for(let kind of [0,1]){
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
  let loss=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>[...tup(m,2)].reduce((n,[x,y])=>n+(!raw(a,x,y)&&raw(b,x,y)?1:0),0)));
  const threshold=mode%2===0?m*m:1,allowed=(a,b)=>Math.floor(a/2)===Math.floor(b/2)&&loss[a][b]<=threshold;
  let pairs=[...tup(m,2)].filter(([a,b])=>allowed(a,b)),pairIndex=new Map(pairs.map((z,i)=>[key(z),i]));
  for(let a=0;a<m;a++)ok(allowed(a,a),"self allowed");
  const full=z=>z.every(a=>a<m)&&!raw(z[0],z[4],z[5])&&!!raw(p(...z.slice(0,4)),z[4],z[5]);
  const E=z=>full(z)&&allowed(z[0],p(...z.slice(0,4)));
  for(let z of tup(m,6)){if(full(z)){if(E(z))lightEntries++;else heavyEntries++;}ok(!E(z)||full(z),"light subset");maskChecks++;}
  
  const pv=z=>z.every(a=>a<m)&&privateF.every(s=>!s.B.has(key(s.h.map(g=>z[g-6]))));
  const orig=z=>z.every(a=>a<m)&&F.every(s=>!s.B.has(key(proj(z,s.h))));
  let records=res.flatMap(s=>[...s.B].map(v=>({h:s.h,z:v.split(",").map(Number)})));
  for(let g of G.slice(0,6))for(let a=m;a<M;a++)records.push({h:[g],z:[a]});
  let expected=new Set(),got=new Set();
  for(let z of tup(m,9)){stats[0]++;if(!orig(z))continue;
   let a=z[0],b=p(...z.slice(0,4)),y=z.slice();y[0]=b;
   if(E(z.slice(0,6))){expected.add(key(z));lightModels++;}
   if(full(z.slice(0,6))&&!allowed(a,b))heavyModels++;
   let env=a===b||!allowed(a,b);
   if(orig(y))ok(y[0]===p(...y.slice(0,4)),"representative recovery");
   else if(!allowed(a,b))ok(env,"heavy recovery");
   else if(full(z.slice(0,6)))ok(E(z.slice(0,6)),"light wide recovery");
   else ok(F.some(s=>s.h.includes(0)&&s.B.has(key(proj(y,s.h)))&&!s.B.has(key(proj(z,s.h)))),"other exact exception");
   recoveryChecks++;
  }
  function tree(t,o){let flag=[...tup(t,3)].some(z=>pv(z.map((a,i)=>a+o[i])));stats[1]++;let ch=[];if(flag&&t>1)for(let d of tup(2,3))ch.push(tree(t/2,o.map((a,i)=>a+d[i]*t/2)));return {flag,ch,active:false};}
  function local(o,t){
   let rows=pairs.map(([a,b])=>[...tup(t,2)].map(z=>+(!raw(a,z[0]+o[4],z[1]+o[5])&&!!raw(b,z[0]+o[4],z[1]+o[5]))));
   let {basis,coeff}=kind===0?factor(rows,t*t):{basis:[],coeff:[]}, {R,ids}=kind===1?intern(rows):{R:[],ids:[]};
   let A=[];for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.every(a=>a<m)&&allowed(x[0],p(...x))){let i=pairIndex.get(key([x[0],p(...x)]));A.push({z,ref:kind===0?coeff[i]:ids[i]});}}
   return {kind,B:basis,R,A};
  }
  function child(D,d,t){
   let u=t/2,o=d.map(a=>a*u);
   const restrict=row=>[...tup(u,2)].map(z=>row[(z[0]+o[4])*t+z[1]+o[5]]);
   let {basis,coeff}=D.kind===0?factor(D.B.map(restrict),u*u):{basis:[],coeff:[]}, {R,ids}=D.kind===1?intern(D.R.map(restrict)):{R:[],ids:[]};
   const change=c=>{if(D.kind===0){rebases++;return decode(coeff,c,basis.length);}relabels++;return ids[c];};
   let A=D.A.filter(a=>a.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(a=>({z:a.z.map((v,i)=>v-o[i]),ref:change(a.ref)}));
   return {kind:D.kind,B:basis,R,A};
  }
  function visit(node,D,C,o,t){
   if(!node.flag)return;ok(!node.active,"exclusive frame");node.active=true;stats[2]++;
   ok(D.B.length**8<=4**8*t**3&&D.R.length<=2*t*t&&D.A.length<=t**4&&C.length<=130*t**3,"rank and frame cap");
   let live=false;
   for(let a of D.A)for(let [x,y] of tup(t,2)){
    let z=[...a.z,x,y].map((v,i)=>v+o[i]),v=!!evalRow(D,a.ref,x*t+y);types[D.kind]++;
    ok(v===E(z),"local coefficient membership");stats[3]++;live ||=v;
   }
   ok(live===D.A.some(a=>D.kind===0?a.ref.some(Boolean):D.R[a.ref].some(Boolean)),"coefficient nonzero iff live");
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
 for(let m of [4,16,64,256,1024]){
  let w=Math.sqrt(m),raw=(a,u,v)=>{let c=Math.floor(a/w);if(u<2&&v<2)return (c>>(2*u+v))&1;if(v===0&&u===c+2)return 1;return +(v>=m/2&&a%2===1);};
  let signatures=[new Set(),new Set()],marker=[];
  for(let a=0;a<m;a++)signatures[a%2].add(key([...tup(2,2)].map(([u,v])=>raw(a,u,v))));
  for(let c=0;c<w;c++)marker.push(Array.from({length:w},(_,j)=>raw(c*w,j+2,0)));
  ok(factor(marker,w).basis.length===w,"independent baseline rows");
  ok(signatures.every(S=>S.size===Math.min(w,16)),"raw square row diversity");
  let differenceChecks=0;
  // Small full-domain pair checks; larger controls only sample source pairs and columns.
  for(let c=0;c<w;c++)for(let a of [c*w,c*w+1])for(let b of [c*w,c*w+1]){
   let cols=m<=64?[...tup(m,2)]:[[0,0],[1,1],[c+2,0],[0,m/2],[m-1,m-1]];
   for(let [u,v] of cols){let val=+(!raw(a,u,v)&&!!raw(b,u,v));ok(val===+(a%2===0&&b%2===1&&v>=m/2),"baseline cancellation");differenceChecks++;}
  }
  controls.push([m,w,signatures[0].size,signatures[1].size,w,differenceChecks]);
 }
 ok(heavyEntries>0&&lightEntries>0&&heavyModels>0&&lightModels>0&&types.every(x=>x>0),"both recovery routes and factors");
 return {fixtures,stats,rankChecks,encodingChecks,rebases,dictChecks,relabels,heavyModels,lightModels,heavyEntries,lightEntries,maskChecks,recoveryChecks,types,controls};
}
console.log('F038_DIRECTED_DIFFERENCE_FACTORS_OK '+JSON.stringify(audit()));
