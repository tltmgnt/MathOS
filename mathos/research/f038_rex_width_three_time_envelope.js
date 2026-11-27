// Conservative explicit virtual-time envelope; genuine checkpoint inputs only.
function envelope(m,Space){
 const {b,S,R,K,N}=Space.space(m),M=BigInt(m),rows=M**4n;
 // Deliberately loose budgets for the finite, fixed nine-bag worker.
 const local=1000n*S+1000000n+10000n*(b+1n)*rows+50n*N;
 const edge=1000n*K*(4n*b+1n)+1000000n+50n*N;
 const select=10000n*(b+1n)*rows+100000n+50n*N;
 const translate=10000n*M*(b+1n)+10000n+10n*N;
 const T=9n*local+9n*edge+9n*select+translate+10000n;
 return {local,edge,select,translate,T,N,physical:(26n*N+16n)*T+8n};
}
function countPhases(J,I,Space,m){
 const T=I.map(x=>["L",...x,"_"]),h=I.map(()=>0),B=envelope(m,Space),ledger={local:[],edge:[],select:[],translate:0},ok=(v,s)=>{if(!v)throw Error(s)};
 let pc=J.entry,steps=0,phase="local",at=0,jumps=0;
 function flush(next){if(phase==="translate")ledger.translate+=steps-at;else if(steps>at)ledger[phase].push(steps-at);at=steps;phase=next;}
 while(true){
  if(pc===J.edge)flush("edge");
  if(pc===J.selectEntry)flush("select");
  if(pc===J.translateEntry)flush("translate");
  const a=J.ins[pc],k=a.t,x=T[k][h[k]]??"_";
  if(a.op==="jump"){pc=a.next;ok(++jumps<100000000,"jump budget");continue;}
  if(a.op==="halt"){flush(phase);break;}
  ok(a.op!=="reject"&&steps<100000000,"IR reject/timeout");
  steps++;
  if(a.op==="read"){pc=a.next[J.alphabet.indexOf(x)];continue;}
  if(a.op==="write"){ok(x!=="L","sentinel");T[k][h[k]]=a.next.v;}
  else if(a.op==="move"){h[k]+=a.next.dir;ok(h[k]>=0,"left");if(h[k]===T[k].length)T[k].push("_");}
  else throw Error("opcode");
  pc=a.next.d;
  if(pc===J.localDone)flush("local");
  if(pc===J.selected)flush("select");
 }
 // Bound total per-phase costs rather than requiring the observer
 // boundary to coincide with every source-level iteration.
 const sum=a=>a.reduce((n,x)=>n+x,0),totals={local:sum(ledger.local),edge:sum(ledger.edge),select:sum(ledger.select),translate:ledger.translate};
 ok(Object.values(totals).reduce((a,b)=>a+b,0)===steps,"ledger");
 for(let [k,n] of Object.entries(totals))ok(BigInt(n)<=B[k]*(k==="translate"?1n:9n)+10000n,"phase bound "+k);
 ok(BigInt(steps)<=B.T,"total");
 return {steps,totals,ledger,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h,bounds:Object.fromEntries(Object.entries(B).map(([k,v])=>[k,v.toString()]))};
}
module.exports={envelope,countPhases};
