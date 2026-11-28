// D7S: bounded aggregate integer division with independently checked acyclic proofs.
function verify(V,d,p){
 const ok=x=>{if(!x)throw Error("invalid cutting certificate");};
 ok(d.m===2&&p?.kind==="cutting-conflict"&&Array.isArray(p.nodes)&&p.nodes.length>0&&p.terminal===p.nodes.length-1);
 const rows=[];
 for(let i=0;i<p.nodes.length;i++){
  const n=p.nodes[i],a=new Map();let b=0n;ok(n);
  if(n.kind==="source"){ok(V.checkRow(d,n.row));for(let j=0;j<n.row.h.length;j++)a.set(n.row.h[j],BigInt(n.row.a[j]));b=BigInt(n.row.b);}
  else if(n.kind==="sum"){
   ok(Array.isArray(n.parents)&&n.parents.length>0);
   for(const j of n.parents){ok(Number.isSafeInteger(j)&&j>=0&&j<i);const r=rows[j];b+=r.b;for(const [x,v] of r.a)a.set(x,(a.get(x)||0n)+v);}
  }else if(n.kind==="divide"){
   ok(Number.isSafeInteger(n.parent)&&n.parent>=0&&n.parent<i&&typeof n.divisor==="string"&&/^[1-9][0-9]*$/.test(n.divisor));
   const g=BigInt(n.divisor);ok(g>1n);const r=rows[n.parent];
   for(const [x,v] of r.a){ok(v%g===0n);a.set(x,v/g);}
   b=r.b/g;if(b*g>r.b)b--;
  }else throw Error("unknown node");
  for(const [x,v] of a)if(!v)a.delete(x);rows.push({a,b});
 }
 const r=rows[p.terminal];let lower=0n;for(const v of r.a.values())if(v<0n)lower+=v;
 ok(lower>r.b&&String(lower)===p.lower&&String(r.b)===p.rhs);return true;
}
module.exports={verify};
