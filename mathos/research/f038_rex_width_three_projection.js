// REX-024D1B: on-tape coordinate masks, tuple projection, keyed merge, retained tuple decoding.
function machine(){
 const alphabet=["L","0","1",":",";","|","_",","],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),bit=x=>x==="0"||x==="1",data=x=>bit(x)||x===":"||x===";";
 const seq=(...fs)=>d=>fs.reduceRight((n,f)=>f(n),d),move=(t,d)=>n=>mv(t,d,n),put=(t,v)=>n=>wr(t,v,n),app=(t,v)=>seq(put(t,v),move(t,1));
 const loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const clear=(t,d)=>start(t,loop(n=>test(t,x=>x==="_",start(t,d),seq(put(t,"_"),move(t,1))(n))));
 const copyAll=(a,b,d)=>loop(n=>rd(a,x=>x==="_"?d:x==="L"?reject:seq(app(b,x),move(a,1))(n)));
 const copyRecord=(a,b,d)=>loop(n=>rd(a,x=>data(x)?seq(app(b,x),move(a,1))(x===";"?d:n):reject));
 const skip=(t,d)=>loop(n=>rd(t,x=>data(x)?mv(t,1,x===";"?d:n):reject));
 const back=(t,d)=>mv(t,-1,loop(n=>test(t,x=>["L",";","|"].includes(x),mv(t,1,d),mv(t,-1,n))));
 const at=(t,y,n)=>test(t,x=>x!=="_"&&x!=="|",y,n);
 function compare(a,b,lt,eq,gt){
  const ret=[lt,eq,gt].map(d=>back(a,back(b,d)));
  return loop(n=>rd(a,x=>rd(b,y=>{
   if(!bit(x)&&x!==":"||!bit(y)&&y!==":")return reject;
   if(x===y)return x===":"?ret[1]:seq(move(a,1),move(b,1))(n);
   return ret[x===":"||y!==":"&&x==="0"?0:2];
  })));
 }
 const P=0,C=1,A=2,B=3,S=4,K=5,O=6,PM=7,CM=8,U=9;
 // Decode the surviving encoded payload to the original tuple stream.
 function retain(dest){
  const rows=label(),fields=label();
  const endField=rd(O,x=>x===";"?seq(app(U,";"),move(O,1))(rows):bit(x)?app(U,",")(fields):reject);
  const token=rd(O,x=>x==="0"?mv(O,1,rd(O,y=>bit(y)?seq(app(U,y),move(O,1))(fields):reject)):x==="1"?mv(O,1,rd(O,y=>y==="0"?mv(O,1,endField):reject)):reject);
  bind(fields,token);
  bind(rows,loop(n=>rd(O,x=>x==="_"?dest:bit(x)?mv(O,1,n):x===":"?mv(O,1,fields):reject)));
  return start(O,start(U,rows));
 }
 const finished=retain(halt);
 function sort(W,dest){
  // pass states preserve only finite flags for alternation and run count.
  const pass=label();
  const merge=[label(),label(),label()]; // 0,1,>=2 output runs
  for(let k=0;k<3;k++){
   let next=seq(app(W,"|"))(merge[Math.min(k+1,2)]);
   const finishB=loop(n=>rd(B,x=>x==="|"?mv(B,1,next):x==="_"?next:copyRecord(B,W,n)));
   const drainA=loop(n=>rd(A,x=>x==="|"?mv(A,1,finishB):x==="_"?finishB:copyRecord(A,W,n)));
   const pair=loop(n=>at(A,at(B,compare(A,B,copyRecord(A,W,n),copyRecord(A,W,n),copyRecord(B,W,n)),drainA),drainA));
   bind(merge[k],test(A,x=>x==="_",test(B,x=>x==="_",k===2?pass:dest,pair),pair));
  }
  const split=[label(),label()];
  for(let k=0;k<2;k++){
   const t=k===0?A:B;
   bind(split[k],test(W,x=>x==="_",clear(W,start(A,start(B,merge[0]))),loop(n=>test(W,x=>x==="|",seq(app(t,"|"),move(W,1))(split[1-k]),copyRecord(W,t,n)))));
  }
  bind(pass,clear(A,clear(B,start(W,split[0]))));
  const single=[label(),label(),label()];
  for(let k=0;k<3;k++){
   let next=seq(app(A,";"),app(A,"|"),move(W,1))(single[Math.min(k+1,2)]);
   const payload=loop(n=>rd(W,x=>bit(x)?seq(app(A,x),move(W,1))(n):x===";"?next:reject));
   const key=loop(n=>rd(W,x=>bit(x)?seq(app(A,x),move(W,1))(n):x===":"?seq(app(A,":"),move(W,1))(payload):reject));
   bind(single[k],test(W,x=>x==="_",clear(W,start(A,copyAll(A,W,k===2?pass:dest))),key));
  }
  return start(W,clear(A,single[0]));
 }
 const join=loop(n=>at(P,at(S,compare(P,S,skip(P,n),copyRecord(P,O,n),skip(S,n)),finished),finished));
 const joinStart=start(P,start(S,start(O,join)));
 const emitKey=(src,dst,d)=>loop(n=>rd(src,x=>bit(x)?seq(app(dst,x),move(src,1))(n):x===":"?seq(app(dst,":"),app(dst,";"))(d):reject));
 const dedup=[label(),label()];
 for(let k=0;k<2;k++){
  let advance=skip(C,dedup[1]),fresh=clear(K,emitKey(C,K,back(C,emitKey(C,S,back(C,start(K,advance))))));
  bind(dedup[k],at(C,k===0?fresh:compare(C,K,fresh,advance,fresh),joinStart));
 }
 // Read bounded coordinate masks from tapes, not compiler arguments.
 // 1..4 fields, at most 3 selected coordinates; counts must agree.
 function validate(t,choose){
  const memo=new Map();
  function node(n,k){
   const id=n*4+k;if(memo.has(id))return memo.get(id);
   const q=rd(t,x=>x==="_"?(n?choose(k):reject):bit(x)&&n<4&&k+Number(x)<=3?mv(t,1,node(n+1,k+Number(x))):reject);
   memo.set(id,q);return q;
  }
  return start(t,node(0,0));
 }
 function project(W,M,dest){
  const row=label(),field=label();
  const payload=loop(n=>rd(W,x=>bit(x)?seq(app(A,"0"),app(A,x),move(W,1))(n):x===","?seq(app(A,"1"),app(A,"0"),move(W,1))(n):x===";"?seq(app(A,"1"),app(A,"0"),app(A,";"),move(W,1))(row):reject));
  const rowEnd=seq(app(A,":"))(back(W,payload));
  function fieldBody(selected){
   const end=seq(...(selected?[app(A,"1"),app(A,"0")]:[]),move(M,1))(rd(M,x=>x==="_"?test(W,y=>y===";",rowEnd,reject):bit(x)?test(W,y=>y===",",mv(W,1,field),reject):reject));
   const digits=loop(n=>rd(W,x=>bit(x)?seq(...(selected?[app(A,"0"),app(A,x)]:[]),move(W,1))(n):x===","||x===";"?end:reject));
   return test(W,bit,digits,reject);
  }
  const no=fieldBody(false),yes=fieldBody(true);
  bind(field,rd(M,x=>x==="0"?no:x==="1"?yes:reject));
  bind(row,test(W,x=>x==="_",clear(W,start(A,copyAll(A,W,dest))),start(M,field)));
  return start(W,clear(A,row));
 }
 const mergeEntry=sort(P,sort(C,start(C,start(S,dedup[0]))));
 const projected=project(P,PM,project(C,CM,mergeEntry));
 const validChild=Array.from({length:4},(_,k)=>validate(CM,c=>c===k?projected:reject));
 const entry=validate(PM,k=>validChild[k]);
 return{alphabet,tapes:10,ins,entry};
}

function compact(J){
 const {ins,alphabet}=J;
 function resolve(i){let n=0;while(ins[i]?.op==="jump"){i=ins[i].next;if(++n>ins.length)throw Error("jump cycle");}if(!ins[i])throw Error("bad target");return i;}
 const entry=resolve(J.entry),ids=new Map([[entry,0]]),states=[entry],rows=[];
 function id(i){i=resolve(i);if(!ids.has(i)){ids.set(i,states.length);states.push(i);}return ids.get(i);}
 for(let i=0;i<states.length;i++){
  let a=ins[states[i]],b={op:a.op,t:a.t,next:0};
  if(a.op==="read")b.next=a.next.map(id);
  else if(a.op==="write"||a.op==="move")b.next={...a.next,d:id(a.next.d)};
  else if(a.op!=="halt"&&a.op!=="reject")throw Error("opcode");
  rows.push(b);
 }
 let cls=rows.map(()=>0),rounds=0,n=1;
 while(true){
  let keys=new Map(),next=rows.map(a=>{let sig=JSON.stringify([a.op,a.t,a.op==="read"?a.next.map(d=>cls[d]):a.op==="move"?[a.next.dir,cls[a.next.d]]:a.op==="write"?[a.next.v,cls[a.next.d]]:null]);if(!keys.has(sig))keys.set(sig,keys.size);return keys.get(sig);});rounds++;cls=next;if(keys.size===n)break;n=keys.size;
 }
 let out=Array(n);
 for(let i=0;i<rows.length;i++){let a=rows[i],b={...a,next:a.op==="read"?a.next.map(d=>cls[d]):a.op==="write"||a.op==="move"?{...a.next,d:cls[a.next.d]}:0},k=cls[i];if(out[k]&&JSON.stringify(out[k])!==JSON.stringify(b))throw Error("IR homomorphism");out[k]=b;}
 return{...J,ins:out,entry:cls[0],stats:{raw:ins.length,reachable:rows.length,compact:n,rounds,checked:rows.length}};
}
module.exports={machine,compact};
