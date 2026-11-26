// Host semantic audit, not physical tape execution.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},key=z=>z.join(","),G=[0,1,2,3,4,5,6,7,8];
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 let n={fixtures:0,passes:0,frequencyChecks:0,entropyChecks:0,scoreChecks:0,greedyChecks:0,fullChecks:0,success:0,heavy:0,wide:0,narrow:0,localChecks:0,positiveChecks:0,relabels:0,children:0,models:0,roots:0},chosen={};
 function learn(m,maps,k){
  let P=Array.from({length:m},()=>Array.from({length:m},()=>new Map())),bad=0;
  for(let a=0;a<m;a++)for(let h=0;h<m;h++){
   let f=Array(m).fill(0);for(let i=0;i<m;i++)for(let j=0;j<m;j++)f[maps.get(key([h,i,j])).p[a]]++;
   let b=Array.from({length:m},(_,i)=>i).sort((i,j)=>f[j]-f[i]||i-j).slice(0,k);
   let L=P[a][h];for(let x of [...b,a])if(!L.has(x))L.set(x,L.size);
   let miss=f.reduce((v,c,x)=>v+(L.has(x)?0:c),0);bad+=miss;
   let max=b.reduce((v,x)=>v+f[x],0);
   for(let mask=0;mask<2**m;mask++){let Q=Array.from({length:m},(_,x)=>x).filter(x=>mask>>x&1);if(Q.length===k){ok(Q.reduce((v,x)=>v+f[x],0)<=max,"top k optimum");n.frequencyChecks++;}}
   ok(miss<=m*m-max&&L.has(a)&&L.size<=k+1,"tail and self");
   let entropy=f.reduce((v,c)=>v+(c?-(c/(m*m))*Math.log2(c/(m*m)):0),0);
   ok((m*m-max)*Math.log2(k+1)<=m*m*entropy+1e-8,"entropy bound");n.entropyChecks++;
  }return {P,bad};
 }
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  n.fixtures++;let M=1;while(M<m)M*=2;
  let F=H.map(h=>({h,R:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){if(mode===0)return false;if(mode===1)return z[0]===z[2]&&z[1]!==z[2];if(mode===2)return z[0]===1&&z[1]===z[2];if(mode===3)return z[0]===1&&z[1]===0;return (z[0]+z[1])%m===z[2];}
   if(key(h)==="0,1,4"&&mode===2)return z[0]===1&&z[1]===z[2];
   if(mode===3&&key(h)==="6,7,8")return (z[0]^z[1]^z[2])&1;
   if(mode===4)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   if(mode===7)return h.length===2&&z[0]===z[1];return false;
  }).map(key))}));
  let T=F.find(s=>key(s.h)==="0,4,5"),raw=(a,u,v)=>T.R.has(key([a,u,v])),orig=z=>z.every(a=>a<m)&&F.every(s=>!s.R.has(key(proj(z,s.h))));
  let rec=F.flatMap(s=>[...s.R].map(k=>({h:s.h,z:k.split(",").map(Number)})));
  for(let g of G)for(let a=m;a<M;a++)rec.push({h:[g],z:[a]});
  let contexts=[...tup(m,3)],localSupports=F.filter(s=>s.h.includes(0));
  function loss(a,b,c,wide){let v=0;for(let s of localSupports){let O=s.h.filter(g=>g!==0&&(g<1||g>3));if((O.length===2)!==wide)continue;
   for(let z of tup(m,O.length)){let x=s.h.map(g=>g===0?a:g>=1&&g<=3?c[g-1]:z[O.indexOf(g)]),y=x.slice();y[0]=b;if(!s.R.has(key(x))&&s.R.has(key(y)))v+=m**(2-O.length);}
  }return v;}
  for(let force of [false,true]){
   n.passes++;let maps=new Map(),cap=0,deltaN=0;
   for(let c of contexts){
    let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>loss(a,b,c,false)+loss(a,b,c,true)));
    let C=[],p=[],best=null;
    if(force){let b=(c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{
     let res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[];
     for(let k=1;k<=m;k++){
      let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let s=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(s<v){v=s;b=j;}}
      A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}
      ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");n.greedyChecks++;
      if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};
     }
     C=best.C;p=best.p;for(let a of C)p[a]=a;
     ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self tie");
    }
    cap+=C.length;for(let a=0;a<m;a++)deltaN+=loss(a,p[a],c,false);maps.set(key(c),{C,p});
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]];
   let candidates=[];
   for(let k=1;k<=m;k++){
    let {P,bad}=learn(m,maps,k),w=0;
    for(let c of contexts)for(let a=0;a<m;a++)if(P[a][c[0]].has(get([a,...c])))w+=loss(a,get([a,...c]),c,true);
    let Q=BigInt((cap+bad)*m*m+deltaN)+BigInt(k+1)**13n*BigInt(w);
    candidates.push({P,bad,w,k,Q});n.scoreChecks++;
   }
   let best=force?candidates[0]:candidates.reduce((a,b)=>a.Q<=b.Q?a:b);if(!force)ok(candidates.every(x=>x.Q>=best.Q),"score minimum");
   chosen[best.k]=(chosen[best.k]||0)+1;let pal=best.P,permit=z=>pal[z[0]][z[1]].has(get(z));
   let E=z=>z.every(a=>a<m)&&permit(z)&&!raw(z[0],z[4],z[5])&&raw(get(z),z[4],z[5]);
   let actual=0;for(let c of contexts)for(let a=0;a<m;a++)if(permit([a,...c]))actual+=loss(a,get([a,...c]),c,true);ok(actual===best.w,"wide weighted mass");
   let expected=new Set(),got=new Set();
   for(let z of tup(m,9)){
    n.fullChecks++;if(!orig(z))continue;let c=z.slice(1,4),a=z[0],b=get(z),y=z.slice();y[0]=b;
    if(orig(y)){ok(maps.get(key(c)).C.includes(b),"representative");n.success++;}
    else if(!permit(z)){ok(!permit(z),"heavy");n.heavy++;}
    else if(E(z.slice(0,6)))n.wide++;
    else{ok(localSupports.some(s=>!s.R.has(key(proj(z,s.h)))&&s.R.has(key(proj(y,s.h)))),"other exception");n.narrow++;}
    if(E(z.slice(0,6)))expected.add(key(z));
   }
   function compact(D,A){
    let used=new Set(A.map(r=>key([r.z[0],r.z[1],r.j]))),by=new Map(),next=new Map(),out=[];
    for(let r of D){let k=key([r.a,r.h,r.j]);if(!used.has(k))continue;let p=key([r.a,r.h]),j=next.get(p)||0;next.set(p,j+1);by.set(k,j);out.push({...r,j});}
    return {D:out,A:A.map(r=>{let j=by.get(key([r.z[0],r.z[1],r.j]));ok(j!==undefined,"compacted key");n.relabels++;return {...r,j};})};
   }
   function local(o,t){
    let D=[],A=[];
    for(let [a,h] of tup(t,2)){let x=a+o[0],y=h+o[1];if(x>=m||y>=m)continue;for(let [b,j] of pal[x][y])D.push({a,h,j,R:[...tup(t,2)].map(([u,v])=>+(!raw(x,u+o[4],v+o[5])&&raw(b,u+o[4],v+o[5])))});}
    for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.some(a=>a>=m)||!permit(x))continue;A.push({z,j:pal[x[0]][x[1]].get(get(x))});}
    return compact(D,A);
   }
   function child(X,d,t){
    let u=t/2,o=d.map(a=>a*u);
    let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u&&r.h>=o[1]&&r.h<o[1]+u).map(r=>({a:r.a-o[0],h:r.h-o[1],j:r.j,R:[...tup(u,2)].map(([x,y])=>r.R[(x+o[4])*t+y+o[5]])}));
    let A=X.A.filter(r=>r.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(r=>({z:r.z.map((v,i)=>v-o[i]),j:r.j}));
    return compact(D,A);
   }
   function visit(X,C,o,t){
    ok(X.D.length<=Math.min(best.k+1,t*t)*t*t&&X.A.length<=t**4,"frame cap");let D=new Map(X.D.map(r=>[key([r.a,r.h,r.j]),r.R]));
    ok(D.size===X.D.length&&X.D.every(r=>r.j<t*t),"local labels");
    let live=false;for(let r of X.A){let R=D.get(key([r.z[0],r.z[1],r.j]));ok(!!R,"ref");for(let [u,v] of tup(t,2)){let z=[...r.z,u,v].map((a,i)=>a+o[i]),f=!!R[u*t+v];ok(f===E(z),"membership");n.localChecks++;live ||=f;}}
    ok(live===[...tup(t,6)].some(z=>E(z.map((a,i)=>a+o[i]))),"positivity");n.positiveChecks++;
    if(!live)return;
    if(t===1){let pass=C.length===0;ok(pass===(orig(o)&&E(o.slice(0,6))),"leaf");if(pass){ok(!got.has(key(o)),"disjoint");got.add(key(o));}return;}
    for(let d of tup(2,9)){let u=t/2,z=d.map(a=>a*u),L=C.map(r=>({h:r.h,z:r.z.map((v,i)=>v-z[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<u));n.children++;visit(child(X,d,t),L,o.map((a,i)=>a+z[i]),u);}
   }
   for(let q of tup(M/2,6)){let po=q.map(a=>a*2),X=local(po,2);for(let v of tup(M/2,3)){let o=[...po,...v.map(a=>a*2)],C=rec.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<2));n.roots++;visit(X,C,o,2);}}
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact model set");n.models+=got.size;
  }
 }
 // Bounded entropy despite a growing support.
 let synthetic=[];
 for(let m of [16,64,256,1024]){let f=Array(m).fill(0);for(let j=0;j<m;j++)f[Math.floor(Math.log2(j+1))]++;f.sort((a,b)=>b-a);let H=f.reduce((s,x)=>s+(x?-(x/m)*Math.log2(x/m):0),0),tail=[1,2,4,8].map(k=>f.slice(k).reduce((s,x)=>s+x,0)/m);ok(tail.every((v,i)=>v*Math.log2(2**i+1)<=H+1e-10),"entropy bound");synthetic.push([m,H,tail]);}
 // Exact deterministic uniform-loss and greedy class control, including source/target zero.
 const parity=x=>{let s=0;while(x){s^=x&1;x>>=1;}return s;};
 let clusters=[];
 for(let m of [16,64,256]){
  let q=Math.sqrt(m),J=m/2,checks=0,code=Array.from({length:m},(_,a)=>a%q+1);
  for(let a=1;a<m;a++)for(let b=1;b<m;b++)if(a!==b){let z=0;for(let u=0;u<m;u++)z+=!parity(a&u)&&parity(b&u);ok(z*J===m*J/4,"uniform loss");checks++;}
  // Sample the actual facility algorithm with five free binary sections and the wide section.
  let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>+(code[a]!==code[b])*5*m*m/4+ +(a!==0&&b===0)*m*m+(a===b||b===0?0:a===0?m*J/2:m*J/4)));
  let A=[],res=Array(m).fill(37*m*m),p=Array(m).fill(-1),best;
  for(let k=1;k<=m;k++){
   let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let s=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(s<v){v=s;b=j;}}
   A.push(b);for(let a=0;a<m;a++)if(p[a]<0||D[a][b]<res[a]){p[a]=b;res[a]=D[a][b];}
   if(!best||k*m*m+v<best.score)best={A:A.slice(),p:p.slice(),score:k*m*m+v};
  }
  ok(best.A.length<=q+1&&best.p.every((b,a)=>code[b]===code[a]),"cluster greedy control");
  clusters.push([m,q,checks,best.A.length,best.p.filter((b,a)=>a!==b).length]);
 }
 // Independent score control: zero wide mass, four equiprobable replacement labels.
 let mm=4,mp=new Map();for(let c of tup(mm,3))mp.set(key(c),{C:[c[1]],p:Array(mm).fill(c[1])});
 let qv=[1,2,4].map(k=>{let x=learn(mm,mp,k);return [k,x.bad,BigInt((mm**3+x.bad)*mm*mm)];});
 let win=qv.reduce((a,b)=>a[2]<=b[2]?a:b);ok(win[0]===4&&win[1]===0,"growing palette selection");
 // Independent narrow-only failure: a permitted replacement introduces a binary forbidden bit.
 let original=[0,0,0,0,0,0,0,0,0],replaced=original.slice();replaced[0]=1;
 let narrow=z=>z[0]===1&&z[1]===0;
 ok(!narrow(original)&&narrow(replaced),"narrow-only exception");
 ok(n.heavy>0&&n.wide>0,"heavy and light routes");
 return {n,chosen,synthetic,clusters,scoreControl:qv.map(([k,b,q])=>[k,b,q.toString()]),narrowControl:1};
}
console.log('F038_LEARNED_PALETTE_TAILS_OK '+JSON.stringify(audit()));
