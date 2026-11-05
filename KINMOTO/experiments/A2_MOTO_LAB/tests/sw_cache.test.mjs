import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';

const src = fs.readFileSync(new URL('../dist/sw.js',import.meta.url),'utf8');
const html = fs.readFileSync(new URL('../dist/index.html',import.meta.url),'utf8');
const findCache = src.match(/const CACHE='(kin-moto-next-v1-[a-f0-9]{12})'/);
assert(findCache,'cache version not tied to build');
const calls = {};
const store = new Map([['kin-moto-next-v1-obsolete',new Map([['./index.html',{ok:true,body:'old'}]])],['other-app',new Map([['foo',true]])]]);
const normalized = v=>typeof v==='string'?v:(v.url.includes('/assets/')?'./assets/'+v.url.split('/assets/')[1]:'./index.html');
let online=true;let networkHits=0;
const caches = {
  async open(key){if(!store.has(key))store.set(key,new Map());const m=store.get(key);return {
    async addAll(files){for(const f of files)m.set(f,{ok:true,body:f,clone(){return {...this}}});},
    async put(req,response){m.set(normalized(req),response)},
    async keys(){return [...m.keys()]}
  }},
  async keys(){return [...store.keys()]},
  async delete(k){return store.delete(k)},
  async match(req){for(const m of store.values()){const v=m.get(normalized(req));if(v)return v;}return undefined}
};
const self={location:{origin:'https://kinmoto.test'},registration:{scope:'https://kinmoto.test/'},addEventListener(type,cb){calls[type]=cb},skipWaiting(){return Promise.resolve()},clients:{claim(){return Promise.resolve()}}};
const fetch=async req=>{networkHits++;if(!online)throw Error('network lost');return {ok:true,body:'online',clone(){return {...this}}}};
vm.runInNewContext(src,{self,caches,fetch,URL,Promise}, {filename:'sw.js'});
const waitEvents=[];
const event=()=>({waitUntil(p){waitEvents.push(Promise.resolve(p))}});
const fetchEvent=req=>{const e=event();e.request=req;e.respondWith=p=>e.answer=Promise.resolve(p);return e;};

test('SW precaches every required resource and removes only old KINMOTO caches',async()=>{
  calls.install(event());await Promise.all(waitEvents.splice(0));
  const current=store.get(findCache[1]);assert(current);assert.equal(current.size,6);
  calls.activate(event());await Promise.all(waitEvents.splice(0));
  assert(!store.has('kin-moto-next-v1-obsolete'));
  assert(store.has('other-app'));
});

test('SW serves fresh online HTML and preserves offline navigation fallback',async()=>{
  const req={url:'https://kinmoto.test/?v=latest',method:'GET',mode:'navigate'};
  const e1=fetchEvent(req);calls.fetch(e1);const a=await e1.answer;assert.equal(a.body,'online');
  await Promise.all(waitEvents.splice(0));
  online=false;
  const e2=fetchEvent(req);calls.fetch(e2);const b=await e2.answer;
  assert(b, 'no cached navigation fallback');
  assert.equal(store.get(findCache[1]).get('./index.html').body,'online');
});

test('SW serves static icons offline without making a network request',async()=>{
  const before=networkHits;const req={url:'https://kinmoto.test/assets/icon.svg',method:'GET',mode:'same-origin'};
  const e=fetchEvent(req);calls.fetch(e);const r=await e.answer;
  assert(r);assert.equal(networkHits,before);
  assert(html.includes('manifest.webmanifest'));
});
