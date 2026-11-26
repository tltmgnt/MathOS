// REX-024D2C independent descriptor parser and sparse physical replay.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;const q=j-3,b=q.toString(2).length;j++;
 const table=new Uint32Array(3*q);
 for(let i=0;i<table.length;i++){const a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2);j+=b+4;ok(a<=q&&w<=2&&d<=2,"descriptor fields");table[i]=(a<<4)|(w<<2)|d;}
 ok(j===C.desc.length,"descriptor size");
 const m=2,pins=[1,0],B=[[-1,-3,-5],[-2,-4,-7],[-1,-6,-8],[-3,-5,-7],[-2],[-1,-4]],raw=E.encode(m,pins,B),D=E.decode(raw),tape=new Map([...raw].map((a,i)=>[i,+a]));
 let s=0,h=0,t=0;const clock=104728446;
 while(s!==q&&t<clock){let v=table[3*s+(tape.get(h)??2)],w=v>>2&3;if(w===2)tape.delete(h);else tape.set(h,w);h+=(v&3)-1;s=v>>>4;t++;}
 ok(s===q&&t===clock&&h===raw.length-1&&!tape.has(h),"exact physical halt");
 const V=[0,1,2,3,4,5,6,7,8],scopes=[1,2,3].flatMap(k=>[...E.subsets(V,k)]),masks=scopes.map(h=>{const f=D.F.find(f=>f.h.join()===h.join());return [...E.tup(m,h.length)].map(z=>+(!!f&&!f.S.has(z.join()))).join("");});
 const word=["1",pins.join(""),...masks].map(f=>[...f].map(x=>"0"+x).join("")+"10").join("");
 const boundary=h+850;ok(!tape.has(boundary)&&!tape.has(boundary+word.length+1),"output delimiters");
 ok(Array.from({length:word.length},(_,i)=>tape.get(boundary+1+i)).join("")===word,"exact independent output");
 let at=h-26;while(tape.has(at-1))at--;ok(Array.from({length:h-26-at},(_,i)=>tape.get(at+i)).join("")===raw.slice(32),"selector preservation");
 let cursor=at-1;
 const edges=V.flatMap(a=>V.filter(b=>b>a).map(b=>[a,b])),graph=new Set(D.F.flatMap(f=>[...E.subsets(f.h,2)].map(h=>h.join())));
 for(let want of edges.map(e=>graph.has(e.join())?"1":"").concat(pins.join(""),masks)){
  ok(!tape.has(cursor),"left delimiter");cursor--;let got="";while(tape.has(cursor))got+=tape.get(cursor--);ok(got===want,"preserved block");
 }
 ok(tape.size===raw.length-32+25+graph.size+2+834+840+word.length,"whole tape nonblank accounting");
 return{q,bits:C.desc.length,entries:table.length,t,head:h,streamBits:word.length,maskBits:834,fields:131};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_DIRECT_LOADER_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_three_direct_loader.js'),require('./f038_tga_normalized_integration.js').engine())));
