// D6O exact segmented clock: charge each right rewrite by leftmost differing digit.
function count(J,inputs,codes,limit=100000000){
 const T=inputs.map(s=>["L",...s,"_"]),h=T.map(()=>0),ok=(x,s)=>{if(!x)throw Error(s)};
 const w=Math.ceil(Math.log2(3+2*J.alphabet.length)),stay=2*w-2,left=3*w-2;
 if(!codes||codes.G.length!==w)throw Error("codebook");
 function right(a,b){const x=codes[a],y=codes[b];let i=0;while(i<w&&x[i]===y[i])i++;return i===w?w:w+2*(w-1-i);}
 let N=1+T.reduce((n,t)=>n+t.length+1,0),N0=N,pc=J.entry,steps=0,clock=0,growth=0,equalCarries=0,changedCarries=0,reads=0,writes=0,movesL=0,movesR=0,peakStep=0,status=null;
 // The encoded layout's logical symbol at a given position, used only
 // to charge suffix-shift carry moves. No host-dependent machine action.
 // Charge suffix carries from actual marked/unmarked logical symbols.
 function suffix(k){let c=k===T.length-1?"E":"D",same=0,different=0,clock=0;
  for(let i=k+1;i<T.length;i++){for(let j=0;j<T[i].length;j++){const a=(h[i]===j?"h":"u")+T[i][j];clock+=right(a,c);if(a===c)same++;else different++;c=a;}
   const a=i===T.length-1?"E":"D";clock+=right(a,c);if(a===c)same++;else different++;c=a;}
  return {same,different,clock};}
 while(true){
  const I=J.ins[pc];if(I.op==="jump"){pc=I.next;continue;}
  if(I.op==="halt"||I.op==="reject"){
   status=I.op;clock+=stay+(I.op==="reject"?1:0);break;
  }
  if(steps===limit)throw Error("IR budget");
  let k=I.t,x=T[k][h[k]],p=1+h[k];for(let j=0;j<k;j++)p+=T[j].length+1;
  const old=N;let cost=p*w+2*stay+p*left;
  if(I.op==="read"){pc=I.next[J.alphabet.indexOf(x)];reads++;}
  else if(I.op==="write"){ok(x!=="L"&&I.next.v!=="L","sentinel");let t=T[k],j=h[k],v=I.next.v;t[j]=v;pc=I.next.d;writes++;}
  else if(I.op==="move"){
   const d=I.next.dir;
   if(d===-1){ok(h[k]>0,"left boundary");h[k]--;movesL++;}
   else if(d===1){
    movesR++;
    if(h[k]+1<T[k].length){cost+=right("h"+x,"u"+x)+left;h[k]++;}
    else{
     const a=suffix(k);ok(a.same+a.different===N-p-2,"suffix size");
     let carry=a.clock;equalCarries+=a.same;changedCarries+=a.different;
     // Scan from G to marked cell; unmark, insert, carry to fresh E;
     // then move left from the old E through the entire region.
     cost=p*w+2*stay+N*left+right("h"+x,"u"+x)+right(k===T.length-1?"E":"D","h_")+carry;
     T[k].push("_");h[k]++;N++;growth++;
    }
   }else throw Error("move");
   pc=I.next.d;
  }else throw Error("instruction");
  steps++;clock+=cost;peakStep=Math.max(peakStep,cost);
  ok(cost<=2*left*old+2*stay,"per-primitive bound");
 }
 const upper=(2*left*N+2*stay)*steps+stay+(status==='reject'?1:0);
 ok(Number.isSafeInteger(clock)&&Number.isSafeInteger(upper)&&clock<=upper&&N===N0+growth,"total bound");
 const encoded=[status==="reject"?"~":"G",...T.flatMap((t,k)=>[...t.map((x,j)=>(h[k]===j?"h":"u")+x),k===T.length-1?"E":"D"])].map(x=>codes[x]).join("");
 ok(encoded.length===w*N,"terminal encoding");
 return{status,lengths:T.map(t=>t.length),encoded,clock,upper,steps,N0,N,growth,equalCarries,changedCarries,reads,writes,movesL,movesR,peakStep,tapes:T.map(t=>t.slice(1).join("").replace(/_+$/,"")),heads:h};
}
module.exports={count};
