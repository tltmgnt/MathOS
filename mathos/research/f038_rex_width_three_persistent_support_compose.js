// Compose the physical headerless encoder with direct support projection.
// Dense input on tape 9 is cleared before projection; high-water allocation
// still includes it. Payload Q=8 remains unchanged throughout projection.
function machine(Support,Gap){
 const worker=Support.machine(),alphabet=worker.alphabet,ins=worker.ins.map(i=>({...i})),add=(op,t,next)=>{let i=ins.length;ins.push({op,t,next});return i;},label=()=>add("jump",0,-1),bind=(n,d)=>{ins[n].next=d;};
 const reject=ins.findIndex(i=>i.op==="reject"),rd=(t,f)=>add("read",t,alphabet.map(f)),wr=(t,v,d)=>add("write",t,{v,d}),mv=(t,dir,d)=>add("move",t,{dir,d}),loop=fn=>{let n=label();bind(n,fn(n));return n;};
 const start=(t,d)=>loop(n=>rd(t,x=>x==="L"?mv(t,1,d):mv(t,-1,n))),clear=(t,d)=>start(t,loop(n=>rd(t,x=>x==="_"?start(t,d):x==="0"||x==="1"?wr(t,"_",mv(t,1,n)):reject)));
 const done=[4,5,6,9].reduceRight((d,t)=>clear(t,d),worker.entry),J=Gap.machine(),map=[8,4,5,6,9],ids=J.ins.map(()=>label());
 J.ins.forEach((i,j)=>{let d;if(i.op==="halt")d=done;else if(i.op==="reject")d=reject;else if(i.op==="jump")d=ids[i.next];else if(i.op==="read")d=add("read",map[i.t],i.next.map(k=>ids[k]));else if(i.op==="move")d=mv(map[i.t],i.next.dir,ids[i.next.d]);else if(i.op==="write")d=wr(map[i.t],i.next.v,ids[i.next.d]);else throw Error("op");bind(ids[j],d);});
 return {...worker,ins,tapes:10,entry:ids[J.entry]};
}
module.exports={machine};
