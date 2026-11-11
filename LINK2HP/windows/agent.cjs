'use strict';
/* LINK2HP Windows agent. No external npm dependencies, Node >=24. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),http=require('node:http'),https=require('node:https');
const crypto=require('node:crypto'),dns=require('node:dns'),net=require('node:net'),{spawn}=require('node:child_process');
const {DatabaseSync}=require('node:sqlite');
const {classify, isPublicIPv4, secureGet, parseCandidates}=require('./network.cjs');
const {createPairing,createDiscovery,privateIPv4}=require('./pairing.cjs');
const {createWifiManager}=require('./wifi.cjs');
const ROOT=path.resolve(process.env.LOCALAPPDATA||path.join(os.homedir(),'AppData','Local'),'LINK2HP');
const CFG=process.env.LINK2HP_CONFIG||path.join(ROOT,'config.json');
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
function readConfig(){
 const config=JSON.parse(fs.readFileSync(CFG,'utf8'));
 for(const k of ['token','pfxPassword','pfxPath','downloadDir'])if(!config[k])throw Error('CONFIG_MISSING_'+k);
 if(config.token.length<48)throw Error('TOKEN_TOO_SHORT');
 if(!fs.existsSync(config.pfxPath))throw Error('TLS_CERT_NOT_FOUND');
 return config;
}
function createStore(file){
 fs.mkdirSync(path.dirname(file),{recursive:true});
 const db=new DatabaseSync(file);
 db.exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=4000;');
 db.exec("CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL, reason TEXT NOT NULL DEFAULT '', progress INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL, updated TEXT NOT NULL, candidates TEXT NOT NULL DEFAULT '[]', output TEXT NOT NULL DEFAULT '')");
 db.prepare("UPDATE tasks SET state='QUEUED', reason='RECOVERED_AFTER_RESTART' WHERE state IN ('RUNNING','ANALYSING')").run();
 return db;
}
const iso=()=>new Date().toISOString();
function statusRow(row){if(!row)return null;return {task_id:row.id,kind:row.kind,state:row.state,reason:row.reason,progress:row.progress,created_at:row.created,updated_at:row.updated,candidates:JSON.parse(row.candidates),file_name:row.output?path.basename(row.output):null};}
function createApp(config,opts={}){
 const db=createStore(opts.dbPath||path.join(ROOT,'tasks.sqlite'));
 fs.mkdirSync(config.downloadDir,{recursive:true});
 const get=db.prepare('SELECT * FROM tasks WHERE id=?');
 const find=db.prepare('SELECT * FROM tasks WHERE fingerprint=?');
 const pairing=createPairing({certificatePin:config.certPin,port:config.port||17642,config,writeConfig:c=>{const tmp=CFG+'.next';fs.writeFileSync(tmp,JSON.stringify(c,null,2),{mode:0o600});fs.renameSync(tmp,CFG)}});
 const discovery=createDiscovery({pin:config.certPin,port:config.port||17642});
 const wifi=createWifiManager(opts.wifiOptions||{});
 let lastWifiAttempt=0;
 let wifiTimer=null;
 let wifiStartupTimer=null;
 async function preferHpWifi(){
   // Switch only when idle; prioritize known Starlink 5 GHz, else 2.4 GHz.
   // Back off to avoid network flapping when the access point is failing.
   if(busy||closed||Date.now()-lastWifiAttempt<300000)return;
   try{const state=await wifi.list();if(!state.available)return;
     const best=wifi.best(state);
     // Do not disrupt a functioning Starlink 5-GHz connection just because
     // the SSID name contains '2.4g' (real HP extender can do exactly this).
     const current=state.networks.find(n=>n.current);
     if(current && current.priority===0 && state.current_band==='5 GHz')return;
     if(best && best.priority<3 && !best.current){
       lastWifiAttempt=Date.now();await wifi.connect(best.ssid);
     }
   }catch(e){console.error('LINK2HP_WIFI_PREFERENCE_ERROR',e.message)}
 }
 const csrf=crypto.randomBytes(24).toString('hex');
 const latest=db.prepare('SELECT * FROM tasks ORDER BY created DESC LIMIT 50');
 const insert=db.prepare('INSERT INTO tasks(id,fingerprint,kind,payload,state,created,updated) VALUES(?,?,?,?,?,?,?)');
 const update=db.prepare('UPDATE tasks SET state=?,reason=?,progress=?,candidates=?,output=?,updated=? WHERE id=?');
 let busy=false,closed=false,active=null;
 function state(id,value,reason='',progress=0,candidates=[],output='') {update.run(value,reason,progress,JSON.stringify(candidates),output,iso(),id)}
 function queue(){if(busy||closed)return;const next=db.prepare("SELECT id FROM tasks WHERE state='QUEUED' ORDER BY created ASC LIMIT 1").get();if(!next)return;busy=true;active=next.id;setImmediate(async()=>{
   try{await processTask(next.id)}catch(e){state(next.id,'FAILED',e.code||e.message||'UNKNOWN_ERROR')}
   finally{busy=false;active=null;queue()}
  });}
 async function processTask(id){
  const task=get.get(id);if(!task)return;
  if(task.kind==='torrent_file'){
   let raw;try{raw=Buffer.from(task.payload,'base64')}catch{throw Error('INVALID_TORRENT_ENCODING')}
   if(raw.length<12||raw.length>5*1024*1024||raw[0]!==100||!raw.includes(Buffer.from('4:info')))throw Error('INVALID_TORRENT_FILE');
   const name=path.join(ROOT,'incoming',id+'.torrent');fs.mkdirSync(path.dirname(name),{recursive:true});fs.writeFileSync(name,raw,{flag:'wx'});
   return handoff(id,name);
  }
  const c=classify(task.payload);
  if(c.kind==='magnet')return handoff(id,c.canonical);
  state(id,'ANALYSING');
  const response=await secureGet(c.canonical,{maxBytes:5*1024*1024,maxRedirects:4,timeoutMs:15000,probeOnly:true});
  const mime=(response.headers['content-type']||'').split(';')[0].toLowerCase();
  if(mime.includes('text/html')||response.body.subarray(0,64).toString().match(/<!doctype html|<html/i)){
    const candidates=parseCandidates(response.body.toString('utf8'),response.finalUrl);
    state(id,'WAIT_SELECTION',candidates.length?'CHOIX_NECESSAIRE':'AUCUN_LIEN_DIRECT_PUBLIC',0,candidates);return;
  }
  if(!isAllowedFile(response.finalUrl,mime)){
    state(id,'WAIT_SELECTION','TYPE_DE_FICHIER_INCERTAIN',0,[]);return;
  }
  if(response.finalUrl.toLowerCase().split('?')[0].endsWith('.torrent')){
   const data=response.body;
   if(data.length<12||data[0]!==100||!data.includes(Buffer.from('4:info')))throw Error('INVALID_TORRENT_FILE');
   const f=path.join(ROOT,'incoming',id+'.torrent');fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,data,{flag:'wx'});
   return handoff(id,f);
  }
  // For simple direct downloads, streaming in chunks with cap and atomic finalization.
  state(id,'RUNNING');
  const dest=path.join(config.downloadDir,safeName(response.finalUrl,id));
  const part=dest+'.'+id+'.partial';
  const length=Number(response.headers['content-length']||0);
  if(length>Math.min(config.maxBytes||2147483648,2147483648))throw Error('FILE_TOO_LARGE');
  const space=fs.statfsSync(config.downloadDir);if(space.bavail*space.bsize < Math.max(length,50*1024*1024))throw Error('DISK_SPACE_LOW');
  try{
   await downloadFile(response.finalUrl,part,{maxBytes:Math.min(config.maxBytes||2147483648,2147483648),onProgress:n=>state(id,'RUNNING','',length?Math.min(99,Math.floor(n*100/length)):0)});
   if(fs.existsSync(dest))throw Error('DESTINATION_EXISTS');
   fs.renameSync(part,dest);state(id,'COMPLETED','',100,[],dest);
  }catch(e){try{fs.unlinkSync(part)}catch{}throw e}
 }
 function isAllowedFile(url,mime){
   let pathname;try{pathname=new URL(url).pathname.toLowerCase()}catch{return false}
   if(/\.(exe|msi|bat|cmd|ps1|scr|dll|apk|jar|vbs|hta)$/.test(pathname))return false;
   return /\.(pdf|txt|zip|7z|rar|iso|jpg|jpeg|png|webp|mp3|mp4|mkv|csv|docx|xlsx|torrent)$/.test(pathname)&&!(mime.includes('text/html'));
 }
 function safeName(raw,id){let n;try{n=decodeURIComponent(new URL(raw).pathname.split('/').pop()||'fichier')}catch{n='fichier'}
   n=n.replace(/[<>:"/\\|?*\x00-\x1f]/g,'_').replace(/[. ]+$/,'').slice(0,96);if(!n)n='fichier';return id.substring(0,8)+'-'+n;
 }
 function handoff(id,magnetOrPath){
   const q=config.qbittorrentExe||'C:\\Program Files\\qBittorrent\\qbittorrent.exe';
   if(!fs.existsSync(q)){state(id,'FAILED','QBITTORRENT_NOT_INSTALLED');return}
   try{
    const child=spawn(q,[magnetOrPath],{detached:true,stdio:'ignore',windowsHide:true});
    child.on('error',()=>state(id,'FAILED','QBITTORRENT_LAUNCH_FAILED'));
    child.unref();state(id,'HANDED_TO_QBITTORRENT','ACCEPTANCE_UNVERIFIED');
   }catch{state(id,'FAILED','QBITTORRENT_LAUNCH_FAILED')}
 }
 function reply(res,code,obj){res.writeHead(code,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(obj))}
 function authorized(req){const got=req.headers.authorization||'';return got.startsWith('Bearer ')&&pairing.authorized(got.slice(7))}
 function remote(req,res){
  const route=new URL(req.url,'https://link2hp.local');
  if(req.method==='GET'&&route.pathname==='/api/discovery'){
    // Local-network identity hint. Public certificate digest only; no token or secret.
    // A remote user cannot pair without explicit HP-side approval.
    if(!privateIPv4(req.socket.remoteAddress))return reply(res,403,{error:'LOCAL_ONLY'});
    return reply(res,200,{magic:'LINK2HP_HERE_V2',name:os.hostname().slice(0,48),port:config.port||17642,pin:config.certPin});
  }
  if(req.method==='POST'&&route.pathname==='/api/pair/init')return parseBody(req,res,2048,body=>{try{reply(res,200,pairing.begin({socket:req.socket,body}))}catch(e){reply(res,403,{error:e.message})}});
  if(req.method==='GET'&&route.pathname==='/api/pair/status')return reply(res,200,pairing.poll(req,route.searchParams.get('id'),route.searchParams.get('device_id')));
  if(!authorized(req))return reply(res,401,{error:'NON_APPAIRE'});
  let u;try{u=new URL(req.url,'https://link2hp.local')}catch{return reply(res,400,{error:'URL_INVALIDE'})}
  if(req.method==='GET'&&u.pathname==='/api/wifi/networks'){
    wifi.list().then(x=>reply(res,200,x)).catch(()=>reply(res,503,{available:false,reason:'WIFI_SCAN_FAILED',networks:[]}));return;
  }
  if(req.method==='POST'&&u.pathname==='/api/wifi/connect'){
    return parseBody(req,res,512,body=>{
      const ssid=body?.ssid;
      if(typeof ssid!=='string'||ssid.length<1||ssid.length>128||/[\x00-\x1f]/.test(ssid))return reply(res,422,{state:'INVALID_SSID'});
      wifi.list().then(info=>{
        if(!info.available)return reply(res,503,{state:'WINDOWS_WIFI_UNAVAILABLE'});
        const selected=info.networks.find(x=>x.ssid===ssid);
        if(!selected)return reply(res,404,{state:'NETWORK_NOT_VISIBLE'});
        if(!selected.saved)return reply(res,409,{state:'CONFIGURE_ON_HP'});
        if(selected.current)return reply(res,200,{state:'ALREADY_CONNECTED',ssid});
        // Acknowledge BEFORE switching: the TCP connection may vanish instantly.
        reply(res,202,{state:'SWITCH_PENDING',ssid,notice:'LINK_MAY_DROP'});
        lastWifiAttempt=Date.now();
        setTimeout(()=>wifi.connect(ssid).catch(e=>console.error('LINK2HP_WIFI_SWITCH_FAILED',e.message)),700).unref();
      }).catch(()=>reply(res,503,{state:'WIFI_SCAN_FAILED'}));
    });
  }
  if(req.method==='GET'&&u.pathname==='/api/health')return reply(res,200,{status:'ONLINE',version:'1.0.0',queue:latest.all().filter(x=>x.state==='QUEUED').length});
  if(req.method==='GET'&&u.pathname==='/api/tasks')return reply(res,200,{tasks:latest.all().map(statusRow)});
  if(req.method==='GET'&&u.pathname.startsWith('/api/tasks/'))return reply(res,200,{task:statusRow(get.get(u.pathname.split('/')[3]))});
  if(req.method==='POST'&&u.pathname==='/api/submit')return receive(req,res);
  if(req.method==='POST'&&/^\/api\/tasks\/[0-9a-f-]+\/select$/.test(u.pathname))return choose(req,res,u.pathname.split('/')[3]);
  return reply(res,404,{error:'ROUTE_INCONNUE'});
 }
 function parseBody(req,res,limit,cb){let parts=[],n=0,rejected=false;req.on('data',b=>{n+=b.length;if(n>limit){rejected=true;reply(res,413,{error:'TROP_VOLUMINEUX'});req.destroy();return}parts.push(b)});req.on('end',()=>{if(rejected)return;try{cb(JSON.parse(Buffer.concat(parts).toString('utf8')))}catch(e){reply(res,400,{error:'REQUETE_INVALIDE'})}})}
 function receive(req,res){parseBody(req,res,8*1024*1024,body=>{
   if(!body||!uuid.test(body.request_id||''))return reply(res,422,{error:'IDENTIFIANT_INVALIDE'});
   let kind, payload;
   if(body.kind==='torrent_file'){
     if(typeof body.payload!=='string'||body.payload.length>7*1024*1024)return reply(res,422,{error:'TORRENT_TROP_VOLUMINEUX'});
     const bytes=Buffer.from(body.payload||'','base64');
     if(bytes.length<12||bytes.length>5*1024*1024||bytes[0]!==100||!bytes.includes(Buffer.from('4:info')))return reply(res,422,{error:'TORRENT_INVALIDE'});
     kind='torrent_file';payload=bytes.toString('base64');
   }else{
      try{const c=classify(body.payload);kind=c.kind;payload=c.canonical}catch(e){return reply(res,422,{error:e.message})}
   }
   const fingerprint=hash(kind+'\n'+payload);const existing=get.get(body.request_id)||find.get(fingerprint);
   if(existing){if(existing.id===body.request_id&&existing.fingerprint!==fingerprint)return reply(res,409,{error:'CONFLIT_ID'});return reply(res,200,{duplicate:true,task:statusRow(existing)})}
   const now=iso();insert.run(body.request_id,fingerprint,kind,payload,'QUEUED',now,now);const row=get.get(body.request_id);reply(res,201,{duplicate:false,task:statusRow(row)});queue();
  })}
 function choose(req,res,id){parseBody(req,res,1024,b=>{
    const row=get.get(id);if(!row||row.state!=='WAIT_SELECTION')return reply(res,409,{error:'ETAT_NON_COMPATIBLE'});
    const choices=JSON.parse(row.candidates);const item=choices[b.index];if(!Number.isInteger(b.index)||!item)return reply(res,422,{error:'CHOIX_INVALIDE'});
    const c=classify(item.url);update.run('QUEUED','',0,'[]','',iso(),id);
    db.prepare('UPDATE tasks SET kind=?,payload=?,fingerprint=? WHERE id=?').run(c.kind,c.canonical,hash(c.kind+'\n'+c.canonical),id);
    reply(res,200,{task:statusRow(get.get(id))});queue();
 })}
 function localDashboard(req,res){
  const u=new URL(req.url,'http://127.0.0.1:17643');
  // Browser-origin and CSRF token mandatory for state changes.
  if(req.method==='POST'&&u.pathname==='/approve'){
    const origin=req.headers.origin||'';
    if(origin!=='http://127.0.0.1:17643'||u.searchParams.get('csrf')!==csrf){res.writeHead(403);res.end('Accès refusé');return}
    const id=u.searchParams.get('id');pairing.approve(id);
    res.writeHead(303,{'Location':'/'});res.end();return;
  }
  if(req.method!=='GET'){res.writeHead(405);res.end();return}
  if(u.pathname==='/api/status')return reply(res,200,{online:true,pending:pairing.list().length,devices:(config.devices||[]).map(x=>x.label),tasks:latest.all().map(statusRow)});
  if(u.pathname!=='/'){res.writeHead(404);res.end();return}
  const escape=s=>String(s).replace(/[&<>'"\u0000-\u001f]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]||''));
  const waiting=pairing.list().map(x=>`<div class="peer"><strong>${escape(x.label)}</strong><div class="muted">Demande depuis ${escape(x.address.replace('::ffff:',''))}</div><form method="POST" action="/approve?id=${encodeURIComponent(x.id)}&csrf=${csrf}"><button type="submit">Autoriser ce téléphone</button></form></div>`).join('');
  const devices=(config.devices||[]).map(x=>`<li>${escape(x.label)}</li>`).join('')||'<li>Aucun téléphone connecté</li>';
  const rows=latest.all().map(x=>`<tr><td>${escape(x.kind)}</td><td>${escape(x.state)}</td><td>${x.progress}%</td></tr>`).join('');
  const html=`<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="6"><title>LINK2HP</title><style>*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#f4f7fb;color:#18243a;max-width:800px;margin:0 auto;padding:20px}main{background:#fff;border-radius:18px;padding:24px;box-shadow:0 4px 24px #23304712}h1{margin:0;font-size:30px}h2{font-size:19px;margin:24px 0 9px}.badge{display:inline-block;background:#e4f8ef;color:#05643c;border-radius:50px;padding:7px 12px;font-weight:700}.muted{color:#526379}.peer{padding:14px;background:#f2f7ff;border:1px solid #bdd7fd;border-radius:12px;margin:8px 0}button{background:#0765d5;color:white;padding:12px 18px;border:0;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer}table{border-collapse:collapse;width:100%;font-size:14px}td{padding:10px;border-bottom:1px solid #edf1f5}small{color:#526379}</style></head><body><main><h1>LINK2HP</h1><p><span class="badge">● Agent HP actif</span></p><p>Le téléphone détecte automatiquement cet ordinateur sur le même Wi-Fi / point d'accès. Aucun code à copier.</p><h2>Autoriser un téléphone</h2>${waiting||'<p class="muted">Ouvre LINK2HP sur Android et touche « Rechercher mon HP ». La demande apparaîtra ici automatiquement.</p>'}<h2>Téléphones associés</h2><ul>${devices}</ul><h2>Activité récente</h2><table>${rows||'<tr><td>Aucune demande</td></tr>'}</table><p><small>Communication HTTPS locale uniquement. Une autorisation est nécessaire seulement lors du premier appairage. Rafraîchissement automatique toutes les 6 secondes.</small></p></main></body></html>`;
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'none';style-src 'unsafe-inline';form-action 'self';base-uri 'none'"});res.end(html);
 }
 const remoteServer=https.createServer({pfx:fs.readFileSync(config.pfxPath),passphrase:config.pfxPassword,minVersion:'TLSv1.2'},remote);
 const dashboard=http.createServer(localDashboard);
 return {db,remoteServer,dashboard,start:async()=>{
   await new Promise((resolve,reject)=>remoteServer.once('error',reject).listen(config.port||17642,'0.0.0.0',resolve));
   await new Promise((resolve,reject)=>dashboard.once('error',reject).listen(17643,'127.0.0.1',resolve));
   try{await discovery.start()}catch(e){console.error('LINK2HP_DISCOVERY_ERROR',e.message)}
   queue();
   wifiStartupTimer=setTimeout(()=>preferHpWifi(),20000);wifiStartupTimer.unref();
   wifiTimer=setInterval(()=>preferHpWifi(),600000);wifiTimer.unref();
   return {https:remoteServer.address(),dashboard:dashboard.address()};
 },close:async()=>{closed=true;clearInterval(wifiTimer);clearTimeout(wifiStartupTimer);await new Promise(r=>remoteServer.close(r));await new Promise(r=>dashboard.close(r));try{await discovery.close()}catch{}db.close()},getState:id=>statusRow(get.get(id))};
}
async function downloadFile(url,destination,{maxBytes,onProgress}){
 // fetch via controlled DNS and redirects, chunks streamed to disk.
 const stream=fs.createWriteStream(destination,{flags:'wx'});let n=0;
 try{
  await new Promise(async (resolve,reject)=>{
   try{await secureGet(url,{maxBytes,timeoutMs:60000,maxRedirects:4,onChunk:chunk=>{
    n+=chunk.length;if(n>maxBytes)throw Error('FILE_TOO_LARGE');stream.write(chunk);onProgress(n);
   },streamOnly:true});resolve()}catch(e){reject(e)}
  });
 }finally{await new Promise(resolve=>stream.end(resolve))}
}
if(require.main===module){try{const config=readConfig();createApp(config).start().then(()=>console.log('LINK2HP_RUNNING')).catch(e=>{console.error(e.message);process.exitCode=1})}catch(e){console.error(e.message);process.exitCode=1}}
module.exports={createStore,createApp,readConfig};
