// FV-10: translate actual D7B source/row-addition/pivot logs to FV-03
// proof trees. This exporter is untrusted: generated Lean checks bind
// all claimed equations to the original factors.
const assert=(b,s)=>{if(!b)throw Error("FV10 "+s);};
const bit=(i)=>1n<<BigInt(i);
const indices=(m,k)=>Array.from({length:k},(_,i)=>i).filter(i=>m&bit(i));
const mask=vs=>vs.reduce((m,v)=>m^bit(v),0n);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const bool=b=>b?"true":"false";
const list=xs=>"["+xs.join(",")+"]";
const term=p=>p.kind==="source"?`(.source ${p.i} ${list(p.mask.map(bool))} ${bool(p.rhs)})`:
 p.kind==="reflexive"?`(.reflexive ${p.v})`:p.kind==="add"?`(.add ${term(p.a)} ${term(p.b)})`:`(.cancel ${term(p.a)} ${p.v})`;
const equation=e=>`⟨${list(e.vars)}, ${bool(e.rhs)}⟩`;
const reflexive=v=>({vars:[v,v],rhs:0,p:{kind:"reflexive",v}});
const add=(a,b)=>({vars:a.vars.concat(b.vars),rhs:a.rhs^b.rhs,p:{kind:"add",a:a.p,b:b.p}});
function cancel(a,v){
 const vs=a.vars.slice();for(let i=0;i<2;i++){const j=vs.indexOf(v);assert(j>=0,"cancel");vs.splice(j,1);}
 return {vars:vs,rhs:a.rhs,p:{kind:"cancel",a:a.p,v}};
}
function normalize(a){
 for(const v of new Set(a.vars))while(a.vars.filter(x=>x===v).length>=2)a=cancel(a,v);
 return a;
}
function reorder(a,target){
 assert(new Set(a.vars).size===a.vars.length&&new Set(target).size===target.length&&mask(a.vars)===mask(target),"reorder");
 // Append a reflexive pair, then cancel the first two occurrences;
 // the remaining occurrence moves to the end. No permutation axiom.
 for(const v of target)a=cancel(add(a,reflexive(v)),v);
 assert(same(a.vars,target),"order");
 return a;
}
function translate(d,a){
 const k=d.k,rows=a.rows.map(r=>{
  const f=d.F[r.factor];assert(f&&Number.isInteger(r.local)&&r.local>=0&&r.local<2**f.h.length,"source index/mask");
  const bits=f.h.map((_,i)=>!!(r.local>>i&1)),vs=f.h.filter((_,i)=>bits[i]);
  assert(mask(vs)===r.mask&&(r.rhs===0||r.rhs===1),"source claim");
  return {vars:vs,rhs:r.rhs,p:{kind:"source",i:r.factor,mask:bits,rhs:r.rhs}};
 });
 const source=rows.slice(),work=rows.slice(),history=rows.slice();
 for(const [i,j] of a.ops){
  assert(Number.isInteger(i)&&Number.isInteger(j)&&0<=j&&j<i&&i<work.length,"operation index");
  work[i]=normalize(add(work[i],work[j]));history.push(work[i]);
 }
 assert(a.work.length===work.length&&work.every((r,i)=>mask(r.vars)===a.work[i].mask&&r.rhs===a.work[i].rhs),"work matrix");
 if(a.contradiction>=0){
  const c=work[a.contradiction];assert(c&&c.vars.length===0&&c.rhs===1,"contradiction");
  return {source,history,work,contradiction:c,forms:[]};
 }
 assert(a.pivots.length===k&&a.forms.length===k&&same(a.free,a.pivots.flatMap((p,i)=>p<0?[i]:[])),"free coordinates");
 const forms=[];
 for(let i=0;i<k;i++){
  const f=a.forms[i],target=[i,...indices(f.mask,a.free.length).map(j=>a.free[j])],p=a.pivots[i];
  let e;
  if(p<0){e=reflexive(i);assert(same(e.vars,target)&&f.rhs===0,"free form");}
  else{
   e=work[p];assert(e&&e.vars.includes(i)&&e.vars.every(j=>j<=i),"pivot");
   for(const j of e.vars.slice())if(j!==i&&a.pivots[j]>=0)e=normalize(add(e,forms[j]));
   e=reorder(e,target);assert(e.rhs===f.rhs,"form RHS");
  }
  forms.push(e);history.push(e);
 }
 return {source,history,work,forms,contradiction:null};
}
const factor=f=>`⟨${list(f.h??f.scope)}, ${list((f.rows??[...f.S]).map(r=>list((typeof r==="string"?(r===""?[]:r.split(",").map(Number)):r).map(bool))))}⟩`;
const tables=fs=>list(fs.map(factor));
const choose=(xs,empty)=>xs.length?xs.reduceRight((tail,x,i)=>i===xs.length-1?x:`if i.val = ${i} then ${x} else ${tail}`,""):empty;
function lean(d,r,local,name){
 const k=d.k,m=r.a.free.length,log=translate(d,r.a),N="MathOS.F038.AffineReplay.Generated_"+name;
 let s=`import F038Formal.AffineReplay
namespace ${N}
open MathOS.F038 MathOS.F038.Cert MathOS.F038.Reduction
open MathOS.F038.LocalMaterialization MathOS.F038.ResidualRefinement MathOS.F038.AffineReplay
set_option maxRecDepth 8192
set_option maxHeartbeats 2000000
def source : List (RowFactor ${k}) := ${tables(d.F)}
def claims : List (EqProof ${k} × Equation ${k}) := ${list(log.history.map(e=>`(${term(e.p)}, ${equation(e)})`))}
example : logCheck source claims = true := by decide
`;
 if(log.contradiction){
  s+=`theorem exported_unsat : ¬ ∃ x, TableModels source x :=
  affine_contradiction_sound source ${term(log.contradiction.p)} (by decide)
#print axioms exported_unsat
`;
 }else{
  assert(local,"local replay");
  const raw=r.a.forms.map(f=>({vars:indices(f.mask,m),rhs:f.rhs}));
  s+=`def amap : AffineMap ${k} ${m} :=
  { free := fun i => ${choose(r.a.free.map(String),"Fin.elim0 i")}
    forms := fun i => ${choose(raw.map(equation),"Fin.elim0 i")}
    proofs := fun i => ${choose(log.forms.map(e=>term(e.p)),"Fin.elim0 i")} }
def localRows : List (RowFactor ${m}) := ${tables(local.local)}
def scopes : List (List (Fin ${m})) := ${list(local.local.map(f=>list(f.scope)))}
def out : List (RowFactor ${Math.max(1,m)}) := ${tables(r.d.F)}
example : affineMapCheck source amap = true := by decide
example : localCheck 8 amap source localRows scopes = true := by decide
`;
  if(m){
   s+=`example : tableSetCheck (simplifyResidual 8 localRows) out = true := by decide
theorem exported_exact (z : Assignment ${m}) :
    TableModels out z ↔ TableModels source (expand amap z) :=
  simplified_exact 8 amap source localRows out scopes (by decide) (by decide) z
#print axioms exported_exact
`;
  }else{
   s+=`example : tableSetCheck (padZero (simplifyResidual 8 localRows)) out = true := by decide
theorem exported_exact :
    (∃ z, TableModels out z) ↔ (∃ x, TableModels source x) := by
  constructor
  · rintro ⟨z,hz⟩
    have hp := (tableSetCheck_exact _ _ (by decide : tableSetCheck (padZero (simplifyResidual 8 localRows)) out = true) z).mpr hz
    have hs := ((padZero_exact _ z).mp hp).2
    exact ⟨expand amap zeroAssignment, (localCheck_exact 8 amap source localRows scopes (by decide) _).mp
      ((simplifyResidual_exact 8 localRows _).mp hs)⟩
  · rintro ⟨x,hx⟩
    have hm := (localCheck_exact 8 amap source localRows scopes (by decide) (project amap x)).mpr (by
      rw [affineMap_reconstruct source amap (by decide) x hx]
      exact hx)
    have he : project amap x = zeroAssignment := by
      funext i
      exact Fin.elim0 i
    rw [he] at hm
    refine ⟨fun _ => false, (tableSetCheck_exact _ _ (by decide : tableSetCheck (padZero (simplifyResidual 8 localRows)) out = true) _).mp ?_⟩
    exact (padZero_exact _ _).mpr ⟨rfl,(simplifyResidual_exact 8 localRows _).mpr hm⟩
#print axioms exported_exact
`;
  }
 }
 return s+`end ${N}\n`;
}
module.exports={translate,lean};
