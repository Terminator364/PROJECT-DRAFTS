import test from 'node:test';
import assert from 'node:assert/strict';
import {makeGame,step,validate} from '../src/sim.js';
import {inspectBikeCar} from '../src/collision.js';

const ready=()=>{const g=makeGame();g.playing=true;return g;};

test('A2-S5 deep initial overlap never teleports bike over 0.35m in one fixed tick',()=>{
 const g=ready(),car=g.cars[0];g.cars=[car];
 g.player.x=car.x;g.player.z=car.z;g.player.yaw=0;g.player.speed=12;
 const old={x:g.player.x,z:g.player.z,meters:g.player.meters};
 step(g,1/60);
 const moved=Math.hypot(g.player.x-old.x,g.player.z-old.z);
 assert.ok(moved<.55,`moved ${moved}m in one frame`);
 assert.ok(g.peakContactCorrection<=.320001);
 assert.equal(g.collisions,1);
 assert.ok(g.save.health<100);
 assert.deepEqual(validate(g),[]);
});

test('A2-S5 repeated static overlap separates gradually without multiple damage events',()=>{
 const g=ready(),car=g.cars[0];g.cars=[car];car.preferred=0;car.speed=0;
 g.player.x=car.x;g.player.z=car.z;g.player.yaw=0;g.player.speed=15;
 const initialHealth=g.save.health;
 for(let i=0;i<25;i++){
  const oldX=g.player.x,oldZ=g.player.z;step(g,1/60);
  const d=Math.hypot(g.player.x-oldX,g.player.z-oldZ);
  assert.ok(d<=.60,`unexpected one-frame jump ${i}: ${d}`);
 }
 assert.equal(g.collisions,1);
 assert.ok(g.save.health<initialHealth);
 assert.deepEqual(validate(g),[]);
 const collision=inspectBikeCar(g.player,car);
 assert.ok(collision.overlap<.01,`deep overlap persisted: ${collision.overlap}`);
});

test('A2-S5 wheel spin and distance do not count collision positional correction',()=>{
 const g=ready(),car=g.cars[0];g.cars=[car];car.preferred=0;car.speed=0;
 g.player.x=car.x;g.player.z=car.z;g.player.speed=0;
 step(g,1/60);
 assert.ok(g.peakContactCorrection>.1);
 assert.ok(g.player.meters<.001);
 assert.ok(Math.abs(g.player.bike.wheelSpin)<.001);
});
