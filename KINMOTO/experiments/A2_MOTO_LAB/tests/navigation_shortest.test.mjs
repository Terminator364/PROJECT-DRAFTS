import test from 'node:test';
import assert from 'node:assert/strict';
import {findRoute} from '../src/navigation.js';
const dist=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
for(const z of [10,25,80,140,-80,-140]){
 test('same vertical road: 10 m remains 10 m, z='+z,()=>{
  const r=findRoute({x:0,z},{x:0,z:z+10});
  assert.ok(Math.abs(r.length-10)<1e-7,JSON.stringify(r));
 });
}
for(const z of [0,120,-120]){
 test('same horizontal road: 20 m remains 20 m, z='+z,()=>{
  const r=findRoute({x:20,z},{x:40,z});
  assert.ok(Math.abs(r.length-20)<1e-7,JSON.stringify(r));
 });
}
test('routing uses streets rather than diagonally crossing buildings',()=>{
 const a={x:4,z:95},b={x:109,z:-13},r=findRoute(a,b);
 assert.ok(r.length>dist(a,b));assert.ok(r.nodes.length>=3);
});
test('all current named mission locations remain reachable',()=>{
 const ps=[{x:13,z:12},{x:13,z:-73},{x:-13,z:64},{x:109,z:13},{x:-108,z:-13},{x:13,z:157},{x:109,z:-13},{x:-13,z:-78},{x:14,z:78}];
 for(const a of ps)for(const b of ps){
  const r=findRoute(a,b);
  assert.ok(Number.isFinite(r.length));
  assert.ok(r.length>=dist(a,b)-1e-7);
  assert.ok(r.nodes.length>=2);
 }
});
test('interior road segments remain axis-aligned',()=>{
 for(let k=0;k<250;k++){
  const a={x:0,z:-175+350*k/250},b={x:-120,z:170-340*k/250},r=findRoute(a,b);
  for(let i=2;i<r.nodes.length-1;i++){
   const v=r.nodes[i-1],w=r.nodes[i];
   assert.ok(Math.abs(v.x-w.x)<1e-7||Math.abs(v.z-w.z)<1e-7,JSON.stringify(r));
  }
 }
});
test('1,500 random routes: symmetry, Euclidean lower bound, determinism',()=>{
 let seed=9281;const rand=()=>((seed=(seed*1664525+1013904223)>>>0)/4294967296);
 for(let i=0;i<1500;i++){
  const a={x:-180+360*rand(),z:-180+360*rand()},b={x:-180+360*rand(),z:-180+360*rand()};
  const r=findRoute(a,b),back=findRoute(b,a),again=findRoute(a,b);
  assert.ok(r.length>=dist(a,b)-1e-7,JSON.stringify({a,b,r}));
  assert.ok(Math.abs(r.length-back.length)<1e-6,JSON.stringify({a,b,r,back}));
  assert.deepEqual(r,again);
 }
});

test('identical sidewalk destination is zero metres, not a detour to street center',()=>{
 const p={x:13,z:157};const r=findRoute(p,p);
 assert.equal(r.length,0);assert.equal(r.nodes.length,2);
});
test('pickup proximity shows one metre rather than 27 metres around a block',()=>{
 const a={x:14,z:78},b={x:13,z:78},r=findRoute(a,b);
 assert.equal(r.length,1);
});
