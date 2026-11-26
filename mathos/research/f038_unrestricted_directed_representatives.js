// Semantic audit; not a physical tape implementation.
function audit(){
 const need=(x,s)=>{if(!x)throw Error(s)},G=[0,1,2,3,4,5,6,7,8],key=z=>z.join(",");
 function* sub(k,i=0,p=[]){if(p.length===k){yield p;return;}for(let g=i;g<=9-k+p.length;g++)yield* sub(k,g+1,p.concat(g));}
 function* tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const H=[...sub(1),...sub(2),...sub(3)],proj=(z,h)=>h.map(g=>z[g]);
 function select(m,g,R){
  let rows=Array.from({length:m},(_,a)=>{
   let r=[];for(let {h,bad} of R)if(h.includes(g))for(let z of tuples(m,h.length-1)){
    let x=z.slice();x.splice(h.indexOf(g),0,a);r.push([+bad.has(key(x)),m**(3-h.length)]);
   }return r;
  });
  let D=rows.map(a=>rows.map(b=>a.reduce((s,[x,w],i)=>s+(!x&&b[i][0]?w:0),0)));
  let loss=Array(m).fill(37*m*m),map=Array(m).fill(-1),centers=[],profile=[],best=null;
  for(let k=1;k<=m;k++){
   let next=-1,v=Infinity;
   for(let b=0;b<m;b++)if(!centers.includes(b)){
    let s=loss.reduce((s,d,a)=>s+Math.min(d,D[a][b]),0);
    if(s<v){v=s;next=b;}
   }
   centers.push(next);
   for(let a=0;a<m;a++)if(map[a]===-1||D[a][next]<loss[a]){loss[a]=D[a][next];map[a]=next;}
   let score=k*m*m+v;profile.push(v);
   need(v===loss.reduce((s,d)=>s+d,0),"loss");
   if(!best||score<best.score)best={centers:centers.slice(),map:map.slice(),loss:v,score};
  }
  for(let mask=1;mask<2**m;mask++){
   let C=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1);
   let opt=D.reduce((s,row)=>s+Math.min(...C.map(b=>row[b])),0);
   let prev=37*m**3;
   for(let v of profile){need(C.length*(prev-v)>=prev-opt,"greedy comparison");prev=v;}
  }
  return best;
 }
 let totals=Array(9).fill(0),forced=Array(3).fill(0),fixtures=0;
 for(let m of [2,3])for(let mode=0;mode<8;mode++){
  let R=H.map(h=>({h,bad:new Set([...tuples(m,h.length)].filter(z=>{
   if(mode===0)return false;
   if(mode===1)return h.length===1&&h[0]===0;
   if(mode===2)return h.length===2&&h[1]===h[0]+1&&z[0]!==z[1];
   if(mode===3)return h.length===3&&(h.reduce((s,g)=>s+g,0)+z.reduce((s,a,i)=>s+(i+2)*a,0))%5===0;
   if(mode===4)return h.length===3&&z.some(a=>a!==0);
   if(mode===5)return h.length===2&&z[0]===1&&z[1]===1;
   if(mode===6)return h.length===1&&z[0]!==h[0]%m;
   return h.includes(0)&&z[h.indexOf(0)]===1&&z.every(a=>a!==0);
  }).map(key))}));
  let cand=G.map(g=>({...select(m,g,R),g})).sort((a,b)=>a.score-b.score||a.g-b.g);
  function check({g,centers,map,loss}){
   let E=R.filter(T=>T.h.includes(g)).map(T=>{
    let i=T.h.indexOf(g),S=new Set();
    for(let z of tuples(m,T.h.length)){let x=z.slice();x[i]=map[z[i]];if(!T.bad.has(key(z))&&T.bad.has(key(x)))S.add(key(z));}
    return {h:T.h,S};
   });
   let err=E.reduce((s,T)=>s+T.S.size*m**(3-T.h.length),0);
   if(loss!==undefined)need(loss===err,"exact directed error");
   let pass=z=>R.every(T=>!T.bad.has(key(proj(z,T.h))));
   let models=0,repModels=0,exc=0,replaced=0,overlap=0,checks=0;
   for(let z of tuples(m,9)){
    checks++;if(!pass(z))continue;models++;
    let y=z.slice();y[g]=map[z[g]];
    let n=E.filter(T=>T.S.has(key(proj(z,T.h)))).length;
    need(pass(y)===(n===0),"replacement iff no exception");
    if(centers.includes(z[g]))repModels++;
    if(n){exc++;if(n>1)overlap++;}else replaced++;
   }
   need(!models||repModels||exc,"exact existence recovery");
   return [centers.length,err,models,repModels,exc,replaced,overlap,checks,E.filter(T=>T.S.size).length];
  }
  check(cand[0]).forEach((v,i)=>totals[i]+=v);fixtures++;
  let row=check({g:0,centers:[1],map:Array(m).fill(1)});
  [row[4],row[6],row[8]].forEach((v,i)=>forced[i]+=v);
 }
 const cyc=(i,j)=>j-i===1||i===0&&j===8,par=x=>{let p=0;while(x){p^=x&1;x>>=1;}return p;};
 function allow(q,i,j,a,b){
  if(!a||!b)return !cyc(i,j)||a===b;
  let x=(a-1)>>1,y=(b-1)>>1,ta=(a-1)&1,tb=(b-1)&1;
  return cyc(i,j)?ta!==tb&&x!==y:par(x&y)===0&&a!==b;
 }
 let controls=[];
 for(let q of [4,8,16,32,64]){
  let m=2*q+1,loss=0,maxLoss=0,minDist=m;
  for(let a=0;a<m;a++){
   let b=a?1+((a-1)&1):0,d=0;
   for(let j=1;j<9;j++)for(let c=0;c<m;c++)if(allow(q,0,j,a,c)&&!allow(q,0,j,b,c))d++;
   need(d<=8,"directed control");loss+=d*m;maxLoss=Math.max(maxLoss,d);
  }
  for(let x=0;x<q;x++)for(let y=x+1;y<q;y++){
   let a=1+2*x,b=1+2*y,n=0;for(let c=0;c<m;c++)n+=allow(q,0,2,a,c)!==allow(q,0,2,b,c);
   need(n>=q-2,"row separation");minDist=Math.min(minDist,n);
  }
  need(G.every(i=>G.slice(i+1).every(j=>allow(q,i,j,0,0))),"zero witness");
  controls.push([q,m,loss,maxLoss,minDist]);
 }
 // Dimension five gives 2^(5-2)>2^2, ensuring a vector outside the previous span.
 let linearChecks=0;
 for(let a=1;a<32;a++)for(let b=1;b<32;b++)if(a!==b)for(let u=0;u<4;u++){
  let found=false;for(let c=1;c<32;c++)if(c!==a&&c!==b&&c!==(a^b)&&par(a&c)===(u&1)&&par(b&c)===(u>>1)){found=true;break;}
  need(found,"independent extension");linearChecks++;
 }
 return {fixtures,totals,forced,controls,linearChecks};
}
console.log('F038_DIRECTED_REPRESENTATIVES_OK '+JSON.stringify(audit()));
