// REX-024B: exact physical width-three planner via bounded nine-vertex DFS.
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
 // 37 blank-separated blocks, right-to-left: 36 edge flags followed by pins.
 // Append at the left edge of the target, shifting the complete farther-left suffix.
 // The control counts separators; consecutive blanks are valid empty blocks.
 const BLOCKS=37,depCache=new Map();
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
 const edges=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)edges.push([i,j]);
 const edge=(i,j)=>edges.findIndex(([a,b])=>a===Math.min(i,j)&&b===Math.max(i,j));
 // The block is either empty or a single one. Query its first cell and
 // return to the workspace separator, even if it was empty.
 function queryBlock(n,target,yes,no){
  add(n,a=>a===2?l(n+"Work",a):bad());
  add(n+"Work",a=>a===2?l(n+"Prefix",a):l(n+"Work",a));
  add(n+"Prefix",a=>a===2?l(n+"Seek0",a):l(n+"Prefix",a));
  for(let j=0;j<target;j++)add(n+"Seek"+j,a=>a===2?l(n+"Seek"+(j+1),a):l(n+"Seek"+j,a));
  function ret(tag,dest){
   for(let j=target;j>=0;j--)add(tag+j,a=>a===2?r(j===0?tag+"Prefix":tag+(j-1),a):r(tag+j,a));
   add(tag+"Prefix",a=>a===2?r(tag+"Work",a):r(tag+"Prefix",a));back(tag+"Work",dest);return tag+target;
  }
  const y=ret(n+"Y",yes),n0=ret(n+"N",no);
  add(n+"Seek"+target,a=>a===2?r(n0,a):a===1?r(y,a):bad());return n;
 }
 let serialEdge=0;
 function setEdge(target,dest){const n="edgeSet"+serialEdge++;return queryBlock(n,target,dest,deposit(target,1,dest));}
 const scopes=new Map();
 function covered(k,gs){
  if(gs.some((g,i)=>i&&g<=gs[i-1]))return "BROKEN";
  if(k===1)return "bits1OptionalS0";
  const name="covered"+gs.join("_");
  if(!scopes.has(name)){const ids=[];for(let i=0;i<k;i++)for(let j=i+1;j<k;j++)ids.push(edge(gs[i],gs[j]));scopes.set(name,{k,ids});}
  return name;
 }
 // Inherited normalization rejection cleanup. Only malformed status 0 is reachable;
 // the former fixed-path flag is never set by the new scope dispatch.
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
  const routes=[0,1].map(bit=>{let dest=name+"Consume"+bit;add(dest,a=>a===2?r(name+"Finish"+bit,a):bad());add(name+"Finish"+bit,a=>a===bit?z("bits"+k+"OptionalS0V"+bit,2):bad());if(bit)for(let j=ids.length-1;j>=0;j--)dest=setEdge(ids[j],dest);return dest;});
  add(name+"Raw",a=>a===2?l("clean0",a):l(routes[a],a));
 }
 add("pinFirst",a=>a===2?r("pinFirstRaw",a):bad());
 const pinRoutes=[0,1].map(bit=>{let dest="pinConsume"+bit;add(dest,a=>a===2?r("pinFinish"+bit,a):bad());add("pinFinish"+bit,a=>a===bit?z("pinStart"+bit,2):bad());return deposit(36,1-bit,dest);});
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
 add("SUCCESS",a=>a===2?z("graphCopy0",2):bad());
 // Physical workspace to the right of the separator:
 // 60-bit blank-separated DFS frames (graph, active, tried, choice, root, status).
 // Original edge blocks and pin data are preserved to the left.
 function emit(name,word,dest){
  add(name,a=>a===2?r(name+"Seek",a):bad());
  add(name+"Seek",a=>a===2?z(name+"W0",a):r(name+"Seek",a));
  for(let i=0;i<word.length;i++)add(name+"W"+i,a=>a===2?(i===word.length-1?l(name+"Back",+word[i]):r(name+"W"+(i+1),+word[i])):bad());
  add(name+"Back",a=>a===2?z(dest,a):l(name+"Back",a));return name;
 }
 for(let i=0;i<36;i++){
  const next=i===35?"activeInit":"graphCopy"+(i+1);
  emit("graphOne"+i,"1",next);emit("graphZero"+i,"0",next);
  queryBlock("graphCopy"+i,i,"graphOne"+i,"graphZero"+i);
 }
 emit("activeInit","111111111"+"0".repeat(9)+"1001"+"10","search0_0");
 // Addressed reads and writes are compiled into fixed unit-move paths.
 // They return left to the same separator; no runtime index supplied.
 function readAt(n,i,yes,no){
  const at=n+"At",step=walk(n+"Walk",1,i,at);
  add(n,a=>a===2?r(step,a):bad());
  for(let [b,d] of [[0,no],[1,yes]])add(n+"Back"+b,a=>a===2?z(d,a):l(n+"Back"+b,a));
  add(at,a=>a===2?bad():l(n+"Back"+a,a));return n;
 }
 function writeAt(n,i,b,dest){
  const at=n+"At",step=walk(n+"Walk",1,i,at);
  add(n,a=>a===2?r(step,a):bad());
  add(at,a=>a===2?bad():l(n+"Back",b));
  add(n+"Back",a=>a===2?z(dest,a):l(n+"Back",a));return n;
 }
 const bin=x=>x.toString(2).padStart(4,"0");

 // All DFS frames have 60 bits; adjacent frame separators differ by 61.
 // The machine head is on the separator immediately left of the current frame.
 const F=60,D=F+1;
 function cross(n,d,k,dest){
  if(!k)return dest;
  for(let j=k;j>0;j--)add(n+j,a=>(d===1?r:l)(j===1?dest:n+(j-1),a));
  return n+k;
 }
 function move(n,d,k,dest){const st=cross(n+"Walk",d,k,dest);return add(n,a=>a===2?z(st,a):bad());}
 function writeChoice(v,dest){let n="choose"+v,word=bin(v);for(let j=3;j>=0;j--)dest=writeAt(n+"Bit"+j,54+j,+word[j],dest);return writeAt(n,45+v,1,dest);}
 function next(v){return v===8?"exhausted":"search"+(v+1)+"_1";}
 // Exhaust all eligible vertices; the tried bitmap persists across failed children.
 const seen=new Set();
 function degree(v,i,k){
  if(i===9)return "choose"+v;
  if(i===v)return degree(v,i+1,k);
  let n="degree"+v+"_"+i+"_"+k;if(seen.has(n))return n;seen.add(n);
  return readAt(n,edge(v,i),k===3?next(v):degree(v,i+1,k+1),degree(v,i+1,k));
 }
 for(let v=0;v<9;v++){
  writeChoice(v,"push");
  readAt("tried"+v,45+v,next(v),degree(v,0,0));
  for(let found of [0,1])readAt("search"+v+"_"+found,36+v,"tried"+v,v===8?(found?"exhausted":"succeeded"):"search"+(v+1)+"_"+found);
 }
 // Push: initialize an empty child frame then copy the original graph
 // and active mask from the parent. Only fixed-length physical walks.
 move("push",1,D,"initChild");emit("initChild","0".repeat(54)+"1001"+"00","returnParent");
 move("returnParent",-1,D,"copy0");
 for(let i=0;i<45;i++){
  const n="copy"+i,dest=i===44?"dispatchChoice":"copy"+(i+1);
  for(let b of [0,1]){
   const tag=n+"Write"+b,offset=D+i+1;
   const back=cross(tag+"Back",-1,offset-1,dest),to=cross(tag+"To",1,offset,tag+"At");
   add(tag,a=>a===2?z(to,a):bad());add(tag+"At",a=>a<2?l(back,b):bad());
  }
  readAt(n,i,n+"Write1",n+"Write0");
 }
 // Read stored parent choice; dispatch its child's fill and deletion.
 function dispatch(p=""){
  if(p.length===4){let v=parseInt(p,2);return v<9?"enter"+v:"BROKEN";}
  return readAt("choiceRead"+p,54+p.length,dispatch(p+"1"),dispatch(p+"0"));
 }
 add("dispatchChoice",a=>a===2?z("choiceRead",a):bad());dispatch();
 for(let v=0;v<9;v++){
  let dest="search0_0";
  for(let u=8;u>=0;u--)if(u!==v)dest=writeAt("delete"+v+"_"+u,edge(v,u),0,dest);
  dest=writeAt("deactivate"+v,36+v,0,dest);
  // Add every missing edge between two current neighbors of v.
  // Incident edges are unchanged until all fill checks finish.
  for(let a=8;a>=0;a--)for(let b=8;b>a;b--)if(a!==v&&b!==v){
   let n="fill"+v+"_"+a+"_"+b,put=writeAt(n+"Put",edge(a,b),1,dest);
   readAt(n+"Second",edge(v,b),put,dest);dest=readAt(n,edge(v,a),n+"Second",dest);
  }
  move("enter"+v,1,D,dest);
 }
 // Failed child: erase exactly its frame, including tried/choice fields,
 // then restore parent separator. Root failure is a structural refusal.
 readAt("exhausted",58,"planHalt","pop");
 add("pop",a=>a===2?r("popErase0",a):bad());
 for(let i=0;i<F;i++)add("popErase"+i,a=>a<2?(i===F-1?l("popReturn",2):r("popErase"+(i+1),2)):bad());
 const popBack=cross("popBack",-1,F-1,"popAtSep");add("popReturn",a=>a===2?z(popBack,a):bad());
 const popParent=cross("popParent",-1,D-1,"search0_0");add("popAtSep",a=>a===2?l(popParent,a):bad());
 // Success keeps the entire ten-frame chain as the physical certificate.
 // Return to the root separator and set its status bit.
 readAt("succeeded",58,"acceptRoot","upSuccess");
 move("upSuccess",-1,D,"succeeded");writeAt("acceptRoot",59,1,"planHalt");
 add("planHalt",a=>a===2?z("HALT",2):bad());
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
 return{q,desc,events,plannerEntry:ids.get("search0_0|0"),pushEntry:ids.get("push|0"),popEntry:ids.get("pop|0")};
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
 const origin=3*raw.length+512,tape=new Uint8Array(origin+raw.length+1024);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=raw.charCodeAt(i)-48;
 let state=0,head=origin,t=0,lo=head,hi=head,plannerAt=null,pushes=0,pops=0;const {q,T}=M;
 const event=observe?new Int32Array(q):null;if(event)for(let i=0;i<M.events.length;i++)event[M.events[i].state]=i+1;
 while(state!==q&&t<limit){
  if(state===M.plannerEntry&&plannerAt===null)plannerAt=t;
  if(state===M.pushEntry)pushes++;if(state===M.popEntry)pops++;
  if(event&&event[state])observe(M.events[event[state]-1],tape,head,origin);
  let v=T[3*state+tape[head]];tape[head]=(v>>2)&3;head+=(v&3)-1;state=v>>>4;t++;
  if(head<0||head>=tape.length)throw Error("simulation buffer");if(head<lo)lo=head;if(head>hi)hi=head;
 }
 if(state!==q)return{status:"TIMEOUT",t,head:head-origin,span:hi-lo+1,plannerAt,pushes,pops};
 let nonblank=0;for(let a of tape)if(a!==2)nonblank++;
 if(tape[head]<2){if(nonblank!==1)throw Error("noncanonical rejection head="+(head-origin)+" nonblank="+nonblank+" at "+t);return{status:tape[head]?"OUTSIDE_FIXED_PATH":"OUTSIDE_NORMALIZED",t,span:hi-lo+1};}
 let p=head-16,vals=[0,0,0,0,0],scale=1;
 while(tape[p]!==2){for(let i=4;i>=0;i--){if(tape[p]>1)throw Error("alignment");vals[i]+=scale*tape[p--];}scale*=2;}
 let end=p,start=p-1;while(tape[start]!==2)start--;start++;
 let selector=Array.from(tape.subarray(start,end)).join(""),workBits=head-end-1;
 const blocks=[];let at=start-1;
 for(let j=0;j<37;j++){if(tape[at]!==2)throw Error("block delimiter");at--;let bits=[];while(tape[at]!==2){bits.push(tape[at--]);if(at<0)throw Error("block buffer");}blocks.push(bits.join(""));}
 const blockBits=blocks.reduce((a,b)=>a+b.length,0);
 const frames=[];let cursor=head;
 while(tape[cursor+1]!==2){
  if(tape[cursor]!==2||tape[cursor+61]!==2)throw Error("frame delimiter");
  let word=Array.from(tape.subarray(cursor+1,cursor+61)).join("");if(!/^[01]{60}$/.test(word))throw Error("frame grammar");
  frames.push({graph:word.slice(0,36),active:word.slice(36,45),tried:word.slice(45,54),choice:parseInt(word.slice(54,58),2),root:+word[58],status:+word[59]});
  cursor+=61;if(frames.length>10)throw Error("frame count");
 }
 if(!frames.length||frames[0].root!==1||frames.slice(1).some(f=>f.root||f.status)||nonblank!==selector.length+workBits+blockBits+60*frames.length)throw Error("checkpoint shape");
 const accepted=frames[0].status===1;
 if(accepted?(frames.length!==10||frames[9].active!=="000000000"):frames.length!==1)throw Error("terminal stack");
 const graph=blocks.slice(0,36).map(b=>b===""?0:b==="1"?1:NaN);if(graph.some(Number.isNaN))throw Error("edge block");
 return{status:accepted?"WIDTH_THREE_PLAN":"OUTSIDE_WIDTH_THREE",t,span:hi-lo+1,plannerAt,pushes,pops,checkpoint:{m:vals[0]+1,ranks:vals.slice(2),selector,workBits,head:head-origin,graph,pins:blocks[36],frames,order:accepted?frames.slice(0,9).map(f=>f.choice):null}};

}


module.exports={compile,decode,run};
if(require.main===module){const C=compile();if(process.argv.includes('--descriptor'))process.stdout.write(C.desc);else console.log(JSON.stringify(run({...decode(C.desc),plannerEntry:C.plannerEntry,pushEntry:C.pushEntry,popEntry:C.popEntry},require('fs').readFileSync(0,'utf8'))));}
