// Host semantic audit; no physical tape execution.
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)},key=z=>z.join(","),G=[0,1,2,3,4,5,6,7,8];
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 let n={fixtures:0,passes:0,scoreChecks:0,keyChecks:0,unionBitChecks:0,fullChecks:0,success:0,heavy:0,head:0,union:0,narrow:0,unionModels:0,headModels:0,localUnionChecks:0,localHeadChecks:0,children:0,roots:0,greedyChecks:0},selected={};
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
    if(policy){let b=(c[1]+c[2]+1)%m;C=[b];p=Array(m).fill(b);}
    else{let D=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>narrow(a,b,c)+W[a][b])),res=Array(m).fill(37*m*m),cur=Array(m).fill(-1),A=[],best;
     for(let k=1;k<=m;k++){let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!A.includes(j)){let u=res.reduce((s,x,a)=>s+Math.min(x,D[a][j]),0);if(u<v){v=u;b=j;}}A.push(b);for(let a=0;a<m;a++)if(cur[a]<0||D[a][b]<res[a]){cur[a]=b;res[a]=D[a][b];}ok(v===res.reduce((s,x)=>s+x,0),"greedy residual");n.greedyChecks++;if(!best||k*m*m+v<best.score)best={C:A.slice(),p:cur.slice(),score:k*m*m+v};}
     C=best.C;p=best.p;for(let a of C)p[a]=a;ok(best.score===C.length*m*m+p.reduce((s,b,a)=>s+D[a][b],0),"self tie");
    }
    maps.set(key(c),{C,p});cap+=C.length;for(let a=0;a<m;a++)dn+=narrow(a,p[a],c);
   }
   const get=z=>maps.get(key(z.slice(1,4))).p[z[0]];
   function evaluate(k,r){
    let keys=new Map(),bad=0,union=0,head=0;
    for(let a=0;a<m;a++)for(let h=0;h<m;h++){
     let f=Array(m).fill(0);for(let i=0;i<m;i++)for(let j=0;j<m;j++)f[get([a,h,i,j])]++;
     let top=new Set([...Array.from({length:m},(_,i)=>i).sort((i,j)=>f[j]-f[i]||i-j).slice(0,k),a]);
     let low=Array.from({length:m},(_,b)=>b).filter(b=>f[b]&&!top.has(b)&&W[a][b]<=r),lowMass=low.reduce((s,b)=>s+f[b],0);
     let U=wide.map(s=>new Set(cols.filter(([x,y])=>low.some(b=>Z(s,a,b,x,y))).map(key))),cost=U.reduce((s,x)=>s+x.size,0);
     let use=cost<=lowMass,heavy=0;
     for(let b=0;b<m;b++){if(top.has(b))head+=f[b]*W[a][b];else if(!use||!low.includes(b))heavy+=f[b];}
     bad+=heavy;if(use)union+=cost;else U=wide.map(()=>new Set());
     ok(heavy+(use?cost:0)===f.reduce((s,x,b)=>s+(!top.has(b)&&!low.includes(b)?x:0),0)+Math.min(cost,lowMass),"key score");n.keyChecks++;
     for(let i=0;i<wide.length;i++)for(let [x,y] of cols){ok(U[i].has(key([x,y]))===(use&&low.some(b=>Z(wide[i],a,b,x,y))),"exact union");n.unionBitChecks++;}
     keys.set(key([a,h]),{top,low:new Set(use?low:[]),U});
    }
    let Q=BigInt((cap+bad+union)*m*m+dn)+BigInt(k+1)**13n*BigInt(head);n.scoreChecks++;
    return {k,r,keys,bad,union,head,Q};
   }
   let cand=[];for(let k of [0,1,2])for(let r of [0,1,10*m*m])cand.push(evaluate(k,r));
   let best=policy===0?cand.reduce((a,b)=>a.Q<=b.Q?a:b):evaluate(policy===1?0:1,policy===1?10*m*m:1);
   if(!policy)ok(cand.every(c=>c.Q>=best.Q),"global minimum");
   let tag=best.k+","+best.r;selected[tag]=(selected[tag]||0)+1;
   const info=z=>best.keys.get(key(z.slice(0,2))),route=z=>{let q=info(z),b=get(z);return q.top.has(b)?0:q.low.has(b)?1:2;};
   let heavy=0,head=0;
   for(let c of ctx)for(let a=0;a<m;a++){let z=[a,...c],b=get(z);if(route(z)===2)heavy++;if(route(z)===0)head+=W[a][b];}
   ok(heavy===best.bad&&head===best.head,"score recount");
   let e=(i,z)=>route(z)===0&&Z(wide[i],z[0],get(z),z[wide[i].h[1]],z[wide[i].h[2]]);
   let u=(i,z)=>info(z).U[i].has(key([z[wide[i].h[1]],z[wide[i].h[2]]]));
   let exp=wide.map(()=>[new Set(),new Set()]);
   for(let z of tup(m,9)){n.fullChecks++;if(!orig(z))continue;let y=z.slice();y[0]=get(z);
    if(orig(y)){ok(maps.get(key(z.slice(1,4))).C.includes(y[0]),"rep");n.success++;}
    else if(route(z)===2)n.heavy++;
    else if(local.some(s=>s.h.filter(g=>g>=4).length<2&&!s.R.has(key(proj(z,s.h)))&&s.R.has(key(proj(y,s.h)))))n.narrow++;
    else if(route(z)===0){ok(wide.some((s,i)=>e(i,z)),"head recovery");n.head++;}
    else{ok(wide.some((s,i)=>u(i,z)),"union recovery");n.union++;}
    for(let i=0;i<wide.length;i++){if(e(i,z))exp[i][0].add(key(z));if(u(i,z))exp[i][1].add(key(z));}
   }
   let raw=F.flatMap(s=>[...s.R].map(k=>({h:s.h,z:k.split(",").map(Number)})));for(let g of G)for(let a=m;a<M;a++)raw.push({h:[g],z:[a]});
   for(let i=0;i<wide.length;i++)for(let typ of [0,1]){
    let P=typ===0?[0,1,2,3,...wide[i].h.slice(1)]:[0,1,...wide[i].h.slice(1)],got=new Set();
    const predicate=z=>{if(z.some(a=>a>=m))return false;let full=Array(9).fill(0);P.forEach((g,j)=>full[g]=z[j]);return typ===0?e(i,full):u(i,full);};
    function visit(t,o,A,C){let real=[...tup(t,P.length)].filter(z=>predicate(z.map((a,j)=>a+o[P[j]]))).map(key);
     ok(real.length===A.length&&A.every(z=>real.includes(key(z))),"exact local relation");
     n[typ===0?"localHeadChecks":"localUnionChecks"]++;if(!A.length)return;
     if(t===1){let pass=C.length===0;ok(pass===(orig(o)&&(typ===0?e(i,o):u(i,o))),"leaf");if(pass)got.add(key(o));return;}
     for(let d of tup(2,9)){let v=t/2,off=d.map(a=>a*v),D=A.map(z=>z.map((a,j)=>a-off[P[j]])).filter(z=>z.every(a=>a>=0&&a<v)),L=C.map(r=>({h:r.h,z:r.z.map((a,j)=>a-off[r.h[j]])})).filter(r=>r.z.every(a=>a>=0&&a<v));n.children++;visit(v,o.map((a,j)=>a+off[j]),D,L);}
    }
    for(let q of tup(M/2,9)){let o=q.map(a=>a*2),A=[...tup(2,P.length)].filter(z=>predicate(z.map((a,j)=>a+o[P[j]]))),C=raw.map(r=>({h:r.h,z:r.z.map((a,j)=>a-o[r.h[j]])})).filter(r=>r.z.every(a=>a>=0&&a<2));n.roots++;visit(2,o,A,C);}
    ok(got.size===exp[i][typ].size&&[...got].every(z=>exp[i][typ].has(z)),"exact branch models");n[typ===0?"headModels":"unionModels"]+=got.size;
   }
  }
 }
 // Exact per-key optimum can prefer a union even for diffuse labels, or envelope on a dense union.
 let controls=[];
 for(let m of [8,16,32,64]){
  let J=m/4,loss=m*J/4,counts=Array(m).fill(m),support=new Set(),a=1;
  const parity=x=>{let r=0;while(x){r^=x&1;x>>=1;}return r;};
  for(let b=1;b<m;b++)if(b!==a){let n=0;for(let u=0;u<m;u++)for(let v=0;v<J;v++)if(!parity(a&u)&&parity(b&u)){n++;support.add(key([u,v]));}ok(n===loss,"uniform pair loss");}
  ok(support.size===(m/2-1)*J,"union support");
  // Canonical facility greedy for the context-dependent allowed singleton.
  let checks=0;
  for(let target=1;target<m;target++){
   let D=Array.from({length:m},(_,x)=>Array.from({length:m},(_,b)=>(x!==0&&b===0?m*m:0)+(x===target&&b!==target?m*m:0)+(x===b||b===0?0:x===0?m*J/2:loss)));
   let sums=Array.from({length:m},(_,b)=>D.reduce((v,row)=>v+row[b],0));ok(sums.every((v,b)=>b===target||v>sums[target]),"first choice unique");checks++;
   for(let b=0;b<m;b++)if(b!==target){let gain=D.reduce((v,row)=>v+Math.max(0,row[target]-row[b]),0);ok(gain<m*m,"stop facility");checks++;}
  }
  // For every retained coordinate, each label occurs at most 2m times among m^2 contexts.
  let max=0;
  for(let h=0;h<3;h++)for(let v=0;v<m;v++){let f=Array(m).fill(0);for(let c of tup(m,3))if(c[h]===v)f[1+(c[0]+c[1])%(m-1)]++;max=Math.max(max,...f);ok(Math.max(...f)<=2*m,"diffuse conditional map");}
  controls.push([m,J,loss,support.size,max,checks]);
 }
 ok(n.heavy>0&&n.head>0&&n.union>0,"all wide routes");
 return {n,selected,controls};
}
console.log('F038_TAIL_UNION_RECOVERY_OK '+JSON.stringify(audit()));
