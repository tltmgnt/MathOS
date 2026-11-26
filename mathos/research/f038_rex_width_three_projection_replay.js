// Independent streamed original descriptor parser and sparse projection replay.
function replay(P,K){
 const J=P.compact(P.machine()),M=K.compile(J),ok=(v,s)=>{if(!v)throw Error(s)},stream=K.descriptorChunks(M),header=stream.next().value,q=header.length-4,b=q.toString(2).length,field=b+4;
 ok(header.startsWith("111")&&header.endsWith("0")&&!header.slice(3,-1).includes("0")&&q===M.q,"header");
 const T=new Uint32Array(3*q);let j=0,bits=header.length;
 for(let chunk of stream){ok(chunk.length%field===0,"alignment");bits+=chunk.length;for(let i=0;i<chunk.length;i+=field){let next=parseInt(chunk.slice(i,i+b),2),write=parseInt(chunk.slice(i+b,i+b+2),2),move=parseInt(chunk.slice(i+b+2,i+field),2);ok(next<=q&&write<=2&&move<=2&&j<T.length,"fields");T[j]=(next<<4)|(write<<2)|move;ok(T[j]===M.T[j],"entry equality");j++;}}
 ok(j===3*q&&bits===4+q+3*q*field,"length");
 const rows=[];
 for(let [name,p,c,pm,cm,clock,support,out] of [["nonadjacent","0,1,0,1;1,0,0,1;1,1,1,0;","0,0,1;1,1,0;","1011","111",53750915,"001000100110:;011001100010:;","0,1,0,1;1,1,1,0;"],["collision","0,01;00,1;","00,1;","11","11",8635461,"0000100110:;","00,1;"]]){
  const input=K.encode(M,J,[p,c,"","","","","",pm,cm,""]),tape=new Map([...input].map((v,i)=>[i,+v]));let s=0,h=0,t=0;
  while(s!==q&&t<clock){let v=T[3*s+(tape.get(h)??2)],a=v>>>4,w=v>>2&3,d=(v&3)-1;if(w===2)tape.delete(h);else tape.set(h,w);s=a;h+=d;t++;}
  ok(s===q&&h===0&&t===clock,"exact sparse halt");
  const inv=Object.fromEntries(Object.entries(M.codes).map(([s,c])=>[c,s]));let word="",words=[],n=0;
  for(let i=0;i<tape.size;i+=M.w){let sym=inv[Array.from({length:M.w},(_,j)=>tape.get(i+j)??2).join("")];if(i===0){ok(sym==="G","start");continue;}if(sym==="D"||sym==="E"){ok(n===1,"head marker");words.push(word.replace(/_+$/,""));word="";n=0;if(sym==="E")break;continue;}ok(sym&&/^[uh]/.test(sym),"segment");n+=+(sym[0]==="h");if(sym.slice(1)!=="L")word+=sym.slice(1);}
  ok(words.length===10&&words[4]===support&&words[7]===pm&&words[8]===cm&&words[9]===out,"sparse output");rows.push({name,t,output:out,support});
 }
 return{q,bits,transitionEntries:j,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_PROJECTION_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_compiler.js'))));
