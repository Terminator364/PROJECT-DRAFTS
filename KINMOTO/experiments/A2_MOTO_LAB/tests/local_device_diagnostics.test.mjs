import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {DevicePerformanceRecorder} from '../src/adaptive_resolution.js';

test('does not collect measurements when paused or hidden',()=>{
 const r=new DevicePerformanceRecorder();
 assert.equal(r.record(0,{fps:60},false),false);
 assert.equal(r.samples.length,0);
});
test('records at most once per second without timer or network',()=>{
 const r=new DevicePerformanceRecorder();
 assert.equal(r.record(0,{fps:30}),true);
 assert.equal(r.record(500,{fps:10}),false);
 assert.equal(r.record(999,{fps:10}),false);
 assert.equal(r.record(1000,{fps:29}),true);
 assert.equal(r.samples.length,2);
});
test('keeps only the last 900 measurements during long sessions',()=>{
 const r=new DevicePerformanceRecorder();
 for(let i=0;i<1000;i++)r.record(i*1000,{fps:25,renderScale:.75});
 assert.equal(r.samples.length,900);
 assert.equal(r.samples[0].elapsed_ms,100000);
 assert.equal(r.samples.at(-1).elapsed_ms,999000);
});
test('summary reports FPS distribution, scale and lost simulation time',()=>{
 const r=new DevicePerformanceRecorder();
 for(const [i,fps] of [10,20,30,40,50].entries()){
  r.record(i*1000,{fps,renderScale:1-i*.1,simSeconds:i,droppedSeconds:i*.05});
 }
 const report=r.report({quality:'eco'});
 assert.equal(report.type,'KINMOTO_LOCAL_DEVICE_DIAGNOSTIC');
 assert.equal(report.summary.avgFps,30);
 assert.equal(report.summary.minFps,10);
 assert.equal(report.summary.maxFps,50);
 assert.equal(report.summary.minRenderScale,.6);
 assert.equal(report.summary.droppedSimSeconds,.2);
 assert.equal(report.meta.quality,'eco');
});
test('missing or invalid browser metrics remain null rather than corrupt report',()=>{
 const r=new DevicePerformanceRecorder();
 r.record(0,{fps:NaN,renderScale:-1,jsHeapBytes:Infinity});
 const sample=r.report().samples[0];
 assert.equal(sample.fps,null);assert.equal(sample.renderScale,null);
 assert.equal(sample.jsHeapBytes,null);
 assert.equal(r.report().summary.avgFps,null);
});
test('reports do not expose game cash, passenger, GPS or account fields',()=>{
 const r=new DevicePerformanceRecorder();r.record(0,{fps:45});
 const output=JSON.stringify(r.report({version:'draft'}));
 for(const field of ['cash','passenger','accountId','latitude','longitude','wallet']){
  assert.ok(!output.includes('"'+field+'"'));
 }
});
test('report returns detached samples so consumers cannot mutate recording',()=>{
 const r=new DevicePerformanceRecorder();r.record(0,{fps:45});
 const exported=r.report();exported.samples[0].fps=3;
 assert.equal(r.samples[0].fps,45);
});
test('invalid sample budgets are rejected',()=>{
 assert.throws(()=>new DevicePerformanceRecorder({intervalMs:10}));
 assert.throws(()=>new DevicePerformanceRecorder({maxSamples:0}));
});
test('pause screen and frame loop wire opt-in local export without server calls',()=>{
 const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
 const main=fs.readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
 assert.match(html,/id="exportTechReport"/);
 assert.match(main,/\$\('exportTechReport'\)\.onclick=exportTechnicalReport/);
 assert.match(main,/deviceRecorder\.shouldSample\(now,game\.playing&&!game\.paused&&!document\.hidden&&!!renderer\)/);
 assert.match(main,/JSON\.stringify\(report,null,2\)/);
 assert.match(main,/a\.download='KINMOTO_RAPPORT_APPAREIL_'/);
});
