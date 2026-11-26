// REX-023D1 — physical general width-two bottom-up separator feasibility.
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
 function classify(name,k,choose,raw=false){
  const memo=new Map(),ret=new Map();let serial=0;
  function toSep(dest){if(!ret.has(dest))ret.set(dest,back(name+"Ret"+ret.size,dest));return ret.get(dest);}
  const skip=(3-k)*5;
  function tree(depth,v){
   if(depth===5*k){let gs=[];for(let i=k-1;i>=0;i--)gs.push((v>>(5*i))&31);return toSep(!raw&&gs.some(g=>g>20)?"BROKEN":choose(gs));}
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
 // 166 blank-separated blocks: 36 edge flags, pins, then 129 scope masks.
 // Append at the left edge of the target, shifting the complete farther-left suffix.
 // The control counts separators; consecutive blanks are valid empty blocks.
 const BLOCKS=166,depCache=new Map();
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
 const scopeList=[];for(let k=1;k<=3;k++){
  function subsets(a,start){if(a.length===k){scopeList.push(a);return;}for(let i=start;i<9;i++)subsets([...a,i],i+1);}
  subsets([],0);
 }
 const scopeIndex=new Map(scopeList.map((a,i)=>[a.join("_"),37+i]));
 const scopes=new Map();
 function covered(k,gs){
  if(gs.some((g,i)=>i&&g<=gs[i-1]))return "BROKEN";

  const name="covered"+gs.join("_");
  if(!scopes.has(name)){const ids=[];for(let i=0;i<k;i++)for(let j=i+1;j<k;j++)ids.push(edge(gs[i],gs[j]));scopes.set(name,{k,ids,target:scopeIndex.get(gs.join("_"))});}
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
 for(let [name,{k,ids,target}] of scopes){
  expected.set(name,{k,s:0,type:"Optional",sreq:-1});
  add(name,a=>a===2?r(name+"Raw",a):bad());
  const routes=[0,1].map(bit=>{let dest=name+"Consume"+bit;add(dest,a=>a===2?r(name+"Finish"+bit,a):bad());add(name+"Finish"+bit,a=>a===bit?z("bits"+k+"OptionalS0V"+bit,2):bad());if(bit)for(let j=ids.length-1;j>=0;j--)dest=setEdge(ids[j],dest);return deposit(target,bit,dest);});
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
 // 36 edge bits, 9 active flags, followed by 12-bit plan records and status.
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
 emit("activeInit","111111111","search0_0");
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
 const records=new Map(),nodeMemo=new Set();
 function record(v,ns){
  const n="choose"+v+"_"+ns.join("_");if(records.has(n))return n;records.set(n,1);
  let dest="clearVertex"+v;
  if(ns.length===2)dest=writeAt(n+"Fill",edge(...ns),1,dest);
  return emit(n,bin(v)+bin(ns[0]??9)+bin(ns[1]??9),dest);
 }
 function neighbors(v,i,ns){
  if(i===9)return record(v,ns);
  if(i===v)return neighbors(v,i+1,ns);
  const n="neighbor"+v+"_"+i+"_"+ns.join("_");if(nodeMemo.has(n))return n;nodeMemo.add(n);
  const no=neighbors(v,i+1,ns),yes=ns.length===2?(v===8?"planReject":"search"+(v+1)+"_1"):neighbors(v,i+1,[...ns,i]);
  return readAt(n,edge(v,i),yes,no);
 }
 for(let v=0;v<9;v++){
  let dest="search0_0";
  for(let i=8;i>=0;i--)if(i!==v)dest=writeAt("clear"+v+"Edge"+i,edge(v,i),0,dest);
  writeAt("clearVertex"+v,36+v,0,dest);
  const yes=neighbors(v,0,[]);
  for(let found of [0,1]){
   const no=v===8?(found?"planReject":"planAccept"):"search"+(v+1)+"_"+found;
   readAt("search"+v+"_"+found,36+v,yes,no);
  }
 }
 emit("planAccept","1","parent0");emit("planReject","0","planHalt");
 // For each elimination record, physically read the two neighbor IDs,
 // scan later vertices until the first match, then append that index.
 // Parent sentinel 9 denotes a component root. Order is elimination order.
 for(let i=0;i<9;i++){
  const next=i===8?"relInit":"parent"+(i+1),root="parent"+i;
  for(let p=i+1;p<=9;p++){
   const name=root+"Emit"+p;emit(name,bin(p),next);
   add(root+"Return"+p,a=>a===2?z(name,a):l(root+"Return"+p,a));
  }
  const memo=new Set();
  function search(a,b,j,prefix=""){
   const n=root+"S_"+a+"_"+b+"_"+j+"_"+prefix;if(memo.has(n))return n;memo.add(n);
   add(n,x=>{
    if(x===2)return bad();let t=prefix+x;
    if(t.length<4)return r(search(a,b,j,t),x);
    let v=parseInt(t,2);if(v>8)return bad();
    if(v===a||v===b)return l(root+"Return"+j,x);
    if(j===8)return bad();
    const tag=root+"Skip_"+a+"_"+b+"_"+j;
    if(!defs.has(tag+"8"))walk(tag,1,8,search(a,b,j+1));
    return r(tag+"8",x);
   });return n;
  }
  function read(prefix=""){
   const n=root+"Read"+prefix;
   add(n,x=>{
    if(x===2)return bad();const t=prefix+x;
    if(t.length<8){const dest=root+"Read"+t;if(!defs.has(dest))read(t);return r(dest,x);}
    const a=parseInt(t.slice(0,4),2),b=parseInt(t.slice(4),2);
    if(a>9||b>9||a===9&&b!==9||b!==9&&a>=b)return bad();
    if(a===9)return l(root+"Return9",x);
    if(i===8)return bad();
    return r(search(a,b,i+1),x);
   });return n;
  }
  const entry=walk(root+"Walk",1,45+12*i+4,read());
  add(root,a=>a===2?r(entry,a):bad());
 }
 add("planHalt",a=>a===2?z("HALT",2):bad());

 // Forest word is followed by four bag-index bits and eight return-code
 // bits, then nine row sections. Sorted group order aligns every projection
 // with the original scope mask lexicographic order. The owner is marked
 // by adding 16 to its group word; 9 denotes a missing coordinate.
 function backLeft(name,dest){return add(name,a=>a===2?z(dest,a):l(name,a));}
 // Target mask is physically ordered right-to-left. Query/rotate in that order.
 function access(name,target,kind,yes,no){
  add(name,a=>a===2?l(name+"Work",a):bad());
  add(name+"Work",a=>a===2?l(name+"Prefix",a):l(name+"Work",a));
  add(name+"Prefix",a=>a===2?l(name+"Seek0",a):l(name+"Prefix",a));
  for(let j=0;j<target;j++)add(name+"Seek"+j,a=>a===2?l(name+"Seek"+(j+1),a):l(name+"Seek"+j,a));
  function returnRight(tag,dest){
   for(let j=target;j>=0;j--)add(tag+j,a=>a===2?r(j===0?tag+"Prefix":tag+(j-1),a):r(tag+j,a));
   add(tag+"Prefix",a=>a===2?r(tag+"Work",a):r(tag+"Prefix",a));
   back(tag+"Work",dest);
   return tag+target;
  }
  const ret=returnRight(name+"R",yes);
  if(kind==="query"){
   const ret1=returnRight(name+"T",no);
   add(name+"Seek"+target,a=>a===2?bad():r(a===0?ret:ret1,a));
  }else if(kind==="forward"){
   // [b0,b1,...,bz] -> [b1,...,bz,b0]: carry b0 to far end,
   // then sweep right with a one-symbol carry.
   add(name+"Seek"+target,a=>a===2?bad():l(name+"Find"+a,a));
   for(let b of [0,1]){
    add(name+"Find"+b,a=>a===2?r(name+"Carry"+b,a):l(name+"Find"+b,a));
    add(name+"Carry"+b,a=>a===2?r(target===0?name+"RPrefix":name+"R"+(target-1),a):r(name+"Carry"+a,b));
   }
  }else if(kind==="reverse"){
   // [b0,b1,...,bz] -> [bz,b0,...,b(z-1)]: carry while scanning left,
   // then write last bit at the first cell (temporary blank marker).
   add(name+"Seek"+target,a=>a===2?bad():l(name+"Carry"+a,2));
   for(let b of [0,1]){
    add(name+"Carry"+b,a=>a===2?r(name+"Find"+b,a):l(name+"Carry"+a,b));
    add(name+"Find"+b,a=>a===2?r(ret,b):r(name+"Find"+b,a));
   }
  }else throw Error("access kind");
  return name;
 }
 // Rank emission reads MSB first. A temporary blank replaces the emitted bit
 // during the append shuttle; finite control holds that bit until restoration.
 function rankEmit(name,lane,dest){
  add(name,a=>a===2?l(name+"Find",a):bad());
  add(name+"Find",a=>a===2?r(name+"MSB",a):l(name+"Find",a));
  const skip=walk(name+"Skip",1,5+lane-1,name+"Digit");
  const first=walk(name+"First",1,lane-1,name+"Digit");
  add(name+"MSB",a=>a===2?bad():r(a?first:skip,a));
  // After restoring a digit, check whether its column is the final one by
  // looking exactly G+W-lane cells to the right, then return the same distance.
  const distance=G+W-lane;
  const more=walk(name+"More",1,W,name+"Digit");
  const retMore=walk(name+"ReturnMore",-1,distance-1,more);
  const retEnd=walk(name+"ReturnEnd",-1,distance-1,name+"EndDigit");
  const look=walk(name+"Look",1,distance-1,name+"TestEnd");
  add(name+"TestEnd",a=>l(a===2?retEnd:retMore,a));
  add(name+"EndDigit",a=>a===2?bad():r(name+"EndScan",a));back(name+"EndScan",dest);
  add(name+"Digit",a=>a===2?bad():r(name+"ToSep"+a,2));
  for(let b of [0,1]){
   add(name+"ToSep"+b,a=>a===2?r(name+"Out"+b,a):r(name+"ToSep"+b,a));
   add(name+"Out"+b,a=>a===2?r(name+"O1_"+b,0):r(name+"Out"+b,a));
   add(name+"O1_"+b,a=>a===2?r(name+"O2_"+b,0):bad());
   add(name+"O2_"+b,a=>a===2?l(name+"BackOut"+b,b):bad());
   add(name+"BackOut"+b,a=>a===2?l(name+"BackMark"+b,a):l(name+"BackOut"+b,a));
   add(name+"BackMark"+b,a=>a===2?r(look,b):l(name+"BackMark"+b,a));
  }
  return name;
 }

 function readWord(name,offset,width,choose){
  const memo=new Set();
  function node(p){let n=name+"D"+p;if(memo.has(n))return n;memo.add(n);
   add(n,a=>{if(a===2)return bad();let v=p+a;if(v.length<width)return r(node(v),a);return l(ret(choose(parseInt(v,2))),a);});return n;
  }
  const returns=new Map();
  function ret(dest){if(!returns.has(dest)){let n=name+"Ret"+returns.size;returns.set(dest,n);backLeft(n,dest);}return returns.get(dest);}
  const start=walk(name+"Walk",1,offset,node(""));return add(name,a=>a===2?r(start,a):bad());
 }
 function writeWord(name,offset,word,dest){
  const start=walk(name+"Walk",1,offset,name+"W0");add(name,a=>a===2?r(start,a):bad());
  for(let i=0;i<word.length;i++)add(name+"W"+i,a=>a===2?bad():i===word.length-1?l(name+"Back",+word[i]):r(name+"W"+(i+1),+word[i]));
  backLeft(name+"Back",dest);return name;
 }
 emit("relInit","000000000000","record0");
 for(let i=0;i<9;i++){
  const start=walk("recordWalk"+i,1,45+12*i,"recordRead");
  add("record"+i,a=>a===2?r(start,a):bad());
 }
 const recordMemo=new Set(),setupMemo=new Set();
 function readRecord(prefix=""){
  let n="recordRead"+prefix;if(recordMemo.has(n))return n;recordMemo.add(n);
  add(n,a=>{
   if(a===2)return bad();let p=prefix+a;if(p.length<12)return r(readRecord(p),a);
   let [v,x,y]=[0,4,8].map(i=>parseInt(p.slice(i,i+4),2));
   if(v>8||x>9||y>9||x===v||y===v||x===9&&y!==9||y!==9&&x>=y)return bad();
   let g=[v,x,y].filter(z=>z!==9).sort((a,b)=>a-b),arity=g.length;
   g=g.map(z=>z===v?z+16:z);while(g.length<3)g.push(9);
   const name="setup"+g.join("_");
   if(!setupMemo.has(name)){setupMemo.add(name);let dest="r"+arity+"Start";for(let j=2;j>=0;j--)dest=groupSet(name+"G"+j,j,g[j],dest);backLeft(name,dest);}
   return l(name,a);
  });return n;
 }
 readRecord();
 const returns=[],ops=new Map(),maskRoutes=new Map();
 function maskCall(name,subset,kind,yes,no=yes){
  const key=subset+":"+kind;
  if(!ops.has(key)){
   const dispatch="maskDispatch"+subset+"_"+kind;ops.set(key,dispatch);
   classify(dispatch,3,gs=>{
    let g=gs.map(v=>v>=16?v-16:v),owner=gs.findIndex(v=>v>=16);
    if(owner<0||gs.filter(v=>v>=16).length!==1||g.some((v,i)=>v>9||i&&v<g[i-1]))return "BROKEN";
    if(!(subset&(1<<owner))||g.some((v,i)=>v===9&&(subset&(1<<i))))return "resume0";
    const scope=g.filter((_,i)=>subset&(1<<i)),target=scopeIndex.get(scope.join("_"));
    if(target===undefined)return "BROKEN";
    const tag="mask"+target+"_"+kind;
    if(!maskRoutes.has(tag)){maskRoutes.set(tag,1);access(tag,target,kind,"resume0","resume1");}
    return tag;
   },true);
  }
  const code=returns.length;returns.push([yes,no]);if(code>=256)throw Error("return codes");
  return writeWord(name,194,code.toString(2).padStart(8,"0"),ops.get(key));
 }
 function rewindMask(name,subset,k,dest){
  const rot=name+"Rot";
  if(k===1){
   maskCall(rot,subset,"reverse",name+"Inc");inc(name+"Inc",4,name+"Test");
   eq(name+"Test",4,0,name+"Clear",rot);clear(name+"Clear",4,dest);
  }else if(k===2){
   maskCall(rot,subset,"reverse",name+"IncC");inc(name+"IncC",4,name+"TestC");
   eq(name+"TestC",4,0,name+"ClearC",rot);clear(name+"ClearC",4,name+"TestB");
   eq(name+"TestB",3,0,name+"ClearB",name+"Cross");
   clear(name+"ClearB",3,dest);maskCall(name+"Cross",subset,"reverse",name+"IncB");inc(name+"IncB",3,rot);
  }else throw Error("rewind arity");
  return rot;
 }
 for(let arity=1;arity<=3;arity++){
  const stem="r"+arity,check=stem+"Check1",advance=stem+"Advance"+(arity-1),last=(1<<arity)-1;
  emit(stem+"Start","11111",check);
  for(let mask=1;mask<=last;mask++)maskCall(stem+"Check"+mask,mask,"query",mask===last?stem+"Row":stem+"Check"+(mask+1),advance);
  emit(stem+"Row","011",stem+"Rank0");
  for(let i=0;i<arity;i++){rankEmit(stem+"Rank"+i,i+2,stem+"Field"+i);emit(stem+"Field"+i,"010",i===arity-1?stem+"Flag":stem+"Rank"+(i+1));}
  emit(stem+"Flag","101",advance);
  for(let c=arity-1;c>=0;c--){
   eq(stem+"Advance"+c,2+c,0,stem+"Clear"+c,stem+"Inc"+c);
   clear(stem+"Clear"+c,2+c,c?stem+"Advance"+(c-1):stem+"Restore");
   let next=check;
   for(let mask=last;mask>=1;mask--){
    const tag=stem+"Carry"+c+"Mask"+mask;
    if(mask&(1<<c))next=maskCall(tag,mask,"forward",next);
    else {let k=0;for(let p=c+1;p<arity;p++)if(mask&(1<<p))k++;if(k)next=rewindMask(tag,mask,k,next);}
   }
   inc(stem+"Inc"+c,2+c,next);
  }
  let next=stem+"CloseRows";for(let mask=last;mask>=1;mask--)next=maskCall(stem+"Restore"+mask,mask,"forward",next);
  add(stem+"Restore",a=>a===2?z(next,a):bad());
  emit(stem+"CloseRows","110","bagNext");
 }
 readWord("resume0",194,8,x=>returns[x]?.[0]??"BROKEN");
 readWord("resume1",194,8,x=>returns[x]?.[1]??"BROKEN");
 for(let i=0;i<8;i++)writeWord("nextBag"+i,190,bin(i+1),"record"+(i+1));
 readWord("bagNext",190,4,i=>i===8?"clearScratch":i<8?"nextBag"+i:"BROKEN");
 writeWord("clearScratch",190,"000000000000","restoreGroup0");
 groupSet("restoreGroup0",0,19,"restoreGroup1");groupSet("restoreGroup1",1,20,"restoreGroup2");groupSet("restoreGroup2",2,20,"workerStart");


 // Process each child->parent edge in increasing elimination order.
 // Scratch: child index [190:194], target bag [194:198], mask/mode [198:202].
 // Group suffix stores child field mask, parent field mask, parent index.
 // A,B are the separator key, C is a temporary decoded rank.
 writeWord("workerStart",190,"0000","edgeIndex");
 for(let i=0;i<9;i++){
  readWord("edge"+i,154+4*i,4,p=>p===9?"edgeNext":p>i&&p<9?"parentIndex"+p:"BROKEN");
  readWord("root"+i,154+4*i,4,p=>p===9?"rootTarget"+i:p>i&&p<9?"rootNext":"BROKEN");
  writeWord("rootTarget"+i,194,bin(i)+"0000","scanDispatch");
  const st=walk("childWalk"+i,1,45+12*i,"childRecord");
  add("child"+i,a=>a===2?r(st,a):bad());
  const pt=walk("parentWalk"+i,1,45+12*i,"parentRecord");
  add("readParent"+i,a=>a===2?r(pt,a):bad());
  writeWord("parentIndex"+i,194,bin(i),"childIndex");
  writeWord("childTarget"+i,194,bin(i),"childMask");
  if(i<8){writeWord("edgeNext"+i,190,bin(i+1),"edgeIndex");writeWord("rootNext"+i,190,bin(i+1),"rootIndex");}
 }
 readWord("edgeIndex",190,4,i=>i<9?"edge"+i:"BROKEN");
 readWord("childIndex",190,4,i=>i<9?"child"+i:"BROKEN");
 readWord("parentIndexRead",194,4,i=>i<9?"readParent"+i:"BROKEN");
 readWord("edgeNext",190,4,i=>i===8?"rootInit":i<8?"edgeNext"+i:"BROKEN");
 writeWord("rootInit",190,"0000","rootIndex");
 readWord("rootIndex",190,4,i=>i<9?"root"+i:"BROKEN");
 readWord("rootNext",190,4,i=>i===8?"decision1":i<8?"rootNext"+i:"BROKEN");
 const decodeRecord=p=>{
  let [v,a,b]=[0,4,8].map(i=>parseInt(p.slice(i,i+4),2));
  if(v>8||a>9||b>9||v===a||v===b||a===9&&b!==9||b!==9&&a>=b)return null;
  return {v,a,b,g:[v,a,b].filter(x=>x!==9).sort((a,b)=>a-b)};
 };
 function recordReader(name,choose){
  const memo=new Set();
  function st(p){let n=name+p;if(memo.has(n))return n;memo.add(n);
   add(n,a=>{if(a===2)return bad();let x=p+a;if(x.length<12)return r(st(x),a);let rec=decodeRecord(x);return rec?l(choose(rec),a):bad();});return n;
  }return st("");
 }
 const childSet=new Map();
 recordReader("childRecord",({v,a,b,g})=>{
  if(a===9)return "BROKEN";
  const mask=g.reduce((s,x,j)=>s|(x===v?0:1<<j),0),n="childSet"+a+"_"+b+"_"+mask;
  if(!childSet.has(n)){childSet.set(n,1);let d="parentIndexRead";d=groupSet(n+"C",2,mask,d);d=groupSet(n+"B",1,b,d);d=groupSet(n+"A",0,a,d);backLeft(n,d);}return n;
 });
 const parentSet=new Map();
 function finishParent(mask){
  const n="finishParent"+mask;
  if(!defs.has(n)){
   groupSet(n+"Mask",1,mask,n+"Copy");
   groupCopy(n+"Copy",2,0,"saveParentIndex");
   add(n,a=>a===2?z(n+"Mask",a):bad());
  }return n;
 }
 recordReader("parentRecord",({g})=>{
  const n="parentSet"+g.join("_");if(parentSet.has(n))return n;parentSet.set(n,1);
  groupRead(n+"A",0,a=>{
   const ai=g.indexOf(a);if(ai<0)return "BROKEN";
   const tag=n+"B"+ai;if(!defs.has(tag))groupRead(tag,1,b=>{
    if(b===9)return finishParent(1<<ai);
    const bi=g.indexOf(b);return bi<0||bi===ai?"BROKEN":finishParent((1<<ai)|(1<<bi));
   });return tag;
  });backLeft(n,n+"A");return n;
 });
 for(let p=0;p<9;p++)groupSet("saveParent"+p,2,p,"keyStart");
 readWord("saveParentIndex",194,4,p=>p<9?"saveParent"+p:"BROKEN");
 readWord("keyStart",190,4,i=>i<9?"childTarget"+i:"BROKEN");
 function setMask(mode,lane,name){
  groupRead(name,lane,k=>{
   if(k<1||k>6)return "BROKEN"; // nonempty proper subset of a bag
   const n=name+"Set"+k;
   if(!defs.has(n))writeWord(n,198,k.toString(2).padStart(3,"0")+mode,"scanDispatch");return n;
  });
 }
 setMask(0,0,"childMask");setMask(1,1,"parentMask");
 for(let p=0;p<9;p++)writeWord("parentTarget"+p,194,bin(p),"parentMask");
 groupRead("missing",2,p=>p<9?"parentTarget"+p:"BROKEN");
 // Advance separator odometer. For one-field keys B remains zero.
 groupRead("keyAdvance",0,k=>[3,5,6].includes(k)?"advanceB":"advanceA");
 eq("advanceB",3,0,"clearB","incB");inc("incB",3,"keyStart");clear("clearB",3,"advanceA");
 eq("advanceA",2,0,"clearA","incA");inc("incA",2,"keyStart");clear("clearA",2,"edgeNext");
 // Scanner token parser. It visits one target bag and either searches
 // for a live matching row or clears all matching row flags.
 const scanMemo=new Set();
 function token(name,choose,prefix=""){
  const n=name+"T"+prefix;if(scanMemo.has(n))return n;scanMemo.add(n);
  add(n,a=>{if(a===2)return bad();let p=prefix+a;return p.length<3?r(token(name,choose,p),a):choose(p,a);});return n;
 }
 // In each digit shuttle the sole temporary blank in the relation word
 // marks the exact return cell. All scratch and rank lanes are restored.
 function digitShuttle(name,b,dest){
  if(!defs.has(name)){
   const finish=name+"Restore";
   scan(name+"Acc",b,(c,v)=>{let x=v[4];v[4]=c;return{out:v,next:x};},c=>c?"BROKEN":finish);
   add(finish,a=>a===2?r(name+"Seek",a):bad());
   add(name+"Seek",a=>a===2?r(dest,b):r(name+"Seek",a));
   backLeft(name,name+"Acc");
  }return l(name,2);
 }
 function compareShuttle(name,lane,yes,no){
  if(!defs.has(name)){
   for(let [tag,dest] of [["Y",yes],["N",no]]){
    clear(name+tag,4,name+tag+"Restore");
    add(name+tag+"Restore",a=>a===2?r(name+tag+"Seek",a):bad());
    add(name+tag+"Seek",a=>a===2?r(dest,0):r(name+tag+"Seek",a));
   }
   eq(name+"Eq",4,lane,name+"Y",name+"N");backLeft(name,name+"Eq");
  }return l(name,2);
 }
 const startScan=new Map();
 function scanner(mask,mode){
  const stem="scan"+mask+"_"+mode;if(startScan.has(stem))return startScan.get(stem);
  const success=mask===0?"rootNext":"keyAdvance",failure=mask===0?"decision0":"missing";
  backLeft(stem+"Found",success);backLeft(stem+"Done",mode?"keyAdvance":failure);
  const memo=new Map();
  function field(f,match){
   const key=f+":"+match;if(memo.has(key))return memo.get(key);
   const n=stem+"F"+f+"M"+match;memo.set(key,n+"T");
   const selected=!!(mask&(1<<f)),ordinal=[0,1,2].filter(i=>i<f&&(mask>>i&1)).length;
   return token(n,(p,a)=>{
    if(p==="000"||p==="001"){
     if(f>=3)return bad();
     if(match&&selected)return digitShuttle(n+"Digit"+a,a,n+"T");return r(n+"T",a);
    }
    if(p==="010"){
     if(f>=3)return bad();
     const yes=field(f+1,match);
     if(match&&selected)return compareShuttle(n+"Compare",2+ordinal,yes,field(f+1,0));
     return r(yes,a);
    }
    if(p==="100"||p==="101"){
     if(!f||mask>>f)return bad();
     if(match&&a===1&&!mode)return l(stem+"Found",a);
     return r(stem+"RowT",match&&mode?0:a);
    }
    return bad();
   });
  }
  token(stem+"Row",(p,a)=>p==="011"?r(field(0,1),a):p==="110"?l(stem+"Done",a):bad());
  // Skip the five-bit bag header, then read 3-bit row tokens.
  const begins=[];
  for(let i=0;i<9;i++){
   const after=i===0?stem+"RowT":stem+"Skip"+i+"T";
   begins.push(walk(stem+"Head"+i,1,5,after));
   if(i>0)token(stem+"Skip"+i,(p,a)=>p==="110"?r(begins[i-1],a):r(stem+"Skip"+i+"T",a));
  }
  const dispatch=stem+"Target";startScan.set(stem,dispatch);
  for(let i=0;i<9;i++){
   const n=stem+"Bag"+i,st=walk(n+"Walk",1,202,begins[i]);add(n,a=>a===2?r(st,a):bad());
  }
  readWord(dispatch,194,4,i=>i<9?stem+"Bag"+i:"BROKEN");
  return dispatch;
 }
 readWord("scanDispatch",198,4,x=>x===0?scanner(0,0):x>=2&&x<=13?scanner(x>>1,x&1):"BROKEN");
 for(let b of [0,1]){
  writeWord("decision"+b,190,"000000000000","finalGroupA"+b);
  groupSet("finalGroupA"+b,0,19,"finalGroupB"+b);groupSet("finalGroupB"+b,1,20,"finalGroupC"+b);groupSet("finalGroupC"+b,2,20,"finalStatus"+b);
  emit("finalStatus"+b,String(b),"planHalt");
 }

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
 return{q,desc,events,workerEntry:ids.get("workerStart|0")};
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
 const origin=3*raw.length+1024;let tape=new Uint8Array(origin+raw.length+1024);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=raw.charCodeAt(i)-48;
 let state=0,head=origin,t=0,lo=head,hi=head;const {q,T}=M;
 const event=observe?new Int32Array(q):null;if(event)for(let i=0;i<M.events.length;i++)event[M.events[i].state]=i+1;
 while(state!==q&&t<limit){
  if(event&&event[state])observe(M.events[event[state]-1],tape,head,origin);
  let v=T[3*state+tape[head]];tape[head]=(v>>2)&3;head+=(v&3)-1;state=v>>>4;t++;
  if(head<0)throw Error("left simulation buffer");if(head>=tape.length){let grown=new Uint8Array(tape.length*2);grown.fill(2);grown.set(tape);tape=grown;}if(head<lo)lo=head;if(head>hi)hi=head;
 }
 if(state!==q)return{status:"TIMEOUT",t,span:hi-lo+1};
 let nonblank=0;for(let a of tape)if(a!==2)nonblank++;
 if(tape[head]<2){if(nonblank!==1)throw Error("noncanonical rejection head="+(head-origin)+" nonblank="+nonblank+" at "+t);return{status:tape[head]?"OUTSIDE_FIXED_PATH":"OUTSIDE_NORMALIZED",t,span:hi-lo+1};}
 let p=head-16,vals=[0,0,0,0,0],scale=1;
 while(tape[p]!==2){for(let i=4;i>=0;i--){if(tape[p]>1)throw Error("alignment");vals[i]+=scale*tape[p--];}scale*=2;}
 let end=p,start=p-1;while(tape[start]!==2)start--;start++;
 let selector=Array.from(tape.subarray(start,end)).join(""),workBits=head-end-1;
 const blocks=[];let at=start-1;
 for(let j=0;j<166;j++){if(tape[at]!==2)throw Error("block delimiter");at--;let bits=[];while(tape[at]!==2){bits.push(tape[at--]);if(at<0)throw Error("block buffer");}blocks.push(bits.join(""));}
 const blockBits=blocks.reduce((a,b)=>a+b.length,0);
 let e=head+1;while(tape[e]!==2)e++;let word=Array.from(tape.subarray(head+1,e)).join("");
 const accepted=word.length>=202&&word[153]==="1";const planEnd=accepted?154:word.length;
 if(planEnd<46||(planEnd-46)%12!==0)throw Error("plan grammar");
 if(nonblank!==selector.length+workBits+blockBits+word.length)throw Error("checkpoint garbage");
 let plan=[];for(let i=45;i<planEnd-1;i+=12)plan.push([0,4,8].map(j=>parseInt(word.slice(i+j,i+j+4),2)));
 let graph=blocks.slice(0,36).map(b=>b===""?0:b==="1"?1:NaN);if(graph.some(Number.isNaN))throw Error("edge block");
 let groups=[];for(let i=0;i<3;i++){let g=0;for(let j=0;j<5;j++)g=2*g+tape[head-15+5*i+j];groups.push(g);}
 return{status:accepted?(word.endsWith("1")?"FOREST_SAT":"FOREST_UNSAT"):"OUTSIDE_WIDTH_TWO",t,span:hi-lo+1,checkpoint:{m:vals[0]+1,rankBounds:vals.slice(0,2),ranks:vals.slice(2),groups,selector,workBits,selectorStart:start-origin,selectorEnd:end-origin,head:head-origin,graph,pins:blocks[36],masks:blocks.slice(37),relations:accepted?word.slice(202,-1):null,decision:accepted?+word.at(-1):null,parents:accepted?Array.from({length:9},(_,i)=>parseInt(word.slice(154+4*i,158+4*i),2)):[],residual:word.slice(0,36),active:word.slice(36,45),plan,word,leftBoundary:at-origin}};
}


module.exports={compile,decode,run};
if(require.main===module){const C=compile();if(process.argv.includes('--descriptor'))process.stdout.write(C.desc);else console.log(JSON.stringify(run(decode(C.desc),require('fs').readFileSync(0,'utf8'))));}
