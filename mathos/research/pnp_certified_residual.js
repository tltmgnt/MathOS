// Research-only certified residual tractability, using FV-11's D7A replay.
// No general polynomial-time SAT claim. Input: explicit Boolean tables, arity <= 3.
const R=require('./f038_rex_variable_relational_closure.js');
const V=require('./f038_rex_variable_relational_certificate.js');
const ok=(b,s)=>{if(!b)throw Error(s);};
const sorted=a=>[...new Set(a)].sort((x,y)=>x-y);
const pass=(f,z)=>f.S.has(f.h.map(v=>z[v]).join(','));
function validate(d){
 ok(d&&d.m===2&&Number.isSafeInteger(d.k)&&d.k>=0&&Array.isArray(d.F),'input');
 for(const f of d.F){
  ok(f&&Array.isArray(f.h)&&f.h.length<=3&&new Set(f.h).size===f.h.length&&f.h.every(v=>Number.isSafeInteger(v)&&v>=0&&v<d.k)&&f.S instanceof Set,'factor');
  for(const t of f.S)ok(typeof t==='string'&&(f.h.length===0?t==='':t.split(',').length===f.h.length&&t.split(',').every(b=>b==='0'||b==='1')),'row');
 }
 return d.k+1+d.F.reduce((a,f)=>a+1+f.h.length+f.S.size*(f.h.length+1),0);
}
function encode3SAT(clauses){
 ok(Array.isArray(clauses),'formula');
 const parse=x=>{ok((typeof x==='number'&&Number.isSafeInteger(x)&&x!==0)||(typeof x==='string'&&/^-?[1-9][0-9]*$/.test(x)),'literal');return BigInt(x);};
 const C=clauses.map(c=>{ok(Array.isArray(c)&&c.length<=3,'clause');return c.map(parse);});
 const abs=x=>x<0n?-x:x;
 const variables=[...new Set(C.flat().map(x=>String(abs(x))))].sort((a,b)=>BigInt(a)<BigInt(b)?-1:BigInt(a)>BigInt(b)?1:0);
 const index=new Map(variables.map((x,i)=>[x,i]));
 const F=C.map(c=>{
  const h=sorted(c.map(x=>index.get(String(abs(x))))),S=new Set();
  for(const t of tuples(h.length)){
   if(c.some(x=>t[h.indexOf(index.get(String(abs(x))))]===+(x>0n)))S.add(t.join(','));
  }
  return {h,S};
 });
 return {variables,d:{k:variables.length,m:2,F}};
}
function* tuples(n,p=[]){
 if(!n){yield p;return;}
 yield* tuples(n-1,[...p,0]);yield* tuples(n-1,[...p,1]);
}
const pack=d=>d.F.map(f=>({h:f.h.slice(),rows:[...f.S]}));
function unpack(d,F){
 ok(Array.isArray(F)&&F.every(f=>f&&Array.isArray(f.h)&&Array.isArray(f.rows)&&new Set(f.rows).size===f.rows.length),'packed tables');
 const out={k:d.k,m:2,F:F.map(f=>({h:f.h,S:new Set(f.rows)}))};validate(out);return out;
}
function solve(d,{widthCap,maxRows=1000000}={}){
 const size=validate(d),limit=Math.floor(Math.log2(size));
 widthCap=widthCap===undefined?limit:widthCap;
 ok(Number.isSafeInteger(widthCap)&&widthCap>=0&&widthCap<=limit&&Number.isSafeInteger(maxRows)&&maxRows>=0,'budget');
 const c=R.close(d,true);
 V.verify(d,c.d,c.log); // Independent row-matching replay; fail closed.
 const closure={output:pack(c.d),log:c.log},steps=[],history=[];
 const metrics={size,widthCap,peakWidth:0,rows:0,eliminated:0};
 const finish=(status,witness=null,reason=null)=>{
  const result={status,witness,reason,metrics:{...metrics}};
  if(status!=='UNKNOWN'){
   result.certificate={closure,steps};
   ok(check(d,result),'independent terminal verification');
  }
  return result;
 };
 let F=c.d.F,active=Array.from({length:d.k},(_,i)=>i);
 if(F.some(f=>!f.S.size))return finish('UNSAT');
 while(active.length){
  let best=null;
  for(const v of active){
   const bucket=F.filter(f=>f.h.includes(v));
   const h=sorted(bucket.flatMap(f=>f.h).filter(u=>u!==v));
   if(!best||h.length<best.h.length)best={v,bucket,h};
  }
  const {v,bucket,h}=best;
  if(h.length>widthCap)return finish('UNKNOWN',null,'width');
  const charge=2**(h.length+1);
  if(charge>maxRows-metrics.rows)return finish('UNKNOWN',null,'row-budget');
  metrics.rows+=charge;metrics.peakWidth=Math.max(metrics.peakWidth,h.length);
  const scope=[v,...h],positions=bucket.map(f=>f.h.map(u=>scope.indexOf(u))),rows=new Set();
  for(const t of tuples(scope.length)){
   if(bucket.every((f,i)=>f.S.has(positions[i].map(j=>t[j]).join(','))))rows.add(t.slice(1).join(','));
  }
  steps.push({v,h,rows:[...rows]});history.push({v,bucket});
  F=F.filter(f=>!f.h.includes(v));F.push({h,S:rows});
  active=active.filter(u=>u!==v);metrics.eliminated++;
  if(!rows.size)return finish('UNSAT');
 }
 const z=Array(d.k).fill(0);
 for(const {v,bucket} of history.reverse()){
  z[v]=0;if(!bucket.every(f=>pass(f,z)))z[v]=1;
  ok(bucket.every(f=>pass(f,z)),'reconstruction');
 }
 return finish('SAT',z);
}
// Independent exact replay: enumerate projected rows first, then test both
// extensions against the old factors. No call to the producer or its planner.
function check(d,result){
 try{
  const size=validate(d),limit=Math.floor(Math.log2(size));
  if(!result||!['SAT','UNSAT'].includes(result.status))return false;
  const {closure,steps}=result.certificate;
  const out=unpack(d,closure.output);
  V.verify(d,out,closure.log);
  if(!Array.isArray(steps)||steps.length>d.k)return false;
  let F=out.F;const remaining=new Set(Array.from({length:d.k},(_,i)=>i));
  for(const step of steps){
   if(F.some(f=>!f.S.size)||!remaining.has(step.v))return false;
   const bucket=F.filter(f=>f.h.includes(step.v)),others=F.filter(f=>!f.h.includes(step.v));
   const support=sorted(bucket.flatMap(f=>f.h).filter(u=>u!==step.v));
   if(support.length>limit||!Array.isArray(step.h)||JSON.stringify(support)!==JSON.stringify(step.h)||!Array.isArray(step.rows))return false;
   const claimed=new Set(step.rows);
   if(claimed.size!==step.rows.length||claimed.size>2**support.length)return false;
   const expected=new Set();
   for(let i=0;i<2**support.length;i++){
    const bits=support.map((_,j)=>Math.floor(i/2**j)%2);
    const assignment=new Map(support.map((v,j)=>[v,bits[j]]));
    for(let b=0;b<2;b++){
     assignment.set(step.v,b);
     if(bucket.every(f=>[...f.S].some(t=>t===f.h.map(v=>assignment.get(v)).join(',')))){
      expected.add(bits.join(','));break;
     }
    }
   }
   if(expected.size!==claimed.size||[...expected].some(t=>!claimed.has(t)))return false;
   F=[...others,{h:support,S:expected}];remaining.delete(step.v);
  }
  const empty=F.some(f=>!f.S.size);
  if(result.status==='UNSAT')return empty&&result.witness===null;
  const z=result.witness;
  return !empty&&remaining.size===0&&Array.isArray(z)&&z.length===d.k&&Array.from(z).every(b=>b===0||b===1)&&d.F.every(f=>pass(f,z));
 }catch(e){return false;}
}
module.exports={encode3SAT,solve,check};
