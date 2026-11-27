// D6S source-clock audit: preserve complete D6N logical terminal state.
const U=require('./f038_rex_width_three_lazy_interval_ir.js'),K=require('./f038_rex_width_three_mark_fusion_compiler.js'),F=require('./f038_rex_width_three_mark_fusion_clock.js'),Old=require('./f038_rex_width_three_bit_carry_clock.js'),E=require('./f038_tga_normalized_integration.js').engine(),H=require('./f038_rex_width_three_two_prefix_hard.js'),a=require('node:assert/strict');
const expected=[[814084632,823871645],[1448450000,1475693033],[2774361247,2810561593]],old=[[1371735821,1389408605],[2462273307,2510948963],[4815294928,4881697883]],rows=[];
for(const full of [false,true]){const J=U.machine(full),codes=K.compile(J).codes;for(const m of [2,3,4])for(const unsat of [false,true]){
 const raw=E.encode(m,Array(m).fill(0),H.family(E,m,unsat)),I=[...Array(19).fill(""),U.stream(E,raw)],r=F.count(J,I,codes),b=U.executeIR(J,I);
 a.deepEqual([r.status,r.tapes,r.heads,r.steps],[b.status,b.tapes,b.heads,b.steps]);a.equal(r.clock,expected[m-2][+unsat]);a.equal(r.localLinks,[[58898,59697],[111497,113901],[238562,243007]][m-2][+unsat]);a.equal(Old.count(J,I,codes).clock,old[m-2][+unsat]);rows.push({full,m,unsat,clock:r.clock,steps:r.steps,growth:r.growth});
}}
a.equal(rows.length,12);console.log(JSON.stringify({cases:rows.length,rows}));
