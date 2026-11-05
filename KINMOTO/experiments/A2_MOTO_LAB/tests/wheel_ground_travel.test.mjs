import test from 'node:test';
import assert from 'node:assert/strict';
import {makeGame,step,validate} from '../src/sim.js';
import {BIKE_WHEEL_RADIUS} from '../src/bike_physics.js';
const run=(g,frames=300)=>{g.playing=true;g.cars=[];g.controls.gas=true;for(let i=0;i<frames;i++)step(g,1/60);return g;};

test('accelerating into a curb cannot rotate wheels despite stationary chassis',()=>{
 const g=makeGame();g.player.x=8.09;g.player.z=45;g.player.yaw=Math.PI/2;run(g);
 assert.ok(g.player.meters<.05,`chassis moved ${g.player.meters}`);
 assert.ok(g.player.bike.groundSpeed<.01,`measured ground speed is phantom: ${g.player.bike.groundSpeed}`);
 assert.ok(Math.abs(g.player.bike.wheelSpin*BIKE_WHEEL_RADIUS-g.player.meters)<1e-6);
 assert.ok(g.player.bike.wheelSpin*BIKE_WHEEL_RADIUS<.05);
 assert.deepEqual(validate(g),[]);
});
test('sliding along curb spins tyre only for permitted tangent travel',()=>{
 const g=makeGame();g.player.x=8.09;g.player.z=45;g.player.yaw=Math.PI/3;run(g,300);
 const tyreDistance=g.player.bike.wheelSpin*BIKE_WHEEL_RADIUS;
 assert.ok(g.player.meters>1,`expected curb tangent movement, got ${g.player.meters}`);
 assert.ok(Math.abs(tyreDistance-g.player.meters)<1e-5,`tyre ${tyreDistance} meters ${g.player.meters}`);
 assert.deepEqual(validate(g),[]);
});
test('free-road riding retains wheel rotation equal to actual travel',()=>{
 const g=makeGame();g.player.x=4.4;g.player.z=95;g.player.yaw=0;run(g,300);
 const tyreDistance=g.player.bike.wheelSpin*BIKE_WHEEL_RADIUS;
 assert.ok(g.player.meters>10);
 assert.ok(Math.abs(tyreDistance-g.player.meters)<1e-5);
});
test('HUD speed is derived from resolved ground speed rather than blocked engine output',async()=>{
 const fs=await import('node:fs');
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/p\.bike\?\.groundSpeed\?\?p\.speed/);
});
