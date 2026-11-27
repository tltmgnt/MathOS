// D5Y compiled worker replay with two converted sparse fields; harness supplies canonical segmented stream.
const p='./f038_rex_width_three_',U=require(p+'inplace_hybrid_integration_ir.js'),W=require(p+'inplace_hybrid_gac_ir.js'),Gap=require(p+'persistent_gap_encoder.js'),K=require(p+'exit_compiler.js'),F=require(p+'fast_clock.js'),Old=require(p+'cost_ir.js'),E=require('./f038_tga_normalized_integration.js').engine();
const J=U.machine(W,Gap,false),M=K.compile(J),raw=E.encode(5,[0,1,0,1,0],[[-5,-10,-15],[-10,-15,-20]]),I=[...Array(21).fill(""),Old.stream(E,raw)],a=F.count(J,I),s=["G",...I.flatMap((v,k)=>["hL",...[...v].map(x=>"u"+x),"u_",k===21?"E":"D"])].map(x=>M.codes[x]).join("");
const T=new Uint8Array(Math.max(s.length,a.encoded.length)+512);T.fill(2);T.set([...s].map(Number),100);let h=100,pc=0,t=0;
while(pc<M.q&&t<=a.clock){const v=M.T[3*pc+T[h]];T[h]=v>>2&3;h+=(v&3)-1;pc=v>>>4;t++;}
if(pc!==M.q+1||t!==a.clock||t!==665898052||h!==100||a.N!==2329||a.steps!==46251||Array.from(T.slice(100,100+a.encoded.length)).join("")!==a.encoded||T.slice(100+a.encoded.length).some(x=>x!==2)||!E.valid(raw,a.tapes[0])||a.tapes[21].length!==496)throw Error("physical");
console.log("D5Y_GAMMA_MODE_PHYSICAL_OK",JSON.stringify({t,N:a.N,steps:a.steps,persistent:a.tapes[21].length,witness:a.tapes[0]}));
