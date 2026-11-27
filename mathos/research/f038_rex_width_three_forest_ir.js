// REX-024D3B1: shared finite-control local enumeration and retained forest semijoins.
function machine(router,cursor,projection){
 const J=router.machine(cursor),alphabet=J.alphabet,ins=J.ins.map(a=>a.op==="read"?{...a,next:a.next.slice()}:a.op==="write"||a.op==="move"?{...a,next:{...a.next}}:{...a});
 const halt=0,reject=1,add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const W=10,B=11,S=12,O=17,K=21,rels=Array.from({length:9},(_,i)=>22+i),H=31,T=32,V=33,base=34,P=34,C=35,PM=41,CM=42,U=43,decision=44;
 function walk(t,dir,k,d){while(k--)d=mv(t,dir,d);return d;}
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const seek=(t,k,d)=>start(t,walk(t,1,k,d)),app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 function copyN(a,b,n,d){while(n--){let next=d;d=rd(a,x=>bit(x)?app(b,x,mv(a,1,next)):reject);}return d;}
 function readN(t,n,choose){function f(p){return p.length===n?choose(parseInt(p,2)):rd(t,x=>bit(x)?mv(t,1,f(p+x)):reject);}return f("");}
 function clear(t,d){return start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):x==="L"?reject:app(t,"_",n))));}
 function copy(a,b,d){return start(a,start(b,loop(n=>rd(a,x=>x==="_"?d:x==="L"?reject:app(b,x,mv(a,1,n))))));}
 const reset=(t,d)=>start(t,word(t,"0".repeat(9),d)),set=(t,v,d)=>seek(t,v,wr(t,"1",d));
 const localDone=label(),edge=label(),afterJoin=label();
 // Append D1B's exact finite program, statically remapping ten tapes.
 const J2=projection.machine(),off=ins.length;
 for(let a of J2.ins){
  const dest=d=>d===0?afterJoin:d===1?reject:off+d;
  ins.push(a.op==="read"?{...a,t:a.t+base,next:alphabet.map(x=>J2.alphabet.includes(x)?dest(a.next[J2.alphabet.indexOf(x)]):reject)}:a.op==="write"||a.op==="move"?{...a,t:a.t+base,next:{...a.next,d:dest(a.next.d)}}:a.op==="jump"?{...a,next:dest(a.next)}:{...a});
 }
 const mergeEntry=off+J2.entry;
 // Intercept only the router's original successful exit to scratch cleanup.
 const hook=label();
 for(let i=0;i<J.ins.length;i++){let a=ins[i];const dest=d=>d===J.cleanupEntry?hook:d===halt?localDone:d;
  if(a.op==="read")a.next=a.next.map(dest);
  else if(a.op==="write"||a.op==="move")a.next.d=dest(a.next.d);
  else if(a.op==="jump")a.next=dest(a.next);
 }
 // Record owner nibble for local output and table addressing. H is
 // a sequential stream of 20-bit records (owner, neighbors, parent).
 const saveTable=start(W,readN(W,4,v=>v<9?seek(T,9*v,start(B,copyN(B,T,9,J.cleanupEntry))):reject));
 bind(hook,start(W,copyN(W,H,20,start(W,start(V,copyN(W,V,4,saveTable))))));
 // Local loop: write O to its owner-indexed retained relation.
 const edgesStart=start(H,start(decision,word(decision,"1",edge)));
 let nextBag=J.entry;for(let t of [...Array(19).keys(),V].reverse())nextBag=clear(t,nextBag);
 function ordinal(n){return rd(K,x=>x==="_"&&n<9?nextBag:x==="_"&&n===9?edgesStart:x==="1"&&n<9?mv(K,1,ordinal(n+1)):reject);}
 const increment=start(K,loop(n=>rd(K,x=>x==="_"?app(K,"1",start(K,ordinal(0))):x==="1"?mv(K,1,n):reject)));
 bind(localDone,start(V,readN(V,4,v=>v<9?copy(O,rels[v],increment):reject)));
 // H remains positioned after the current record while edge operations
 // use W. Preserve child relation, replace only parent with U.
 bind(afterJoin,seek(W,16,readN(W,4,v=>v<9?clear(rels[v],copy(U,rels[v],edge)):reject)));
 function mask(out,d){
  const n=label(),yes=rd(S,x=>bit(x)?app(out,x,mv(B,1,mv(S,1,n))):reject);
  bind(n,rd(B,x=>x==="_"?d:x==="0"?mv(B,1,mv(S,1,n)):x==="1"?yes:reject));
  return start(B,start(S,start(out,n)));
 }
 const parentMask=mask(PM,mergeEntry);
 const parentLoad=seek(W,16,readN(W,4,v=>v<9?copy(rels[v],P,seek(T,9*v,start(B,copyN(T,B,9,parentMask)))):reject));
 const childMask=mask(CM,parentLoad);
 const childLoad=start(W,readN(W,4,v=>v<9?copy(rels[v],C,seek(T,9*v,start(B,copyN(T,B,9,childMask)))):reject));
 let sep=childLoad;for(let j=3;j>=1;j--){let d=sep;sep=seek(W,4*j,readN(W,4,v=>v<9?set(S,v,d):v===9?d:reject));}
 let nonroot=reset(S,sep);for(let t=43;t>=34;t--)nonroot=clear(t,nonroot);
 // Root emptiness updates a persistent decision bit; never skips other components.
 const root=start(W,readN(W,4,v=>v<9?start(rels[v],test(rels[v],x=>x==="_",start(decision,wr(decision,"0",edge)),edge)):reject));
 const dispatch=seek(W,16,readN(W,4,v=>v===9?root:v<9?nonroot:reject));
 bind(edge,test(H,x=>x==="_",halt,start(W,copyN(H,W,20,dispatch))));
 const entry=start(H,start(T,word(T,"0".repeat(81),J.entry)));
 return{alphabet,tapes:45,ins,entry,localDone,edge,afterJoin};
}
module.exports={machine};
