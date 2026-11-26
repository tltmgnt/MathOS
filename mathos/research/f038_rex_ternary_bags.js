// F038-REX-022B4 — fixed single-tape raw selector to nested-bag serializer.
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
 add("SUCCESS",a=>a===2?z("bag0Start",2):bad());
 // All serialization subroutines begin/end at the original workspace separator.
 // Output is a contiguous append-only word immediately to its right.
 function emit(name,word,dest){
  add(name,a=>a===2?r(name+"Seek",a):bad());
  add(name+"Seek",a=>a===2?z(name+"W0",a):r(name+"Seek",a));
  for(let i=0;i<word.length;i++)add(name+"W"+i,a=>a===2?(i===word.length-1?l(name+"Back",+word[i]):r(name+"W"+(i+1),+word[i])):bad());
  backLeft(name+"Back",dest);
  return name;
 }
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
  const choose=walk(name+"Choose",1,lane,name+"Digit");
  const skip=walk(name+"Skip",1,5+lane-1,name+"Digit");
  add(name+"MSB",a=>a===2?bad():a===1?r(lane===1?name+"Digit":walkOnce(),a):r(skip,a));
  function walkOnce(){return choose;} // replaced below by exact fixed-distance lane move
  // The MSB state has already moved one cell right; choose must take lane-1 steps.
  const first=walk(name+"First",1,lane-1,name+"Digit");
  defs.set(name+"MSB",a=>a===2?bad():r(a?first:skip,a));
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
 // A carry at coordinate c resets all lower coordinates. For a mask
 // containing c, rotate forward once. Otherwise rewind m^k-1 times,
 // where k counts included lower coordinates (using their zeroed lanes).
 function rewindMask(name,target,k,dest){
  const rot=name+"Rot";
  if(k===1){
   access(rot,target,"reverse",name+"Inc");inc(name+"Inc",4,name+"Test");
   eq(name+"Test",4,0,name+"Clear",rot);clear(name+"Clear",4,dest);
  }else if(k===2){
   access(rot,target,"reverse",name+"IncC");inc(name+"IncC",4,name+"TestC");
   eq(name+"TestC",4,0,name+"ClearC",rot);clear(name+"ClearC",4,name+"TestB");
   // At a row end, the last reverse rotation has counted m-1 moves.
   // One extra reverse rotation crosses to the next row, except after
   // the final row. Increment B only on that extra rotation.
   eq(name+"TestB",3,0,name+"ClearB",name+"Cross");
   clear(name+"ClearB",3,dest);
   access(name+"Cross",target,"reverse",name+"IncB");inc(name+"IncB",3,rot);
  }else throw Error("rewind arity");
  return rot;
 }
 for(let j=0;j<7;j++){
  const stem="bag"+j,check=stem+"Check1",advance=stem+"Advance2";
  emit(stem+"Start",j?"11110":"11111",check);
  for(let mask=1;mask<8;mask++)access(stem+"Check"+mask,7*j+mask-1,"query",mask===7?stem+"Row":stem+"Check"+(mask+1),advance);
  emit(stem+"Row","011",stem+"Rank0");
  for(let i=0;i<3;i++){rankEmit(stem+"Rank"+i,i+2,stem+"Field"+i);emit(stem+"Field"+i,"010",i===2?stem+"Flag":stem+"Rank"+(i+1));}
  emit(stem+"Flag","101",advance);
  for(let c=2;c>=0;c--){
   eq(stem+"Advance"+c,2+c,0,stem+"Clear"+c,stem+"Inc"+c);
   clear(stem+"Clear"+c,2+c,c?stem+"Advance"+(c-1):stem+"Restore");
   let next=check;
   for(let mask=7;mask>=1;mask--){
    const tag=stem+"Carry"+c+"Mask"+mask,target=7*j+mask-1;
    if(mask&(1<<c))next=access(tag,target,"forward",next);
    else {let k=0;for(let p=c+1;p<3;p++)if(mask&(1<<p))k++;
     if(k)next=rewindMask(tag,target,k,next);
    }
   }
   inc(stem+"Inc"+c,2+c,next);
  }
  // Final tuple uses the final index of every projection. One more
  // forward rotation restores every mask to its original ordering.
  let next=stem+"CloseRows";for(let mask=7;mask>=1;mask--)next=access(stem+"Restore"+mask,7*j+mask-1,"forward",next);
  add(stem+"Restore",a=>a===2?z(next,a):bad());
  emit(stem+"CloseRows","110",j===6?"closeTree":"bag"+(j+1)+"Start");
 }
 emit("closeTree","010".repeat(7),"serializedHalt");
 add("serializedHalt",a=>a===2?z("HALT",2):bad());
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
 const origin=3*raw.length+512,tape=new Uint8Array(origin+5*raw.length+512);tape.fill(2);
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
 let e=head+1;while(tape[e]!==2){if(e>=tape.length)throw Error("output buffer");e++;}const prepared=Array.from(tape.subarray(head+1,e)).join("");
 if(nonblank!==selector.length+workBits+maskBits+prepared.length)throw Error("checkpoint garbage");
 let groups=[];for(let i=0;i<3;i++){let g=0;for(let j=0;j<5;j++)g=2*g+tape[head-15+5*i+j];groups.push(g);}
 return{status:"BAGS_PREPARED",t,span:hi-lo+1,prepared,checkpoint:{m:vals[0]+1,rankBounds:vals.slice(0,2),ranks:vals.slice(2),groups,selector,workBits,selectorStart:start-origin,selectorEnd:end-origin,head:head-origin,masks:blocks.slice(0,49),pins:blocks[49],maskBits:maskBits-blocks[49].length,leftBoundary:at-origin}};
}


module.exports={compile,decode,run};
