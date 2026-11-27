// D5X: compare gamma payload against run token count, bypass short fields.
function machine(W,Gap,full=false){
 const worker=W.machine(full),alphabet=worker.alphabet,ins=worker.ins.map(i=>({...i})),S=21,Q=19,R=1,C=2,N=3,G=4,K=5,T=6;
 // Input S is cleared before the worker reuses it as countdown.
 const reject=ins.findIndex(i=>i.op==="reject"),add=(op,t,next)=>{let i=ins.length;ins.push({op,t,next});return i;},label=()=>add("jump",0,-1),bind=(n,d)=>{ins[n].next=d;};
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n))),app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 const clears=(ts,d)=>ts.reduceRight((next,t)=>clear(t,next),d);
 function splice(J,map,done){
  const ids=J.ins.map(()=>label());J.ins.forEach((i,j)=>{let d;
   if(i.op==="halt")d=done;else if(i.op==="reject")d=reject;else if(i.op==="jump")d=ids[i.next];else if(i.op==="read")d=add("read",map[i.t],i.next.map(k=>ids[k]));else if(i.op==="move")d=mv(map[i.t],i.next.dir,ids[i.next.d]);else if(i.op==="write")d=wr(map[i.t],i.next.v,ids[i.next.d]);else throw Error("op");bind(ids[j],d);
  });return ids[J.entry];
 }
 const field=label(),load=label(),finish=clears([R,C,N,G,K,S],clearToken(worker.entry));
 function clearToken(d){return start(T,loop(n=>rd(T,x=>x==="_"?start(T,d):bit(x)||x==="x"?app(T,"_",n):reject)));}
 const cleanup=clears([R,C,N,G,K],clearToken(field));
 const runEnd=word(Q,"10",cleanup);
 const runEmit=loop(n=>rd(T,x=>x==="_"?runEnd:x==="x"?word(Q,"11",mv(T,1,n)):bit(x)?word(Q,"0"+x,mv(T,1,n)):reject));
 const fallback=word(Q,"00",start(T,runEmit));
 const emit=loop(n=>rd(C,x=>x==="_"?word(Q,"10",cleanup):bit(x)?word(Q,"0"+x,mv(C,1,n)):reject));
 const compare=label();
 // Gamma only if at least a factor-two payload-token saving.
 bind(compare,rd(C,x=>x==="_"?start(C,emit):bit(x)?rd(T,y=>y==="_"?fallback:mv(T,1,rd(T,z=>z==="_"?fallback:mv(T,1,mv(C,1,compare))))):reject));
 const choose=start(C,rd(C,x=>x==="0"?fallback:x==="1"?mv(C,1,start(T,compare)):reject));
 const encode=splice(Gap.machine(),[C,N,G,K,R],choose);
 const expand=loop(n=>rd(T,x=>x==="_"?encode:x==="x"?word(R,"0000",mv(T,1,n)):bit(x)?app(R,x,mv(T,1,n)):reject));
 const long=start(T,expand);
 // Count up to 17 tokens in finite control; small fields never invoke encoder.
 const scan=Array.from({length:18},()=>label());
 for(let k=0;k<18;k++){
  const next=scan[Math.min(k+1,17)],end=k<=16?fallback:long;
  bind(scan[k],rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,app(T,y,next)):reject)):x==="1"?mv(S,1,rd(S,y=>y==="1"?mv(S,1,app(T,"x",next)):y==="0"?mv(S,1,end):reject)):reject));
 }
 bind(load,scan[0]);
 bind(field,rd(S,x=>x==="_"?finish:x==="0"?load:x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,word(Q,"10",field)):y==="1"?mv(S,-1,load):reject)):reject));
 let next=field;for(let i=0;i<11;i++){const end=word(Q,"10",next),scan=label();bind(scan,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,word(Q,"0"+y,scan)):reject)):x==="1"?mv(S,1,test(S,y=>y==="0",mv(S,1,end),reject)):reject));next=scan;}
 return {...worker,ins,entry:start(Q,start(R,start(T,start(S,next)))),streamTape:S,canonicalTape:Q};
}
module.exports={machine};
