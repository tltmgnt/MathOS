// REX-020: nested sparse introduction trees, child-pivot bounded-sweep refinement.
function compile(worker,symbols,projection){
 const blank="__",width=Math.ceil(Math.log2(symbols.length-1)),code={ [blank]:"2".repeat(width) };
 symbols.filter(s=>s!==blank).forEach((s,i)=>code[s]=i.toString(2).padStart(width,"0"));
 const decode=new Map(Object.entries(code).map(([s,c])=>[c,s]));
 const prefixes=new Set(Object.values(code).flatMap(c=>Array.from({length:width-1},(_,i)=>c.slice(0,i+1))));
 const rules=new Map();
 for(const row of worker){
  if(!Array.isArray(row)||row.length!==5)throw Error("rule arity");
  let [s,a,t,w,d]=row;
  if(!/^[a-zA-Z0-9]+$/.test(s)||!/^[a-zA-Z0-9]+$/.test(t)||["ready","reject"].includes(s)||!symbols.includes(a)||!symbols.includes(w)||![-1,0,1].includes(d)||(["ready","reject"].includes(t)&&d!==0)||(t==="reject"&&w!==blank))throw Error("invalid logical rule");
  let k=s+":"+a;if(rules.has(k))throw Error("nondeterministic rule");rules.set(k,[t,w,d]);
 }
 const names=[],ids=new Map(),T=[];
 function id(s){if(s==="HALT")return -1;if(!ids.has(s)){ids.set(s,names.length);names.push(s)}return ids.get(s);}
 id("pBegin");
 function step(s,a){
  const [p,b,j,k]=s.split(":");
  const l=(n,w=a)=>[n,w,-1],r=(n,w=a)=>[n,w,1],z=(n,w=a)=>[n,w,0],fail=()=>z("HALT",2);
  if(p==="pBegin"||p==="pSeek"||p==="pNext"){
   if(a<2)return r("pSeek");
   if(p==="pBegin")return z("read:init:");
   return l(p==="pNext"?"pFinishGap":"pRead");
  }
  if(p==="pRead")return a<2?l("pCross:"+a,2):fail();
  if(p==="pCross")return a<2?l(s):l("pOut:"+b);
  if(p==="pOut")return a<2?l(s):l("pWrite:"+b+":"+(width-2),+code[b+"_"][width-1]);
  if(p==="pWrite")return a===2?l(+j===0?"pTurn":"pWrite:"+b+":"+(+j-1),+code[b+"_"][+j]):fail();
  if(p==="pTurn")return a===2?r("pReturn"):fail();
  if(p==="pReturn")return a<2?r(s):r("pNext");
  if(p==="pFinishGap")return a===2?l("pFinish"):fail();
  if(p==="pFinish")return a<2?l(s):r("read:init:");
  // Aligned logical transition: decode, rewrite backwards, move to aligned next head.
  if(p==="read"){
   const c=(j??"")+a;
   if(c.length<width)return prefixes.has(c)?r("read:"+b+":"+c):fail();
   const sym=decode.get(c),rule=rules.get(b+":"+sym);
   if(!rule)return fail();
   const [ns,w,d]=rule;
   return l("write:"+ns+":"+code[w]+":"+d+":"+(width-2),+code[w][width-1]);
  }
  if(p==="write"){
   const i=+s.split(":")[4],d=+k;
   if(i>0)return l("write:"+b+":"+j+":"+k+":"+(i-1),+j[i]);
   if(d===0)return z(b==="ready"?"sBegin":b==="reject"?"HALT":"read:"+b+":",+j[0]);
   return d===1?r("move:"+b+":"+(width-1)+":1",+j[0]):l("move:"+b+":"+(width-1)+":-1",+j[0]);
  }
  if(p==="move"){
   const next=+j===1?"read:"+b+":":"move:"+b+":"+(+j-1)+":"+k;
   return +k===1?r(next):l(next);
  }
  // Output contract: a contiguous nonblank product region followed by R,
  // head at its first block; project witness track, skipping witness blanks.
  if(p==="sBegin")return a===2?z("HALT"):r("sSeek");
  if(p==="sSeek")return a<2?r(s):l("sEnd:"+ (width-1));
  if(p==="sEnd")return a===+code.R[+b]?l(+b===0?"sBack":"sEnd:"+(+b-1),2):fail();
  if(p==="sBack")return a<2?l(s):r("sStart");
  if(p==="sStart"||p==="sNext"||p==="sScan"){
   if(a<2)return r("sScan");
   if(p==="sStart")return z("HALT");
   return l(p==="sNext"?"sFinishGap":"sRead:");
  }
  if(p==="sRead"){
   if(a===2)return fail();
   let c=a+(b??"");
   if(c.length<width)return l("sRead:"+c,2);
   const sym=decode.get(c);
   if(!sym||!Object.hasOwn(projection,sym))return fail();
   return l("sCross:"+projection[sym],2);
  }
  if(p==="sCross")return a<2?l(s):l("sOut:"+b);
  if(p==="sOut"){
   if(a<2)return l(s);
   if(b==="_")return r("sReturn"); // turn immediately; no output bit.
   return l("sTurn",+b);
  }
  if(p==="sTurn")return a===2?r("sReturn"):fail();
  if(p==="sReturn")return a<2?r(s):r("sNext");
  if(p==="sFinishGap")return a===2?l("sFinish"):fail();
  if(p==="sFinish")return a<2?l(s):r("HALT");
  return fail();
 }
 // Include every declared logical state so microstep audit can check unreachable rules too.
 for(const [s] of worker)id("read:"+s+":");
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [s,w,d]=step(names[i],a);T.push([id(s),w,d]);}
 const q=names.length;
 for(const t of T)if(t[0]===-1)t[0]=q;
 const b=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc,names,code,symbols,width,worker};
}












function worker(){
 const symbols=["__","0_","1_","L","R","Z","O","D","J","X","C","Y","P","Q","K","S","W","V","G","B4","T00","T10","T11"];
 for(let k=0;k<4;k++)for(let a of ["A","B","H","F"])symbols.push(a+k);
 for(let k=0;k<3;k++)for(let b=0;b<2;b++)symbols.push("d"+k+b,"u"+k+b);
 const projection=Object.fromEntries(symbols.filter(a=>a!=="__").map(a=>[a,a==="P"?"0":a==="W"?"1":"_"]));
 const defs=new Map(),add=(s,fn)=>{if(defs.has(s))throw Error(s);defs.set(s,fn)};
 const r=(s,a)=>[s,a,1],l=(s,a)=>[s,a,-1],z=(s,a)=>[s,a,0],bad=()=>z("reject","__"),raw=a=>a==="0_"||a==="1_",data=a=>!["__","L","R"].includes(a),T=a=>/^T(00|10|11)$/.test(a),A=a=>/^A[0-3]$/.test(a),B=a=>/^B[0-4]$/.test(a),H=a=>/^H[0-3]$/.test(a),F=a=>/^F[0-3]$/.test(a),used=a=>/^u[0-2][01]$/.test(a);
 const restore=a=>used(a)?"d"+a.slice(1):a;
 function find(s,p,act){add(s,a=>a==="L"?r(s+"Scan",a):a==="__"?bad():l(s,a));add(s+"Scan",a=>p(a)?act(a):data(a)?r(s+"Scan",a):bad());}
 function walk(s,d,act){add(s,a=>act(a)??(data(a)?(d===1?r(s,a):l(s,a)):bad()));}
 add("init",a=>raw(a)?l("left",a):bad());add("left",a=>a==="__"?r("parseRoot","L"):bad());
 let parse={Root:{"111":["O","rootCode"]},Rows:{"011":["P","First0"],"110":["D","Children"]},Children:{"111":["O","childCode"],"010":["X","closeSeek"]}};
 for(let j=0;j<3;j++){parse["First"+j]={"000":["d"+j+"0","Bits"+j],"001":["d"+j+"1","Bits"+j]};parse["Bits"+j]={...parse["First"+j],"010":["J",j===2?"Mask":"First"+(j+1)]};}
 parse.Mask={"100":["T00","Rows"],"101":["T11","Rows"]};
 for(let [name,table] of Object.entries(parse))for(let n=0;n<3;n++)for(let i=0;i<2**n;i++){
  let b=n?i.toString(2).padStart(n,"0"):"";
  add("parse"+name+b,a=>{if(!raw(a))return bad();let v=b+a[0];if(n<2)return r("parse"+name+v,"Z");let t=table[v];return t?t[1]==="closeSeek"?l("closeSeek","X"):r(["rootCode","childCode"].includes(t[1])?t[1]:"parse"+t[1],t[0]):bad();});
 }
 for(let m of ["root","child"]){
  add(m+"Code",a=>raw(a)?r(m+"Code"+a[0],a):bad());
  for(let b of [0,1])add(m+"Code"+b,a=>{if(!raw(a))return bad();let k=2*b+ +a[0];return (m==="root"?k===3:k<3)?l("mark"+k,a):bad();});
 }
 for(let k=0;k<4;k++)walk("mark"+k,-1,a=>a==="O"?r("skipCode1","A"+k):null);
 add("skipCode1",a=>raw(a)?r("skipCode2",a):bad());add("skipCode2",a=>raw(a)?r("parseRows",a):bad());
 walk("closeSeek",-1,a=>A(a)?a==="A3"?r("rootClose","F3"):l("fParent"+a[1],"H"+a[1]):null);
 walk("rootClose",1,a=>a==="X"?r("endCheck","C"):null);
 add("endCheck",a=>a==="__"?l("rootRewind","R"):bad());
 add("rootRewind",a=>a==="L"?r("rootStart",a):data(a)?l("rootRewind",a):bad());
 walk("rootStart",1,a=>a==="F3"?r("rootRow","H3"):null);
 walk("rootRow",1,a=>a==="P"?r("rootMask","Q"):a==="D"?bad():null);
 walk("rootMask",1,a=>T(a)?z(a==="T11"?"rootPick":"rootDrop",a):null);
 find("rootDrop",a=>a==="Q",a=>r("rootSkip","P"));
 walk("rootSkip",1,a=>T(a)?r("rootRow",a):null);
 find("rootPick",a=>a==="Q",a=>z("rootOpen","W"));
 find("rootOpen",a=>a==="H3",a=>r("backTable","V"));
 walk("backTable",1,a=>a==="D"?r("backScan",a):null);
 walk("backScan",1,a=>F(a)?a==="F3"?bad():l("bParent"+a[1],"H"+a[1]):a==="C"?l("pop","Y"):a==="R"?l("clean",a):null);
 walk("pop",-1,a=>a==="V"?r("popResume","G"):null);
 walk("popResume",1,a=>a==="Y"?r("backScan","C"):null);
 const pairs=[[0,1],[0,2],[1,2]];
 for(let m of ["f","b"])for(let k=0;k<3;k++){
  let h=m+k;
  walk(m+"Parent"+k,-1,a=>m==="f"&&A(a)?z(h+"Child","B"+a[1]):m==="b"&&a==="V"?z(h+"Child","B4"):null);
  find(h+"Child",H,a=>r(h+"Row",a));
  walk(h+"Row",1,a=>a==="P"?r(h+"Mask","Q"):a==="D"?z(m==="f"?"finalize":"badBack",a):null);
  walk(h+"Mask",1,a=>T(a)?z(a==="T11"?h+"Activate":h+"SkipPivot",a):null);
  find(h+"Activate",B,a=>r(h+"ActivateRows",a));
  walk(h+"ActivateRows",1,a=>a==="D"?z(h+"Digit0",a):m==="f"&&a==="P"||m==="b"&&a==="W"?r(h+"ActivateRows","K"):null);
  for(let field=0;field<2;field++){
   let g=h+"d"+field, p=pairs[k][field];
   find(h+"Digit"+field,a=>a==="Q",a=>r(g+"Pivot",a));
   walk(g+"Pivot",1,a=>a==="d"+field+"0"||a==="d"+field+"1"?z(g+"Send"+a[2],"u"+a.slice(1)):T(a)?z(g+"Send2",a):null);
   for(let b=0;b<3;b++){
    let q=g+"x"+b;
    find(g+"Send"+b,B,a=>r(q+"Rows",a));
    walk(q+"Rows",1,a=>a==="K"?r(q+"Compare",a):["P","S","W"].includes(a)?r(q+"Skip",a):a==="D"?z(b===2?(field===0?h+"Digit1":h+"Collect"):h+"Digit"+field,a):null);
    walk(q+"Compare",1,a=>a==="d"+p+"0"||a==="d"+p+"1"?b!==2&&+a[2]===b?r(q+"Skip","u"+a.slice(1)):l(q+"Drop",a):T(a)?b===2?r(q+"Rows",a):l(q+"Drop",a):null);
    walk(q+"Drop",-1,a=>a==="K"?r(q+"Skip",m==="f"?"P":"S"):null);
    walk(q+"Skip",1,a=>T(a)?r(q+"Rows",a):null);
   }
  }
  find(h+"Collect",B,a=>r(h+"Collect0",a));
  for(let hit=0;hit<2;hit++){
   walk(h+"Collect"+hit,1,a=>a==="K"?r(h+"Collect1",m==="f"?"S":"W"):m==="b"&&a==="S"?r(h+"Collect"+hit,"W"):used(a)?r(h+"Collect"+hit,restore(a)):a==="D"?z(h+"Restore"+hit,a):null);
   find(h+"Restore"+hit,a=>a==="Q",a=>r(h+"RestoreFields"+hit,a));
   walk(h+"RestoreFields"+hit,1,a=>used(a)?r(h+"RestoreFields"+hit,restore(a)):T(a)?z(m==="b"&&hit?"bChoose":h+"SkipPivot",a):null);
  }
  find(h+"SkipPivot",a=>a==="Q",a=>r(h+"SkipRow","P"));
  walk(h+"SkipRow",1,a=>T(a)?r(h+"Row",a):null);
 }
 add("badBack",a=>bad());
 find("finalize",B,a=>r("finalRows",a));
 walk("finalRows",1,a=>a==="P"?r("finalMask0",a):a==="S"?r("finalMask1","P"):a==="D"?z("restoreFParent",a):null);
 for(let hit=0;hit<2;hit++)walk("finalMask"+hit,1,a=>T(a)?r("finalRows","T"+a[1]+(+a[2]&hit)):null);
 find("restoreFParent",B,a=>a==="B4"?bad():z("restoreFChild","A"+a[1]));
 find("restoreFChild",H,a=>r("resume","F"+a[1]));
 walk("resume",1,a=>a==="X"?r("parseChildren","C"):null);
 find("bChoose",a=>a==="Q",a=>z("restoreBParent","W"));
 find("restoreBParent",B,a=>z("restoreBChild","V"));
 find("restoreBChild",H,a=>r("backTable","V"));
 add("clean",a=>a==="L"?r("readyAt","__"):data(a)?l("clean",a):bad());
 add("readyAt",a=>a==="Z"?z("ready",a):bad());
 const rules=[];for(let [s,fn] of defs)for(let a of symbols){let [t,w,d]=fn(a);rules.push([s,a,t,w,d]);}
 return {symbols,projection,rules};
}
function encode(t){
 let row=([a,b,c,v])=>"011"+[a,b,c].map(s=>[...s].map(x=>"00"+x).join("")+"010").join("")+(v?"101":"100");
 return "111"+t.k.toString(2).padStart(2,"0")+t.rows.map(row).join("")+"110"+t.children.map(encode).join("")+"010";
}
function logical(J,raw,limit=10000000){
 const rules=new Map(J.rules.map(([s,a,...r])=>[s+":"+a,r])),tape=new Map([...raw].map((v,i)=>[i,v+"_"]));let state="init",head=0,t=0,moves=0,trace=[];
 while(!["ready","reject"].includes(state)&&t<limit){let a=tape.get(head)??"__";let [s,w,d]=rules.get(state+":"+a);trace.push([state,head,a]);if(trace.length>12)trace.shift();if(w==="__")tape.delete(head);else tape.set(head,w);head+=d;moves+=+(d!==0);state=s;t++;}
 return {state,head,t,moves,trace,out:[...tape].sort((a,b)=>a[0]-b[0]).map(([,a])=>J.projection[a]??"_").filter(a=>a!=="_").join("")};
}

function physical(M,raw,limit=40000000){
 let tape=new Map([...raw].map((v,i)=>[i,+v])),head=0,state=0,t=0,lo=0,hi=0,ph=[0,0,0],logical=0,forward=null,backward=null;
 const snap=()=>({head,tape:[...tape].sort((a,b)=>a[0]-b[0])});
 while(state!==M.q&&t<limit){
  let name=M.names[state];if(name==="read:rootRewind:"&&!forward)forward=snap();if(name==="read:readyAt:")backward=snap();
  ph[name[0]==="p"?0:name[0]==="s"?2:1]++;
  if(name.startsWith("read:")&&name.endsWith(":"))logical++;
  let [q,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);head+=d;state=q;t++;lo=Math.min(lo,head);hi=Math.max(hi,head);
 }return {tape,head,state,t,ph,logical,span:hi-lo+1,forward,backward};
}
function flatten(t){
 const nodes=[],pairs=[[0,1],[0,2],[1,2]];let n=3;
 function visit(v,scope){let i=nodes.length;nodes.push({v,scope});for(let c of v.children){let [a,b]=pairs[c.k];visit(c,[scope[a],scope[b],n++]);}return i;}
 visit(t,[0,1,2]);return nodes;
}
function oracle(t,forced=-1){
 const nodes=flatten(t),a=new Map(),choices=[];
 function dfs(i){
  if(i===nodes.length)return choices.slice();
  let {v,scope}=nodes[i];
  for(let j=0;j<v.rows.length;j++){
   let row=v.rows[j];if(!row[3]||(i===0&&forced>=0&&j!==forced)||scope.some((x,k)=>a.has(x)&&a.get(x)!==row[k]))continue;
   let added=[];for(let k=0;k<3;k++)if(!a.has(scope[k])){a.set(scope[k],row[k]);added.push(scope[k]);}
   choices.push(j);let out=dfs(i+1);if(out!==null)return out;choices.pop();for(let x of added)a.delete(x);
  }return null;
 }return dfs(0);
}
function audit(){
 const J=worker(),M=compile(J.rules,J.symbols,J.projection),ok=(v,s)=>{if(!v)throw Error(s)},dec=new Map(Object.entries(M.code).map(([a,b])=>[b,a]));
 let counts={logicalCases:0,physicalCases:0,sat:0,unsat:0,physicalSat:0,physicalUnsat:0,bags:0,rows:0,physical:0,logical:0,checkpoints:0,physicalRows:0,malformed:0,malformedTransitions:0,cutoffs:0},digest=2166136261,physicalDigest=2166136261;
 function check(t,mode=true,record=true){
  let raw=encode(t),N=raw.length,w=M.width,nodes=flatten(t),a=oracle(t),want=a===null?null:nodes.map(({v},i)=>v.rows.map((_,j)=>+(a[i]===j)).join("")).join(""),ref=logical(J,raw);
  ok(ref.state===(a===null?"reject":"ready")&&(a===null||ref.out===want),"logical "+JSON.stringify({raw,want,ref}));
  let expected=[],positions=[],selected=[],openings=[],idx=0;
  const token=v=>{expected.push("Z","Z",v);return expected.length-1;};
  function visit(v){
   let i=idx++;openings.push(token("F"+v.k));expected.push((v.k>>1)+"_",(v.k&1)+"_");
   for(let j=0;j<v.rows.length;j++){let row=v.rows[j],p=token("P");positions.push(p);if(a!==null&&a[i]===j)selected.push(p);
    for(let k=0;k<3;k++){for(let bit of row[k])token("d"+k+bit);token("J");}
    token("T"+row[3]+ +(oracle(v,j)!==null));
   }token("D");for(let c of v.children)visit(c);token("C");
  }visit(t);expected.push("R");
  let r=null;
  if(mode){
   r=physical(M,raw);ok(r.state===M.q&&r.logical===ref.t,"physical halt");
   let prep=(w+1)*N*(N+1)+(w+4)*N+3,mid=(3*w-2)*ref.moves+(2*w-1)*(ref.t-ref.moves);
   ok(r.ph[0]===prep&&r.ph[1]===mid,"phase clocks");
   let start=-w*N-1;
   function unpack(cp,left){ok(cp&&cp.tape.length===w*(N+1+left)&&cp.tape.every(([p],i)=>p===start-left*w+i),"layout");let bits=cp.tape.map(x=>x[1]).join(""),v=Array.from({length:N+1+left},(_,i)=>dec.get(bits.slice(i*w,(i+1)*w)));ok(!left||v[0]==="L","sentinel");return v.slice(left);}
   ok(JSON.stringify(unpack(r.forward,1))===JSON.stringify(expected),"forward "+raw);
   if(a!==null){
    ok(r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"physical output");
    let back=expected.slice();for(let p of openings)back[p]="G";for(let p of selected)back[p]="W";
    ok(JSON.stringify(unpack(r.backward,0))===JSON.stringify(back),"backward "+raw);
    let H=want.length,c=0,body=0,p=new Set(positions);
    for(let i=N-1;i>=0;i--){let e=+p.has(i);body+=2*w*(i+1)+2*c+2*e+4;c+=e;}
    ok(r.ph[2]===2*w*N+2*w+2+body+H+3&&r.head===-w*N-H-2,"serializer");
   }else ok(!r.tape.has(r.head)&&!r.backward&&r.ph[2]===0,"reject");
  }
  if(record){
   counts.logicalCases++;counts.sat+=+(a!==null);counts.unsat+=+(a===null);counts.bags+=nodes.length;counts.rows+=positions.length;
   for(let ch of raw+":"+(a===null?"-":ref.out)+";")digest=Math.imul(digest^ch.charCodeAt(0),16777619)>>>0;
   if(mode){counts.physicalCases++;counts.physicalSat+=+(a!==null);counts.physicalUnsat+=+(a===null);counts.physical+=r.t;counts.logical+=r.logical;counts.checkpoints+=1+ +(a!==null);counts.physicalRows+=positions.length;let out=a===null?"-":Array.from({length:want.length},(_,i)=>r.tape.get(r.head+i)).join("");for(let ch of raw+":"+out+";")physicalDigest=Math.imul(physicalDigest^ch.charCodeAt(0),16777619)>>>0;}
  }return r;
 }
 const node=(k,rows,children=[])=>({k,rows,children}),pairs=[[0,1],[0,2],[1,2]],row=(x,v)=>[...x.toString(2).padStart(3,"0"),v];
 for(let k=0;k<3;k++)for(let p=0;p<8;p++)for(let c=0;c<8;c++)for(let m=0;m<4;m++)check(node(3,[row(p,m&1)],[node(k,[row(c,m>>1)])]),p===0&&c===0&&m===3||p===5&&c===3&&m===3);
 check(node(3,[]));check(node(3,[row(0,1)]));check(node(3,[row(0,1)],[node(2,[])]));
 // All root tuples, distinct child pair predicates forming an inconsistent cycle.
 let rootRows=Array.from({length:8},(_,i)=>row(i,1)),eq=[row(0,1),row(6,1)],neq=[row(2,1),row(4,1)];
 let conflict=node(3,rootRows,[node(0,eq),node(1,eq),node(2,neq)]);ok(oracle(conflict)===null,"cycle oracle");check(conflict);
 let mixed=node(3,[["0","10","101",1],["1","10","101",0],["1","10","101",1]],[node(1,[["1","101","00",1],["1","101","0",1]],[node(2,[["101","0","11",1]])]),node(0,[["1","10","1",1]])]);
 ok(oracle(mixed)?.join(",")==="2,1,0,0","mixed oracle");check(mixed);
 let seed=0x52455820,labels=["0","1","00","10","101"],rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<60;i++){
  let n=2+i%4,rows=()=>Array.from({length:1+(rand()>>>16)%3},()=>[...Array.from({length:3},()=>labels[(rand()>>>16)%labels.length]),rand()>>>31]),nodes=[node(3,rows())];
  for(let j=1;j<n;j++){let k=(rand()>>>16)%3,p=(rand()>>>16)%j;nodes.push(node(k,rows()));nodes[p].children.push(nodes[j]);}
  if(i%2){function plant(v,r){v.rows.push(r);for(let c of v.children){let [x,y]=pairs[c.k];plant(c,[r[x],r[y],labels[(rand()>>>16)%labels.length],1]);}}plant(nodes[0],["0","10","101",1]);}
  check(nodes[0],i<8);
 }
 let good=encode(node(3,[row(0,1)])),malformed=["","0","111","11100","11111","11111110","11111"+"011010",good.slice(0,-1),good.slice(0,-3),good+"0",good+good,encode(node(0,[row(0,1)])),encode(node(3,[row(0,1)],[node(3,[row(0,1)])])),encode(node(3,[["","0","1",1]]))];
 for(let raw of malformed){let r=physical(M,raw);ok(r.state===M.q&&!r.tape.has(r.head),"malformed "+raw);counts.malformed++;counts.malformedTransitions+=r.t;}
 let scaling=[];
 for(let n of [1,2,4,8]){
  let t=node(3,[["0","10","101",1]]);for(let j=0;j<n;j++)t.children.push(node(0,[["0","10","11",1]]));
  let raw=encode(t),r=check(t,true,false);
  if(n<=2){ok(physical(M,raw,r.t-1).state!==M.q,"cutoff");counts.cutoffs++;}
  scaling.push([n,raw.length,r.t,r.logical,r.span,r.ph]);
 }
 let stress=[];
 for(let n of [2,4,8]){
  let t=node(3,Array.from({length:n},(_,i)=>["0","10","101",i%2]));
  for(let j=0;j<n;j++)t.children.push(node(0,[["0","10","11",1]]));
  let r=check(t,true,false);stress.push(["wide",n,encode(t).length,r.t,r.logical,r.span]);
 }
 for(let n of [4,8]){
  let t=node(3,[["0","10","101",1]]),v=t;
  for(let j=1;j<n;j++){let k=j%3,[x,y]=pairs[k],c=node(k,[[v.rows[0][x],v.rows[0][y],"0".repeat(j)+"1",1]]);v.children.push(c);v=c;}
  let r=check(t,true,false);stress.push(["deep",n,encode(t).length,r.t,r.logical,r.span]);
 }
 let pos=3;while(M.desc[pos]==="1")pos++;ok(pos-3===M.q&&M.desc[pos++]==="0","descriptor");let b=M.q.toString(2).length;
 for(let [q,w,d] of M.T){ok(parseInt(M.desc.slice(pos,pos+b),2)===q&&parseInt(M.desc.slice(pos+b,pos+b+2),2)===w&&parseInt(M.desc.slice(pos+b+2,pos+b+4),2)===d+1,"descriptor entry");pos+=b+4;}ok(pos===M.desc.length,"length");
 return {alphabet:J.symbols.length,width:M.width,logicalStates:new Set(J.rules.map(x=>x[0])).size,rules:J.rules.length,states:M.q,bits:M.desc.length,counts,scaling,stress,digest,physicalDigest};
}
module.exports={worker,compile,encode,logical,physical,audit};
if(require.main===module) if(process.argv.includes('--description')){let j=worker();console.log(compile(j.rules,j.symbols,j.projection).desc);}else console.log('F038_REX_NESTED_VARIABLE_OVERLAP_OK '+JSON.stringify(audit()));
