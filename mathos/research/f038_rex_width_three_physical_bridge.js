// D4A: physical producer-to-segmented configuration bridge. No host intervention during transitions.
function bridge(J){
 const syms=["G","D","E","~",...J.alphabet.flatMap(x=>["u"+x,"h"+x])],w=Math.ceil(Math.log2(syms.length-1)),codes=Object.fromEntries(syms.filter(s=>s!=="~").map((s,i)=>[s,i.toString(2).padStart(w,"0")]));
 const defs=new Map(),add=(n,f)=>{if(defs.has(n))throw Error("duplicate "+n);defs.set(n,f);return n;},r=(n,a)=>[n,a,1],l=(n,a)=>[n,a,-1],z=(n,a)=>[n,a,0],bad=()=>z("HALT",2);
 const empty=(last=false)=>["hL","u_",last?"E":"D"];
 const encode=ss=>ss.map(s=>{if(!codes[s])throw Error("code "+s);return codes[s];}).join("");
 function cross(n,dir,k,dest){if(!k)return dest;const go=dir===1?r:l;
  for(let i=1;i<=k;i++)add(n+i,a=>a===2?(i===1?z(dest,a):go(n+(i-1),a)):go(n+i,a));
  return add(n,a=>a===2?go(n+k,a):bad());
 }
 function scan(n,dir,d){const go=dir===1?r:l;return add(n,a=>a===2?z(d,a):go(n,a));}
 // From a frame delimiter, reach the stream's right blank boundary.
 function toBoundary(n,f,d){const s=scan(n+"Stream",1,d);const at=add(n+"Last",a=>a===2?r(s,a):bad());return cross(n+"Frames",1,9-f,at);}
 function fromBoundary(n,f,d){const back=cross(n+"Frames",-1,9-f,d),s=scan(n+"Stream",-1,back);return add(n,a=>a===2?l(s,a):bad());}
 // Append an encoded word to the binary region right of boundary.
 // Returning left reaches that same blank, not any source marker.
 function append(n,word,d){
  const back=scan(n+"Back",-1,d);
  for(let i=0;i<word.length;i++)add(n+"Put"+i,a=>a===2?(i===word.length-1?l(back,+word[i]):r(n+"Put"+(i+1),+word[i])):bad());
  const seek=scan(n+"Seek",1,n+"Put0");return add(n,a=>a===2?r(seek,a):bad());
 }
 const tail=encode(["u_","D",...Array.from({length:J.tapes-21},(_,i)=>empty(i===J.tapes-22)).flat()]);
 const finish=add("finish",a=>a===2?r("SUCCESS",a):bad()),finishAppend=append("tail",tail,finish);
 // Copy the contiguous raw mask stream, marking one cell blank temporarily.
 add("streamRead",a=>a===2?z(finishAppend,a):r("streamSeek"+a,2));
 for(let b=0;b<2;b++){
  const n="stream"+b,restore=scan(n+"Restore",-1,n+"Put");
  add(n+"Put",a=>a===2?r("streamRead",b):bad());
  const ret=add(n+"Return",a=>a===2?l(restore,a):bad()),put=append(n+"Append",encode(["u"+b]),ret);
  scan("streamSeek"+b,1,put);
 }
 // Copy each fixed frame from left to right. The temporary blank lies
 // inside that frame, so return from its right delimiter is unambiguous.
 for(let f=0;f<10;f++){
  const n="frame"+f,next=f===9?"streamRead":"frame"+(f+1)+"Read";
  const endNext=add(n+"Next",a=>a===2?r(next,a):bad());
  const endRet=fromBoundary(n+"EndReturn",f,endNext);
  const endApp=append(n+"EndAppend",encode(f===9?["ub","u_","D","hL"]:["ub"]),endRet);
  const endGo=toBoundary(n+"EndGo",f,endApp);
  add(n+"Read",a=>a===2?z(endGo,a):r(n+"Seek"+a,2));
  for(let b=0;b<2;b++){
   const t=n+"Bit"+b,restore=scan(t+"Restore",-1,t+"Put");
   add(t+"Put",a=>a===2?r(n+"Read",b):bad());
   const enter=add(t+"Enter",a=>a===2?l(restore,a):bad()),ret=fromBoundary(t+"Return",f,enter);
   const put=append(t+"Append",encode(["u"+b]),ret),go=toBoundary(t+"Go",f,put);
   scan(n+"Seek"+b,1,go);
  }
 }
 const first=add("first",a=>a===2?r("frame0Read",a):bad());
 const ret=fromBoundary("initialReturn",-1,first);
 const pre=encode(["G",...Array.from({length:19},()=>empty()).flat(),"hL","uH"]);
 const put=append("initialAppend",pre,ret),entry=toBoundary("initialGo",-1,put);
 const names=[entry],ids=new Map([[entry,0]]),rows=[];
 function id(n){if(n==="HALT")return -1;if(n==="SUCCESS")return -2;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){const [n,v,d]=defs.get(names[i])(a);rows.push((id(n)<<4)|(v<<2)|(d+1));}
 const q=names.length,T=Uint32Array.from(rows,v=>v<0?((q+(v>>>4===0xffffffe?1:0))<<4)|(v&15):v);
 return{q,T,w,codes};
}
function compose(producer,J,worker=null){
 const C=producer.compile(),P=producer.decode(C.desc),B=bridge(J),offset=P.q,workerAt=offset+B.q,q=workerAt+(worker?.q??0),T=new Uint32Array(3*q);
 if(worker&&(worker.w!==B.w||JSON.stringify(worker.codes)!==JSON.stringify({...B.codes,"~":"2".repeat(B.w)})))throw Error("encoding mismatch");
 const relocate=(v,n,base,exit)=>((v>>>4===n?exit:base+(v>>>4))<<4)|(v&15);
 for(let i=0;i<P.T.length;i++)T[i]=relocate(P.T[i],P.q,0,q);
 if(C.bridgeReady===undefined||P.T[3*C.bridgeReady+2]>>>4!==P.q)throw Error("producer entry");
 T[3*C.bridgeReady+2]=(offset<<4)|(2<<2)|1;
 for(let i=0;i<B.T.length;i++){let v=B.T[i],n=v>>>4;T[3*offset+i]=((n===B.q?q:n===B.q+1?(worker?workerAt:q):offset+n)<<4)|(v&15);}
 if(worker)for(let i=0;i<worker.T.length;i++)T[3*workerAt+i]=relocate(worker.T[i],worker.q,workerAt,q);
 return{q,T,bridgeAt:offset,workerAt,producerStates:P.q,bridgeStates:B.q,workerStates:worker?.q??0,w:B.w,codes:worker?.codes??{...B.codes,"~":"2".repeat(B.w)}};
}
function run(M,raw,limit=Infinity){
 const origin=3*raw.length+1024;let tape=new Uint8Array(origin+2*raw.length+4096);tape.fill(2);for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let h=origin,s=0,t=0,lo=h,hi=h,bridgeClock=null,workerClock=null,sourceHead=null,workerHead=null;
 while(s!==M.q&&t<limit){
  if(s===M.bridgeAt&&bridgeClock===null){bridgeClock=t;sourceHead=h;}
  if(s===M.workerAt&&workerClock===null){workerClock=t;workerHead=h;}
  let v=M.T[3*s+tape[h]];tape[h]=v>>2&3;h+=(v&3)-1;s=v>>>4;t++;
  if(h<0)throw Error("left buffer");if(h===tape.length){let a=new Uint8Array(tape.length*2);a.fill(2);a.set(tape);tape=a;}lo=Math.min(lo,h);hi=Math.max(hi,h);
 }
 const result={status:s===M.q?"HALT":"TIMEOUT",t,head:h-origin,span:hi-lo+1,bridgeClock,workerClock};
 if(s!==M.q)return result;
 if(bridgeClock===null)return{...result,status:"REFUSAL"};
 if(!M.workerStates){workerHead=h;workerClock=t;result.workerClock=t;}
 if(workerHead===null||h!==workerHead)throw Error("worker halt position");
 let end=workerHead;while(tape[end]!==2)end++;
 const encoded=Array.from(tape.subarray(workerHead,end)).join("");
 const source=Array.from(tape.subarray(lo,workerHead-1)).map(x=>x===2?"_":String(x));source[sourceHead-lo]="H";
 return{...result,status:"COMPLETE",encoded,source:source.join(""),workerHead:workerHead-origin};
}
module.exports={bridge,compose,run};
