import { createHash } from 'node:crypto';
import {
  mkdirSync, readFileSync, writeFileSync, existsSync, rmSync, renameSync,
  openSync, closeSync, unlinkSync, readdirSync, statSync
} from 'node:fs';
import { join, dirname, resolve, sep } from 'node:path';
import { homedir, freemem, totalmem, setPriority, constants as osConstants } from 'node:os';
import { execFileSync, spawn } from 'node:child_process';
import { createServer } from 'node:net';

const OWNER='Terminator364';
const REPO='PROJECT-DRAFTS';
const UPDATE_CHANNEL='release/tlib-hybrid-v2-stable';
const DEVELOPMENT_BRANCH='lab/tlib-hybrid-v2';
const PREFIX='TLIB-HYBRID-V2';
const DATA=process.env.TLIB_DATA_DIR || join(process.env.LOCALAPPDATA || homedir(),'TLIB-PC');
const DEPLOY=join(DATA,'deployments');
const CURRENT=join(DATA,'current-deployment.json');
const PENDING=join(DATA,'pending-deployment.json');
const LASTGOOD=join(DATA,'last-good-deployment.json');
const LOCK=join(DATA,'slot-update.lock');
const LOG=join(DATA,'slot-update-audit.jsonl');
const PROGRESS=join(DATA,'slot-update-progress.json');
const BG_WORKER=join(DATA,'background-worker.json');
const MODE=(process.argv[2]||'status').toLowerCase();
const FORCE=process.argv.includes('--force');
const FETCH_TIMEOUT_MS=45000;
const MAX_MANIFEST_FILES=256;
const MAX_FILE_BYTES=8*1024*1024;
const MAX_TOTAL_BYTES=64*1024*1024;
mkdirSync(DATA,{recursive:true}); mkdirSync(DEPLOY,{recursive:true});
try{setPriority(process.pid,osConstants.priority?.PRIORITY_BELOW_NORMAL ?? 10)}catch{}

function now(){return new Date().toISOString()}
function log(event,status='INFO',detail=''){
  try{writeFileSync(LOG,JSON.stringify({at:now(),event,status,detail,mode:MODE})+'\n',{flag:'a'})}catch{}
}
function readJson(path,fallback=null){try{return JSON.parse(readFileSync(path,'utf8'))}catch{return fallback}}
function writeJson(path,value){writeFileSync(path,JSON.stringify(value,null,2)+'\n','utf8')}
function progress(phase,pct,detail='',extra={}){
  try{writeJson(PROGRESS,{at:now(),mode:MODE,phase,percent:Math.max(0,Math.min(100,Math.round(Number(pct)||0))),detail,...extra})}catch{}
}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function headers(){return {'User-Agent':'TLIB-Slot-Updater/1.1','Accept':'application/vnd.github+json'}}
async function fetchOk(url,opts={}){
  let lastErr=null;
  for(let attempt=0;attempt<3;attempt++){
    try{
      const res=await fetch(url,{...opts,headers:{...headers(),...(opts.headers||{})},signal:AbortSignal.timeout(FETCH_TIMEOUT_MS)});
      if(res.ok)return res;
      const retry=res.status===408||res.status===429||res.status>=500;
      const err=new Error('HTTP_'+res.status+' '+url);
      if(!retry)throw err;
      lastErr=err;
    }catch(e){lastErr=e}
    if(attempt<2)await sleep(1000*Math.pow(2,attempt));
  }
  throw lastErr||new Error('FETCH_FAILED '+url);
}
async function latestCommit(){
  const url='https://api.github.com/repos/'+OWNER+'/'+REPO+'/branches/'+encodeURIComponent(UPDATE_CHANNEL);
  const j=await (await fetchOk(url)).json();
  const sha=String(j?.commit?.sha||'');
  if(!/^[0-9a-f]{40}$/i.test(sha))throw new Error('LATEST_COMMIT_INVALID');
  return sha;
}
function blobSha(buf){
  return createHash('sha1').update(Buffer.from('blob '+buf.length+'\0')).update(buf).digest('hex');
}
async function rawFile(commit,path){
  const url='https://raw.githubusercontent.com/'+OWNER+'/'+REPO+'/'+commit+'/'+PREFIX+'/'+path;
  const res=await fetchOk(url,{headers:{Accept:'application/octet-stream'}});
  const len=Number(res.headers.get('content-length')||0);
  if(len>MAX_FILE_BYTES)throw new Error('FILE_TOO_LARGE '+path+' '+len);
  const buf=Buffer.from(await res.arrayBuffer());
  if(buf.length>MAX_FILE_BYTES)throw new Error('FILE_TOO_LARGE '+path+' '+buf.length);
  return buf;
}
async function manifestFor(commit){
  const buf=await rawFile(commit,'deploy-manifest.json');
  const j=JSON.parse(buf.toString('utf8'));
  if(j?.schema!==1||j?.product!=='TLIB'||!Array.isArray(j.files))throw new Error('MANIFEST_INVALID');
  if(j.files.length<1||j.files.length>MAX_MANIFEST_FILES)throw new Error('MANIFEST_FILE_COUNT '+j.files.length);
  return j;
}
function runNode(args,cwd,env={}){
  return execFileSync(process.execPath,args,{cwd,env:{...process.env,...env},encoding:'utf8',windowsHide:true,stdio:['ignore','pipe','pipe'],timeout:90000});
}
async function health(port=8787,timeout=1500){
  try{
    const res=await fetch('http://127.0.0.1:'+port+'/api/health',{signal:AbortSignal.timeout(timeout)});
    if(!res.ok)return null;
    return await res.json();
  }catch{return null}
}
async function waitHealth(port,commit,ms=15000){
  const end=Date.now()+ms;
  while(Date.now()<end){
    const h=await health(port,1200);
    if(h?.ok && (!commit || h.commit===commit))return h;
    await sleep(350);
  }
  return null;
}
function killPid(pid){
  if(!pid)return;
  const n=Number(pid);
  try{
    // Never use /T here: the updater itself can be a descendant of the old agent.
    // Tree-killing the agent would kill the updater during self-update.
    if(process.platform==='win32')execFileSync('taskkill.exe',['/PID',String(n),'/F'],{windowsHide:true,timeout:5000,stdio:'ignore'});
    else process.kill(n,'SIGTERM');
  }catch{}
}
function stopBackgroundWorker(){
  const bg=readJson(BG_WORKER,null);
  const pid=Number(bg?.pid||0);
  if(pid&&pid!==process.pid){
    log('BACKGROUND_WORKER_STOP','INFO','pid='+pid);
    killPid(pid);
  }
  try{rmSync(BG_WORKER,{force:true})}catch{}
}
function portPid(port){
  if(process.platform!=='win32')return null;
  try{
    const r=execFileSync('netstat.exe',['-ano','-p','tcp'],{encoding:'utf8',windowsHide:true,timeout:4000});
    const re=new RegExp('(?:127\\.0\\.0\\.1|0\\.0\\.0\\.0):'+port+'\\s+0\\.0\\.0\\.0:0\\s+LISTENING\\s+(\\d+)','i');
    for(const line of String(r||'').split(/\r?\n/)){const m=line.match(re);if(m)return Number(m[1])}
  }catch{}
  return null;
}
async function stopActive(){
  stopBackgroundWorker();
  const h=await health(8787,1200);
  let pid=h?.pid||null;
  if(!pid)pid=portPid(8787);
  if(pid){log('WORKER_STOP','INFO','pid='+pid);killPid(pid);for(let i=0;i<30;i++){await sleep(200);if(!await health(8787,350)&&!portPid(8787))break}}
}
function startWorker(slot){
  const entry=join(slot.path,'src','tlib.mjs');
  const child=spawn(process.execPath,[entry,'agent'],{
    cwd:slot.path,detached:true,windowsHide:true,stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:DATA,TLIB_DEPLOYMENT_COMMIT:slot.commit}
  });
  child.unref();
  return child.pid;
}
async function freePreflightPort(){
  return await new Promise((resolvePort,reject)=>{
    const s=createServer();
    s.unref();
    s.on('error',reject);
    s.listen(0,'127.0.0.1',()=>{const a=s.address();const p=typeof a==='object'&&a?a.port:0;s.close(()=>p?resolvePort(p):reject(new Error('NO_PREFLIGHT_PORT')))});
  });
}
async function preflight(slot){
  const temp=join(DATA,'preflight-'+slot.commit.slice(0,12)+'-'+process.pid);
  rmSync(temp,{recursive:true,force:true});mkdirSync(temp,{recursive:true});
  const entry=join(slot.path,'src','tlib.mjs');
  const port=await freePreflightPort();
  const child=spawn(process.execPath,[entry,'dashboard'],{
    cwd:slot.path,windowsHide:true,stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:temp,TLIB_DASHBOARD_PORT:String(port),TLIB_DEPLOYMENT_COMMIT:slot.commit}
  });
  try{
    const h=await waitHealth(port,slot.commit,12000);
    if(!h)throw new Error('PREFLIGHT_HEALTH_FAILED port='+port);
    return h;
  }finally{
    killPid(child.pid);
    rmSync(temp,{recursive:true,force:true});
  }
}
function verifiedSlot(commit){
  const path=join(DEPLOY,commit);
  const marker=readJson(join(path,'VERIFIED.json'),null);
  if(marker?.commit===commit && existsSync(join(path,'src','tlib.mjs')))return {commit,path,build:marker.build||''};
  return null;
}
async function stage(){
  const freeMB=Math.round(freemem()/1048576);
  const totalMB=Math.round(totalmem()/1048576);
  const lowRamProfile=totalMB<=6144;
  const minFree=lowRamProfile?90:320;
  progress('CHECK',2,'Vérification du canal stable');
  log('STAGE_CHECK_BEGIN','INFO','free_mb='+freeMB+' total_mb='+totalMB+' profile='+(lowRamProfile?'LOW_RAM_4_6GB':'STANDARD'));
  // Sur 4–6 Go, une RAM utilisée à 80–95 % est attendue. On diffère uniquement
  // quand la marge libre devient réellement critique pour le staging lui-même.
  if(!FORCE && freeMB<minFree){
    log('STAGE_DEFERRED','SKIP','free_mb='+freeMB+' min_free='+minFree+' profile='+(lowRamProfile?'LOW_RAM_4_6GB':'STANDARD'));
    return {ok:true,deferred:true,reason:'CRITICAL_FREE_MEMORY_ONLY',free_mb:freeMB,total_mb:totalMB,min_free_mb:minFree};
  }
  let commit;
  try{commit=await latestCommit()}catch(e){log('LATEST_CHECK_FAIL','FAIL',String(e.message||e));throw e}
  const current=readJson(CURRENT,null);
  if(current?.commit===commit){rmSync(PENDING,{force:true});progress('DONE',100,'TLIB est déjà à jour',{commit});log('NO_UPDATE','PASS',commit);return {ok:true,no_update:true,commit}}
  const existing=verifiedSlot(commit);
  if(existing){writeJson(PENDING,{...existing,verified:true,staged_at:now()});progress('READY',100,'Version déjà vérifiée',{commit,build:existing.build});log('STAGE_REUSE','PASS',commit);return {ok:true,staged:true,reused:true,...existing}}
  const manifest=await manifestFor(commit);
  const finalPath=join(DEPLOY,commit),tmp=finalPath+'.tmp-'+process.pid;
  rmSync(tmp,{recursive:true,force:true});mkdirSync(tmp,{recursive:true});
  log('STAGE_BEGIN','INFO','commit='+commit+' files='+manifest.files.length);
  try{
    let totalBytes=0;
    progress('DOWNLOAD',8,'Téléchargement et vérification des fichiers',{commit,total_files:manifest.files.length,current_file:0});
    for(let i=0;i<manifest.files.length;i++){
      const f=manifest.files[i];
      if(!f?.path||!/^[0-9a-f]{40}$/i.test(String(f.git_blob_sha||'')))throw new Error('MANIFEST_ENTRY_INVALID '+i);
      const rel=String(f.path).replace(/\\/g,'/');
      if(rel.startsWith('/')||rel.split('/').includes('..'))throw new Error('MANIFEST_PATH_UNSAFE '+rel);
      const dest=resolve(tmp,rel);
      if(!(dest===tmp||dest.startsWith(tmp+sep)))throw new Error('MANIFEST_PATH_ESCAPE '+rel);
      const buf=await rawFile(commit,rel);
      totalBytes+=buf.length;if(totalBytes>MAX_TOTAL_BYTES)throw new Error('UPDATE_TOO_LARGE '+totalBytes);
      const got=blobSha(buf);
      if(got!==f.git_blob_sha)throw new Error('BLOB_MISMATCH '+rel+' expected='+f.git_blob_sha+' got='+got);
      mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,buf);
      progress('DOWNLOAD',8+Math.round(((i+1)/manifest.files.length)*62),'Fichier '+(i+1)+' / '+manifest.files.length,{commit,total_files:manifest.files.length,current_file:i+1,file:rel});
      if(i%4===3)await sleep(80);
    }
    writeFileSync(join(tmp,'deploy-manifest.json'),JSON.stringify(manifest,null,2)+'\n','utf8');
    writeJson(join(tmp,'deployment.json'),{commit,channel:UPDATE_CHANNEL,source_branch:DEVELOPMENT_BRANCH,staged_at:now(),manifest_schema:manifest.schema});
    progress('VERIFY',75,'Audit statique de la nouvelle version',{commit});
    runNode([join(tmp,'scripts','verify-build.mjs')],tmp,{TLIB_DEPLOYMENT_COMMIT:commit});
    const testData=join(DATA,'verify-slot-'+process.pid);
    rmSync(testData,{recursive:true,force:true});mkdirSync(testData,{recursive:true});
    progress('SELFTEST',88,'Auto-test moteur isolé',{commit});
    try{runNode([join(tmp,'src','tlib.mjs'),'selftest'],tmp,{TLIB_DATA_DIR:testData,TLIB_DEPLOYMENT_COMMIT:commit})}
    finally{rmSync(testData,{recursive:true,force:true})}
    const src=readFileSync(join(tmp,'src','tlib.mjs'),'utf8');
    const m=src.match(/const APP_BUILD = '([^']+)'/);
    const build=m?.[1]||'UNKNOWN';
    writeJson(join(tmp,'VERIFIED.json'),{commit,build,verified_at:now(),files:manifest.files.length});
    rmSync(finalPath,{recursive:true,force:true});renameSync(tmp,finalPath);
    const slot={commit,path:finalPath,build,verified:true,staged_at:now()};
    writeJson(PENDING,slot);progress('READY',100,'Version prête à être activée',{commit,build});log('STAGE_PASS','PASS','commit='+commit+' build='+build);return {ok:true,staged:true,...slot};
  }catch(e){rmSync(tmp,{recursive:true,force:true});log('STAGE_FAIL','FAIL',String(e.message||e));throw e}
}
function syncBootstrapArtifacts(slot){
  for(const name of ['bootstrap-node.cjs','launch-hidden.vbs']){
    try{
      const src=join(slot.path,'scripts',name);if(!existsSync(src))continue;
      const dest=join(DATA,name),tmp=dest+'.tmp-'+process.pid;
      writeFileSync(tmp,readFileSync(src));renameSync(tmp,dest);
      log('BOOTSTRAP_SYNC','PASS',name);
    }catch(e){log('BOOTSTRAP_SYNC','WARN',name+' '+String(e.message||e))}
  }
}
async function apply(){
  const freeMB=Math.round(freemem()/1048576);
  const totalMB=Math.round(totalmem()/1048576);
  const lowRamProfile=totalMB<=6144;
  const activationFloor=lowRamProfile?80:220;
  if(!FORCE && freeMB<activationFloor){
    log('APPLY_DEFERRED','SKIP','free_mb='+freeMB+' floor='+activationFloor+' profile='+(lowRamProfile?'LOW_RAM_4_6GB':'STANDARD'));
    return {ok:true,deferred:true,reason:'ACTIVATION_MEMORY_FLOOR',free_mb:freeMB,total_mb:totalMB,activation_floor_mb:activationFloor};
  }
  progress('PREFLIGHT',5,'Préflight de la version préparée');
  const pending=readJson(PENDING,null);
  if(!pending?.verified||!pending?.commit||!pending?.path)throw new Error('NO_VERIFIED_PENDING_SLOT');
  const slot=verifiedSlot(pending.commit);
  if(!slot)throw new Error('PENDING_SLOT_NOT_VERIFIED');
  await preflight(slot);
  progress('ACTIVATE',35,'Préflight réussi · préparation de la bascule',{commit:slot.commit,build:slot.build});
  const old=readJson(CURRENT,null);
  writeJson(join(DATA,'rollback-deployment.json'),old||{});
  if(old?.commit&&old?.path)writeJson(LASTGOOD,{...old,preserved_at:now(),reason:'pre-activation-last-good'});
  await stopActive();
  progress('ACTIVATE',55,'Ancien moteur arrêté · updater toujours actif',{commit:slot.commit,updater_pid:process.pid});
  log('UPDATER_SURVIVED_STOP','PASS','pid='+process.pid+' old='+(old?.commit||'none'));
  progress('ACTIVATE',62,'Démarrage de la nouvelle version',{commit:slot.commit});
  try{
    const pid=startWorker(slot);
    progress('HEALTH',78,'Health-check du nouveau moteur',{commit:slot.commit});
    const h=await waitHealth(8787,slot.commit,16000);
    if(!h)throw new Error('ACTIVE_HEALTH_FAILED');
    const active={commit:slot.commit,path:slot.path,build:h.build||slot.build,pid:h.pid||pid,activated_at:now()};
    writeJson(CURRENT,active);rmSync(PENDING,{force:true});
    if(!old?.commit)writeJson(LASTGOOD,{...active,promoted_at:now(),reason:'first-install-no-prior-good'});
    syncBootstrapArtifacts(slot);
    progress('DONE',100,'Mise à jour activée',{commit:slot.commit,build:active.build,pid:active.pid});
    log('ACTIVATE_PASS','PASS','commit='+slot.commit+' build='+active.build+' pid='+active.pid+' last_good='+(old?.commit||slot.commit));
    cleanup();
    return {ok:true,active};
  }catch(e){
    progress('ROLLBACK',85,'Échec activation · rollback en cours',{error:String(e.message||e).slice(0,300)});
    log('ACTIVATE_FAIL','FAIL',String(e.message||e));
    await stopActive();
    if(old?.commit&&old?.path&&existsSync(join(old.path,'src','tlib.mjs'))){
      const pid=startWorker(old);const h=await waitHealth(8787,old.commit,15000);
      if(h){writeJson(CURRENT,{...old,pid:h.pid||pid,rollback_at:now()});progress('ROLLED_BACK',100,'Rollback réussi',{commit:old.commit,build:old.build||''});log('ROLLBACK_PASS','PASS',old.commit)}
      else log('ROLLBACK_FAIL','CRITICAL',old.commit);
    }
    throw e;
  }
}
async function repair(){
  const freeMB=Math.round(freemem()/1048576);
  const totalMB=Math.round(totalmem()/1048576);
  const lowRamProfile=totalMB<=6144;
  const repairFloor=lowRamProfile?60:180;
  if(!FORCE && freeMB<repairFloor){
    log('REPAIR_DEFERRED','SKIP','free_mb='+freeMB+' floor='+repairFloor+' profile='+(lowRamProfile?'LOW_RAM_4_6GB':'STANDARD'));
    return {ok:true,deferred:true,reason:'REPAIR_MEMORY_FLOOR',free_mb:freeMB,total_mb:totalMB,repair_floor_mb:repairFloor};
  }
  const cur=readJson(CURRENT,null);
  if(!cur?.commit||!cur?.path)throw new Error('NO_CURRENT_SLOT');
  const h=await health(8787,1500);
  if(h?.ok&&h.commit===cur.commit){log('REPAIR_NOT_NEEDED','PASS',cur.commit);return {ok:true,repaired:false,health:h}}
  await stopActive();const pid=startWorker(cur);const next=await waitHealth(8787,cur.commit,16000);
  if(!next)throw new Error('REPAIR_HEALTH_FAILED');
  writeJson(CURRENT,{...cur,pid:next.pid||pid,repaired_at:now()});log('REPAIR_PASS','PASS',cur.commit);return {ok:true,repaired:true,health:next};
}
function cleanup(){
  const keep=new Set([readJson(CURRENT,{})?.commit,readJson(PENDING,{})?.commit,readJson(LASTGOOD,{})?.commit].filter(Boolean));
  const dirs=readdirSync(DEPLOY,{withFileTypes:true}).filter(x=>x.isDirectory()&&/^[0-9a-f]{40}$/i.test(x.name)).map(x=>x.name);
  const extras=dirs.filter(x=>!keep.has(x)).slice(0,Math.max(0,dirs.length-3));
  for(const d of extras)rmSync(join(DEPLOY,d),{recursive:true,force:true});
}
function status(){
  return {ok:true,current:readJson(CURRENT,null),pending:readJson(PENDING,null),last_good:readJson(LASTGOOD,null),free_mb:Math.round(freemem()/1048576)};
}

function pidAlive(pid){try{process.kill(Number(pid),0);return true}catch{return false}}
function acquireUpdateLock(){
  for(let attempt=0;attempt<2;attempt++){
    try{
      const fd=openSync(LOCK,'wx');
      writeFileSync(fd,JSON.stringify({pid:process.pid,created_at:now(),mode:MODE}));
      return fd;
    }catch(e){
      if(e?.code!=='EEXIST')throw e;
      let info=null,age=Infinity;
      try{info=readJson(LOCK,null);age=Date.now()-statSync(LOCK).mtimeMs}catch{}
      const alive=info?.pid?pidAlive(info.pid):false;
      const stale=(info?.pid&&!alive)||(!info?.pid&&age>15*60*1000);
      if(stale){try{unlinkSync(LOCK);log('STALE_UPDATE_LOCK_REMOVED','WARN','pid='+(info?.pid||'unknown')+' age_ms='+Math.round(age));continue}catch{}}
      return null;
    }
  }
  return null;
}
let lockFd=null;
try{lockFd=acquireUpdateLock()}catch(e){console.error(String(e.message||e));process.exit(1)}
if(lockFd===null){
  console.log(JSON.stringify({ok:true,busy:true,message:'another slot update is running'}));process.exit(0);
}
try{
  let out;
  if(MODE==='stage')out=await stage();
  else if(MODE==='apply')out=await apply();
  else if(MODE==='latest'){const s=await stage();out=s.no_update||s.deferred?s:await apply()}
  else if(MODE==='repair')out=await repair();
  else if(MODE==='status')out=status();
  else throw new Error('UNKNOWN_MODE '+MODE);
  console.log(JSON.stringify(out,null,2));
}catch(e){
  progress('ERROR',100,'Échec : '+String(e.message||e).slice(0,300));
  log('COMMAND_FAIL','FAIL',String(e.stack||e.message||e));
  console.error(String(e.stack||e.message||e));process.exitCode=1;
}finally{
  try{if(lockFd!==null)closeSync(lockFd)}catch{}
  try{unlinkSync(LOCK)}catch{}
}
