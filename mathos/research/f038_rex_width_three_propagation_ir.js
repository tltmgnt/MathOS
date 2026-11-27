// D5J: binary arc-consistency to a fixed point, then radius-two first/second candidate repair.
function machine(){
 const alphabet=["L","0","1",":",";","|","_",",","x","H","b"],ins=[],symbols=alphabet.filter(x=>x!=="L"&&x!=="_");
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const Q=18,A=15,V=[16,17],G=Array.from({length:9},(_,i)=>i+1),R=[10,11,12],D=13,P=14,X=0;
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 const copy=(a,b,d)=>start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,x,mv(a,1,n)):reject)));
 const domain=x=>bit(x)||x==="x";
 function chosen(a,b,d){return start(a,loop(n=>rd(a,x=>x==="_"?d:domain(x)?app(b,x==="x"?"1":"0",mv(a,1,n)):reject)));}
 function field(out,d){return loop(n=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?(out===null?mv(Q,1,n):app(out,y,mv(Q,1,n))):reject)):x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));}
 // Generate original X words and cumulative Y words only after every mask passes.
 const done=start(X,halt),tail=copy(P,X,word(X,"00",done));
 function cumulative(t,d){
  const before=label(),after=label();
  bind(before,rd(t,x=>x==="_"?d:domain(x)?app(X,x==="x"?"1":"0",mv(t,1,x==="x"?after:before)):reject));
  bind(after,rd(t,x=>x==="_"?d:domain(x)?app(X,"1",mv(t,1,after)):reject));
  // omit rank-zero Y; if X0=1, all subsequent Y bits are one.
  return start(t,rd(t,x=>domain(x)?mv(t,1,x==="x"?after:before):reject));
 }
 let emit=tail;for(let t of G.slice().reverse())emit=cumulative(t,emit);
 for(let t of G.slice().reverse())emit=chosen(t,X,emit);
 emit=start(X,emit);
 const finish=test(Q,x=>x==="_",emit,reject);
 const retry=label(),attempt=label(),dispatch=label(),row=label(),advance0=label(),advance1=label(),advance2=label();
 // A pair uses a one-symbol third rank word. All other words are nonempty one-hot.
 function next(t,carry,normal){return mv(t,1,rd(t,x=>x==="_"?start(t,carry):bit(x)?normal:reject));}
 const end=rd(Q,x=>x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,dispatch),reject)):reject);
 bind(advance0,next(R[0],end,row));bind(advance1,next(R[1],advance0,row));bind(advance2,next(R[2],advance1,row));
 const token=forbidden=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?(forbidden&&y==="1"?retry:mv(Q,1,advance2)):reject)):reject);
 const any=token(false),all=token(true);
 bind(row,rd(R[0],x=>x==="0"?any:x==="1"?rd(R[1],y=>y==="0"?any:y==="1"?rd(R[2],z=>z==="0"?any:z==="1"?all:reject):reject):reject));
 const beginRows=start(R[0],start(R[1],start(R[2],row)));
 const load3=label(),load2=label(),load1=label(),kind=label();
 function load(slot,d){return clear(R[slot],rd(D,x=>symbols.includes(x)?chosen(G[symbols.indexOf(x)],R[slot],mv(D,1,d)):reject));}
 bind(load3,load(2,beginRows));bind(load2,load(1,kind));bind(load1,load(0,load2));
 bind(kind,rd(D,x=>x==="0"?mv(D,1,clear(R[2],app(R[2],"1",beginRows))):x==="1"?mv(D,1,load3):reject));
 bind(dispatch,rd(D,x=>x==="_"?finish:symbols.includes(x)?load1:reject));
 const scopes=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)scopes.push(symbols[i]+symbols[j]+"0");
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let k=j+1;k<9;k++)scopes.push(symbols[i]+symbols[j]+"1"+symbols[k]);
 // Arc consistency: domains are 0/1 words before candidate selection.
 // For each pair compute both support vectors using the old pair domains,
 // then replace both domains. A single bit records any deletion in a pass.
 const pass=label(),pair=label(),pairLoad2=label(),pairKind=label(),pairRow=label(),pairNext=label(),pairCarry=label(),pairEnd=label(),writeFirst=label(),writeSecond=label(),propDone=label(),candidateStart=label();
 function zeros(a,b,d){return start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,"0",mv(a,1,n)):reject)));}
 function rewindPair(d){return start(R[0],start(R[1],start(V[0],start(V[1],d))));}
 const advanceD=mv(D,1,pair);
 // D at kind marker; return to group ids for the writeback.
 const writeBack=mv(D,-1,mv(D,-1,writeFirst));
 bind(pairEnd,rd(Q,x=>x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,writeBack),reject)):reject));
 bind(pairCarry,mv(R[0],1,mv(V[0],1,rd(R[0],x=>x==="_"?pairEnd:bit(x)?pairRow:reject))));
 bind(pairNext,mv(R[1],1,mv(V[1],1,rd(R[1],x=>x==="_"?start(R[1],start(V[1],pairCarry)):bit(x)?pairRow:reject))));
 const supported=wr(V[0],"1",wr(V[1],"1",pairNext));
 const pairToken=allowed=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?mv(Q,1,allowed&&y==="0"?supported:pairNext):reject)):reject);
 const pt0=pairToken(false),pt1=pairToken(true);
 bind(pairRow,rd(R[0],x=>x==="0"?pt0:x==="1"?rd(R[1],y=>y==="0"?pt0:y==="1"?pt1:reject):reject));
 const prep=clear(V[0],zeros(R[0],V[0],clear(V[1],zeros(R[1],V[1],rewindPair(pairRow)))));
 // First triple encountered ends this pass; its mask is not read.
 bind(pairKind,rd(D,x=>x==="0"?prep:x==="1"?propDone:reject));
 function loadDomain(slot,d){return clear(R[slot],rd(D,x=>symbols.includes(x)?copy(G[symbols.indexOf(x)],R[slot],mv(D,1,d)):reject));}
 bind(pairLoad2,loadDomain(1,pairKind));bind(pair,loadDomain(0,pairLoad2));
 function update(t,v,d){
  const scan=[label(),label()];
  for(let seen=0;seen<2;seen++)bind(scan[seen],rd(v,x=>x==="_"?(seen?test(t,y=>y==="_",d,reject):reject):bit(x)?rd(t,y=>!bit(y)||x==="1"&&y==="0"?reject:(()=>{
   const cont=mv(v,1,mv(t,1,scan[seen||+(x==="1")]));
   return x===y?cont:wr(t,"0",start(A,wr(A,"1",cont)));
  })()):reject));
  return start(t,start(v,scan[0]));
 }
 function putDomain(v,d){return rd(D,x=>symbols.includes(x)?update(G[symbols.indexOf(x)],v,mv(D,1,d)):reject);}
 bind(writeFirst,putDomain(V[0],writeSecond));bind(writeSecond,putDomain(V[1],advanceD));
 let skip=start(D,pair);for(let j=0;j<11;j++)skip=field(null,skip);
 bind(pass,start(A,wr(A,"0",start(Q,skip))));
 bind(propDone,start(A,rd(A,x=>x==="1"?pass:x==="0"?candidateStart:reject)));
 // Radius <=2 among first/second allowed ranks. A is a little-endian
 // 9-bit counter; only words of Hamming weight <=2 enter a trial.
 const check=label(),inc=label();
 const count=[label(),label(),label()];
 for(let k=0;k<=2;k++)bind(count[k],rd(A,x=>x==="_"?attempt:x==="0"?mv(A,1,count[k]):x==="1"?k===2?inc:mv(A,1,count[k+1]):reject));
 bind(check,start(A,count[0]));
 bind(inc,start(A,loop(n=>rd(A,x=>x==="0"?wr(A,"1",check):x==="1"?app(A,"0",n):reject))));
 bind(retry,inc);
 let trial=start(D,dispatch);
 function mark(t,d,second){
  const seen=[label(),label(),label()],need=second?2:1;
  for(let k=0;k<=need;k++)bind(seen[k],rd(t,x=>x==="_"?(k===need?d:k===0?reject:retry):domain(x)?wr(t,x==="0"?"0":k===need-1?"x":"1",mv(t,1,seen[Math.min(need,k+ +(x!=="0"))])):reject));
  return start(t,seen[0]);
 }
 for(let t of G.slice().reverse()){const d=mv(A,1,trial);trial=rd(A,x=>x==="0"?mark(t,d,false):x==="1"?mark(t,d,true):reject);}
 let skipCandidate=start(A,trial);for(let j=0;j<11;j++)skipCandidate=field(null,skipCandidate);
 bind(attempt,start(Q,skipCandidate));
 bind(candidateStart,clear(A,word(A,"000000000",attempt)));
 // Load unary domains once; pass and candidate scans never alter Q.
 function unary(t,d){const seen=[label(),label()];for(let k=0;k<=1;k++)bind(seen[k],rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?app(t,y==="0"?"1":"0",mv(Q,1,seen[k||+(y==="0")])):reject)):x==="1"&&k===1?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));return start(t,seen[0]);}
 let init=start(A,word(A,"0",pass));for(let t of G.slice().reverse())init=unary(t,init);
 const entry=start(D,word(D,scopes.join(""),start(Q,field(null,start(P,field(P,init))))));
 return {alphabet,ins,tapes:19,entry,witnessTape:X,streamTape:Q};
}

function executeIR(J,inputs){
 const T=inputs.map(s=>["L",...s,"_"]),h=T.map(()=>0);let pc=J.entry,steps=0,jumps=0;
 while(true){const a=J.ins[pc];if(a.op==="halt"||a.op==="reject")return {status:a.op,steps,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h};if(a.op==="jump"){if(++jumps>10000000)throw Error("jump limit");pc=a.next;continue;}if(++steps>10000000)throw Error("step limit");const k=a.t,x=T[k][h[k]];
  if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
  if(a.op==="write"){if(x==="L")throw Error("sentinel");T[k][h[k]]=a.next.v;}
  else if(a.op==="move"){h[k]+=a.next.dir;if(h[k]<0)throw Error("left");if(h[k]===T[k].length)T[k].push("_");}else throw Error("op");pc=a.next.d;
 }
}

function stream(E,raw){
 const d=E.decode(raw);if(!d)throw Error("normalized precondition");
 const groups=[0,1,2,3,4,5,6,7,8],fields=[(d.m-1).toString(2).split("").reverse().join(""),d.pins.join("")];
 for(let k=1;k<=3;k++)for(const h of E.subsets(groups,k)){const f=d.F.find(x=>x.h.join()===h.join());fields.push([...E.tup(d.m,k)].map(z=>f&&!f.S.has(z.join())?"1":"0").join(""));}
 return fields.map(s=>[...s].map(x=>"0"+x).join("")+"10").join("");
}
module.exports={machine,executeIR,stream};
