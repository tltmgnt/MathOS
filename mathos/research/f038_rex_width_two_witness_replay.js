// Independent sparse interpreter and original integer clause verifier.
function replay(P,E){
 const C=P.compile(),ok=(v,s)=>{if(!v)throw Error(s)};
 let j=3;while(C.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const T=new Uint32Array(3*q);
 for(let i=0;i<T.length;i++){let a=parseInt(C.desc.slice(j,j+b),2),w=parseInt(C.desc.slice(j+b,j+b+2),2),d=parseInt(C.desc.slice(j+b+2,j+b+4),2);j+=b+4;ok(a<=q&&w<=2&&d<=2,"descriptor field");T[i]=(a<<4)|(w<<2)|d;}
 ok(j===C.desc.length,"descriptor length");
 const pair=[...E.tup(2,3)].filter(z=>z[1]!==z[2]).map(z=>[0,4,8].map((v,i)=>-(2*v+z[i]+1)));pair.push([-9,-17],[-10,-18]);
 const rows=[];
 for(let [name,B,clock,sat,head] of [["sat",[[-1,-9,-17]],34911962,true,38652],["joint-unsat",pair,34465372,false,37913]]){
  let raw=E.encode(2,[1,0],B),tape=new Map([...raw].map((x,i)=>[i,+x])),h=0,state=0,t=0;
  while(state!==q&&t<clock){let v=T[3*state+(tape.get(h)??2)],a=v>>>4,w=(v>>2)&3,d=(v&3)-1;if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;t++;}
  ok(state===q&&t===clock&&h===head,"exact clock and head");
  const n=31,bits=Array.from({length:n},(_,i)=>tape.get(h+i)??2),x=bits.every(v=>v<2)?bits.reduceRight((v,b)=>(v<<1n)|BigInt(b),0n):null;
  let C=[...E.pool(n)],selector=raw.slice(n+1),valid=x!==null&&x<(1n<<BigInt(n))&&C.every((c,j)=>selector[j]==="0"||c.some(l=>Boolean(x>>BigInt(Math.abs(l)-1)&1n)===(l>0)));
  if(sat)ok(valid&&bits.join("")==="0110101010101010101111111111000"&&!tape.has(h-1)&&!tape.has(h+n),"exact original witness");
  else ok(x===null&&!valid&&!tape.has(h),"blank refusal");
  rows.push({name,t,head,integer:x===null?null:x.toString(),valid,bits:sat?bits.join(""):null});
 }
 return{q,descriptorBits:C.desc.length,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_WIDTH_TWO_WITNESS_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_width_two_witness.js'),require('./f038_tga_normalized_integration.js').engine())));
