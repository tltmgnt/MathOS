// Audit actual compiled two-cell carry transitions, not a host-side codec surrogate.
function carryAudit(P){
 const c=P.compile(true),M=P.decode(c.desc),ids=new Map(c.names.map(([n,f],i)=>[n+"|"+f,i])),entries=new Map();
 for(let i=0;i<c.names.length;i++){const [name,flag]=c.names[i];if(flag!==0||!name.endsWith("DoubleFirst"))continue;const next=c.names[M.T[3*i]>>>4]?.[0]||"",j=next.match(/Double(\d+)_20$/);const k=j?+j[1]:0;entries.set(k,{entry:i,end:ids.get(name.replace("DoubleFirst","Return0")+"|0")});}
 if(entries.size!==120)throw Error("entry count "+entries.size);
 let cases=0,maxSteps=0;
 function check(suffix,J){
  const {entry,end}=entries.get(J),T=new Uint8Array(suffix.length+8);T.fill(2);T[0]=1;T.set(suffix,1);let h=1,s=entry,t=0;
  while(s!==end){if(s===M.q||t>suffix.length+8||h<0||h>=T.length)throw Error("macro");const v=M.T[3*s+T[h]];T[h]=v>>2&3;h-=((v&3)-1);s=v>>>4;t++;}
  const want=[1,1,2,...suffix],actual=Array.from(T.slice(0,want.length));
  if(actual.join()!==want.join()||h!==want.length-2||T.slice(want.length).some(x=>x!==2))throw Error("carry "+JSON.stringify({J,suffix,actual,want,h,t}));
  maxSteps=Math.max(maxSteps,t);cases++;
 }
 check([],0);
 for(let n=0;n<=8;n++)for(let v=0;v<3**n;v++){let a=[],k=v;for(let i=0;i<n;i++){a.push(k%3);k=Math.floor(k/3);}a.push(2);check(a,a.filter(x=>x===2).length);}
 for(let J=1;J<=119;J++){check(Array(J).fill(2),J);check(Array.from({length:2*J},(_,i)=>i%2?2:i%4===0?0:1),J);}
 return {entries:entries.size,cases,maxSteps};
}
module.exports={carryAudit};
if(require.main===module)console.log(JSON.stringify(carryAudit(require('./f038_rex_width_three_joint_producer.js'))));
