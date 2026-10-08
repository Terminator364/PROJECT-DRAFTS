import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawn} from "node:child_process";
import {fileURLToPath} from "node:url";
const dir=path.dirname(fileURLToPath(import.meta.url));
const script=path.join(dir,"rescue.mjs");
const fixture=path.join(dir,"mock-entry.mjs");
const temp=fs.mkdtempSync(path.join(os.tmpdir(),"Blessing Rescue With Spaces "));
function run(extraArgs=[],vars={},max=7000,stopOn){
  return new Promise((resolve,reject)=>{
    const env={...process.env,RESCUE_TEST_MODE:"1",RESCUE_TEST_ENTRY:fixture,RESCUE_STATE_DIR:path.join(temp,"case-"+Math.random().toString(16).slice(2)),...vars};
    const child=spawn(process.execPath,[script,...extraArgs],{env,stdio:["ignore","pipe","pipe"],windowsHide:true});
    let out="",err="",ended=false;
    const finish=(status)=>{if(ended)return;ended=true;clearTimeout(timer);try{child.kill();}catch{};resolve({status,out,err,env});};
    const timer=setTimeout(()=>finish("TIMEOUT"),max);
    child.stdout.on("data",d=>{
      out+=d.toString();
      if(stopOn&&out.includes(stopOn))finish("MATCHED");
    });
    child.stderr.on("data",d=>{err+=d.toString();});
    child.on("exit",code=>finish(code));
    child.on("error",e=>reject(e));
  });
}
try{
  const st=await run(["--selftest"],{RESCUE_TEST_ALLOW_STARTUP:"1",APPDATA:path.join(temp,"Fake User AppData With Spaces")});
  assert.equal(st.status,0,st.out+" "+st.err);console.log("PASS SELFTEST + ISOLATED STARTUP");
  const probe=await run(["--probe"],{},10000);
  assert.equal(probe.status,0,probe.out+" "+probe.err);
  assert.match(probe.out,/LOCAL_MCP_PASS/);console.log("PASS MCP MOCK PROBE");
  const online=await run([],{RESCUE_MOCK_SCENARIO:"online"},7000,"ONLINE_REPORTED");
  assert.equal(online.status,"MATCHED",online.out+" "+online.err);
  console.log("PASS ONLINE SIMULATION");
  const auth=await run([],{RESCUE_MOCK_SCENARIO:"auth",RESCUE_CONNECT_TIMEOUT_MS:"300"},5000,"AUTH_REQUIRED");
  assert.equal(auth.status,"MATCHED",auth.out+" "+auth.err);
  console.log("PASS AUTH GATE, NO CREDENTIAL RESET");
  const timeout=await run([],{RESCUE_MOCK_SCENARIO:"hang",RESCUE_CONNECT_TIMEOUT_MS:"180"},5000,"RETRY_WAIT");
  assert.equal(timeout.status,"MATCHED",timeout.out+" "+timeout.err);
  console.log("PASS HUNG REMOTE DETECTION");
  console.log("RESCUE V3 MOCK SUITE PASS");
}finally {
  fs.rmSync(temp,{recursive:true,force:true});
}
