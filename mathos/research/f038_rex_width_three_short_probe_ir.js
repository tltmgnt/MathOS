// D5Z: probe original tokens before allocating field scratch.
function machine(W,Gap,full=false){
 const worker=W.machine(full),alphabet=worker.alphabet,ins=worker.ins.map(i=>({...i})),S=21,Q=21,R=1,C=2,N=3,G=4,K=5,T=6;
 // S is the persistent stream; short fields remain entirely untouched.
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
 const field=label(),load=label(),finish=worker.entry;
 function clearToken(d){return start(T,loop(n=>rd(T,x=>x==="_"?start(T,d):bit(x)||x==="x"?app(T,"_",n):reject)));}
 const cleanup=clears([R,C,G,K],clearToken(field));
 const fallback=cleanup;
 // Replace remaining old two-cell tokens by padding xx, preserve 10.
 const pad=loop(n=>rd(Q,x=>x==="0"?wr(Q,"x",mv(Q,1,rd(Q,y=>bit(y)?wr(Q,"x",mv(Q,1,n)):reject))):x==="1"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,1,cleanup):y==="1"?wr(Q,"x",mv(Q,-1,wr(Q,"x",mv(Q,1,mv(Q,1,n))))):reject)):reject));
 // Gamma payload is written within the original interval, checked
 // against each original non-delimiter token before replacement.
 function replaceToken(v,d){
  const emit=word(Q,v,d);
  return rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?mv(Q,-1,emit):reject)):x==="1"?mv(Q,1,test(Q,y=>y==="1",mv(Q,-1,emit),reject)):reject);
 }
 const emit=loop(n=>rd(C,x=>x==="_"?pad:bit(x)?replaceToken("0"+x,mv(C,1,n)):reject));
 const first=replaceToken("xx",start(C,mv(C,1,emit)));
 // At S immediately after original delimiter, rewind whole tokens
 // until preceding delimiter, then write marker and selected payload.
 const left2=d=>mv(Q,-1,mv(Q,-1,d));
 const rewind=loop(n=>rd(Q,x=>x==="0"?left2(n):x==="1"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,1,first):y==="1"?mv(Q,-1,left2(n)):reject)):reject));
 const convert=left2(left2(rewind));
 const compare=label();
 bind(compare,rd(C,x=>x==="_"?convert:bit(x)?rd(T,y=>y==="_"?fallback:mv(T,1,rd(T,z=>z==="_"?fallback:mv(T,1,mv(C,1,compare))))):reject));
 const choose=start(C,rd(C,x=>x==="0"?fallback:x==="1"?mv(C,1,start(T,compare)):reject));
 const encode=splice(Gap.machine(),[C,N,G,K,R],choose);
 const expand=loop(n=>rd(T,x=>x==="_"?encode:x==="x"?word(R,"0000",mv(T,1,n)):bit(x)?app(R,x,mv(T,1,n)):reject));
 const long=start(T,expand);
 // Short fields are skipped without even writing the compact scratch.
 // On the 17th token rewind to the prior delimiter, then collect once.
 const collect=label();
 const rewindLoad=loop(n=>rd(S,x=>x==="0"?left2(n):x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,collect):y==="1"?mv(S,-1,left2(n)):reject)):reject));
 let probe=left2(rewindLoad);
 for(let k=16;k>=0;k--){const next=probe;probe=rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,next):reject)):x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,field):y==="1"?mv(S,1,next):reject)):reject);}
 bind(load,probe);
 bind(collect,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,app(T,y,collect)):reject)):x==="1"?mv(S,1,rd(S,y=>y==="1"?mv(S,1,app(T,"x",collect)):y==="0"?mv(S,1,long):reject)):reject));
 bind(field,rd(S,x=>x==="_"?finish:x==="0"?load:x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,field):y==="1"?mv(S,-1,load):reject)):reject));
 let next=field;for(let i=0;i<11;i++){const end=next,scan=label();bind(scan,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,scan):reject)):x==="1"?mv(S,1,test(S,y=>y==="0",mv(S,1,end),reject)):reject));next=scan;}
 return {...worker,ins,entry:start(R,start(T,start(S,next))),streamTape:S,canonicalTape:Q};
}
module.exports={machine};
