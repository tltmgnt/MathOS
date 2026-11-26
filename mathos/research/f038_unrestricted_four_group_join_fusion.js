// Standalone semantic regression, not a physical-tape implementation.
function audit(){
 const need=(x,msg)=>{if(!x)throw new Error(msg)};
 const G=Array.from({length:9},(_,i)=>i), H=[];
 for(let i=0;i<9;i++)H.push([i]);
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)H.push([i,j]);
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let k=j+1;k<9;k++)H.push([i,j,k]);
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const key=z=>z.join(","), sub=(h,g)=>h.every(x=>g.includes(x));
 function predicate(g,records){
  let by=new Map();for(let [h,z] of records){let k=key(h);if(!by.has(k))by.set(k,[h.map(x=>g.indexOf(x)),new Set()]);by.get(k)[1].add(key(z));}
  let a=[...by.values()];return z=>a.every(([ix,S])=>!S.has(key(ix.map(i=>z[i]))));
 }
 function control(m,mode,P){
  let out=[];
  for(let h of H)for(let z of tuples(m,h.length)){
   let hit=false;
   if(mode===1)hit=h.length===1&&h[0]===P[0];
   if(mode===2)hit=key(h)===key(P.slice(0,3))&&(z[0]+z[1])%m!==z[2];
   if(mode===3)hit=key(h)===key(P.slice(0,3))&&z[0]%2!==z[1]%2&&z[2]!==z[0]||
     key(h)===key([P[0],P[1],P[3]])&&z[0]%2===z[1]%2&&z[2]!==z[0];
   if(mode===4)hit=(h.reduce((s,g)=>s+g,0)+z.reduce((s,v,i)=>s+(i+2)*v,0))%7===0;
   if(mode===5)hit=h.length===3&&z.some(x=>x!==0);
   if(mode===6)hit=h.length===2&&((z[1]-z[0]+m)%m)>=m/4&&((z[1]-z[0]+m)%m)<m/2||
     key(h)==="0,1,2"&&z[0]%2!==z[1]%2&&z[2]!==z[0]||
     key(h)==="0,1,3"&&z[0]%2===z[1]%2&&z[2]!==z[0];
   if(hit)out.push([h,z]);
  }return out;
 }
 function* chunks(m,P,records,b,cap,stats){
  let p=predicate(P,records.filter(([h])=>sub(h,P))),batch=[],pending=[];
  function* flush(){for(let z of batch)if(p(z)){stats[1]++;pending.push(z);if(pending.length===b){yield pending;pending=[];}}batch=[];}
  for(let z of tuples(m,P.length)){stats[0]++;batch.push(z);if(batch.length===cap)yield* flush();}
  yield* flush();if(pending.length)yield pending;
 }
 function fixture(m,mode,P,b){
  let records=control(m,mode,P),rest=G.filter(g=>!P.includes(g)),r=rest.length+1,localG=Array.from({length:r},(_,i)=>i),stats=Array(9).fill(0);
  let orig=predicate(G,records),expected=new Set(),actual=new Set(),covered=new Set();
  for(let z of tuples(m,9))if(orig(z))expected.add(key(z));
  let ref=[...tuples(m,4)].filter(predicate(P,records.filter(([h])=>sub(h,P)))).map(key),got=[];
  for(let chunk of chunks(m,P,records,b,5,stats)){
   stats[2]++;got.push(...chunk.map(key));
   for(let block of tuples(Math.ceil(m/b),rest.length)){
    stats[3]++;let off=block.map(x=>x*b),local=[],counts=new Map();
    for(let [h,z] of records){
     let plain=h.filter(g=>!P.includes(g)),inside=h.filter(g=>P.includes(g)),vals=plain.map(g=>z[h.indexOf(g)]-off[rest.indexOf(g)]);
     if(vals.some(a=>a<0||a>=b))continue;
     let ids=plain.map(g=>1+rest.indexOf(g));
     let emit=(hh,zz)=>{local.push([hh,zz]);stats[4]++;let k=key(h)+":"+key(hh)+":"+key(zz);need(!counts.has(k),"per-support injection");counts.set(k,true);};
     if(!inside.length)emit(ids,vals);
     else for(let j=0;j<chunk.length;j++)if(inside.every(g=>chunk[j][P.indexOf(g)]===z[h.indexOf(g)]))emit([0,...ids],[j,...vals]);
    }
    for(let i=0;i<r;i++)for(let a=0;a<b;a++)if(i===0?a>=chunk.length:off[i-1]+a>=m){local.push([[i],[a]]);stats[5]++;}
    need(local.every(([h,z])=>h.length>=1&&h.length<=3&&new Set(h).size===h.length&&z.every(a=>a>=0&&a<b)),"width");
    let pass=predicate(localG,local);
    for(let z of tuples(b,r)){
     stats[6]++;let ok=pass(z);
     if(z[0]>=chunk.length||z.slice(1).some((a,i)=>a+off[i]>=m)){need(!ok,"padding");continue;}
     stats[7]++;let outer=G.map(g=>P.includes(g)?chunk[z[0]][P.indexOf(g)]:off[rest.indexOf(g)]+z[1+rest.indexOf(g)]),k=key(outer);
     need(!covered.has(k),"disjoint tiles");covered.add(k);need(ok===expected.has(k),"local equivalence");
     if(ok){actual.add(k);stats[8]++;}
    }
   }
  }
  need(got.join("|")===ref.join("|"),"stream order and completeness");
  need(covered.size===ref.length*m**5&&actual.size===expected.size&&[...actual].every(k=>expected.has(k)),"exact global model set");
  return [m,mode,b,records.length,expected.size,...stats];
 }
 let rows=[];
 for(let m of [2,3])for(let mode=0;mode<6;mode++)rows.push(fixture(m,mode,mode%2?[0,2,5,8]:[1,3,4,7],2));
 rows.push(fixture(3,3,[0,1,2,3],3));
 let dense=[];
 for(let m of [8,16,24]){
  let records=control(m,6,[0,1,2,3]),P=[0,1,2,3],rmin=Infinity,tmin=Infinity,fanout=m,supports=0,anti=0;
  for(let h of H){
   let pass=predicate(h,records.filter(([k])=>sub(k,h))),A=[...tuples(m,h.length)].filter(pass);
   if(h.length===2)rmin=Math.min(rmin,A.length);if(h.length===3)tmin=Math.min(tmin,A.length);
   for(let i=0;i<h.length;i++){
    need(new Set(A.map(z=>z[i])).size===m,"full support");supports+=m;
    let counts=new Map();for(let z of A){let k=key(z.filter((_,j)=>j!==i));counts.set(k,(counts.get(k)||0)+1);}
    fanout=Math.min(fanout,Math.max(...counts.values()));
   }
   if(h.length===2)for(let i=0;i<2;i++){
    let rr=Array.from({length:m},(_,a)=>key(A.filter(z=>z[i]===a).map(z=>z[1-i])));
    need(new Set(rr).size===m&&A.length===m*(m-m/4),"maximal pair conflict and forbidden degree");anti+=m*(m-1);
   }
  }
  let p=predicate(P,records.filter(([h])=>sub(h,P))),R=0;for(let z of tuples(m,4))if(p(z))R++;
  need(R<=m**3&&R>0&&rmin>=m*m/64&&tmin>=m**3/2048,"dense local sparse join");
  need(fanout>=Math.floor(m/16),"fanout");need(predicate(G,records)(Array(9).fill(0)),"zero witness");
  dense.push([m,records.length,rmin,tmin,R,fanout,supports,anti]);
 }
 const sums=rows.reduce((a,r)=>a.map((v,i)=>v+r[i+3]),Array(11).fill(0));
 for(let [p,q] of [[1,2],[1,4],[1,20]]){
  let N=3*q,D=3*q+p;
  need(3*q*D===N*(3*q+p),"balanced exponent");
  need(p<q&&N<D,"fixed block exponent");
 }
 return {fixtures:rows.length,sums,dense};
}
console.log('F038_FOUR_GROUP_JOIN_FUSION_OK '+JSON.stringify(audit()));
