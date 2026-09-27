const fs=require('fs');
const path=require('path');
const os=require('os');
const http=require('http');
const {spawn}=require('child_process');

const DATA=path.join(process.env.LOCALAPPDATA||os.homedir(),'TLIB-PC');
const CURRENT=path.join(DATA,'current-deployment.json');
const LASTGOOD=path.join(DATA,'last-good-deployment.json');
const LOCK=path.join(DATA,'boot.lock');
const LOG=path.join(DATA,'boot-node.log');
const ERROR=path.join(DATA,'last-launch-error.json');
const NO_OPEN=process.argv.includes('--no-open');
const URL='http://127.0.0.1:8787';

fs.mkdirSync(DATA,{recursive:true});
function log(event,detail=''){
  try{fs.appendFileSync(LOG,new Date().toISOString()+' '+event+(detail?' '+detail:'')+'\n','utf8')}catch{}
}
function readJson(p){try{return JSON.parse(fs.readFileSync(p,'utf8'))}catch{return null}}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function health(timeout=900){
  return new Promise(resolve=>{
    let done=false;
    const finish=v=>{if(done)return;done=true;resolve(v)};
    const req=http.get(URL+'/api/health',{timeout},res=>{
      let body='';res.setEncoding('utf8');res.on('data',d=>body+=d);res.on('end',()=>{try{finish(JSON.parse(body))}catch{finish(null)}});
    });
    req.on('timeout',()=>{req.destroy();finish(null)});
    req.on('error',()=>finish(null));
  });
}
function verifiedSlot(slot){
  if(!slot||!slot.commit||!slot.path)return false;
  try{
    const v=readJson(path.join(slot.path,'VERIFIED.json'));
    return !!(v&&v.commit===slot.commit&&fs.existsSync(path.join(slot.path,'src','tlib.mjs')));
  }catch{return false}
}
function stopPid(pid){
  if(!pid)return;
  try{process.kill(Number(pid),'SIGTERM');log('STALE_WORKER_STOP','pid='+pid)}catch{}
}
function startSlot(slot){
  const entry=path.join(slot.path,'src','tlib.mjs');
  const child=spawn(process.execPath,[entry,'agent'],{
    cwd:slot.path,
    detached:true,
    windowsHide:true,
    stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:DATA,TLIB_DEPLOYMENT_COMMIT:slot.commit}
  });
  child.unref();
  log('WORKER_SPAWN','pid='+child.pid+' commit='+slot.commit);
  return child.pid;
}
async function waitHealthy(slot,ms){
  const end=Date.now()+ms;
  while(Date.now()<end){
    const h=await health(850);
    if(h&&h.ok&&h.commit===slot.commit)return h;
    await sleep(350);
  }
  return null;
}
function openUI(){
  if(NO_OPEN)return;
  try{
    const p=spawn('explorer.exe',[URL],{detached:true,windowsHide:true,stdio:'ignore'});
    p.unref();
    log('UI_OPEN');
  }catch(e){log('UI_OPEN_FAIL',String(e.message||e))}
}
function writeError(code,detail){
  try{fs.writeFileSync(ERROR,JSON.stringify({at:new Date().toISOString(),code,detail},null,2),'utf8')}catch{}
}
function acquireLock(){
  for(let attempt=0;attempt<2;attempt++){
    try{
      const fd=fs.openSync(LOCK,'wx');
      fs.writeFileSync(fd,String(process.pid)+' '+Date.now());
      return fd;
    }catch(e){
      if(e.code!=='EEXIST')return null;
      try{
        const age=Date.now()-fs.statSync(LOCK).mtimeMs;
        if(age>45000){fs.unlinkSync(LOCK);continue}
      }catch{}
      return null;
    }
  }
  return null;
}

(async()=>{
  log('BOOT_BEGIN','noOpen='+NO_OPEN);
  const fd=acquireLock();
  if(fd===null){
    log('BOOT_ALREADY_RUNNING');
    if(!NO_OPEN){
      for(let i=0;i<16;i++){const h=await health(700);if(h&&h.ok){openUI();return}await sleep(300)}
    }
    return;
  }
  try{
    const current=readJson(CURRENT);
    const lastGood=readJson(LASTGOOD);
    let desired=verifiedSlot(current)?current:(verifiedSlot(lastGood)?lastGood:null);
    if(!desired){
      log('NO_VERIFIED_SLOT');
      writeError('NO_VERIFIED_SLOT','No current or last-good verified deployment.');
      return;
    }

    let h=await health(900);
    if(h&&h.ok&&h.commit===desired.commit){
      log('ALREADY_HEALTHY','pid='+h.pid+' build='+h.build);
      openUI();
      return;
    }

    if(h&&h.ok&&h.pid&&h.commit!==desired.commit){
      stopPid(h.pid);
      await sleep(500);
    }

    const totalMB=Math.round(os.totalmem()/1048576);
    const waitMs=totalMB<=6144?14000:9000;
    startSlot(desired);
    h=await waitHealthy(desired,waitMs);

    if(!h&&lastGood&&verifiedSlot(lastGood)&&lastGood.commit!==desired.commit){
      log('CURRENT_BOOT_FAILED','fallback='+lastGood.commit);
      const stale=await health(500);if(stale&&stale.pid)stopPid(stale.pid);
      startSlot(lastGood);
      h=await waitHealthy(lastGood,waitMs);
      if(h)desired=lastGood;
    }

    if(h&&h.ok){
      log('BOOT_READY','pid='+h.pid+' build='+h.build+' commit='+h.commit);
      try{fs.unlinkSync(ERROR)}catch{}
      openUI();
      return;
    }

    log('BOOT_FAILED','commit='+desired.commit);
    writeError('BOOT_FAILED','Worker did not become healthy within '+waitMs+' ms.');
  }finally{
    try{fs.closeSync(fd)}catch{}
    try{fs.unlinkSync(LOCK)}catch{}
  }
})().catch(e=>{log('BOOT_EXCEPTION',String(e.stack||e));writeError('BOOT_EXCEPTION',String(e.message||e));try{fs.unlinkSync(LOCK)}catch{}});
