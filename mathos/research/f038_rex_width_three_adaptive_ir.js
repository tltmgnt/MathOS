// F038-REX-024D5H: optional first-allowed rank selection for genuine admitted D2C checkpoints.
// Adaptive mode tests exactly one candidate; failure is refusal, never general UNSAT.
// Refusal (blank) is not a general UNSAT claim. 16-tape compact layout.
function machine(adaptive=false){
 const alphabet=["L","0","1",":",";","|","_",",","x","H","b"],ins=[],symbols=alphabet.filter(x=>x!=="L"&&x!=="_");
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const Q=15,G=Array.from({length:9},(_,i)=>i+1),R=[10,11,12],D=13,P=14,X=0;
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 const copy=(a,b,d)=>start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,x,mv(a,1,n)):reject)));
 function field(out,d){return loop(n=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?(out===null?mv(Q,1,n):app(out,y,mv(Q,1,n))):reject)):x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));}
 // Generate original X words and cumulative Y words only after every mask passes.
 const done=start(X,halt),tail=copy(P,X,word(X,"00",done));
 function cumulative(t,d){
  const before=label(),after=label();
  bind(before,rd(t,x=>x==="_"?d:bit(x)?app(X,x,mv(t,1,x==="1"?after:before)):reject));
  bind(after,rd(t,x=>x==="_"?d:bit(x)?app(X,"1",mv(t,1,after)):reject));
  // omit rank-zero Y; if X0=1, all subsequent Y bits are one.
  return start(t,rd(t,x=>bit(x)?mv(t,1,x==="1"?after:before):reject));
 }
 let emit=tail;for(let t of G.slice().reverse())emit=cumulative(t,emit);
 for(let t of G.slice().reverse())emit=copy(t,X,emit);
 emit=start(X,emit);
 const finish=test(Q,x=>x==="_",emit,reject);
 const dispatch=label(),row=label(),advance0=label(),advance1=label(),advance2=label();
 // A pair uses a one-symbol third rank word. All other words are nonempty one-hot.
 function next(t,carry,normal){return mv(t,1,rd(t,x=>x==="_"?start(t,carry):bit(x)?normal:reject));}
 const end=rd(Q,x=>x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,dispatch),reject)):reject);
 bind(advance0,next(R[0],end,row));bind(advance1,next(R[1],advance0,row));bind(advance2,next(R[2],advance1,row));
 const token=forbidden=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)&&!(forbidden&&y==="1")?mv(Q,1,advance2):reject)):reject);
 const any=token(false),all=token(true);
 bind(row,rd(R[0],x=>x==="0"?any:x==="1"?rd(R[1],y=>y==="0"?any:y==="1"?rd(R[2],z=>z==="0"?any:z==="1"?all:reject):reject):reject));
 const beginRows=start(R[0],start(R[1],start(R[2],row)));
 const load3=label(),load2=label(),load1=label(),kind=label();
 function load(slot,d){return clear(R[slot],rd(D,x=>symbols.includes(x)?copy(G[symbols.indexOf(x)],R[slot],mv(D,1,d)):reject));}
 bind(load3,load(2,beginRows));bind(load2,load(1,kind));bind(load1,load(0,load2));
 bind(kind,rd(D,x=>x==="0"?mv(D,1,clear(R[2],app(R[2],"1",beginRows))):x==="1"?mv(D,1,load3):reject));
 bind(dispatch,rd(D,x=>x==="_"?finish:symbols.includes(x)?load1:reject));
 const scopes=[];for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)scopes.push(symbols[i]+symbols[j]+"0");
 for(let i=0;i<9;i++)for(let j=i+1;j<9;j++)for(let k=j+1;k<9;k++)scopes.push(symbols[i]+symbols[j]+"1"+symbols[k]);
 let entry=start(D,word(D,scopes.join(""),start(D,dispatch)));
 // Consume unary masks and prove each has exactly one allowed bit.
 function unary(t,d){
  const seen=[label(),label()];
  for(let k=0;k<2;k++)bind(seen[k],rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>y==="1"?app(t,"0",mv(Q,1,seen[k])):y==="0"&&k===0?app(t,"1",mv(Q,1,seen[1])):y==="0"&&adaptive?app(t,"0",mv(Q,1,seen[1])):reject)):x==="1"&&k===1?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,d),reject)):reject));
  return start(t,seen[0]);
 }
 for(let t of G.slice().reverse())entry=unary(t,entry);
 entry=start(Q,field(null,start(P,field(P,entry))));
 return {alphabet,ins,tapes:16,entry,witnessTape:X,streamTape:Q};
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
