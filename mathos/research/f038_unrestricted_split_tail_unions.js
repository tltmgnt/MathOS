// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},key=z=>z.join(","),G=[0,1,2,3,4,5,6,7,8];
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 let n={fixtures:0,passes:0,candidates:0,dominance:0,keyChecks:0,unionBits:0,full:0,success:0,heavy:0,head:0,tail:0,narrow:0,branchModels:0,headModels:0,localChecks:0,children:0,roots:0,greedyChecks:0},selected={};
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  n.fixtures++;let M=1;while(M<m)M*=2;
  let F=H.map(h=>({h,R:new Set([...tup(m,h.length)].filter(z=>{
   if(key(h)==="0,4,5"){if(mode===0)return false;if(mode===1)return z[0]===z[2]&&z[1]!==z[2];if(mode===2)return z[0]===1&&z[1]===z[2];if(mode===3)return z[0]===1&&z[1]===0;return (z[0]+z[1])%m===z[2];}
   if(key(h)==="0,6,7"&&mode===3)return z[0]===1&&z[1]!==z[2];
   if(key(h)==="0,1,4"&&mode===2)return z[0]===1&&z[1]===z[2];
   if(mode===4)return h.length===3&&(z[0]+z[1])%m===z[2];
   if(mode===5)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   if(mode===7)return h.length===2&&z[0]===z[1];return false;
  }).map(key))}));
  let wide=F.filter(s=>s.h[0]===0&&s.h.length===3&&s.h[1]>=4&&s.R.size),local=F.filter(s=>s.h.includes(0)),ctx=[...tup(m,3)],cols=[...tup(m,2)];
  const orig=z=>z.every(a=>a<m)&&F.every(s=>!s.R.has(key(proj(z,s.h))));
  const Z=(s,a,b,x,y)=>!s.R.has(key([a,x,y]))&&s.R.has(key([b,x,y]));
  const W=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>wide.reduce((v,s)=>v+cols.reduce((w,[x,y])=>w+Z(s,a,b,x,y),0),0)));
  function narrow(a,b,c){let v=0;for(let s of local){let O=s.h.filter(g=>g>=4);if(O.length===2)continue;for(let z of tup(m,O.length)){let x=s.h.map(g=>g===0?a:g<=3?c[g-1]:z[O.indexOf(g)]),y=x.slice();y[0]=b;if(!s.R.has(key(x))&&s.R.has(key(y)))v+=m**(2-O.length);}}return v;}
  for(let policy of [0,1,2]){
   n.passes++;let maps=new Map(),cap=0,dn=0;
   for(let c of ctx){let C=[],p=[];
    if(policy){let b=(c[0]+c[1]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow(a,b,c)+W[a][b])),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");n.greedyChecks++;if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self tie");
    }
    maps.set(key(c),{C,p});cap+=C.length;for(let a=0;a<m;a++)dn+=narrow(a,p[a],c);
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]];
   function evaluate(k,r){
    let heads=new Map(),keys=new Map(),coarse=0,fine=0,bad=0,union=0,head=0;
    function charge(a,top,f,scale){
     let low=Array.from({length:m},(_,b)=>b).filter(b=>f[b]&&!top.has(b)&&W[a][b]<=r),nl=low.reduce((s,b)=>s+f[b],0),nh=f.reduce((s,x,b)=>s+(!top.has(b)&&!low.includes(b)?x:0),0);
     let U=wide.map(s=>new Set(cols.filter(([x,y])=>low.some(b=>Z(s,a,b,x,y))).map(key))),v=U.reduce((s,x)=>s+x.size,0),use=v<=scale*nl;
     for(let i=0;i<wide.length;i++)for(let [x,y] of cols){ok(U[i].has(key([x,y]))===low.some(b=>Z(wide[i],a,b,x,y)),"union exact");n.unionBits++;}
     let heavy=nh+(use?0:nl);ok(scale*heavy+(use?v:0)===scale*nh+Math.min(scale*nl,v),"charge");n.keyChecks++;
     return {cost:scale*heavy+(use?v:0),heavy,v:use?v:0,low:new Set(use?low:[]),U:use?U:wide.map(()=>new Set())};
    }
    for(let a=0;a<m;a++)for(let d=0;d<m;d++){
     let f=Array(m).fill(0);for(let e=0;e<m;e++)for(let t=0;t<m;t++)f[get([a,d,e,t])]++;
     let top=new Set([...Array.from({length:m},(_,i)=>i).sort((i,j)=>f[j]-f[i]||i-j).slice(0,k),a]);
     heads.set(key([a,d]),top);for(let b of top)head+=f[b]*W[a][b];
     let p=charge(a,top,f,1),sum=0;
     for(let e=0;e<m;e++){let ff=Array(m).fill(0);for(let t=0;t<m;t++)ff[get([a,d,e,t])]++;
      let q=charge(a,top,ff,m);keys.set(key([a,d,e]),q);sum+=q.cost;bad+=q.heavy;union+=q.v;
     }
     ok(sum<=m*p.cost,"refinement monotonicity");n.dominance++;coarse+=p.cost;fine+=sum;
    }
    let Q=BigInt((cap+bad)*m*m+union*m+dn)+BigInt(k+1)**13n*BigInt(head);
    let old=BigInt((cap+coarse)*m*m+dn)+BigInt(k+1)**13n*BigInt(head);
    ok(Q<=old&&fine===m*bad+union,"score domination");n.candidates++;
    return {k,r,heads,keys,bad,union,head,Q};
   }
   let cand=[];for(let k of [0,1,2])for(let r of [0,1,10*m*m])cand.push(evaluate(k,r));
   let best=policy===0?cand.reduce((a,b)=>a.Q<=b.Q?a:b):evaluate(policy===1?0:1,policy===1?10*m*m:1);
   let tag=best.k+","+best.r;selected[tag]=(selected[tag]||0)+1;
   const info=z=>best.keys.get(key(z.slice(0,3))),route=z=>best.heads.get(key(z.slice(0,2))).has(get(z))?0:info(z).low.has(get(z))?1:2;
   let heavy=0,head=0;
   for(let c of ctx)for(let a=0;a<m;a++){let z=[a,...c],b=get(z);if(route(z)===2)heavy++;if(route(z)===0)head+=W[a][b];}
   ok(heavy===best.bad&&head===best.head,"score recount");
   let e=(i,z)=>route(z)===0&&Z(wide[i],z[0],get(z),z[wide[i].h[1]],z[wide[i].h[2]]);
   let u=(i,z)=>info(z).U[i].has(key([z[wide[i].h[1]],z[wide[i].h[2]]]));
   let exp=wide.map(()=>new Set());
   for(let z of tup(m,9)){n.full++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"rep");n.success++;}
    else if(route(z)===2)n.heavy++;
    else if(local.some(s=>s.h.filter(g=>g>=4).length<2&&!s.R.has(key(proj(z,s.h)))&&s.R.has(key(proj(y,s.h)))))n.narrow++;
    else if(route(z)===0){ok(wide.some((s,i)=>e(i,z)),"head recovery");n.head++;}
    else{ok(wide.some((s,i)=>u(i,z)),"union recovery");n.tail++;}
    for(let i=0;i<wide.length;i++){if(e(i,z))n.headModels++;if(u(i,z))exp[i].add(key(z));}
   }
   let raw=F.flatMap(s=>[...s.R].map(k=>({h:s.h,z:k.split(",").map(Number)})));for(let g of G)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
   for(let i=0;i<wide.length;i++){
    let P=[0,1,2,...wide[i].h.slice(1)],got=new Set();
    const predicate=z=>{if(z.some(a=>a>=m))return false;let full=Array(9).fill(0);P.forEach((g,j)=>full[g]=z[j]);return u(i,full);};
    // Build immutable five-coordinate positivity tree once per projected block.
    function tree(t,o){let A=[...tup(t,5)].filter(z=>predicate(z.map((a,j)=>a+o[j])));n.localChecks++;let ch=[];if(A.length&&t>1)for(let d of tup(2,5))ch.push(tree(t/2,o.map((a,j)=>a+d[j]*t/2)));return {flag:!!A.length,ch,active:false};}
    function visit(T,t,o,C){if(!T.flag)return;ok(!T.active,"exclusive frame");T.active=true;
     if(t===1){let pass=C.length===0;ok(pass===(orig(o)&&u(i,o)),"leaf");if(pass)got.add(key(o));}
     else for(let d of tup(2,9)){let v=t/2,off=d.map(a=>a*v),idx=P.reduce((s,g)=>2*s+d[g],0),L=C.map(r=>({h:r.h,z:r.z.map((a,j)=>a-off[r.h[j]])})).filter(r=>r.z.every(a=>a>=0&&a<v));n.children++;visit(T.ch[idx],v,o.map((a,j)=>a+off[j]),L);ok(!T.ch[idx].active,"reuse");}
     T.active=false;
    }
    let V=G.filter(g=>!P.includes(g));
    for(let q of tup(M/2,5)){let o=q.map(a=>a*2),T=tree(2,o);
     for(let v of tup(M/2,4)){let full=Array(9).fill(0);P.forEach((g,j)=>full[g]=o[j]);V.forEach((g,j)=>full[g]=v[j]*2);let C=raw.map(r=>({h:r.h,z:r.z.map((a,j)=>a-full[r.h[j]])})).filter(r=>r.z.every(a=>a>=0&&a<2));n.roots++;visit(T,2,full,C);}
    }
    ok(got.size===exp[i].size&&[...got].every(z=>exp[i].has(z)),"exact union models");n.branchModels+=got.size;
   }
  }
 }
 // Hash family: actual all-pair directed loss, diffuse labels, and one-vs-two retained score.
 let controls=[];
 for(let [d,poly] of [[3,11],[4,19],[5,37],[6,67]]){
  let m=2**d,J=m/4,loss=J*(m-J);
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  const bit=(a,x,y)=>(mul(a,x)^y)<J;
  let pairChecks=0;for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a!==b){let v=0;for(let x=0;x<m;x++)for(let y=0;y<m;y++)v+=!bit(a,x,y)&&bit(b,x,y);ok(v===loss,"field pair loss");pairChecks++;}
  let freq=Array(m).fill(0);for(let i=0;i<m;i++)freq[1+i%(m-1)]++;
  let old=0,newCost=0,heavy=0;
  for(let a=0;a<m;a++){
   let top=new Set([a]),nLow=0,targets=[];for(let b=1;b<m;b++)if(!top.has(b)){targets.push(b);nLow+=m*freq[b];}
   let v=0;for(let x=0;x<m;x++)for(let y=0;y<m;y++)v+=targets.some(b=>!bit(a,x,y)&&bit(b,x,y));
   ok(v===(m-1)*(m-J),"dense union");
   old+=Math.min(nLow,v);for(let b of targets)newCost+=freq[b]*Math.min(m,loss/m);heavy+=nLow;
  }
  // Here one retained key has m^2 assignments; two retained keys have m each.
  let expected=(m-1)*m; // distinct source-target pairs over a and varying second digit
  ok(newCost===expected*loss/m,"split normalization");
  let greedy=0;
  for(let target=1;target<m;target++){
   const D=(a,b)=>(a!==b?loss:0)+(a!==0&&b===0?m*m:0)+(a===target&&b!==target?m*m:0);
   let cost=Array.from({length:m},(_,b)=>Array.from({length:m},(_,a)=>D(a,b)).reduce((s,x)=>s+x,0));
   ok(cost.every((v,b)=>b===target||v>cost[target]),"unique first");
   for(let b=0;b<m;b++)if(b!==target){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,D(a,target)-D(a,b));ok(gain<m*m,"greedy stop");greedy++;}
  }
  controls.push([m,J,loss,pairChecks,old,newCost,heavy,greedy]);
 }
 ok(n.heavy>0&&n.tail>0&&n.head>0,"all routes exercised");
 return {n,selected,controls};
}
console.log('F038_SPLIT_TAIL_UNIONS_OK '+JSON.stringify(audit()));
