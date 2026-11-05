import test from 'node:test';
import assert from 'node:assert/strict';
import {FixedStepScheduler} from '../src/adaptive_resolution.js';
import {makeGame,step,validate} from '../src/sim.js';
import fs from 'node:fs';

const runAtFps=(fps,seconds=5)=>{
 const game=makeGame();game.cars=[];game.playing=true;game.controls.gas=true;
 const scheduler=new FixedStepScheduler();
 for(let i=0;i<fps*seconds;i++)scheduler.advance(1/fps,dt=>step(game,dt));
 return {game,scheduler};
};

for(const fps of [60,30,10,5,3,2]){
 test(`simulation keeps real-time 60Hz clock at ${fps} actual FPS`,()=>{
  const {game,scheduler}=runAtFps(fps);
  assert.ok(Math.abs(game.clock-5)<1e-7,`FPS ${fps}: sim time ${game.clock} versus 5 seconds`);
  assert.equal(game.stats.steps,300);
  assert.equal(scheduler.ticks,300);
  assert.ok(Math.abs(game.player.meters-66.979281) < .03);
  assert.deepEqual(validate(game),[]);
 });
}

test('one-second visible frame is deliberately bounded to 30 fixed physics ticks',()=>{
 const scheduler=new FixedStepScheduler();let count=0;
 const ticks=scheduler.advance(1,dt=>{count++;assert.equal(dt,1/60)});
 assert.equal(ticks,30);assert.equal(count,30);
 assert.ok(Math.abs(scheduler.droppedSeconds-.5)<1e-8);
});

test('five seconds of page suspension never cause a teleport or catch-up storm',()=>{
 const scheduler=new FixedStepScheduler();let count=0;
 scheduler.advance(1/60,()=>count++);
 scheduler.advance(5,()=>count++,{active:false});
 const ticks=scheduler.advance(1/60,()=>count++);
 assert.equal(ticks,1);assert.equal(count,2);
});

test('at 1 FPS catch-up remains bounded and explicitly reports discarded time',()=>{
 const {game,scheduler}=runAtFps(1);
 assert.ok(Math.abs(game.clock-2.5)<1e-7);
 assert.equal(scheduler.ticks,150);
 assert.ok(Math.abs(scheduler.droppedSeconds-2.5)<1e-7);
});

test('invalid elapsed times cannot overflow the frame scheduler',()=>{
 const s=new FixedStepScheduler();let ticks=0;
 for(const dt of [NaN,Infinity,-Infinity,-1])s.advance(dt,()=>ticks++);
 assert.equal(ticks,0);assert.equal(s.ticks,0);
});

test('invalid scheduler tick budgets fail at construction',()=>{
 for(const options of [{fixed:0},{maxFrame:.5,maxSteps:10},{maxSteps:0},{maxFrame:NaN}]){
  assert.throws(()=>new FixedStepScheduler(options));
 }
});

test('browser routes untruncated elapsed time into the physics scheduler',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/physicsClock\.advance\(frameSeconds,fixed=>step\(game,fixed\),\{active:isSimulating\}\)/);
 assert.match(main,/const isSimulating=game\.playing&&!game\.paused&&!document\.hidden/);
 assert.match(main,/collisionCount:game\.collisions,physics:/);
});
