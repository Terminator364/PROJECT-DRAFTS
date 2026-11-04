import test from 'node:test';import assert from 'node:assert/strict';
import {makeGame,step,validate,trafficTargetSpeed} from '../src/sim.js';
const d=(car,other)=>Math.hypot(car.x-other.x,car.z-other.z);
test('traffic brakes when a car enters its actual lane ahead',()=>{
 const g=makeGame();g.playing=true;
 const leader=g.cars[1],car=g.cars[0];car.speed=12;car.preferred=12;
 // Force a cross-loop blocker immediately ahead. The car remains physically
 // elsewhere on its own route after the first movement, but sensor sees it now.
 leader.loop=(car.loop+1)%4;leader.x=car.x+Math.sin(car.yaw)*5.4;
 leader.z=car.z-Math.cos(car.yaw)*5.4;
 step(g,1/60);
 assert.ok(car.braking,'the follower must recognize the obstacle');
 assert.ok(car.speed<12,'a real loss of velocity is required');
 assert.equal(validate(g).length,0);
});
test('cars avoid artificial reverse movement under crowding',()=>{
 const g=makeGame();g.playing=true;for(const car of g.cars){car.preferred=10;car.speed=8}
 for(let i=0;i<3000;i++){g.controls.gas=i%100<50;step(g,1/60);}
 assert.equal(validate(g).length,0);assert.ok(g.cars.every(c=>c.speed>=0));
});
test('traffic yields toward perpendicular car with prior right-of-way',()=>{
 const g=makeGame();g.playing=true;
 const car=g.cars[7],other=g.cars[0];car.speed=11;car.preferred=11;
 other.x=car.x+Math.sin(car.yaw)*9;
 other.z=car.z-Math.cos(car.yaw)*9;
 other.yaw=car.yaw+Math.PI/2;
 assert.ok(trafficTargetSpeed(car,g.cars)<car.speed);
});
