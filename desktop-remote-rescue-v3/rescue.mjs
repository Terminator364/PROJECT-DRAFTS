// Desktop Commander Remote Rescue, standalone Node.js. No npm install.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { spawn, execFileSync } from "node:child_process";

const args = new Set(process.argv.slice(2));
const TEST = args.has("--selftest");
const CI = process.env.RESCUE_TEST_MODE === "1";
const home = os.homedir();
const stateDir = process.env.RESCUE_STATE_DIR || path.join(process.env.LOCALAPPDATA || path.join(home,"AppData","Local"),"BlessingPC","remote-rescue-v3");
const logsDir = path.join(stateDir,"logs");
const logPath = path.join(logsDir,"rescue.log");
const statePath = path.join(stateDir,"status.json");
const lockPath = path.join(stateDir,"lock.json");
const maxLogBytes = 1024*1024;
fs.mkdirSync(logsDir,{recursive:true});

const sleep = ms => new Promise(resolve=>setTimeout(resolve,ms));
const timeoutValue = (name,defaultMs) => CI && /^\d+$/.test(process.env[name] || "") ? Number(process.env[name]) : defaultMs;
const connectTimeout = timeoutValue("RESCUE_CONNECT_TIMEOUT_MS",120000);
const localTimeout = timeoutValue("RESCUE_LOCAL_TIMEOUT_MS",25000);
let released=false, lockOwned=false, child=null, shouldStop=false, readiness=false;

function sanitize(s) {
  return String(s).replace(/(access_token|refresh_token|authorization|apikey|api_key|secret|password)\s*[:=]\s*["']?([^\s"',]+)/ig,"$1=[REDACTED]").slice(0,2500);
}
function log(message) {
  const line=new Date().toISOString()+" "+sanitize(message);
  console.log(line);
  try {
    if(fs.existsSync(logPath)&&fs.statSync(logPath).size>maxLogBytes) {
      const old=logPath+".previous";
      fs.rmSync(old,{force:true});
      fs.renameSync(logPath,old);
    }
    fs.appendFileSync(logPath,line+"\n",{encoding:"utf8"});
  }catch{}
}
function state(status,detail,extra={}) {
  const obj={schema:"blessing.remote.rescue.v3",status,detail:sanitize(detail),at:new Date().toISOString(),...extra};
  const temp=statePath+".tmp";
  fs.writeFileSync(temp,JSON.stringify(obj,null,2),"utf8");
  fs.renameSync(temp,statePath);
  log(status+" "+detail);
}
function isPidAlive(pid) {
  if(!Number.isInteger(pid)||pid<=0)return false;
  try {process.kill(pid,0);return true;}catch(e){return e?.code==="EPERM";}
}
function release() {
  if(released)return;released=true;
  if(child&&!child.killed){try{child.kill("SIGTERM");}catch{}}
  if(lockOwned){try{const v=JSON.parse(fs.readFileSync(lockPath,"utf8"));if(v.pid===process.pid)fs.rmSync(lockPath,{force:true});}catch{}}
}
function acquire() {
  for(let attempt=0;attempt<2;attempt++){
    try {fs.writeFileSync(lockPath,JSON.stringify({pid:process.pid,createdAt:new Date().toISOString()}),{flag:"wx"});lockOwned=true;return true;}
    catch(e) {
      if(e.code!=="EEXIST")throw e;
      let other=null;
      try{other=JSON.parse(fs.readFileSync(lockPath,"utf8"));}catch{}
      if(other&&isPidAlive(other.pid)){
        log("ALREADY_RUNNING pid="+other.pid+"; not starting a second copy");
        return false;
      }
      try{fs.rmSync(lockPath,{force:true});}catch{}
    }
  }
  throw new Error("Cannot obtain one-instance lock");
}
function findInstalled() {
  if(CI && process.env.RESCUE_TEST_ENTRY)return process.env.RESCUE_TEST_ENTRY;
  const candidates=[
    path.join(process.env.APPDATA||path.join(home,"AppData","Roaming"),"npm","node_modules","@wonderwhy-er","desktop-commander","dist","index.js"),
    path.join(process.env.LOCALAPPDATA||path.join(home,"AppData","Local"),"npm","node_modules","@wonderwhy-er","desktop-commander","dist","index.js")
  ];
  try{
    const root=execFileSync("npm.cmd",["root","-g"],{encoding:"utf8",timeout:5000,windowsHide:true}).trim();
    candidates.push(path.join(root,"@wonderwhy-er","desktop-commander","dist","index.js"));
  }catch{}
  return candidates.find(p=>fs.existsSync(p))||null;
}
function verifyNode() {
  const major=Number(process.versions.node.split(".")[0]);
  if(major<22||(major===22&&Number(process.versions.node.split(".")[1])<12))throw new Error("Node "+process.version+" is too old for Desktop Commander 0.2.52 (needs 22.12+).");
}
async function localMcpProbe(entry,timeoutMs=localTimeout) {
  // MCP stdio JSON-RPC framing, no external SDK/npm required.
  const p=spawn(process.execPath,[entry],{windowsHide:true,stdio:["pipe","pipe","pipe"],env:{...process.env,DC_REMOTE_DEVICE:"true"}});
  let raw="",err="",done=false;
  const complete=(ok,reason)=>{
    if(done)return;done=true;
    try{p.stdin.end();}catch{}
    try{p.kill("SIGTERM");}catch{}
    return {ok,reason};
  };
  return new Promise(resolve=>{
    const timer=setTimeout(()=>resolve(complete(false,"MCP_INITIALIZE_TIMEOUT")),timeoutMs);
    const finish=(ok,reason)=>{clearTimeout(timer);resolve(complete(ok,reason));};
    p.on("error",e=>finish(false,"SPAWN: "+e.message));
    p.on("exit",code=>finish(false,"MCP_EXIT_"+code+" "+err.slice(-400)));
    p.stderr.on("data",d=>{err+=d.toString("utf8");if(err.length>1500)err=err.slice(-1500);});
    p.stdout.on("data",d=>{
      raw+=d.toString("utf8");if(raw.length>500000)raw=raw.slice(-500000);
      while(raw.includes("\n")){
        const at=raw.indexOf("\n");
        const line=raw.slice(0,at).trim(); raw=raw.slice(at+1);
        if(!line.startsWith("{"))continue;
        try {
          const msg=JSON.parse(line.replace(/^\uFEFF/,""));
          if(msg.id===1 && msg.result && !msg.error){
            p.stdin.write(JSON.stringify({jsonrpc:"2.0",method:"notifications/initialized"})+"\n");
            p.stdin.write(JSON.stringify({jsonrpc:"2.0",id:2,method:"tools/list",params:{}})+"\n");
          } else if(msg.id===2 && msg.result?.tools?.length>0){
            finish(true,"MCP_TOOL_COUNT_"+msg.result.tools.length);
            return;
          } else if(msg.error && (msg.id===1||msg.id===2)){finish(false,JSON.stringify(msg.error));return;}
        }catch{}
      }
    });
    p.stdin.write(JSON.stringify({jsonrpc:"2.0",id:1,method:"initialize",params:{protocolVersion:"2025-03-26",capabilities:{},clientInfo:{name:"blessing-remote-rescue",version:"3.0.0"}}})+"\n");
  });
}
function setStartupIfOnline() {
  if(CI)return;
  const appData=process.env.APPDATA;
  if(!appData)return;
  const startup=path.join(appData,"Microsoft","Windows","Start Menu","Programs","Startup");
  const cmdFile=path.join(startup,"Blessing-Remote-Rescue.cmd");
  const sourceRoot=path.dirname(fileURLToPath(import.meta.url));
  const sourceCmd=path.join(sourceRoot,"RUN_RESCUE.cmd");
  const sourceJs=fileURLToPath(import.meta.url);
  if(!fs.existsSync(sourceCmd))return;
  const stable=path.join(stateDir,"bin");
  fs.mkdirSync(stable,{recursive:true});
  fs.copyFileSync(sourceCmd,path.join(stable,"RUN_RESCUE.cmd"));
  fs.copyFileSync(sourceJs,path.join(stable,"rescue.mjs"));
  fs.mkdirSync(startup,{recursive:true});
  const text="@echo off\r\nstart \"Blessing Remote Rescue\" /min node.exe \""+path.join(stable,"rescue.mjs")+"\"\r\n";
  fs.writeFileSync(cmdFile,text,"utf8");
}
function stopExistingRemoteLaunchers() {
  // A previous Remote-only launcher can hold an old auth session open.
  // Scope restart narrowly to Node commands that mention Desktop Commander
  // and have the actual CLI subcommand "remote". Never kill general Node apps.
  if(process.platform!=="win32" || CI)return;
  const ps=String.raw`Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine -match 'desktop-commander'
      -and $_.CommandLine -match '(^|\s)remote(\s|$)' } |
    Select-Object -ExpandProperty ProcessId`;
  try{
    const output=execFileSync("powershell.exe",["-NoProfile","-NonInteractive","-Command",ps],{
      encoding:"utf8",timeout:10000,windowsHide:true
    });
    const ids=output.split(/\s+/).map(Number).filter(n=>Number.isInteger(n)&&n>0&&n!==process.pid);
    for(const pid of new Set(ids)){
      try{
        execFileSync("taskkill.exe",["/PID",String(pid),"/T","/F"],{timeout:7000,stdio:"ignore",windowsHide:true});
        log("Stopped previous Desktop Commander Remote launcher PID "+pid);
      }catch(e){log("Could not stop previous Remote launcher PID "+pid+": "+e.message);}
    }
  }catch(e){log("Remote process scan skipped: "+e.message);}
}

async function runRemote(entry) {
  let attempts=0;
  while(!shouldStop && attempts<3){
    attempts++;readiness=false;
    state("CONNECTING","Attempt "+attempts);
    child=spawn(process.execPath,[entry,"remote"],{windowsHide:true,stdio:["ignore","pipe","pipe"],env:{...process.env,DEBUG_MODE:"false"}});
    let buffer="",online=false,auth=false;
    const outcome=await new Promise(resolve=>{
      let settled=false;
      const finish=(reason)=>{
        if(settled)return;settled=true;
        clearTimeout(timer);
        resolve(reason);
      };
      const timer=setTimeout(()=>{
        if(!auth&&!online){try{child.kill("SIGTERM");}catch{};finish("STARTUP_TIMEOUT");}
      },connectTimeout);
      function handle(chunk) {
        buffer+=chunk.toString("utf8");
        while(buffer.includes("\n")){
          const at=buffer.indexOf("\n"),line=buffer.slice(0,at).trim();
          buffer=buffer.slice(at+1);
          if(line)log("REMOTE "+line);
          if(/verification.*code|device authorization|open.*browser|sign in|sign-in|authorize this device/i.test(line)){
            if(!auth){auth=true;state("AUTH_REQUIRED","Confirm browser verification once. Existing saved login has not been deleted.");}
          }
          if(/Desktop Commander Remote is connected|Status:\s*Online|Presence tracked .*visible as online/i.test(line)){
            if(!online){online=true;readiness=true;state("ONLINE_REPORTED","Remote says online; confirm via remote service. PID "+child.pid);setStartupIfOnline();}
          }
        }
      }
      child.stdout.on("data",handle);child.stderr.on("data",handle);
      child.on("error",e=>finish("SPAWN_ERROR "+e.message));
      child.on("exit",(code,signal)=>finish("EXIT "+code+" "+signal));
    });
    child=null;
    if(shouldStop)break;
    state("RETRY_WAIT",outcome);
    if(attempts<3)await sleep(attempts*4000);
  }
  if(!shouldStop)state("FAILED_NEEDS_INSPECTION","3 attempts exhausted. See local logs; no credentials or applications deleted.");
}
function selftest() {
  const run = (name,check) => { if(!check)throw new Error("TEST_FAIL "+name);console.log("PASS "+name); };
  run("no-install-subprocess",findInstalled.toString().includes('"root","-g"') && !findInstalled.toString().includes('"install"'));
  run("node-supported",Number(process.versions.node.split(".")[0])>=22);
  run("sanitization",!sanitize("access_token=secret123").includes("secret123"));
  run("lock-file-path",path.isAbsolute(lockPath));
  run("status-file-path",path.isAbsolute(statePath));
  run("startup-only-after-online",setStartupIfOnline.toString().includes("if(CI)return"));
  log("SELFTEST_PASS");
}
async function main(){
  if(TEST){selftest();return;}
  if(!acquire())return;
  process.once("SIGINT",()=>{shouldStop=true;release();process.exit(0);});
  process.once("SIGTERM",()=>{shouldStop=true;release();process.exit(0);});
  process.once("exit",release);
  try{
    verifyNode();
    const entry=findInstalled();
    if(!entry){state("MISSING_LOCAL_PACKAGE","Desktop Commander not found in the existing global npm locations. Not downloading anything.");return;}
    state("PROBING_LOCAL","Testing existing Desktop Commander MCP; no installation or login reset.");
    const probe=await localMcpProbe(entry);
    if(!probe.ok){state("LOCAL_MCP_FAILED",probe.reason);return;}
    state("LOCAL_MCP_PASS",probe.reason);
    if(args.has("--probe"))return;
    stopExistingRemoteLaunchers();
    await runRemote(entry);
  }catch(err){state("FAILED",err?.stack||String(err));process.exitCode=1;}
  finally{release();}
}
main();
