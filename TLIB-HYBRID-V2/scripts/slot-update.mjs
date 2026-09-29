import { createHash } from 'node:crypto';
import {
  mkdirSync, readFileSync, writeFileSync, existsSync, rmSync, renameSync,
  openSync, closeSync, unlinkSync, readdirSync
} from 'node:fs';
import { join, dirname } from 'node:path';
import { homedir, freemem, totalmem, setPriority, constants as osConstants } from 'node:os';
import { execFileSync, spawn } from 'node:child_process';

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
const MODE=(process.argv[2]||'status').toLowerCase();
const FORCE=process.argv.includes('--force');
mkdirSync(DATA,{recursive:true}); mkdirSync(DEPLOY,{recursive:true});
try{setPriority(process.pid,osConstants.priority?.PRIORITY_BELOW_NORMAL ?? 10)}catch{}

function now(){return new Date().toISOString()}
function log(event,status='INFO',detail=''){
  try{writeFileSync(LOG,JSON.stringify({at:now(),event,status,detail,mode:MODE})+'\n',{flag:'a'})}catch{}
}
function readJson(path,fallback=null){try{return JSON.parse(readFileSync(path,'utf8'))}catch{return fallback}}
function writeJson(path,value){writeFileSync(path,JSON.stringify(value,null,2)+'\n','utf8')}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function headers(){return {'User-Agent':'TLIB-Slot-Updater/1.1','Accept':'application/vnd.github+json'}}
async function fetchOk(url,opts={}){
  const res=await fetch(url,{...opts,headers:{...headers(),...(opts.headers||{})},signal:AbortSignal.timeout(10000)});
  if(!res.ok)throw new Error('HTTP_'+res.status+' '+url);
  return res;
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
  return Buffer.from(await res.arrayBuffer());
}
async function manifestFor(commit){
  const buf=await rawFile(commit,'deploy-manifest.json');
  const j=JSON.parse(buf.toString('utf8'));
  if(j?.schema!==1||j?.product!=='TLIB'||!Array.isArray(j.files))throw new Error('MANIFEST_INVALID');
  return j;
}
function runNode(args,cwd,env={}){
  return execFileSync(process.execPath,args,{cwd,env:{...process.env,...env},encoding:'utf8',windowsHide:true,stdio:['ignore','pipe','pipe'],timeout:30000});
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
  try{process.kill(Number(pid),'SIGTERM')}catch{}
}
async function stopActive(){
  const h=await health(8787,1200);
  if(h?.pid){log('WORKER_STOP','INFO','pid='+h.pid);killPid(h.pid);for(let i=0;i<25;i++){await sleep(200);if(!await health(8787,400))break}}
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
async function preflight(slot){
  const temp=join(DATA,'preflight-'+slot.commit.slice(0,12)+'-'+process.pid);
  rmSync(temp,{recursive:true,force:true});mkdirSync(temp,{recursive:true});
  const entry=join(slot.path,'src','tlib.mjs');
  const child=spawn(process.execPath,[entry,'dashboard'],{
    cwd:slot.path,windowsHide:true,stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:temp,TLIB_DASHBOARD_PORT:'8797',TLIB_DEPLOYMENT_COMMIT:slot.commit}
  });
  const h=await waitHealth(8797,slot.commit,10000);
  killPid(child.pid);
  rmSync(temp,{recursive:true,force:true});
  if(!h)throw new Error('PREFLIGHT_HEALTH_FAILED');
  return h;
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
  if(current?.commit===commit){rmSync(PENDING,{force:true});log('NO_UPDATE','PASS',commit);return {ok:true,no_update:true,commit}}
  const existing=verifiedSlot(commit);
  if(existing){writeJson(PENDING,{...existing,verified:true,staged_at:now()});log('STAGE_REUSE','PASS',commit);return {ok:true,staged:true,reused:true,...existing}}
  const manifest=await manifestFor(commit);
  const finalPath=join(DEPLOY,commit),tmp=finalPath+'.tmp-'+process.pid;
  rmSync(tmp,{recursive:true,force:true});mkdirSync(tmp,{recursive:true});
  log('STAGE_BEGIN','INFO','commit='+commit+' files='+manifest.files.length);
  try{
    for(let i=0;i<manifest.files.length;i++){
      const f=manifest.files[i];
      if(!f?.path||!/^[0-9a-f]{40}$/i.test(String(f.git_blob_sha||'')))throw new Error('MANIFEST_ENTRY_INVALID '+i);
      const buf=await rawFile(commit,String(f.path));
      const got=blobSha(buf);
      if(got!==f.git_blob_sha)throw new Error('BLOB_MISMATCH '+f.path+' expected='+f.git_blob_sha+' got='+got);
      const dest=join(tmp,String(f.path));mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,buf);
      if(i%4===3)await sleep(80);
    }
    writeJson(join(tmp,'deployment.json'),{commit,channel:UPDATE_CHANNEL,source_branch:DEVELOPMENT_BRANCH,staged_at:now(),manifest_schema:manifest.schema});
    runNode([join(tmp,'scripts','verify-build.mjs')],tmp,{TLIB_DEPLOYMENT_COMMIT:commit});
    const testData=join(DATA,'verify-slot-'+process.pid);
    rmSync(testData,{recursive:true,force:true});mkdirSync(testData,{recursive:true});
    try{runNode([join(tmp,'src','tlib.mjs'),'selftest'],tmp,{TLIB_DATA_DIR:testData,TLIB_DEPLOYMENT_COMMIT:commit})}
    finally{rmSync(testData,{recursive:true,force:true})}
    const src=readFileSync(join(tmp,'src','tlib.mjs'),'utf8');
    const m=src.match(/const APP_BUILD = '([^']+)'/);
    const build=m?.[1]||'UNKNOWN';
    writeJson(join(tmp,'VERIFIED.json'),{commit,build,verified_at:now(),files:manifest.files.length});
    rmSync(finalPath,{recursive:true,force:true});renameSync(tmp,finalPath);
    const slot={commit,path:finalPath,build,verified:true,staged_at:now()};
    writeJson(PENDING,slot);log('STAGE_PASS','PASS','commit='+commit+' build='+build);return {ok:true,staged:true,...slot};
  }catch(e){rmSync(tmp,{recursive:true,force:true});log('STAGE_FAIL','FAIL',String(e.message||e));throw e}
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
  const pending=readJson(PENDING,null);
  if(!pending?.verified||!pending?.commit||!pending?.path)throw new Error('NO_VERIFIED_PENDING_SLOT');
  const slot=verifiedSlot(pending.commit);
  if(!slot)throw new Error('PENDING_SLOT_NOT_VERIFIED');
  await preflight(slot);
  const old=readJson(CURRENT,null);
  writeJson(join(DATA,'rollback-deployment.json'),old||{});
  await stopActive();
  try{
    const pid=startWorker(slot);
    const h=await waitHealth(8787,slot.commit,16000);
    if(!h)throw new Error('ACTIVE_HEALTH_FAILED');
    const active={commit:slot.commit,path:slot.path,build:h.build||slot.build,pid:h.pid||pid,activated_at:now()};
    writeJson(CURRENT,active);writeJson(LASTGOOD,active);rmSync(PENDING,{force:true});
    log('ACTIVATE_PASS','PASS','commit='+slot.commit+' build='+active.build+' pid='+active.pid);
    cleanup();
    return {ok:true,active};
  }catch(e){
    log('ACTIVATE_FAIL','FAIL',String(e.message||e));
    await stopActive();
    if(old?.commit&&old?.path&&existsSync(join(old.path,'src','tlib.mjs'))){
      const pid=startWorker(old);const h=await waitHealth(8787,old.commit,15000);
      if(h){writeJson(CURRENT,{...old,pid:h.pid||pid,rollback_at:now()});log('ROLLBACK_PASS','PASS',old.commit)}
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

let lockFd=null;
try{
  lockFd=openSync(LOCK,'wx');
}catch{
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
  log('COMMAND_FAIL','FAIL',String(e.stack||e.message||e));
  console.error(String(e.stack||e.message||e));process.exitCode=1;
}finally{
  try{if(lockFd!==null)closeSync(lockFd)}catch{}
  try{unlinkSync(LOCK)}catch{}
}
