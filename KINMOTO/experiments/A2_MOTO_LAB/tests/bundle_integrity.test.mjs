import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
function pythonList(){const m=read('build.py').match(/SOURCES=\[([^\]]+)\]/);assert.ok(m,'source list absent');return [...m[1].matchAll(/'([^']+\.js)'/g)].map(x=>x[1]);}
function powerShellList(){const m=read('tools/build_offline.ps1').match(/\$modules = @\(([^\)]+)\)/);assert.ok(m,'PowerShell source list absent');return [...m[1].matchAll(/'([^']+\.js)'/g)].map(x=>x[1]);}
test('Python and PowerShell builders have exactly identical module order',()=>{
 assert.deepEqual(powerShellList(),pythonList());
});
test('combined browser JS is syntactically valid with no duplicate globals',()=>{
 const chunks=pythonList().map(p=>read(p).replace(/^import .*?;\s*$/gm,'').replace(/^export /gm,''));
 const out=chunks.join('\n');assert.doesNotThrow(()=>new vm.Script(out,{filename:'kinmoto.inline.js'}));
});
test('all imported module dependencies are included by the bundler',()=>{
 const included=new Set(pythonList());
 for(const path of included)for(const imp of read(path).matchAll(/^import .*?from ['"](\.[^'"]+)['"];?/gm)){
  const prefix=path.split('/').slice(0,-1).join('/');
  const resolved=new URL(imp[1], 'file:///app/'+prefix+'/').pathname.replace('/app/','');
  assert.ok(included.has(resolved),path+' dependency '+resolved+' missing from standalone build');
 }
});
