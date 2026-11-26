// Host semantic audit; not physical tape execution.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)};
 let state=0x41f038a1;
 function rand(){state=(Math.imul(state,1664525)+1013904223)>>>0;return state;}
 function shuffle(n){let a=Array.from({length:n},(_,i)=>i);for(let i=n-1;i>0;i--){let j=rand()%(i+1);[a[i],a[j]]=[a[j],a[i]];}return a;}
 let checks={pair:0,triple:0,tripleDirect:0,greedyFirst:0,greedyStop:0,map:0,dag:0,run:0,union:0},fields=[],tiles=[],greedy=[];
 for(let [m,poly,B] of [[16,19,4],[32,37,8],[64,67,16]]){
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  let T=Array.from({length:m},(_,a)=>Array.from({length:m},(_,b)=>mul(a,b)));
  for(let a=1;a<m;a++)ok(new Set(T[a]).size===m,"field");
  let q=m/2,D=(m/4)*(3*m/4),best;
  for(let k=0;k<8;k++){
   let J=new Set(shuffle(m).slice(0,m/4)),min1=m*m,min0=m*m,counts=[];
   for(let l=2;l<m;l++){
    let v=0,w=0;for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(!J.has(a)&&J.has(b)){
     let c=T[1^l][a]^T[l][b];if(J.has(c))v++;else w++;
    }
    ok(v+w===D,"triple partition");checks.triple++;min1=Math.min(min1,v);min0=Math.min(min0,w);counts[l]=[v,w];
   }
   if(!best||Math.min(min1,min0)>Math.min(best.min1,best.min0))best={J,min1,min0,counts};
  }
  let {J,min1,min0,counts}=best,P=shuffle(m*m),raw=[];
  for(let a=0;a<m;a++)raw.push(Uint8Array.from(P,i=>+J.has(T[a][Math.floor(i/m)]^(i%m))));
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a!==b){
   let v=0,w=0;for(let i=0;i<m*m;i++){v+=!raw[a][i]&&raw[b][i];let x=Math.floor(i/m),y=i%m;w+=!J.has(T[a][x]^y)&&J.has(T[b][x]^y);}
   ok(v===D&&w===D,"permutation loss");checks.pair++;
  }
  for(let k=0;k<256;k++){
   let a=rand()%m,b=rand()%m,c=rand()%m;if(a===b||a===c||b===c)continue;
   let l=T[b^a].indexOf(c^a),v=0,w=0;
   for(let i=0;i<m*m;i++)if(!raw[a][i]&&raw[b][i]){if(raw[c][i])v++;else w++;}
   ok(v===counts[l][0]&&w===counts[l][1],"affine ratio");checks.tripleDirect++;
  }
  let union=0;
  for(let i=0;i<m*m;i++){let exists=raw.some(r=>r[i]);for(let a=0;a<m;a++)union+=exists&&!raw[a][i];checks.union++;}
  ok(union===(m-1)*m*(m-J.size),"union exact");
  fields.push([m,J.size,D,min1,min0,union]);
  let d=Math.log2(m),even=0,odd=0,worst=0;
  for(let j=0;j<d-1;j++)if(j%2)odd|=1<<j;else even|=1<<j;
  for(let f=q;f<m;f++){
   function loss(a,b){return (a===b?0:D)+m*m*(+(a>=q&&b<q)+ +((a&even)===(f&even)&&(b&even)!==(f&even))+ +((a&odd)===(f&odd)&&(b&odd)!==(f&odd)));}
   let sums=Array(m).fill(0);for(let b=0;b<m;b++)for(let a=0;a<m;a++)sums[b]+=loss(a,b);
   ok(sums.every((v,b)=>b===f||v>sums[f]),"unique first");checks.greedyFirst++;
   for(let b=0;b<m;b++)if(b!==f){let gain=0;for(let a=0;a<m;a++)gain+=Math.max(0,loss(a,f)-loss(a,b));ok(gain<=D&&gain<m*m,"second marginal");worst=Math.max(worst,gain);checks.greedyStop++;}
  }
  let targets=new Set();
  for(let c=0;c<B;c++)for(let e=0;e<B;e++){let f=q;for(let j=0;j<d-1;j++)f|=(((j%2?e:c)>>Math.floor(j/2))&1)<<j;targets.add(f);checks.map++;}
  ok(targets.size===q,"coarse target coverage");greedy.push([m,q,worst,targets.size]);
  for(let [ax,xx,yy] of [[0,0,0],[m-B,B,0],[0,m-B,m-B]]){
   let sets=Array.from({length:Math.log2(B)+1},()=>new Set());
   let sourceMin=Infinity,run=0,adjEqual=0,starts=0,rows=0;
   for(let a=ax;a<ax+B;a++){
    let roots=new Set();
    for(let b of targets)if(a!==b){
     let bits=[];for(let x=0;x<B;x++){let row="";for(let y=0;y<B;y++){let i=(xx+x)*m+yy+y;row+=+(!raw[a][i]&&raw[b][i]);}bits.push(row);}
     let str=bits.join("");if(str.includes("1"))roots.add(str);rows++;
     for(let x=0;x<B;x++){if(x&&bits[x]===bits[x-1])adjEqual++;for(let y=0;y<B;y+=2)starts+=bits[x].slice(y,y+2)==="01";}
     for(let j=0,t=1;t<=B;j++,t*=2)for(let x=0;x<B;x+=t)for(let y=0;y<B;y+=t){
      let s="";for(let u=0;u<t;u++)s+=bits[x+u].slice(y,y+t);
      if(s.includes("1"))sets[j].add(s);checks.dag++;
     }
    }
    sourceMin=Math.min(sourceMin,roots.size);
    for(let s of roots){let prev=null,w=1;for(let x=0;x<B;x++){let t=s.slice(x*B,(x+1)*B);if(t!==prev&&t.includes("1"))w+=1+(t.match(/1+/g)||[]).length;prev=t;}run+=w;checks.run++;}
   }
   let actual=sets.map(s=>s.size),sum=actual.reduce((a,b)=>a+b,0);
   ok(sum<=2*rows*B*B&&sourceMin<=q,"DAG bound");
   tiles.push([m,B,ax,xx,yy,rows,sourceMin,actual,sum,run,adjEqual,starts]);
  }
 }
 let asym=[];
 for(let d of [128,256,512,1024]){
  let b=Math.floor(2*d/3),p=1/Math.log2(d+2),s=Math.ceil(Math.log2(Math.sqrt(1024*d/(p*p)))),cap=4*b+d/32,dag=3*b+d-2*s-2;
  ok(s<b,"subsquare fits");asym.push([d,b,s,cap,dag,dag-cap]);
 }
 let urnChecks=0;
 for(let N=6;N<=10;N++)for(let K=2;K<=N-2;K++)for(let l=1;l<=2;l++){
  let total=0,none=0;
  function walk(A,k){if(!k){total++;if(A.every(v=>v>=K))none++;return;}for(let i=0;i<N;i++)if(!A.includes(i))walk([...A,i],k-1);}
  walk([],l);ok(none/total<=(1-K/N)**l+1e-12,"avoidance");urnChecks++;
  for(let first=0;first<N;first++)for(let wanted of [0,1]){
   let count=0;for(let i=0;i<N;i++)if(i!==first&&+(i<K)===wanted)count++;
   ok(count/(N-1)<=1-(Math.min(K,N-K)-1)/(N-1)+1e-12,"conditional bit");urnChecks++;
  }
 }
 return {checks,fields,greedy,tiles,asym,urnChecks};
}
console.log('F038_PERMUTED_FIELD_OBSTRUCTION_OK '+JSON.stringify(audit()));
