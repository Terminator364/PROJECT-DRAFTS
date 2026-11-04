import test from 'node:test';
import assert from 'node:assert/strict';
import {SPEED_BUMPS,ROAD_TOP_Y,smoothBump,sampleRoadSurface} from '../src/road_surface.js';
import {advanceBike,createBikeTelemetry} from '../src/bike_physics.js';
import {makeWorld} from '../src/geom.js';
const STEP=1/60, RADIUS=.49;
const go=(bike,input,n)=>{for(let i=0;i<n;i++)advanceBike(bike,input,STEP);return bike};
function tireBottom(p,t,z){const body=-.045+t.suspension,cp=Math.cos(t.pitch),sp=Math.sin(t.pitch),cr=Math.cos(p.lean);
 const y=(z>0?t.frontWheelY:t.rearWheelY);return body+cr*(y*cp-z*sp)-RADIUS;
}
test('surface bump is continuous, bounded and returns exact flat road',()=>{
 assert.equal(SPEED_BUMPS.length,3);
 for(const b of SPEED_BUMPS){
  let h=b.axis==='z'?sampleRoadSurface(b.road,b.along):sampleRoadSurface(b.along,b.road);
  assert.ok(Math.abs(h-ROAD_TOP_Y-b.height)<1e-9);
  assert.equal(smoothBump(b.halfLength,b.halfLength),0);
  for(let i=-500;i<=500;i++){
   const pos=b.along+b.halfLength*i/500;
   const v=b.axis==='z'?sampleRoadSurface(b.road,pos):sampleRoadSurface(pos,b.road);
   assert.ok(v>=ROAD_TOP_Y-1e-9 && v<ROAD_TOP_Y+.2);
  }
 }
 assert.equal(sampleRoadSurface(0,100),ROAD_TOP_Y);
});
test('wheel centers remain grounded on sloped profile even when bike leans',()=>{
 for(const steer of [0,-.2,.35,1]){
  let p={x:0,z:46,yaw:0,lean:0,speed:5,bike:createBikeTelemetry()};
  // Ride toward visible bump at z=39 from z=46.
  for(let k=0;k<185;k++){
   advanceBike(p,{gas:0,brake:0,steer},STEP);
   const t=p.bike;
   for(const [z,height] of [[1.08,t.frontHeight],[-1.10,t.rearHeight]]){
     assert.ok(Math.abs(tireBottom(p,t,z)-height)<1e-7,
       `wheel not grounded: steer=${steer}, k=${k}, wheel=${z}`);
   }
   for(const v of [t.frontWheelY,t.rearWheelY,t.suspension,t.pitch,t.lean])assert.ok(Number.isFinite(v));
  }
 }
});
test('speed bump physically drives the chassis spring instead of fake camera noise',()=>{
 let p={x:0,z:48,yaw:0,lean:0,speed:6,bike:createBikeTelemetry()};
 let maxBody=0,maxGrade=0,minHeight=0.025,last=0;
 for(let i=0;i<230;i++){
  advanceBike(p,{gas:0,brake:0,steer:0},STEP);
  let t=p.bike;maxBody=Math.max(maxBody,t.suspension);
  maxGrade=Math.max(maxGrade,Math.abs(t.roadGrade));
  minHeight=Math.min(minHeight,t.frontHeight,t.rearHeight);
  assert.ok(Math.abs(t.suspension-last)<.05);
  last=t.suspension;
 }
 assert.ok(maxBody>.012,`suspension didn't move ${maxBody}`);
 assert.ok(maxGrade>.02,`grade never computed ${maxGrade}`);
 assert.ok(minHeight>=ROAD_TOP_Y);
});
test('off-road path remains flat and does not invent bumps',()=>{
 assert.equal(sampleRoadSurface(35,39),ROAD_TOP_Y);
 assert.equal(sampleRoadSurface(0,70),ROAD_TOP_Y);
 assert.equal(sampleRoadSurface(0,-39),ROAD_TOP_Y);
});
test('3D world mesh contains enough triangles for bump stripes',()=>{
 let m=makeWorld();assert.ok(m.count>10000);assert.ok(m.a.every(Number.isFinite));
});
