// RE-X-002 actual fixed logical-to-physical track demo; not a SAT solver.
function build(){
 const alphabet=["_","B0","B1","W0","W1","L","R","X"];
 const code={_: "222",B0:"000",B1:"001",W0:"010",W1:"011",L:"100",R:"101",X:"110"};
 // Logical worker: complement input payload into witness track, marking left/right
 // sentinels on external blank blocks, then remove markers and project W track.
 // It is not a SAT solver. Symbol alphabet represents two bit tracks + control.
 const logical=[];
 const states=["init","markL","forward","back","eraseL","ready"];
 function delta(s,a){
  if(s==="init")return a==="_"?["ready","_",0]:["markL",a,-1];
  if(s==="markL")return ["forward","L",1];
  if(s==="forward"){
   if(a==="B0"||a==="B1")return ["forward",a==="B0"?"W1":"W0",1];
   if(a==="_")return ["back","R",-1];
  }
  if(s==="back"){
   if(a==="W0"||a==="W1")return ["back",a,-1];
   if(a==="L")return ["eraseL","_",1];
  }
  if(s==="eraseL")return ["ready",a,0];
  throw Error("unreachable");
 }
 for(let s of states.slice(0,-1))for(let a of alphabet){try{logical.push([s,a,...delta(s,a)])}catch{}}
 const M=new Map(logical.map(([s,a,...t])=>[s+":"+a,t]));
 const names=[],ids=new Map(),T=[];
 function id(s){if(s==="HALT")return -1;if(!ids.has(s)){ids.set(s,names.length);names.push(s)}return ids.get(s)}
 id("pBegin");
 function D(s,a){
  let [p,b,j,k]=s.split(":");
  const l=(n,w=a)=>[n,w,-1],r=(n,w=a)=>[n,w,1],z=(n,w=a)=>[n,w,0],fail=()=>z("HALT",2);
  // prepare: take rightmost raw bit, prepend 3-cell code left of gap.
  if(p==="pBegin"||p==="pSeek"||p==="pNext"){
   if(a<2)return r("pSeek");
   if(p==="pBegin")return z("read:init:");
   if(p==="pNext")return l("pFinishGap");
   return l("pRead");
  }
  if(p==="pRead")return a<2?l("pCross:"+a,2):fail();
  if(p==="pCross")return a<2?l(s):l("pOut:"+b);
  if(p==="pOut")return a<2?l(s):l("pWrite:"+b+":1",+code["B"+b][2]);
  if(p==="pWrite")return a===2?l(+j===0?"pTurn":"pWrite:"+b+":0",+code["B"+b][+j]):fail();
  if(p==="pTurn")return a===2?r("pReturn"):fail();
  if(p==="pReturn")return a<2?r(s):r("pNext");
  if(p==="pFinishGap")return a===2?l("pFinish"):fail();
  if(p==="pFinish")return a<2?l(s):r("read:init:");
  // compiler: read three physical cells moving right twice; third read stays.
  // Write third, second, first going left; then move to next block start.
  if(p==="read"){
   let prefix=(j??"")+a;
   if(prefix.length<3)return r("read:"+b+":"+prefix);
   let sym=alphabet.find(x=>code[x]===prefix);
   if(!sym)return fail();
   let t=M.get(b+":"+sym);if(!t)return fail();
   let [ns,w,d]=t;
   return l("write:"+ns+":"+code[w]+":"+d,+code[w][2]);
  }
  if(p==="write")return l("first:"+b+":"+j+":"+k,+j[1]);
  if(p==="first"){
   let d=+k;
   return d===0?z(b==="ready"?"sBegin":"read:"+b+":",+j[0]):
    d===1?r("move:"+b+":2:1",+j[0]):l("move:"+b+":2:-1",+j[0]);
  }
  if(p==="move"){
   let next=+j===1?"read:"+b+":":"move:"+b+":"+(+j-1)+":"+k;
   return +k===1?r(next):l(next);
  }
  // serialize left-to-right via RIGHT side. Need erase R marker first.
  // start at first W block; seek right through binary blocks to R, erase R,
  // move back to first W; then consume rightmost W, prepend output to LEFT
  // (same layout as preparation), reading 3-cell code right-to-left.
  if(p==="sBegin"){
   if(a===2)return z("HALT");
   return r("sSeek");
  }
  if(p==="sSeek")return a<2?r(s):l("sR2");
  if(p==="sR2")return a===1?l("sR1",2):fail();
  if(p==="sR1")return a===0?l("sR0",2):fail();
  if(p==="sR0")return a===1?l("sBack",2):fail();
  if(p==="sBack")return a<2?l(s):r("sStart");
  if(p==="sStart"||p==="sNext"||p==="sScan"){
   if(a<2)return r("sScan");
   if(p==="sStart")return z("HALT");
   if(p==="sNext")return l("sFinishGap");
   return l("sRead");
  }
  if(p==="sRead")return a<2?l("sMid:"+a,2):fail();
  if(p==="sMid")return a===1?l("sFirst:"+b,2):fail();
  if(p==="sFirst")return a===0?l("sCross:"+b,2):fail();
  if(p==="sCross")return a<2?l(s):l("sOut:"+b);
  if(p==="sOut")return a<2?l(s):l("sTurn",+b);
  if(p==="sTurn")return a===2?r("sReturn"):fail();
  if(p==="sReturn")return a<2?r(s):r("sNext");
  if(p==="sFinishGap")return a===2?l("sFinish"):fail();
  if(p==="sFinish")return a<2?l(s):r("HALT");
  return fail();
 }
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [s,w,d]=D(names[i],a);T.push([id(s),w,d])}
 let q=names.length;for(let t of T)if(t[0]===-1)t[0]=q;
 let b=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc,names,code,logical};
}
function audit(){
 const M=build(),ok=(v,s)=>{if(!v)throw Error(s)};
 function run(input,limit=Infinity){
  let tape=new Map([...input].map((a,i)=>[i,+a])),head=0,state=0,t=0,lo=0,hi=0,phase=[0,0,0],boundaries=[];
  while(state!==M.q&&t<limit){
   let name=M.names[state],p=name[0]==="p"?0:name[0]==="s"?2:1;
   if(name==="read:init:"||name==="sBegin")boundaries.push([name,head,t,[...tape.entries()].sort((a,b)=>a[0]-b[0])]);
   let [ns,w,d]=M.T[3*state+(tape.get(head)??2)];
   if(w===2)tape.delete(head);else tape.set(head,w);head+=d;state=ns;t++;phase[p]++;lo=Math.min(lo,head);hi=Math.max(hi,head);
   if(t>1e7)throw Error("runaway");
  }return {head,state,t,tape,lo,hi,phase,boundaries};
 }
 function check(s){
  let n=s.length,r=run(s),want=[...s].map(x=>1-+x),out=want.map((_,i)=>r.tape.get(r.head+i));
  ok(r.state===M.q&&JSON.stringify(out)===JSON.stringify(want)&&r.tape.size===n,"final "+s+" "+JSON.stringify([r.head,r.t,r.phase,out,[...r.tape]]));
  let b=r.boundaries[0],c=r.boundaries[1];ok(b&&c,"phase boundaries");
  let prepared=[...s].map(x=>M.code["B"+x]).join("");
  ok(b[3].map(x=>x[1]).join("")===prepared,"prep");
  let expected=want.map(x=>M.code["W"+x]).join("")+(n?M.code.R:"");
  ok(c[3].map(x=>x[1]).join("")===expected,"logical");
  return r;
 }
 let counts={cases:0,transitions:0,cutoffs:0},rows=[];
 for(let n=0;n<=7;n++)for(let i=0;i<2**n;i++){
  let s=n?i.toString(2).padStart(n,"0"):"",r=check(s);counts.cases++;counts.transitions+=r.t;
  if(i===0){ok(run(s,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;rows.push([n,r.t,r.phase,r.hi-r.lo+1,r.head]);}
 }
 return {states:M.q,bits:M.desc.length,counts,rows};
}
if(process.argv.includes('--description'))console.log(build().desc);else console.log('F038_REX_TRACK_COMPILER_OK '+JSON.stringify(audit()));
