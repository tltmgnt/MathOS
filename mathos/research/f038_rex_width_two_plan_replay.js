// REX-023B independent sparse physical interpreter.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=[];for(let i=0;i<3*q;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&d>=-1&&d<=1,"descriptor field");table.push([a,w,d]);}
 ok(j===C.desc.length,"descriptor length");
 const rows=[];
 for(let [name,B,clock] of [["outside-triple",[[-1,-9,-17]],8080323],["K4",[[-1,-3],[-1,-5],[-1,-7],[-3,-5],[-3,-7],[-5,-7]],8042470]]){
  const pins=name==="K4"?[1,1]:[0,1],raw=E.encode(2,pins,B),ref=P.run(P.decode(C.desc),raw,clock),p=ref.checkpoint;
  let tape=new Map([...raw].map((v,i)=>[i,+v])),h=0,state=0,t=0;
  while(state!==q&&t<clock){let [a,w,d]=table[3*state+(tape.get(h)??2)];if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
  ok(state===q&&t===clock&&h===p.head&&!tape.has(h),"sparse exact halt");
  let out="",i=h+1;while(tape.has(i))out+=tape.get(i++);
  ok(out===p.word,"physical plan");
  let cursor=p.selectorStart-1;
  for(let expected of [...p.graph.map(b=>b?"1":""),p.pins]){ok(!tape.has(cursor),"separator");cursor--;let got="";while(tape.has(cursor))got+=tape.get(cursor--);ok(got===expected,"preserved graph/pin");}
  ok(cursor===p.leftBoundary&&tape.size===p.selector.length+p.workBits+p.graph.reduce((a,b)=>a+b,0)+p.pins.length+out.length,"tape shape");
  rows.push({name,t,outputBits:out.length,status:ref.status});
 }
 return{q,descriptorBits:C.desc.length,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_two_plan.js'),require('./f038_tga_normalized_integration.js').engine())));
