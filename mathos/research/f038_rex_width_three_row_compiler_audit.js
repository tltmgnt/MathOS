// Exact rooted transition homomorphism check against previous symbol-movement lowering on projection kernel.
function compare(P,A,B){
 const J=P.compact(P.machine()),X=A.compile(J),Y=B.compile(J),ok=(v,s)=>{if(!v)throw Error(s)},map=new Int32Array(X.q+1).fill(-1),seen=new Uint8Array(Y.q+1),queue=new Uint32Array(X.q+1);let count=1,checks=0,covered=1;map[0]=0;seen[0]=1;queue[0]=0;
 for(let i=0;i<count;i++){
  const a=queue[i],b=map[a];ok((a===X.q)===(b===Y.q),"halt");
  if(a===X.q)continue;
  for(let s=0;s<3;s++){
   let x=X.T[3*a+s],y=Y.T[3*b+s];ok((x&15)===(y&15),"physical action");let p=x>>>4,q=y>>>4;
   if(map[p]===-1){map[p]=q;queue[count++]=p;}else ok(map[p]===q,"successor mapping");
   if(!seen[q]){seen[q]=1;covered++;}checks++;
  }
 }
 ok(count===X.q+1&&covered===Y.q+1,"coverage");
 return{original:X.q,interned:Y.q,checks,covered,logical:Y.logicalRoots};
}
module.exports={compare};
if(require.main===module)console.log('F038_REX_WIDTH_THREE_ROW_COMPILER_OK '+JSON.stringify(compare(require('./f038_rex_width_three_projection.js'),require('./f038_rex_width_three_local_compiler.js'),require('./f038_rex_width_three_row_compiler.js'))));
