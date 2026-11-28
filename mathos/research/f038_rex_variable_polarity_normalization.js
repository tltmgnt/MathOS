// D7H: certified coordinate complements and mixed intermediate resolution chains.
function transform(d,sigma){
 if(d.m!==2||!Array.isArray(sigma)||sigma.length!==d.k||Array.from(sigma).some(x=>x!==0&&x!==1))throw Error("invalid polarity");
 const s=sigma.slice();
 const F=d.F.map(f=>({h:f.h.slice(),S:new Set([...f.S].map(t=>{const row=t.split(",");return f.h.map((v,i)=>Number(row[i])^s[v]).join();}))}));
 return {d:{k:d.k,m:2,F},expand:z=>z.map((x,i)=>x^s[i])};
}

function orientations(C,d){
 const votes=Array.from({length:d.k},()=>[0,0]);let binary=0;
 for(const {c} of C.clauses(d))if(c.length===2){binary++;for(const x of c)votes[Math.abs(x)-1][+(x>0)]++;}
 const sigma=votes.map(([p,n])=>+(n>p)),alt=votes.map(([p,n])=>+(n>=p&&n>0));
 return {vectors:sigma.join()===alt.join()?[sigma]:[sigma,alt],binary,anchored:votes.filter(([p,n])=>p+n>0).length,ties:votes.filter(([p,n])=>p===n&&p>0).length};
}

function signedGroups(C,d,beam=8){
 const ax=C.clauses(d),supported=new Set(),index=new Map();
 for(const a of ax){if(a.c.length===2)for(const x of a.c)if(x<0)supported.add(-x);for(const x of a.c){if(!index.has(x))index.set(x,[]);index.get(x).push(a);}}
 const metrics={starts:0,expanded:0,transitions:0,tautologies:0,dropped:0,candidates:0};
 const rows=[];
 function state(c,proof,used){return {c,proof,used,bad:c.filter(x=>!supported.has(x)).length,key:c.join()};}
 const cmp=(a,b)=>a.bad-b.bad||a.c.length-b.c.length||a.proof.length-b.proof.length||a.key.localeCompare(b.key);
 for(const a of ax){
  if(!a.c.length||!a.c.some(x=>supported.has(x))||a.c.some(x=>supported.has(-x)&&!supported.has(x)))continue;
  metrics.starts++;let layer=[state(a.c,[a],new Set())];const saved=new Map();
  for(let depth=0;depth<=d.k&&layer.length;depth++){
   const out=new Map();
   for(const s of layer){metrics.expanded++;
    if(s.bad===0){if(!saved.has(s.key))saved.set(s.key,s);continue;}
    if(depth===d.k)continue;
    const p=s.c.find(x=>!supported.has(x)&&!supported.has(-x)&&!s.used.has(Math.abs(x)));
    if(p===undefined)continue;
    for(const b of index.get(-p)||[]){
     metrics.transitions++;
     const c=[...new Set([...s.c.filter(x=>x!==p),...b.c.filter(x=>x!==-p)])].sort((a,b)=>Math.abs(a)-Math.abs(b));
     if(c.some(x=>c.includes(-x))){metrics.tautologies++;continue;}
     if(!c.length||c.some(x=>supported.has(-x)&&!supported.has(x)))continue;
     const used=new Set(s.used);used.add(Math.abs(p));const t=state(c,[...s.proof,{...b,p}],used);
     const key=t.key+"|"+[...used].sort((a,b)=>a-b).join();
     if(!out.has(key))out.set(key,t);
    }
   }
   const sorted=[...out.values()].sort(cmp);metrics.dropped+=Math.max(0,sorted.length-beam);layer=sorted.slice(0,beam);
  }
  const all=[...saved.values()].sort(cmp);metrics.candidates+=all.length;if(all.length)rows.push(all);
 }
 return {rows,metrics};
}

function normalize(G,B,H,C,d,beam=8){
 if(!Number.isSafeInteger(beam)||beam<1||beam>32)throw Error("beam");
 const base=G.alternative(B,H,C,d,beam);
 if(base.kind==="hall")return {kind:"hall",hall:base,mode:"inherited",attempts:0};
 const o=orientations(C,d);let attempts=0,last=null;
 for(const sigma of o.vectors){
  const t=transform(d,sigma);attempts++;
  const h=G.alternative(B,H,C,t.d,beam);
  if(h.kind==="hall")return {kind:"polarity-hall",sigma,hall:h,mode:"normalized",attempts,binary:o.binary,anchored:o.anchored,ties:o.ties};
  const g=signedGroups(C,t.d,beam);last=g.metrics;
  for(const mode of ["short","wide","reverse"]){
   const policy=(a,sign)=>{
    if(sign!==1)return [];
    const rows=g.rows.slice(),taken=new Set(),selected=[];
    if(mode==="reverse")rows.reverse();
    for(const row of rows){const options=mode==="wide"?row.slice().sort((a,b)=>b.c.length-a.c.length):row;
     const s=options.find(x=>x.c.every(y=>!taken.has(y)));if(!s)continue;
     s.c.forEach(x=>taken.add(x));selected.push({options:s.c,proof:s.proof});
    }return selected;
   };
   const r=B.robust(H,C,t.d,policy);
   if(r.kind==="hall")return {kind:"signed-hall",sigma,hall:r,mode:"signed-"+mode,attempts,binary:o.binary,anchored:o.anchored,ties:o.ties,search:g.metrics};
  }
 }
 return {kind:"unknown",mode:"none",attempts,binary:o.binary,anchored:o.anchored,ties:o.ties,search:last};
}

function reduce(G,B,H,C,V,D,T,HV,NV,d,budget=2000000,beam=8){
 const h=normalize(G,B,H,C,d,beam);
 if(h.kind==="unknown")return {...D.reduce(C,V,T,d,budget),polarity:h};
 if(NV.verify(HV,d,h)!==true)throw Error("unverified polarity proof");
 return {d:{k:1,m:2,F:[{h:[0],S:new Set()}]},cert:h,polarity:h,contradiction:true,expand:()=>{throw Error("UNSAT");}};
}
module.exports={transform,orientations,signedGroups,normalize,reduce};
