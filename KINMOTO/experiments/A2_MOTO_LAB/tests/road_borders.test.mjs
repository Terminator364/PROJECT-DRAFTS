import test from 'node:test';
import assert from 'node:assert/strict';
import {nearestRoad, keepOverStreet, STREET_SAFE_HALF_WIDTH} from '../src/math.js';
import {makeGame,step,validate} from '../src/sim.js';

const drive=(steer,n=1100)=>{
  const g=makeGame();g.playing=true;g.cars=[];g.controls.gas=true;
  if(steer<0)g.controls.left=true;else if(steer>0)g.controls.right=true;
  for(let i=0;i<n;i++){step(g,1/60);
    assert.ok(nearestRoad(g.player).distance<=STREET_SAFE_HALF_WIDTH+1e-8,
      `entered building plot at ${i}: ${g.player.x} / ${g.player.z}`);
    assert.equal(validate(g).length,0);
  }return g;
};
test('rider cannot penetrate façades when holding left for 18 seconds',()=>{let g=drive(-1);assert.ok(g.player.x>-175);assert.ok(g.player.x<175)});
test('rider cannot penetrate façades when holding right for 18 seconds',()=>{let g=drive(+1);assert.ok(g.player.x>-175);assert.ok(g.player.x<175)});
test('camera is clamped inside street envelope without changing height',()=>{
  const camera={x:-28,y:9,z:67};assert(keepOverStreet(camera,7.5));
  assert.ok(nearestRoad(camera).distance<=7.5);assert.equal(camera.y,9);
});
test('street envelope is stable and invariant under repeated clamping',()=>{
  let p={x:30,z:70};assert(keepOverStreet(p));const x=p.x,z=p.z;
  for(let i=0;i<100;i++)assert.equal(keepOverStreet(p),false);
  assert.equal(p.x,x);assert.equal(p.z,z);
});
test('negative coordinates and intersections are not teleported arbitrarily',()=>{
  let a={x:-13,z:-13};assert(keepOverStreet(a));assert.ok(nearestRoad(a).distance<=STREET_SAFE_HALF_WIDTH);
  const b={x:8,z:8};assert.equal(keepOverStreet(b),false);
});
