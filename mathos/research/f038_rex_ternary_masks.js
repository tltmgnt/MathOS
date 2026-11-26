// F038-REX-022B3 — fixed ternary single-tape mask and pin deposition. Derived from REX-022B2.
function compile(){
 // Fixed finite-state compiler. Tape workspace: binary columns (M,Y,A,B,C)
 // followed by three fixed-width group words. M=m-1, Y=m-2 after header.
 const defs=new Map(),r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0];
 const add=(s,f)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,f);return s;};
 const bad=()=>z("BROKEN",0);
 const W=5,G=15;
 function walk(name,d,n,dest){if(!n)return dest;for(let i=n;i>0;i--)add(name+i,a=>a<2?(d===1?r:l)(i===1?dest:name+(i-1),a):bad());return name+n;}
 function back(name,dest){return add(name,a=>a===2?z(dest,a):r(name,a));}
 function fromSep(name,distance,dest){const st=walk(name+"W",-1,distance-1,dest);return add(name,a=>a===2?l(st,a):bad());}
 // Column transformations. Full column read uses at most 32 finite prefixes.
 function scan(name,init,fn,finish,{readonly=false,extend=false}={}){
  const seen=new Set(),returnState=new Map();
  function ret(dest){if(!returnState.has(dest))returnState.set(dest,back(name+"Back"+returnState.size,dest));return returnState.get(dest);}
  function state(acc,prefix){
   const s=name+"R"+acc+"_"+prefix;if(seen.has(s))return s;seen.add(s);
   add(s,a=>{
    if(a===2){
     if(prefix.length)return bad();
     const dest=finish(acc);
     if(extend&&acc===1){
      const e=name+"Ext";if(!defs.has(e+"1")){
       for(let i=1;i<W;i++)add(e+i,a=>a===2?(i===W-1?r(ret(dest),1):l(e+(i+1),0)):bad());
      }return l(e+"1",0);
     }
     return r(ret(dest),2);
    }
    if(prefix.length<W-1)return l(state(acc,prefix+a),a);
    let b=[a,...prefix.split("").reverse().map(Number)],{out,next}=fn(acc,b),dest=state(next,"");
    if(readonly)return l(dest,a);
    const t=name+"W"+next+"_"+out.join("");
    if(!defs.has(t+"1")){
     for(let i=1;i<W;i++)add(t+i,a=>i===W-1?l(t+"B1",out[i]):r(t+(i+1),out[i]));
     for(let i=1;i<W;i++)add(t+"B"+i,a=>l(i===W-1?dest:t+"B"+(i+1),a));
    }return r(t+"1",out[0]);
   });return s;
  }
  // Skip group words then enter least-significant column, from right to left.
  return fromSep(name,G+1,state(init,""));
 }
 function inc(name,i,dest,extend=false){return scan(name,1,(carry,b)=>{let t=b[i]+carry;b[i]=t&1;return{out:b,next:t>>1};},c=>c&&!extend?"BROKEN":dest,{extend});}
 function minus(name,src,dst,dest){return scan(name,1,(borrow,b)=>{let t=b[src]-borrow;b[dst]=t&1;return{out:b,next:+(t<0)};},c=>c?"BROKEN":dest);}
 function copy(name,src,dst,dest){return scan(name,0,(a,b)=>{b[dst]=b[src];return{out:b,next:0};},()=>dest);}
 function clear(name,i,dest){return scan(name,0,(a,b)=>{b[i]=0;return{out:b,next:0};},()=>dest);}
 function eq(name,i,j,yes,no){return scan(name,1,(a,b)=>({out:b,next:+(a&&b[i]===b[j])}),a=>a?yes:no,{readonly:true});}
 function constant(name,i,k,yes,no){return scan(name,0,(a,b)=>({out:b,next:a===2?2:b[i]!== (a===0?k:0)?2:1}),a=>a!==2?yes:no,{readonly:true});}
 function successor(name,i,j,yes,no){ // register i = register j + 1
  return scan(name,1,(a,b)=>{if(a===2)return{out:b,next:2};let t=b[j]+a;return{out:b,next:b[i]===(t&1)?t>>1:2};},a=>a===0?yes:no,{readonly:true});
 }
 // Read 5-bit group word (index 0 nearest the left end of group suffix).
 // Build fixed decision DAG; identical subtrees share states.
 function groupRead(name,i,choose){
  const dist=(2-i)*5+1,ret=new Map(),memo=new Map();let serial=0;
  function toSep(dest){if(!ret.has(dest))ret.set(dest,back(name+"Ret"+ret.size,dest));return ret.get(dest);}
  function tree(depth,v){
   if(depth===5)return toSep(choose(v));
   const a=tree(depth+1,v),b=tree(depth+1,v+(1<<depth)),key=depth+":"+a+":"+b;
   if(memo.has(key))return memo.get(key);
   const st=name+"D"+serial++;memo.set(key,st);add(st,x=>x===2?bad():l(x?b:a,x));return st;
  }
  return fromSep(name,dist,tree(0,0));
 }
 function groupSet(name,i,k,dest){
  let dist=(2-i)*5+1,ret=back(name+"Back",dest);
  for(let j=0;j<5;j++)add(name+"Bit"+j,a=>a<2?(j===4?r(ret,(k>>j)&1):l(name+"Bit"+(j+1),(k>>j)&1)):bad());
  return fromSep(name,dist,name+"Bit0");
 }
 function groupCopy(name,i,j,dest){
  return groupRead(name,i,k=>{if(k>20)return "BROKEN";let st=name+"Set"+k;if(!defs.has(st))groupSet(st,j,k,dest);return st;});
 }
 // Read all three group words, rightmost first; classify via a minimized decision DAG.
 function classify(name,k,choose){
  const memo=new Map(),ret=new Map();let serial=0;
  function toSep(dest){if(!ret.has(dest))ret.set(dest,back(name+"Ret"+ret.size,dest));return ret.get(dest);}
  const skip=(3-k)*5;
  function tree(depth,v){
   if(depth===5*k){let gs=[];for(let i=k-1;i>=0;i--)gs.push((v>>(5*i))&31);return toSep(gs.some(g=>g>20)?"BROKEN":choose(gs));}
   const a=tree(depth+1,v),b=tree(depth+1,v+(1<<depth)),key=depth+":"+a+":"+b;
   if(memo.has(key))return memo.get(key);
   const st=name+"D"+serial++;memo.set(key,st);add(st,x=>x===2?bad():l(x?b:a,x));return st;
  }
  return fromSep(name,skip+1,tree(0,0));
 }
 // Move workspace right one cell, optionally retain consumed selector bit.
 function shift(name,dest,retained=2){
  add(name,a=>a===2?l(name+"Gap",2):bad());
  add(name+"Gap",a=>a===2?l(name+"Read",a):bad());
  add(name+"Read",a=>a===2?r(name+"Clear",retained):r(name+"Write"+a,a));
  for(let b of [0,1])add(name+"Write"+b,a=>l(name+"Skip",b));
  add(name+"Skip",a=>l(name+"Read",a));add(name+"Clear",a=>r(name+"Return",2));
  add(name+"Return",a=>a===2?z(dest,a):r(name+"Return",a));return name;
 }
 // 50 blank-separated blocks, right-to-left: 49 mask tapes followed by pins.
 // Append at the left edge of the target, shifting the complete farther-left suffix.
 // The control counts separators; consecutive blanks are valid empty blocks.
 const BLOCKS=50,depCache=new Map();
 function deposit(target,bit,dest){
  const key=target+":"+bit+":"+dest;if(depCache.has(key))return depCache.get(key);
  const n="deposit"+depCache.size;depCache.set(key,n);
  add(n,a=>a===2?l(n+"Work",a):bad());
  add(n+"Work",a=>a===2?l(n+"Prefix",a):l(n+"Work",a));
  add(n+"Prefix",a=>a===2?l(n+"Seek0",a):l(n+"Prefix",a));
  for(let j=0;j<=target;j++)add(n+"Seek"+j,a=>a===2?(j===target?l(n+"Carry"+(BLOCKS-1-target)+"_2",bit):l(n+"Seek"+(j+1),a)):l(n+"Seek"+j,a));
  for(let j=0;j<=BLOCKS-1-target;j++)for(let carry=0;carry<3;carry++)add(n+"Carry"+j+"_"+carry,a=>{
   if(j===0)return a===2&&carry===2?r(n+"Return0",2):bad();
   return l(n+"Carry"+(j-(a===2?1:0))+"_"+a,carry);
  });
  for(let j=0;j<BLOCKS;j++)add(n+"Return"+j,a=>a===2?r(j===BLOCKS-1?n+"BackPrefix":n+"Return"+(j+1),a):r(n+"Return"+j,a));
  add(n+"BackPrefix",a=>a===2?r(n+"BackWork",a):r(n+"BackPrefix",a));
  add(n+"BackWork",a=>a===2?z(dest,a):r(n+"BackWork",a));
  return n;
 }
 const scopes=new Map();
 function covered(k,gs){
  if(gs.some((g,i)=>i&&g<=gs[i-1]))return "BROKEN";
  if(gs[gs.length-1]-gs[0]>2)return "bits"+k+"OutsideS0";
  const name="covered"+gs.join("_");
  if(!scopes.has(name)){const ids=[];for(let j=0;j<7;j++)if(gs.every(g=>g>=j&&g<=j+2))ids.push(7*j+gs.reduce((a,g)=>a|(1<<(g-j)),0)-1);
   if(!ids.length)throw Error("coverage");scopes.set(name,{k,ids});}
  return name;
 }
 // Rejection removes all tape content and writes 0 (malformed) or 1 (outside fixed path).
 for(let v of [0,1]){
  add("clean"+v,a=>a===2?r("tail"+v,a):bad());
  add("tail"+v,a=>a===2?l("eraseTail"+v,a):r("tail"+v,a));
  add("eraseTail"+v,a=>a===2?l("eraseWork"+v,a):l("eraseTail"+v,2));
  add("eraseWork"+v,a=>a===2?l("erasePrefix"+v,2):l("eraseWork"+v,2));
  add("erasePrefix"+v,a=>a===2?l("eraseMask"+v+"_0",2):l("erasePrefix"+v,2));
  for(let j=0;j<BLOCKS;j++)add("eraseMask"+v+"_"+j,a=>a===2?(j===BLOCKS-1?z("HALT",v):l("eraseMask"+v+"_"+(j+1),2)):l("eraseMask"+v+"_"+j,2));
 }
 add("BROKEN",a=>z("HALT",0)); // unreachable on well-formed internal layouts; audited by canonical halt.
 add("begin",a=>l("setupGap",a));add("setupGap",a=>a===2?l("setup"+(G+W-1),2):bad());
 for(let i=G+W-1;i>=0;i--)add("setup"+i,a=>a===2?(i?l("setup"+(i-1),0):r("setupReturn",0)):bad());
 back("setupReturn","h0");
 // n=19m-7: increment M on count 12,31,50,...; M=m until header end.
 for(let h=0;h<50;h++){
  const next=h===49?31:h+1,hit=next===12||next===31;
  if(hit)inc("hInc"+h,0,"h"+next,true);
  shift("hShift"+h,hit?"hInc"+h:"h"+next);
  add("h"+h,a=>a===2?r("hRaw"+h,a):bad());
  add("hRaw"+h,a=>a===1?z("hShift"+h,2):a===0&&h===31?z("headerEnd",2):l("clean0",a));
 }
 shift("headerEnd","makeM");minus("makeM",0,0,"makeY");minus("makeY",0,1,"class1");
 // Coordinate order: X0..X8 (m), Y0..Y8 (m-1), P (m), G1,G2 (1).
 function nextCoord(name,i,normal,overflow){
  const rank=2+i,groupEnd=name+"End",limitM=name+"M",limitY=name+"Y",incRank=name+"Rank";
  inc(incRank,rank,normal);eq(limitM,rank,0,groupEnd,incRank);eq(limitY,rank,1,groupEnd,incRank);
  groupRead(name,i,g=>g===20?overflow:g===19?groupEnd:g>=9&&g<=17?limitY:g>=0&&g<=18?limitM:"BROKEN");
  clear(groupEnd,rank,name+"Group");
  groupRead(name+"Group",i,g=>{if(g>=20)return "BROKEN";let st=name+"G"+g;if(!defs.has(st))groupSet(st,i,g+1,normal);return st;});
 }
 function copyCoord(name,i,j,dest){copy(name,2+i,2+j,name+"G");groupCopy(name+"G",i,j,dest);}
 // Width transitions reset a to (X0,0); b/c are initialized from their predecessor.
 function first(name,k,dest){
  clear(name,2,name+"G");groupSet(name+"G",0,0,k===1?dest:name+"B");
  if(k>=2){copyCoord(name+"B",0,1,name+"NB");nextCoord(name+"NB",1,k===2?dest:name+"C","BROKEN");}
  if(k===3){copyCoord(name+"C",1,2,name+"NC");nextCoord(name+"NC",2,dest,"BROKEN");}
 }
 nextCoord("advance1",0,"class1","init2");first("init2",2,"class2");
 nextCoord("advance2",1,"class2","adv2A");nextCoord("adv2A",0,"adv2Copy","BROKEN");copyCoord("adv2Copy",0,1,"adv2Next");nextCoord("adv2Next",1,"class2","init3");
 first("init3",3,"class3");nextCoord("advance3",2,"class3","adv3B");nextCoord("adv3B",1,"adv3CopyC","adv3A");
 copyCoord("adv3CopyC",1,2,"adv3NextC");nextCoord("adv3NextC",2,"class3","adv3A");
 nextCoord("adv3A",0,"adv3CopyB","BROKEN");copyCoord("adv3CopyB",0,1,"adv3NextB");nextCoord("adv3NextB",1,"adv3CopyC2","done");
 copyCoord("adv3CopyC2",1,2,"adv3NextC2");nextCoord("adv3NextC2",2,"class3","done");
 // Classification uses group identities then exact rank comparisons.
 const req=(k,s)=>"bits"+k+"Req"+s+"S0",none=k=>"bits"+k+"NoneS0",opt=(k,out)=>"bits"+k+(out?"Outside":"Optional")+"S0";
 classify("class1",1,([a])=>a<9?covered(1,[a]):a<=17?"oneY":a===18?none(1):req(1,0));
 eq("oneY",2,1,req(1,1),none(1));
 classify("class2",2,([a,b])=>{
  if(a<9&&b<9)return a===b?req(2,0):covered(2,[a,b]);
  if(a<9&&b===a+9)return "twoXY";
  if(a>=9&&a<=17&&a===b)return "twoYY";
  return none(2);
 });
 constant("twoXY",2,0,"twoXYzero","twoXYsucc");constant("twoXYzero",3,0,req(2,1),"twoXYsucc");
 successor("twoXYsucc",2,3,req(2,1),none(2));successor("twoYY",3,2,req(2,1),none(2));
 classify("class3",3,([a,b,c])=>{
  if(a<9&&b<9&&c<9&&a<b&&b<c)return covered(3,[a,b,c]);
  if(a<9&&a===b&&c===a+9)return "threeXXY";
  if(a<9&&b===a+9&&c===b)return "threeXYY";
  if(a===18&&b===19&&c===20)return "pinFirst";
  return none(3);
 });
 constant("threeXXY",2,0,"threeXXYb",none(3));constant("threeXXYb",3,1,"threeXXYc",none(3));constant("threeXXYc",4,0,req(3,6),none(3));
 successor("threeXYY",4,3,"threeXYYa",none(3));successor("threeXYYa",2,4,req(3,6),none(3));
 // Consume selector bits. The outside flag is a second finite-control bit.
 const expected=new Map();
 function bits(k,type,sreq){
  const stem="bits"+k+type;
  for(let s=0;s<2**k;s++){
   const name=stem+"S"+s,dest=s+1<2**k?stem+"S"+(s+1):"advance"+k;
   expected.set(name,{k,s,type,sreq});
   add(name,a=>a===2?r(name+"Raw",a):bad());
   add(name+"Raw",a=>{
    if(a===2)return l("clean0",a);
    const optional=(type==="Optional"||type==="Outside")&&s===0,need=type.startsWith("Req")&&s===sreq?1:0;
    if(!optional&&a!==need)return l("clean0",a);
    return z(name+"V"+a+(type==="Outside"&&optional&&a===1?"!":""),2);
   });
   for(let b of [0,1])shift(name+"V"+b,dest,b);
  }
 }
 for(let k=1;k<=3;k++){bits(k,"None",-1);bits(k,"Optional",-1);bits(k,"Outside",-1);}
 bits(1,"Req0",0);bits(1,"Req1",1);bits(2,"Req0",0);bits(2,"Req1",1);bits(3,"Req6",6);
 for(let [name,{k,ids}] of scopes){
  expected.set(name,{k,s:0,type:"Optional",sreq:-1});
  add(name,a=>a===2?r(name+"Raw",a):bad());
  const routes=[0,1].map(bit=>{let dest=name+"Consume"+bit;add(dest,a=>a===2?r(name+"Finish"+bit,a):bad());add(name+"Finish"+bit,a=>a===bit?z("bits"+k+"OptionalS0V"+bit,2):bad());for(let j=ids.length-1;j>=0;j--)dest=deposit(ids[j],bit,dest);return dest;});
  add(name+"Raw",a=>a===2?l("clean0",a):l(routes[a],a));
 }
 add("pinFirst",a=>a===2?r("pinFirstRaw",a):bad());
 const pinRoutes=[0,1].map(bit=>{let dest="pinConsume"+bit;add(dest,a=>a===2?r("pinFinish"+bit,a):bad());add("pinFinish"+bit,a=>a===bit?z("pinStart"+bit,2):bad());return deposit(49,1-bit,dest);});
 add("pinFirstRaw",a=>a===2?l("clean0",a):l(pinRoutes[a],a));
 for(let b of [0,1]){
  shift("pinStart"+b,"pin"+b+"S1",b);
  for(let s=1;s<8;s++){
   const name="pin"+b+"S"+s,need=s<4?b:1-b,dest=s===7?"advance3":"pin"+b+"S"+(s+1);
   expected.set(name,{k:3,s,type:"Pin",sreq:b});add(name,a=>a===2?r(name+"Raw",a):bad());
   add(name+"Raw",a=>a===need?z(name+"Shift",2):l("clean0",a));shift(name+"Shift",dest,need);
  }
 }
 expected.set("pinFirst",{k:3,s:0,type:"Pin",sreq:-1});
 add("done",a=>a===2?r("doneRaw",a):bad());
 add("doneRaw",a=>a===2?l("SUCCESS",a):l("clean0",a));
 add("SUCCESS",a=>a===2?z("HALT",2):bad());
 const names=[],ids=new Map(),rows=[];
 function id(s,flag){if(s==="HALT")return -1;const key=s+"|"+flag;if(!ids.has(key)){ids.set(key,names.length);names.push([s,flag]);}return ids.get(key);}
 id("begin",0);
 for(let i=0;i<names.length;i++){
  let [name,flag]=names[i],f=defs.get(name);if(!f)throw Error("missing "+name);
  for(let a=0;a<3;a++){
   let [s,w,d]=f(a),nf=flag;if(s.endsWith("!")){nf=1;s=s.slice(0,-1);}
   if(s==="SUCCESS"&&nf)s="clean1";
   rows.push([id(s,nf),w,d]);
  }
 }
 const q=names.length,b=q.toString(2).length;for(let t of rows)if(t[0]===-1)t[0]=q;
 const desc="111"+"1".repeat(q)+"0"+rows.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 const events=[];for(let i=0;i<q;i++){let [name,flag]=names[i];if(expected.has(name))events.push({state:i,flag,...expected.get(name)});}
 return{q,desc,events};
}
function decode(desc){
 if(!/^1111+0[01]+$/.test(desc))throw Error("descriptor grammar");
 let p=3;while(desc[p]==="1")p++;let q=p-3;p++;let b=q.toString(2).length;
 if(desc.length!==p+3*q*(b+4))throw Error("descriptor size");
 let T=new Uint32Array(3*q);
 for(let i=0;i<T.length;i++){let s=parseInt(desc.slice(p,p+b),2),w=parseInt(desc.slice(p+b,p+b+2),2),d=parseInt(desc.slice(p+b+2,p+b+4),2);p+=b+4;if(s>q||w>2||d>2)throw Error("descriptor field");T[i]=(s<<4)|(w<<2)|d;}
 return{q,T};
}
function run(M,raw,limit=Infinity,observe=null){
 if(!/^[01]*$/.test(raw))throw Error("binary raw required");
 if(limit!==Infinity&&(!Number.isSafeInteger(limit)||limit<0))throw Error("invalid limit");
 const origin=3*raw.length+512,tape=new Uint8Array(origin+raw.length+512);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=raw.charCodeAt(i)-48;
 let state=0,head=origin,t=0,lo=head,hi=head;const {q,T}=M;
 const event=observe?new Int32Array(q):null;if(event)for(let i=0;i<M.events.length;i++)event[M.events[i].state]=i+1;
 while(state!==q&&t<limit){
  if(event&&event[state])observe(M.events[event[state]-1],tape,head,origin);
  let v=T[3*state+tape[head]];tape[head]=(v>>2)&3;head+=(v&3)-1;state=v>>>4;t++;
  if(head<0||head>=tape.length)throw Error("simulation buffer");if(head<lo)lo=head;if(head>hi)hi=head;
 }
 if(state!==q)return{status:"TIMEOUT",t,span:hi-lo+1};
 let nonblank=0;for(let a of tape)if(a!==2)nonblank++;
 if(tape[head]<2){if(nonblank!==1)throw Error("noncanonical rejection head="+(head-origin)+" nonblank="+nonblank+" at "+t);return{status:tape[head]?"OUTSIDE_FIXED_PATH":"OUTSIDE_NORMALIZED",t,span:hi-lo+1};}
 let p=head-16,vals=[0,0,0,0,0],scale=1;
 while(tape[p]!==2){for(let i=4;i>=0;i--){if(tape[p]>1)throw Error("alignment");vals[i]+=scale*tape[p--];}scale*=2;}
 let end=p,start=p-1;while(tape[start]!==2)start--;start++;
 let selector=Array.from(tape.subarray(start,end)).join(""),workBits=head-end-1;
 const blocks=[];let at=start-1;
 for(let j=0;j<50;j++){if(tape[at]!==2)throw Error("block delimiter");at--;let bits=[];while(tape[at]!==2){bits.push(tape[at--]);if(at<0)throw Error("block buffer");}blocks.push(bits.join(""));}
 const maskBits=blocks.reduce((a,b)=>a+b.length,0);
 if(nonblank!==selector.length+workBits+maskBits)throw Error("checkpoint garbage");
 let groups=[];for(let i=0;i<3;i++){let g=0;for(let j=0;j<5;j++)g=2*g+tape[head-15+5*i+j];groups.push(g);}
 return{status:"MASKS_PREPARED",t,span:hi-lo+1,checkpoint:{m:vals[0]+1,rankBounds:vals.slice(0,2),ranks:vals.slice(2),groups,selector,workBits,selectorStart:start-origin,selectorEnd:end-origin,head:head-origin,masks:blocks.slice(0,49),pins:blocks[49],maskBits:maskBits-blocks[49].length,leftBoundary:at-origin}};
}

function audit(P,E,A){
 const C=compile(),M={...decode(C.desc),events:C.events},ok=(v,s)=>{if(!v)throw Error(s)};
 // Only the reference producer is instrumented; the physical machine never calls it.
 const src=P.producer.toString(),anchor='phase="output";';
 ok(src.includes(anchor),"reference probe anchor");
 const reference=new Function("return ("+src.replace(anchor,'return {...result("PREPARED"), masks:masks.flat().map(t=>t.cells.slice(1).join(""))};')+")")();
 function direct(m,raw){
  const masks=Array.from({length:49},()=>[]);let at=19*m-6,pins=[];
  for(let c of E.pool(19*m-7)){
   let bit=raw[at++],gs=c.map(x=>Math.floor((-x-1)/m));
   if(c.every(x=>x<0&&-x<=9*m)&&new Set(gs).size===c.length){
    for(let j=0;j<7;j++)if(gs.every(g=>g>=j&&g<=j+2))masks[7*j+gs.reduce((a,g)=>a|(1<<(g-j)),0)-1].push(bit);
   }
   let n=19*m-7;
   if(c.length===3&&c[0]>=n-m-1&&c[0]<=n-2&&c[1]===1-n&&c[2]===-n)pins.push(bit);
  }
  return {masks:masks.map(a=>a.join("")),pins:pins.join("")};
 }
 function serialize(m,masks){
  const w=Math.ceil(Math.log2(m));let o="";
  for(let j=0;j<7;j++){
   o+=j?"11110":"11111";
   for(let z of E.tup(m,3)){
    let allowed=true;for(let mask=1;mask<8;mask++){
     let rank=0;for(let i=0;i<3;i++)if(mask&(1<<i))rank=rank*m+z[i];
     if(masks[7*j+mask-1][rank]==="1")allowed=false;
    }
    if(allowed)o+="011"+z.map(x=>x.toString(2).padStart(w,"0").split("").map(b=>"00"+b).join("")+"010").join("")+"101";
   }
   o+="110";
  }
  return o+"010".repeat(7);
 }
 const rows=[],controls=[];let seed=0x52455823;const rnd=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 function fixture(m,mode){
  let B=[];for(let c of E.pool(19*m-7))if(c.every(x=>x<0&&-x<=9*m)){
   let gs=c.map(x=>Math.floor((-x-1)/m));
   if(new Set(gs).size!==c.length||gs[gs.length-1]-gs[0]>2)continue;
   if(mode===1&&c.length===1&&(-c[0]-1)%m!==m-1||mode===2||mode===3&&(rnd()>>>24)<101)B.push(c);
  }
  return B;
 }
 function check(m,mode,pins){
  const B=fixture(m,mode),raw=E.encode(m,pins,B),ref=reference(raw),oracle=direct(m,raw);
  const r=run(M,raw,3000000000),p=r.checkpoint;
  ok(r.status==="MASKS_PREPARED"&&ref.status==="PREPARED","prepare "+m+":"+mode+" "+JSON.stringify(r));
  ok(p.m===m&&p.selector===raw.slice(19*m-6)&&p.pins===pins.join("")&&p.pins===ref.pins&&p.pins===oracle.pins,"payload/pin mismatch");
  ok(p.masks.length===49&&p.masks.every((b,i)=>b===ref.masks[i]&&b===oracle.masks[i]),"mask differential "+m+":"+mode);
  const count=x=>((x&1)>0)+((x&2)>0)+((x&4)>0);
  ok(p.masks.every((b,i)=>b.length===m**count(i%7+1))&&p.maskBits===7*((m+1)**3-1),"mask lengths");
  ok(p.head===raw.length-1&&p.selectorEnd+p.workBits+1===p.head&&p.leftBoundary===p.selectorStart-1-50-p.maskBits-m,"layout");
  const prepared=serialize(m,p.masks),old=P.producer(raw);
  ok(old.status==="PREPARED"&&old.prepared===prepared&&old.pins===p.pins,"downstream serialization oracle");
  let ones=p.masks.reduce((a,b)=>a+b.split("1").length-1,0);
  rows.push({m,mode,pins:p.pins,L:raw.length,maskBits:p.maskBits,ones,selected:B.length,duplicateOnes:ones-B.length,preparedBits:prepared.length,t:r.t,span:r.span});
  return {raw,r,prepared};
 }
 for(let mode=0;mode<4;mode++)check(2,mode,[mode&1,(mode>>1)&1]);
 for(let m of [3,4])check(m,3,Array.from({length:m},(_,i)=>i%2));
 let forced=check(3,1,[1,0,1]);
 let raw=E.encode(2,[0,1],[]),n=31,pos=new Map(),at=n+1;for(let c of E.pool(n))pos.set(c.join(","),at++);
 const flip=(s,i)=>s.slice(0,i)+(s[i]==="1"?"0":"1")+s.slice(i+1);
 let wide=E.encode(2,[0,1],[[-1,-17]]),wide3=E.encode(2,[0,1],[[-1,-3,-17]]);
 for(let [name,bad,want] of [["empty","","OUTSIDE_NORMALIZED"],["header","1".repeat(32)+"0","OUTSIDE_NORMALIZED"],["earlyMandatory",flip(raw,pos.get("-31")),"OUTSIDE_NORMALIZED"],["latePin",flip(raw,pos.get("-28,-30,-31")),"OUTSIDE_NORMALIZED"],["truncated",raw.slice(0,-1),"OUTSIDE_NORMALIZED"],["extra",raw+"1","OUTSIDE_NORMALIZED"],["outside",wide,"OUTSIDE_FIXED_PATH"],["outsideTriple",wide3,"OUTSIDE_FIXED_PATH"],["outsideLateMalformed",flip(wide,pos.get("-28,-30,-31")),"OUTSIDE_NORMALIZED"]]){
  let r=run(M,bad,500000000);ok(r.status===want,"control "+name+" "+JSON.stringify(r));controls.push({name,status:r.status,t:r.t});
 }
 let clock=run(M,raw,500000000).t;
 for(let limit of [0,1,100,clock-1]){let r=run(M,raw,limit);ok(r.status==="TIMEOUT"&&r.t===limit,"cutoff "+limit);}
 ok(run(M,raw,clock).status==="MASKS_PREPARED","exact clock");
 // Worker input is reconstructed only by the host oracle; this is not same-machine handoff.
 const J=A.worker(),Q=A.compile(J.rules,J.symbols,J.projection),worker=A.physical(Q,forced.prepared,120000000);
 ok(worker.state===Q.q&&worker.tape.has(worker.head),"inherited worker replay");
 return {q:C.q,descriptorBits:C.desc.length,rows,controls,cutoffs:4,exactBudget:clock,workerTransitions:worker.t,totals:rows.reduce((a,r)=>({rawBits:a.rawBits+r.L,maskBits:a.maskBits+r.maskBits,pinBits:a.pinBits+r.pins.length,preparedBits:a.preparedBits+r.preparedBits,transitions:a.transitions+r.t,blocks:a.blocks+49}),{rawBits:0,maskBits:0,pinBits:0,preparedBits:0,transitions:0,blocks:0})};
}
module.exports={compile,decode,run,audit};
if(require.main===module){if(process.argv.includes('--descriptor'))process.stdout.write(compile().desc);else if(process.argv.includes('--produce'))console.log(JSON.stringify(run(decode(compile().desc),require('fs').readFileSync(0,'utf8'))));else console.log('F038_REX_TERNARY_MASKS_OK '+JSON.stringify(audit(require('./f038_rex_multitape_producer.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_nested_variable_overlap.js'))));}
