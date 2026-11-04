import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectBikeCar,closingSpeed} from '../src/collision.js';
import {makeGame,step,validate} from '../src/sim.js';
const bike=(x,z,v=10,yaw=0)=>({x,z,speed:v,yaw,bike:{vx:Math.sin(yaw)*v,vz:-Math.cos(yaw)*v}});
const car=(x=0,z=0,yaw=0,kind=0,v=0)=>({x,z,yaw,kind,speed:v});
test('collision footprint rejects false contact when overtaking beside a car',()=>{
 const c=car(); const b=bike(2.2,0);const out=inspectBikeCar(b,c);
 assert.equal(out.hit,false);assert(out.clearance>1.1);
});
test('oriented collision detects a front bumper contact and resolves outward',()=>{
 const c=car();const b=bike(0,-2.25);
 let q=inspectBikeCar(b,c);assert.equal(q.hit,true);assert(q.normalZ<0);
 b.x+=q.normalX*q.overlap;b.z+=q.normalZ*q.overlap;
 assert.ok(inspectBikeCar(b,c).clearance>=.58-1e-9);
});
test('side contact uses car yaw rather than screen-space axis',()=>{
 const c=car(0,0,Math.PI/2);const hit=inspectBikeCar(bike(0,1.23),c);
 assert.equal(hit.hit,true);assert(hit.normalZ>0);
 const miss=inspectBikeCar(bike(0,2.5),c);assert.equal(miss.hit,false);
});
test('bus has visibly larger contact footprint than a small taxi',()=>{
 const b=bike(0,-2.9);
 assert.equal(inspectBikeCar(b,car(0,0,0,0)).hit,false);
 assert.equal(inspectBikeCar(b,car(0,0,0,4)).hit,true);
});
test('deeply embedded motorcycle has finite exit and finite closing speed',()=>{
 const b=bike(0,0,13),c=car();let q=inspectBikeCar(b,c);assert(q.inside&&q.overlap>1.0);
 assert(Number.isFinite(q.normalX)&&Number.isFinite(q.normalZ));assert(closingSpeed(b,c,q)>0);
});
test('closingSpeed excludes vehicles separating from contact',()=>{
 const c=car(0,0,0,0,0),b=bike(0,-2.35,10,0);
 let q=inspectBikeCar(b,c); assert(q.hit); assert.equal(closingSpeed(b,c,q),0);
});
test('contact scratch object is reused with zero per-car heap allocation',()=>{
 const scratch={};const a=inspectBikeCar(bike(0,0),car(),scratch);
 assert.strictEqual(a,scratch);const b=inspectBikeCar(bike(9,9),car(),scratch);
 assert.strictEqual(b,scratch);assert.equal(b.hit,false);
});
test('same-center impact still reduces health, and cooldown prevents double damage',()=>{
 let g=makeGame();g.playing=true;let c=g.cars[0];
 g.player.x=c.x;g.player.z=c.z;g.player.speed=12;
 let h=g.save.health;step(g,1/60);assert(g.save.health<h);let d=g.save.health;
 step(g,1/60);assert.equal(g.save.health,d);assert.equal(g.collisions,1);assert.deepEqual(validate(g),[]);
});
