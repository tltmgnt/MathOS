// F038-REX-022B1 — compiled ternary single-tape raw pool-shape and address cursor; not a normalized validator or SAT solver.
function compile({checkpoint=false}={}){
 const defs=new Map(),events=new Map(),add=(s,f)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,f);return s;};
 const r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0],stop=a=>z("HALT",a),bad=()=>stop(0);
 // Cleanup starts at the blank separating workspace from raw suffix.
 for(let v of [0,1]){
  add("clean"+v,a=>a===2?r("tail"+v,a):bad());
  add("tail"+v,a=>a===2?l("eraseTail"+v,a):r("tail"+v,a));
  add("eraseTail"+v,a=>a===2?l("eraseWork"+v,a):l("eraseTail"+v,2));
  add("eraseWork"+v,a=>a===2?(checkpoint?l("erasePrefix"+v,2):stop(v)):l("eraseWork"+v,2));
  if(checkpoint)add("erasePrefix"+v,a=>a===2?stop(v):l("erasePrefix"+v,2));
 }
 // Columns contain n,a,b,c; least significant column on the right.
 function scan(name,init,fn,finish,{readonly=false,extend=false}={}){
  const seen=new Set();
  function back(dest){const s=name+"Back"+dest;if(!defs.has(s))add(s,a=>a===2?z(dest,a):r(s,a));return s;}
  function state(acc,prefix){
   const s=name+"R"+acc+"_"+prefix;if(seen.has(s))return s;seen.add(s);
   add(s,a=>{
    if(a===2){
     if(prefix.length)return bad();
     let dest=finish(acc);
     if(extend&&acc===1){
      let e=name+"Ext";if(!defs.has(e+"1")){
       add(e+"1",a=>a===2?l(e+"2",0):bad());
       add(e+"2",a=>a===2?l(e+"3",0):bad());
       add(e+"3",a=>a===2?r(back(dest),1):bad());
      }return l(e+"1",0);
     }
     return r(back(dest),2);
    }
    if(prefix.length<3)return l(state(acc,prefix+a),a);
    let bits=[a,...prefix.split("").reverse().map(Number)],{out,next}=fn(acc,bits),dest=state(next,"");
    if(readonly)return l(dest,a);
    const t=name+"W"+next+"_"+out.join("");
    if(!defs.has(t+"1")){
     add(t+"1",a=>r(t+"2",out[1]));add(t+"2",a=>r(t+"3",out[2]));add(t+"3",a=>l(t+"B1",out[3]));
     add(t+"B1",a=>l(t+"B2",a));add(t+"B2",a=>l(t+"B3",a));add(t+"B3",a=>l(dest,a));
    }return r(t+"1",out[0]);
   });return s;
  }
  add(name,a=>a===2?l(state(init,""),a):bad());return name;
 }
 function inc(name,i,dest,extend=false){return scan(name,1,(carry,b)=>{let t=b[i]+carry;b[i]=t&1;return {out:b,next:t>>1};},c=>c&&!extend?"clean0":dest,{extend});}
 function copyPlus(name,src,dst,dest){return scan(name,1,(carry,b)=>{let t=b[src]+carry;b[dst]=t&1;return {out:b,next:t>>1};},c=>c?"clean0":dest);}
 function equal(name,i,yes,no){return scan(name,1,(eq,b)=>({out:b,next:+(eq&&b[0]===b[i])}),c=>c?yes:no,{readonly:true});}
 function set(name,k,dest){return scan(name,0,(j,b)=>{let vals=[0,1,k>=2?2:0,k===3?3:0];for(let i=1;i<4;i++)b[i]=(vals[i]>>j)&1;return {out:b,next:Math.min(2,j+1)};},()=>dest);}
 // Consume raw bit and shift workspace one cell right, preserving every work bit.
 function shift(name,dest,retained=2){
  add(name,a=>a===2?l(name+"Gap",2):bad());
  add(name+"Gap",a=>a===2?l(name+"Read",a):bad());
  add(name+"Read",a=>a===2?r(name+"Clear",retained):r(name+"Write"+a,a));
  for(let b of [0,1])add(name+"Write"+b,a=>l(name+"Skip",b));
  add(name+"Skip",a=>l(name+"Read",a));add(name+"Clear",a=>r(name+"Return",2));
  add(name+"Return",a=>a===2?z(dest,a):r(name+"Return",a));return name;
 }
 add("begin",a=>l("setupGap",a));add("setupGap",a=>a===2?l("setup3",2):bad());
 for(let i=3;i>=0;i--)add("setup"+i,a=>a===2?(i?l("setup"+(i-1),0):r("setupReturn",0)):bad());
 add("setupReturn",a=>a===2?z("h0",a):r("setupReturn",a));
 // h=0..30 exact count; h=31..49 represents 31+(n-31) mod 19.
 for(let h=0;h<50;h++){
  const next=h===49?31:h+1;inc("hInc"+h,0,"h"+next,true);shift("hShift"+h,"hInc"+h);
  add("h"+h,a=>a===2?r("hRaw"+h,a):bad());
  add("hRaw"+h,a=>a===1?z("hShift"+h,2):a===0&&h===31?z("headerEnd",2):l("clean0",a));
 }
 shift("headerEnd","init1");
 for(let k=1;k<=3;k++){
  set("init"+k,k,"read"+k+"s0");
  for(let s=0;s<(1<<k);s++){
   let name="read"+k+"s"+s,sh="shift"+k+"s"+s,dest=s+1<(1<<k)?"read"+k+"s"+(s+1):"advance"+k;
   events.set(name,{k,s});add(name,a=>a===2?r(name+"Raw",a):bad());
   add(name+"Raw",a=>a===2?l("clean0",a):z(checkpoint?sh+"v"+a:sh,2));
   if(checkpoint){shift(sh+"v0",dest,0);shift(sh+"v1",dest,1);}else shift(sh,dest);
  }
 }
 equal("advance1",1,"init2","inc1");inc("inc1",1,"read1s0");
 equal("advance2",2,"inc2a","inc2b");inc("inc2b",2,"read2s0");inc("inc2a",1,"test2a");
 equal("test2a",1,"init3","set2b");copyPlus("set2b",1,2,"read2s0");
 equal("advance3",3,"inc3b","inc3c");inc("inc3c",3,"read3s0");inc("inc3b",2,"test3b");
 equal("test3b",2,"inc3a","set3c");inc("inc3a",1,"set3b");copyPlus("set3b",1,2,"test3end");
 equal("test3end",2,"done","set3c");copyPlus("set3c",2,3,"read3s0");
 add("done",a=>a===2?r("doneRaw",a):bad());add("doneRaw",a=>l(a===2?(checkpoint?"checkpointDone":"clean1"):"clean0",a));
 if(checkpoint)add("checkpointDone",a=>a===2?stop(2):bad());
 const names=[],ids=new Map(),rows=[];
 function id(s){if(s==="HALT")return -1;if(!ids.has(s)){ids.set(s,names.length);names.push(s);}return ids.get(s);}
 id("begin");
 for(let i=0;i<names.length;i++){let f=defs.get(names[i]);if(!f)throw Error("missing "+names[i]);for(let a=0;a<3;a++){let [s,w,d]=f(a);rows.push([id(s),w,d]);}}
 let q=names.length,b=q.toString(2).length;for(let t of rows)if(t[0]===-1)t[0]=q;
 const desc="111"+"1".repeat(q)+"0"+rows.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,desc,names,checkpoint,events:[...events].map(([s,e])=>({state:ids.get(s),...e}))};
}
function decode(desc){
 if(!/^1111+0[01]+$/.test(desc))throw Error("descriptor grammar");
 let p=3;while(desc[p]==="1")p++;let q=p-3;p++;let b=q.toString(2).length;
 if(desc.length!==p+3*q*(b+4))throw Error("descriptor size");
 let T=new Int32Array(3*q);
 for(let i=0;i<T.length;i++){let s=parseInt(desc.slice(p,p+b),2),w=parseInt(desc.slice(p+b,p+b+2),2),d=parseInt(desc.slice(p+b+2,p+b+4),2);p+=b+4;
  if(s>q||w>2||d>2)throw Error("descriptor field");T[i]=(s<<4)|(w<<2)|d;}
 return {q,T};
}
function run(M,raw,limit=Infinity,observe=null){
 if(!/^[01]*$/.test(raw))throw Error("binary input required");
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("invalid limit");
 const origin=256,tape=new Uint8Array(raw.length+512);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=raw.charCodeAt(i)-48;
 const {q,T}=M;let state=0,head=origin,t=0,lo=head,hi=head;
 const event=observe?new Int16Array(q):null;
 if(event)for(let e of M.events)event[e.state]=16*e.k+e.s;
 while(state!==q&&t<limit){
  if(event&&event[state])observe(event[state]>>4,event[state]&15,tape,head-origin,origin);
  let v=T[3*state+tape[head]];tape[head]=(v>>2)&3;head+=(v&3)-1;state=v>>>4;t++;
  if(head<0||head>=tape.length)throw Error("simulation buffer");
  if(head<lo)lo=head;if(head>hi)hi=head;
 }
 let out=null,checkpoint=null;
 if(state===q){
  let nonblank=0;for(let a of tape)if(a!==2)nonblank++;
  if(M.checkpoint&&tape[head]===2){
   let vals=[0,0,0,0],scale=1,p=head-1;
   while(tape[p]!==2){for(let i=3;i>=0;i--){if(tape[p]>1)throw Error("checkpoint alignment");vals[i]+=scale*tape[p--];}scale*=2;}
   const workBits=head-p-1,end=p;let begin=end-1;while(tape[begin]!==2)begin--;begin++;
   let selector=Array.from(tape.subarray(begin,end)).join("");
   if(nonblank!==selector.length+workBits)throw Error("checkpoint garbage");
   checkpoint={n:vals[0],a:vals[1],b:vals[2],c:vals[3],workBits,selector,selectorStart:begin-origin,selectorEnd:end-origin};
  }else{if(nonblank!==1||tape[head]>1)throw Error("noncanonical output");out=tape[head];}
 }
 return {status:state!==q?"TIMEOUT":checkpoint?"POOL_CHECKPOINT":out?"POOL_SHAPE_OK":"OUTSIDE_POOL_SHAPE",t,span:hi-lo+1,head:head-origin,...(checkpoint?{checkpoint}:{})};
}
function audit(E){
 let C=compile(),M={...decode(C.desc),events:C.events},ok=(v,s)=>{if(!v)throw Error(s)};
 function check(raw,n,limit=Infinity){
  let oracle=E.pool(n),count=0;
  let r=run(M,raw,limit,(k,s,tape,h,origin)=>{
   const c=oracle.next();ok(!c.done&&c.value.length===k,"pool length");
   let values=[0,0,0,0],scale=1,pos=h+origin-1;
   while(tape[pos]!==2){for(let i=3;i>=0;i--){ok(tape[pos]<2,"aligned counter");values[i]+=scale*tape[pos--];}scale*=2;}
   ok(values[0]===n&&c.value.every((x,i)=>Math.abs(x)===values[i+1]&&+(x>0)===(s>>(k-1-i)&1)),"address disagreement "+count+" "+values+" "+c.value);
   ok(h+1===n+1+count&&tape[origin+h+1]===+raw[n+1+count],"raw cursor disagreement "+count+" "+h);
   count++;
  });
  if(r.status==="POOL_SHAPE_OK")ok(oracle.next().done&&count===raw.length-n-1,"incomplete pool");
  return {...r,count};
 }
 const results=[];
 for(let m of [2,3,4]){
  let pins=Array.from({length:m},(_,i)=>i%2),raw=E.encode(m,pins,[[-1],[-m-1,-2*m-1],[-1,-m-1,-2*m-1]]),n=19*m-7;
  let r=check(raw,n,300000000);ok(r.status==="POOL_SHAPE_OK","valid shape "+m+" "+JSON.stringify(r));results.push({m,n,L:raw.length,...r});
 }
 let raw=E.encode(2,[0,1],[]),n=31,controls=[];
 for(let [name,bad] of [["empty",""],["shortHeader","1110"],["wrongDimension","1".repeat(32)+"0"],["truncated",raw.slice(0,-1)],["extra",raw+"1"],["noTerminator","1".repeat(31)]]){
  let r=run(M,bad,300000000);ok(r.status==="OUTSIDE_POOL_SHAPE","malformed "+name+" "+JSON.stringify(r));controls.push({name,...r});
 }
 for(let limit of [0,1,100,10000,results[0].t-1]){let r=run(M,raw,limit);ok(r.status==="TIMEOUT"&&r.t===limit,"cutoff");}
 ok(run(M,raw,results[0].t).status==="POOL_SHAPE_OK","exact halt budget");
 let invalid=raw.slice(0,n+1)+"0".repeat(raw.length-n-1),r=run(M,invalid,300000000);
 ok(E.decode(invalid)===null&&r.status==="POOL_SHAPE_OK","scope boundary");
 return {q:C.q,descriptorBits:C.desc.length,results,controls,cutoffs:5,exactBudget:results[0].t,normalizationCounterexample:{L:invalid.length,...r},totals:results.reduce((a,r)=>({rawBits:a.rawBits+r.L,addresses:a.addresses+r.count,transitions:a.transitions+r.t}),{rawBits:0,addresses:0,transitions:0})};
}
function checkpointAudit(E){
 const C=compile({checkpoint:true}),M={...decode(C.desc),checkpoint:true},ok=(v,s)=>{if(!v)throw Error(s)},results=[];
 for(let m of [2,3,4]){
  let n=19*m-7,raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),[[-1],[-m-1,-2*m-1],[-1,-m-1,-2*m-1]]);
  let r=run(M,raw,300000000),p=r.checkpoint;
  ok(r.status==="POOL_CHECKPOINT"&&p.n===n&&p.selector===raw.slice(n+1)&&p.a===n-1&&p.b===n&&p.c===n&&p.workBits===4*n.toString(2).length,"checkpoint equality");
  ok(r.head===raw.length-1&&p.selectorEnd+p.workBits+1===r.head&&p.selectorEnd-p.selectorStart===p.selector.length,"checkpoint layout");
  results.push({m,n,L:raw.length,selectorBits:p.selector.length,t:r.t,span:r.span,workBits:p.workBits});
 }
 let n=31,raw=E.encode(2,[0,1],[]),invalid=raw.slice(0,n+1)+"0".repeat(raw.length-n-1),r=run(M,invalid,300000000);
 ok(E.decode(invalid)===null&&r.status==="POOL_CHECKPOINT"&&r.checkpoint.selector===invalid.slice(n+1),"shape-only negative control");
 let controls=[];
 for(let [name,bad] of [["empty",""],["wrongDimension","1".repeat(32)+"0"],["truncated",raw.slice(0,-1)],["extra",raw+"1"]]){
  let r=run(M,bad,300000000);ok(r.status==="OUTSIDE_POOL_SHAPE"&&!r.checkpoint,"checkpoint malformed "+name);controls.push({name,t:r.t});
 }
 let short=run(M,raw,results[0].t-1);ok(short.status==='TIMEOUT'&&short.t===results[0].t-1,'checkpoint one-step-short');
 ok(run(M,raw,results[0].t).status==='POOL_CHECKPOINT','checkpoint exact budget');
 return {q:C.q,descriptorBits:C.desc.length,results,controls,cutoffs:1,exactBudget:results[0].t,shapeOnlyControl:true,totals:results.reduce((a,r)=>({rawBits:a.rawBits+r.L,selectorBits:a.selectorBits+r.selectorBits,transitions:a.transitions+r.t}),{rawBits:0,selectorBits:0,transitions:0})};
}
module.exports={compile,decode,run,audit,checkpointAudit};
if(require.main===module){if(process.argv.includes('--descriptor'))process.stdout.write(compile({checkpoint:process.argv.includes('--checkpoint')}).desc);else if(process.argv.includes('--shape')){const C=compile();console.log(JSON.stringify(run(decode(C.desc),require('fs').readFileSync(0,'utf8'))));}else if(process.argv.includes('--checkpoint'))console.log('F038_REX_TERNARY_CHECKPOINT_OK '+JSON.stringify(checkpointAudit(require('./f038_tga_normalized_integration.js').engine())));else console.log('F038_REX_TERNARY_ADDRESS_OK '+JSON.stringify(audit(require('./f038_tga_normalized_integration.js').engine())));}
