const fs=require('fs');
const path=require('path');
const os=require('os');
const http=require('http');
const cp=require('child_process');
const {spawn}=require('child_process');

const DATA=path.join(process.env.LOCALAPPDATA||os.homedir(),'TLIB-PC');
const TARGET='0fb1f855b6d82a1ca5c60d9cb22294ae6e8e2fc0';
const BUILD='2026.09.27-v0.6.3-resilient-boot';
const SLOT=path.join(DATA,'deployments',TARGET);
const CURRENT=path.join(DATA,'current-deployment.json');
const LASTGOOD=path.join(DATA,'last-good-deployment.json');
const RESULT=path.join(DATA,'FINAL-SEAL-v063.json');
const BOOT=path.join(DATA,'bootstrap-node.cjs');
const HIDDEN=path.join(DATA,'launch-hidden.vbs');
const URL='http://127.0.0.1:8787';
const previous=(()=>{try{return JSON.parse(fs.readFileSync(CURRENT,'utf8'))}catch{return null}})();

function now(){return new Date().toISOString()}
function readJson(p){try{return JSON.parse(fs.readFileSync(p,'utf8'))}catch{return null}}
function writeJson(p,v){fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n','utf8')}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function run(file,args,timeout=5000){
  try{return cp.spawnSync(file,args,{encoding:'utf8',windowsHide:true,timeout,stdio:['ignore','pipe','pipe']})}
  catch(e){return {status:-1,stdout:'',stderr:String(e.message||e)}}
}
function health(timeout=800){
  return new Promise(resolve=>{
    let done=false;
    const finish=v=>{if(done)return;done=true;resolve(v)};
    const req=http.get(URL+'/api/health',{timeout},res=>{
      let b='';res.setEncoding('utf8');res.on('data',d=>b+=d);res.on('end',()=>{try{finish(JSON.parse(b))}catch{finish(null)}});
    });
    req.on('timeout',()=>{req.destroy();finish(null)});
    req.on('error',()=>finish(null));
  });
}
function portPid(port){
  const r=run('netstat.exe',['-ano','-p','tcp'],4000);
  if(r.status!==0)return null;
  const re=new RegExp('127\\.0\\.0\\.1:'+port+'\\s+0\\.0\\.0\\.0:0\\s+LISTENING\\s+(\\d+)','i');
  for(const line of String(r.stdout||'').split(/\r?\n/)){const m=line.match(re);if(m)return Number(m[1])}
  return null;
}
function kill(pid){
  if(!pid)return false;
  const r=run('taskkill.exe',['/PID',String(pid),'/T','/F'],5000);
  return r.status===0;
}
function startWorker(slot){
  const entry=path.join(slot.path,'src','tlib.mjs');
  const child=spawn(process.execPath,[entry,'agent'],{
    cwd:slot.path,detached:true,windowsHide:true,stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:DATA,TLIB_DEPLOYMENT_COMMIT:slot.commit}
  });
  child.unref();return child.pid;
}
async function waitTarget(ms){
  const end=Date.now()+ms;
  while(Date.now()<end){
    const h=await health(700);
    if(h&&h.ok&&h.commit===TARGET&&h.build===BUILD)return h;
    await sleep(300);
  }
  return null;
}
function ensureSlot(){
  const v=readJson(path.join(SLOT,'VERIFIED.json'));
  const entry=path.join(SLOT,'src','tlib.mjs');
  const boot=path.join(SLOT,'scripts','bootstrap-node.cjs');
  const hidden=path.join(SLOT,'scripts','launch-hidden.vbs');
  if(!v||v.commit!==TARGET)throw new Error('VERIFIED_SLOT_MISSING_OR_WRONG_COMMIT');
  if(!fs.existsSync(entry)||!fs.existsSync(boot)||!fs.existsSync(hidden))throw new Error('SLOT_ESSENTIAL_FILE_MISSING');
  const src=fs.readFileSync(entry,'utf8');
  if(!src.includes("const APP_BUILD = '"+BUILD+"'"))throw new Error('SLOT_BUILD_NOT_V063');
  new Function(fs.readFileSync(boot,'utf8'));
  return {entry,boot,hidden};
}
function installLaunchers(slotFiles){
  fs.copyFileSync(slotFiles.boot,BOOT);
  fs.copyFileSync(slotFiles.hidden,HIDDEN);

  const startup=path.join(process.env.APPDATA,'Microsoft','Windows','Start Menu','Programs','Startup','TLIB-PC-Agent.vbs');
  const startupText=[
    'Set sh = CreateObject("WScript.Shell")',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    'nodePath = sh.ExpandEnvironmentStrings("%ProgramFiles%\\nodejs\\node.exe")',
    'If Not fso.FileExists(nodePath) Then nodePath = "node.exe"',
    'boot = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\\TLIB-PC\\bootstrap-node.cjs")',
    'args = Chr(34) & nodePath & Chr(34) & " " & Chr(34) & boot & Chr(34) & " --no-open"',
    'sh.Run args, 0, False'
  ].join('\r\n');
  fs.writeFileSync(startup,startupText,'ascii');

  const desktop=path.join(process.env.USERPROFILE,'Desktop');
  const make=path.join(DATA,'make-final-shortcut.vbs');
  const lnk=path.join(desktop,'TLIB.lnk');
  const vbs=[
    'Set sh = CreateObject("WScript.Shell")',
    'Set fso = CreateObject("Scripting.FileSystemObject")',
    'lnkPath = sh.ExpandEnvironmentStrings("%USERPROFILE%\\Desktop\\TLIB.lnk")',
    'Set lnk = sh.CreateShortcut(lnkPath)',
    'lnk.TargetPath = sh.ExpandEnvironmentStrings("%SystemRoot%\\System32\\wscript.exe")',
    'lnk.Arguments = Chr(34) & sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\\TLIB-PC\\launch-hidden.vbs") & Chr(34)',
    'lnk.WorkingDirectory = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\\TLIB-PC")',
    'lnk.Description = "TLIB - Bibliotheque intelligente"',
    'lnk.IconLocation = sh.ExpandEnvironmentStrings("%SystemRoot%\\System32\\SHELL32.dll,220")',
    'lnk.Save'
  ].join('\r\n');
  fs.writeFileSync(make,vbs,'ascii');
  const cr=run('cscript.exe',['//nologo',make],5000);

  // Fallback clickable launcher if .lnk creation is blocked by Windows.
  const fallback=path.join(desktop,'TLIB.vbs');
  fs.writeFileSync(fallback,[
    'Set sh = CreateObject("WScript.Shell")',
    'sh.Run Chr(34) & sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\\TLIB-PC\\launch-hidden.vbs") & Chr(34), 0, False'
  ].join('\r\n'),'ascii');

  return {startup,lnk,lnk_exists:fs.existsSync(lnk),shortcut_status:cr.status,fallback};
}
function cleanupArtifacts(){
  const names=[
    'audit-shortcut.vbs','create-shortcut.vbs','audit-shortcut.vbs','shortcut-audit.txt',
    'run-preflight-v063.vbs','preflight-v063.cjs','run-make-slot.vbs','make-slot.cjs',
    'install-bundle.cjs','install-bundle-lite.cjs','incoming-runtime-bundle.ndjson'
  ];
  const removed=[];
  for(const n of names){const p=path.join(DATA,n);try{fs.rmSync(p,{force:true,recursive:true});removed.push(n)}catch{}}
  for(const port of [8797,8799,8813]){const pid=portPid(port);if(pid){kill(pid);removed.push('port-'+port+'-pid-'+pid)}}
  return removed;
}
async function simulateClicks(){
  const before=await health(900);
  const p1=spawn('wscript.exe',[HIDDEN],{detached:true,windowsHide:true,stdio:'ignore'});p1.unref();
  const p2=spawn('wscript.exe',[HIDDEN],{detached:true,windowsHide:true,stdio:'ignore'});p2.unref();
  await sleep(2200);
  const after=await health(900);
  return {
    before_pid:before&&before.pid||null,
    after_pid:after&&after.pid||null,
    stable:!!(before&&after&&before.pid===after.pid&&after.commit===TARGET&&after.build===BUILD)
  };
}
async function rollback(reason){
  if(!previous||!previous.commit||!previous.path)return {ok:false,reason:'NO_PREVIOUS_SLOT'};
  const h=await health(500);if(h&&h.pid)kill(h.pid);else{const p=portPid(8787);if(p)kill(p)}
  startWorker(previous);
  const end=Date.now()+14000;let rh=null;
  while(Date.now()<end){rh=await health(700);if(rh&&rh.ok&&rh.commit===previous.commit)break;await sleep(350)}
  if(rh&&rh.ok){writeJson(CURRENT,{...previous,pid:rh.pid,rollback_at:now(),rollback_reason:reason});return {ok:true,health:rh}}
  return {ok:false,reason:'ROLLBACK_HEALTH_FAILED'};
}

(async()=>{
  const result={sealed:false,started_at:now(),target_commit:TARGET,target_build:BUILD,gates:{}};
  try{
    const slotFiles=ensureSlot();
    result.gates.slot={pass:true};

    const installed=installLaunchers(slotFiles);
    result.gates.launchers={pass:fs.existsSync(BOOT)&&fs.existsSync(HIDDEN)&&fs.existsSync(installed.startup)&&(installed.lnk_exists||fs.existsSync(installed.fallback)),...installed};

    result.cleaned=cleanupArtifacts();

    const desired={commit:TARGET,path:SLOT,build:BUILD,activated_at:now()};
    writeJson(CURRENT,desired);

    let h=await health(800);
    if(!h||!h.ok||h.commit!==TARGET||h.build!==BUILD){
      const owner=h&&h.pid?h.pid:portPid(8787);if(owner)kill(owner);
      await sleep(500);
      startWorker(desired);
      h=await waitTarget(15000);
    }
    result.gates.runtime={pass:!!h,health:h};
    if(!h)throw new Error('TARGET_HEALTH_FAILED');

    writeJson(CURRENT,{...desired,pid:h.pid,activated_at:now(),sealed_candidate:true});
    writeJson(LASTGOOD,{...desired,pid:h.pid,activated_at:now(),sealed_candidate:true});

    const clicks=await simulateClicks();
    result.gates.double_click={pass:clicks.stable,...clicks};
    if(!clicks.stable)throw new Error('DOUBLE_CLICK_NOT_IDEMPOTENT');

    const listener=portPid(8787);
    result.gates.port={pass:listener===h.pid,listener_pid:listener,health_pid:h.pid};
    if(listener!==h.pid)throw new Error('PORT_OWNER_MISMATCH');

    result.sealed=true;
    result.completed_at=now();
    writeJson(CURRENT,{...desired,pid:h.pid,activated_at:now(),sealed:true});
    writeJson(LASTGOOD,{...desired,pid:h.pid,activated_at:now(),sealed:true});
  }catch(e){
    result.error=String(e.stack||e);
    result.rollback=await rollback(String(e.message||e));
    result.completed_at=now();
  }
  writeJson(RESULT,result);
  process.exit(result.sealed?0:2);
})();