// D5N: reversible run-token decoding in the physical worker; four zeros per 11.
function machine(full=false){
 const alphabet=["L","0","_","1","x"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const Q=19,A=15,V=[16,17,18],G=Array.from({length:9},(_,i)=>i+1),R=[10,11,12],D=13,P=14,X=0;
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
 // Exactly one row can match a one-hot candidate. On a passing match,
 // consume the remaining field tokens without rank-cursor updates.
 // Skip the remaining whole tokens after the selected tuple. Run tokens
 // are restored before entering this routine, including an interrupted run.
 function skipMask(d){return loop(n=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?mv(Q,1,n):reject)):x==="1"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,1,d):y==="1"?mv(Q,1,n):reject)):reject));}
 const suffix=skipMask(dispatch);
 // A run's first/second cells encode four successive zero emissions:
 // 11 -> x0 -> x1 -> xx -> 11 (advance). Q returns to the first cell
 // between emissions, except after the fourth or a selected tuple.
 function maskToken(zero,one,early=false){
  const finish=wr(Q,"1",mv(Q,-1,wr(Q,"1",mv(Q,1,mv(Q,1,zero)))));
  const phase=y=>early?finish:y==="0"?wr(Q,"1",mv(Q,-1,zero)):y==="1"?wr(Q,"x",mv(Q,-1,zero)):y==="x"?finish:reject;
  const first=early?mv(Q,1,zero):wr(Q,"0",mv(Q,-1,wr(Q,"x",zero)));
  return rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,1,zero):y==="1"?mv(Q,1,one):reject)):x==="1"?mv(Q,1,rd(Q,y=>y==="1"?first:reject)):x==="x"?mv(Q,1,rd(Q,phase)):reject);
 }
 const token=forbidden=>forbidden?maskToken(suffix,retry,true):maskToken(advance2,advance2);
 const any=token(false),all=token(true);
 bind(row,rd(R[0],x=>x==="0"?any:x==="1"?rd(R[1],y=>y==="0"?any:y==="1"?rd(R[2],z=>z==="0"?any:z==="1"?all:reject):reject):reject));
 const beginRows=start(R[0],start(R[1],start(R[2],row)));
 const load3=label(),load2=label(),load1=label(),kind=label();
 // Fixed-width binary scope IDs consume exactly four tape cells.
 function idRead(choose,p=""){return p.length===4?(parseInt(p,2)<9?choose(parseInt(p,2)):reject):rd(D,x=>bit(x)?mv(D,1,idRead(choose,p+x)):reject);}
 function load(slot,d){return clear(R[slot],idRead(g=>chosen(G[g],R[slot],d)));}
 bind(load3,load(2,beginRows));bind(load2,load(1,kind));bind(load1,load(0,load2));
 bind(kind,rd(D,x=>x==="0"?mv(D,1,clear(R[2],app(R[2],"1",beginRows))):x==="1"?mv(D,1,load3):reject));
 // A flag is consumed at each scope dispatch. Skip only masks proved all-zero.
 function skipScope(d){
  let tail=rd(D,x=>x==="0"?mv(D,1,d):x==="1"?mv(D,1,walkD(4,d)):reject);
  return walkD(8,tail);
 }
 function walkD(k,d){while(k--)d=mv(D,1,d);return d;}
 function indexed(d,active,end){
  // 10 at the start of a higher-arity field denotes a universal relation.
  const inactive=skipScope(mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)));
  return rd(Q,x=>x==="1"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,-1,inactive):y==="1"?mv(Q,-1,active):reject)):x==="0"?active:x==="_"?test(D,y=>y==="_",end,reject):reject);
 }
 bind(dispatch,indexed(dispatch,load1,finish));
 const code=g=>g.toString(2).padStart(4,"0"),scopes=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)scopes.push(code(i)+code(j)+"0");
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let k=j+1;k<9;k++)scopes.push(code(i)+code(j)+"1"+code(k));
 // Bounded GAC: every scope projects all currently supported tuples.
 // For a pair the third rank and support scratch each have length one.
 const pass=label(),prop=label(),pLoad2=label(),pKind=label(),pLoad3=label(),pRow=label(),pNext=label(),pCarry1=label(),pCarry0=label(),pEnd=label(),writeFirst=label(),writeSecond=label(),writeKind=label(),writeThird=label(),propDone=label(),candidateStart=label();
 function zeros(a,b,d){return start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,"0",mv(a,1,n)):reject)));}
 // Prep must initialize supports before rewinding rank/support heads.
 const rewinds=R.reduceRight((d,t,i)=>start(t,start(V[i],d)),pRow);
 let prepared=rewinds;for(let i=2;i>=0;i--)prepared=clear(V[i],zeros(R[i],V[i],prepared));
 function adv(i,carry){return mv(R[i],1,mv(V[i],1,rd(R[i],x=>x==="_"?start(R[i],start(V[i],carry)):bit(x)?pRow:reject)));}
 bind(pNext,adv(2,pCarry1));bind(pCarry1,adv(1,pCarry0));bind(pCarry0,adv(0,pEnd));
 const supported=wr(V[0],"1",wr(V[1],"1",wr(V[2],"1",pNext)));
 const tokenP=allowed=>maskToken(allowed?supported:pNext,pNext);
 const pt0=tokenP(false),pt1=tokenP(true);
 bind(pRow,rd(R[0],x=>x==="0"?pt0:x==="1"?rd(R[1],y=>y==="0"?pt0:y==="1"?rd(R[2],z=>z==="0"?pt0:z==="1"?pt1:reject):reject):reject));
 function back(t,k,d){while(k--)d=mv(t,-1,d);return d;}
 // At record end, the third scratch length distinguishes pair and triple.
 const pairBack=back(D,9,writeFirst),tripleBack=back(D,13,writeFirst);
 const rewindD=start(R[2],mv(R[2],1,rd(R[2],x=>x==="_"?pairBack:bit(x)?tripleBack:reject)));
 bind(pEnd,rd(Q,x=>x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,rewindD),reject)):reject));
 function loadDomain(slot,d){return clear(R[slot],idRead(g=>copy(G[g],R[slot],d)));}
 bind(pLoad3,loadDomain(2,prepared));
 bind(pKind,rd(D,x=>x==="0"?mv(D,1,clear(R[2],app(R[2],"1",prepared))):x==="1"?mv(D,1,pLoad3):reject));
 bind(pLoad2,loadDomain(1,pKind));
 const pLoad1=loadDomain(0,pLoad2);
 bind(prop,indexed(prop,pLoad1,propDone));
 function update(t,v,d){
  const scan=[label(),label()];
  for(let seen=0;seen<2;seen++)bind(scan[seen],rd(v,x=>x==="_"?(seen?test(t,y=>y==="_",d,reject):reject):bit(x)?rd(t,y=>!bit(y)||x==="1"&&y==="0"?reject:(()=>{
   const cont=mv(v,1,mv(t,1,scan[seen||+(x==="1")]));
   return x===y?cont:wr(t,"0",start(A,wr(A,"1",cont)));
  })()):reject));
  return start(t,start(v,scan[0]));
 }
 function putDomain(v,d){return idRead(g=>update(G[g],v,d));}
 bind(writeFirst,putDomain(V[0],writeSecond));bind(writeSecond,putDomain(V[1],writeKind));
 bind(writeKind,rd(D,x=>x==="0"?mv(D,1,prop):x==="1"?mv(D,1,writeThird):reject));bind(writeThird,putDomain(V[2],prop));
 let skip=start(D,prop);for(let j=0;j<11;j++)skip=field(null,skip);
 bind(pass,start(A,wr(A,"0",start(Q,skip))));
 // A is change flag plus four budget slots. A changed pass consumes one
 // slot; the fourth changed pass ends at its resulting (possibly nonfixed) domains.
 const consume=loop(n=>rd(A,x=>x==="1"?mv(A,1,n):x==="0"?wr(A,"1",mv(A,1,rd(A,y=>y==="_"?candidateStart:y==="0"?pass:reject))):reject));
 bind(propDone,start(A,rd(A,x=>x==="1"?(full?pass:mv(A,1,consume)):x==="0"?candidateStart:reject)));
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
 let init=start(A,word(A,"00000",pass));for(let t of G.slice().reverse())init=unary(t,init);
 const entry=start(D,word(D,scopes.join(""),start(Q,field(null,start(P,field(P,init))))));
 return {alphabet,ins,tapes:20,entry,witnessTape:X,streamTape:Q};
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
 return fields.map((s,i)=>{if(i>=11&&!s.includes("1"))return "10";let out="";for(let k=0;k<s.length;){if(i>=11&&s.slice(k,k+4)==="0000"){out+="11";k+=4;}else out+="0"+s[k++];}return out+"10";}).join("");
}
module.exports={machine,executeIR,stream};
