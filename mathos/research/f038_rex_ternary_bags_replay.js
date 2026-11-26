// Independent sparse-table replay of a complete physical serializer.
function replay(P,E,R){
 const C=P.compile(),M={...P.decode(C.desc),serializationEntry:C.serializationEntry},raw=E.encode(2,[1,0],[[-1],[-3],[-5],[-7],[-9],[-11],[-13],[-15],[-17]]),v=P.run(M,raw),ok=(a,s)=>{if(!a)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=[];for(let i=0;i<3*q;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&d>=-1&&d<=1,"descriptor field");table.push([a,w,d]);}ok(j===C.desc.length,"descriptor size");
 let tape=new Map([...raw].map((x,i)=>[i,+x])),h=0,state=0,t=0;
 while(state!==q&&t<v.t){let [a,w,d]=table[3*state+(tape.get(h)??2)];if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
 ok(state===q&&t===v.t&&h===v.checkpoint.head&&!tape.has(h),"sparse halt");
 const p=v.checkpoint;let out="",pos=h+1;while(tape.has(pos))out+=tape.get(pos++);
 ok(out===v.prepared&&out===R.producer(raw).prepared,"sparse prepared");
 let cursor=p.selectorStart-1;for(let expect of [...p.masks,p.pins]){ok(!tape.has(cursor),"delimiter");cursor--;let bits="";while(tape.has(cursor))bits+=tape.get(cursor--);ok(bits===expect,"sparse preserved mask");}
 ok(cursor===p.leftBoundary&&tape.size===p.selector.length+p.workBits+p.maskBits+p.pins.length+out.length,"sparse tape shape");
 return{replays:1,transitions:t,preparedBits:out.length,maskBits:p.maskBits};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_TERNARY_BAGS_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_ternary_bags.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_multitape_producer.js'))));
