const CACHE='kin-moto-v1-1.0.0';
const PRECACHE=['./','./index.html','./style.css','./src/main.js','./src/math.js','./src/navigation.js','./src/sim.js','./src/geom.js','./src/render.js','./manifest.webmanifest','./assets/icon.svg','./assets/icon-192.png','./assets/icon-512.png'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(async cache=>{await cache.addAll(PRECACHE)})));
self.addEventListener('activate',event=>event.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',event=>{const r=event.request;if(r.method!=='GET'||new URL(r.url).origin!==self.location.origin)return;event.respondWith(caches.match(r,{ignoreSearch:true}).then(hit=>hit||fetch(r).then(response=>{if(response.ok){const clone=response.clone();caches.open(CACHE).then(cache=>cache.put(r,clone));}return response})));});
