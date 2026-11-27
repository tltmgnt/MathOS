// D5V independent Cartesian support oracle and actual ternary replays.
function audit(S,U,G,W,R,K,F){
 const J=S.machine(),C=U.machine(S,G),JM=K.compile(J),CM=K.compile(C),ok=(x,s)=>{if(!x)throw Error(s)};let direct=0,composed=0,physical=0,malformed=0,sparse=0,dense=0;const rows=[];
 function oracle(mask,dom){const out=dom.map(s=>Array(s.length).fill("0"));let p=0;for(let a=0;a<dom[0].length;a++)for(let b=0;b<dom[1].length;b++)for(let c=0;c<dom[2].length;c++){if(mask[p++]==="0"&&dom[0][a]==="1"&&dom[1][b]==="1"&&dom[2][c]==="1")[a,b,c].forEach((x,i)=>out[i][x]="1");}return out.map(s=>s.join(""));}
 function actual(j,m,I){const a=F.count(j,I),raw=["G",...I.flatMap((v,k)=>["hL",...[...v].map(x=>"u"+x),"u_",k===I.length-1?"E":"D"])].map(x=>m.codes[x]).join("");let T=new Uint8Array(Math.max(raw.length,a.encoded.length)+512);T.fill(2);T.set([...raw].map(Number),100);let h=100,pc=0,t=0;while(pc<m.q&&t<=a.clock){const v=m.T[3*pc+T[h]];T[h]=v>>2&3;h+=(v&3)-1;pc=v>>>4;t++;}
  ok(pc===m.q+1&&h===100&&t===a.clock&&Array.from(T.slice(100,100+a.encoded.length)).join("")===a.encoded&&T.slice(100+a.encoded.length).every(x=>x===2),"physical");physical++;return {clock:t,steps:a.steps,N:a.N};}
 function test(mask,dom,compose=false,phys=false){const code=R.encode(mask),I=["",...dom,"","","","",code],want=oracle(mask,dom),a=W.executeIR(J,I);
  ok(a.status==="halt"&&a.tapes.slice(4,7).join()===want.join()&&a.tapes.slice(1,4).join()===dom.join()&&a.tapes[8]===code&&a.tapes[7]==="","direct");direct++;if(code[0]==="1")sparse++;else dense++;
  if(compose){const II=["",...dom,"","","","","",mask],b=W.executeIR(C,II);ok(b.status==="halt"&&b.tapes.slice(0,9).join("|")===a.tapes.join("|")&&b.tapes[9]==="","composition");composed++;if(phys)rows.push({n:mask.length,forbidden:mask.split("1").length-1,mode:code[0],bits:code.length,direct:actual(J,JM,I),composed:actual(C,CM,II)});}
 }
 for(let v=0;v<256;v++)for(let d=0;d<64;d++)test(v.toString(2).padStart(8,"0"),[0,1,2].map(i=>((d>>(2*i))&3).toString(2).padStart(2,"0")),d===0||d===63);
 for(let v=0;v<16;v++)for(let d=0;d<16;d++)test(v.toString(2).padStart(4,"0"),[0,1].map(i=>((d>>(2*i))&3).toString(2).padStart(2,"0")).concat("1"),d===15);
 let seed=0xD5A6;function rand(n){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;}
 for(let m of [3,4,5])for(let i=0;i<30;i++){const mask=Array.from({length:m**3},()=>rand(100)<[0,1,5,25,50,100][i%6]?"1":"0").join(""),dom=Array.from({length:3},()=>Array.from({length:m},()=>String(rand(2))).join(""));test(mask,dom,true);}
 for(const mask of ["0".repeat(8),"00000001","01010101","11111111","0".repeat(63)+"1","01".repeat(32)]){const m=mask.length===8?2:4;test(mask,Array(3).fill("1".repeat(m)),true,true);}
 for(const code of ["","00","0"+"0".repeat(9),"100","10001","10001001","1111111111","10100000"]){const a=W.executeIR(J,["","11","11","11","","","","",code]);ok(a.status==="reject","malformed "+code);malformed++;}
 return {direct,composed,physical,malformed,sparse,dense,instructions:[J.ins.length,C.ins.length],states:[JM.q,CM.q],rows};
}
module.exports={audit};
if(require.main===module){const p='./f038_rex_width_three_';console.log(JSON.stringify(audit(require(p+'persistent_support_ir.js'),require(p+'persistent_support_compose.js'),require(p+'persistent_gap_encoder.js'),require(p+'cost_ir.js'),require(p+'gap_reference.js'),require(p+'exit_compiler.js'),require(p+'fast_clock.js'))));}
