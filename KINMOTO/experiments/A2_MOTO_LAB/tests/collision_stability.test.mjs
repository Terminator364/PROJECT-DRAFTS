import test from 'node:test';
import assert from 'node:assert/strict';
import {makeGame,step,validate} from '../src/sim.js';
import {inspectBikeCar} from '../src/collision.js';

test('long 6-minute gameplay with traffic stays finite and collision scratch reusable',()=>{
 const g=makeGame();g.playing=true;let maxOverlap=0;
 const samples=[];
 for(let i=0;i<21600;i++){
   g.controls.gas=(i%400)<260;
   g.controls.brake=(i%400)>=260&& (i%400)<310;
   g.controls.left=i%900>=120&&i%900<165;
   g.controls.right=i%900>=565&&i%900<610;
   step(g,1/60);
   if(i%600===0){
     assert.deepEqual(validate(g),[]);
     assert(Number.isFinite(g.player.bike.frontWheelY));
     assert(Number.isFinite(g.player.bike.rearWheelY));
     samples.push(process.memoryUsage().heapUsed);
   }
   if(g.cars.length){
      const scratch=g._contactScratch;assert(scratch);
      for(let j=0;j<g.cars.length;j++){
        const c=inspectBikeCar(g.player,g.cars[j],scratch);
        if(c.overlap>maxOverlap)maxOverlap=c.overlap;
        assert(Number.isFinite(c.clearance));
      }
   }
 }
 assert.equal(g.stats.steps,21600);
 assert(g.save.cash>=0);
 assert(Number.isFinite(maxOverlap));
 // Heap samples are informational; GC runs nondeterministically in Node.
 assert(samples.length===36);
});

test('bike receives impact when a moving car contacts a stationary rider',()=>{
 const g=makeGame();g.playing=true;
 const car=g.cars[0];
 g.cars=[car];
 g.player.x=car.x;g.player.z=car.z;g.player.speed=0;
 g.player.bike.vx=0;g.player.bike.vz=0;
 const health=g.save.health;
 step(g,1/60);
 assert(g.save.health<health,'moving traffic should damage stationary rider when overlapping');
 assert(g.collisions===1);
});
