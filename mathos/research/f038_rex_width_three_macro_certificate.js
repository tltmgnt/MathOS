// Static bounded-span certificate for producer compiler macro SCCs. Instrumentation must preserve original descriptor bit-for-bit.
function instrument(source){
 const kinds=["scan","groupRead","groupSet","classify","shift","deposit","queryBlock","emit","blanks","streamEnd"];
 const pre=`let active=-1;const owners=new Map(),macros=[];function tagged(kind,name,fn){const old=active;if(active<0){active=macros.length;macros.push({kind,name});}try{return fn();}finally{active=old;}}\n`;
 const old='const add=(s,f)=>{if(defs.has(s))throw Error("duplicate "+s);defs.set(s,f);return s;};';
 if(!source.includes(old))throw Error("add signature");
 let s=source.replace(old,pre+`const add=(s,f)=>{if(defs.has(s))throw Error("duplicate "+s);const owner=active;owners.set(s,owner);defs.set(s,a=>{const old=active;active=owner;try{return f(a);}finally{active=old;}});return s;};`);
 for(let k of kinds){const needle="function "+k+"(";if(!s.includes(needle))throw Error("helper "+k);s=s.replace(needle,`function ${k}(...args){return tagged("${k}",String(args[0]),()=>original_${k}(...args));}\n function original_${k}(`);}
 s=s.replace("return{q,desc,events,plannerEntry:","return{macroOwner:Int32Array.from(names,([n])=>owners.get(n)),macros,q,desc,events,plannerEntry:");
 if(!s.includes("macroOwner:"))throw Error("return");
 const module={exports:{}};new Function("module","require",s)(module,()=>{throw Error("dependency");});return module.exports;
}
function certify(M,owners,macros){
 const q=M.q,T=M.T,groups=macros.map(()=>[]),ok=(v,s)=>{if(!v)throw Error(s)};
 ok(owners.length===q,"owner count");
 let taggedStates=0,taggedEntries=0,internalEdges=0,cyclic=0,potentialChecks=0,untagged=0;
 for(let i=0;i<q;i++){let k=owners[i];if(k<0){untagged++;continue;}groups[k].push(i);taggedStates++;}
 const maxima={},worst=[];let maxA=0,maxC=0;
 for(let k=0;k<groups.length;k++){
  let states=groups[k];if(!states.length)continue;
  const map=new Map(states.map((s,i)=>[s,i])),n=states.length,edges=states.map(s=>{const a=[];for(let x=0;x<3;x++){taggedEntries++;let v=T[3*s+x],j=map.get(v>>>4);if(j!==undefined){a.push([j,(v&3)-1]);internalEdges++;}}return a;});
  // Tarjan, each group is bounded finite compiler metadata, not input dependent.
  const idx=new Int32Array(n).fill(-1),low=new Int32Array(n),part=new Int32Array(n).fill(-1),stack=[],parts=[];let serial=0;
  function visit(i){idx[i]=low[i]=serial++;stack.push(i);
   for(let [j] of edges[i]){if(idx[j]<0){visit(j);low[i]=Math.min(low[i],low[j]);}else if(part[j]<0)low[i]=Math.min(low[i],idx[j]);}
   if(low[i]===idx[i]){let p=[],j;do{j=stack.pop();part[j]=parts.length;p.push(j);}while(j!==i);parts.push(p);}
  }
  for(let i=0;i<n;i++)if(idx[i]<0)visit(i);
  const aBound=[],cBound=[];
  for(let p=0;p<parts.length;p++){
   const vs=parts[p],loop=vs.length>1||edges[vs[0]].some(([j])=>j===vs[0]);let a=0,c=1;
   if(loop){
    cyclic++;
    // For all internal transitions check 1 <= 4*sign*move + phi(v)-phi(u).
    // A positive-weight cycle makes the constraint system infeasible.
    let proof=null;
    for(let sign of [-1,1]){
     const phi=new Int32Array(n);let changed=false;
     for(let it=0;it<vs.length;it++){changed=false;for(let i of vs)for(let [j,d] of edges[i])if(part[j]===p){let z=phi[i]+1-4*sign*d;if(z>phi[j]){phi[j]=z;changed=true;}}if(!changed)break;}
     if(changed)continue;proof={sign,phi};break;
    }
    ok(proof,"non-drifting SCC "+JSON.stringify(macros[k])+" size="+vs.length);
    let lo=Infinity,hi=-Infinity;for(let i of vs){lo=Math.min(lo,proof.phi[i]);hi=Math.max(hi,proof.phi[i]);for(let [j,d] of edges[i])if(part[j]===p){ok(1<=4*proof.sign*d+proof.phi[j]-proof.phi[i],"potential");potentialChecks++;}}
    a=4;c+=hi-lo;
   }
   let aa=0,cc=0;
   for(let i of vs)for(let [j] of edges[i])if(part[j]!==p){ok(part[j]<p,"SCC ordering");aa=Math.max(aa,aBound[part[j]]);cc=Math.max(cc,cBound[part[j]]);}
   aBound[p]=a+aa;cBound[p]=c+cc;
  }
  const A=Math.max(...aBound),C=Math.max(...cBound),kind=macros[k].kind;
  maxA=Math.max(maxA,A);maxC=Math.max(maxC,C);
  let r=maxima[kind]??={groups:0,states:0,A:0,C:0};r.groups++;r.states+=n;r.A=Math.max(r.A,A);r.C=Math.max(r.C,C);
  worst.push({kind,name:macros[k].name,A,C,states:n});
 }
 return{q,taggedStates,untagged,taggedEntries,internalEdges,cyclic,potentialChecks,maxA,maxC,maxima,worst:worst.sort((a,b)=>b.A-a.A||b.C-a.C).slice(0,3)};
}
function audit(source){
 const old={exports:{}};new Function("module","require",source)(old,()=>{throw Error("dependency")});
 const I=instrument(source),a=old.exports.compile(),b=I.compile();
 if(a.desc!==b.desc)throw Error("instrumentation changed descriptor");
 return certify(I.decode(b.desc),b.macroOwner,b.macros);
}
module.exports={audit,instrument,certify};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');console.log('F038_REX_MACRO_CERTIFICATE_OK '+JSON.stringify(audit(fs.readFileSync(path.join(__dirname,'f038_rex_width_three_bridge_producer.js'),'utf8'))));}
