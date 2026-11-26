// REX-024D2A: finite header-suffix parser, owner-indexed routing and canonical scope IDs.
function machine(){
 const alphabet=["L","0","1",":",";","|","_",",","H","b"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const I=0,H=1,B=2,S=3,T=4,W=5,R=6,F=7,Z=8;
 function walk(t,dir,n,d){while(n--)d=mv(t,dir,d);return d;}
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const seek=(t,k,d)=>start(t,walk(t,1,k,d));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function word(t,s,d){for(let i=s.length-1;i>=0;i--)d=app(t,s[i],d);return d;}
 function skip(t,n,d){while(n--)d=test(t,bit,mv(t,1,d),reject);return d;}
 function expect(t,x,d){return test(t,y=>y===x,mv(t,1,d),reject);}
 function copy(a,b,n,d){while(n--) {let next=d;d=rd(a,x=>bit(x)?app(b,x,mv(a,1,next)):reject);}return d;}
 function readN(t,n,choose){function f(p){if(p.length===n)return choose(parseInt(p,2));return rd(t,x=>bit(x)?mv(t,1,f(p+x)):reject);}return f("");}
 const bin=(v,n=4)=>v.toString(2).padStart(n,"0");
 function set(t,v,d){return seek(t,v,wr(t,"1",d));}
 function reset(t,d){return start(t,word(t,"0".repeat(9),d));}
 const scopes=[];for(let k=1;k<=3;k++){function sub(a,at){if(a.length===k){scopes.push(a);return;}for(let i=at;i<9;i++)sub([...a,i],i+1);}sub([],0);}
 const ids=new Map(scopes.map((h,i)=>[Array.from({length:9},(_,j)=>+h.includes(j)).join(""),i]));
 // Read bounded bitmaps and map a canonical scope to its physical C1 mask index.
 function scopeId(dest){
  function f(p){if(p.length===9)return ids.has(p)?word(F,bin(ids.get(p),8),dest):reject;
   if(![...ids.keys()].some(s=>s.startsWith(p)))return reject;
   return rd(B,x=>bit(x)?mv(B,1,f(p+x)):reject);
  }return start(B,f(""));
 }
 // A fixed slot-dispatch tape shares one canonical scope decoder.
 const slotFields=[[],[1],[2],[3],[1,2],[1,3],[2,3]];
 function owned(slot,dest,decode){
  let d=decode;
  for(let j of [0,...slotFields[slot]].reverse()){
   let next=d;d=seek(W,4*j,readN(W,4,v=>v<9?set(B,v,next):reject));
  }
  return seek(W,20+slot,rd(W,x=>x==="0"?word(F,"11111111",dest):x==="1"?reset(B,d):reject));
 }
 function coord(dest){
  const n=label(),yes=rd(S,x=>bit(x)?app(R,x,mv(S,1,mv(B,1,n))):reject);
  bind(n,rd(B,x=>x==="_"?dest:x==="0"?mv(S,1,mv(B,1,n)):x==="1"?yes:reject));
  return start(B,start(S,n));
 }
 // Second pass: copy each fixed 45-bit header into W. Derive separator
 // masks and emit seven canonical mask IDs, with 255 for absent slots.
 const route=label();
 const slotSymbols="01:;|,H",slotLoop=label(),advance=mv(Z,1,slotLoop),decode=scopeId(advance);
 const slotEntries=Array.from({length:7},(_,i)=>owned(i,advance,decode));
 bind(slotLoop,rd(Z,x=>x==="_"?route:slotSymbols.includes(x)?slotEntries[slotSymbols.indexOf(x)]:reject));
 const scopesDone=start(Z,slotLoop);
 const parentDone=app(R,";",scopesDone);
 const parentCoord=coord(parentDone);
 const parentMask=seek(W,16,readN(W,4,v=>v===9?parentDone:v<9?seek(T,9*v,start(B,copy(T,B,9,parentCoord))):reject));
 const childCoord=coord(app(R,":",parentMask));
 const routeBody=seek(W,27,start(B,copy(W,B,9,start(S,copy(W,S,9,childCoord)))));
 const emitParent=seek(W,16,copy(W,R,4,routeBody));
 const emitOwner=start(W,copy(W,R,4,emitParent));
 bind(route,test(H,x=>x==="_",halt,start(W,copy(H,W,45,emitOwner))));
 const routeStart=start(H,start(R,start(F,route)));
 // Parse one frame into H: owner, three neighbors, parent, seven slots,
 // bag bitmap and separator bitmap. T is indexed by owner ID (9 bits each).
 const nextFrame=label();
 const tableStore=start(W,readN(W,4,v=>v<9?seek(T,9*v,start(B,copy(B,T,9,nextFrame))):reject));
 const finish=expect(I,"b",start(B,copy(B,H,9,start(S,copy(S,H,9,tableStore)))));
 const slots=copy(I,H,7,expect(I,"0",finish));
 const parent=readN(I,4,v=>v<=9?word(H,bin(v),slots):reject);
 let neighbors=parent;
 for(let j=2;j>=0;j--){let d=neighbors;neighbors=readN(I,4,v=>v===9?word(H,bin(v),d):v<9?word(H,bin(v),set(B,v,set(S,v,d))):reject);}
 function owner(v,first){
  if(v===9)return first?reject:expect(I,"0",expect(I,"0",expectZeros(24,expect(I,"b",routeStart))));
  if(v>8)return reject;
  return expect(I,first?"1":"0",expect(I,first?"1":"0",word(H,bin(v),start(W,word(W,bin(v),reset(B,reset(S,set(B,v,neighbors))))))));
 }
 function expectZeros(n,d){while(n--)d=expect(I,"0",d);return d;}
 bind(nextFrame,skip(I,54,readN(I,4,v=>owner(v,false))));
 const entry=start(Z,word(Z,slotSymbols,start(I,expect(I,"H",start(H,start(T,word(T,"0".repeat(81),skip(I,54,readN(I,4,v=>owner(v,true))))))))));
 return{alphabet,tapes:9,ins,entry};
}
module.exports={machine};
