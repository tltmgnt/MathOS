// Apache-2.0; reproducibility reference, not a physical-machine certification.
function verify(E,Admission,Audit) {
  const ok=(p,s)=>{if(!p)throw Error(s)};
  const vars=Array.from({length:9},(_,i)=>i);
  function* tuples(m,k,p=[]){if(!k){yield p;return;}for(let a=0;a<m;a++)yield* tuples(m,k-1,[...p,a]);}
  function accepts(m,B,z){return B.every(c=>c.some(l=>{const x=-l-1;return z[Math.floor(x/m)]!==x%m;}));}
  function forest(m,B){
    const scopes=B.map(c=>c.map(l=>Math.floor((-l-1)/m)));
    const graph=vars.map(()=>Array(9).fill(false));
    for(const h of scopes)for(const i of h)for(const j of h)if(i!==j)graph[i][j]=true;
    function search(active,G){
      if(!active.length)return [];
      for(const v of active){
        const sep=active.filter(u=>G[v][u]);
        if(sep.length>3)continue;
        const next=G.map(r=>r.slice());
        for(const a of sep)for(const b of sep)if(a!==b)next[a][b]=true;
        const tail=search(active.filter(u=>u!==v),next);
        if(tail!==null)return [{v,sep,h:[v,...sep].sort((a,b)=>a-b)},...tail];
      }
      return null;
    }
    const bags=search(vars,graph);
    if(bags===null)return {status:"STRUCTURAL_REFUSAL"};
    const order=bags.map(b=>b.v);
    for(const [i,b] of bags.entries()){
      b.parent=b.sep.length?Math.min(...b.sep.map(v=>order.indexOf(v))):-1;
      b.owned=B.filter((c,j)=>Math.min(...scopes[j].map(v=>order.indexOf(v)))===i);
      ok(b.owned.every(c=>c.every(l=>b.h.includes(Math.floor((-l-1)/m)))),"factor coverage");
      b.rows=[...tuples(m,b.h.length)].filter(row=>{
        const z=Array(9);b.h.forEach((v,j)=>z[v]=row[j]);return accepts(m,b.owned,z);
      });
    }
    const key=(bag,row,sep)=>sep.map(v=>row[bag.h.indexOf(v)]).join(",");
    for(const [i,b] of bags.entries())if(b.parent>=0){
      const par=bags[b.parent];ok(b.parent>i&&b.sep.every(v=>par.h.includes(v)),"separator containment");
      const support=new Set(b.rows.map(row=>key(b,row,b.sep)));
      par.rows=par.rows.filter(row=>support.has(key(par,row,b.sep)));
    }
    if(bags.some(b=>b.parent<0&&!b.rows.length))return {status:"UNSAT"};
    const z=Array(9);
    for(const b of bags.slice().reverse()){
      const row=b.rows.find(row=>b.sep.every(v=>row[b.h.indexOf(v)]===z[v]));
      ok(row,"reverse support");z[b.v]=row[b.h.indexOf(b.v)];
    }
    ok(accepts(m,B,z),"reference witness");
    return {status:"SAT",z};
  }
  let assignments=0,sat=0,unsat=0,refused=0;
  const rows=[];
  function check(f,expected){
    const raw=E.encode(f.m,f.pins,f.B),d=E.decode(raw),r=forest(f.m,f.B);
    ok(d&&d.m===f.m&&d.pins.join()===f.pins.join()&&raw.length===E.length(d.n),"encoder "+f.name);
    let hits=0;
    for(const z of tuples(f.m,9)){
      const truth=accepts(f.m,f.B,z),decoded=d.F.every(f=>f.S.has(f.h.map(v=>z[v]).join(",")));
      ok(truth===decoded,"factor decoding "+f.name);
      assignments++;if(truth)hits++;
    }
    if(r.status==="STRUCTURAL_REFUSAL"){refused++;ok(hits>0,"positive refusal control "+f.name);}
    else if(r.status==="SAT"){sat++;ok(hits>0&&E.valid(raw,E.witness(f.m,f.pins,r.z)),"SAT witness "+f.name);}
    else {unsat++;ok(hits===0,"UNSAT "+f.name);}
    if(expected)ok(r.status===expected,"expected status "+f.name);
    if(f.witness)ok(E.valid(raw,f.witness),"historical witness "+f.name);
    rows.push({name:f.name,status:r.status,models:hits,L:raw.length});
  }
  const expected={"empty":"SAT","edge-SAT":"SAT","edge-UNSAT":"UNSAT","K5-refusal":"STRUCTURAL_REFUSAL","m3-forced":"SAT","m4-forced":"SAT"};
  for(const f of Admission.fixtures(E,"all"))check(f,expected[f.name]);
  let seed=0x52455831;
  const rand=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed>>>8)%n;};
  for(let i=0;i<24;i++){
    const B=[];
    for(let j=0;j<20;j++){
      const start=rand(7),k=1+rand(3);
      B.push(Array.from({length:k},(_,a)=>-(2*(start+a)+rand(2)+1)));
    }
    check({name:"seed-"+i,m:2,pins:[i%2,0],B});
  }
  const raw=E.encode(2,[0,0],[]);
  for(const bad of ["",raw.slice(0,-1),raw+"0",raw.slice(0,31)+"1"+raw.slice(32)])ok(E.decode(bad)===null,"malformed input");
  const a=Audit.sharpened();
  ok(a.count===10018&&a.H0===2785338274n,"arithmetic regression");
  return {scope:"HOST_REFERENCE_AND_FINITE_ARITHMETIC_ONLY",cases:rows.length,assignments,sat,unsat,refused,malformed:4,arithmeticCases:a.count,rows,PNP_RESOLUTION_STATUS:"OPEN",PROMOTION:"NONE"};
}
module.exports={verify};
if(require.main===module){const E=require('./f038_tga_normalized_integration.js').engine(),A=require('./f038_rex_width_three_admission.js'),U=require('./f038_rex_width_three_independent_audit.js');console.log(JSON.stringify(verify(E,A,U),null,2));}
