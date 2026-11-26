// Independent streamed original descriptor parser and sparse replay; genuine mask grammar precondition.
function replay(A,P,K){
 const J=P.compact(A.machine()),M=K.compile(J),ok=(v,s)=>{if(!v)throw Error(s)};
 const stream=K.descriptorChunks(M),header=stream.next().value,q=header.length-4,b=q.toString(2).length,field=b+4;
 ok(header.startsWith("111")&&header.endsWith("0")&&!header.slice(3,-1).includes("0")&&q===M.q,"header");
 const T=new Uint32Array(3*q);let j=0,bits=header.length;
 for(let chunk of stream){ok(chunk.length%field===0,"alignment");bits+=chunk.length;for(let i=0;i<chunk.length;i+=field){let next=parseInt(chunk.slice(i,i+b),2),write=parseInt(chunk.slice(i+b,i+b+2),2),move=parseInt(chunk.slice(i+b+2,i+field),2);ok(next<=q&&write<=2&&move<=2&&j<T.length,"fields");T[j]=(next<<4)|(write<<2)|move;ok(T[j]===M.T[j],"entry equality");j++;}}
 ok(j===3*q&&bits===4+q+3*q*field,"length");
 const inputs=["1","11","1000110000000000000000000000","00","1000","","","","","",...Array(9).fill("")];
 const raw=K.encode(M,J,inputs),tape=new Map([...raw].map((v,i)=>[i,+v]));let s=0,h=0,t=0,clock=1195509;
 while(s!==q&&t<clock){let v=T[3*s+(tape.get(h)??2)],w=v>>2&3;if(w===2)tape.delete(h);else tape.set(h,w);h+=(v&3)-1;s=v>>>4;t++;}
 ok(s===q&&h===0&&t===clock,"exact sparse halt");
 const inv=Object.fromEntries(Object.entries(M.codes).map(([s,c])=>[c,s]));let words=[],heads=[],word="",head=null,cell=0;
 for(let i=0;i<tape.size;i+=M.w){let sym=inv[Array.from({length:M.w},(_,j)=>tape.get(i+j)??2).join("")];if(i===0){ok(sym==="G","start");continue;}if(sym==="D"||sym==="E"){ok(head!==null,"head");words.push(word.replace(/_+$/,""));heads.push(head);word="";head=null;cell=0;if(sym==="E")break;continue;}ok(sym&&/^[uh]/.test(sym),"segment");if(sym[0]==="h"){ok(head===null,"duplicate head");head=cell;}if(cell===0)ok(sym.slice(1)==="L","left sentinel");else word+=sym.slice(1);cell++;}
 ok(words.length===19&&words.slice(0,10).join("|")===inputs.slice(0,10).join("|")&&words[17]==="0,1;1,0;1,1;"&&words.slice(10,17).join("|")==="0|0|0|0|xx|xx|xx","sparse output and rank state");
 const cutoffs=[0,1,100,clock-1];for(let n of cutoffs){let r=K.run(M,raw,n);ok(r.status==="TIMEOUT"&&r.t===n,"cutoff");}
 const complete=K.run(M,raw,clock);ok(complete.status==="COMPLETE"&&complete.tapes.join("|")===words.join("|")&&complete.heads.join()===heads.join(),"exact budget");
 let no=inputs.slice();no[3]="11";let r=K.run(M,K.encode(M,J,no),100000000);ok(r.status==="COMPLETE"&&r.tapes[17]==="","empty relation");
 return{q,bits,entries:j,t,output:words[17],heads,cutoffs,emptyClock:r.t};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_TUPLE_CURSOR_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_three_tuple_cursor.js'),require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_compiler.js'))));
