// D5G compact physical bridge: skip the ten validated planner frames; copy only the mask stream onto tape 15. Project tape 0.
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
 const tail=encode(["u_","E"]);
 const finish=add("finish",a=>a===2?r("SUCCESS",a):bad()),finishAppend=append("tail",tail,finish);
 // Copy the contiguous raw mask stream, marking one cell blank temporarily.
 add("streamRead",a=>a===2?z(finishAppend,a):r("streamSeek"+a,2));
 for(let b=0;b<2;b++){
  const n="stream"+b,restore=scan(n+"Restore",-1,n+"Put");
  add(n+"Put",a=>a===2?r("streamRead",b):bad());
  const ret=add(n+"Return",a=>a===2?l(restore,a):bad()),put=append(n+"Append",encode(["u"+b]),ret);
  scan("streamSeek"+b,1,put);
 }
 const first=add("first",a=>a===2?r("streamRead",a):bad());
 const ret=fromBoundary("initialReturn",9,first);
 const pre=encode(["G",...Array.from({length:15},()=>empty()).flat(),"hL"]);
 const put=append("initialAppend",pre,ret),entry=toBoundary("initialGo",-1,put);
 const names=[entry],ids=new Map([[entry,0]]),rows=[];
 function id(n){if(n==="HALT")return -1;if(n==="SUCCESS")return -2;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){const [n,v,d]=defs.get(names[i])(a);rows.push((id(n)<<4)|(v<<2)|(d+1));}
 const q=names.length,T=Uint32Array.from(rows,v=>v<0?((q+(v>>>4===0xffffffe?1:0))<<4)|(v&15):v);
 return{q,T,w,codes};
}

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
 tree("entry",(s,a)=>s==="G"?r("sentinel",a):bad());
 const names=["entry"],ids=new Map([["entry",0]]),rows=[];
 function id(n){if(n==="HALT")return -1;if(!ids.has(n)){ids.set(n,names.length);names.push(n);}return ids.get(n);}
 for(let i=0;i<names.length;i++)for(let a=0;a<3;a++){let [n,v,d]=defs.get(names[i])(a);rows.push((id(n)<<4)|(v<<2)|(d+1));}
 const q=names.length,T=Uint32Array.from(rows,v=>v<0?(q<<4)|(v&15):v);return{q,T};
}

function compose(producer,J,worker){
 const C=producer.compile(),P=producer.decode(C.desc),I=bridge(J),O=projector(worker),bridgeAt=P.q,workerAt=bridgeAt+I.q,outputAt=workerAt+worker.q,blankAt=outputAt+O.q,q=blankAt+1,T=new Uint32Array(3*q);
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

module.exports={bridge,projector,compose};
