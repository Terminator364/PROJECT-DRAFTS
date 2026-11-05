import test from 'node:test';
import assert from 'node:assert/strict';
import {makeGame,step,interact,byId,validate,snapshot,VIP_STORY} from '../src/sim.js';
import {startChallenge,advanceChallenge,challengeTarget,CHALLENGE_GATES,CHALLENGE_LIMIT_SECONDS} from '../src/challenge.js';

function setup(){const g=makeGame();g.playing=true;g.cars=[];return g;}
function finishPickupDrop(g){for(const id of [g.mission.from,g.mission.to]){const t=byId(id);g.player.x=t.x;g.player.z=t.z;g.player.speed=0;const r=interact(g);assert.ok(r.ok);}}

test('V1 has distinct taxi, parcel, timed skill and special VIP customer activities',()=>{
 const g=setup();assert.equal(g.mission.kind,'taxi');finishPickupDrop(g);
 assert.equal(g.mission.kind,'colis');finishPickupDrop(g);
 assert.equal(g.mission.kind,'vip');assert.equal(g.mission.client,VIP_STORY.client);
 assert.equal(CHALLENGE_GATES.length,7);
 assert.ok(CHALLENGE_LIMIT_SECONDS>60);
});

test('V1 VIP extra bonus requires comfort, punctuality and zero impacts',()=>{
 const a=setup();a.save.rides=2;a.mission={...a.mission,...VIP_STORY,stage:'drop',timer:40,comfort:100,impacts:0,penalty:0};
 const b=setup();b.save.rides=2;b.mission={...a.mission,comfort:38,impacts:1,timer:140};
 const t=byId(a.mission.to);for(const g of [a,b]){g.player.x=t.x;g.player.z=t.z;g.player.speed=0;}
 const ra=interact(a),rb=interact(b);
 assert.ok(ra.ok&&rb.ok);assert.ok(ra.payout>rb.payout+700,`${ra.payout} vs ${rb.payout}`);
 assert.equal(a.save.rides,3);assert.equal(b.save.rides,3);
 assert.deepEqual(validate(a),[]);assert.deepEqual(validate(b),[]);
});

test('V1 challenge starts at correct playable road with seven sequential gates',()=>{
 const g=setup();const before=snapshot(g),oldCash=g.save.cash;
 const c=startChallenge(g);assert.equal(c.status,'running');assert.equal(c.index,0);
 assert.deepEqual(challengeTarget(g),CHALLENGE_GATES[0]);
 for(let i=0;i<CHALLENGE_GATES.length;i++){
  const pt=CHALLENGE_GATES[i];g.player.x=pt.x;g.player.z=pt.z;
  step(g,1/60);
  assert.equal(g.challenge.index,i+1);
 }
 assert.equal(g.challenge.status,'won');assert.equal(g.challenge.stars,3);
 assert.ok(g.save.highScore>0);assert.equal(g.save.cash,oldCash+450);
 assert.equal(g.save.rides,before.save.rides);
 assert.deepEqual(g.mission,before.mission);
 assert.deepEqual(validate(g),[]);
});

test('V1 challenge reward is paid only on a strictly improved high score',()=>{
 const g=setup();
 const run=()=>{startChallenge(g);for(const pt of CHALLENGE_GATES){g.player.x=pt.x;g.player.z=pt.z;step(g,1/60);}return g.challenge.paid;};
 assert.equal(run(),450);const cash=g.save.cash;assert.equal(run(),0);assert.equal(g.save.cash,cash);
});

test('V1 challenge can time out and never changes career rides or wallet',()=>{
 const g=setup();const initial=snapshot(g);startChallenge(g);
 const result=advanceChallenge(g,CHALLENGE_LIMIT_SECONDS+.5);
 assert.equal(result.type,'timeout');assert.equal(g.challenge.active,false);
 assert.equal(g.challenge.status,'timeout');assert.equal(g.save.cash,initial.save.cash);
 assert.equal(g.save.rides,initial.save.rides);
 assert.deepEqual(g.mission,initial.mission);
});

test('V1 challenge does not advance while game is paused or hidden from gameplay',()=>{
 const g=setup();startChallenge(g);g.paused=true;
 for(let i=0;i<200;i++)step(g,1/60);
 assert.equal(g.challenge.elapsed,0);g.paused=false;step(g,1/60);
 assert.ok(g.challenge.elapsed>0);
});

test('V1 skill trial does not change passenger comfort nor impose mission penalties',()=>{
 const g=setup(),mission=snapshot(g).mission;startChallenge(g);g.controls.gas=true;
 for(let i=0;i<300;i++)step(g,1/60);
 assert.equal(g.mission.penalty,mission.penalty);assert.equal(g.mission.comfort,mission.comfort);
 assert.ok(g.player.meters>1);
 assert.deepEqual(validate(g),[]);
});

test("V1 challenge target always lies on the game's accessible asphalt network",async()=>{
 const {nearestRoad}=await import('../src/math.js');
 for(const p of CHALLENGE_GATES)assert.ok(nearestRoad(p).distance<8.0,`${p.name} inaccessible`);
});

test('V1 snapshot excludes temporary trial and preserves existing version-1 save schema',()=>{
 const g=setup();startChallenge(g);const s=snapshot(g);
 assert.equal(s.schema,1);assert.ok(!('challenge' in s));
 assert.deepEqual(validate(makeGame(s)),[]);
});

test('V1 skill points cannot be awarded by replaying the same gate repeatedly',()=>{
 const g=setup();startChallenge(g);const a=CHALLENGE_GATES[0];
 g.player.x=a.x;g.player.z=a.z;advanceChallenge(g,1/60);const firstScore=g.challenge.score;
 for(let k=0;k<20;k++)advanceChallenge(g,1/60);
 assert.equal(g.challenge.index,1);assert.equal(g.challenge.score,firstScore);
});

test('V1 restarting a skill run preserves original career location for returning home',()=>{
 const g=setup();g.player.x=111;g.player.z=7;g.player.yaw=1.2;
 startChallenge(g);assert.deepEqual(g.challenge.returnPlayer,{x:111,z:7,yaw:1.2});
 g.player.x=CHALLENGE_GATES[2].x;g.player.z=CHALLENGE_GATES[2].z;
 startChallenge(g);assert.deepEqual(g.challenge.returnPlayer,{x:111,z:7,yaw:1.2});
});

test('V1 special customer race timer really runs when passenger is onboard',()=>{
 const g=setup();g.save.rides=2;g.mission={...g.mission,...VIP_STORY,stage:'drop',timer:0};
 for(let i=0;i<600;i++)step(g,1/60);
 assert.ok(g.mission.timer>=9.9,`VIP timer did not advance: ${g.mission.timer}`);
});
