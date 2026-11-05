import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeGame,step,validate} from '../src/sim.js';
import {startChallenge,CHALLENGE_GATES} from '../src/challenge.js';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');

test('V1 single HTML requires zero external CSS, JS, manifest and icon resources',()=>{
 const h=read('dist/KIN_MOTO_V1_FICHIER_UNIQUE.html');
 assert.match(h,/<style>/);assert.match(h,/<script>/);
 assert.doesNotMatch(h,/<script[^>]+src=/i);
 assert.doesNotMatch(h,/<link[^>]+href="\.\//i);
 assert.match(h,/data:image\/svg\+xml;base64,/);
 assert.match(h,/CHALLENGE_GATES/);
 assert.match(h,/KIN-MOTO-NEXT-V1-1\.0\.1-OPTIMIZED-REVIEW/);
});

test('V1 hosted PWA still offers manifest and content-hashed isolated cache',()=>{
 const html=read('dist/index.html'),sw=read('dist/sw.js');
 assert.match(html,/manifest\.webmanifest/);
 assert.match(sw,/kin-moto-next-v1-[a-f0-9]{12}/);
 assert.doesNotMatch(sw,/kin-moto-a2-lab-/);
});

test('V1 frontend includes all required mode buttons, destination and screens',()=>{
 const h=read('index.html'),m=read('src/main.js');
 for(const id of ['play','challengePlay','challengeAgain','challengeBack','challengeResult','resume','pause',
  'openGarageMenu','buyRepair','buyEngine','buyBrakes','saveButton','importSave','quality'])assert.match(h,new RegExp(`id="${id}"`));
 assert.match(m,/\$\('challengePlay'\)\.onclick=launchChallenge/);
 assert.match(m,/\$\('challengeAgain'\)\.onclick=launchChallenge/);
 assert.match(m,/challengeTarget\(game\)/);
});

test('V1 7-gate time trial finishes from actual bike driving without teleportation',()=>{
 const g=makeGame();g.playing=true;g.cars=[];startChallenge(g);
 for(let tick=0;tick<90*60&&g.challenge.active;tick++){
  const p=g.player,target=CHALLENGE_GATES[g.challenge.index];
  const dx=target.x-p.x,dz=target.z-p.z;
  const head=Math.atan2(dx,-dz),err=Math.atan2(Math.sin(head-p.yaw),Math.cos(head-p.yaw));
  const distance=Math.hypot(dx,dz),kmh=p.speed*3.6;
  const brake=(Math.abs(err)>.6&&kmh>20)||(distance<8&&Math.abs(err)>.3&&kmh>13);
  g.controls.right=err>.06;g.controls.left=err<-.06;
  g.controls.gas=!brake&&kmh<(Math.abs(err)>.5?28:47);
  g.controls.brake=brake;
  step(g,1/60);
 }
 assert.equal(g.challenge.status,'won');
 assert.ok(g.challenge.elapsed>10&&g.challenge.elapsed<70);
 assert.equal(g.challenge.index,7);assert.equal(g.challenge.stars,3);
 assert.equal(g.collisions,0);assert.deepEqual(validate(g),[]);
});
