const {encode3SAT,solve,check}=require('./pnp_certified_residual.js');
const ok=(b,s)=>{if(!b)throw Error(s);};
const f=(h,rows)=>({h,S:new Set(rows)});
const d=(k,F)=>({k,m:2,F});
const eq=['0,0','1,1'],ne=['0,1','1,0'];
function oracle(x){
 for(let i=0;i<2**x.k;i++){
  const z=Array.from({length:x.k},(_,j)=>Math.floor(i/2**j)%2);
  if(x.F.every(f=>f.S.has(f.h.map(v=>z[v]).join(','))))return 'SAT';
 }
 return 'UNSAT';
}
function run(){
 const stats={small:0,sat:0,unsat:0,unknown:0,tamperRejected:0,structured:[]};
 let seed=0xF038;
 const rand=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 for(let i=0;i<512;i++){
  const k=1+i%7,F=[];
  for(let j=0;j<1+i%10;j++){
   const h=[...new Set(Array.from({length:1+(rand()>>>16)%3},()=> (rand()>>>16)%k))];
   const mask=rand()>>>16,rows=[];
   for(let t=0;t<2**h.length;t++)if(mask>>t&1)rows.push(h.map((_,b)=>t>>b&1).join(','));
   F.push(f(h,rows));
  }
  const x=d(k,F),r=solve(x),expected=oracle(x);
  ok(r.status===expected&&check(x,r),'exhaustive oracle '+i);
  stats.small++;stats[r.status.toLowerCase()]++;
 }
 const cases=[
  ['empty formula',encode3SAT([]).d,'SAT'],
  ['empty clause',encode3SAT([[]]).d,'UNSAT'],
  ['large literal IDs',encode3SAT([['999999999999999999999'],['-999999999999999999999']]).d,'UNSAT'],
  ['tautology and repeated literal',encode3SAT([[1,-1],[2,2]]).d,'SAT'],
  ['odd cycle',d(101,Array.from({length:101},(_,i)=>f([i,(i+1)%101],ne))),'UNSAT'],
  ['long chain',d(512,Array.from({length:511},(_,i)=>f([i,i+1],eq))),'SAT'],
  ['disjoint blocks',d(512,Array.from({length:256},(_,i)=>f([2*i,2*i+1],ne))),'SAT'],
  ['connected wide obstruction',d(32,Array.from({length:32},(_,i)=>Array.from({length:31-i},(_,j)=>f([i,i+j+1],['0,0','0,1','1,0']))).flat()),'UNKNOWN']
 ];
 for(const [name,x,expected] of cases){
  const r=solve(x);ok(r.status===expected,'structured '+name);
  ok(expected==='UNKNOWN'?!check(x,r):check(x,r),'structured certificate');
  stats.structured.push({name,k:x.k,status:r.status,reason:r.reason,rows:r.metrics.rows,width:r.metrics.peakWidth,eliminated:r.metrics.eliminated});
 }
 const cycle=cases[4][1],r=solve(cycle),clone=x=>JSON.parse(JSON.stringify(x));
 const mutations=[
  a=>{a.certificate.steps[0].rows=[];},
  a=>{a.certificate.steps[0].h=[];},
  a=>{a.certificate.steps.pop();},
  a=>{a.certificate.closure.output[0].rows=[];},
  a=>{a.certificate.steps[0].v=999;}
 ];
 for(const mutate of mutations){const a=clone(r);mutate(a);ok(!check(cycle,a),'tamper');stats.tamperRejected++;}
 const sat=cases[5][1],a=solve(sat);a.witness[0]^=1;ok(!check(sat,a),'wrong witness');stats.tamperRejected++;
 for(const [opts,reason] of [[{widthCap:0},'width'],[{maxRows:0},'row-budget']]){
  const u=solve(cycle,opts);ok(u.status==='UNKNOWN'&&u.reason===reason&&!check(cycle,u),'budget');stats.unknown++;
 }
 return stats;
}
module.exports={run};
if(require.main===module)console.log(JSON.stringify(run(),null,2));
