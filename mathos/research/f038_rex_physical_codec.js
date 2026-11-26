// RE-X-001: fixed physical binary payload codec; NOT a SAT solver or full product-track compiler.
function compile(u,v){
 if(!((u===1&&v===4)||(u===4&&v===1)))throw Error("fixed codec modes only");
 const names=[],ids=new Map(),T=[];
 function id(s){if(s==="HALT")return -1;if(!ids.has(s)){ids.set(s,names.length);names.push(s);}return ids.get(s);}
 id("begin");
 function delta(s,a){
  const [p,b,j]=s.split(":");const bit=a<2,stay=(next,w=a)=>[next,w,0],left=(next,w=a)=>[next,w,-1],right=(next,w=a)=>[next,w,1];
  const fail=()=>stay("HALT",2);
  if(p==="begin"||p==="seek"||p==="next"){
   if(bit)return right("seek");
   if(p==="begin")return stay("HALT");
   if(p==="next")return left("finishGap");
   return left("read");
  }
  if(p==="read")return bit?left(u===1?"cross:"+a:"readMore:"+a+":"+(u-1),2):fail();
  if(p==="readMore")return a===+b?left(+j===1?"cross:"+b:"readMore:"+b+":"+(+j-1),2):fail();
  if(p==="cross")return bit?left(s):left("output:"+b);
  if(p==="output"){
   if(bit)return left(s);
   return left(v===1?"turn":"write:"+b+":"+(v-1),+b);
  }
  if(p==="write")return a===2?left(+j===1?"turn":"write:"+b+":"+(+j-1),+b):fail();
  if(p==="turn")return a===2?right("return"):fail();
  if(p==="return")return bit?right(s):right("next");
  if(p==="finishGap")return a===2?left("finish"):fail();
  if(p==="finish")return bit?left(s):right("HALT");
  return fail();
 }
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [s,w,d]=delta(names[i],a);T.push([id(s),w,d]);}
 let q=names.length;for(let r of T)if(r[0]===-1)r[0]=q;
 let b=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([s,w,d])=>s.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc,u,v};
}
function compose(){
 const A=compile(1,4),B=compile(4,1),q=A.q+B.q;
 // A's halt target is exactly B's initial state, with the same head/tape.
 const T=A.T.concat(B.T.map(([a,w,d])=>[a+A.q,w,d]));
 const b=q.toString(2).length,desc="111"+"1".repeat(q)+"0"+T.map(([a,w,d])=>a.toString(2).padStart(b,"0")+w.toString(2).padStart(2,"0")+(d+1).toString(2).padStart(2,"0")).join("");
 return {q,T,desc};
}
function audit(){
 const ok=(x,s)=>{if(!x)throw Error(s)};
 const A=compile(1,4),B=compile(4,1),C=compose();
 function decode(d){
  let j=3;while(d[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;let T=[];
  ok(d.startsWith("111")&&q>0&&d.length-j===3*q*(b+4),"descriptor");
  for(let i=0;i<3*q;i++){let a=parseInt(d.slice(j,j+b),2),w=parseInt(d.slice(j+b,j+b+2),2),m=parseInt(d.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&m>=-1&&m<=1,"range");T.push([a,w,m]);}
  return {q,T};
 }
 for(let M of [A,B,C])ok(JSON.stringify(decode(M.desc))===JSON.stringify({q:M.q,T:M.T}),"decode roundtrip");
 function run(M,input,limit=Infinity){
  let tape=new Map([...input].map((s,i)=>[i,+s])),head=0,state=0,steps=0,lo=0,hi=0;
  while(state!==M.q&&steps<limit){let [s,w,d]=M.T[3*state+(tape.get(head)??2)];if(w===2)tape.delete(head);else tape.set(head,w);head+=d;state=s;steps++;lo=Math.min(lo,head);hi=Math.max(hi,head);}
  return {halt:state===M.q,head,steps,lo,hi,tape};
 }
 function check(M,s){
  let input=[...s].map(b=>b.repeat(M.u)).join(""),want=[...s].map(b=>b.repeat(M.v)).join(""),n=s.length,r=run(M,input);
  let clock=n?(M.u+M.v)*n*(n+1)+(M.v+4)*n+3:1;
  ok(r.halt&&r.steps===clock,"exact clock "+[M.u,n,r.steps,clock]);
  ok(r.head===(n?-M.v*n-1:0),"halt head");
  ok(r.hi-r.lo+1===(n?(M.u+M.v)*n+3:1),"span");
  ok(r.tape.size===want.length&&[...want].every((b,i)=>r.tape.get(r.head+i)===+b),"exact output and cleanup");
  return r;
 }
 let exhaustive=0,transitions=0,roundtrips=0,cutoffs=0,malformed=0,malformedTransitions=0,composedTransitions=0,composedCutoffs=0,scaling=[];
 for(let n=0;n<=8;n++)for(let a=0;a<2**n;a++){
  let s=n?a.toString(2).padStart(n,"0"):"";
  let x=check(A,s),y=check(B,s);exhaustive+=2;transitions+=x.steps+y.steps;
  let prepared=Array.from({length:4*n},(_,i)=>String(x.tape.get(x.head+i))).join("");
  ok(prepared===[...s].map(b=>b.repeat(4)).join(""),"roundtrip input");
  let z=run(C,s);ok(z.halt&&z.steps===x.steps+y.steps&&z.head===(n?-5*n-2:0)&&z.hi-z.lo+1===(n?6*n+4:1)&&z.tape.size===n&&[...s].every((b,i)=>z.tape.get(z.head+i)===+b),"same-tape roundtrip");roundtrips++;composedTransitions+=z.steps;
  if(a===0){ok(!run(C,s,z.steps-1).halt,"composed cutoff");composedCutoffs++;}
  if(a===0)for(let [M,r] of [[A,x],[B,y]]){ok(!run(M,[...s].map(b=>b.repeat(M.u)).join(""),r.steps-1).halt,"short clock");cutoffs++;}
 }
 for(let n=1;n<=9;n++)for(let a=0;a<2**n;a++){
  let s=a.toString(2).padStart(n,"0");
  if(n%4===0&&s.match(/.{4}/g).every(w=>w==="0000"||w==="1111"))continue;
  let r=run(B,s);ok(r.halt&&!r.tape.has(r.head),"malformed pack must halt on blank");malformed++;malformedTransitions+=r.steps;
 }
 for(let n of [16,32,64,128,256]){
  let s=Array.from({length:n},(_,i)=>String((i+Math.floor(i/7))%2)).join("");
  let x=check(A,s),y=check(B,s);scaling.push([n,x.steps,y.steps,x.hi-x.lo+1,y.hi-y.lo+1]);
 }
 return {machines:[[A.q,A.desc.length],[B.q,B.desc.length],[C.q,C.desc.length]],exhaustive,transitions,roundtrips,composedTransitions,composedCutoffs,cutoffs,malformed,malformedTransitions,scaling};
}
if(process.argv.includes('--expand-description')) console.log(compile(1,4).desc); else if(process.argv.includes('--pack-description')) console.log(compile(4,1).desc); else if(process.argv.includes('--roundtrip-description')) console.log(compose().desc); else console.log('F038_REX_PHYSICAL_CODEC_OK '+JSON.stringify(audit()));
