// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(","),G=[0,1,2,3,4,5,6,7,8],K=[1,2,3];
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function sketch(m,reserve){let d=Math.ceil(Math.log2(m)),w=d-reserve,M=2**d;
  let mask=Array.from({length:3},(_,i)=>(2**Math.floor((i+1)*w/3)-1)^(2**Math.floor(i*w/3)-1)),fixed=reserve?M/2:0;
  return {M,mask,fixed,S:c=>fixed|c.reduce((v,x,i)=>v|(x&mask[i]),0)};
 }
 let n={fixtures:0,passes:0,scoreChecks:0,fiberChecks:0,unionBits:0,greedyChecks:0,fullChecks:0,success:0,heavy:0,head:0,tail:0,narrow:0,otherWide:0,headModels:0,unionModels:0,rootChecks:0,localChecks:0,membership:0,childChoices:0,relabels:0,paddingChecks:0},selected={};
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  n.fixtures++;let S=sketch(m,mode%2),M=S.M,ctx=[...tup(m,3)],cols=[...tup(m,2)];
  let F=H.map(h=>({h,R:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){if(mode===0)return false;if(mode===1)return z[0]===z[2]&&z[1]!==z[2];if(mode===2)return z[0]===1&&z[1]===z[2];if(mode===3)return z[0]===1&&z[1]===0;return (z[0]+z[1])%m===z[2];}
   if(key(h)==="0,1,4"&&mode===2)return z[0]===1&&z[1]===z[2];
   if(key(h)==="6,7,8"&&mode===3)return (z[0]^z[1]^z[2])&1;
   if(mode===4)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   if(mode===7)return h.length===2&&z[0]===z[1];return false;
  }).map(key))}));
  let wide=F.filter(s=>s.h[0]===0&&s.h.length===3&&s.h[1]>=4),T=wide.find(s=>key(s.h)==="0,4,5"),local=F.filter(s=>s.h.includes(0));
  const orig=z=>z.every(a=>a<m)&&F.every(s=>!s.R.has(key(proj(z,s.h))));
  const Z=(s,a,b,x,y)=>a<m&&b<m&&x<m&&y<m&&!s.R.has(key([a,x,y]))&&s.R.has(key([b,x,y]));
  const W=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>wide.reduce((v,s)=>v+cols.reduce((w,[x,y])=>w+Z(s,a,b,x,y),0),0)));
  let Qs=Array(M).fill(0);for(let c of ctx)Qs[S.S(c)]++;ok(Qs.every(q=>q<=2*M*M)&&Qs.reduce((a,b)=>a+b,0)===m**3,"bounded unbalanced fiber");
  function narrow(a,b,c){let v=0;for(let s of local){let O=s.h.filter(g=>g>=4);if(O.length===2)continue;for(let z of tup(m,O.length)){let x=s.h.map(g=>g===0?a:g<=3?c[g-1]:z[O.indexOf(g)]),y=x.slice();y[0]=b;if(!s.R.has(key(x))&&s.R.has(key(y)))v+=m**(2-O.length);}}return v;}
  for(let policy of [0,1,2]){
   n.passes++;let maps=new Map(),cap=0,dn=0;
   for(let c of ctx){let C=[],p=[];
    if(policy){let b=(policy===1?S.S(c):c[0]+c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow(a,b,c)+W[a][b])),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");n.greedyChecks++;if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self tie");
    }
    maps.set(key(c),{C,p});cap+=C.length;for(let a=0;a<m;a++)dn+=narrow(a,p[a],c);
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]];
   function evalScore(k,r){
    let keys=new Map(),bad=0,union=0,head=0;
    for(let a=0;a<m;a++)for(let s=0;s<M;s++)if(Qs[s]){
     let f=Array(m).fill(0);for(let c of ctx)if(S.S(c)===s)f[get([a,...c])]++;
     ok(f.reduce((v,x)=>v+x,0)===Qs[s],"fiber count");n.fiberChecks++;
     let top=new Set([...Array.from({length:m},(_,i)=>i).sort((i,j)=>f[j]-f[i]||i-j).slice(0,k),a]);
     let low=Array.from({length:m},(_,b)=>b).filter(b=>f[b]&&!top.has(b)&&W[a][b]<=r);
     let nl=low.reduce((v,b)=>v+f[b],0),nh=f.reduce((v,x,b)=>v+(!top.has(b)&&!low.includes(b)?x:0),0);
     let U=wide.map(h=>new Set(cols.filter(([x,y])=>low.some(b=>Z(h,a,b,x,y))).map(key))),v=U.reduce((v,x)=>v+x.size,0),use=Qs[s]*v<=m*m*nl;
     let heavy=nh+(use?0:nl);bad+=heavy;union+=use?Qs[s]*v:0;
     ok(m*m*heavy+(use?Qs[s]*v:0)===m*m*nh+Math.min(m*m*nl,Qs[s]*v),"weighted charge");n.scoreChecks++;
     for(let i=0;i<wide.length;i++)for(let [x,y] of cols){ok(U[i].has(key([x,y]))===low.some(b=>Z(wide[i],a,b,x,y)),"exact union");n.unionBits++;}
     for(let b of top)head+=f[b]*W[a][b];
     keys.set(key([a,s]),{top,low:new Set(use?low:[]),U:use?U:wide.map(()=>new Set())});
    }
    return {k,r,keys,bad,union,head,Q:BigInt((cap+bad)*m*m+dn+union)+BigInt(k+1)**13n*BigInt(head)};
   }
   let cand=[];for(let k of [0,1,2])for(let r of [0,1,10*m*m])cand.push(evalScore(k,r));
   let best=policy===0?cand.reduce((a,b)=>a.Q<=b.Q?a:b):evalScore(policy===1?0:1,policy===1?10*m*m:1);
   if(!policy)ok(cand.every(x=>x.Q>=best.Q),"minimum");
   let tag=best.k+","+best.r;selected[tag]=(selected[tag]||0)+1;
   const info=z=>best.keys.get(key([z[0],S.S(z.slice(1,4))])),route=z=>info(z).top.has(get(z))?0:info(z).low.has(get(z))?1:2;
   const hi=wide.indexOf(T),e=(z,i=hi)=>z.every(a=>a<m)&&route(z)===0&&Z(wide[i],z[0],get(z),z[wide[i].h[1]],z[wide[i].h[2]]),
    u=(z,i=hi)=>z.every(a=>a<m)&&info(z).U[i].has(key([z[wide[i].h[1]],z[wide[i].h[2]]]));
   let hc=0,uc=0,bc=0;
   for(let a=0;a<m;a++)for(let c of ctx){let z=[a,...c];if(route(z)===0)hc+=W[a][get(z)];if(route(z)===2)bc++;uc+=info(z).U.reduce((v,R)=>v+R.size,0);}
   ok(hc===best.head&&uc===best.union&&bc===best.bad,"expanded score");
   let expected=[new Set(),new Set()],got=[new Set(),new Set()];
   for(let z of tup(m,9)){n.fullChecks++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"representative");n.success++;}
    else if(route(z)===2)n.heavy++;
    else if(local.some(s=>s.h.filter(g=>g>=4).length<2&&!s.R.has(key(proj(z,s.h)))&&s.R.has(key(proj(y,s.h)))))n.narrow++;
    else if(route(z)===0){ok(wide.some((s,i)=>e(z,i)),"head recovery");n.head++;}
    else{ok(wide.some((s,i)=>u(z,i)),"union recovery");n.tail++;}
    if(e(z))expected[0].add(key(z));if(u(z))expected[1].add(key(z));
   }
   let raw=F.flatMap(s=>[...s.R].map(k=>({h:s.h,z:k.split(",").map(Number)})));for(let g of G)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
   const rel=(c,t)=>c.reduce((v,x,i)=>v|(x&(S.mask[i]&(t-1))),0);
   function attainable(t,len){let A=new Set();for(let c of tup(t,3))if(c.every((x,i)=>x<len[i]))A.add(rel(c,t));return A;}
   function compact(D,A){let used=new Set(A.map(r=>key([r.z[0],r.s,r.j]))),by=new Map(),cnt=new Map(),out=[];
    for(let r of D){let k=key([r.a,r.s,r.j]);if(!used.has(k))continue;let p=key([r.a,r.s]),j=cnt.get(p)||0;cnt.set(p,j+1);by.set(k,j);out.push({...r,j});}
    return {D:out,A:A.map(r=>{let j=by.get(key([r.z[0],r.s,r.j]));ok(j!==undefined,"compact reference");n.relabels++;return {...r,j};})};
   }
   function root(o,t){let len=o.slice(1,4).map(x=>Math.max(0,Math.min(t,m-x))),base=S.S(o.slice(1,4)),poss=attainable(t,len),U=[],D=[],A=[];
    for(let a=0;a<t&&a+o[0]<m;a++)for(let s of poss){
     let q=best.keys.get(key([a+o[0],base|s]));ok(!!q,"actual sketch key");
     U.push({a,s,R:[...tup(t,2)].map(([x,y])=>+q.U[hi].has(key([x+o[4],y+o[5]])))});
     let j=0;for(let b of q.top){D.push({a,s,j,b,R:[...tup(t,2)].map(([x,y])=>+Z(T,a+o[0],b,x+o[4],y+o[5]))});j++;}
    }
    for(let z of tup(t,4)){let x=z.map((v,i)=>v+o[i]);if(x.some(v=>v>=m)||route(x)!==0)continue;let s=rel(z.slice(1,4),t),row=D.find(r=>r.a===z[0]&&r.s===s&&r.b===get(x));ok(!!row,"root reference");A.push({z,s,j:row.j});}
    n.rootChecks++;return {...compact(D.map(({b,...r})=>r),A),U,len};
   }
   function child(X,d,t){let v=t/2,off=d.map(a=>a*v),q=rel(off.slice(1,4),t),len=X.len.map((x,i)=>Math.max(0,Math.min(v,x-off[i+1]))),poss=attainable(v,len);
    function clip(R){return R.filter(r=>r.a>=off[0]&&r.a<off[0]+v&&(r.s&v)===q&&poss.has(r.s&(v-1))).map(r=>({...r,a:r.a-off[0],s:r.s&(v-1),R:[...tup(v,2)].map(([x,y])=>r.R[(x+off[4])*t+y+off[5]])}));}
    let A=X.A.filter(r=>r.z.every((x,i)=>x>=off[i]&&x<off[i]+v)).map(r=>({z:r.z.map((x,i)=>x-off[i]),s:r.s&(v-1),j:r.j}));
    return {...compact(clip(X.D),A),U:clip(X.U),len};
   }
   function visit(X,C,o,t){let h=false,u0=false,D=new Map(X.D.map(r=>[key([r.a,r.s,r.j]),r.R])),U=new Map(X.U.map(r=>[key([r.a,r.s]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r]));
    ok(X.U.length<=t*t&&X.D.length<=Math.min(best.k+1,t*t)*t*t&&X.A.length<=t**4,"frame bounds");
    for(let z of tup(t,6)){
     let x=z.map((a,i)=>a+o[i]),s=rel(z.slice(1,4),t),r=A.get(key(z.slice(0,4))),dr=r?D.get(key([z[0],s,r.j])):null,ur=U.get(key([z[0],s])),valid=x.every(a=>a<m);
     let h1=!!(valid&&dr&&dr[z[4]*t+z[5]]),u1=!!(valid&&ur&&ur[z[4]*t+z[5]]);
     ok(h1===e(x)&&u1===u(x),"exact local membership");n.membership++;h ||=h1;u0 ||=u1;
    }
    ok(h===X.A.some(r=>D.get(key([r.z[0],r.s,r.j])).some(Boolean))&&u0===X.U.some(r=>r.R.some(Boolean)),"exact positivity");n.localChecks++;
    if(!h&&!u0)return;
    if(t===1){if(!C.length){ok(orig(o),"original");if(h)got[0].add(key(o));if(u0)got[1].add(key(o));}return;}
    for(let d of tup(2,9)){let v=t/2,off=d.map(a=>a*v),L=C.map(r=>({h:r.h,z:r.z.map((a,i)=>a-off[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<v));n.childChoices++;visit(child(X,d,t),L,o.map((a,i)=>a+off[i]),v);}
   }
   for(let q of tup(M/2,6)){let po=q.map(a=>a*2),X=root(po,2);for(let v of tup(M/2,3)){let o=[...po,...v.map(a=>a*2)],C=raw.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<2));visit(X,C,o,2);}}
   for(let i=0;i<2;i++)ok(got[i].size===expected[i].size&&[...got[i]].every(z=>expected[i].has(z)),"exact branch models");
   n.headModels+=got[0].size;n.unionModels+=got[1].size;
  }
 }
 // Exact local sketch restriction with nonpower domains and every dyadic context tile.
 for(let m of [3,5,9,17])for(let reserve of [0,1]){
  let S=sketch(m,reserve);
  for(let t=2;t<=S.M;t*=2)for(let q of tup(S.M/t,3)){
   let o=q.map(a=>a*t),base=S.S(o),vals=new Set(),R=new Set();
   for(let z of tup(t,3))if(z.every((a,i)=>a+o[i]<m)){
    let v=z.reduce((v,a,i)=>v|(a&(S.mask[i]&(t-1))),0);ok(S.S(z.map((a,i)=>a+o[i]))===(base|v),"local identity");vals.add(v);R.add(base|v);
   }
   ok(vals.size<=t&&vals.size===R.size,"local image cap");
   for(let d of tup(2,3)){let u=t/2,off=d.map(a=>a*u),sel=off.reduce((v,a,i)=>v|(a&S.mask[i]),0),C=new Set();
    for(let z of tup(u,3))if(z.every((a,i)=>a+o[i]+off[i]<m))C.add(z.reduce((v,a,i)=>v|(a&(S.mask[i]&(u-1))),0));
    ok([...C].every(v=>vals.has(sel|v)),"child exact subset");n.paddingChecks++;
   }
  }
 }
 // Finite-field block-subspace control: all nonzero quotient forms and exact bad-x counts.
 let controls=[];
 for(let [d,poly] of [[6,67],[9,529]]){
  let m=2**d,S=sketch(m,1),ell=1,J=m/2**ell,D=J*(m-J);
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  for(let a=1;a<m;a++)ok(new Set(Array.from({length:m},(_,b)=>mul(a,b))).size===m,"field");
  let checks=0,bad=[];
  for(let i=0;i<3;i++){
   let W=Array.from({length:m},(_,a)=>a).filter(a=>(a&~S.mask[i])===0),B=W.map(a=>a|S.fixed),count=0;
   for(let x=0;x<m;x++){
    let f=Array(2**ell).fill(0);for(let a of W)f[Math.floor(mul(x,a)/J)]++;
    if(f.some(v=>v===0))count++;else ok(f.every(v=>v===W.length/2**ell),"uniform fibers");checks++;
   }
   ok(count<=(2**ell-1)*m/W.length,"bad x bound");
   // Direct union on a=0, old-zero columns; all good x must be covered.
   let hits=0;for(let x=0;x<m;x++)for(let y=J;y<m;y++)if(B.some(b=>(mul(x,b)^y)<J))hits++;
   ok(hits>=(m-count)*(m-J),"dense union lower bound");bad.push([W.length,count,hits]);
  }
  // Actual first choice and every second marginal for block-match narrow supports.
  let ctx=[m-1,Math.floor(m/3),Math.floor(m/5)],f=S.S(ctx);
  const narrow=(a,b)=>+(a>=m/2&&b<m/2)*m*m+S.mask.reduce((v,M,i)=>v+((a&M)===(ctx[i]&M)&&(b&M)!==(ctx[i]&M)?m*m:0),0);
  const dist=(a,b)=>narrow(a,b)+(a===b?0:D);
  let scores=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>dist(a,b)).reduce((v,x)=>v+x,0));
  ok(scores.every((v,b)=>b===f||v>scores[f]),"unique target");
  for(let b=0;b<m;b++)if(b!==f){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,dist(a,f)-dist(a,b));ok(gain<m*m,"stop");}
  controls.push([m,J,D,checks,bad,f]);
 }
 ok(n.head>0&&n.tail>0&&n.heavy>0,"routes");
 return {n,selected,controls};
}
console.log('F038_CONTEXT_SKETCHES_OK '+JSON.stringify(audit()));
