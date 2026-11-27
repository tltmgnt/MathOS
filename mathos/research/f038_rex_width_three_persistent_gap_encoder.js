// D5V headerless physical gap encoder. Rank domains independently determine mask length.
function machine(decode=false){if(decode)throw Error('headerless encoder only');
 const alphabet=["L","0","_","1","x"],ins=[],X=0,N=1,G=2,C=3,Q=4;
 const add=(op,t,next)=>{let i=ins.length;ins.push({op,t,next});return i;},label=()=>add("jump",0,-1),bind=(n,d)=>{ins[n].next=d;},halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 const copy=(a,b,d)=>start(a,loop(n=>rd(a,x=>x==="_"?d:bit(x)?app(b,x,mv(a,1,n)):reject)));
 const inc=(t,d)=>start(t,loop(n=>rd(t,x=>x==="1"?app(t,"0",n):x==="0"||x==="_"?wr(t,"1",d):reject)));
 // Canonical LSB-first counter: zero is empty; trim a newly zero MSB.
 const dec=(t,d)=>start(t,loop(n=>rd(t,x=>x==="0"?app(t,"1",n):x==="1"?wr(t,"0",mv(t,1,rd(t,y=>y==="_"?mv(t,-1,wr(t,"_",d)):bit(y)?d:reject))):reject)));
 const empty=(t,y,n)=>start(t,test(t,x=>x==="_",y,n));
 // Emit gamma of a positive LSB-first counter, without changing it.
 function gamma(t,out,d){
  const reverse=loop(n=>rd(t,x=>x==="L"?d:bit(x)?app(out,x,mv(t,-1,n)):reject));
  const scan=loop(n=>rd(t,x=>x==="_"?mv(t,-1,reverse):bit(x)?app(out,"0",mv(t,1,n)):reject));
  return start(t,test(t,bit,mv(t,1,scan),reject));
 }
 // Parse gamma from Q, building LSB-first counter t directly. t is empty.
 function parse(t,d){
  const tail=loop(n=>rd(t,x=>x==="L"?d:bit(x)?rd(Q,y=>bit(y)?wr(t,y,mv(Q,1,mv(t,-1,n))):reject):reject));
  return start(t,loop(n=>rd(Q,x=>x==="0"?app(t,"0",mv(Q,1,n)):x==="1"?wr(t,"1",mv(Q,1,mv(t,-1,tail))):reject)));
 }
 const done=start(X,halt);let entry;
 if(!decode){
  const scan=label(),compare=label();
  const dense=app(X,"0",copy(Q,X,done)),sparse=app(X,"1",copy(C,X,done));
  bind(compare,rd(C,x=>x==="_"?sparse:bit(x)?rd(Q,y=>y==="_"?dense:bit(y)?mv(C,1,mv(Q,1,compare)):reject):reject));
  const finish=start(C,start(Q,compare));
  const emit=gamma(G,C,clear(G,mv(Q,1,scan)));
  bind(scan,rd(Q,x=>x==="_"?finish:x==="0"?inc(G,mv(Q,1,scan)):x==="1"?inc(G,emit):reject));
  entry=start(X,start(C,start(Q,scan)));
 }else{
  const dense=label(),next=label(),gap=label(),trail=label(),afterDec=label();
  bind(dense,empty(N,test(Q,x=>x==="_",done,reject),rd(Q,x=>bit(x)?app(X,x,mv(Q,1,dec(N,dense))):reject)));
  bind(trail,empty(N,done,app(X,"0",dec(N,trail))));
  bind(next,rd(Q,x=>x==="_"?trail:bit(x)?parse(G,gap):reject));
  bind(gap,empty(N,reject,dec(G,afterDec)));
  bind(afterDec,empty(G,app(X,"1",dec(N,next)),app(X,"0",dec(N,gap))));
  const mode=rd(Q,x=>x==="0"?mv(Q,1,dense):x==="1"?mv(Q,1,next):reject);
  entry=start(X,start(Q,parse(N,dec(N,mode))));
 }
 return {alphabet,ins,tapes:5,entry};
}
module.exports={machine};
