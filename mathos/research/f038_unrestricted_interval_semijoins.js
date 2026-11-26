// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let n={fixtures:0,passes:0,filters:0,extensionChecks:0,monotone:0,rootMass:0,rootBuild:0,childBuild:0,member:0,weights:0,volume:0,full:0,models:0,overflowModels:0,dominance:0,recovery:0};
 const A=[0,1,2,3],P=[0,1,2,3,4,5];
 function weight(D,t,mode){
  if(mode==="dense"){let count=Array(t).fill(0);for(let r of D)count[r.a]++;return Math.max(...count);}
  if(mode==="run"){let w=0;for(let r of D){w++;let prev="";for(let x=0;x<t;x++){let s=r.bits.slice(x*t,(x+1)*t);if(s!==prev&&s.includes("1"))w+=1+(s.match(/1+/g)||[]).length;prev=s;}}return w;}
  let sets=Array.from({length:Math.log2(t)+1},()=>new Set());
  for(let r of D)for(let j=0,u=1;u<=t;j++,u*=2)for(let x=0;x<t;x+=u)for(let y=0;y<t;y+=u){let s="";for(let k=0;k<u;k++)s+=r.bits.slice((x+k)*t+y,(x+k)*t+y+u);if(s.includes("1"))sets[j].add(s);}
  return sets.reduce((v,s)=>v+s.size,0);
 }
 function make(m,B,C,F,get,center,mode,filter,full){
  let M=1;while(M<m)M*=2;
  const valid=z=>z.every(a=>a<m),raw=F.flatMap(s=>[...tup(m,s.h.length)].filter(s.f).map(z=>({h:s.h,z})));
  for(let g of P)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
  const proj=raw.filter(r=>r.h.every(g=>g<6));
  const wide=F[0].f, E=z=>valid(z)&&!wide([z[0],z[4],z[5]])&&wide([get(z),z[4],z[5]])&&!wide([center(z[0],get(z)),z[4],z[5]]);
  const original=z=>valid(z)&&F.every(r=>!r.f(r.h.map(g=>z[g])));
  function clip(L,o,t){return L.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<t));}
  function pass(L,z,t){
   n.filters++;
   if(L.some(r=>r.h.every(g=>g<4)&&r.z.every((v,i)=>v===z[r.h[i]])))return false;
   for(let v of [4,5]){
    let found=false;
    for(let a=0;a<t;a++){let k=z.slice();k[v]=a;n.extensionChecks++;
     if(!L.some(r=>r.h.every(g=>g<4||g===v)&&r.z.every((b,i)=>b===k[r.h[i]]))){found=true;break;}
    }if(!found)return false;
   }return true;
  }
  function directPass(z,o,t){
   if(!valid(z))return false;
   if(F.some(s=>s.h.every(g=>g<4)&&s.f(s.h.map(g=>z[g]))))return false;
   for(let v of [4,5]){let found=false;
    for(let a=o[v];a<Math.min(m,o[v]+t);a++){let k=z.slice();k[v]=a;if(!F.some(s=>s.h.every(g=>g<4||g===v)&&s.f(s.h.map(g=>k[g])))){found=true;break;}}
    if(!found)return false;
   }return true;
  }
  function intern(D,R,t,L){
   let used=new Set(R.map(r=>key([r.z[0],r.id]))),dict=new Map(),by=new Map(),out=[];
   for(let r of D){let k=key([r.a,r.id]);if(!used.has(k))continue;if(!r.bits.includes("1")){by.set(k,null);continue;}
    let s=key([r.a,r.bits]);if(!dict.has(s)){let j=out.length;dict.set(s,j);out.push({a:r.a,id:j,bits:r.bits});}by.set(k,dict.get(s));
   }
   R=R.filter(r=>by.get(key([r.z[0],r.id]))!==null).map(r=>{let id=by.get(key([r.z[0],r.id]));ok(id!==undefined,"reference");return {...r,id};});
   return {D:out,R,L,w:weight(out,t,mode)};
  }
  function build(o,t){
   let L=clip(proj,o,t),D=[],R=[],seen=new Set();
   for(let z of tup(t,4)){let v=z.map((a,i)=>a+o[i]);if(!valid(v))continue;
    let p=pass(L,z,t);ok(p===directPass(v,o,t),"root extension identity");if(filter&&!p)continue;
    let b=get(v),k=key([z[0],b]);if(!seen.has(k)){seen.add(k);let bits="";for(let [x,y] of tup(t,2))bits+=+E([...v,x+o[4],y+o[5]]);D.push({a:z[0],id:b,bits});}R.push({z,id:b});
   }n.rootBuild++;return intern(D,R,t,L);
  }
  function child(X,d,t,o){
   let u=t/2,off=d.map(a=>a*u),O=o.map((a,i)=>a+off[i]),L=clip(X.L,off,u);
   let R=X.R.filter(r=>r.z.every((a,i)=>a>=off[i]&&a<off[i]+u)).map(r=>({z:r.z.map((a,i)=>a-off[i]),id:r.id}));
   R=R.filter(r=>{let v=r.z.map((a,i)=>a+O[i]),p=pass(L,r.z,u);ok(p===directPass(v,O,u),"child extension identity");if(p){ok(directPass(v,o,t),"extension monotone");n.monotone++;}return !filter||p;});
   let D=X.D.filter(r=>r.a>=off[0]&&r.a<off[0]+u).map(r=>{let bits="";for(let x=0;x<u;x++)bits+=r.bits.slice((x+off[4])*t+off[5],(x+off[4])*t+off[5]+u);return {...r,a:r.a-off[0],bits};});
   n.childBuild++;return intern(D,R,u,L);
  }
  const cap=t=>C*(mode==="dense"?t:t**4);
  let roots=new Map(),over=[],mass=0,rootR=0;
  function tree(X,o,t,isRoot){
   let D=new Map(X.D.map(r=>[r.id,r.bits])),R=new Map(X.R.map(r=>[key(r.z),r.id])),seen=new Map(),positive=false,localR=0;
   for(let z of tup(t,4)){let v=z.map((a,i)=>a+o[i]),bits="",allowed=!filter||directPass(v,o,t);
    for(let [x,y] of tup(t,2)){let e=allowed&&E([...v,x+o[4],y+o[5]]),s=D.get(R.get(key(z)));ok(!!(s&&s[x*t+y]==="1")===e,"membership");bits+=+e;n.member++;localR+=+e;positive ||=e;}
    if(bits.includes("1"))seen.set(key([z[0],bits]),{a:z[0],bits});
   }
   ok(X.w===weight([...seen.values()],t,mode),"exact weight");n.weights++;
   ok(positive===!!X.R.length,"positivity");if(isRoot){rootR+=localR;n.rootMass++;}
   if(X.w>cap(t)){over.push({o,t});mass+=t**6;return {over:true,flag:true};}
   let T={over:false,flag:positive,ch:[]};
   if(positive&&t>1)for(let d of tup(2,6))T.ch.push(tree(child(X,d,t,o),o.map((a,i)=>a+d[i]*t/2),t/2,false));
   return T;
  }
  for(let q of tup(M/B,6)){let o=q.map(a=>a*B);roots.set(key(q),tree(build(o,B),o,B,true));}
  const belongs=z=>over.some(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t));
  let vol=0,rr=0;
  for(let z of tup(M,6)){let k=over.filter(r=>z.every((a,i)=>a>=r.o[i]&&a<r.o[i]+r.t)).length;ok(k<=1,"disjoint overflow");vol+=k;n.volume++;
   if((!filter||directPass(z.slice(0,4),z.map(a=>Math.floor(a/B)*B),B))&&E(z))rr++;
  }
  ok(vol===mass&&rr===rootR,"exact volume and root-filtered mass");
  if(full){
   let expected=new Set(),got=new Set();
   for(let z of tup(m,9)){n.full++;if(original(z)&&(E(z.slice(0,6))||belongs(z.slice(0,6))))expected.add(key(z));}
   function go(T,o,t){
    if(T.over){for(let z of tup(t,9)){let v=z.map((a,i)=>a+o[i]);if(original(v)){got.add(key(v));n.overflowModels++;}}return;}
    if(!T.flag)return;if(t===1){if(original(o))got.add(key(o));return;}
    for(let d of tup(2,9)){let u=t/2,idx=d.slice(0,6).reduce((v,a)=>2*v+a,0);go(T.ch[idx],o.map((a,i)=>a+d[i]*u),u);}
   }
   for(let q of tup(M/B,9))go(roots.get(key(q.slice(0,6))),q.map(a=>a*B),B);
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact full branch model set");n.models+=got.size;
   for(let z of tup(m,9))if(original(z)&&E(z.slice(0,6))){ok(got.has(key(z)),"original E witness preserved");n.recovery++;}
  }
  return {mass,rootR,belongs,over:over.length};
 }
 let cases=[];
 for(let m of [2,3])for(let mode=0;mode<4;mode++){
  n.fixtures++;
  let F=[{h:[0,4,5],f:([a,x,y])=>mode===0?a===y&&x!==y:(a+x)%m===y},
   {h:[0,1,4],f:([a,c,x])=>mode===1?a!==c&&x!==0:mode===2?a===c&&x===0:mode===3?a!==c:false},
   {h:[0,2,5],f:([a,c,y])=>mode===2?a!==c&&y!==1:false},
   {h:[0,3],f:([a,c])=>mode===0&&a===c},
   {h:[4],f:([x])=>mode===3&&x===0},
   {h:[6,7],f:([a,b])=>a===b},{h:[2,8],f:([a,b])=>a===b}];
  let get=z=>(z[1]+2*z[2]+z[3]+1)%m,center=mode===2?()=>0:a=>a;
  for(let rep of ["dense","run","dag"]){
   n.passes++;let X=make(m,2,1,F,get,center,rep,false,false),Y=make(m,2,1,F,get,center,rep,true,true);
   ok(Y.mass<=X.mass&&Y.rootR<=X.rootR,"score dominance");
   let M=m===2?2:4;for(let z of tup(M,6)){ok(!Y.belongs(z)||X.belongs(z),"overflow inclusion");n.dominance++;}
   cases.push([m,mode,rep,X.rootR,Y.rootR,X.mass,Y.mass]);
  }
 }
 // Finite field conditional escape control, direct bit enumeration.
 let controls=[];
 for(let [m,poly,B] of [[16,19,4],[32,37,8],[64,67,16]]){
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  let T=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>mul(a,b))),d=Math.log2(m),q=m/2,j=m/4,D=j*(m-j);
  let state=0x517f038,perm=Array.from({length:m*m},(_,i)=>i);
  for(let k=perm.length-1;k>0;k--){state=(Math.imul(state,1664525)+1013904223)>>>0;let i=state%(k+1);[perm[k],perm[i]]=[perm[i],perm[k]];}
  let raw=Array.from({length:m},(_,a)=>Uint8Array.from(perm,i=>+( (T[a][Math.floor(i/m)]^(i%m))<j)));
  let targets=new Set(),even=0,odd=0;for(let p=0;p<d-1;p++)if(p%2)odd|=1<<p;else even|=1<<p;
  for(let c1=0;c1<B;c1++)for(let c2=0;c2<B;c2++){let f=q;for(let p=0;p<d-1;p++)f|=(((p%2?c2:c1)>>Math.floor(p/2))&1)<<p;targets.add(f);}
  ok(targets.size===q,"coarse target coverage");
  let losses=0,first=0,marginal=0,filtered=0,unfiltered=0,witnesses=0,minEscape=Infinity;
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a!==b){
   let total=0,esc=0;for(let i=0;i<m*m;i++){let v=+(!raw[a][i]&&raw[b][i]);total+=v;if(i<B*m)esc+=v;}ok(total===D,"pair loss");losses++;
   if(targets.has(b)){unfiltered+=total;filtered+=esc;witnesses+=esc;minEscape=Math.min(minEscape,esc);}
  }
  let gate=m*(m-B);
  for(let f of targets){
   function loss(a,b){return (a===b?0:D)+gate*(+(a>=q&&b<q)+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));}
   let sums=Array(m).fill(0);for(let b=0;b<m;b++)for(let a=0;a<m;a++)sums[b]+=loss(a,b);
   ok(sums.every((v,b)=>b===f||v>sums[f]),"first facility");first++;
   for(let b=0;b<m;b++)if(b!==f){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,loss(a,f)-loss(a,b));ok(gain<=D&&gain<m*m,"second marginal");marginal++;}
  }
  let intervalChecks=0;
  for(let a=0;a<m;a++)for(let f of targets)for(let x0=0;x0<m;x0+=B){
   let allowed=false;for(let x=x0;x<x0+B;x++)if(x<B||(a>=q&&(a&even)===(f&even)&&(a&odd)===(f&odd)))allowed=true;
   ok(allowed===(x0===0||a===f),"interval extension");intervalChecks++;
  }
  ok(filtered>0&&filtered<unfiltered&&minEscape>0,"nonvacuous escape");
  // Every target has m^3/q contexts. Exact mass uses this multiplicity.
  controls.push([m,B,losses,first,marginal,intervalChecks,unfiltered*m**3/q,filtered*m**3/q,minEscape,witnesses]);
 }
 return {n,cases,controls};
}
console.log('F038_INTERVAL_SEMIJOINS_OK '+JSON.stringify(audit()));
