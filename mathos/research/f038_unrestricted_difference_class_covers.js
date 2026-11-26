// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let n={fixtures:0,passes:0,candidates:0,tailChecks:0,capChecks:0,classChecks:0,zeroPairs:0,dominance:0,full:0,success:0,heavy:0,wide:0,narrow:0,local:0,membership:0,relabels:0,children:0,models:0,roots:0,greedy:0},selected={};
 const id=r=>key([r.a,...r.c]);
 function census(m,F){
  let labels=Array.from({length:m},()=>Array(m)),rows=Array.from({length:m},()=>new Map()),loss=Array.from({length:m},()=>Array(m));
  for(let a=0;a<m;a++){let D=new Map();for(let b=0;b<m;b++){
   let R=[...tup(m,2)].map(([x,y])=>+(!F(a,x,y)&&F(b,x,y))),k=R.join(""),w=R.reduce((s,x)=>s+x,0);
   loss[a][b]=w;if(!w){labels[a][b]=null;n.zeroPairs++;continue;}
   if(!D.has(k)){D.set(k,b);rows[a].set(b,R);}
   let j=D.get(k);labels[a][b]=j;ok(rows[a].get(j).every((v,i)=>v===R[i]),"exact directed class");n.classChecks++;
  }}
  return {labels,rows,loss};
 }
 function trim(records,B,C,alpha,label){
  let live=records.filter(r=>label(r)!==null),original=live.slice(),tail=0;
  const cap=t=>Math.floor(C*t**alpha+1e-9);
  function groups(A,t){let D=new Map();for(let r of A){let k=key([r.a,...r.c.map(x=>Math.floor(x/t))]);if(!D.has(k))D.set(k,[]);D.get(k).push(r);}return D;}
  function head(A,k){let N=new Map();for(let r of A){let j=label(r);N.set(j,(N.get(j)||0)+1);}return new Set([...N].sort((a,b)=>b[1]-a[1]||a[0]-b[0]).slice(0,k).map(r=>r[0]));}
  for(let t=B;t>=1;t/=2){
   let keep=[],e=0;
   for(let A of groups(original,t).values()){let h=head(A,cap(t));for(let r of A)if(!h.has(label(r)))e++;}
   for(let A of groups(live,t).values()){let h=head(A,cap(t));for(let r of A)if(h.has(label(r)))keep.push(r);}
   ok(live.length-keep.length<=e,"level tail");n.tailChecks++;tail+=e;live=keep;
  }
  for(let t=B;t>=1;t/=2)for(let A of groups(live,t).values()){ok(new Set(A.map(label)).size<=cap(t),"all-scale cap");n.capChecks++;}
  let keep=new Set(live.map(id)),out=records.filter(r=>label(r)===null||keep.has(id(r))),removed=records.length-out.length;
  ok(removed<=tail,"tail bound");return {live:out,removed,tail};
 }
 const labelRaw=r=>r.a===r.b?null:r.b;
 function classTrim(records,B,C,alpha,Qs){
  let live=records,tail=0;
  for(let Q of Qs){let label=r=>Q.labels[r.a][r.b],T=trim(live,B,C,alpha,label);tail+=T.tail;live=T.live;}
  let removed=records.length-live.length;ok(removed<=tail,"combined bound");
  return {live,removed,tail};
 }
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  n.fixtures++;let M=1;while(M<m)M*=2;let B=2,ctx=[...tup(m,3)],cols=[...tup(m,2)];
  let F=[{h:[0,4,5],f:z=>mode===0?false:mode===1?z[0]===z[2]&&z[1]!==z[2]:mode===2?z[0]===1&&z[1]===z[2]:(z[0]+z[1])%m===z[2]},
   {h:[0,6,7],f:z=>mode===5&&(z[0]+z[2])%m===z[1]},
   {h:[0,1,4],f:z=>mode===2&&z[0]===1&&z[1]===z[2]},
   {h:[6,7,8],f:z=>mode===3&&!!((z[0]^z[1]^z[2])&1)},
   {h:[2,8],f:z=>mode===4&&z[0]===z[1]}];
  const proj=(z,h)=>h.map(g=>z[g]),orig=z=>z.every(a=>a<m)&&F.every(s=>!s.f(proj(z,s.h)));
  let Qs=F.slice(0,2).map(s=>census(m,(a,x,y)=>s.f([a,x,y])));
  const wide=(a,b)=>Qs.reduce((w,Q)=>w+Q.loss[a][b],0);
  const narrow=(a,b,c)=>m*[...tup(m,1)].filter(([x])=>!F[2].f([a,c[0],x])&&F[2].f([b,c[0],x])).length;
  for(let policy of [0,1]){
   n.passes++;let maps=new Map(),records=[],cap=0,dn=0;
   for(let c of ctx){let C,p;
    if(policy){let b=(c[0]+c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow(a,b,c)+wide(a,b))),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");n.greedy++;if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self ties");
    }
    cap+=C.length;maps.set(key(c),{C,p});for(let a=0;a<m;a++){records.push({a,c,b:p[a]});dn+=narrow(a,p[a],c);}
   }
   let cand=[];
   for(let alpha of [1,1.25])for(let C of [1,2,4]){
    let old=trim(records,B,C,alpha,labelRaw),X=classTrim(records,B,C,alpha,Qs),P=alpha===1?13:25;
    let score=A=>BigInt((cap+A.removed)*m*m+dn)+BigInt(C)**BigInt(P)*BigInt(A.live.reduce((v,r)=>v+wide(r.a,r.b),0));
    let qOld=score(old),qNew=score(X);
    // Portfolio includes raw-label trimming; use quotient rows for both options.
    let Y=qNew<=qOld?X:old;ok(score(Y)<=qOld,"portfolio dominance");n.dominance++;
    cand.push({...Y,alpha,C,Q:score(Y),type:qNew<=qOld?"class":"label"});n.candidates++;
   }
   let best=policy?cand[0]:cand.reduce((a,b)=>a.Q<=b.Q?a:b);
   let tag=best.alpha+","+best.C+","+best.type;selected[tag]=(selected[tag]||0)+1;
   let live=new Set(best.live.map(id)),get=z=>maps.get(key(z.slice(1,4))).p[z[0]],isLive=z=>live.has(key(z.slice(0,4)));
   const e=(i,z)=>z.every(a=>a<m)&&isLive(z)&&!F[i].f(proj(z,F[i].h))&&F[i].f([get(z),z[F[i].h[1]],z[F[i].h[2]]]);
   let expected=[new Set(),new Set()];
   for(let z of tup(m,9)){n.full++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"representative recovery");n.success++;}
    else if(!isLive(z)){ok(z[0]!==y[0],"heavy");n.heavy++;}
    else if(!F[2].f(proj(z,F[2].h))&&F[2].f(proj(y,F[2].h)))n.narrow++;
    else{ok(e(0,z)||e(1,z),"wide recovery");n.wide++;}
    for(let i=0;i<2;i++)if(e(i,z))expected[i].add(key(z));
   }
   let raw=F.flatMap(s=>[...tup(m,s.h.length)].filter(s.f).map(z=>({h:s.h,z})));for(let g=0;g<9;g++)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
   for(let i=0;i<2;i++){
    let Q=Qs[i],P=[0,1,2,3,...F[i].h.slice(1)],V=Array.from({length:9},(_,g)=>g).filter(g=>!P.includes(g)),got=new Set();
    if(!Q.rows.some(R=>R.size)){ok(expected[i].size===0,"empty branch");continue;}
    function expand(z){let a=Array(9).fill(0);P.forEach((g,j)=>a[g]=z[j]);return a;}
    function compact(D,A){
     let used=new Set(A.map(r=>key([r.z[0],r.j]))),by=new Map(),cnt=new Map(),out=[];
     for(let r of D){let k=key([r.a,r.j]);if(!used.has(k))continue;let j=cnt.get(r.a)||0;cnt.set(r.a,j+1);by.set(k,j);out.push({...r,j});}
     return {D:out,A:A.map(r=>{let j=by.get(key([r.z[0],r.j]));ok(j!==undefined,"ref");n.relabels++;return {...r,j};})};
    }
    function root(o,t){let D=[],A=[],ids=new Map(),cnt=new Map();
     for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.some(a=>a>=m)||!isLive(x))continue;let b=get(x),v=Q.labels[x[0]][b];if(v===null)continue;let k=key([z[0],v]);
      if(!ids.has(k)){let j=cnt.get(z[0])||0;cnt.set(z[0],j+1);ids.set(k,j);D.push({a:z[0],j,R:[...tup(t,2)].map(([u,w])=>+(u+o[4]<m&&w+o[5]<m&&Q.rows[x[0]].get(v)[(u+o[4])*m+w+o[5]]))});}
      A.push({z,j:ids.get(k)});
     }return {D,A};
    }
    function child(X,d,t){let u=t/2,o=P.map(g=>d[g]*u);
     let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u).map(r=>({...r,a:r.a-o[0],R:[...tup(u,2)].map(([x,y])=>r.R[(x+o[4])*t+y+o[5]])}));
     let A=X.A.filter(r=>r.z.every((a,i)=>a>=o[i]&&a<o[i]+u)).map(r=>({z:r.z.map((a,i)=>a-o[i]),j:r.j}));return compact(D,A);
    }
    function visit(X,C,o,t){let D=new Map(X.D.map(r=>[key([r.a,r.j]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r.j]));
     for(let a=0;a<t;a++){let count=X.D.filter(r=>r.a===a).length;ok(count<=Math.floor(best.C*t**best.alpha+1e-9)&&count<=t**3,"local class cap");}
     let flag=false;
     for(let z of tup(t,6)){let j=A.get(key(z.slice(0,4))),R=D.get(key([z[0],j])),x=expand(z.map((a,j)=>a+o[P[j]])),f=!!(R&&R[z[4]*t+z[5]]);ok(f===e(i,x),"exact local membership");n.membership++;flag ||=f;}
     ok(flag===X.A.some(r=>D.get(key([r.z[0],r.j])).some(Boolean)),"positive");n.local++;
     if(!flag)return;if(t===1){if(!C.length){ok(orig(o)&&e(i,o),"leaf");got.add(key(o));}return;}
     for(let d of tup(2,9)){let u=t/2,off=d.map(a=>a*u),L=C.map(r=>({h:r.h,z:r.z.map((a,i)=>a-off[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<u));n.children++;visit(child(X,d,t),L,o.map((a,i)=>a+off[i]),u);}
    }
    for(let q of tup(M/B,6)){let po=q.map(a=>a*B),X=root(po,B);for(let v of tup(M/B,3)){let o=expand(po);V.forEach((g,j)=>o[g]=v[j]*B);let C=raw.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<B));n.roots++;visit(X,C,o,B);}}
    ok(got.size===expected[i].size&&[...got].every(k=>expected[i].has(k)),"exact branch model set");n.models+=got.size;
   }
  }
 }
 // Different raw targets agree after masking the old row; distinct per-support classes need not form a small joint class.
 let m=32,Qs=[census(m,(a,x,y)=>a>0&&a<=16&&x===((a-1)%4)&&y===0),census(m,(a,x,y)=>a>0&&a<=16&&x===Math.floor((a-1)/4)&&y===0)];
 let rec=[...tup(4,3)].map(c=>({a:0,c,b:1+c[0]+4*c[1]})),A=classTrim(rec,4,1,1,Qs),B=trim(rec,4,1,1,labelRaw);
 ok(A.removed===0&&B.removed>0,"separate classes avoid product");
 let product=[rec.length,B.removed,A.removed,...Qs.map(Q=>new Set(rec.map(r=>Q.labels[r.a][r.b])).size),new Set(rec.map(r=>key(Qs.map(Q=>Q.labels[r.a][r.b])))).size];
 // A nontrivial heavy class trim with genuinely nonzero differences.
 let Q=census(8,(a,x,y)=>a!==0&&x===a&&y===0),rr=[...tup(8,3)].map(c=>({a:0,c,b:1+((c[0]+2*c[1]+4*c[2])%7)})),R=classTrim(rr,8,1,1,[Q]),keep=new Set(R.live.map(id)),heavyModels=0;
 for(let r of rr)if(!keep.has(id(r))){
  const F=(a,x,y)=>a!==0&&x===a&&y===0;
  ok(Q.loss[r.a][r.b]===1&&!F(r.a,r.b,0)&&F(r.b,r.b,0)&&r.a!==r.b,"heavy original witness");
  heavyModels++;
 }
 ok(heavyModels===R.removed&&heavyModels>0,"heavy recount");
 // Uniform loss and actual greedy singleton checks for distinct raw rows with hidden target variation.
 const parity=x=>{let v=0;while(x){v^=x&1;x>>=1;}return v;};
 let controls=[];
 for(let d of [4,5,6]){
  let m=2**d,r=Math.floor(0.9*d),q=2**r,low=m/2,J=Math.max(1,m/16),target=a=>a>=low&&a<low+q;
  let raw=(a,x,y)=>target(a)?y<J||(y>=m/4&&y<m/2&&!!(parity(a&x)^(y&1))):y>=m/4&&y<m/2||y>=m/2&&!!(parity(a&x)^(y&1));
  let Q=census(m,raw),rawRows=new Set(),checks=0,merged=0,greedy=0;
  for(let a=0;a<m;a++){rawRows.add([...tup(m,2)].map(([x,y])=>+raw(a,x,y)).join(""));
   if(!target(a)){let C=new Set();for(let b=low;b<low+q;b++)C.add(Q.labels[a][b]);ok(C.size===1,"all target differences identical for old source");merged++;}
   for(let b=0;b<m;b++)if(a!==b){
    let want=!target(a)?target(b)?m*J:m*m/8:target(b)?m*m/16:null;
    if(want!==null){ok(Q.loss[a][b]===want,"loss identity");checks++;}
   }
  }
  ok(rawRows.size===m,"all raw rows distinct");
  let even=0,odd=0;for(let j=0;j<r;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let f=low;f<low+q;f++){
   let narrow=(a,b)=>m*m*(+ (target(a)&&!target(b))+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));
   const D=(a,b)=>Q.loss[a][b]+narrow(a,b);
   let sums=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>D(a,b)).reduce((v,x)=>v+x,0));
   ok(sums.every((v,b)=>b===f||v>sums[f]),"unique first facility");
   for(let b=0;b<m;b++)if(b!==f){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,D(a,f)-D(a,b));ok(gain<m*m,"second marginal below penalty");greedy++;}
  }
  controls.push([m,q,rawRows.size,merged,checks,greedy]);
 }
 // Arithmetic comparison only, not enumeration of these enormous families.
 let exponents=[];for(let d of [64,128,256,512]){
  let b=Math.floor(2*d/3),r=Math.floor(0.9*d),logCap=d/32+1.25*b;
  ok(logCap<r&&Math.ceil(r/2)<=b,"old cap obstruction");exponents.push([d,b,r,logCap]);
 }
 // Nonself substitutions with no directed differences consume no class slots.
 let zero=census(8,()=>false),zr=classTrim(rr,8,1,1,[zero]);
 ok(zr.removed===0&&zr.live.length===rr.length,"zero differences require no rows");
 return {n,selected,product,heavy:[rr.length,R.live.length,R.removed,R.tail,heavyModels],controls,exponents,zeroControl:[rr.length,zr.removed]};
}
console.log('F038_DIFFERENCE_CLASS_COVERS_OK '+JSON.stringify(audit()));
