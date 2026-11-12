// A2 *source-tree* offline cache; dist/sw.js is generated independently by build.py.
// Never share the old V1 cache name with the experimental source laboratory.
const CACHE='kin-moto-a2-source-v056-20261105';
const FILES=[
 './','./index.html','./style.css',
 './src/road_surface.js','./src/math.js','./src/navigation.js',
 './src/route_guidance.js','./src/ride_quality.js','./src/adaptive_resolution.js',
 './src/geom.js','./src/bike_physics.js','./src/collision.js',
 './src/sim.js','./src/render.js','./src/main.js',
 './manifest.webmanifest','./assets/icon.svg'
];
// PNG icons are reconstructed by build.py; source repo stores their .base64 text.
// Including non-existent PNG files here would make addAll reject the entire install.
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)));
 // Do not force an update in the middle of an active mission.
});
self.addEventListener('activate',event=>{
 event.waitUntil(caches.keys().then(keys=>Promise.all(
  keys.filter(key=>key.startsWith('kin-moto-a2-source-')&&key!==CACHE).map(key=>caches.delete(key))
 )));
});
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET'||new URL(req.url).origin!==self.location.origin)return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  const key=req.mode==='navigate'?'./index.html':req;
  try{
   const response=await fetch(req);
   if(response.ok){try{await cache.put(key,response.clone());}catch{ /* storage quota is not a network failure */ }}
   return response;
  }catch(err){
   const hit=await cache.match(key,{ignoreSearch:true});
   if(hit)return hit;
   throw err;
  }
 })());
});
