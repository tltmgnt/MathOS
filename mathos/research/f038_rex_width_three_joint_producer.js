// D5Q: compact packed blocks with a single two-cell carry insertion of forbidden tokens.
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
 // Validate a fixed mandatory selector suffix before altering the tape.
 // Shift the entire workspace by the suffix length in one right-to-left pass.
 // The consumed prefix is preserved byte-for-byte.
 function batch(name,word,dest){
  const k=word.length;
  if(k===1){shift(name+"Shift",dest,+word[0]);add(name,a=>a===2?r(name+"V0",a):bad());add(name+"V0",a=>a===+word[0]?z(name+"Shift",2):l("clean0",a));return name;}
  function cross(n,d,count,to){if(!count)return to;for(let i=count;i>0;i--)add(n+i,a=>(d===1?r:l)(i===1?to:n+(i-1),a));return n+count;}
  const read=name+"Read",clear=name+"Clear",go=cross(name+"ToWork",-1,1,read);
  for(let i=0;i<k;i++){
   const fail=cross(name+"Fail"+i+"_", -1,i,"clean0");
   add(name+"V"+i,a=>a===+word[i]?(i===k-1?z(clear+(k-1),a):r(name+"V"+(i+1),a)):l(fail,a));
   add(clear+i,a=>a===+word[i]?l(i?clear+(i-1):go,2):bad());
  }
  add(name,a=>a===2?r(name+"V0",a):bad());
  const ret=cross(name+"Return",-1,k,read);
  for(let b=0;b<2;b++){
   const put=name+"Put"+b,step=cross(name+"To"+b+"_",1,k-1,put);
   add(put,a=>l(ret,b));add(name+"Bit"+b,a=>r(step,a));
  }
  add(read,a=>a===2?z(name+"Prefix0",a):z(name+"Bit"+a,a));
  for(let i=0;i<k;i++)add(name+"Prefix"+i,a=>r(i===k-1?name+"Gap":name+"Prefix"+(i+1),+word[i]));
  add(name+"Gap",a=>r(name+"Back",2));back(name+"Back",dest);
  return name;
 }
 // 37 blank-separated blocks, right-to-left: 36 edge flags followed by pins.
 // Append at the left edge of the target, shifting the complete farther-left suffix.
 // The control counts separators; consecutive blanks are valid empty blocks.
 const BLOCKS=130,depCache=new Map();
 function deposit(target,bit,dest,packed=false){
  const double=packed&&bit===1;
  const key=target+":"+bit+":"+dest+":"+packed;if(depCache.has(key))return depCache.get(key);
  const n="deposit"+depCache.size;depCache.set(key,n);
  add(n,a=>a===2?l(n+"Work",a):bad());
  add(n+"Work",a=>a===2?l(n+"Prefix",a):l(n+"Work",a));
  add(n+"Prefix",a=>a===2?l(n+"Seek0",a):l(n+"Prefix",a));
  const insert=n+"Insert",fold=packed&&bit===0;
  add(insert,a=>a===2?l(double?n+"DoubleFirst":n+"Carry"+(BLOCKS-1-target)+"_2",bit):bad());
  for(let j=0;j<=target;j++)add(n+"Seek"+j,a=>a===2?(j===target?(fold?r(n+"Fold1",a):z(insert,a)):l(n+"Seek"+(j+1),a)):l(n+"Seek"+j,a));
  if(fold){
   for(let k=1;k<=3;k++){
    // An appended word ends in 1 unless it is a literal zero.
    // Three terminal literal zeros plus the new zero become 101.
    let ret=insert;
    for(let t=1;t<k;t++){const next=ret;ret=add(n+"Fail"+k+"_"+t,a=>l(next,a));}
    add(n+"Fold"+k,a=>a===0?(k===3?l(n+"FoldMid",1):r(n+"Fold"+(k+1),a)):l(ret,a));
   }
   add(n+"FoldMid",a=>a===0?l(n+"FoldFirst",a):bad());
   add(n+"FoldFirst",a=>a===0?r(n+"Return"+(BLOCKS-1-target),1):bad());
  }
  if(double){
   const J=BLOCKS-1-target;
   // First cell is the second 1; retain the displaced separator and cell.
   add(n+"DoubleFirst",a=>J===0?(a===2?l(n+"Flush2",1):bad()):l(n+"Double"+(J-(a===2?1:0))+"_2"+a,1));
   // The final old separator has been read when j becomes zero.
   // Flush the two-cell carry onto the unused blank extent.
   add(n+"Flush2",a=>a===2?r(n+"Return0",2):bad());
   for(let c=0;c<3;c++)add(n+"Double0_"+c+"2",a=>a===2?l(n+"Flush2",c):bad());
   for(let j=1;j<=J;j++)for(let c=0;c<3;c++)for(let d=0;d<3;d++)add(n+"Double"+j+"_"+c+d,a=>l(n+"Double"+(j-(a===2?1:0))+"_"+d+a,c));
  }else for(let j=0;j<=BLOCKS-1-target;j++)for(let carry=0;carry<3;carry++)add(n+"Carry"+j+"_"+carry,a=>{
   if(j===0)return a===2&&carry===2?r(n+"Return0",2):bad();
   return l(n+"Carry"+(j-(a===2?1:0))+"_"+a,carry);
  });
  for(let j=0;j<BLOCKS;j++)add(n+"Return"+j,a=>a===2?r(j===BLOCKS-1?n+"BackPrefix":n+"Return"+(j+1),a):r(n+"Return"+j,a));
  add(n+"BackPrefix",a=>a===2?r(n+"BackWork",a):r(n+"BackPrefix",a));
  add(n+"BackWork",a=>a===2?z(dest,a):r(n+"BackWork",a));
  return n;
 }
 const scopeList=[];for(let k=1;k<=3;k++){
  function subsets(a,start){if(a.length===k){scopeList.push(a);return;}for(let i=start;i<9;i++)subsets([...a,i],i+1);}
  subsets([],0);
 }
 const scopeIndex=new Map(scopeList.map((a,i)=>[a.join("_"),1+i]));
 const scopes=new Map();
 function covered(k,gs){
  if(gs.some((g,i)=>i&&g<=gs[i-1]))return "BROKEN";

  const name="covered"+gs.join("_");
  if(!scopes.has(name)){scopes.set(name,{k,target:scopeIndex.get(gs.join("_"))});}
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
  const stem="bits"+k+type,optional=type==="Optional"||type==="Outside",len=2**k;
  const word=Array.from({length:len},(_,i)=>type.startsWith("Req")&&i===sreq?"1":"0").join("");
  for(let i=0;i<len;i++)expected.set(stem+"S"+i,{k,s:i,type,sreq});
  if(!optional){batch(stem+"S0",word,"advance"+k);return;}
  const name=stem+"S0";
  add(name,a=>a===2?r(name+"Raw",a):bad());
  add(name+"Raw",a=>a===2?l("clean0",a):z(name+"V"+a+(type==="Outside"&&a===1?"!":""),2));
  for(let b=0;b<2;b++)shift(name+"V"+b,stem+"S1",b);
  batch(stem+"S1",word.slice(1),"advance"+k);
 }
 for(let k=1;k<=3;k++){bits(k,"None",-1);bits(k,"Optional",-1);bits(k,"Outside",-1);}
 bits(1,"Req0",0);bits(1,"Req1",1);bits(2,"Req0",0);bits(2,"Req1",1);bits(3,"Req6",6);
 for(let [name,{k,target}] of scopes){
  expected.set(name,{k,s:0,type:"Optional",sreq:-1});
  add(name,a=>a===2?r(name+"Raw",a):bad());
  const routes=[0,1].map(bit=>{let dest=name+"Consume"+bit;add(dest,a=>a===2?r(name+"Finish"+bit,a):bad());add(name+"Finish"+bit,a=>a===bit?z("bits"+k+"OptionalS0V"+bit,2):bad());return deposit(target,bit,dest,k>=2);});
  add(name+"Raw",a=>a===2?l("clean0",a):l(routes[a],a));
 }
 add("pinFirst",a=>a===2?r("pinFirstRaw",a):bad());
 const pinRoutes=[0,1].map(bit=>{let dest="pinConsume"+bit;add(dest,a=>a===2?r("pinFinish"+bit,a):bad());add("pinFinish"+bit,a=>a===bit?z("pinStart"+bit,2):bad());return deposit(0,1-bit,dest);});
 add("pinFirstRaw",a=>a===2?l("clean0",a):l(pinRoutes[a],a));
 for(let b of [0,1]){
  shift("pinStart"+b,"pin"+b+"S1",b);
  for(let i=1;i<8;i++)expected.set("pin"+b+"S"+i,{k:3,s:i,type:"Pin",sreq:b});
  batch("pin"+b+"S1",String(b).repeat(3)+String(1-b).repeat(4),"advance3");
 }
 expected.set("pinFirst",{k:3,s:0,type:"Pin",sreq:-1});
 add("done",a=>a===2?r("doneRaw",a):bad());
 add("doneRaw",a=>a===2?l("SUCCESS",a):l("clean0",a));
 add("SUCCESS",a=>a===2?z("loadStart",2):bad());
 // Preserve the complete C1 checkpoint. Output starts immediately to
 // the right of the tenth frame delimiter. 00/01=data bits, 10=end field.
 // Exactly one source bit is temporarily blank during a copy shuttle.
 // Its original value is held in finite control, then restored.
 function blanks(n,dir,k,dest){
  const go=dir===1?r:l;
  for(let j=1;j<=k;j++)add(n+"Count"+j,a=>a===2?(j===1?z(dest,a):go(n+"Count"+(j-1),a)):go(n+"Count"+j,a));
  return add(n,a=>go(n+"Count"+k,a));
 }
 function streamEnd(n,word,dest){
  // At h, skip ten frame separators; output is contiguous binary.
  const ret=dest;
  add(n+"Back",a=>a===2?z(ret,a):l(n+"Back",a));
  for(let i=0;i<word.length;i++)add(n+"Put"+i,a=>a===2?(i===word.length-1?l(n+"Back",+word[i]):r(n+"Put"+(i+1),+word[i])):bad());
  add(n+"Seek",a=>a===2?z(n+"Put0",a):r(n+"Seek",a));
  add(n+"Boundary",a=>a===2?r(n+"Seek",a):bad());
  return add(n,a=>a===2?z(n+"Boundary",a):bad());
 }
 // Scan the bound's M lane from LSB to MSB without altering any other lane.
 const loadFirst=walk("loadSkip", -1,15,"loadColumn");
 add("loadStart",a=>a===2?l(loadFirst,a):bad());
 const toM=walk("loadLane",-1,4,"loadM");
 add("loadColumn",a=>a===2?z("loadBoundDone",a):z(toM,a));
 for(let b=0;b<2;b++){
  const n="loadBound"+b;
  add(n+"Restore",a=>a===2?l("loadColumn",b):l(n+"Restore",a));
  add(n+"Return",a=>a===2?l(n+"Restore",a):bad());
  streamEnd(n+"Emit","0"+b,n+"Return");
  add(n+"Right",a=>a===2?z(n+"Emit",a):r(n+"Right",a));
 }
 add("loadM",a=>a<2?r("loadBound"+a+"Right",2):bad());
 blanks("loadBoundDone",1,1,"trimBound");
 // Remove high zero digits, keeping the final 01 pair (m>=2).
 const trimRet="loadBlock0";
 add("trimBack",a=>a===2?z(trimRet,a):l("trimBack",a));
 add("trimPut1",a=>a===2?l("trimBack",0):bad());
 add("trimPut0",a=>a===2?r("trimPut1",1):bad());
 add("trimBit",a=>a===0?l("trimZero",2):a===1?r("trimPut0",1):bad());
 add("trimZero",a=>a===0?l("trimBit",2):bad());
 add("trimSeek",a=>a===2?l("trimBit",a):r("trimSeek",a));
 add("trimBoundary",a=>a===2?r("trimSeek",a):bad());
 add("trimBound",a=>a===2?z("trimBoundary",a):bad());
 // j counts the original right-to-left blocks. The right delimiter
 // of block j is the (j+2)nd blank left of h, even for empty edges.
 for(let j=0;j<130;j++){
  const n="loadBlock"+j,next=j===129?"bridgeReady":"loadBlock"+(j+1);
  // Higher-arity zero blocks need only their delimiter. Scan without
  // modifying the block; on finding a one, return to its right delimiter.
  add(n+"Enter",a=>a===2?l(n+(j>=10?"Detect":"Read"),a):bad());
  if(j>=10){
   add(n+"Detect",a=>a===0?l(n+"Detect",a):a===1?l(n+"Detect1",a):z(n+"Done",a));
   add(n+"Detect1",a=>a===1?r(n+"ActiveBack",a):a===0?l(n+"DetectRun",a):bad());
   add(n+"DetectRun",a=>a===1?l(n+"Detect",a):bad());
   add(n+"ActiveBack",a=>a===2?l(n+"Read",a):r(n+"ActiveBack",a));
  }
  blanks(n,-1,j+2,n+"Enter");
  for(let b=0;b<2;b++){
   const tag=n+"Bit"+b;
   add(tag+"Restore",a=>a===2?l(n+"Read",b):l(tag+"Restore",a));
   add(tag+"Enter",a=>a===2?l(tag+"Restore",a):bad());
   blanks(tag+"Return",-1,j+2,tag+"Enter");
   streamEnd(tag+"Emit","0"+b,tag+"Return");
   blanks(tag+"Right",1,j+3,tag+"Emit");
  }
  streamEnd(n+"End","10",next);
  blanks(n+"Done",1,j+3,n+"End");
  if(j>=10){
   // Packed blocks are decoded from their right edge. Both multi-cell
   // words end at a one; mark only that last cell for the copy shuttle.
   for(const [kind,word] of [["One","01"],["Run","11"]]){
    const tag=n+kind;
    add(tag+"Restore",a=>a===2?l(n+"Read",1):l(tag+"Restore",a));
    add(tag+"Enter",a=>a===2?l(tag+"Restore",a):bad());
    blanks(tag+"Return",-1,j+2,tag+"Enter");
    streamEnd(tag+"Emit",word,tag+"Return");
    blanks(tag+"Right",1,j+3,tag+"Emit");
    add(tag+"Mark",a=>a===1?z(tag+"Right",2):bad());
   }
   add(n+"Packed1",a=>a===1?z(n+"OneMark",a):a===0?l(n+"RunMark",a):bad());
   // Batch the terminal one to three literal zeros as in D5O.
   for(let k=1;k<=3;k++)add(n+"Probe"+k,a=>a===0?(k===3?bad():l(n+"Probe"+(k+1),a)):r(k===1?n+"Mark0":n+"ShortMark"+k,a));
   for(let k=2;k<=3;k++){
    const tag=n+"Short"+k;
    add(tag+"Restore",a=>a===2?l(n+"Read",0):l(tag+"Restore",a));
    add(tag+"Enter",a=>a===2?l(tag+"Restore",a):bad());
    blanks(tag+"Return",-1,j+2,tag+"Enter");
    streamEnd(tag+"Emit","00".repeat(k),tag+"Return");
    blanks(tag+"Right",1,j+3,tag+"Emit");
    add(n+"ShortMark"+k,a=>a===0?z(tag+"Right",2):bad());
   }
   add(n+"Read",a=>a===2?z(n+"Done",a):a===0?l(n+"Probe1",a):l(n+"Packed1",a));
  }else add(n+"Read",a=>a===2?z(n+"Done",a):z(n+"Mark"+a,a));
  for(let b=0;b<2;b++)add(n+"Mark"+b,a=>a===b?z(n+"Bit"+b+"Right",2):bad());
 }

 add("bridgeReady",a=>a===2?z("HALT",2):bad());
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
 return{q,desc,events,plannerEntry:ids.get("search0_0|0"),pushEntry:ids.get("push|0"),popEntry:ids.get("pop|0"),loaderEntry:ids.get("loadStart|0"),bridgeReady:ids.get("bridgeReady|0")};
}
function decode(desc){
 if(!/^1111+0[01]+$/.test(desc))throw Error("descriptor grammar");
 let p=3;while(desc[p]==="1")p++;let q=p-3;p++;let b=q.toString(2).length;
 if(desc.length!==p+3*q*(b+4))throw Error("descriptor size");
 let T=new Uint32Array(3*q);
 for(let i=0;i<T.length;i++){let s=parseInt(desc.slice(p,p+b),2),w=parseInt(desc.slice(p+b,p+b+2),2),d=parseInt(desc.slice(p+b+2,p+b+4),2);p+=b+4;if(s>q||w>2||d>2)throw Error("descriptor field");T[i]=(s<<4)|(w<<2)|d;}
 return{q,T};
}
function run(M,raw,limit=Infinity){
 if(!/^[01]*$/.test(raw))throw Error("binary raw required");
 const origin=3*raw.length+1024;let tape=new Uint8Array(origin+2*raw.length+2048);tape.fill(2);for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let s=0,h=origin,t=0,lo=h,hi=h,loaded=false;
 while(s!==M.q&&t<limit){if(s===M.bridgeReady&&tape[h]===2)loaded=true;
  const v=M.T[3*s+tape[h]];tape[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;
  if(h<0)throw Error("left buffer");if(h===tape.length){const a=new Uint8Array(tape.length*2);a.fill(2);a.set(tape);tape=a;}
  lo=Math.min(lo,h);hi=Math.max(hi,h);
 }
 if(s!==M.q)return{status:"TIMEOUT",t,head:h-origin,span:hi-lo+1};
 if(!loaded)return{status:"REFUSAL",t,head:h-origin,span:hi-lo+1,headSymbol:tape[h]};
 let e=h+1;while(tape[e]!==2)e++;const stream=Array.from(tape.subarray(h+1,e)).join("");
 let fields=[],field="";for(let i=0;i<stream.length;i+=2){const tok=stream.slice(i,i+2);if(tok==="10"){fields.push(field);field="";}else if(tok==="00"||tok==="01")field+=tok[1];else if(tok==="11"&&fields.length>=11)field+="0000";else throw Error("stream token");}
 if(field||fields.length!==131||tape[h]!==2)throw Error("stream shape");
 return{status:"MASK_STREAM_LOADED",t,head:h-origin,span:hi-lo+1,stream,fields};
}
module.exports={compile,decode,run};
if(require.main===module){const C=compile();if(process.argv.includes('--descriptor'))process.stdout.write(C.desc);else console.log(JSON.stringify(run({...decode(C.desc),bridgeReady:C.bridgeReady},require('fs').readFileSync(0,'utf8'))));}
