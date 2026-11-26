// Host semantic audit; no physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let n={fixtures:0,passes:0,scoreChecks:0,tailChecks:0,capChecks:0,full:0,recovery:0,heavy:0,wide:0,narrow:0,local:0,membership:0,relabels:0,children:0,models:0,roots:0},selected={};
 function trim(records,B,C,alpha){
  let live=records.filter(r=>r.a!==r.b),original=live.slice(),tail=0;
  function groups(A,t){let D=new Map();for(let r of A){let k=key([r.a,...r.c.map(x=>Math.floor(x/t))]);if(!D.has(k))D.set(k,[]);D.get(k).push(r);}return D;}
  function head(A,k){let N=new Map();for(let r of A)N.set(r.b,(N.get(r.b)||0)+1);return new Set([...N].sort((a,b)=>b[1]-a[1]||a[0]-b[0]).slice(0,k).map(r=>r[0]));}
  const cap=t=>Math.floor(C*t**alpha+1e-9);
  for(let t=B;t>=1;t/=2){
   let keep=[],e=0;
   for(let A of groups(original,t).values()){let h=head(A,cap(t));for(let r of A)if(!h.has(r.b))e++;}
   for(let A of groups(live,t).values()){let h=head(A,cap(t));for(let r of A)if(h.has(r.b))keep.push(r);}
   ok(live.length-keep.length<=e,"single level tail");n.tailChecks++;tail+=e;live=keep;
  }
  for(let t=B;t>=1;t/=2)for(let A of groups(live,t).values()){ok(new Set(A.map(r=>r.b)).size<=cap(t),"all-scale cap");n.capChecks++;}
  let removed=original.length-live.length;ok(removed<=tail,"union bound");return {live,removed,tail};
 }
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  n.fixtures++;let M=1;while(M<m)M*=2;let B=2,ctx=[...tup(m,3)],cols=[...tup(m,2)];
  const F=[{h:[0,4,5],f:z=>mode===0?false:mode===1?z[0]===z[2]&&z[1]!==z[2]:mode===2?z[0]===1&&z[1]===z[2]:(z[0]+z[1])%m===z[2]},
   {h:[0,1,4],f:z=>mode===2&&z[0]===1&&z[1]===z[2]},
   {h:[6,7,8],f:z=>mode===3&&!!((z[0]^z[1]^z[2])&1)},
   {h:[2,8],f:z=>mode===4&&z[0]===z[1]}];
  const proj=(z,h)=>h.map(g=>z[g]),orig=z=>z.every(a=>a<m)&&F.every(s=>!s.f(proj(z,s.h))),T=F[0];
  const Z=(a,b,x,y)=>a<m&&b<m&&x<m&&y<m&&!T.f([a,x,y])&&T.f([b,x,y]);
  const wide=(a,b)=>cols.reduce((w,[x,y])=>w+Z(a,b,x,y),0);
  const narrow=(a,b,c)=>m*[...tup(m,1)].filter(([x])=>!F[1].f([a,c[0],x])&&F[1].f([b,c[0],x])).length;
  for(let policy of [0,1]){
   n.passes++;let maps=new Map(),records=[],cap=0,dn=0;
   for(let c of ctx){let C,p;if(policy){let b=(c[0]+c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}else{
    let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow(a,b,c)+wide(a,b))),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
    for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(v===res.reduce((s,x)=>s+x,0),"greedy");if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};}
    C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self");
   }
   cap+=C.length;maps.set(key(c),{C,p});for(let a=0;a<m;a++){records.push({a,c,b:p[a]});dn+=narrow(a,p[a],c);}
   }
   let cand=[];for(let alpha of [1,1.25])for(let C of [1,2,4]){
    let X=trim(records,B,C,alpha),w=X.live.reduce((v,r)=>v+wide(r.a,r.b),0),P=alpha===1?13:25;
    let Q=BigInt((cap+X.removed)*m*m+dn)+BigInt(C)**BigInt(P)*BigInt(w);cand.push({...X,C,alpha,w,Q});n.scoreChecks++;
   }
   let best=policy?cand[0]:cand.reduce((a,b)=>a.Q<=b.Q?a:b);if(!policy)ok(cand.every(x=>x.Q>=best.Q),"minimum");
   let tag=best.alpha+","+best.C;selected[tag]=(selected[tag]||0)+1;
   let live=new Set(best.live.map(r=>key([r.a,...r.c]))),get=z=>maps.get(key(z.slice(1,4))).p[z[0]],isLive=z=>live.has(key(z.slice(0,4)));
   let e=z=>z.every(a=>a<m)&&isLive(z)&&Z(z[0],get(z),z[4],z[5]);
   let expected=new Set(),got=new Set();
   for(let z of tup(m,9)){n.full++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"rep");n.recovery++;}
    else if(!isLive(z)){ok(z[0]!==y[0],"heavy nonself");n.heavy++;}
    else if(!F[1].f(proj(z,F[1].h))&&F[1].f(proj(y,F[1].h)))n.narrow++;
    else{ok(e(z),"wide recovery");n.wide++;}
    if(e(z))expected.add(key(z));
   }
   let raw=F.flatMap(s=>[...tup(m,s.h.length)].filter(s.f).map(z=>({h:s.h,z})));for(let g=0;g<9;g++)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
   function compact(D,A){
    let used=new Set(A.map(r=>key([r.z[0],r.j]))),by=new Map(),cnt=new Map(),out=[];
    for(let r of D){let k=key([r.a,r.j]);if(!used.has(k))continue;let j=cnt.get(r.a)||0;cnt.set(r.a,j+1);by.set(k,j);out.push({...r,j});}
    return {D:out,A:A.map(r=>{let j=by.get(key([r.z[0],r.j]));ok(j!==undefined,"ref");n.relabels++;return {...r,j};})};
   }
   function root(o,t){let D=[],A=[],ids=new Map(),cnt=new Map();
    for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.some(a=>a>=m)||!isLive(x))continue;let b=get(x),k=key([z[0],b]);
     if(!ids.has(k)){let j=cnt.get(z[0])||0;cnt.set(z[0],j+1);ids.set(k,j);D.push({a:z[0],j,R:[...tup(t,2)].map(([u,v])=>+Z(x[0],b,u+o[4],v+o[5]))});}
     A.push({z,j:ids.get(k)});
    }return {D,A};
   }
   function child(X,d,t){let u=t/2,o=d.map(a=>a*u);
    let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u).map(r=>({...r,a:r.a-o[0],R:[...tup(u,2)].map(([x,y])=>r.R[(x+o[4])*t+y+o[5]])}));
    let A=X.A.filter(r=>r.z.every((a,i)=>a>=o[i]&&a<o[i]+u)).map(r=>({z:r.z.map((a,i)=>a-o[i]),j:r.j}));return compact(D,A);
   }
   function visit(X,C,o,t){let D=new Map(X.D.map(r=>[key([r.a,r.j]),r.R])),A=new Map(X.A.map(r=>[key(r.z),r.j]));
    for(let a=0;a<t;a++){let count=X.D.filter(r=>r.a===a).length;ok(count<=Math.floor(best.C*t**best.alpha+1e-9)&&count<=t**3,"local row cap");}
    let flag=false;
    for(let z of tup(t,6)){let j=A.get(key(z.slice(0,4))),R=D.get(key([z[0],j])),x=z.map((a,i)=>a+o[i]),f=!!(R&&R[z[4]*t+z[5]]);ok(f===e(x),"local exact");n.membership++;flag ||=f;}
    ok(flag===X.A.some(r=>D.get(key([r.z[0],r.j])).some(Boolean)),"positive");n.local++;
    if(!flag)return;if(t===1){if(!C.length){ok(orig(o)&&e(o),"leaf");got.add(key(o));}return;}
    for(let d of tup(2,9)){let u=t/2,off=d.map(a=>a*u),L=C.map(r=>({h:r.h,z:r.z.map((a,i)=>a-off[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<u));n.children++;visit(child(X,d,t),L,o.map((a,i)=>a+off[i]),u);}
   }
   for(let q of tup(M/B,6)){let po=q.map(a=>a*B),X=root(po,B);for(let v of tup(M/B,3)){let o=[...po,...v.map(a=>a*B)],C=raw.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<B));n.roots++;visit(X,C,o,B);}}
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"model set");n.models+=got.size;
  }
 }
 let controls=[];
 for(let d of [3,4,5,6]){
  let m=2**d,mask=2**Math.floor((d-1)/2)-1,other=m/2-1-mask,f=c=>m/2|((c[0]^c[1])&mask)|((c[1]^c[2])&other);
  let checks=0,maxRatio=0;
  for(let t=1;t<=m;t*=2)for(let q of tup(m/t,3)){
   let S=new Set();for(let z of tup(t,3))S.add(f(z.map((a,i)=>a+q[i]*t)));ok(S.size<=t,"XOR local cap");maxRatio=Math.max(maxRatio,S.size/t);checks++;
  }
  let fibers=new Map();for(let c of tup(m,3)){let s=(c[0]&mask)|(c[2]&other)|(c[1]&(m/2));if(!fibers.has(s))fibers.set(s,new Set());fibers.get(s).add(f(c));}
  ok([...fibers.values()].every(s=>s.size===m/2),"diffuse sketch");
  let omitted=[];for(let i=0;i<3;i++){let S=new Set(Array.from({length:m},(_,x)=>f([0,0,0].map((a,j)=>i===j?x:a))));omitted.push(S.size);}
  let rec=[];for(let c of tup(m,3))rec.push({a:0,c,b:f(c)});let X=trim(rec,m,1,1);ok(X.removed===0,"no trimming XOR");
  controls.push([m,checks,maxRatio,fibers.size,omitted,X.removed]);
 }
 let rec=[...tup(8,3)].map(c=>({a:0,c,b:1+((c[0]+2*c[1]+4*c[2])%7)}));let R=trim(rec,8,1,1);ok(R.removed>0,"nontrivial trim");
 // Every discarded assignment can be recovered by the width-four envelope.
 let retained=new Set(R.live.map(r=>key(r.c)));let heavyCheck=0;
 for(let r of rec)if(!retained.has(key(r.c))){ok(r.a!==r.b,"heavy nonself");heavyCheck++;}
 ok(heavyCheck===R.removed,"heavy recount");
 return {n,selected,controls,trimControl:[rec.length,R.live.length,R.removed,R.tail,heavyCheck]};
}
console.log('F038_LOCAL_LABEL_COVERS_OK '+JSON.stringify(audit()));
