// KINMOTO CPU simulation stress (not Android/WebGL/real FPS).
import {makeGame,step,validate} from '../src/sim.js';
import {performance} from 'node:perf_hooks';
import fs from 'node:fs';
const g=makeGame();g.playing=true;
if(global.gc)global.gc();
const init=process.memoryUsage(),start=performance.now();
const samples=[],steps=20*60*60;let maxStep=0;
for(let i=0;i<steps;i++){
  g.controls.gas=i%490<425;
  g.controls.brake=i%490>=425;
  g.controls.left=i%2700>=540&&i%2700<780;
  g.controls.right=i%2700>=1800&&i%2700<2050;
  const t0=performance.now();step(g,1/60);const ms=performance.now()-t0;if(ms>maxStep)maxStep=ms;
  if((i+1)%3600===0){
    if(global.gc)global.gc();
    samples.push({minute:(i+1)/3600,heapUsed:process.memoryUsage().heapUsed,position:[Number(g.player.x.toFixed(2)),Number(g.player.z.toFixed(2))],collisions:g.collisions,errors:validate(g)});
  }
}
if(global.gc)global.gc();const finish=process.memoryUsage(),duration=performance.now()-start;
const errors=validate(g),delta=finish.heapUsed-init.heapUsed;
const report={test:'20 minutes simulated CPU loop',fps_claim:false,android_hardware:false,webgl:false,
 steps,elapsed_real_ms:Math.round(duration),avg_step_ms:Number((duration/steps).toFixed(4)),
 max_step_ms:Number(maxStep.toFixed(2)),heap_init_bytes:init.heapUsed,heap_final_bytes:finish.heapUsed,
 heap_delta_bytes:delta,collision_count:g.collisions,mission_started:g.mission.stage,
 events_buffer_length:g.events.length,events_buffer_cap:35,samples,errors,
 passed:errors.length===0&&g.events.length<=35&&delta<25_000_000};
fs.writeFileSync(new URL('../docs/STRESS_CPU_20MIN_V055.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,steps,avg_step_ms:report.avg_step_ms,heap_delta_bytes:delta,collisions:g.collisions,errors},null,2));
if(!report.passed)process.exitCode=1;
