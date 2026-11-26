// Host semantic reference; no physical tape measurements.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],K=[1,2,3],key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function masks(d){return Array.from({length:6},(_,i)=>{let lo=Math.floor(i*d/6),hi=Math.floor((i+1)*d/6);return (2**hi-1)^(2**lo-1);});}
 function palette(m,a,h){
  let B=masks(Math.ceil(Math.log2(m))),L=new Map();
  for(let j=0;j<729;j++){let q=j,b=0;for(let i=0;i<6;i++){let s=q%3;q=Math.floor(q/3);b|=(s===1?a:s===2?h:0)&B[i];}if(b<m&&!L.has(b))L.set(b,j);}
  ok(L.has(a)&&L.size<=729,"palette self and cap");return L;
 }
 let fixtures=0,stats=Array(16).fill(0),greedyChecks=0,penaltyChecks=0,selected=Array(4).fill(0),forced=Array(4).fill(0);
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let M=1;while(M<m)M*=2;let B=2;
  let F=H.map(h=>({h,R:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){
    if(mode===0)return false;
    if(mode===1)return z[0]===z[2]&&z[1]!==z[2];
    if(mode===2)return z[0]===1&&z[1]===z[2];
    if(mode===3)return z[0]===1&&z[1]===0;
    return (z[0]+z[1])%m===z[2];
   }
   if(mode===2&&key(h)==="0,1,4")return z[0]===1&&z[1]===z[2];
   if(mode===3&&key(h)==="6,7,8")return (z[0]^z[1]^z[2])&1;
   if(mode===4)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   if(mode===7)return h.length===2&&z[0]===z[1];
   return false;
  }).map(key))}));
  let T=F.find(s=>key(s.h)==="0,4,5"),raw=(a,u,v)=>T.R.has(key([a,u,v])),orig=z=>z.every(a=>a<m)&&F.every(s=>!s.R.has(key(proj(z,s.h))));
  let pal=Array.from({length:m},(_,a)=>Array.from({length:m},(_,h)=>palette(m,a,h)));
  let rec=F.flatMap(s=>[...s.R].map(k=>({h:s.h,z:k.split(",").map(Number)})));
  for(let g of G)for(let a=m;a<M;a++)rec.push({h:[g],z:[a]});
  let contexts=[...tup(m,3)],localSupports=F.filter(s=>s.h.includes(0));
  function loss(a,b,c){let n=0;for(let s of localSupports){
   let O=s.h.filter(g=>g!==0&&!K.includes(g));
   for(let z of tup(m,O.length)){
    let x=s.h.map(g=>g===0?a:K.includes(g)?c[K.indexOf(g)]:z[O.indexOf(g)]),y=x.slice();y[0]=b;
    if(!s.R.has(key(x))&&s.R.has(key(y)))n+=m**(2-O.length);
   }
  }return n;}
  for(let force of [false,true]){
   let maps=new Map(),mass=[0,0,0,0];
   for(let c of contexts){
    let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>loss(a,b,c)+(pal[a][c[0]].has(b)?0:m*m)));
    let C=[],p=[],best=null;
    if(force){let b=(c.reduce((s,a)=>s+a,0)+1)%m;C=[b];p=Array(m).fill(b);}
    else{
     let res=Array(m).fill(38*m*m),cur=Array(m).fill(-1),A=[],profile=[];
     for(let k=1;k<=m;k++){
      let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let n=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(n<v){v=n;b=j;}}
      A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}
      ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");profile.push(v);
      if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};
     }
     for(let bits=1;bits<2**m;bits++){
      let Q=Array.from({length:m},(_,i)=>i).filter(i=>bits>>i&1),h=Q.length,L=D.reduce((s,row)=>s+Math.min(...Q.map(j=>row[j])),0),prev=38*m**3;
      for(let v of profile){ok(h*(prev-v)>=prev-L,"marginal averaging");prev=v;greedyChecks++;}
      ok(best.score<=m*m*(h*(1+Math.log(m/h))+1)+L+38*m*m*h/Math.E+1e-8,"greedy comparison");
     }
     C=best.C;p=best.p;
     ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"score");
     ok(C.every(a=>pal[a][c[0]].has(p[a])),"representative permitted");
    }
    mass[0]+=C.length;
    for(let a=0;a<m;a++){let b=p[a],bad=!pal[a][c[0]].has(b);mass[1]+=bad;mass[2]+=loss(a,b,c);penaltyChecks++;if(!force)ok(D[a][b]===loss(a,b,c)+m*m*bad,"penalty");}
    maps.set(key(c),{C,p});
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]],permit=z=>pal[z[0]][z[1]].has(get(z));
   const E=z=>z.every(a=>a<m)&&permit(z)&&!raw(z[0],z[4],z[5])&&raw(get(z),z[4],z[5]);
   let expected=new Set(),got=new Set();
   for(let z of tup(m,9)){
    stats[0]++;if(!orig(z))continue;
    let c=z.slice(1,4),a=z[0],b=get(z),y=z.slice();y[0]=b;
    if(orig(y)){ok(maps.get(key(c)).C.includes(b),"representative recovery");stats[1]++;}
    else if(!permit(z)){stats[2]++;ok(!permit(z),"heavy envelope");}
    else if(!raw(a,z[4],z[5])&&raw(b,z[4],z[5])){ok(E(z.slice(0,6)),"light wide recovery");stats[3]++;}
    else{ok(localSupports.some(s=>!s.R.has(key(proj(z,s.h)))&&s.R.has(key(proj(y,s.h)))),"other exact exception");stats[4]++;}
    if(E(z.slice(0,6)))expected.add(key(z));
   }
   mass[3]=expected.size;
   mass.forEach((v,i)=>(force?forced:selected)[i]+=v);
   function local(o,t){
    let D=[],A=[];
    for(let [a,h] of tup(t,2)){
     let x=a+o[0],y=h+o[1];if(x>=m||y>=m)continue;
     for(let [b,j] of pal[x][y]){
      let R=[...tup(t,2)].map(([u,v])=>+(!raw(x,u+o[4],v+o[5])&&raw(b,u+o[4],v+o[5])));
      D.push({a,h,j,R});stats[5]++;
     }
    }
    for(let z of tup(t,4)){let x=z.map((a,i)=>a+o[i]);if(x.some(a=>a>=m)||!permit(x))continue;A.push({z,j:pal[x[0]][x[1]].get(get(x))});}
    return {D,A};
   }
   function child(X,d,t){
    let u=t/2,o=d.map(a=>a*u);
    let D=X.D.filter(r=>r.a>=o[0]&&r.a<o[0]+u&&r.h>=o[1]&&r.h<o[1]+u).map(r=>({a:r.a-o[0],h:r.h-o[1],j:r.j,R:[...tup(u,2)].map(([x,y])=>r.R[(x+o[4])*t+y+o[5]])}));
    let A=X.A.filter(r=>r.z.every((v,i)=>v>=o[i]&&v<o[i]+u)).map(r=>({z:r.z.map((v,i)=>v-o[i]),j:r.j}));
    stats[6]+=D.length;return {D,A};
   }
   function visit(X,C,o,t){
    stats[7]++;ok(X.D.length<=729*t*t&&X.A.length<=t**4&&C.length<=129*t**3,"frame cap");
    let D=new Map(X.D.map(r=>[key([r.a,r.h,r.j]),r.R]));
    ok(D.size===X.D.length,"unique row keys");
    let live=false;
    for(let r of X.A){let R=D.get(key([r.z[0],r.z[1],r.j]));ok(!!R,"row reference");
     for(let [u,v] of tup(t,2)){let z=[...r.z,u,v].map((a,i)=>a+o[i]),f=!!R[u*t+v];ok(f===E(z),"exact membership");stats[8]++;live ||=f;}
    }
    ok(live===[...tup(t,6)].some(z=>E(z.map((a,i)=>a+o[i]))),"positivity");stats[9]++;
    if(!live)return;stats[10]++;
    if(t===1){stats[11]++;let pass=C.length===0;ok(pass===(orig(o)&&E(o.slice(0,6))),"exact leaf");if(pass){ok(!got.has(key(o)),"disjoint");got.add(key(o));}return;}
    for(let d of tup(2,9)){let u=t/2,z=d.map(a=>a*u),L=C.map(r=>({h:r.h,z:r.z.map((v,i)=>v-z[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<u));stats[12]++;visit(child(X,d,t),L,o.map((a,i)=>a+z[i]),u);}
   }
   for(let q of tup(M/B,6)){
    let po=q.map(a=>a*B),X=local(po,B);
    for(let v of tup(M/B,3)){let o=[...po,...v.map(a=>a*B)],C=rec.map(r=>({h:r.h,z:r.z.map((a,i)=>a-o[r.h[i]])})).filter(r=>r.z.every(a=>a>=0&&a<B));stats[13]++;visit(X,C,o,B);}
   }
   ok(got.size===expected.size&&[...got].every(k=>expected.has(k)),"exact model set");stats[14]+=got.size;stats[15]+=expected.size;
  }
  fixtures++;
 }
 const parity=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 // Six-block deletion control with three simultaneous binary forms and excluded digits.
 let deletionChecks=0,allNonzero=0,splices=0;
 for(let d of [6,9,12,18]){
  let m=2**d,B=masks(d);
  for(let i=0;i<512;i++){
   let a=(i*7919+17)%m,c=[(i*41+3)%m,(i*113+5)%m,(i*193+7)%m];
   let choices=[];for(let mask=0;mask<64;mask++){let b=0;for(let j=0;j<6;j++)if(mask>>j&1)b|=a&B[j];choices.push(b);}
   let pool=b=>B.some(mask=>(b&mask)===0);
   if(a===0||c.includes(a)||pool(a)){ok(choices.includes(a),"self in palette");}
   else{allNonzero++;let good=choices.filter(b=>b!==a&&b!==0&&!c.includes(b)&&pool(b)&&c.every(h=>parity(a&h)===parity(b&h)));ok(good.length>=3,"kernel deletion choices");}
   deletionChecks++;
  }
 }
 for(let m of [2,3,5,9,17,33])for(let a=0;a<m;a++)for(let h=0;h<m;h++){
  let L=palette(m,a,h);ok([...L].every(([b,j])=>b>=0&&b<m&&j>=0&&j<729),"nonpower palette");splices++;
 }
 // Actual permutations at small field size: all ordered nonzero distinct losses equal.
 let uniform=[];
 for(let d of [4,5,6]){
  let m=2**d,J=m/2,perms=[];
  for(let v=0;v<J;v++){let p=Array.from({length:m},(_,i)=>i);if(v<2)for(let u=0;u<2;u++){let k=p.indexOf(2**(2*v+u));[p[u],p[k]]=[p[k],p[u]];}ok(new Set(p).size===m,"permutation");perms.push(p);}
  let n=0;
  for(let a=1;a<m;a++)for(let b=1;b<m;b++)if(a!==b){let x=0;for(let p of perms)for(let u of p)x+=!parity(a&u)&&parity(b&u);ok(x===m*J/4,"uniform directed loss");n++;}
  uniform.push([m,J,n]);
 }
 let patterns=new Set();for(let p=0;p<65536;p++){let a=65536,b=a+p,row=0;for(let j=0;j<16;j++)row|=(+(!parity(a&(1<<j))&&parity(b&(1<<j))))<<j;ok(row===p,"independent 4-square patterns");patterns.add(row);}
 ok(patterns.size===65536&&16>4*Math.sqrt(4),"old factors fail");
 ok(stats[2]>0&&stats[3]>0&&stats[4]>0&&allNonzero>0,"all recovery routes");
 return {fixtures,stats,greedyChecks,penaltyChecks,selected,forced,deletionChecks,allNonzero,splices,uniform,patterns:patterns.size};
}
console.log('F038_CONTEXT_PALETTES_OK '+JSON.stringify(audit()));
