// REX-024D3A1: fixed finite-IR one-bag lexicographic mask-cursor generator.
function machine(){
 // Input: M LSB-first, arity word 1^r, seven 4-bit projection masks,
 // seven forbidden-bit streams (empty for absent). All are preencoded.
 // Fixed tape IDs: M=0,A=1,C=2,F0..6=3..9,R0..3=10..13,
 // unary domain D0..2=14..16, output O=17, first flag Z=18.
 const alphabet=["L","0","1",":",";","|","_",",","x"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const M=0,A=1,C=2,F=[3,4,5,6,7,8,9],R=[10,11,12,13],D=[14,15,16],O=17,Z=18;
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const seek=(t,k,d)=>{while(k--)d=mv(t,1,d);return start(t,d);};
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 const zero=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?d:bit(x)?app(t,"0",n):reject)));
 const inc=(t,d)=>start(t,loop(n=>rd(t,x=>x==="0"?wr(t,"1",d):x==="1"?app(t,"0",n):reject)));
 function eq(t,yes,no){
  return start(t,start(M,loop(n=>rd(t,x=>rd(M,y=>x===y?(x==="_"?yes:bit(x)?mv(t,1,mv(M,1,n)):reject):no)))));
 }
 function emitRank(t,d){
  const copy=loop(n=>rd(t,x=>x==="L"?d:bit(x)?app(O,x,mv(t,-1,n)):reject));
  return start(t,loop(n=>rd(t,x=>x==="_"?mv(t,-1,copy):bit(x)?mv(t,1,n):reject)));
 }
 // read arity 1^r followed by blank, with r in finite control.
 function arity(dest){
  function go(n){return rd(A,x=>x==="_"&&n?dest[n-1]:x==="1"&&n<4?mv(A,1,go(n+1)):reject);}
  return start(A,go(0));
 }
 // Rewind a mask m^k-1 positions by nested scans of unary domain tapes.
 // First combination consumes flag 1 without moving the mask.
 function rewind(t,k,d){
  const body=n=>start(Z,rd(Z,x=>x==="1"?wr(Z,"0",n):x==="0"?mv(t,-1,n):reject));
  function nest(j,next){if(j===k)return body(next);return start(D[j],loop(n=>rd(D[j],x=>x==="_"?next:x==="x"?nest(j+1,mv(D[j],1,n)):reject)));}
  return start(Z,wr(Z,"1",nest(0,d)));
 }
 // After the rightmost nonmaximal coordinate c advances, its suffix
 // resets. Inspect each slot's 4-bit projection in C. Absent is 0000.
 const tuple=label();
 const carry=Array.from({length:4},()=>label());
 for(let c=0;c<4;c++){
  let next=tuple;
  for(let i=6;i>=0;i--){
   const dest=next,adv=mv(F[i],1,dest),rew=[dest,...[1,2,3].map(k=>rewind(F[i],k,dest))];
   function parse(j,has,k){
    if(j===4)return has?adv:rew[k];
    return rd(C,x=>bit(x)?mv(C,1,parse(j+1,has||(j===c&&x==="1"),k+ +(j>c&&x==="1"))):reject);
   }
   next=seek(C,4*i,parse(0,false,0));
  }
  bind(carry[c],inc(R[c],next));
 }
 // Once every rank is maximal, masks must end simultaneously.
 const finish=Array.from({length:7},()=>label());
 for(let i=0;i<7;i++){
  const d=i===6?halt:finish[i+1];
  bind(finish[i],rd(F[i],x=>x==="_"?d:bit(x)?mv(F[i],1,test(F[i],y=>y==="_",d,reject)):reject));
 }
 const advance=Array.from({length:4},()=>label());
 for(let c=0;c<4;c++)bind(advance[c],eq(R[c],zero(R[c],c===0?finish[0]:advance[c-1]),carry[c]));
 const next=arity(advance);
 const rowEnds=[];
 for(let r=1;r<=4;r++){
  let n=next;for(let j=r-1;j>=0;j--)n=emitRank(R[j],app(O,j===r-1?";":",",n));
  rowEnds.push(n);
 }
 const emit=arity(rowEnds);
 // Read all seven heads. Absent streams are empty; actual streams
 // are checked by the caller's legitimate mask-shape precondition.
 let check=emit;
 for(let i=6;i>=0;i--)check=rd(F[i],x=>x==="1"?next:x==="0"||x==="_"?check:reject);
 bind(tuple,check);
 // Generate unary domain on three tapes by a binary counter.
 const unary=label();
 let more=inc(R[0],unary),done=zero(R[0],start(O,tuple));
 let appendDomains=eq(R[0],done,more);for(let t of D.slice().reverse())appendDomains=app(t,"x",appendDomains);
 bind(unary,appendDomains);
 let init=unary;for(let t of [...F,...D].reverse())init=start(t,init);
 // Initialize four zero counters of the same width as M.
 for(let t of R.slice().reverse()){
  const d=init;init=start(t,start(M,loop(n=>rd(M,x=>x==="_"?d:bit(x)?app(t,"0",mv(M,1,n)):reject))));
 }
 const entry=init;
 return{alphabet,tapes:19,ins,entry};
}
module.exports={machine};
