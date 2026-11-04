import test from 'node:test';
import assert from 'node:assert/strict';
import {guideTo} from '../src/route_guidance.js';
import {angleOf} from '../src/math.js';
import {byId,makeGame,missionTarget} from '../src/sim.js';
test('road distance is longer than straight line when route must turn',()=>{
  const a={x:4,z:95},b={x:109,z:-13};const result=guideTo(a,b,0);
  assert.ok(result.distance>Math.hypot(a.x-b.x,a.z-b.z));assert.ok(result.route.length>=3);
});
test('navigation uses graph route, no route teleports through buildings',()=>{
  const g=makeGame(),nav=guideTo(g.player,missionTarget(g.mission),g.player.yaw);
  assert.ok(nav.distance>100&&nav.distance<900);assert.ok(nav.route.length>=3);
});
test('navigation tells left/right relative to bike yaw in world coordinates',()=>{
  const a={x:0,z:0},b={x:0,z:-70};const route={nodes:[a,{x:0,z:-40},b]};
  assert.equal(guideTo(a,b,-Math.PI/2,route).kind,'right');
  assert.equal(guideTo(a,b,Math.PI/2,route).kind,'left');
  assert.equal(guideTo(a,b,0,route).kind,'straight');
});
test('navigation signals stop near destination, not endless road arrow',()=>{
  const a={x:13,z:3},b={x:13,z:12};let nav=guideTo(a,b,1);
  assert.equal(nav.kind,'arrive');assert.equal(nav.turnDistance,0);
});
test('navigation calculations are deterministic and finite for all places',()=>{
 const g=makeGame();for(const p of [byId('victoire'),byId('garage'),byId('matonge'),byId('clinique')]){
  let nav=guideTo(g.player,p,g.player.yaw),nav2=guideTo(g.player,p,g.player.yaw);
  assert.deepEqual(nav,nav2);assert.ok(Number.isFinite(nav.distance));
 }
});
