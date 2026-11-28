// FV-06: independent physical packed-table/quotient replay, not IR compilation proof.
const W=require('./f038_rex_variable_rank_worker.js');
const C=require('./f038_rex_width_three_local_motion_compiler.js');
const Clock=require('./f038_rex_width_three_local_motion_clock.js');
const Q=require('./f038_rex_width_two_quotient.js');
const ok=(x,s)=>{if(!x)throw Error("FV06: "+s);};
function checkQuotient(a,b,map){
 ok(a.singleExit&&b.singleExit&&a.T.length===3*a.q&&b.T.length===3*b.q,"shape");
 ok(map.length===a.q+1&&map[0]===0&&map[a.q]===b.q,"initial/halt");
 let mapped=0,checks=0;
 for(let s=0;s<=a.q;s++){
  const t=map[s];ok(Number.isInteger(t)&&t>=-1&&t<=b.q,"map");
  if(t===-1)continue;
  mapped++;ok((s===a.q)===(t===b.q),"terminal distinction");
  if(s===a.q)continue;
  for(let x=0;x<3;x++){
   const u=a.T[3*s+x],v=b.T[3*t+x],next=Math.floor(u/16),qn=Math.floor(v/16);
   ok(next<=a.q&&qn<=b.q&&map[next]===qn,"successor");
   ok(u%16===v%16&&Math.floor((u%16)/4)<3&&u%4<3,"write/move");
   checks++;
  }
 }
 return {mapped,checks};
}
// Independently implement an unbounded blank-default tape, with a sparse map
// of nonblank symbols. No W.run buffer or quotient construction code reused.
function sparseRun(M,s,limit){
 const initial=["G","hL","u_","D","hL",...[...s].map(x=>"u"+x),"u_","E"].map(x=>M.codes[x]).join("");
 const tape=new Map();for(let i=0;i<initial.length;i++)if(initial[i]!=="2")tape.set(i,Number(initial[i]));
 const read=i=>tape.get(i)??2;
 let q=0,h=0,t=0,hi=initial.length-1;
 while(q<M.q&&t<limit){
  const v=M.T[3*q+read(h)],next=Math.floor(v/16),w=Math.floor((v%16)/4),dir=v%4-1;
  ok(next<=M.q&&w<3&&dir>=-1&&dir<=1,"transition");
  if(w===2)tape.delete(h);else tape.set(h,w);
  h+=dir;q=next;t++;hi=Math.max(hi,h);
 }
 const word=i=>Array.from({length:M.w},(_,j)=>read(i+j)).join("");
 const status=q<M.q?"TIMEOUT":word(0)===M.codes.G?"SAT":"UNSAT";
 const rev=new Map(Object.entries(M.codes).map(([a,b])=>[b,a]));
 let encoded="",z=null;
 // Match W.run's finite serialization window, including a timeout while E
 // may be mid-shift. The simulated transition tape itself has no boundary.
 const window=initial.length+4*s.length+112;
 for(let i=0;i<window;i+=M.w){
  const w=Array.from({length:Math.min(M.w,window-i)},(_,j)=>read(i+j)).join("");
  encoded+=w;if(rev.get(w)==="E")break;
 }
 if(status==="SAT"){
  z=[];for(let i=M.w;i<encoded.length;i+=M.w){const x=rev.get(encoded.slice(i,i+M.w));if(x==="D")break;if(["u0","h0","u1","h1"].includes(x))z.push(Number(x[1]));}
 }
 return {status,z,t,head:h,span:hi+1,encoded};
}
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const U={*tuples(m,k){for(let i=0;i<m**k;i++)yield Array.from({length:k},(_,j)=>Math.floor(i/m**j)%m);}};
const factor=(h,rows)=>({h,S:new Set(rows)});
function audit(){
 const J=W.machine(),M=W.singleExit(C.compile(J)),ref=Q.refine(M),min={...M,...ref};
 const {mapped,checks}=checkQuotient(M,min,ref.map);
 let corrupt=0;
 const reject=f=>{try{f();}catch{corrupt++;return;}throw Error("tamper accepted");};
 const map=Int32Array.from(ref.map);map[0]=-1;reject(()=>checkQuotient(M,min,map));
 const map2=Int32Array.from(ref.map);map2[M.q]=0;reject(()=>checkQuotient(M,min,map2));
 const bad={...min,T:Uint32Array.from(min.T)};bad.T[0]^=4;reject(()=>checkQuotient(M,bad,ref.map));
 const fixtures=[
  ["constant-unsat",{k:1,m:2,F:[factor([0],[])]}],
  ["free",{k:1,m:2,F:[]}],
  ["force-one",{k:1,m:2,F:[factor([0],["1"])]}],
  ["equal",{k:2,m:2,F:[factor([0,1],["0,0","1,1"])]}],
  ["unequal",{k:2,m:2,F:[factor([0,1],["0,1","1,0"])]}],
  ["last-witness",{k:3,m:2,F:[factor([0,1,2],["1,1,1"])]}],
  ["binary-unsat",{k:2,m:2,F:[factor([0,1],["0,0"]),factor([0,1],["1,1"])]}]
 ];
 const rows=[];let comparisons=0,cutoffs=0;
 for(const [name,d] of fixtures){
  const s=W.stream(U,d),clock=Clock.count(J,["",s],M.codes),a=W.run(M,s,clock.clock),b=W.run(min,s,clock.clock);
  ok(a.status!=="TIMEOUT"&&a.t===clock.clock&&a.encoded===clock.encoded&&same(a,b),"clock or quotient");
  const models=[...U.tuples(2,d.k)].filter(z=>d.F.every(f=>f.S.has(f.h.map(i=>z[i]).join()))).sort((a,b)=>a.join().localeCompare(b.join()));
  ok(a.status===(models.length?"SAT":"UNSAT")&&same(a.z,models[0]??null),"oracle witness");
  for(const fuel of [...new Set([0,1,Math.floor(a.t/2),a.t-1,a.t,a.t+1])]){
   const x=W.run(M,s,fuel),y=W.run(min,s,fuel),p=sparseRun(M,s,fuel),q=sparseRun(min,s,fuel);
   ok(same(x,y)&&same(x,p)&&same(x,q),"prefix simulation "+name+" "+fuel);
   comparisons++;
   if(fuel<a.t){ok(x.status==="TIMEOUT"&&x.t===fuel,"cutoff");cutoffs++;}
   else ok(same(x,a),"halt freeze");
  }
  rows.push({name,status:a.status,transitions:a.t,stream:s.length,witness:a.z,logicalSteps:clock.steps});
 }
 return {originalStates:M.q,quotientStates:min.q,descriptorBits:ref.stats.quotientBits,mapped,checks,corrupt,comparisons,cutoffs,rows};
}
module.exports={checkQuotient,sparseRun,audit};
if(require.main===module)console.log(JSON.stringify(audit()));
