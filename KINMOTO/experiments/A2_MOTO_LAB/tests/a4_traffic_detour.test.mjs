import test from 'node:test';
import assert from 'node:assert/strict';
import {makeGame,step,validate} from '../src/sim.js';
import {nearestRoad} from '../src/math.js';
import {inspectBikeCar} from '../src/collision.js';

// Same stationary player/traffic scenario as the standalone baseline-vs-patch
// experiment. The original A4 car stopped forever at path coordinate ~5 m.
function blockedBike(){
 const g=makeGame();g.playing=true;
 const car=g.cars[0];g.cars=[car];
 g.player.x=car.x+.6;g.player.z=car.z-8;g.player.speed=0;g.player.yaw=0;
 return {g,car};
}
test('A4 traffic detours around a stopped bike and moves forward again',()=>{
 const {g,car}=blockedBike();let hit=0,maxJump=0,previous={x:car.x,z:car.z};
 let shifted=false,highestRoadOffset=0;
 for(let i=0;i<1200;i++){
  step(g,1/60);
  if(Math.hypot(car.avoidDX||0,car.avoidDZ||0)>.5)shifted=true;
  highestRoadOffset=Math.max(highestRoadOffset,nearestRoad(car).distance);
  hit+=+inspectBikeCar(g.player,car).hit;
  maxJump=Math.max(maxJump,Math.hypot(car.x-previous.x,car.z-previous.z));
  previous={x:car.x,z:car.z};
 }
 assert.ok(car.u>120,`stalled at u=${car.u}m rather than overtaking`);
 assert.ok(car.speed>6,`stalled at ${car.speed}m/s`);
 assert.ok(shifted,'car never moved laterally');
 assert.equal(hit,0,'passing vehicle hit stopped player');
 assert.ok(highestRoadOffset<=7.201,'the car left the safe asphalt envelope');
 assert.ok(maxJump<.22,`car teleported ${maxJump}m`);
 assert.equal(car.avoidTarget,0,'car remains in overtaking mode after passing');
 assert.ok(Math.hypot(car.avoidDX||0,car.avoidDZ||0)<1e-5,'car failed to return to normal lane');
 assert.deepEqual(validate(g),[]);
});
test('A4 traffic keeps its original route if a bike is far away',()=>{
 const {g,car}=blockedBike();g.player.x=110;g.player.z=85;
 for(let i=0;i<100;i++)step(g,1/60);
 assert.ok(!car.avoidTarget);
 assert.ok(!car.avoidDX&&!car.avoidDZ);
 assert.ok(car.u>5);
});
test('A4 overtaking does not enter an occupied adjacent lane',()=>{
 const {g,car}=blockedBike();const other=makeGame().cars[1];
 // car 0 heads along -Z with +X as its right axis. Rider is to its right,
 // so desired bypass is -2.9m sideways at x=car.x-2.9.
 other.x=car.x-2.9;other.z=car.z;other.loop=3;other.u=0;other.speed=0;
 g.cars=[car,other];
 step(g,1/60);
 assert.equal(car.avoidTarget||0,0,'passed into occupied adjacent lane');
});
test('A4 hard impact still causes real collision damage (traffic is not intangible)',()=>{
 const g=makeGame();g.playing=true;
 const car=g.cars[0];g.cars=[car];
 g.player.x=car.x;g.player.z=car.z;g.player.speed=12;g.player.yaw=0;
 step(g,1/60);
 assert.equal(g.collisions,1);
 assert.ok(g.save.health<100);
 assert.ok(g.peakContactCorrection<=.320001);
});
test('A4 repeated 20-minute virtual stress does not leave cars trapped in bike',()=>{
 const g=makeGame();g.playing=true;
 let contacts=0,maxContactEpisode=0,episode=0,maxCarJump=0,maxCarRoadDistance=0;
 const prev=g.cars.map(c=>({x:c.x,z:c.z}));
 for(let i=0;i<72000;i++){
  const t=i%960;g.controls.gas=t<580;g.controls.brake=t>=580&&t<720;
  g.controls.left=t>=140&&t<245;g.controls.right=t>=455&&t<570;
  step(g,1/60);
  let frameContact=false;
  for(let j=0;j<g.cars.length;j++){
   const car=g.cars[j];
   const delta=Math.hypot(car.x-prev[j].x,car.z-prev[j].z);
   maxCarJump=Math.max(maxCarJump,delta);prev[j].x=car.x;prev[j].z=car.z;
   maxCarRoadDistance=Math.max(maxCarRoadDistance,nearestRoad(car).distance);
   if(inspectBikeCar(g.player,car).hit)frameContact=true;
  }
  if(frameContact){contacts++;episode++;maxContactEpisode=Math.max(maxContactEpisode,episode);}
  else episode=0;
 }
 assert.deepEqual(validate(g),[]);
 assert.ok(contacts<2000,`too many persistent contact frames: ${contacts}`);
 assert.ok(maxContactEpisode<600,`persistent car/bike deadlock: ${maxContactEpisode} ticks`);
 assert.ok(maxCarJump<.40,`car jumped ${maxCarJump}m in one tick`);
 assert.ok(maxCarRoadDistance<=7.3,`traffic left asphalt: ${maxCarRoadDistance}m`);
 assert.ok(g.player.meters>100,'aggressive stress did not exercise any motion');
});
test('A4 detour is deterministic under the same inputs and traffic states',()=>{
 const run=()=>{
  const {g,car}=blockedBike();
  for(let i=0;i<900;i++)step(g,1/60);
  return {car:{x:car.x,z:car.z,u:car.u,speed:car.speed,avoidDX:car.avoidDX||0},
   collisions:g.collisions,steps:g.stats.steps,cash:g.save.cash,player:{x:g.player.x,z:g.player.z}};
 };
 assert.deepEqual(run(),run());
});

test('A4 every traffic route stays inside the asphalt corridor at all corners',async()=>{
 const {makeRoute,sampleRoute}=await import('../src/sim.js');
 const loops=[[-120,-120,0,0],[0,-120,120,0],[-120,0,0,120],[0,0,120,120]];
 for(const edges of loops){
  const route=makeRoute(...edges);
  let maxDistance=0;
  for(let u=0;u<route.length;u+=.08){
   maxDistance=Math.max(maxDistance,nearestRoad(sampleRoute(route,u)).distance);
  }
  assert.ok(maxDistance<=6.3,`road route cuts through an inaccessible block (${maxDistance}m)`);
 }
});
test('A4 route sample cache is exact through corners, wrap-around and rewinds',async()=>{
 const {makeRoute,sampleRoute}=await import('../src/sim.js');
 const g=makeGame();g.playing=true;g.player.x=110;g.player.z=95;
 const routes=[makeRoute(-120,-120,0,0),makeRoute(0,-120,120,0),makeRoute(-120,0,0,120),makeRoute(0,0,120,120)];
 for(let tick=0;tick<1800;tick++){
  step(g,1/60);
  if(tick%50!==0)continue;
  for(const car of g.cars){
   const expected=sampleRoute(routes[car.loop],car.u);
   assert.ok(Math.abs(car.x-(expected.x+(car.avoidDX||0)))<1e-9);
   assert.ok(Math.abs(car.z-(expected.z+(car.avoidDZ||0)))<1e-9);
   assert.equal(car.yaw,expected.yaw);
  }
 }
 // Source edits or imported telemetry may rewind a route coordinate; cache
 // must not continue using a segment for a future part of the road.
 g.cars[0].u=.125;step(g,1/60);
 assert.ok(g.cars[0].routeSegmentIndex===0);
});
test('A4 explicit blocked-lane route safety preserves normal car contact geometry',()=>{
 const {g,car}=blockedBike();
 for(let i=0;i<270;i++)step(g,1/60);
 const expected=inspectBikeCar(g.player,car);
 assert.equal(expected.hit,false);
 assert.ok(nearestRoad(car).distance<7.3);
 assert.ok(Math.hypot(car.avoidDX||0,car.avoidDZ||0)<3.1);
});
test('A4 car visual heading eases into the bypass without disturbing traffic collision yaw',async()=>{
 const {g,car}=blockedBike();let visibleSteer=false;
 for(let i=0;i<240;i++){
  step(g,1/60);
  assert.ok(Number.isFinite(car.visualYaw));
  assert.ok(Math.abs(Math.atan2(Math.sin(car.visualYaw-car.yaw),Math.cos(car.visualYaw-car.yaw)))<=.301);
  if(Math.abs(car.visualYaw-car.yaw)>.01)visibleSteer=true;
 }
 assert.ok(visibleSteer,'the rendered vehicle still crabs sideways without steering');
 const {readFileSync}=await import('node:fs');
 const render=readFileSync(new URL('../src/render.js',import.meta.url),'utf8');
 assert.match(render,/car\.visualYaw\?\?car\.yaw/);
});
test('A4 stationary rider can remain in one traffic lane for 20 virtual minutes without AI deadlock',()=>{
 const g=makeGame();g.playing=true;
 const anchor=g.cars[0];g.player.x=anchor.x+.6;g.player.z=anchor.z-8;
 let hitFrames=0,maxJump=0,maxRoadDistance=0,previous=g.cars.map(c=>({x:c.x,z:c.z}));
 for(let i=0;i<72000;i++){
  step(g,1/60);
  for(let j=0;j<g.cars.length;j++){
   const car=g.cars[j];
   if(inspectBikeCar(g.player,car).hit)hitFrames++;
   maxJump=Math.max(maxJump,Math.hypot(car.x-previous[j].x,car.z-previous[j].z));
   previous[j].x=car.x;previous[j].z=car.z;
   maxRoadDistance=Math.max(maxRoadDistance,nearestRoad(car).distance);
  }
 }
 assert.equal(hitFrames,0);
 assert.equal(g.collisions,0);
 assert.equal(g.contactCorrections||0,0);
 assert.equal(g.player.meters,0);
 assert.ok(maxJump<.25);
 assert.ok(maxRoadDistance<7.4);
 assert.deepEqual(validate(g),[]);
});
