import test from 'node:test';import assert from 'node:assert/strict';
import {AdaptiveResolution} from '../src/adaptive_resolution.js';
function feed(c,frames,dt,visible=true){let changed=0;for(let i=0;i<frames;i++)changed+=c.observe(dt,{visible})?1:0;return changed;}
test('sustained heavy GPU frames lower internal resolution',()=>{const r=new AdaptiveResolution({targetFps:30});feed(r,190,1/18);assert.ok(r.scale<=.84&&r.scale>=.68);});
test('healthy performance raises resolution slowly without exceeding native cap',()=>{const r=new AdaptiveResolution({targetFps:30,initialScale:.68});feed(r,450,1/55);assert.ok(r.scale>.75&&r.scale<=1);});
test('background long frame does not trigger quality changes',()=>{const r=new AdaptiveResolution();feed(r,100,.3);feed(r,100,1/10,false);assert.equal(r.scale,1);assert.equal(r.samples,0);});
test('normal 30fps retains native quality',()=>{const r=new AdaptiveResolution({targetFps:30});feed(r,600,1/30);assert.equal(r.scale,1);assert.equal(r.updates,0);});
test('quality oscillations bounded, no thrashing every frame',()=>{const r=new AdaptiveResolution({targetFps:30});for(let i=0;i<1200;i++)r.observe(i%50<25?1/20:1/52);assert.ok(r.updates<70);assert.ok(r.scale>=.68&&r.scale<=1);});
test('minimum scale respects quality preset and reset',()=>{const r=new AdaptiveResolution({targetFps:60,minScale:.85});feed(r,500,1/23);assert.ok(r.scale>=.85);r.reset();assert.equal(r.scale,1);assert.equal(r.samples,0);});

test('sustained visible 6 FPS degrades quality instead of silently ignoring slowdown',()=>{
 const r=new AdaptiveResolution({targetFps:30});
 feed(r,100,1/6,true);
 assert.ok(r.scale<.9&&r.scale>=.68);
});
test('isolated half-second foreground hitch remains excluded and does not lower quality',()=>{
 const r=new AdaptiveResolution({targetFps:30});
 feed(r,300,1/30);
 r.observe(.4,{visible:true});
 feed(r,40,1/30);
 assert.equal(r.scale,1);
});

test('render loop forwards measured wall-clock frame duration, not physics cap',async()=>{
 const fs=await import('node:fs');
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(main,/function frame\(now\)\{const frameSeconds=Math\.max\(0,\(now-prev\)\/1000\);const delta=Math\.min\(\.1,frameSeconds\)/);
 assert.match(main,/renderer\?\.render\(game,frameSeconds\)/);
 assert.match(main,/step\(game,fixed\)/);
});
