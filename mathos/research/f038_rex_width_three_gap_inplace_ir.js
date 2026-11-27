// D5U in-place physical gap roundtrip: no second complete mask stream.
// Reconstruct each active field in its original tape interval before GAC.
function machine(W,Gap,full=false){
 const worker=W.machine(full),alphabet=worker.alphabet,ins=worker.ins.map(i=>({...i})),S=19,Q=19,R=1,C=2,N=3,G=4,K=5,B=6;
 const reject=ins.findIndex(i=>i.op==="reject"),add=(op,t,next)=>{let i=ins.length;ins.push({op,t,next});return i;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 const clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):bit(x)?app(t,"_",n):reject)));
 function clears(ts,d){return ts.reduceRight((next,t)=>clear(t,next),d);}
 function splice(J,map,done,budget=false){
  const ids=J.ins.map(()=>label());
  J.ins.forEach((i,j)=>{
   let dest;
   if(i.op==="halt")dest=budget?test(B,x=>x==="_",done,reject):done;
   else if(i.op==="reject")dest=reject;
   else if(i.op==="jump")dest=ids[i.next];
   else if(i.op==="read")dest=add("read",map[i.t],i.next.map(k=>ids[k]));
   else if(i.op==="move")dest=mv(map[i.t],i.next.dir,ids[i.next.d]);
   else if(i.op==="write"){
    dest=wr(map[i.t],i.next.v,ids[i.next.d]);
    if(budget&&i.t===0)dest=test(B,x=>x==="1",mv(B,1,dest),reject);
   }else throw Error("op");
   bind(ids[j],dest);
  });return ids[J.entry];
 }
 const field=label(),load=label();
 const finish=clears([R,C,N,G,K,B],worker.entry);
 // The producer is canonical. Verify each reconstructed token against
 // the original before writing it. This prevents overwriting the next
 // field if the codec ever returns a different length or content.
 function checked(s,d){for(let i=s.length-1;i>=0;i--)d=test(Q,x=>x===s[i],app(Q,s[i],d),reject);return d;}
 const emitEnd=checked("10",clears([R,C,N,G,K,B],field));
 const run=Array.from({length:4},()=>label());
 for(let k=0;k<4;k++){
  const flush="00".repeat(k);
  bind(run[k],rd(R,x=>x==="_"?checked(flush,emitEnd):x==="1"?checked(flush+"01",mv(R,1,run[0])):x==="0"?mv(R,1,k===3?checked("11",run[0]):run[k+1]):reject));
 }
 // Rewind two-cell tokens to the preceding field delimiter, not to
 // the tape origin. The active field always has a preceding field.
 const rewind=label(),left2=d=>mv(Q,-1,mv(Q,-1,d));
 bind(rewind,rd(Q,x=>x==="0"?left2(rewind):x==="1"?mv(Q,1,rd(Q,y=>y==="0"?mv(Q,1,start(R,run[0])):y==="1"?mv(Q,-1,left2(rewind)):reject)):reject));
 const decodeExit=left2(left2(rewind));
 const decode=splice(Gap.machine(true),[R,N,G,K,C],decodeExit,true);
 const budgetEntry=start(B,decode);
 const afterEncode=clears([R,N,G,K],budgetEntry);
 const encode=splice(Gap.machine(false),[C,N,G,K,R],afterEncode);
 function raw(s,d){for(let i=s.length-1;i>=0;i--)d=app(R,s[i],app(B,"1",d));return d;}
 bind(load,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,raw(y,load)):reject)):x==="1"?mv(S,1,rd(S,y=>y==="1"?mv(S,1,raw("0000",load)):y==="0"?mv(S,1,encode):reject)):reject));
 bind(field,rd(S,x=>x==="_"?finish:x==="0"?load:x==="1"?mv(S,1,rd(S,y=>y==="0"?mv(S,1,field):y==="1"?mv(S,-1,load):reject)):reject));
 let next=field;
 for(let i=0;i<11;i++){
  const end=next,scan=label();
  bind(scan,rd(S,x=>x==="0"?mv(S,1,rd(S,y=>bit(y)?mv(S,1,scan):reject)):x==="1"?mv(S,1,test(S,y=>y==="0",mv(S,1,end),reject)):reject));
  next=scan;
 }
 const entry=start(R,start(B,start(S,next)));
 return {...worker,ins,tapes:20,entry,streamTape:S,canonicalTape:Q,budgetEntry,decodeExit};
}
module.exports={machine};
