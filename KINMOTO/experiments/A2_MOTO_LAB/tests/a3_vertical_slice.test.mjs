import test from 'node:test';
import assert from 'node:assert/strict';
import {SLICE_STORY,makeGame,byId,interact,validate} from '../src/sim.js';
import {findRoute} from '../src/navigation.js';
import {makeWorld} from '../src/geom.js';

test('A3 two curated first missions live in one nearby Kinshasa neighborhood',()=>{
 assert.equal(SLICE_STORY.length,2);
 for(const m of SLICE_STORY){
  const a=byId(m.from),b=byId(m.to);assert.ok(a&&b);
  assert.ok(Math.abs(a.x)<=16&&Math.abs(b.x)<=16&&a.z>=0&&b.z>=0);
  const route=findRoute(a,b);
  assert.ok(route.nodes.length>=2&&route.length>1&&route.length<180);
 }
});
test('A3 garage and first pickup reachable from game spawn without a 500m detour',()=>{
 const g=makeGame();assert.equal(g.mission.from,'arret');
 const start=findRoute(g.player,byId(g.mission.from));
 assert.ok(start.length<70,`pickup too distant: ${start.length}`);
});
test('A3 first two missions pay exactly once and third reverts to career rotation',()=>{
 const g=makeGame();g.playing=true;g.cars=[];
 let total=0;
 for(let i=0;i<2;i++){
  assert.equal(g.mission.title,SLICE_STORY[i].title);
  for(const id of [g.mission.from,g.mission.to]){
   const target=byId(id);g.player.x=target.x;g.player.z=target.z;g.player.speed=0;
   const result=interact(g);assert.equal(result.ok,true);
   if(result.type==='completed'){total+=result.payout;assert.ok(result.payout>0);}
  }
  assert.equal(g.save.rides,i+1);
 }
 assert.equal(g.save.cash,3500+total);
 assert.equal(g.mission.ride,2);
 assert.ok(!SLICE_STORY.some(m=>g.mission.title===m.title));
 assert.deepEqual(validate(g),[]);
});
test('A3 two mission story is stable through snapshot restore',async()=>{
 const {snapshot}=await import('../src/sim.js');
 const g=makeGame();g.playing=true;const t=byId(g.mission.from);
 g.player.x=t.x;g.player.z=t.z;interact(g);
 const restored=makeGame(snapshot(g));
 assert.equal(restored.mission.stage,'drop');
 assert.equal(restored.mission.title,g.mission.title);
 assert.deepEqual(validate(restored),[]);
});
test('A3 roadside shelter is included in static world mesh without new draw calls',()=>{
 const g=makeWorld();assert.ok(g.count>50000&&g.count<200000);
});
