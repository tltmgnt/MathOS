// D6O source-clock audit: preserve complete D6N logical terminal state.
const U=require('./f038_rex_width_three_lazy_interval_ir.js'),K=require('./f038_rex_width_three_paired_lowering_compiler.js'),F=require('./f038_rex_width_three_paired_lowering_clock.js'),Old=require('./f038_rex_width_three_fast_clock.js'),E=require('./f038_tga_normalized_integration.js').engine(),H=require('./f038_rex_width_three_two_prefix_hard.js'),a=require('node:assert/strict');
const expected=[[2403936576,2434761639],[4313087382,4398038139],[8431523030,8547390995]],old=[2404230732,4313582992,8432474098],rows=[];
for(const full of [false,true]){const J=U.machine(full),codes=K.compile(J).codes;for(const m of [2,3,4])for(const unsat of [false,true]){
 const raw=E.encode(m,Array(m).fill(0),H.family(E,m,unsat)),I=[...Array(19).fill(""),U.stream(E,raw)],r=F.count(J,I,codes),b=U.executeIR(J,I);
 a.deepEqual([r.status,r.tapes,r.heads,r.steps],[b.status,b.tapes,b.heads,b.steps]);a.equal(r.clock,expected[m-2][+unsat]);if(!unsat)a.equal(Old.count(J,I).clock,old[m-2]);rows.push({full,m,unsat,clock:r.clock,steps:r.steps,growth:r.growth});
}}
a.equal(rows.length,12);console.log(JSON.stringify({cases:rows.length,rows}));
