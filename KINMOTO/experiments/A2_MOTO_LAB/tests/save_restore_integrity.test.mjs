import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeGame,snapshot,validate,readSave,SAVE_KEY} from '../src/sim.js';

const corrupt=change=>{const s=snapshot(makeGame());change(s);return makeGame(s);};
const store=payload=>({getItem:k=>k===SAVE_KEY?JSON.stringify(payload):null});

test('corrupt text rating is rejected before HUD calls toFixed()',()=>{
 const g=corrupt(s=>s.save.stars='not a number');
 assert.ok(validate(g).includes('non-finite'));
 assert.ok(validate(g).includes('invalid-stars'));
});
test('negative health is not an acceptable saved state',()=>{
 const g=corrupt(s=>s.save.health=-200);
 assert.ok(validate(g).includes('invalid-health'));
});
test('invalid mission reward cannot break next payout',()=>{
 const g=corrupt(s=>s.mission.reward='oops');
 assert.ok(validate(g).includes('invalid-reward'));
});
test('unknown mission stage cannot silently make mission impossible to finish',()=>{
 const g=corrupt(s=>s.mission.stage='abandoned');
 assert.ok(validate(g).includes('invalid-mission'));
});
test('manually embedded incomplete bike telemetry is rejected before physics runs',()=>{
 const g=corrupt(s=>s.player.bike={});
 assert.ok(validate(g).includes('invalid-bike-telemetry'));
});
test('corrupted ride counters and upgrades cannot enter the game',()=>{
 const g=corrupt(s=>{s.save.rides='bad';s.save.engine=200;s.save.brakes=-4});
 assert.ok(validate(g).includes('invalid-counters'));
 assert.ok(validate(g).includes('invalid-upgrades'));
});
test('corrupt persisted optional values are normalized rather than converted to NaN',()=>{
 const value=readSave(store({schema:1,cash:4000,stars:'oops',health:-200,rides:'bad',engine:'3',brakes:null}));
 assert.equal(value.cash,4000);
 assert.equal(value.stars,4.5);
 assert.equal(value.health,0);
 assert.equal(value.rides,0);
 assert.equal(value.engine,1);
 assert.equal(value.brakes,1);
 assert.deepEqual(validate(makeGame({save:value})),[]);
});
test('old persistent upgrade level 5 is clamped to actual max level 4',()=>{
 const value=readSave(store({schema:1,cash:12000,engine:5,brakes:5}));
 assert.equal(value.engine,4);assert.equal(value.brakes,4);
});
test('missing and malformed stored saves fall back to a valid new career',()=>{
 for(const x of [null,{schema:1,cash:'bad'}, {schema:2,cash:3500}]){
  const value=readSave(store(x));const g=makeGame({save:value});
  assert.deepEqual(validate(g),[]);
 }
});
test('a genuine legacy snapshot still restores valid progress without optional bike telemetry',()=>{
 const original=makeGame();original.save.cash=9888;original.save.stars=3.9;original.player.x=7;
 const restored=makeGame(snapshot(original));
 assert.deepEqual(validate(restored),[]);
 assert.equal(restored.player.x,7);
 assert.equal(restored.save.cash,9888);
 assert.equal(restored.save.stars,3.9);
});
test('startup and manual import both validate snapshots before changing game',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/const restored=makeGame\(saved\);if\(validate\(restored\)\.length===0\)game=restored/);
 assert.match(main,/if\(validate\(restored\)\.length\)throw Error\('Sauvegarde incohérente'\)/);
});
