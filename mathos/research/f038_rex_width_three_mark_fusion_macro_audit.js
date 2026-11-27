// D6S independent physical macro audit. No original-format producer needed
// for isolated worker tests; execute actual ternary transitions and compare
// every cell, exit, head and count with a separately decoded logical model.
function audit(K,F){
 const alphabet=["L","0","_","1","x"],ok=(b,s)=>{if(!b)throw Error(s)};
 function encode(T,h,codes,status="halt"){return [status==="reject"?"~":"G",...T.flatMap((t,k)=>[...t.map((x,j)=>(h[k]===j?"h":"u")+x),k===T.length-1?"E":"D"])].map(x=>codes[x]).join("");}
 function run(M,s,limit=10000000){const a=new Uint8Array(s.length+128);a.fill(2);for(let i=0;i<s.length;i++)a[32+i]=+s[i];let h=32,q=0,t=0;
  while(q<M.q&&t<limit){const v=M.T[3*q+a[h]];a[h]=(v>>2)&3;h+=(v&3)-1;q=v>>>4;t++;ok(h>=0&&h<a.length,"buffer");}
  ok(q>=M.q&&t<limit,"macro halt");return {q:q-M.q,h:h-32,t,tape:a};}
 let cases=0,reads=0,writes=0,lefts=0,rights=0,growth=0,rejects=0,clockChecks=0,exactScannerParity=0,exactDeltaChecks=0,strictSavings=0,localProgramChecks=0,localLinks=0,localSavings=0;
 for(const [paired,special] of [[false,false],[true,false],[true,true]])for(let k=0;k<3;k++){
  const ops=[...alphabet.map(v=>({op:"read",t:k,next:alphabet.map(x=>x===v?1:2)})),...alphabet.slice(1).map(v=>({op:"write",t:k,next:{v,d:1}})),...[-1,1].map(dir=>({op:"move",t:k,next:{dir,d:1}}))];
  for(const I of ops){
   const J={alphabet,tapes:3,entry:0,ins:[I,{op:"halt",t:0,next:0},{op:"reject",t:0,next:0}]},M=K.compile(J,paired,special);
   const baseline=special?K.compile(J,true,true,true,false,false,false):null;const codes=M.codes;ok(new Set(Object.values(codes)).size===14,"injective");
   for(const v of alphabet)if(paired)ok(codes["h"+v].slice(0,3)===codes["u"+v].slice(0,3)&&codes["h"+v][3]!==codes["u"+v][3],"paired");
   for(const s of ["","0","1","x","_","01x_","1x10","0000"])for(let h0=0;h0<s.length+2;h0++){
    const T=[["L",..."01x_","_"],["L",..."x001","_"],["L",..."_10x","_"]],h=[2,3,4];T[k]=["L",...s,"_"];h[k]=h0;
    if((I.op==="write"||I.op==="move"&&I.next.dir===-1)&&h0===0)continue;
    const input=encode(T,h,codes),expectedDelta=I.op==="move"&&I.next.dir===-1?6:0;
    let status="halt",x=T[k][h0];
    if(I.op==="read"){reads++;if(I.next[alphabet.indexOf(x)]===2){status="reject";rejects++;}}
    if(I.op==="write"){writes++;T[k][h0]=I.next.v;}
    if(I.op==="move"){if(I.next.dir===1){rights++;if(h0+1===T[k].length){T[k].push("_");growth++;}}else lefts++;h[k]+=I.next.dir;}
    const a=run(M,input),expected=encode(T,h,codes,status);
    ok(a.q===(status==="halt"?1:0)&&a.h===0,"exit/head "+I.op);
    ok(Array.from(a.tape.slice(32,32+expected.length)).join("")===expected&&a.tape[32+expected.length]===2&&a.tape[31]===2,"physical contents "+I.op+" "+s+" "+h0);if(baseline){const b=run(baseline,input);ok(a.t<=b.t&&a.q===b.q&&a.h===b.h&&a.tape.every((x,i)=>x===b.tape[i]),'serial macro parity');ok(b.t-a.t===expectedDelta,'independent directional mark delta');exactDeltaChecks++;if(expectedDelta>0)strictSavings++;exactScannerParity++;}cases++;
   }
  }
  // Multi-primitive programs exercise terminal clock accounting with
  // arbitrary suffix marks after writes, moves, interior and end growth.
  for(const s of ["","0","1","x","_","01x_","1x10","0000"]){
   const ins=[],emit=(op,t,next)=>ins.push({op,t,next}),move=(t,dir)=>emit("move",t,{dir,d:ins.length+1}),write=(t,v)=>emit("write",t,{v,d:ins.length+1});
   for(let j=0;j<3;j++){move(j,1);write(j,alphabet[1+j]);move(j,1);move(j,1);write(j,"x");move(j,-1);}
   for(let j=0;j<s.length+4;j++)move(k,1);
   emit("halt",0,0);const J={alphabet,tapes:3,entry:0,ins},M=K.compile(J,paired,special),I=[s,"01x","_10"],T=I.map(s=>["L",...s,"_"]),a=run(M,encode(T,[0,0,0],M.codes)),c=F.count(J,I,M.codes,100000000,special);
   ok(a.t===c.clock&&a.q===1&&a.h===0&&Array.from(a.tape.slice(32,32+c.encoded.length)).join("")===c.encoded,"exact clock");if(special){const b=run(K.compile(J,true,true,true,false,false,false),encode(T,[0,0,0],M.codes));ok(a.t<=b.t&&a.q===b.q&&a.h===b.h&&a.tape.every((x,i)=>x===b.tape[i]),'serial program parity');exactScannerParity++;}clockChecks++;
  }
 }
 // Independent logical simulation computes savings from actual
 // head positions, without invoking either clock model. Compare
 // branch-dependent local read/write links across jump chains.
 for(let k=0;k<3;k++)for(const s of ["0","1","x","_","01x_","1x10","0000",""]){
  const t=(k+1)%3,J={alphabet,tapes:3,entry:0,ins:[
   {op:"move",t:k,next:{dir:1,d:1}},
   {op:"read",t:k,next:[2,3,4,5,6]},
   ...Array.from({length:5},(_,j)=>({op:"jump",next:7+j})),
   ...alphabet.map((v,j)=>({op:"write",t:k,next:{v:alphabet[1+j%4],d:12}})),
   {op:"read",t:k,next:[13,13,14,14,13]},
   {op:"read",t:k,next:[15,15,15,15,15]},
   {op:"move",t:k,next:{dir:1,d:16}},
   {op:"move",t:k,next:{dir:-1,d:16}},
   {op:"move",t,next:{dir:1,d:17}},
   {op:"write",t,next:{v:"x",d:18}},
   {op:"read",t,next:[19,19,19,19,19]},
   {op:"halt",t:0,next:0}
  ]};
  const input=[s,"01x","_10"],T=input.map(x=>["L",...x,"_"]),h=[0,0,0],M=K.compile(J),B=K.compile(J,true,true,true,false,false,false);
  const encoded=encode(T,h,M.codes),a=run(M,encoded),b=run(B,encoded);let pc=0,delta=0,links=0,saved=0;
  while(J.ins[pc].op!=="halt"){
   const I=J.ins[pc];if(I.op==="jump"){pc=I.next;continue;}
   const g=I.t,idx=1+h[g]+T.slice(0,g).reduce((n,x)=>n+x.length+1,0);
   if(I.op==="read")pc=I.next[alphabet.indexOf(T[g][h[g]])];
   else if(I.op==="write"){T[g][h[g]]=I.next.v;pc=I.next.d;}
   else if(I.op==="move"){if(I.next.dir===-1)delta+=6;h[g]+=I.next.dir;if(h[g]===T[g].length)T[g].push("_");pc=I.next.d;}
   else throw Error("test op");
   let d=pc;while(J.ins[d].op==="jump")d=J.ins[d].next;
   if((I.op==="read"||I.op==="write")&&J.ins[d].t===g&&["read","write","move"].includes(J.ins[d].op)){const n=8*idx+(I.op==="read"?1:0);links++;saved+=n;delta+=n;}
  }
  const c=F.count(J,input,M.codes);ok(a.q===1&&a.h===0&&a.t===c.clock&&c.localLinks===links&&b.t-a.t===delta&&a.tape.every((v,i)=>v===b.tape[i])&&Array.from(a.tape.slice(32,32+encode(T,h,M.codes).length)).join("")===encode(T,h,M.codes),"independent local link delta");localProgramChecks++;localLinks+=links;localSavings+=saved;
 }
 // Zero-primitive terminals must include the extra reject rewrite step.
 for(const op of ["halt","reject"]){const J={alphabet,tapes:1,entry:0,ins:[{op,t:0,next:0}]},M=K.compile(J),c=F.count(J,[""],M.codes),v=run(M,encode([["L","_"]],[0],M.codes));ok(c.clock===c.upper&&c.clock===v.t&&v.q===(op==="halt"?1:0),"zero primitive terminal");}
 return {cases,reads,writes,lefts,rights,growth,rejects,clockChecks,exactScannerParity,exactDeltaChecks,strictSavings,localProgramChecks,localLinks,localSavings};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_mark_fusion_compiler.js"),require("./f038_rex_width_three_mark_fusion_clock.js"))));
