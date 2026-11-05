import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {IdleFrameGate} from '../src/adaptive_resolution.js';

test('menu displays immediately on first frame',()=>{
 const g=new IdleFrameGate();assert.equal(g.shouldRender(0,{active:false}),true);
});
test('idle drawing is bounded to roughly eight frames per second',()=>{
 const g=new IdleFrameGate();let draws=0;
 for(let i=0;i<=120;i++)draws+=Number(g.shouldRender(i*1000/60,{active:false}));
 assert.ok(draws>=15&&draws<=18,'unexpected idle draw count '+draws);
});
test('active gameplay draws every visible animation frame',()=>{
 const g=new IdleFrameGate();for(let i=0;i<500;i++)assert.equal(g.shouldRender(i*16,{active:true}),true);
});
test('hidden documents never draw, regardless of playback',()=>{
 const g=new IdleFrameGate();
 for(let i=0;i<150;i++)assert.equal(g.shouldRender(i*16,{visible:false,active:true}),false);
});
test('resume from pause draws immediately',()=>{
 const g=new IdleFrameGate();g.shouldRender(1000,{active:false});
 assert.equal(g.shouldRender(1010,{active:true}),true);
});
test('clock discontinuity does not permanently suppress menu redraw',()=>{
 const g=new IdleFrameGate();g.shouldRender(1000,{active:false});
 assert.equal(g.shouldRender(100,{active:false}),true);
});
test('reset restarts the idle cadence',()=>{
 const g=new IdleFrameGate();g.shouldRender(1000,{active:false});g.reset();
 assert.equal(g.shouldRender(1001,{active:false}),true);
});
test('invalid clock values are not treated as animation frames',()=>{
 const g=new IdleFrameGate();assert.equal(g.shouldRender(NaN),false);assert.equal(g.shouldRender(Infinity),false);
});
test('invalid idle intervals are rejected',()=>{
 assert.throws(()=>new IdleFrameGate(0));assert.throws(()=>new IdleFrameGate(-10));
});
test('runtime wires the gate to renderer and excludes idle frames from FPS adaptation',()=>{
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 const render=fs.readFileSync(new URL('../src/render.js',import.meta.url),'utf8');
 assert.match(main,/idleFrameGate\.shouldRender\(now,\{active,visible:!document\.hidden\}\)/);
 assert.match(main,/renderer\?\.render\(game,active\?frameSeconds:1\/60,active\)/);
 assert.match(render,/visible:foreground&&active/);
 assert.match(render,/else \{this\.frames=0;this\.seconds=0;\}/);
});
