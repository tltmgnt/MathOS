// TGA-CPR-001 host audit, not a compiled solver.
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},key=z=>z.join(",");
 function* tup(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**(k-j-1))%m);}
 const bits=[...tup(2,5)],n={hierarchy:0,multiplicity:0,keys:0,tuples:0,models:0,rejected:0,flags:0,types:0,treeNodes:0,fullNodes:0};
 let hierarchy=[];
 for(let d=3;d<=6;d++){
  let X=[...tup(2,d)],F=X.filter(z=>z.reduce((a,b)=>a^b,0)===0),C=[];
  for(let k=1;k<=d;k++){
   let S=[...Array(1<<d).keys()].map(v=>Array.from({length:d},(_,i)=>i).filter(i=>v>>i&1)).filter(s=>s.length===k);
   let p=S.map(s=>new Set(F.map(z=>key(s.map(i=>z[i])))));
   let R=X.filter(z=>S.every((s,i)=>p[i].has(key(s.map(j=>z[j])))));
   ok(R.length===(k<d?X.length:F.length),"hierarchy");C.push(R.length);n.hierarchy+=X.length;
  }
  for(let z of X)ok(F.some(a=>z.every((v,i)=>v===a[i]))===(z.reduce((a,b)=>a^b,0)===0),"hidden binary encoding");
  hierarchy.push([d,...C]);
 }
 for(let m=2;m<=4;m++)for(let mask=0;mask<1<<m;mask++)for(let p of tup(m,m)){
  let A=Array.from({length:m},(_,a)=>a).filter(a=>mask>>a&1);
  let R=A.reduce((s,a)=>s+(a!==p[a]?7:0),0);
  ok(R===7*(A.length-A.filter(a=>a===p[a]).length),"multiplicity");
  if(p.every(b=>b===p[0]))ok(R===7*(A.length-+A.includes(p[0])),"singleton");n.multiplicity++;
 }
 function make(m,h,f){return {h,S:new Set([...tup(m,h.length)].filter(f).map(key))};}
 const bad=(s,z)=>s.S.has(key(s.h.map(g=>z[g])));
 function compile(m,F){
  let total=[0,0];for(let x=0;x<m;x++)for(let y=0;y<m;y++)total[(x^y)&1]++;
  let edges=[];
  for(let s of F){
   let v=s.h.filter(g=>g>=4),a=s.h.filter(g=>g<4);if(v.length!==2||a.length>1)continue;
   let cnt=Array.from({length:a.length?m:1},()=>[0,0]);
   for(let r of s.S){let z=r.split(",").map(Number);cnt[a.length?z[s.h.indexOf(a[0])]:0][(z[s.h.indexOf(v[0])]^z[s.h.indexOf(v[1])])&1]++;}
   let flags=cnt.map(c=>+(c[0]<total[0])+2*+(c[1]<total[1]));
   for(let h=0;h<flags.length;h++){
    let actual=0;
    for(let x=0;x<m;x++)for(let y=0;y<m;y++){
     let z=[];z[v[0]]=x;z[v[1]]=y;if(a.length)z[a[0]]=h;
     if(!bad(s,z))actual|=1<<((x^y)&1);
    }ok(flags[h]===actual,"edge flags");n.flags++;
   }
   edges.push({u:v[0]-4,v:v[1]-4,a:a.length?a[0]:-1,flags});
  }
  const pass=(z,skip=-1)=>bits.some(p=>edges.every(e=>e.u===skip||e.v===skip||(e.flags[e.a<0?0:z[e.a]]&(1<<(p[e.u]^p[e.v])))));
  let classes=[0,1,2,3].map(g=>{let C=new Map();for(let a=0;a<m;a++){let s=key(edges.filter(e=>e.a===g).map(e=>e.flags[a]));if(!C.has(s))C.set(s,[]);C.get(s).push(a);}return [...C.values()];}),count=0;
  for(let a of classes[0])for(let b of classes[1])for(let c of classes[2])for(let d of classes[3]){if(pass([a[0],b[0],c[0],d[0]]))count+=a.length*b.length*c.length*d.length;n.types++;}
  return {pass,count,edges};
 }
 let seed=0x54474120;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
 let random=[];
 for(let m of [2,3])for(let mode=0;mode<3;mode++){
  let F=[];for(let i=4;i<8;i++)F.push(make(m,[i,i+1],([x,y])=>((x^y)&1)===0));
  F.push(make(m,[0,4,8],([a,x,y])=>a%2===0&&((x^y)&1)===0));
  F.push(make(m,[1,5,7],([a,x,y])=>a%2===1&&((x^y)&1)===0));
  F.push(make(m,[0,1,3],()=> (rand()>>>24)<25+mode*15));
  F.push(make(m,[3,4,6],()=> (rand()>>>24)<40+mode*15));
  let {pass,count}=compile(m,F),trueKeys=0,expected=new Set(),c=0;
  for(let z of tup(m,4)){
   let truth=false;for(let v of tup(m,5)){let p=[...z,...v];n.tuples++;if(F.every(s=>!bad(s,p))){truth=true;expected.add(key(p));}}
   ok(!truth||pass(z),"no false negative");trueKeys+=+truth;n.keys++;c+=+pass(z);n.rejected+=+!pass(z);
  }
  ok(c===count,"type score");n.models+=expected.size;
  let M=m===2?2:4,b=2,roots=new Map(),got=new Set();
  for(let r of tup(M/b,4)){
   let origin=r.map(v=>v*b),flags=[...tup(b,4)].filter(z=>{let p=z.map((v,i)=>v+origin[i]);return p.every(v=>v<m)&&pass(p);});
   function tree(o,t){n.treeNodes++;let positive=flags.some(z=>z.every((v,i)=>v>=o[i]&&v<o[i]+t)),T={positive,ch:[]};if(positive&&t>1)for(let d of tup(2,4))T.ch.push(tree(o.map((v,i)=>v+d[i]*t/2),t/2));return T;}
   roots.set(key(r),tree([0,0,0,0],b));
  }
  function walk(T,o,t){n.fullNodes++;if(!T.positive)return;if(t===1){if(o.every(v=>v<m)&&F.every(s=>!bad(s,o)))got.add(key(o));return;}
   for(let d of tup(2,9)){let j=d.slice(0,4).reduce((v,a)=>2*v+a,0);walk(T.ch[j],o.map((v,i)=>v+d[i]*t/2),t/2);}}
  for(let r of tup(M/b,9))walk(roots.get(key(r.slice(0,4))),r.map(v=>v*b),b);
  ok(got.size===expected.size&&[...got].every(v=>expected.has(v)),"original search");random.push([m,mode,count,trueKeys,got.size]);
 }
 let cycle=[];
 for(let [m,poly] of [[8,11],[16,19],[32,37],[64,67]]){
  function mul(a,b){let r=0;while(b){if(b&1)r^=a;b>>=1;a<<=1;if(a&m)a^=poly;}return r;}
  let J=m/8,D=J*(m-J),P=Array.from({length:m*m},(_,i)=>i);
  for(let i=P.length-1;i>0;i--){let j=rand()%(i+1);[P[i],P[j]]=[P[j],P[i]];}
  let raw=Array.from({length:m},(_,a)=>Uint8Array.from(P,i=>+((mul(a,Math.floor(i/m))^(i%m))<J)));
  // All four fixed parity rectangles have an allowed pair for each row.
  let rect=0;for(let a=0;a<m;a++)for(let x=0;x<2;x++)for(let y=0;y<2;y++){
   let hit=false;for(let u=x;u<m;u+=2)for(let v=y;v<m;v+=2)hit ||= !raw[a][u*m+v];ok(hit,"actual parity rectangle");rect++;
  }
  let local=0,global=0;
  for(let a=0;a<m;a++){
   const test=skip=>bits.some(p=>[0,1,2,3,4].every(i=>{let j=(i+1)%5;return i===skip||j===skip||(i===4&&a<2)||p[i]!==p[j];}));
   ok(test(-1)===(a<2),"cycle");global+=+test(-1);for(let i=0;i<5;i++){ok(test(i),"proper subset");local++;}
  }
  let losses=Array.from({length:m},()=>Array(m).fill(0)),pairs=0;
  for(let a=0;a<m;a++)for(let b=0;b<m;b++)if(a!==b){
   let d=0;for(let i=0;i<m*m;i++)d+=!raw[a][i]&&raw[b][i];ok(d===D,"uniform pair");pairs++;
   losses[a][b]=d+(a<2&&b>=2?m*m/2:0);
  }
  let sums=Array.from({length:m},(_,b)=>losses.reduce((s,r)=>s+r[b],0));
  ok(sums[0]===sums[1]&&sums.slice(2).every(v=>v>sums[0]),"first good tie");
  for(let b=1;b<m;b++){let gain=losses.reduce((s,r)=>s+Math.max(0,r[0]-r[b]),0);ok(gain<=D&&gain<m*m,"second marginal");}
  let actual=0;for(let x=0;x<m;x++)for(let y=0;y<m;y++)if(((x^y)&1)===0&&!raw[1][x*m+y]&&raw[0][x*m+y])actual++;
  cycle.push([m,J,D,pairs,rect,local,global,D*(m-1)*m**3,D*m**3,actual*m**3]);
 }
 let clique=[],colorChecks=0;
 for(let m of [4,8,16]){
  let F=[];for(let i=4;i<=8;i++)for(let j=i+1;j<=8;j++)if(i===4&&j===8)F.push(make(m,[0,i,j],([a,x,y])=>a>=2&&x%4===y%4));else F.push(make(m,[i,j],([x,y])=>x%4===y%4));
  let {count}=compile(m,F);ok(count===m**4,"parity accepts all");
  let good=0,proper=0;
  for(let a=0;a<m;a++){
   const test=skip=>[...tup(4,5)].some(v=>F.every(s=>s.h.includes(skip)||!bad(s,[a,0,0,0,...v])));
   ok(test(-1)===(a<2),"clique exact");good+=+test(-1);for(let g=4;g<=8;g++){ok(test(g),"clique proper");proper++;}
  }clique.push([m,count,good*m**3,proper]);
 }
 for(let a=0;a<16;a++)for(let b=0;b<16;b++){
  let p=0;for(let x=0;x<4;x++)for(let y=0;y<4;y++)if(x!==y)p|=1<<((a>>x&1)^(b>>y&1));
  if(p!==3)ok((a===0||a===15)&&(b===0||b===15),"connected edge forces constants");colorChecks++;
 }
 return {n,hierarchy,random,cycle,clique,colorChecks};
}
console.log('F038_TGA_CONDITIONED_PARITY_OK '+JSON.stringify(audit()));
