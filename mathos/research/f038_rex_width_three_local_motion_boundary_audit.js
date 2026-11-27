// D6T finite transition-table certificate for every emitted local motion marking root.
// Check physical table, not logical transition functions. Growth uses representative
// D/E suffixes; arbitrary-length growth still relies on the FIFO invariant.
function audit(K,U){
 const ok=(x,m)=>{if(!x)throw Error(m);},out=[];
 for(const full of [false,true]){
  const J=U.machine(full),M=K.compile(J),names=M.rootNames,ids=new Map(names.map((n,i)=>[n,i])),w=M.w,C=M.codes;
  let roots=0,leftRoots=0,rightRoots=0,interiorChecks=0,growthChecks=0,steps=0;
  function check(start,end,input,expected,head,expectedHead,clock){
   const a=new Uint8Array(128);a.fill(2);for(let i=0;i<input.length;i++)a[16+i]=+input[i];let q=start,h=16+head,t=0;
   while(q!==end&&q<M.q&&t<128){const v=M.T[3*q+a[h]];a[h]=(v>>>2)&3;h+=(v&3)-1;q=v>>>4;t++;ok(h>=0&&h<a.length,"head");}
   ok(q===end&&h===16+expectedHead&&t===clock,"boundary "+names[start]+" "+JSON.stringify({q,h,t,expectedHead,clock}));
   for(let i=0;i<a.length;i++)ok(a[i]===(i>=16&&i<16+expected.length?+expected[i-16]:2),"changed guard or code");steps+=t;
  }
  for(let i=0;i<names.length;i++){
   const m=/^mark([LR])(i[0-9]+act)$/.exec(names[i]);if(!m)continue;
   const dir=m[1],end=ids.get(m[2]);ok(end!==undefined,"local successor");roots++;if(dir==="L")leftRoots++;else rightRoots++;
   for(const x of J.alphabet){const prefix=C.G+C.u0,suffix=C.E,input=prefix+C["u"+x]+suffix,expected=prefix+C["h"+x]+suffix;
    check(i,end,input,expected,prefix.length+(dir==="L"?w-1:0),prefix.length,dir==="L"?w-1:2*w-2);interiorChecks++;
   }
   if(dir==="R"){
    const ret=ids.get("ret"+m[2].slice(1,-3));ok(ret!==undefined,"growth fallback root");
    for(const d of ["D","E"]){const prefix=C.G+C.uL+C.u0,suffix=d==="D"?C.uL+C.h_+C.E:"",input=prefix+C[d]+suffix,expected=prefix+C.h_+C[d]+suffix;
     let j=0;while(C[d][j]===C.h_[j])j++;const rewrite=w+2*(w-1-j);
     check(i,ret,input,expected,prefix.length,expected.length-w-1,rewrite+suffix.length+2*w-1);growthChecks++;
    }
   }
  }
  ok(roots>0&&leftRoots>0&&rightRoots>0,"coverage");
  out.push({full,roots,leftRoots,rightRoots,interiorChecks,growthChecks,steps});
 }
 return out;
}
module.exports={audit};
if(require.main===module)console.log(JSON.stringify(audit(require("./f038_rex_width_three_local_motion_compiler.js"),require("./f038_rex_width_three_lazy_interval_ir.js"))));
