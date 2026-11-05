import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeGame,snapshot,step,validate} from '../src/sim.js';
import {startChallenge,restoreChallengeCareer,CHALLENGE_GATES} from '../src/challenge.js';
import {Renderer} from '../src/render.js';

function setup(){const g=makeGame();g.playing=true;g.cars=[];return g;}

test('V1 skill exit restores career odometer, mileage, motorcycle wheel spin and collision totals',()=>{
 const g=setup();g.player.x=110;g.player.z=14;g.player.yaw=.37;g.player.meters=212;
 g.player.bike.wheelSpin=212/.49;g.player.bike.suspension=.12;
 g.travel=204;g.collisions=3;g.nearMisses=5;
 startChallenge(g);g.controls.gas=true;
 for(let i=0;i<360;i++)step(g,1/60);
 assert.ok(g.player.meters>212,'challenge should advance the temporary odometer');
 assert.equal(g.challenge.returnMetrics.meters,212);
 assert.equal(restoreChallengeCareer(g),true);
 assert.deepEqual({x:g.player.x,z:g.player.z,yaw:g.player.yaw},{x:110,z:14,yaw:.37});
 assert.equal(g.player.meters,212);assert.equal(g.travel,204);
 assert.equal(g.collisions,3);assert.equal(g.nearMisses,5);
 assert.equal(g.player.bike.wheelSpin,212/.49);
 assert.equal(g.player.bike.suspension,.12);
 assert.equal(g.challenge,null);assert.deepEqual(validate(g),[]);
});
test('V1 challenge saved from an interrupted mid-run returns original career location and odometer',()=>{
 const g=setup();g.player.x=33;g.player.z=-44;g.player.yaw=1.5;g.player.meters=123.456;
 const before=snapshot(g);
 startChallenge(g);g.controls.gas=true;
 for(let i=0;i<300;i++)step(g,1/60);
 const during=snapshot(g);
 assert.deepEqual(during.player,before.player);
 assert.deepEqual(during.mission,before.mission);
 assert.equal(during.save.cash,before.save.cash);
 assert.deepEqual(validate(makeGame(during)),[]);
});
test('V1 challenge retries preserve original checkpoint across multiple launches',()=>{
 const g=setup();g.player.x=60;g.player.z=90;g.player.meters=84;
 startChallenge(g);g.controls.gas=true;
 for(let i=0;i<240;i++)step(g,1/60);
 startChallenge(g);assert.equal(g.challenge.returnMetrics.meters,84);
 assert.equal(g.challenge.returnPlayer.x,60);
 restoreChallengeCareer(g);assert.equal(g.player.meters,84);
});
test('V1 challenge finish retains new high-score payout after returning to original career',()=>{
 const g=setup(),oldCash=g.save.cash;
 startChallenge(g);
 for(const pt of CHALLENGE_GATES){g.player.x=pt.x;g.player.z=pt.z;step(g,1/60);}
 assert.equal(g.challenge.status,'won');assert.equal(g.save.cash,oldCash+450);
 const record=g.save.highScore;
 restoreChallengeCareer(g);
 assert.equal(g.save.cash,oldCash+450);assert.equal(g.save.highScore,record);
});
test('V1 cached renderer projection is rebuilt only if viewport or pixel resolution changes',()=>{
 const innerW=globalThis.innerWidth,innerH=globalThis.innerHeight,dpr=globalThis.devicePixelRatio;
 let viewportCalls=0;
 const fake={quality:'eco',dynamic:{scale:1},canvas:{width:300,height:150},gl:{viewport(){viewportCalls++}}};
 try{
  globalThis.innerWidth=393;globalThis.innerHeight=852;globalThis.devicePixelRatio=2;
  Renderer.prototype.resize.call(fake);assert.equal(fake.projectionRebuilds,1);
  const proj=fake.proj;
  for(let i=0;i<500;i++)Renderer.prototype.resize.call(fake);
  assert.equal(fake.projectionRebuilds,1);
  assert.equal(fake.proj,proj);
  globalThis.innerWidth=852;globalThis.innerHeight=393;
  Renderer.prototype.resize.call(fake);
  assert.equal(fake.projectionRebuilds,2);
  assert.notEqual(fake.proj,proj);
  assert.equal(viewportCalls,2);
 }finally{globalThis.innerWidth=innerW;globalThis.innerHeight=innerH;globalThis.devicePixelRatio=dpr;}
});
test('V1 WebGL vertex attributes are enabled only at renderer initialization',()=>{
 const render=fs.readFileSync(new URL('../src/render.js',import.meta.url),'utf8');
 assert.equal((render.match(/gl\.enableVertexAttribArray\(/g)||[]).length,1);
 assert.match(render,/for\(const idx of Object\.values\(this\.attr\)\)gl\.enableVertexAttribArray/);
 assert.match(render,/projectionRebuilds:/);
});
test('V1 minimap prerenders static road and POI layer once',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/minimapBase=cv;mapBackgroundBuilds\+\+/);
 assert.match(main,/ctx\.drawImage\(minimapBackground\(\),0,0,w,h\)/);
 assert.match(main,/ui:\{minimapBackgroundBuilds:mapBackgroundBuilds\}/);
});
test('V1 iOS JavaScript compatibility avoids Array.at and offscreen canvas requirement',()=>{
 for(const file of ['src/main.js','src/adaptive_resolution.js']){
  const source=fs.readFileSync(new URL('../'+file,import.meta.url),'utf8');
  assert.doesNotMatch(source,/\.at\(-1\)/);
 }
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.doesNotMatch(main,/new OffscreenCanvas/);
 assert.match(main,/document\.createElement\('canvas'\)/);
});
test('V1 WebGL failure provides an explicit Eco-mode recovery without switching to 2D',()=>{
 const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(html,/id="retryEco"/);
 assert.match(main,/\$\('retryEco'\)\.onclick=/);
 assert.match(main,/kinmoto_a2_lab_quality','eco'/);
});
test('V1 skill-only riding never renders a seated career passenger',()=>{
 const source=fs.readFileSync(new URL('../src/render.js',import.meta.url),'utf8');
 assert.match(source,/g\.challenge\?this\.mesh\.bike:g\.mission\.stage/);
});
test('V1 mobile save export includes native file-share capability and download fallback',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
 assert.match(main,/navigator\.share&&navigator\.canShare/);
 assert.match(main,/new File\(\[content\],filename/);
 assert.match(main,/a\.download='KIN_MOTO_V1_SAUVEGARDE\.json'/);
 assert.match(html,/SAUVEGARDER \/ PARTAGER/);
});
test('V1 incompatible persistent storage is detected rather than falsely claiming save persistence',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/function isStorageAvailable/);
 assert.match(main,/exporte régulièrement ta sauvegarde/);
 assert.match(main,/persistentStorage,mode:renderer/);
});
test('V1 completed challenge cannot be unpaused behind its result overlay',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/game\.challenge&&game\.challenge\.status!=='running'/);
});
