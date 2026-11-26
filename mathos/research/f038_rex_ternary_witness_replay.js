// Independent original-format sparse tape replay and integer witness verifier.
function replay(V,P,H,A,E,mode="sat"){
 const M=V.compile(P,H,A),n=31,m=2,pins=[1,0],ok=(v,s)=>{if(!v)throw Error(s)};
 let B=Array.from({length:9},(_,g)=>[-(2*g+1)]);
 if(mode==="unsat"){B=[[-2],[-17]];for(let g=0;g<8;g++)B.push([-(2*g+1),-(2*(g+1)+2)],[-(2*g+2),-(2*(g+1)+1)]);}
 const raw=E.encode(m,pins,B),C=[...E.pool(n)],p=raw.slice(n+1).split("").reduceRight((v,b)=>(v<<1n)|BigInt(b),0n);
 // Independent descriptor decoding and original integer witness interface.
 let j=3;while(M.desc[j]==="1")j++;let q=j-3,b=q.toString(2).length;j++;
 const table=[];for(let i=0;i<3*q;i++){let a=parseInt(M.desc.slice(j,j+b),2),w=parseInt(M.desc.slice(j+b,j+b+2),2),d=parseInt(M.desc.slice(j+b+2,j+b+4),2)-1;j+=b+4;ok(a<=q&&w<=2&&d>=-1&&d<=1,"descriptor field");table.push([a,w,d]);}
 ok(j===M.desc.length,"descriptor length");
 let tape=new Map([...raw].map((v,i)=>[i,+v])),h=0,state=0,t=0;
 const clock=mode==="sat"?44654867:54399245;let oneBefore=false;
 for(;state!==q&&t<clock;t++){
  if(t===clock-1)oneBefore=state!==q;
  let [a,w,d]=table[3*state+(tape.get(h)??2)];if(w===2)tape.delete(h);else tape.set(h,w);h+=d;state=a;
 }
 ok(state===q&&t===clock&&oneBefore,"exact sparse clock");
 const bits=Array.from({length:n},(_,i)=>tape.get(h+i)??2);
 const x=bits.every(v=>v<2)?bits.reduceRight((v,b)=>(v<<1n)|BigInt(b),0n):null;
 const valid=x!==null&&x>=0n&&x<1n<<BigInt(n)&&C.every((c,j)=>!(p>>BigInt(j)&1n)||c.some(l=>Boolean(x>>BigInt(Math.abs(l)-1)&1n)===(l>0)));
 if(mode==="sat")ok(valid&&bits.join("")===E.witness(m,pins,Array(9).fill(1))&&!tape.has(h-1)&&!tape.has(h+n),"original integer witness");
 else ok(x===null&&!valid,"blank refusal");
 return{mode,q,descriptorBits:M.desc.length,transitions:t,head:h,witness:x===null?null:bits.join(""),integer:x===null?null:x.toString(),valid,oneStepShort:oneBefore};
}
module.exports={replay};
if(require.main===module)console.log('F038_REX_TERNARY_WITNESS_REPLAY_OK '+JSON.stringify(replay(require('./f038_rex_ternary_witness.js'),require('./f038_rex_ternary_bags.js'),require('./f038_rex_ternary_handoff.js'),require('./f038_rex_nested_variable_overlap.js'),require('./f038_tga_normalized_integration.js').engine(),process.argv[2]||'sat')));
