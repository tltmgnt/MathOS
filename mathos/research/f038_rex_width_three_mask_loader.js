// REX-024D2B: finite IR left checkpoint reader; bound, pins and ordered mask stream.
function machine(){
 const alphabet=["L","0","1",":",";","|","_",",","H","b"],ins=[];
 const add=(op,t,next)=>{let n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].op!=="jump"||ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d});
 const I=0,M=1,P=2,F=3,bit=x=>x==="0"||x==="1",test=(t,p,y,n)=>rd(t,x=>p(x)?y:n),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>test(t,x=>x==="L",mv(t,1,d),mv(t,-1,n)));
 const app=(t,v,d)=>wr(t,v,mv(t,1,d));
 function skip(n,d){while(n--)d=test(I,bit,mv(I,-1,d),reject);return d;}
 // Each fixed block is read from its right edge towards the left.
 // Only masks and pins are emitted; every mask has a delimiter.
 function block(out,d){
  return mv(I,-1,loop(n=>rd(I,x=>x==="b"?(out===F?app(F,";",d):d):bit(x)?(out===null?mv(I,-1,n):app(out,x,mv(I,-1,n))):reject)));
 }
 let blocks=halt;for(let j=165;j>=0;j--)blocks=block(j>=37?F:j===36?P:null,blocks);
 const selector=mv(I,-1,loop(n=>rd(I,x=>x==="b"?blocks:bit(x)?mv(I,-1,n):reject)));
 const trim=mv(M,-1,loop(n=>rd(M,x=>x==="0"?wr(M,"_",mv(M,-1,n)):x==="1"?selector:reject)));
 const columns=loop(n=>rd(I,x=>x==="b"?trim:bit(x)?skip(4,rd(I,y=>bit(y)?app(M,y,mv(I,-1,n)):reject)):reject));
 const locate=loop(n=>rd(I,x=>x==="H"?mv(I,-1,skip(15,columns)):x==="_"?reject:mv(I,1,n)));
 const entry=start(M,start(P,start(F,start(I,locate))));
 return{alphabet,tapes:4,ins,entry};
}
module.exports={machine};
