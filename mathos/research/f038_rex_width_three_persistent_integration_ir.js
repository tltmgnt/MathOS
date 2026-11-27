// Physical canonical producer stream -> persistent framed fields -> direct GAC.
// The producer is unchanged. No decoded mask is reconstructed during GAC.
function machine(W,Gap,full=false){
 const worker=W.machine(full),alphabet=worker.alphabet,ins=worker.ins.map(i=>({...i})),S=21,Q=19,R=1,C=2,N=3,G=4,K=5;
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
 const field=label(),load=label(),finish=clears([R,C,N,G,K,S],worker.entry);
 const emit=loop(n=>rd(C,x=>x==="_"?word(Q,"10",clears([R,C,N,G,K],field)):bit(x)?word(Q,"0"+x,mv(C,1,n)):reject));
 const encode=splice(Gap.machine(),[C,N,G,K,R],start(C,emit));
 bind(load,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,word(R,y,load)):reject)):x==="1"?mv(S,1,rd(S,y=>y==="1"?mv(S,1,word(R,"0000",load)):y==="0"?mv(S,1,encode):reject)):reject));
 bind(field,rd(S,x=>x==="_"?finish:x==="0"?load:x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,word(Q,"10",field)):y==="1"?mv(S,-1,load):reject)):reject));
 let next=field;for(let i=0;i<11;i++){const end=word(Q,"10",next),scan=label();bind(scan,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,word(Q,"0"+y,scan)):reject)):x==="1"?mv(S,1,test(S,y=>y==="0",mv(S,1,end),reject)):reject));next=scan;}
 return {...worker,ins,entry:start(Q,start(R,start(S,next))),streamTape:S,canonicalTape:Q};
}
module.exports={machine};
