// D5S host reference only: ordered forbidden-position gaps, gamma coding,
// literal fallback. Field boundary and original mask length n are external.
// Not an implementation of a physical producer or a physical decoder.
function encode(mask){
 if(!/^[01]*$/.test(mask))throw Error("mask");
 let prior=-1,s="";for(let i=0;i<mask.length;i++)if(mask[i]==="1"){const b=(i-prior).toString(2);s+="0".repeat(b.length-1)+b;prior=i;}
 return s.length<=mask.length?"1"+s:"0"+mask;
}
function decode(code,n){
 if(!Number.isSafeInteger(n)||n<0||!/^[01]+$/.test(code))throw Error("shape");
 if(code[0]==="0"){if(code.length!==n+1)throw Error("length");return code.slice(1);}
 const out=Array(n).fill("0");let i=1,prior=-1;
 while(i<code.length){let z=0;while(code[i]==="0"){z++;i++;}
  if(i+z>=code.length||z>52)throw Error("truncated gap");
  const gap=parseInt(code.slice(i,i+z+1),2);i+=z+1;prior+=gap;
  if(!Number.isSafeInteger(prior)||prior>=n)throw Error("position");out[prior]="1";
 }
 return out.join("");
}
function audit(){
 let patterns=0,sparse=0,dense=0,strict=0,malformed=0,seed=0xD5A5,rows=[];
 function test(mask){const c=encode(mask);if(decode(c,mask.length)!==mask||c.length>mask.length+1)throw Error("codec");patterns++;if(c[0]==="1")sparse++;else dense++;if(c.length<mask.length+1)strict++;return c.length;}
 for(let n=0;n<=12;n++)for(let v=0;v<2**n;v++)test(n?v.toString(2).padStart(n,"0"):"");
 for(let n of [16,64,256,1024])for(let d of [0,1,5,25,50,100]){
  let mask="";for(let i=0;i<n;i++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;mask+=(seed%100<d?"1":"0");}const length=test(mask);rows.push({n,d,forbidden:mask.split("1").length-1,encoded:length});
 }
 for(let [c,n] of [["",4],["0",4],["100",4],["1001",4],["111111",4],["1011",1],["2",4]]){let bad=false;try{decode(c,n);}catch{bad=true;}if(!bad)throw Error("malformed");malformed++;}
 return {patterns,sparse,dense,strict,malformed,rows};
}
module.exports={encode,decode,audit};
if(require.main===module)console.log(JSON.stringify(audit()));
