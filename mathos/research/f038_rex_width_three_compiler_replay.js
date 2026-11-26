// Independent streamed original descriptor parser and sparse ternary replay.
function replay(K){
 const J=K.machine(),M=K.compile(J),ok=(v,s)=>{if(!v)throw Error(s)},stream=K.descriptorChunks(M),header=stream.next().value,q=header.length-4,b=q.toString(2).length,field=b+4;
 ok(header.startsWith("111")&&header.endsWith("0")&&!header.slice(3,-1).includes("0")&&q===M.q,"unary state header");
 let T=new Uint32Array(3*q),j=0,bits=header.length;
 for(let chunk of stream){ok(chunk.length%field===0,"alignment");bits+=chunk.length;for(let i=0;i<chunk.length;i+=field){let next=parseInt(chunk.slice(i,i+b),2),write=parseInt(chunk.slice(i+b,i+b+2),2),move=parseInt(chunk.slice(i+b+2,i+field),2);ok(next<=q&&write<=2&&move<=2&&j<T.length,"codec fields");T[j]=(next<<4)|(write<<2)|move;ok(T[j]===M.T[j],"entry equality");j++;}}
 ok(j===3*q&&bits===4+q+3*q*field,"descriptor length");
 const rows=[];
 for(let [name,p,c,clock,support,out] of [["stable","01:10;00:01;01:11;11:00;","01:1;00:0;01:0;",5554143,"00:;01:;","00:01;01:10;01:11;"],["parity","001:0;010:0;100:0;111:0;","000:;011:;101:;110:;",7288731,"000:;011:;101:;110:;",""]]){
  const input=K.encode(M,J,[p,c,"","","","",""]),tape=new Map([...input].map((v,i)=>[i,+v]));let s=0,h=0,t=0;
  while(s!==q&&t<clock){let v=T[3*s+(tape.get(h)??2)],a=v>>>4,w=v>>2&3,d=(v&3)-1;if(w===2)tape.delete(h);else tape.set(h,w);s=a;h+=d;t++;}
  ok(s===q&&h===0&&t===clock,"exact sparse halt");
  const inv=Object.fromEntries(Object.entries(M.codes).map(([s,c])=>[c,s]));let word="",words=[],n=0;
  for(let i=0;i<tape.size;i+=M.w){let sym=inv[Array.from({length:M.w},(_,j)=>tape.get(i+j)??2).join("")];if(i===0){ok(sym==="G","start");continue;}if(sym==="D"||sym==="E"){ok(n===1,"head marker");words.push(word.replace(/_+$/,""));word="";n=0;if(sym==="E")break;continue;}ok(sym&&/^[uh]/.test(sym),"segment");n+=+(sym[0]==="h");if(sym.slice(1)!=="L")word+=sym.slice(1);}
  ok(words.length===7&&words[4]===support&&words[6]===out,"sparse output");rows.push({name,t,output:out,support});
 }
 return{q,bits,transitionEntries:j,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_COMPILER_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_three_compiler.js'))));
