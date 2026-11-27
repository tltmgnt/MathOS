// D5V standalone direct support projection over persistent gamma-gap fields.
// Input rank domains A/B/C and mode+payload Q; blank terminates payload.
// One-symbol C domain handles binary scopes. No decoded mask tape.
function machine(){
 const alphabet=["L","0","_","1","x"],ins=[],X=0,R=[1,2,3],V=[4,5,6],G=7,Q=8;
 const add=(op,t,next)=>{let i=ins.length;ins.push({op,t,next});return i;},label=()=>add("jump",0,-1),bind=(n,d)=>{ins[n].next=d;},halt=add("halt",0,0),reject=add("reject",0,0);
 const rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n))),app=(t,v,d)=>wr(t,v,mv(t,1,d));
 const empty=(y,n)=>start(G,test(G,x=>x==="_",y,n));
 function parse(d){
  const tail=loop(n=>rd(G,x=>x==="L"?d:bit(x)?rd(Q,y=>bit(y)?wr(G,y,mv(Q,1,mv(G,-1,n))):reject):reject));
  return start(G,loop(n=>rd(Q,x=>x==="0"?app(G,"0",mv(Q,1,n)):x==="1"?wr(G,"1",mv(Q,1,mv(G,-1,tail))):reject)));
 }
 function sparse(zero,one){
  const dec=start(G,loop(n=>rd(G,x=>x==="0"?app(G,"1",n):x==="1"?wr(G,"0",mv(G,1,rd(G,y=>y==="_"?mv(G,-1,wr(G,"_",empty(one,zero))):bit(y)?zero:reject))):reject)));
  return empty(rd(Q,x=>x==="_"?zero:bit(x)?parse(dec):reject),dec);
 }
 let output=start(X,halt);
 for(const t of V.slice().reverse()){
  const next=output;
  output=start(t,loop(n=>rd(t,x=>x==="_"?app(X,"1",next):bit(x)?app(X,x,mv(t,1,n)):reject)));
 }
 const end=empty(test(Q,x=>x==="_",start(X,output),reject),reject);
 function sweep(isSparse){
  const row=label();
  function adv(i,carry){return mv(R[i],1,mv(V[i],1,rd(R[i],x=>x==="_"?start(R[i],start(V[i],carry)):bit(x)?row:reject)));}
  const next=adv(2,adv(1,adv(0,end))),support=wr(V[0],"1",wr(V[1],"1",wr(V[2],"1",next)));
  const read=(yes,no)=>isSparse?sparse(yes,no):rd(Q,x=>x==="0"?mv(Q,1,yes):x==="1"?mv(Q,1,no):reject);
  bind(row,rd(R[0],x=>x==="0"?read(next,next):x==="1"?rd(R[1],y=>y==="0"?read(next,next):y==="1"?rd(R[2],z=>z==="0"?read(next,next):z==="1"?read(support,next):reject):reject):reject));
  return row;
 }
 const mode=rd(Q,x=>x==="0"?mv(Q,1,sweep(false)):x==="1"?mv(Q,1,sweep(true)):reject);
 let entry=start(Q,mode);
 for(let i=2;i>=0;i--){
  const t=R[i],v=V[i],next=entry;
  const scan=loop(n=>rd(t,x=>x==="_"?start(t,start(v,next)):bit(x)?app(v,"0",mv(t,1,n)):reject));
  entry=start(t,test(t,bit,start(v,scan),reject));
 }
 return {alphabet,ins,tapes:9,entry};
}
module.exports={machine};
