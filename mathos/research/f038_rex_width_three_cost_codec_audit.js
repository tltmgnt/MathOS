// D5O independent local lookahead accounting and exhaustive m2 ternary-mask regression.
function codecAudit(U,E,Old){
 const J=U.machine(false),O=Old.machine(false);let patterns=0,runPatterns=0,maskCases=0,accepted=0,refused=0,maxProbe=0;
 // Independent finite lookahead accounting, excluding inherited copy shuttles.
 // A failed probe of k cells moves k left and k right (one is the original
 // Read transition); a successful four-zero probe needs three extra moves.
 for(let n=1;n<=12;n++)for(let v=0;v<2**n;v++){
  const word=v.toString(2).padStart(n,"0");let code="",extra=0,groups=0;
  for(let i=0;i<n;){if(word[i]==="1"){code+="01";i++;continue;}
   let k=1;while(k<4&&i+k<n&&word[i+k]==="0")k++;
   if(k===4){code+="11";extra+=3;groups++;i+=4;}else{code+="00";extra+=2*k;i++;}
  }
  let out="";for(let i=0;i<code.length;i+=2)out+=code.slice(i,i+2)==="11"?"0000":code[i+1];
  if(out!==word||code.length!==2*n-6*groups||extra>6*n)throw Error("probe macro");
  patterns++;if(groups)runPatterns++;maxProbe=Math.max(maxProbe,extra);
 }
 // All 256 truth masks on the same ternary scope, with and without unary
 // restrictions, compare the compiled IR's observable behavior to D5M.
 for(let mask=0;mask<256;mask++)for(const forced of [false,true]){
  const c=[];for(let i=0;i<8;i++)if(mask>>i&1)c.push([-(1+(i>>2)),-(3+((i>>1)&1)),-(5+(i&1))]);
  if(forced)c.push([-2],[-4],[-6]);
  const raw=E.encode(2,[0,0],c),s=U.stream(E,raw),a=U.executeIR(J,[...Array(19).fill(""),s]),b=Old.executeIR(O,[...Array(19).fill(""),Old.stream(E,raw)]);
  if(a.status!==b.status||a.tapes[0]!==b.tapes[0]||a.tapes[19]!==s||a.status==="halt"&&!E.valid(raw,a.tapes[0]))throw Error("mask "+mask);
  maskCases++;if(a.status==="halt")accepted++;else refused++;
 }
 return {patterns,runPatterns,maskCases,accepted,refused,maxProbe};
}
module.exports={codecAudit};
if(require.main===module){const U=require('./f038_rex_width_three_cost_ir.js'),E=require('./f038_tga_normalized_integration.js').engine(),Old=require('./f038_rex_width_three_compressed_ir.js');console.log(JSON.stringify(codecAudit(U,E,Old)));}
