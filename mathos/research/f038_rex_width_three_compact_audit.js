// REX-024D2B: exact physical quotient and two-stage quotient cross-check.
function audit(H,P,K,Q,C,E,U){
 const J=P.compact(H.machine());let stats=null;
 const A={...K,compile(j){const M=K.compile(j),R=Q.refine(M);stats=R.stats;return{...M,q:R.q,T:R.T};}};
 const a=U.audit(H,P,A,C,E,"physical");
 const ok=(v,s)=>{if(!v)throw Error(s)};
 ok(a.rows.map(r=>r.t).join()==="1010897771,672898103,2407717"&&a.rows.map(r=>r.span).join()==="10415,10190,2710","exact parent physical clocks and spans");
 return{...a,quotient:stats};
}
function compare(H,P,K,L,Q){
 const J=P.compact(H.machine());
 function compress(compiler){const M=compiler.compile(J),R=Q.refine(M);return{q:R.q,T:R.T,stats:R.stats,logical:M.logicalQuotient??null};}
 const A=compress(K),B=compress(L),ok=(v,s)=>{if(!v)throw Error(s)};
 ok(A.q===B.q,"quotient size");
 // Compare the two rooted deterministic machines via a bijection.
 const map=new Int32Array(A.q+1).fill(-1),rev=new Int32Array(B.q+1).fill(-1),queue=new Uint32Array(A.q+1);let count=1,checks=0;map[0]=rev[0]=0;queue[0]=0;
 for(let i=0;i<count;i++){let a=queue[i],b=map[a];ok((a===A.q)===(b===B.q),"halt class");
  if(a===A.q)continue;
  for(let s=0;s<3;s++){let x=A.T[3*a+s],y=B.T[3*b+s];ok((x&15)===(y&15),"write/move");let p=x>>>4,q=y>>>4;
   if(map[p]===-1){ok(rev[q]===-1,"injective");map[p]=q;rev[q]=p;queue[count++]=p;}else ok(map[p]===q&&rev[q]===p,"successor");checks++;
  }
 }
 ok(count===A.q+1&&map[A.q]===B.q,"full rooted isomorphism");
 return{direct:A.stats,staged:B.stats,logical:B.logical,isomorphismStates:count,checks};
}
function smoke(H,P,K,Q){
 const J=P.compact(H.machine()),M=K.compile(J),R=Q.refine(M),C={...M,q:R.q,T:R.T};
 const frame=(v,i)=>"0".repeat(54)+v.toString(2).padStart(4,"0")+(i===0?"11":"00")+(v===9?"0".repeat(24):"1001".repeat(4)+"10000000")+"b";
 const input="H"+Array.from({length:10},(_,i)=>frame(i,i)).join(""),raw=K.encode(C,J,[input,...Array(8).fill("")]),r=K.run(C,raw,672898103);
 const routes=Array.from({length:9},(_,i)=>i.toString(2).padStart(4,"0")+"10010:;").join("");
 if(r.status!=="COMPLETE"||r.t!==672898103||r.span!==10190||r.tapes[6]!==routes||r.tapes[7].length!==504)throw Error("exact empty replay");
 return{stats:R.stats,t:r.t,span:r.span,route:r.tapes[6],scopeBits:r.tapes[7].length};
}
module.exports={audit,compare,smoke};
if(require.main===module){const H=require('./f038_rex_width_three_headers.js'),P=require('./f038_rex_width_three_projection.js'),K=require('./f038_rex_width_three_compiler.js'),Q=require('./f038_rex_width_two_quotient.js');const r=process.argv[2]==='smoke'?smoke(H,P,K,Q):process.argv[2]==='compare'?compare(H,P,K,require('./f038_rex_width_three_compact_compiler.js'),Q):audit(H,P,K,Q,require('./f038_rex_width_three_factors.js'),require('./f038_tga_normalized_integration.js').engine(),require('./f038_rex_width_three_headers_audit.js'));console.log('F038_REX_WIDTH_THREE_COMPACT_OK '+JSON.stringify(r));}
