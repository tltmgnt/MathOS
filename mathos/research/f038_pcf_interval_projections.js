// PCF-001 host semantic audit, not physical one-tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 let seed=0x50434601;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 let n={fixtures:0,orientations:0,projectedRoots:0,localKeys:0,pairTests:0,flags:0,flagChecks:0,treeNodes:0,fullNodes:0,fullTuples:0,models:0,correctionModels:0,extraModels:0,zeroRoots:0};
 const results=[];
 for(let m of [2,3,4])for(let mode=0;mode<3;mode++){
  n.fixtures++;let M=m===2?2:4,b=2;
  let supports=[[0,4,5],[0,1,4],[0,2,5],[1,2,3],[4,5],[0,3,4],[2,4,5],[6,7],[0,1,8],[5,6,8]];
  let F=supports.map((h,i)=>({h,S:new Set([...tup(m,h.length)].filter(z=>i===0?(mode===0?z[0]===z[2]:mode===1?(z[0]+z[1])%m===z[2]:(z[0]+z[1]+z[2])%2===0):(rand()>>>24)<20+12*mode).map(key))}));
  let valid=z=>z.every(a=>a<m),bad=(s,z)=>s.S.has(key(s.h.map(i=>z[i]))),projected=F.filter(s=>s.h.every(i=>i<6));
  let original=z=>valid(z)&&F.every(s=>!bad(s,z)),target=z=>(z[1]+2*z[2]+z[3]+1)%m,center=mode===2?()=>0:z=>z[0];
  let E=z=>valid(z)&&!bad(F[0],z)&&bad(F[0],[target(z),...z.slice(1)])&&!bad(F[0],[center(z),...z.slice(1)]);
  let point=z=>E(z)&&projected.every(s=>!bad(s,z));
  let expectedPoint=new Set();
  for(let z of tup(m,9))if(original(z)&&E(z.slice(0,6)))expectedPoint.add(key(z));
  for(let keep of [4,5]){
   n.orientations++;let drop=9-keep,idx=[0,1,2,3,keep],trees=new Map(),S=0,rawPoint=0;
   function construct(o){
    // Equivalent to per-key local fixed-tape scan, using host direct pair evaluation.
    let flags=new Set();
    for(let z of tup(b,4)){
     n.localKeys++;let a=z.map((v,i)=>v+o[i]);if(!valid(a))continue;
     let hits=new Set();
     for(let x=0;x<b;x++)for(let y=0;y<b;y++){
      let v=[...a,x+o[4],y+o[5]];n.pairTests++;
      if(point(v)){hits.add(v[keep]-o[keep]);rawPoint++;}
     }
     for(let v of hits)flags.add(key([...z,v]));
    }
    for(let q of tup(b,5)){
     let z=Array(6).fill(0);idx.forEach((g,i)=>z[g]=q[i]+o[g]);
     let truth=false;for(let y=0;y<b;y++){z[drop]=o[drop]+y;truth ||= point(z);}
     ok(flags.has(key(q))===truth,"exact flags");n.flagChecks++;
    }
    S+=flags.size;n.flags+=flags.size;if(!flags.size)n.zeroRoots++;
    function tree(o,t){
     n.treeNodes++;let positive=[...flags].some(k=>k.split(",").map(Number).every((v,i)=>v>=o[i]&&v<o[i]+t));
     let T={positive,ch:[]};if(positive&&t>1)for(let d of tup(2,5))T.ch.push(tree(o.map((v,i)=>v+d[i]*t/2),t/2));return T;
    }
    return {flags,T:tree(Array(5).fill(0),b)};
   }
   for(let q of tup(M/b,6)){n.projectedRoots++;trees.set(key(q),construct(q.map(v=>v*b)));}
   let got=new Set(),expected=new Set(),envelopeMass=0;
   for(let z of tup(M,6)){
    let q=z.map(v=>Math.floor(v/b)),u=idx.map(g=>z[g]%b);
    let member=trees.get(key(q)).flags.has(key(u));envelopeMass+=+member;
    ok(!point(z)||member,"point containment");
   }
   ok(envelopeMass===b*S&&rawPoint<=envelopeMass,"padded volume identity");
   for(let z of tup(m,9)){
    n.fullTuples++;if(!original(z))continue;
    let q=z.slice(0,6).map(v=>Math.floor(v/b)),u=idx.map(g=>z[g]%b);
    if(trees.get(key(q)).flags.has(key(u)))expected.add(key(z));
   }
   function go(T,o,t){
    n.fullNodes++;if(!T.positive)return;
    if(t===1){if(original(o))got.add(key(o));return;}
    for(let d of tup(2,9)){let j=idx.reduce((v,g)=>2*v+d[g],0);go(T.ch[j],o.map((v,g)=>v+d[g]*t/2),t/2);}
   }
   for(let q of tup(M/b,9))go(trees.get(key(q.slice(0,6))).T,q.map(v=>v*b),b);
   ok(got.size===expected.size&&[...got].every(v=>expected.has(v)),"exact envelope models");
   ok([...expectedPoint].every(v=>got.has(v)),"all actual correction models preserved");
   n.models+=got.size;n.correctionModels+=expectedPoint.size;n.extraModels+=got.size-expectedPoint.size;
   results.push([m,mode,keep,rawPoint,S,envelopeMass,got.size,expectedPoint.size]);
  }
 }
 // Field controls: compare distributed x escape against private escape (all projected pairs allowed by narrow constraints).
 let fields=[];
 for(let [m,poly,b,B] of [[16,19,4,4],[32,37,8,8],[64,67,8,16]]){
  function mul(a,b){let v=0;while(b){if(b&1)v^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return v;}
  let q=m/2,J=m/4,D=J*(m-J),P=Array.from({length:m*m},(_,i)=>i);
  for(let i=P.length-1;i>0;i--){let j=rand()%(i+1);[P[i],P[j]]=[P[j],P[i]];}
  let F=Array.from({length:m},(_,a)=>Uint8Array.from(P,i=>+( (mul(a,Math.floor(i/m))^(i%m))<J)));
  let raw=0,actual=0,S=[0,0],denseS=[0,0],pairs=0;
  for(let a=0;a<m;a++)for(let c=q;c<m;c++)if(a!==c){
   let loss=0;
   for(let x=0;x<m;x++)for(let y=0;y<m;y++){let e=+(!F[a][x*m+y]&&F[c][x*m+y]);loss+=e;if(x%B===0)actual+=e;}
   ok(loss===D,"field loss");raw+=loss;pairs++;
   for(let keep of [0,1])for(let v=0;v<m;v++)for(let o=0;o<m;o+=b){
    let hit=false,dense=false;
    for(let u=o;u<o+b;u++){let x=keep===0?v:u,y=keep===0?u:v,e=!F[a][x*m+y]&&F[c][x*m+y];dense ||= e;hit ||= e&&x%B===0;}
    S[keep]+=+hit;denseS[keep]+=+dense;
   }
  }
  let mult=m**3/q,weighted=S.map(v=>b*v*mult),denseWeighted=denseS.map(v=>b*v*mult);
  ok(weighted[0]<=m**6/B&&actual*mult<=Math.min(...weighted)&&denseWeighted.every((v,i)=>v>=weighted[i]),"asymmetric envelope bound");
  fields.push([m,b,B,pairs,raw*mult,actual*mult,...weighted,...denseWeighted]);
 }
 return {n,results,fields};
}
console.log('F038_PCF_INTERVAL_PROJECTIONS_OK '+JSON.stringify(audit()));
