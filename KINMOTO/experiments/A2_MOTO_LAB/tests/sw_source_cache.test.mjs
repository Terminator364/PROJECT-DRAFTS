import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const src=fs.readFileSync(new URL('../sw.js',import.meta.url),'utf8');
const events={},stores=new Map([['other-app',new Map([['keep',true]])],['kin-moto-a2-lab-abcdef000111',new Map([['keep',true]])],['kin-moto-a2-source-obsolete',new Map()]]);
const norm=x=>typeof x==='string'?x:x.url.replace('https://kinmoto.test/','./').split('?')[0];
let online=true;
const caches={open:async name=>{
 if(!stores.has(name))stores.set(name,new Map());const m=stores.get(name);return {
 addAll:async arr=>{for(const u of arr)m.set(u,{body:u,ok:true,clone(){return {...this}}});},
 put:async (req,r)=>m.set(norm(req),r),match:async req=>m.get(norm(req)),
 keys:async()=>[...m.keys()]
 };},keys:async()=>[...stores.keys()],delete:async name=>stores.delete(name)};
const self={location:{origin:'https://kinmoto.test'},addEventListener:(name,cb)=>events[name]=cb};
const fetch=async req=>{if(!online)throw Error('offline');return {body:'network',ok:true,clone(){return {...this}}}};
vm.runInNewContext(src,{self,caches,fetch,URL,Promise},{filename:'sw.js'});
function evt(){return {waitUntil(p){this.p=Promise.resolve(p)},respondWith(p){this.answer=Promise.resolve(p)}};}
test('install caches all 12 modules, does not request source PNGs that are absent',async()=>{
 const e=evt();events.install(e);await e.p;
 const m=stores.get('kin-moto-a2-source-v056-20261105');assert(m);assert.equal(m.size,17);
 for(const name of ['road_surface','math','navigation','route_guidance','ride_quality','adaptive_resolution','geom','bike_physics','collision','sim','render','main'])assert(m.has('./src/'+name+'.js'));
 assert(!m.has('./assets/icon-192.png'));
});
test('activation cannot delete dist cache or unrelated apps',async()=>{
 const e=evt();events.activate(e);await e.p;
 assert(stores.has('kin-moto-a2-source-v056-20261105'));assert(!stores.has('kin-moto-a2-source-obsolete'));
 assert(stores.has('other-app'));assert(stores.has('kin-moto-a2-lab-abcdef000111'));
});
test('offline navigation and nested modules use current source cache only',async()=>{
 online=false;
 for(const req of [{url:'https://kinmoto.test/?qa=1',method:'GET',mode:'navigate'},{url:'https://kinmoto.test/src/collision.js',method:'GET',mode:'same-origin'}]){
  const e=evt();e.request=req;events.fetch(e);const r=await e.answer;assert(r&&r.ok,JSON.stringify(req));
 }
});
test('cross-origin and non-GET traffic is not intercepted',()=>{
 const a=evt();a.request={url:'https://analytics.example.test/',method:'GET',mode:'no-cors'};events.fetch(a);assert(!a.answer);
 const b=evt();b.request={url:'https://kinmoto.test/submit',method:'POST'};events.fetch(b);assert(!b.answer);
});
