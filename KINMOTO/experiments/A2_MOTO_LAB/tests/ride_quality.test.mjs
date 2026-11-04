import test from 'node:test';import assert from 'node:assert/strict';
import {observeRide,addRideDiscomfort,rideComfortGrade,rideComfortPaymentMultiplier} from '../src/ride_quality.js';
import {makeGame,step,byId,interact} from '../src/sim.js';
test('no comfort penalty while driving empty bike',()=>{const m={stage:'pickup',comfort:100};observeRide(m,{acceleration:-50,yawRate:2,suspensionVelocity:5},30,1/60);assert.equal(m.comfort,100);});
test('soft ride keeps comfort high',()=>{const m={stage:'drop',comfort:100};for(let i=0;i<3600;i++)observeRide(m,{acceleration:2,yawRate:.08,suspensionVelocity:.08},5,1/60);assert.equal(m.comfort,100);});
test('hard braking and harsh turn lower comfort',()=>{const m={stage:'drop',comfort:100};observeRide(m,{acceleration:-10,yawRate:.9,suspensionVelocity:0},15,1);assert.equal(m.comfort,100);observeRide(m,{acceleration:-10,yawRate:.9,suspensionVelocity:0},15,1/60);assert.ok(m.comfort<100);});
test('impact penalizes after pickup and stays bounded',()=>{const m={stage:'drop',comfort:5};addRideDiscomfort(m,100,'impact');assert.equal(m.comfort,0);assert.equal(m.impacts,1);addRideDiscomfort(m,500,'impact');assert.equal(m.comfort,0);});
test('comfortable trip pays at least as much as harsh one',()=>{assert.equal(rideComfortPaymentMultiplier({comfort:100}),1);assert.ok(rideComfortPaymentMultiplier({comfort:20})<1);assert.ok(rideComfortPaymentMultiplier({comfort:20})>=.78);});
test('ride grades are stable and comprehensible',()=>{assert.equal(rideComfortGrade({comfort:90}),'EXCELLENT');assert.equal(rideComfortGrade({comfort:20}),'INCONFORTABLE');});
test('game starts comfort only after pickup, and settles bonus once',()=>{
 const g=makeGame();g.playing=true;g.cars=[];
 assert.equal(g.mission.comfort,100);
 g.player.x=byId(g.mission.from).x;g.player.z=byId(g.mission.from).z;g.player.speed=0;assert(interact(g).ok);
 addRideDiscomfort(g.mission,30);
 if(g.mission.stage==='via'){g.player.x=byId(g.mission.via).x;g.player.z=byId(g.mission.via).z;assert(interact(g).ok);}
 g.player.x=byId(g.mission.to).x;g.player.z=byId(g.mission.to).z;
 const ret=interact(g);assert(ret.ok);assert.equal(g.mission.comfort,100);assert.equal(g.save.rides,1);assert(ret.payout>0);
});
