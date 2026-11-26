// F038-REX-022B5: independent sparse descriptor replay, without tape reset.
function replay(H,P,A,E,R){
 const M=H.compile(P,A),raw=E.encode(2,[1,0],Array.from({length:9},(_,g)=>[-(2*g+1)])),ref=R.producer(raw),ok=(a,s)=>{if(!a)throw Error(s)};
 // Separate parser and dictionary-tape interpreter; no producer or worker run calls.
 let j=3;while(M.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=[];for(let i=0;i<3*q;i++){let a=parseInt(M.desc.slice(j,j+b),2),w=parseInt(M.desc.slice(j+b,j+b+2),2),d=parseInt(M.desc.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&d>=-1&&d<=1,"descriptor field");table.push([a,w,d]);}
 ok(j===M.desc.length,"descriptor length");
 let tape=new Map([...raw].map((x,i)=>[i,+x])),h=0,state=0,t=0,protectedBefore=null,bridgeAt=null,workerAt=null,origin=null,producerHead=null;
 const sorted=(x)=>[...x].sort((a,b)=>a[0]-b[0]);
 while(state!==q&&t<50000000){
  if(state===M.bridgeEntry&&bridgeAt===null){
   bridgeAt=t;producerHead=h;protectedBefore=sorted([...tape].filter(([i])=>i<h));
   ok(Array.from({length:ref.prepared.length},(_,i)=>tape.get(h+1+i)).join("")===ref.prepared,"producer word");
  }
  if(state===M.workerEntry&&workerAt===null){
   workerAt=t;origin=h;
   let right=sorted([...tape].filter(([i])=>i>=producerHead));
   ok(right.length===ref.prepared.length&&right.every(([p,x],i)=>p===h+i&&x===+ref.prepared[i]),"isolated word");
  }
  let [a,w,d]=table[3*state+(tape.get(h)??2)];if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;
 }
 ok(state===q&&t===44149177&&bridgeAt===41229674&&workerAt===42557335,"exact phases");
 ok(JSON.stringify(sorted([...tape].filter(([i])=>i<producerHead)))===JSON.stringify(protectedBefore),"preserved prefix");
 const certificate=sorted([...tape].filter(([i])=>i>=producerHead));ok(certificate.length===7&&certificate.every(([i,a],k)=>i===h+k&&a===1),"sparse certificate");
 ok(E.valid(raw,E.witness(2,[1,0],Array(9).fill(1))),"original host witness");
 return{states:q,descriptorBits:M.desc.length,transitions:t,producer:bridgeAt,handoff:workerAt-bridgeAt,worker:t-workerAt,workerOrigin:origin,certificate:"1111111",protectedCells:protectedBefore.length};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_TERNARY_HANDOFF_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_ternary_handoff.js'),require('./f038_rex_ternary_bags.js'),require('./f038_rex_nested_variable_overlap.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_multitape_producer.js'))));
