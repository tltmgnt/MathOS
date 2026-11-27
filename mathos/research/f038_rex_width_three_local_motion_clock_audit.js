// D6T source-clock audit: preserve complete D6N logical terminal state.
const U=require('./f038_rex_width_three_lazy_interval_ir.js'),K=require('./f038_rex_width_three_local_motion_compiler.js'),F=require('./f038_rex_width_three_local_motion_clock.js'),Old=require('./f038_rex_width_three_mark_fusion_clock.js'),E=require('./f038_tga_normalized_integration.js').engine(),H=require('./f038_rex_width_three_two_prefix_hard.js'),a=require('node:assert/strict');
const expected=[[100874416,102405415],[180983007,185472205],[360391458,366142030]],old=[[814084632,823871645],[1448450000,1475693033],[2774361247,2810561593]],rows=[];
for(const full of [false,true]){const J=U.machine(full),codes=K.compile(J).codes;for(const m of [2,3,4])for(const unsat of [false,true]){
 const raw=E.encode(m,Array(m).fill(0),H.family(E,m,unsat)),I=[...Array(19).fill(""),U.stream(E,raw)],r=F.count(J,I,codes),b=U.executeIR(J,I);
 a.deepEqual([r.status,r.tapes,r.heads,r.steps],[b.status,b.tapes,b.heads,b.steps]);a.equal(r.clock,expected[m-2][+unsat]);a.equal(r.localLinks,[[133730,135255],[243986,248689],[502895,511658]][m-2][+unsat]);a.equal(r.motionLinks,[[74832,75558],[132489,134788],[264333,268651]][m-2][+unsat]);a.equal(r.growthBarriers,unsat?1438:1440);a.equal(Old.count(J,I,codes).clock,old[m-2][+unsat]);rows.push({full,m,unsat,clock:r.clock,steps:r.steps,growth:r.growth});
}}
a.equal(rows.length,12);console.log(JSON.stringify({cases:rows.length,rows}));
