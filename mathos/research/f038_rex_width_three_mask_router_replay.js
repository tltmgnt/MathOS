// Independent sparse packed-table replay. Does not claim serialized descriptor decoding.
function replay(A,C,P,K,L,E){
 const J=P.compact(A.machine(C)),M=K.compile(J),ok=(x,s)=>{if(!x)throw Error(s)};
 let entries=0;for(let v of M.T){ok((v>>>4)<=M.q&&(v>>2&3)<=2&&(v&3)<=2,"packed fields");entries++;}
 ok(entries===3*M.q,"entry count");
 const G=L.compile(),D={...L.decode(G.desc),loaderEntry:G.loaderEntry,plannerEntry:G.plannerEntry,pushEntry:G.pushEntry,popEntry:G.popEntry},B=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]],p=L.run(D,E.encode(2,[1,0],B),5000000000,null,true);
 ok(p.status==="MASK_STREAM_LOADED","producer");
 const i=p.snapshot.indexOf("H"),header=p.snapshot.slice(i,i+851).replaceAll("_","b"),input=[...Array(19).fill(""),header,p.stream,"11111111"],raw=K.encode(M,J,input),tape=new Map([...raw].map((v,i)=>[i,+v]));
 let s=0,h=0,t=0,clock=18903682,hi=raw.length-1;
 while(s!==M.q&&t<clock){let v=M.T[3*s+(tape.get(h)??2)],w=v>>2&3;if(w===2)tape.delete(h);else tape.set(h,w);h+=(v&3)-1;s=v>>>4;t++;hi=Math.max(hi,h);}
 ok(s===M.q&&h===0&&t===clock&&hi+1===14810,"exact sparse halt");
 const inv=Object.fromEntries(Object.entries(M.codes).map(([s,c])=>[c,s]));let words=[],heads=[],word="",head=null,cell=0;
 for(let i=0;i<=hi;i+=M.w){let sym=inv[Array.from({length:M.w},(_,j)=>tape.get(i+j)??2).join("")];if(i===0){ok(sym==="G","start");continue;}if(sym==="D"||sym==="E"){ok(head!==null,"head");words.push(word.replace(/_+$/,""));heads.push(head);word="";head=null;cell=0;if(sym==="E")break;continue;}ok(sym&&/^[uh]/.test(sym),"segment");if(sym[0]==="h"){ok(head===null,"duplicate head");head=cell;}if(cell===0)ok(sym.slice(1)==="L","left sentinel");else word+=sym.slice(1);cell++;}
 ok(words.length===22&&words.slice(0,10).join("|")==="1|1|1000000000000000000000000000|00||||||"&&words[17]==="0;1;"&&words.slice(19).join("|")===input.slice(19).join("|"),"sparse config/output");
 const cutoffs=[0,1,100,clock-1];for(let n of cutoffs){let r=K.run(M,raw,n);ok(r.status==="TIMEOUT"&&r.t===n,"cutoff");}
 const complete=K.run(M,raw,clock);ok(complete.status==="COMPLETE"&&complete.tapes.join("|")===words.join("|")&&complete.heads.join()===heads.join(),"exact budget");
 const rejects=[];for(let [header,stream,ord] of [["",p.stream,""],[input[19],"11",""],[input[19],p.stream,"111111111"]]){let r=K.run(M,K.encode(M,J,[...Array(19).fill(""),header,stream,ord]),300000000);ok(r.status==="REJECT","physical malformed");rejects.push(r.t);}
 return{q:M.q,entries,t,span:hi+1,output:words[17],cutoffs,rejects};
}
module.exports={replay};
if(require.main===module){const A=require('./f038_rex_width_three_mask_router.js'),C=require('./f038_rex_width_three_tuple_cursor.js'),P=require('./f038_rex_width_three_projection.js'),K={...require('./f038_rex_width_three_compiler.js'),...require('./f038_rex_width_three_local_compiler.js')},L=require('./f038_rex_width_three_direct_loader.js'),E=require('./f038_tga_normalized_integration.js').engine();console.log('F038_REX_WIDTH_THREE_MASK_ROUTER_REPLAY_OK '+JSON.stringify(replay(A,C,P,K,L,E)));}
