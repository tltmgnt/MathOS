// D7G: bounded alternative disjunction derivation, terminal subsumption, and certified Hall reuse.
function explore(axioms,sign,next,mutex,k,beam=8){
 const support=new Map();for(const a of mutex.values())for(const x of a.c.map(y=>-y))support.set(x,(support.get(x)||0)+1);
 const metrics={starts:0,expanded:0,ambiguous:0,transitions:0,beamDropped:0,candidates:0,dominanceTests:0,dominated:0};
 const compare=(a,b)=>a.unsupported-b.unsupported||a.options.length-b.options.length||b.weight-a.weight||a.proof.length-b.proof.length||a.key.localeCompare(b.key);
 function state(options,proof,used){
  return {options,proof,used,key:options.join(),unsupported:options.filter(x=>!support.has(x)).length,weight:options.reduce((s,x)=>s+(support.get(x)||0),0)};
 }
 const rows=[];
 for(const a of axioms){
  if(!a.c.length||!a.c.every(x=>x*sign>0))continue;metrics.starts++;
  let layer=[state(a.c,[a],new Set())];const saved=new Map();
  const save=s=>{const old=saved.get(s.key);if(!old||s.proof.length<old.proof.length)saved.set(s.key,s);};
  for(let depth=0;depth<=k&&layer.length;depth++){
   const out=new Map();
   for(const s of layer){
    metrics.expanded++;
    const p=s.options.find(x=>next.has(x)&&!s.used.has(x));
    if(p===undefined||depth===k||s.unsupported===0)save(s);
    if(p===undefined||depth===k)continue;
    const choices=next.get(p);if(choices.length>1)metrics.ambiguous++;
    for(const b of choices){
     metrics.transitions++;
     const options=[...new Set([...s.options.filter(x=>x!==p),...b.c.filter(x=>x!==-p)])].sort((a,b)=>Math.abs(a)-Math.abs(b));
     const used=new Set(s.used);used.add(p);const t=state(options,[...s.proof,b],used);
     const key=t.key+"|"+[...used].sort((a,b)=>Math.abs(a)-Math.abs(b)).join();
     if(!out.has(key))out.set(key,t);
    }
   }
   const sorted=[...out.values()].sort(compare);metrics.beamDropped+=Math.max(0,sorted.length-beam);layer=sorted.slice(0,beam);
  }
  const all=[...saved.values()].sort(compare),minimal=[];
  metrics.candidates+=all.length;
  for(const s of all){
   let dominated=false;
   for(const t of minimal){metrics.dominanceTests++;if(t.options.length<s.options.length&&t.options.every(x=>s.options.includes(x))){dominated=true;break;}}
   if(dominated)metrics.dominated++;else minimal.push(s);
  }
  if(all.length)rows.push({all,minimal});
 }
 return {rows,metrics};
}

function alternative(B,H,C,d,beam=8){
 if(!Number.isSafeInteger(beam)||beam<1||beam>32)throw Error("beam 1..32");
 const base=B.robust(H,C,d),stats={policies:0,starts:0,expanded:0,ambiguous:0,transitions:0,beamDropped:0,candidates:0,dominanceTests:0,dominated:0};
 if(base.kind==="hall")return {...base,groupStrategy:"inherited",extraction:stats};
 const cache=new Map();let last=base;
 for(const mode of ["minimal","wide","reverse","supported-first"]){
  stats.policies++;
  const policy=(axioms,sign,next,mutex)=>{
   if(!cache.has(sign)){const r=explore(axioms,sign,next,mutex,d.k,beam);cache.set(sign,r.rows);for(const [key,value] of Object.entries(r.metrics))stats[key]+=value;}
   let rows=cache.get(sign).slice();
   if(mode==="reverse")rows.reverse();
   if(mode==="supported-first")rows.sort((a,b)=>a.minimal[0].unsupported-b.minimal[0].unsupported||a.minimal[0].options.length-b.minimal[0].options.length);
   const selected=[],taken=new Set();
   for(const row of rows){
    const choices=mode==="wide"?row.all.slice().sort((a,b)=>a.unsupported-b.unsupported||b.options.length-a.options.length||b.weight-a.weight||a.key.localeCompare(b.key)):row.minimal;
    const s=choices.find(x=>x.options.every(y=>!taken.has(y)));if(!s)continue;
    s.options.forEach(x=>taken.add(x));selected.push({options:s.options,proof:s.proof});
   }
   return selected;
  };
  last=B.robust(H,C,d,policy);
  if(last.kind==="hall")return {...last,groupStrategy:mode,extraction:{...stats},baseline:base.kind};
 }
 return {...last,groupStrategy:"none",extraction:{...stats},baseline:base.kind};
}

function reduce(B,H,C,V,D,T,HV,d,budget=2000000,beam=8){
 const h=alternative(B,H,C,d,beam);
 if(h.kind==="unknown")return {...D.reduce(C,V,T,d,budget),hall:h};
 if(HV.verify(d,h)!==true)throw Error("unverified alternative Hall certificate");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:h,hall:h,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={explore,alternative,reduce};
