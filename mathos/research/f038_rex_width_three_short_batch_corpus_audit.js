// D6X genuine corpus and checkpoint audit: execute emitted ternary rows,
// verify original packed mask checkpoint, bound relocation and erased tail.
function audit(P,Old,U,E,D,H,large=false){
 const ok=(b,m)=>{if(!b)throw Error(m);},C=P.compile(true),M=P.decode(C.desc),O=Old.compile(),OM={...Old.decode(O.desc),bridgeReady:O.bridgeReady};
 const ids=Object.fromEntries(C.names.map(([n,f],i)=>[n+"|"+f,i])),pre=ids["compactStart|0"],post=ids["loadBlock0|0"],ready=C.bridgeReady;
 ok([pre,post,ready].every(Number.isInteger),"checkpoints");
 function execute(raw,expected){
  const origin=3*raw.length+1024,a=new Uint8Array(6*raw.length+4096);a.fill(2);for(let i=0;i<raw.length;i++)a[origin+i]=+raw[i];
  let h=origin,q=0,t=0,lo=h,hi=h,checkpoint=null,relocated=false,result=null;
  function leftBlock(end){let j=end-1;while(a[j]<2)j--;return j;}
  function rightBlock(start){let j=start+1;while(a[j]<2)j++;return j;}
  function maskStart(B){let j=B;for(let i=0;i<130;i++)j=leftBlock(j);return j;}
  const str=(l,r)=>Array.from(a.subarray(l,r)).join("");
  while(q!==M.q&&t<30000000000){
   if(q===pre){ok(!checkpoint&&a[h]===2,"pre");
    const A=leftBlock(h),B=leftBlock(A),L=maskStart(B),end=rightBlock(h),bound=str(h+1,end);
    ok(str(B+1,A)===raw.slice(raw.indexOf("0")+1),"validated selector preserved before compaction");
    ok(bound.length>=4&&bound.length+6<A-B,"space for relocation");
    checkpoint={B,L,end,bound,mask:str(L,B+1),t,oldHead:h,rawCells:A-B-1};
   }
   if(q===post){const c=checkpoint;ok(c&&!relocated&&h===c.B+4&&str(c.B+1,h+1)==="0202","placeholder layout");
    ok(str(c.L,c.B+1)===c.mask&&str(h+1,h+1+c.bound.length)===c.bound,"source/bound exact");
    ok(a.subarray(h+1+c.bound.length,c.end+1).every(x=>x===2),"reclaimed region blank");relocated=true;c.relocation=t-c.t;
   }
   if(q===ready){const c=checkpoint;ok(relocated&&h===c.B+4&&str(c.L,c.B+1)===c.mask,"final mask checkpoint");
    const end=rightBlock(h),stream=str(h+1,end);ok(stream===expected,"exact canonical stream");
    result={stream,head:h-origin,oldHead:c.oldHead-origin,rawCells:c.rawCells,boundBits:c.bound.length,relocation:c.relocation,load:t-c.t-c.relocation};
   }
   let v=M.T[3*q+a[h]];a[h]=(v>>>2)&3;h+=(v&3)-1;q=v>>>4;t++;if(h<lo)lo=h;if(h>hi)hi=h;
  }
  ok(q===M.q,"budget");
  if(expected!==null)ok(result&&relocated,"missing stream");
  else ok(!checkpoint&&!result,"malformed reached compaction");
  return {status:result?"MASK_STREAM_LOADED":"REFUSAL",t,head:h-origin,span:hi-lo+1,headSymbol:a[h],...result};
 }
 const cases=[["empty",2,[]],["unary",2,[[-1],[-2]]],["cross",2,[[-1,-3]]],["one-sat",2,D.family(E,2,1,false)],["one-unsat",2,D.family(E,2,1,true)],["two-sat",2,D.family(E,2,2,false)],["two-unsat",2,D.family(E,2,2,true)]];
 for(const v of [1,85,170,254,255]){const B=[];for(let i=0;i<8;i++)if(v>>i&1)B.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);cases.push(["mask-"+v,2,B]);}
 if(large)cases.push(["hard3",3,H.family(E,3,false)],["hard4",4,H.family(E,4,false)]);
 let preserved=0,oldParity=0,refusals=0,oldSteps=0,newSteps=0,improved=0,regressed=0,tied=0;const rows=[];
 for(const [name,m,B] of cases){const raw=E.encode(m,Array.from({length:m},(_,i)=>i%2),B),a=execute(raw,U.stream(E,raw));preserved++;
  const b=Old.run(OM,raw,30000000000);ok(b.status===a.status&&b.stream===a.stream,"predecessor "+name);oldParity++;if(a.t<b.t)improved++;else if(a.t>b.t)regressed++;else tied++;oldSteps+=b.t;newSteps+=a.t;rows.push({name,m,old:b.t,new:a.t,relocation:a.relocation,load:a.load,head:a.head,rawCells:a.rawCells,boundBits:a.boundBits});
 }
 const raw=E.encode(2,[0,0],[]);for(const [name,s] of [["bad-header","0"+raw.slice(1)],["truncated",raw.slice(0,-1)],["extra",raw+"1"]]){
  const a=execute(s,null),b=Old.run(OM,s,30000000000);ok(b.status===a.status&&b.headSymbol===a.headSymbol,"refusal "+name);refusals++;
 }
 return {preserved,oldParity,refusals,oldSteps,newSteps,improved,regressed,tied,rows};
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_short_batch_producer.js"),require("./f038_rex_width_three_shared_deposit_producer.js"),require("./f038_rex_width_three_lazy_interval_ir.js"),require("./f038_tga_normalized_integration.js").engine(),require("./f038_rex_width_three_direct_extension_audit.js"),require("./f038_rex_width_three_two_prefix_hard.js"),process.argv.includes("--large"))));
