from pathlib import Path
import re,shutil,zipfile,hashlib,json,base64
ROOT=Path(__file__).parent
SOURCES=['src/math.js','src/navigation.js','src/geom.js','src/bike_physics.js','src/sim.js','src/render.js','src/main.js']
# Binary icons are also committed as base64 text to allow entirely text-only GitHub
# syncing through the connector. The generated PNGs are identical to the originals.
for icon_size in (192,512):
    png=ROOT/'assets'/f'icon-{icon_size}.png'
    source=ROOT/'assets'/f'icon-{icon_size}.png.base64'
    if not png.exists():
        png.write_bytes(base64.b64decode(source.read_text()))
css=(ROOT/'style.css').read_text()
scripts=[]
for name in SOURCES:
    js=(ROOT/name).read_text()
    js=re.sub(r'(?m)^import .*?;\s*$', '', js)
    js=re.sub(r'(?m)^export ', '', js)
    scripts.append('// MODULE '+name+'\n'+js)
bundle='\n'.join(scripts)
script='\n<script>\n'+bundle+'\n</script>\n'
html=(ROOT/'index.html').read_text().replace('<link rel="stylesheet" href="./style.css"/>','<style>\n'+css+'\n</style>').replace('<script type="module" src="./src/main.js"></script>',script)
dist=ROOT/'dist';dist.mkdir(exist_ok=True)
(dist/'index.html').write_text(html)
(dist/'KIN_MOTO_A2_LAB_JOUER.html').write_text(html)
assets=dist/'assets';assets.mkdir(exist_ok=True)
for f in (ROOT/'assets').iterdir():
    if f.suffix!='.base64': shutil.copy2(f,assets/f.name)
shutil.copy2(ROOT/'manifest.webmanifest',dist/'manifest.webmanifest')
# For a self-contained HTML bundle the SW needs only the files actually loaded
cache_hash=hashlib.sha256(html.encode('utf-8')).hexdigest()[:12]
# Every build gets a content-derived cache key; navigations use network-first,
# so an online player will not be locked on an obsolete cached game.
sw=f"""const CACHE='kin-moto-a2-lab-{cache_hash}';
const FILES=['./','./index.html','./manifest.webmanifest','./assets/icon.svg','./assets/icon-192.png','./assets/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('kin-moto-a2-lab-')&&k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',e=>{{
 const req=e.request,url=new URL(req.url);
 if(req.method!=='GET'||url.origin!==self.location.origin)return;
 if(req.mode==='navigate'){{
  e.respondWith(fetch(req).then(r=>{{if(r.ok){{const copy=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{{}});}}return r;}})
   .catch(()=>caches.match('./index.html')));return;
 }}
 e.respondWith(caches.match(req).then(hit=>hit||fetch(req).then(r=>{{if(r.ok){{const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy)).catch(()=>{{}});}}return r;}})));
}});
"""
(dist/'sw.js').write_text(sw)
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [dist/'index.html',dist/'sw.js',dist/'manifest.webmanifest',*(assets.iterdir())]}
(ROOT/'docs'/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
print(json.dumps({'html_bytes':len(html.encode()),'source_modules':len(SOURCES),'total_bundle_bytes':sum((dist/x).stat().st_size for x in ['index.html','sw.js','manifest.webmanifest'])},indent=2))
