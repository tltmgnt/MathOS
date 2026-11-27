// REX-024D3A2: finite-IR router and cursor on one transition program. Literal D2C stream/header suffix and unary ordinal input.
function machine(cursor){
 const J=cursor.machine(),alphabet=[...J.alphabet,"H","b"],ins=J.ins.map(a=>a.op==="read"?{...a,next:[...a.next,1,1]}:{...a});
 const reject=1,add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const M=0,A=1,C=2,F=[3,4,5,6,7,8,9],W=10,B=11,S=12,N=13,Z=14,I=19,Q=20,K=21;
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 function walk(t,dir,k,d){while(k--)d=mv(t,dir,d);return d;}
 const seek=(t,k,d)=>start(t,walk(t,1,k,d)),app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 function copy(a,b,n,d){while(n--){let next=d;d=rd(a,x=>bit(x)?app(b,x,mv(a,1,next)):reject);}return d;}
 function expect(t,x,d){return test(t,y=>y===x,mv(t,1,d),reject);}
 function clear(t,d){return start(t,loop(n=>rd(t,x=>x==="_"?d:x==="L"?reject:app(t,"_",n))));}
 function readN(t,n,choose){function f(p){return p.length===n?choose(parseInt(p,2)):rd(t,x=>bit(x)?mv(t,1,f(p+x)):reject);}return f("");}
 const reset=(t,d)=>start(t,word(t,"0".repeat(9),d)),set=(t,v,d)=>seek(t,v,wr(t,"1",d));
 // D2C token grammar: 00/01 data; 10 terminator. Start at token boundary.
 function field(out,d){return loop(n=>rd(Q,x=>x==="0"?mv(Q,1,rd(Q,y=>bit(y)?(out===null?mv(Q,1,n):app(out,y,mv(Q,1,n))):reject)):x==="1"?mv(Q,1,expect(Q,"0",d)):reject));}
 const slots="01:;|,x",advance=label(),slotLoop=label();
 bind(advance,mv(Z,1,slotLoop));
 const copyEntries=F.map(t=>start(t,field(t,advance)));
 const deliver=rd(Z,x=>slots.includes(x)?copyEntries[slots.indexOf(x)]:reject);
 // Counter N has 8 little-endian bits; skip one field per decrement.
 const count=label(),dec=start(N,loop(n=>rd(N,x=>x==="1"?wr(N,"0",count):x==="0"?app(N,"1",n):reject)));
 bind(count,start(N,loop(n=>rd(N,x=>x==="_"?deliver:x==="0"?mv(N,1,n):x==="1"?field(null,dec):reject))));
 const locate=start(Q,field(null,field(null,count)));
 const scopes=[];for(let k=1;k<=3;k++){function sub(a,at){if(a.length===k){scopes.push(a);return;}for(let i=at;i<9;i++)sub([...a,i],i+1);}sub([],0);}
 const ids=new Map(scopes.map((h,i)=>[Array.from({length:9},(_,j)=>+h.includes(j)).join(""),i]));
 function scopeId(p){if(p.length===9)return ids.has(p)?word(N,ids.get(p).toString(2).padStart(8,"0").split("").reverse().join(""),locate):reject;
  if(![...ids.keys()].some(s=>s.startsWith(p)))return reject;
  return rd(S,x=>bit(x)?mv(S,1,scopeId(p+x)):reject);
 }
 const decode=start(N,start(S,scopeId("")));
 const coords=Array.from({length:5},()=>label());
 for(let j=0;j<=4;j++){
  const pad=word(C,"0".repeat(4-j),decode);
  const yes=j<4?rd(S,y=>bit(y)?app(C,y,mv(B,1,mv(S,1,coords[j+1]))):reject):reject;
  bind(coords[j],rd(B,x=>x==="_"?pad:x==="0"?mv(B,1,mv(S,1,coords[j])):x==="1"?yes:reject));
 }
 const project=start(B,start(S,coords[0]));
 const slotFields=[[],[1],[2],[3],[1,2],[1,3],[2,3]];
 const slotEntries=slotFields.map((fields,i)=>{
  let d=project;
  for(let j of [0,...fields].reverse()){let next=d;d=seek(W,4*j,readN(W,4,v=>v<9?set(S,v,next):reject));}
  return seek(W,20+i,rd(W,x=>x==="0"?word(C,"0000",advance):x==="1"?reset(S,d):reject));
 });
 let cleanup=J.entry;for(let t of [W,B,S,N,Z].reverse())cleanup=clear(t,cleanup);
 bind(slotLoop,rd(Z,x=>x==="_"?cleanup:slots.includes(x)?slotEntries[slots.indexOf(x)]:reject));
 const route=start(Z,slotLoop);
 const arity=start(B,loop(n=>rd(B,x=>x==="_"?route:x==="0"?mv(B,1,n):x==="1"?app(A,"1",mv(B,1,n)):reject)));
 let bag=arity;for(let j=3;j>=0;j--){let d=bag;bag=seek(W,4*j,readN(W,4,v=>v<9?set(B,v,d):v===9&&j!==0?d:reject));}
 const parse=walk(I,1,54,start(W,copy(I,W,4,walk(I,1,2,copy(I,W,23,reset(B,bag))))));
 function select(n){return rd(K,x=>x==="_"?parse:x==="1"&&n<8?mv(K,1,walk(I,1,85,select(n+1))):reject);}
 const selectStart=start(I,expect(I,"H",start(K,select(0))));
 const accepted=start(I,expect(I,"H",walk(I,1,59,test(I,x=>x==="1",selectStart,reject))));
 const entry=start(Z,word(Z,slots,start(C,start(A,start(M,start(Q,field(M,accepted)))))));
 return{alphabet,tapes:22,ins,entry,tupleEntry:J.tupleEntry,cursorEntry:J.entry,cleanupEntry:cleanup};
}
module.exports={machine};
