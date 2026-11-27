// REX-024D3B2: reverse elimination selection and original-layout witness on the retained forest IR.
function machine(forest,router,cursor,projection){
 const J=forest.machine(router,cursor,projection),alphabet=J.alphabet,ins=J.ins.map(a=>a.op==="read"?{...a,next:a.next.slice()}:a.op==="write"||a.op==="move"?{...a,next:{...a.next}}:{...a});
 const halt=0,reject=1,add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const M=0,W=10,B=11,S=12,Q=20,H=31,T=32,P=34,decision=44,chosen=Array.from({length:9},(_,i)=>45+i),G=54,temp=55,counter=56,X=57,Y=58,flag=59,first=60;
 const symbols=alphabet.filter(x=>x!=="L"&&x!=="_").join("");if(symbols.length!==9)throw Error("dispatcher");
 function walk(t,d,k,n){while(k--)n=mv(t,d,n);return n;}
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const seek=(t,k,d)=>start(t,walk(t,1,k,d)),app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 function copyN(a,b,n,d){while(n--){let next=d;d=rd(a,x=>bit(x)?app(b,x,mv(a,1,next)):reject);}return d;}
 function readN(t,n,choose){function f(p){return p.length===n?choose(parseInt(p,2)):rd(t,x=>bit(x)?mv(t,1,f(p+x)):reject);}return f("");}
 function clear(t,d){return start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):x==="L"?reject:app(t,"_",n))));}
 function copy(a,b,d){return start(a,start(b,loop(n=>rd(a,x=>x==="_"?d:x==="L"?reject:app(b,x,mv(a,1,n))))));}
 const reset=(t,d)=>start(t,word(t,"0".repeat(9),d)),set=(t,v,d)=>seek(t,v,wr(t,"1",d));
 const selectEntry=label(),prev=label(),candidate=label(),group=label(),selected=label(),translateEntry=label(),translateGroup=label();
 // Copy owner field during candidate scan; no speculative assignment
 // becomes committed until the whole row matches the separator.
 const advance=mv(G,1,mv(B,1,mv(S,1,group)));
 const endField=rd(P,x=>x===","?mv(P,1,advance):x===";"?advance:reject);
 const mismatch=loop(n=>rd(P,x=>x===";"?mv(P,1,candidate):bit(x)||x===","?mv(P,1,n):reject));
 const capture=start(temp,loop(n=>rd(P,x=>bit(x)?app(temp,x,mv(P,1,n)):endField)));
 function compare(t){
  return start(t,loop(n=>rd(P,x=>bit(x)?rd(t,y=>x===y?mv(P,1,mv(t,1,n)):mismatch):x===","||x===";"?test(t,y=>y==="_",endField,mismatch):reject)));
 }
 const cmp=chosen.map(compare),dispatch=rd(G,x=>symbols.includes(x)?cmp[symbols.indexOf(x)]:reject);
 bind(group,rd(B,x=>x==="_"?test(P,y=>y===";",selected,reject):x==="0"?advance:x==="1"?rd(S,y=>y==="1"?capture:y==="0"?dispatch:reject):reject));
 bind(candidate,test(P,x=>x==="_",reject,clear(temp,start(G,start(B,start(S,group))))));
 // H is at the right boundary of the current 20-bit record.
 // Move back to its first cell after committing the owner rank.
 bind(selected,start(W,readN(W,4,v=>v<9?copy(temp,chosen[v],walk(H,-1,20,prev)):reject)));
 const load=start(W,readN(W,4,v=>v<9?copy(Array.from({length:9},(_,i)=>22+i)[v],P,seek(T,9*v,start(B,copyN(T,B,9,reset(S,set(S,v,start(P,candidate))))))):reject));
 const loadRecord=clear(P,start(W,copyN(H,W,20,load)));
 bind(prev,mv(H,-1,test(H,x=>x==="L",translateEntry,walk(H,-1,19,loadRecord))));
 bind(selectEntry,start(decision,rd(decision,x=>x==="0"?halt:x==="1"?clear(B,clear(S,start(G,word(G,symbols,prev)))):reject)));
 // Redirect the actual end-of-forest branch, not other references.
 const edgeRead=ins[J.edge].next;if(ins[edgeRead].op!=="read"||ins[edgeRead].next[alphabet.indexOf("_")]!==halt)throw Error("edge exit");
 ins[edgeRead].next[alphabet.indexOf("_")]=selectEntry;
 // Original Boolean layout: enumerate i=0..M; output onehot X and
 // cumulative Y once equality is reached, omitting Y at i=0.
 function eq(a,b,yes,no){return start(a,start(b,loop(n=>rd(a,x=>rd(b,y=>x===y?(x==="_"?yes:bit(x)?mv(a,1,mv(b,1,n)):reject):no)))));}
 const inc=(t,d)=>start(t,loop(n=>rd(t,x=>x==="0"?wr(t,"1",d):x==="1"?app(t,"0",n):reject)));
 const bitLoop=label(),nextGroup=mv(G,1,translateGroup);
 const afterBits=eq(counter,M,nextGroup,inc(counter,bitLoop));
 const yEmit=start(first,rd(first,x=>x==="1"?wr(first,"0",afterBits):x==="0"?start(flag,rd(flag,y=>bit(y)?app(Y,y,afterBits):reject)):reject));
 bind(bitLoop,eq(counter,temp,app(X,"1",start(flag,wr(flag,"1",yEmit))),app(X,"0",yEmit)));
 const initCounter=clear(counter,start(M,start(counter,loop(n=>rd(M,x=>x==="_"?start(flag,wr(flag,"0",start(first,wr(first,"1",bitLoop)))):bit(x)?app(counter,"0",mv(M,1,n)):reject)))));
 function reverse(t){const back=loop(n=>rd(t,x=>x==="L"?initCounter:bit(x)?app(temp,x,mv(t,-1,n)):reject));return clear(temp,start(t,loop(n=>rd(t,x=>x==="_"?mv(t,-1,back):bit(x)?mv(t,1,n):reject))));}
 const reverseEntries=chosen.map(reverse);
 const done=start(X,halt);
 const pins=loop(n=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?app(X,y,mv(Q,1,n)):reject)):x==="1"?mv(Q,1,test(Q,y=>y==="0",app(X,"0",app(X,"0",done)),reject)):reject));
 const skipBound=start(Q,loop(n=>rd(Q,x=>x==="0"?mv(Q,1,test(Q,bit,mv(Q,1,n),reject)):x==="1"?mv(Q,1,test(Q,y=>y==="0",mv(Q,1,pins),reject)):reject)));
 const appendY=start(Y,loop(n=>rd(Y,x=>x==="_"?skipBound:bit(x)?app(X,x,mv(Y,1,n)):reject)));
 bind(translateGroup,rd(G,x=>x==="_"?appendY:symbols.includes(x)?reverseEntries[symbols.indexOf(x)]:reject));
 bind(translateEntry,start(X,start(Y,start(G,translateGroup))));
 return{...J,ins,tapes:61,selectEntry,selected,translateEntry,witnessTape:X,chosen};
}
module.exports={machine};
