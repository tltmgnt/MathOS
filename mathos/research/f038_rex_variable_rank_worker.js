// D6Z: fixed two-tape binary-rank canonical-stream worker.
// Input tape1: 1^k 0, then x (1^(g+1) 0 rank){1..3} per forbidden
// tuple, then blank. Tape0 initially empty. Host raw conversion separate.
function machine(){
 const alphabet=["L","0","_","1","x"],ins=[];
 const add=(op,t,next)=>{const n=ins.length;ins.push({op,t,next});return n;},label=()=>add("jump",0,-1),bind=(n,d)=>{if(ins[n].next!==-1)throw Error("label");ins[n].next=d;};
 const halt=add("halt",0,0),reject=add("reject",0,0),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),loop=f=>{const n=label();bind(n,f(n));return n;};
 const A=0,Q=1,bit=x=>x==="0"||x==="1";
 const rewind=(t,d)=>loop(n=>rd(t,x=>x==="L"?mv(t,1,d):mv(t,-1,n)));
 const attempt=label(),clause=label(),fail=label(),header=label();
 const carry=label();bind(carry,rd(A,x=>x==="1"?wr(A,"0",mv(A,-1,carry)):x==="0"?wr(A,"1",attempt):reject));
 bind(fail,loop(n=>rd(A,x=>x==="_"?mv(A,-1,carry):x==="L"||bit(x)?mv(A,1,n):reject)));
 const finish=rewind(A,halt);
 const lit=new Map();
 for(let c=1;c<=3;c++)for(const b of [false,true])lit.set(c+":"+b,label());
 for(let c=1;c<=3;c++)for(const b of [false,true]){
  const tail=all=>rd(Q,x=>x==="x"||x==="_"?(all?fail:clause):x==="1"&&c<3?lit.get((c+1)+":"+all):reject);
  const yes=tail(b),no=tail(false);
  const rank=rd(Q,r=>bit(r)?rd(A,a=>bit(a)?mv(Q,1,a===r?yes:no):reject):reject);
  const idx=label();bind(idx,rd(Q,x=>x==="1"?rd(A,a=>bit(a)?mv(A,1,mv(Q,1,idx)):reject):x==="0"?rd(A,a=>bit(a)?mv(Q,1,rank):reject):reject));
  bind(lit.get(c+":"+b),rewind(A,rd(Q,x=>x==="1"?mv(Q,1,idx):reject)));
 }
 bind(clause,rd(Q,x=>x==="_"?finish:x==="x"?mv(Q,1,lit.get("1:true")):reject));
 bind(header,rd(Q,x=>x==="1"?mv(Q,1,header):x==="0"?mv(Q,1,clause):reject));
 bind(attempt,rewind(Q,header));
 const init=label();bind(init,rd(Q,x=>x==="1"?wr(A,"0",mv(A,1,mv(Q,1,init))):x==="0"?mv(Q,1,clause):reject));
 const entry=mv(A,1,mv(Q,1,rd(Q,x=>x==="1"?init:reject)));
 return {alphabet,tapes:2,entry,ins,witnessTape:A,streamTape:Q};
}
function stream(U,d){
 if(d.m!==2)throw Error("binary domains only");
 let s="1".repeat(d.k)+"0";
 for(const f of d.F)for(const z of U.tuples(2,f.h.length))if(!f.S.has(z.join())){
  s+="x";for(let j=0;j<f.h.length;j++)s+="1".repeat(f.h[j]+1)+"0"+z[j];
 }return s;
}
function encode(M,s){return ["G","hL","u_","D","hL",...[...s].map(x=>"u"+x),"u_","E"].map(x=>M.codes[x]).join("");}
function run(M,s,limit=100000000){
 const input=encode(M,s),o=16,a=new Uint8Array(input.length+4*s.length+128);a.fill(2);for(let i=0;i<input.length;i++)a[o+i]=+input[i];
 let q=0,h=o,t=0,hi=h;while(q<M.q&&t<limit){const v=M.T[3*q+a[h]];a[h]=v>>>2&3;h+=(v&3)-1;q=v>>>4;t++;if(h>hi)hi=h;if(h<0||h>=a.length)throw Error("buffer");}
 const status=q<M.q?"TIMEOUT":q===M.q+1?"SAT":"UNSAT",rev=new Map(Object.entries(M.codes).map(([x,y])=>[y,x]));let z=null,encoded="";
 for(let i=o;i<a.length;i+=M.w){const w=Array.from(a.subarray(i,i+M.w)).join("");encoded+=w;if(rev.get(w)==="E")break;}
 if(status==="SAT"){z=[];for(let i=M.w;i<encoded.length;i+=M.w){const x=rev.get(encoded.slice(i,i+M.w));if(x==="D")break;if(x==="u0"||x==="h0"||x==="u1"||x==="h1")z.push(+x.slice(1));}}
 return {status,z,t,head:h-o,span:hi-o+1,encoded};
}
module.exports={machine,stream,encode,run};
