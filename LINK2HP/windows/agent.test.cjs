'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {classify,isPublicIPv4,parseCandidates}=require('./network.cjs');
const {createStore}=require('./agent.cjs');
test('Reject unsafe URLs, schemes, local and reserved addresses',()=>{
 for(const url of ['javascript:alert(1)','file:///etc/passwd','http://localhost/','http://10.0.0.1/','http://127.0.0.1/','http://169.254.169.254/','http://192.168.1.1/','http://[::1]/','https://user:pass@example.org/','magnet:?xt=bad'])assert.throws(()=>classify(url),undefined,url);
 for(const ip of ['10.1.2.3','172.18.1.1','192.168.1.1','169.254.1.2','127.0.0.1','100.65.1.2','224.0.0.1'])assert.equal(isPublicIPv4(ip),false,ip);
 assert.equal(isPublicIPv4('8.8.8.8'),true);
});
test('Accept URL and magnet and extract explicit safe links from HTML',()=>{
 assert.equal(classify('magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567').kind,'magnet');
 assert.equal(classify('https://example.org/a.iso').kind,'url');
 const links=parseCandidates('<a href="/linux.iso">Linux</a><a href="http://localhost/p.zip">Forbidden</a><a href="magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567">Magnet</a>','https://example.org/page');
 assert.equal(links.length,2);
});
test('SQLite WAL durable across restart',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'l2h-test-'));const p=path.join(dir,'state.sqlite');
 try{let db=createStore(p);db.prepare('INSERT INTO tasks(id,fingerprint,kind,payload,state,created,updated) VALUES(?,?,?,?,?,?,?)').run(crypto.randomUUID(),'x','url','https://example.org/a.iso','QUEUED','now','now');db.close();db=createStore(p);assert.equal(db.prepare('SELECT count(*) as n FROM tasks').get().n,1);db.close()}finally{fs.rmSync(dir,{recursive:true,force:true})}
});
