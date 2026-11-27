// REX-024D4B: original halt-head witness projection and blank exits.
function projector(M){
 const {w,codes}=M,defs=new Map(),add=(n,f)=>{if(defs.has(n))throw Error("duplicate "+n);defs.set(n,f);return n;},r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",2);
 function walk(n,dir,k,d){for(let i=k;i>0;i--)add(n+i,a=>(dir===1?r:l)(i===1?d:n+(i-1),a));return k?n+k:d;}
 function scan(n,dir,d){return add(n,a=>a===2?z(d,a):(dir===1?r:l)(n,a));}
 const inv=new Map(Object.entries(codes).filter(([s,c])=>!c.includes("2")).map(([s,c])=>[c,s]));
 function read(n,choose,p=""){return add(n+p,a=>{if(a===2)return bad();let b=p+a;if(b.length===w)return choose(inv.get(b),a);return r(n+b,a);});}
 function tree(n,choose,p=""){if(p.length===w)return;read(n,choose,p);tree(n,choose,p+"0");tree(n,choose,p+"1");}
 const finish=scan("finish",1,"atEnd");add("atEnd",a=>a===2?r("outHalt",a):bad());add("outHalt",a=>z("HALT",a));
 for(let b=0;b<2;b++){
  const n="copy"+b,restore=scan(n+"Restore",-1,n+"Put");
  // Temporary marker is the first bit of the encoded source block.
  const first=+codes["u"+b][0];if(+codes["h"+b][0]!==first)throw Error("first bit");
  add(n+"Put",a=>a===2?r(walkDest(n),first):bad());
  function walkDest(n){return n+"Advance"+(w-1);}
  walk(n+"Advance",1,w-1,"value");
  add(n+"Return",a=>a===2?l(restore,a):bad());
  const back=scan(n+"Back",-1,n+"Return");
  add(n+"Append",a=>a===2?l(back,b):r(n+"Append",a));
  add(n+"Boundary",a=>a===2?r(n+"Append",a):bad());
  const go=scan(n+"Go",1,n+"Boundary");
  add(n+"Mark",a=>a===first?r(go,2):bad());
  walk(n+"Rewind",-1,w-2,n+"Mark");
 }
 // Read one encoded block at a time. The first witness symbol is
 // head-marked; subsequent ones are unmarked. Virtual blank ends output.
 tree("value",(s,a)=>s==="u0"||s==="h0"?l("copy0Rewind"+(w-2),a):s==="u1"||s==="h1"?l("copy1Rewind"+(w-2),a):s==="u_"||s==="h_"?r(finish,a):bad());
 tree("sentinel",(s,a)=>s==="uL"||s==="hL"?r("value",a):bad());
 for(let k=1;k<=57;k++){const n="skip"+k+"_",next=k===1?"sentinel":"skip"+(k-1)+"_";tree(n,(s,a)=>!s||s==="G"||s==="E"?bad():r(s==="D"?next:n,a));}
 tree("entry",(s,a)=>s==="G"?r("skip57_",a):bad());
 const names=["entry"],ids=new Map([["entry",0]]),rows=[];
 function id(n){if(n==="HALT")return -1;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [n,v,d]=defs.get(names[i])(a);rows.push((id(n)<<4)|(v<<2)|(d+1));}
 const q=names.length,T=Uint32Array.from(rows,v=>v<0?(q<<4)|(v&15):v);return{q,T};
}
function compose(B,producer,J,worker){
 const C=producer.compile(),P=producer.decode(C.desc),I=B.bridge(J),O=projector(worker),bridgeAt=P.q,workerAt=bridgeAt+I.q,outputAt=workerAt+worker.q,blankAt=outputAt+O.q,q=blankAt+1,T=new Uint32Array(3*q);
 if(worker.w!==I.w||JSON.stringify(worker.codes)!==JSON.stringify({...I.codes,"~":"2".repeat(I.w)}))throw Error("codebook");
 function append(A,base,exit){for(let i=0;i<A.T.length;i++){let v=A.T[i],n=v>>>4;T[3*base+i]=((n>=A.q?exit(n-A.q):base+n)<<4)|(v&15);}}
 append(P,0,n=>{if(n)throw Error("producer exit");return blankAt;});
 if(P.T[3*C.bridgeReady+2]>>>4!==P.q)throw Error("entry");
 T[3*C.bridgeReady+2]=(bridgeAt<<4)|9;
 append(I,bridgeAt,n=>n===0?blankAt:n===1?workerAt:(()=>{throw Error("bridge exit")})());
 append(worker,workerAt,n=>n===0?blankAt:n===1?outputAt:(()=>{throw Error("worker exit")})());
 append(O,outputAt,n=>{if(n)throw Error("projection exit");return q;});
 for(let a=0;a<3;a++)T[3*blankAt+a]=(q<<4)|9;
 return{q,T,w:worker.w,codes:worker.codes,producerStates:P.q,bridgeStates:I.q,workerStates:worker.q,outputStates:O.q,bridgeAt,workerAt,outputAt,blankAt};
}
function run(M,raw,n,limit=Infinity,initial=0){
 const origin=3*raw.length+1024;let tape=new Uint8Array(origin+2*raw.length+4096);tape.fill(2);for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let h=origin,s=initial,t=0,lo=h,hi=h,clocks={};
 const phases=["bridgeAt","workerAt","outputAt"],entries=phases.map(k=>M[k]),blankAt=M.blankAt,T=M.T,q=M.q;let phase=0,next=entries[0];
 while(s!==q&&t<limit){if(s===next){clocks[phases[phase]]=t;next=entries[++phase];}if(s===blankAt)clocks.blankAt=t;
  let v=T[3*s+tape[h]];tape[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;
  if(h<0)throw Error("left buffer");if(h===tape.length){let a=new Uint8Array(tape.length*2);a.fill(2);a.set(tape);tape=a;}if(h<lo)lo=h;if(h>hi)hi=h;
 }
 const bits=s===M.q?Array.from(tape.subarray(h,h+n)):[],witness=bits.length===n&&bits.every(x=>x<2)?bits.join(""):null;
 return{status:s===M.q?"HALT":"TIMEOUT",t,head:h-origin,span:hi-lo+1,clocks,witness,headSymbol:tape[h],nextSymbol:tape[h+n]};
}
module.exports={projector,compose,run};
