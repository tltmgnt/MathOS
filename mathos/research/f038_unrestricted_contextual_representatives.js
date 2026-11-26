// Semantic audit; not an original-tape simulator.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function select(m,R,g,h){
  let maps=[],sets=[],loss=0;
  for(let c=0;c<m;c++){
   let rows=Array.from({length:m},(_,a)=>{
    let r=[];for(let T of R)if(T.h.includes(g)){
     let P=T.h.filter(i=>i!==g&&i!==h);
     for(let x of tuples(m,P.length)){
      let z=T.h.map(i=>i===g?a:i===h?c:x[P.indexOf(i)]);
      r.push([+T.bad.has(key(z)),m**(2-P.length)]);
     }
    }return r;
   });
   let D=rows.map(a=>rows.map(b=>a.reduce((s,[x,w],i)=>s+(!x&&b[i][0]?w:0),0)));
   let res=Array(m).fill(37*m*m),map=Array(m).fill(-1),C=[],best=null;
   for(let k=1;k<=m;k++){
    let b=-1,v=Infinity;for(let j=0;j<m;j++)if(!C.includes(j)){
     let f=res.reduce((s,r,a)=>s+Math.min(r,D[a][j]),0);if(f<v){v=f;b=j;}
    }
    C.push(b);for(let a=0;a<m;a++)if(map[a]<0||D[a][b]<res[a]){res[a]=D[a][b];map[a]=b;}
    let score=k*m*m+v;if(!best||score<best.score)best={score,C:C.slice(),map:map.slice(),loss:v};
   }
   maps.push(best.map);sets.push(best.C);loss+=best.loss;
  }return {maps,sets,loss};
 }
 function check(m,R,g,h,{maps,sets,loss},fuse){
  let E=R.filter(T=>T.h.includes(g)).map(T=>{
   let P=[...new Set([...T.h,h])].sort((a,b)=>a-b),S=new Set();
   for(let z of tuples(m,P.length)){
    let a=z[P.indexOf(g)],c=z[P.indexOf(h)],x=T.h.map(i=>z[P.indexOf(i)]),y=T.h.map(i=>i===g?maps[c][a]:z[P.indexOf(i)]);
    if(!T.bad.has(key(x))&&T.bad.has(key(y)))S.add(key(z));
   }return {P,S};
  });
  let err=E.reduce((s,T)=>s+T.S.size*m**(4-T.P.length),0);if(loss!==undefined)need(err===loss,"weighted exception mass");
  let pass=z=>R.every(T=>!T.bad.has(key(proj(z,T.h))));
  let n=0,rep=0,exc=0,replaced=0,checks=0,overlap=0;
  for(let z of tuples(m,9)){checks++;if(!pass(z))continue;n++;let y=z.slice();y[g]=maps[z[h]][z[g]];
   let e=E.filter(T=>T.S.has(key(proj(z,T.P)))).length;
   need(pass(y)===(e===0),"exact failure characterization");
   if(sets[z[h]].includes(z[g]))rep++;
   if(e){exc++;if(e>1)overlap++;}else replaced++;
  }
  need(!n||rep||exc,"existence recovery");
  let tiles=0,localChecks=0,localModels=0;
  if(fuse){
   let T=E.find(T=>T.P.length===4&&T.S.size);
   if(T){
    let P=T.P,A=[...T.S].map(s=>s.split(",").map(Number)),rest=G.filter(g=>!P.includes(g)),seen=new Set();
    for(let i=0;i<A.length;i+=m){
     let chunk=A.slice(i,i+m),local=new Map();
     function emit(h,z){let k=key(h);if(!local.has(k))local.set(k,[h,new Set()]);local.get(k)[1].add(key(z));}
     for(let {h,bad} of R)for(let s of bad){
      let x=s.split(",").map(Number),plain=h.filter(g=>!P.includes(g)),inside=h.filter(g=>P.includes(g)),ids=plain.map(g=>1+rest.indexOf(g)),vals=plain.map(g=>x[h.indexOf(g)]);
      if(!inside.length)emit(ids,vals);else for(let j=0;j<chunk.length;j++)if(inside.every(g=>chunk[j][P.indexOf(g)]===x[h.indexOf(g)]))emit([0,...ids],[j,...vals]);
     }
     for(let a=chunk.length;a<m;a++)emit([0],[a]);
     tiles++;
     for(let z of tuples(m,6)){
      localChecks++;let ok=[...local.values()].every(([h,S])=>!S.has(key(proj(z,h))));
      if(z[0]>=chunk.length){need(!ok,"padding");continue;}
      let x=G.map(g=>P.includes(g)?chunk[z[0]][P.indexOf(g)]:z[1+rest.indexOf(g)]);
      need(ok===pass(x),"fused local equivalence");
      if(ok){need(!seen.has(key(x)),"disjoint chunks");seen.add(key(x));localModels++;}
     }
    }
    let expected=0;for(let z of tuples(m,9))if(pass(z)&&T.S.has(key(proj(z,P))))expected++;
    need(expected===seen.size,"complete exception branch");
   }
  }
  return [sets.reduce((s,C)=>s+C.length,0),err,n,rep,exc,replaced,overlap,checks,E.filter(T=>T.P.length===4&&T.S.size).length,tiles,localChecks,localModels];
 }
 let totals=Array(12).fill(0),forced=Array(12).fill(0),fixtures=0;
 for(let m of [2,3])for(let mode=0;mode<6;mode++){
  let R=H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===0;
   if(mode===2)return h.length===2&&h[1]===h[0]+1&&z[0]!==z[1];
   if(mode===3)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===4)return key(h)==="0,2,3"&&z[0]===1&&z[1]===z[2];
   return h.length===3&&z.some(a=>a!==0);
  }).map(key))}));
  let g=mode%2?0:8,h=mode%2?8:0;
  check(m,R,g,h,select(m,R,g,h),true).forEach((x,i)=>totals[i]+=x);
  check(m,R,0,8,{maps:Array.from({length:m},(_,c)=>Array(m).fill((c+1)%m)),sets:Array.from({length:m},(_,c)=>[(c+1)%m])},true).forEach((x,i)=>forced[i]+=x);
  fixtures++;
 }
 const par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 let controls=[];
 for(let q of [4,8,16,32]){
  let m=q-1,minG=Infinity,minH=Infinity,minJ=Infinity,n=0;
  for(let c=1;c<q;c++){
   let C=[0,1].map(v=>Array.from({length:m},(_,i)=>i+1).find(a=>par(a&c)===v));
   need(C.every(a=>a>0),"two conditional reps");
   for(let a=1;a<q;a++)for(let z=1;z<q;z++){need((par(a&c)^par(c&z))===(par(C[par(a&c)]&c)^par(c&z)),"zero loss");n++;}
  }
  for(let a=1;a<q;a++)for(let b=1;b<q;b++)if(a!==b){
   let x=0,y=0,j=0;
   for(let c=1;c<q;c++){
    j+=par(a&c)===0&&par(b&c)===1;
    for(let z=1;z<q;z++){
     x+=(par(a&c)^par(c&z))===0&&(par(b&c)^par(c&z))===1;
     y+=(par(c&a)^par(a&z))===0&&(par(c&b)^par(b&z))===1;
    }
   }
   minG=Math.min(minG,x);minH=Math.min(minH,y);minJ=Math.min(minJ,j*m);
  }
  need(minG>=q*(q-2)/4&&minH===q*(q-2)/4&&minJ===q*m/4,"directed separation");
  need(par(3&3)===0,"constant witness");
  controls.push([q,m,n,minG,minH,minJ]);
 }
 return {fixtures,totals,forced,controls};
}
console.log('F038_CONTEXTUAL_REPRESENTATIVES_OK '+JSON.stringify(audit()));
