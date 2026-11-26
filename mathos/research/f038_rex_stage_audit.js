// F038-REX-023A: exact quotient replay and per-description stage ledger.
function simulate(P,desc,raw,limit=Infinity){
 const {q,T}=P.decode(desc),origin=3*raw.length+512;
 let tape=new Uint8Array(origin+raw.length+512);tape.fill(2);
 for(let i=0;i<raw.length;i++)tape[origin+i]=+raw[i];
 let h=origin,s=0,t=0,lo=h,hi=h;
 while(s!==q&&t<limit){
  const v=T[3*s+tape[h]];tape[h]=(v>>2)&3;h+=(v&3)-1;s=v>>>4;t++;
  if(h<0)throw Error("left buffer");
  if(h>=tape.length){let g=new Uint8Array(tape.length*2);g.fill(2);g.set(tape);tape=g;}
  if(h<lo)lo=h;if(h>hi)hi=h;
 }
 if(s!==q)return{status:"TIMEOUT",t,head:h-origin,span:hi-lo+1};
 let bits=null;if(tape[h]!==2){let e=h;while(tape[e]!==2)e++;bits=Array.from(tape.subarray(h,e)).join("");}
 return{status:bits===null?"BLANK":"WITNESS",t,head:h-origin,span:hi-lo+1,bits};
}
function slot(ell,t,L){
 if(!Number.isSafeInteger(ell)||ell<0||!Number.isSafeInteger(t)||t<1||!Number.isSafeInteger(L)||L<2)throw Error("slot input");
 const log=x=>BigInt(x-1).toString(2).length-(x===1?1:0);
 const b=log(L),s=ell+log(t),k=Math.ceil(s/b);
 return{ell,t,L,logL:b,minStage:s,minK:k,stage3:3*b,admitted3:s<=3*b,firstKBudgetExponent:k*b-ell};
}
function audit(Q,P,V,H,A,E,suite="small"){
 const M=V.compile(P,H,A),C=Q.quotient(P,M.desc),ok=(v,s)=>{if(!v)throw Error(s)},rows=[];
 const force=(m,z)=>Array.from({length:9},(_,g)=>Array.from({length:m},(_,i)=>i===z[g]?null:[-(g*m+i+1)]).filter(Boolean)).flat();
 function check(name,m,pins,B,expected,oldClock=null){
  const raw=E.encode(m,pins,B),r=simulate(P,C.desc,raw,6000000000);
  ok(r.status===(expected===null?"BLANK":"WITNESS"),name+" status "+JSON.stringify(r));
  if(expected!==null)ok(r.bits===E.witness(m,pins,expected)&&E.valid(raw,r.bits),"witness "+name);
  if(oldClock!==null)ok(r.t===oldClock,"exact inherited clock");
  let original=slot(M.desc.length,r.t,raw.length),reduced=slot(C.desc.length,r.t,raw.length);
  const exhaustive={ell:3,tExponent:19*m-7,minStage:19*m-4,admitted3:19*m-4<=reduced.stage3};
  rows.push({name,m,L:raw.length,status:r.status,t:r.t,head:r.head,span:r.span,bits:r.bits,original,reduced,exhaustive});
  return{raw,r};
 }
 if(suite==="small"){
  check("forced",2,[1,0],force(2,Array(9).fill(1)),Array(9).fill(1),44654867);
  check("multirow",2,[0,1],force(2,[0,1,0,1,0,1,0,1,0]).filter(c=>c[0]!==-2&&c[0]!==-17),[0,1,0,1,0,1,0,1,0],46090469);
  let B=[[-2],[-17]];for(let g=0;g<8;g++)B.push([-(2*g+1),-(2*(g+1)+2)],[-(2*g+2),-(2*(g+1)+1)]);
  check("nonempty-inconsistent",2,[1,0],B,null,54399245);
  let outside=check("outside-path-SAT",2,[1,0],[[-1,-17]],null,7687297);ok(E.valid(outside.raw,E.witness(2,[1,0],Array(9).fill(1))),"outside model");
  let raw=E.encode(2,[1,0],force(2,Array(9).fill(1))),clock=44654867;
  ok(simulate(P,C.desc,raw,clock-1).status==="TIMEOUT"&&simulate(P,C.desc,raw,clock).status==="WITNESS","exact budget");
  ok(simulate(P,C.desc,"1000",1000).status==="BLANK","n1 refusal");
 }else if(suite==="three"){
  let z=[0,1,2,0,2,1,2,0,1];check("mixed-ranks",3,[1,0,1],force(3,z),z,522655657);
 }else if(suite==="four"){
  let z=[0,1,2,3,0,3,2,1,0];check("four-mixed-ranks",4,[1,0,1,1],force(4,z),z);
 }else throw Error("unknown suite");
 // Minimum raw descriptor length q=1: 20 bits. No generic description is
 // eligible in the original n=2 stage 0..6 fixture.
 ok(3+1+1+3*(1+4)===20,"minimum description");
 return{suite,stats:C.stats,rows,transitions:rows.reduce((a,r)=>a+r.t,0)};
}
module.exports={simulate,slot,audit};
if(require.main===module){const Q=require('./f038_rex_stage_quotient.js'),P=require('./f038_rex_ternary_bags.js'),V=require('./f038_rex_ternary_witness.js'),H=require('./f038_rex_ternary_handoff.js'),A=require('./f038_rex_nested_variable_overlap.js'),E=require('./f038_tga_normalized_integration.js').engine();if(process.argv.includes('--descriptor'))process.stdout.write(Q.quotient(P,V.compile(P,H,A).desc).desc);else console.log('F038_REX_STAGE_AUDIT_OK '+JSON.stringify(audit(Q,P,V,H,A,E,process.argv[2]||'small')));}
