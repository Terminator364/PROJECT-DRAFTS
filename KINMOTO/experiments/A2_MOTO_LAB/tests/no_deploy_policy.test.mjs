import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=rel=>readFileSync(resolve(dir,rel),'utf8');

test('build has no external game engine and no hosting-dependent build step',()=>{
 const pkg=JSON.parse(read('package.json'));
 assert.equal(pkg.private,true);
 assert.equal(pkg.dependencies,undefined);
 assert.equal(pkg.devDependencies,undefined);
 assert.ok(!Object.values(pkg.scripts).join(' ').match(/vercel|wrangler|gh-pages|firebase deploy|cloudflare/i));
 assert.ok(existsSync(resolve(dir,'tools','build_offline.ps1')));
});

test('Windows test server defaults to loopback and cannot deploy',()=>{
 const server=read('tools/serve_local.ps1');
 assert.ok(server.includes('[Net.IPAddress]::Loopback'));
 assert.ok(server.includes('[switch]$Lan'));
 assert.ok(!/Invoke-WebRequest|Invoke-RestMethod|vercel deploy|CreateDeployment/i.test(server));
 const python=read('tools/serve_local.py');
 assert.ok(python.includes("'127.0.0.1'"));
 assert.ok(python.includes("opts.lan"));
});

test('offline build contains no remote runtime JavaScript links',()=>{
 const html=read('dist/index.html');
 assert.ok(html.includes('<script>'));
 assert.ok(!/<script[^>]+src=["']https?:\/\//i.test(html));
 assert.ok(!/<link[^>]+(?:stylesheet|preload)[^>]+href=["']https?:\/\//i.test(html));
 assert.ok(!/sendBeacon\(|gtag\(|googletagmanager|goatcounter|Sentry\.init/i.test(html));
});
