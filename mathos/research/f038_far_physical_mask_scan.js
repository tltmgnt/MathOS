// FAR-002: physical transitions on prepared product-track blocks; no SAT or input-preparation claim.
function compile(){
 const width=4, symbols=[],codes=[];
 for(let s of ["_","0","1","E"])for(let m of ["_","L","R","0","1"])for(let o of ["_","0","1"]){symbols.push([s,m,o]);codes.push(symbols.length===1?"2222":(symbols.length-2).toString(3).padStart(width,"0"));}
 const index=(s,m,o)=>symbols.findIndex(v=>v[0]===s&&v[1]===m&&v[2]===o);
 const names=["start","scan0","scan1","back00","back01","back10","back11","carryL","carry0","carry1","carryR","rewind"];
 function logical(q,id){
  let [s,m,o]=symbols[id],same=(next,dir)=>[next,id,dir],put=(next,mm,oo,dir)=>[next,index(s,mm,oo),dir];
  if(q==="start"&&m==="L")return same("scan0",1);
  if(q.startsWith("scan")){
   let v=+q[4];
   if((m==="0"||m==="1")&&(s==="0"||s==="1"))return same("scan"+(v|(+m&+s)),1);
   if(m==="R")return same("back"+v+(s==="E"?1:0),-1);
  }
  if(q.startsWith("back")){
   if(m==="0"||m==="1")return same(q,-1);
   if(m==="L")return q[5]==="1"?put("HALT","L",q[4],0):put("carryL","_",q[4],1);
  }
  if(q==="carryL"||q==="carry0"||q==="carry1"){
   if(m==="0"||m==="1")return put("carry"+m,q.slice(5),o,1);
   if(m==="R")return put("carryR",q.slice(5),o,1);
  }
  if(q==="carryR"&&m==="_")return put("rewind","R",o,-1);
  if(q==="rewind"){
   if(m==="0"||m==="1")return same(q,-1);
   if(m==="L")return same("start",0);
  }
  return same("HALT",0);
 }
 // Compile a finite block interpreter into an actual transition table.
 const states=[],ids=new Map(),rows=[];
 function state(k){let s=JSON.stringify(k);if(!ids.has(s)){ids.set(s,states.length);states.push(k);}return ids.get(s);}
 state(["read","start",""]);
 const target=q=>q==="HALT"?-1:state(["read",q,""]);
 for(let i=0;i<states.length;i++){
  let k=states[i],r=[];
  for(let a=0;a<3;a++){
   if(k[0]==="read"){
    let p=k[2]+a;
    if(p.length<width)r.push([state(["read",k[1],p]),a,1]);
    else{let id=codes.indexOf(p);
     if(id<0)r.push([-1,a,0]);
     else{let [next,out,dir]=logical(k[1],id);r.push([state(["write",next,codes[out],dir,width-1]),a,0]);}
    }
   }else if(k[0]==="write"){
    let [,next,out,dir,j]=k;
    if(j)r.push([state(["write",next,out,dir,j-1]),+out[j],-1]);
    else r.push([dir===0?target(next):state(["move",next,dir,width-1]),+out[0],dir]);
   }else{
    let [,next,dir,left]=k;r.push([left===1?target(next):state(["move",next,dir,left-1]),a,dir]);
   }
  }rows.push(...r);
 }
 const q=states.length,T=rows.map(([a,w,d])=>[a<0?q:a,w,d]),b=q.toString(2).length;
 const desc="111"+"1".repeat(q)+"0"+T.map(([a,w,d])=>a.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc,width,codes,symbols,index,names};
}
function audit(){
 const ok=(v,s)=>{if(!v)throw Error(s)},M=compile(),{q,T,desc,width,codes,symbols,index}=M;
 // Decoder matching the repository's original binary machine description.
 let j=3;while(desc[j]==="1")j++;let count=j-3,b=count.toString(2).length;j++;
 ok(count===q&&desc.length-j===3*q*(b+4),"description length");
 for(let i=0;i<T.length;i++){let z=[parseInt(desc.slice(j,j+b),2),parseInt(desc.slice(j+b,j+b+2),2),parseInt(desc.slice(j+b+2,j+b+4),2)-1];ok(z.every((v,h)=>v===T[i][h]),"decode");j+=b+4;}
 function run(stream,mask,limit=Infinity){
  let n=stream.length,k=mask.length,W=n-k+1,tape=new Map();
  function write(i,s,m,o){let code=codes[index(s,m,o)];for(let h=0;h<width;h++)if(code[h]!=="2")tape.set(i*width+h,+code[h]);}
  write(-1,"1","R","1");write(n+2,"0","L","0");
  for(let i=0;i<=n+1;i++)write(i,i===0?"_":i===n+1?"E":stream[i-1],i===0?"L":i===k+1?"R":i<=k?mask[i-1]:"_","_");
  let head=0,state=0,steps=0,lo=0,hi=0;
  while(state!==q&&steps<limit){
   let [next,w,d]=T[3*state+(tape.get(head)??2)];
   if(w===2)tape.delete(head);else tape.set(head,w);
   head+=d;state=next;steps++;lo=Math.min(lo,head);hi=Math.max(hi,head);
  }
  function read(i){let s="";for(let h=0;h<width;h++)s+=tape.get(i*width+h)??2;let id=codes.indexOf(s);ok(id>=0,"block encoding");return symbols[id];}
  if(state!==q)return {halt:false,steps};
  let outputs="";
  for(let i=0;i<=n+1;i++){
   let [s,m,o]=read(i),expected=i===0?"_":i===n+1?"E":stream[i-1];
   ok(s===expected,"stationary input changed");
   let finalM=i===n-k?"L":i===n+1?"R":i>n-k&&i<=n?mask[i-(n-k)-1]:"_";
   ok(m===finalM,"mobile component wrong");
   if(i<W){let v=0;for(let a=0;a<k;a++)v|=(+mask[a]&+stream[i+a]);ok(o===String(v),"intersection");outputs+=o;}else ok(o==="_","output outside range");
  }
  ok(read(-1).join("")==="1R1"&&read(n+2).join("")==="0L0","external sentinels changed");
  ok([...tape.keys()].every(i=>i>=-width&&i<(n+3)*width),"out-of-bounds write");
  let logical=(2*W-1)*(2*k+3),expected=11*logical-3*W;
  ok(steps===expected&&head===(n-k)*width&&lo===0&&hi===(n+2)*width-1,"exact physical clock/head/span");
  return {halt:true,steps,logical,span:hi-lo+1,outputs};
 }
 let tests=0,transitions=0,windows=0,cutoffs=0;
 for(let n=1;n<=6;n++)for(let k=1;k<=n;k++)for(let a=0;a<2**n;a++)for(let c=0;c<2**k;c++){
  let stream=a.toString(2).padStart(n,"0"),mask=c.toString(2).padStart(k,"0"),r=run(stream,mask);tests++;transitions+=r.steps;windows+=n-k+1;
  if(a===0&&c===0){let t=run(stream,mask,r.steps-1);ok(!t.halt&&t.steps===r.steps-1,"short clock");cutoffs++;}
 }
 let scaling=[];
 for(let [n,k] of [[32,4],[64,4],[128,4],[64,8],[128,16],[256,32],[512,64]]){
  let stream=Array.from({length:n},(_,i)=>String((i*13+i*i+Math.floor(i/7))%2)).join(""),mask=Array.from({length:k},(_,i)=>String(+(i%3===0))).join("");
  let r=run(stream,mask);scaling.push([n,k,n-k+1,r.steps,r.logical,r.span]);
 }
 // Exact table validation, including all states, raw symbols, moves and destinations.
 let left=0,stay=0,right=0;
 for(let [a,w,d] of T){ok(Number.isInteger(a)&&a>=0&&a<=q&&[0,1,2].includes(w)&&[-1,0,1].includes(d),"transition range");if(d<0)left++;else if(d===0)stay++;else right++;}
 // Adversarial final alignment and internal blank physical cells: all-zero,
 // all-one, alternating masks, maximal window, and single-position window.
 let edge=[];
 for(let [n,k] of [[17,1],[17,17],[33,16],[65,32]])for(let mode=0;mode<3;mode++){
  let stream=Array.from({length:n},(_,i)=>String(mode===0?0:mode===1?1:i%2)).join(""),mask=Array.from({length:k},(_,i)=>String(mode===0?1:mode===1?0:(i+1)%2)).join("");
  let r=run(stream,mask);ok(!run(stream,mask,r.steps-1).halt,"edge exact clock");edge.push([n,k,mode,r.steps,r.outputs.split("1").length-1]);
 }
 return {states:q,descriptionBits:desc.length,blockWidth:width,alphabet:symbols.length,tests,transitions,windows,cutoffs,scaling,table:[left,stay,right],edge};
}
if(process.argv.includes('--description')) console.log(compile().desc); else console.log('F038_FAR_PHYSICAL_MASK_SCAN_OK '+JSON.stringify(audit()));
