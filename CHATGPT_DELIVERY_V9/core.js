(function(){
"use strict";
const V = "9.0.0";
const CFG = {
  ROOT:"ChatGPT Delivery",
  OUT:"Ã€ envoyer", SENT:"EnvoyÃ©", FAIL:"Ã‰checs", RECEIPTS:"ReÃ§us", INBOX:"Inbox Telegram",
  XL:"XL Jobs", MANIFESTS:"Manifests",
  OWNER_CHAT_ID:"1298744015",
  CATS:["Applications-APK","PDF","Documents","Images","VidÃ©os","Audio","Archives","DonnÃ©es","Autres"],
  CLOUD_DOWNLOAD_MAX:19*1024*1024,
  CLOUD_UPLOAD_SAFE:45*1024*1024,
  CHUNK_BYTES:16*1024*1024,
  MAX_PARTS_PER_RUN:3,
  RETRIES:4
};

function setup(){
  const p=PropertiesService.getScriptProperties();
  if(!p.getProperty("TELEGRAM_BOT_TOKEN")) throw new Error("TELEGRAM_BOT_TOKEN absent.");
  ensureStorage_();
  p.setProperty("TELEGRAM_CHAT_ID", CFG.OWNER_CHAT_ID);
  safe_(()=>tg_("deleteWebhook",{drop_pending_updates:false}));
  setIdentity_(); setCommands_(); ensureTrigger_();
  sendDashboard_("home");
  processDelivery();
  return "READY_V9";
}

function processDelivery(){
  const lock=LockService.getScriptLock();
  if(!lock.tryLock(1200)) return "BUSY";
  try{
    ensureStorage_();
    processUpdates_();
    processOutbox_();
    resumeChunkJobs_();
    return "OK_V9";
  } finally { lock.releaseLock(); }
}

function status(){
  ensureStorage_();
  const p=PropertiesService.getScriptProperties();
  return {
    version:V,
    bot:!!p.getProperty("TELEGRAM_BOT_TOKEN"),
    chat:p.getProperty("TELEGRAM_CHAT_ID")||"",
    pending:countFiles_(folder_(CFG.OUT)),
    inbox:countFiles_(folder_(CFG.INBOX)),
    xl_jobs:countFiles_(folder_(CFG.XL)),
    trigger:ScriptApp.getProjectTriggers().some(t=>t.getHandlerFunction()==="processDelivery"),
    last_update:(JSON.parse(p.getProperty("CDV9_CORE_META")||"{}")).fetched_at||""
  };
}

function selfTest(){
  const checks=[];
  const p=PropertiesService.getScriptProperties();
  checks.push(["token",!!p.getProperty("TELEGRAM_BOT_TOKEN")]);
  checks.push(["chat",String(p.getProperty("TELEGRAM_CHAT_ID")||"")===CFG.OWNER_CHAT_ID]);
  checks.push(["root",!!root_()]);
  checks.push(["trigger",ScriptApp.getProjectTriggers().some(t=>t.getHandlerFunction()==="processDelivery")]);
  checks.push(["telegram_getMe",safeBool_(()=>!!tg_("getMe",{}).result)]);
  return {version:V,ok:checks.every(x=>x[1]),checks:checks};
}

function resetTelegram(){
  safe_(()=>tg_("deleteWebhook",{drop_pending_updates:false}));
  PropertiesService.getScriptProperties().deleteProperty("TELEGRAM_UPDATE_OFFSET");
  return "RESET_OK";
}

function processUpdates_(){
  const p=PropertiesService.getScriptProperties(), off=Number(p.getProperty("TELEGRAM_UPDATE_OFFSET")||0);
  const data=tg_("getUpdates",{offset:off,limit:60,timeout:0}), updates=data.result||[];
  let next=off;
  updates.forEach(u=>{
    next=Math.max(next,Number(u.update_id)+1);
    const q=u.callback_query;
    if(q && q.message && String(q.message.chat.id)===CFG.OWNER_CHAT_ID){
      safe_(()=>tg_("answerCallbackQuery",{callback_query_id:q.id}));
      handleAction_(String(q.data||"home"), q.message.message_id); return;
    }
    const m=u.message;
    if(!m || String(m.chat.id)!==CFG.OWNER_CHAT_ID) return;
    if(m.text){ handleText_(String(m.text).trim()); return; }
    handleInboundMedia_(m);
  });
  if(next!==off) p.setProperty("TELEGRAM_UPDATE_OFFSET",String(next));
}

function handleText_(t){
  const x=t.toLowerCase();
  const map={"/start":"home","/menu":"home","/status":"status","/inbox":"inbox","/outbox":"outbox","/xl":"xl","/latest":"latest","/help":"help","/selftest":"diag"};
  sendDashboard_(map[x]||"home");
}

function handleAction_(a,msgId){
  if(a==="retry") { processDelivery(); a="status"; }
  if(a==="resend_last") { resendLast_(); a="latest"; }
  editDashboard_(msgId,a);
}

function handleInboundMedia_(m){
  const info=extractMedia_(m); if(!info) return;
  const rec={direction:"IN",message_id:m.message_id,file_id:info.file_id,file_unique_id:info.file_unique_id||"",
    name:info.name,size:Number(info.size||0),kind:info.kind,mime:info.mime||"",received_at:new Date().toISOString()};
  if(rec.size<=CFG.CLOUD_DOWNLOAD_MAX){
    try{
      const blob=downloadTelegram_(rec.file_id,rec.name);
      const cat=category_(rec.name,rec.mime,rec.kind);
      const f=getOrCreate_(folder_(CFG.INBOX),cat).createFile(blob.setName(rec.name));
      rec.status="INGESTED"; rec.drive_file_id=f.getId(); receipt_(rec);
      sendNotice_("âœ… ReÃ§u vers ChatGPT", rec.name+" â€¢ "+human_(rec.size));
    }catch(e){ rec.status="RETRY_INBOUND"; rec.error=msg_(e); receipt_(rec); }
  }else{
    rec.status="XL_PENDING";
    const jf=getOrCreate_(root_(),CFG.XL);
    jf.createFile(jobName_("IN",m.message_id,rec.name),JSON.stringify(rec,null,2),MimeType.PLAIN_TEXT);
    receipt_(rec);
    sendNotice_("ðŸ§© Fichier XL enregistrÃ©",
      rec.name+" â€¢ "+human_(rec.size)+"\nLe fichier reste sur Telegram. V9 a conservÃ© son file_id et son message source. Le worker XL pourra le rÃ©cupÃ©rer sans te demander de le renvoyer.");
  }
}

function processOutbox_(){
  const out=folder_(CFG.OUT);
  CFG.CATS.forEach(cat=>{
    const fcat=getOrCreate_(out,cat), it=fcat.getFiles();
    while(it.hasNext()){
      const f=it.next();
      try{
        const n=f.getName().toLowerCase();
        if(n.endsWith(".apk")||n.endsWith(".aab")) throw new Error("APK/AAB brut interdit: emballage de transport requis avant Drive.");
        if(f.getSize()<=CFG.CLOUD_UPLOAD_SAFE) sendSmall_(f,cat);
        else createOrResumeChunkJob_(f,cat);
      }catch(e){ fail_(f,cat,msg_(e)); }
    }
  });
}

function sendSmall_(f,cat){
  const key="OUT_"+f.getId(), p=PropertiesService.getScriptProperties();
  if(p.getProperty(key)){ move_(f,CFG.SENT,cat); return; }
  const blob=driveBlob_(f.getId(),f.getName());
  const sha=sha_(blob.getBytes());
  const d=sendDocRetry_(blob,caption_(f.getName(),cat,f.getSize(),sha));
  const fileId=(d.result.document&&d.result.document.file_id)||"";
  p.setProperty(key,JSON.stringify({message_id:d.result.message_id,file_id:fileId,sha:sha}));
  rememberTelegramCache_(f.getName(),fileId,sha,f.getSize(),cat);
  receipt_({status:"DELIVERED",direction:"OUT",filename:f.getName(),drive_file_id:f.getId(),telegram_message_id:d.result.message_id,telegram_file_id:fileId,sha256:sha,size:f.getSize(),category:cat,delivered_at:new Date().toISOString()});
  move_(f,CFG.SENT,cat);
}

function createOrResumeChunkJob_(f,cat){
  const id=f.getId(), p=PropertiesService.getScriptProperties(), key="CHUNKJOB_"+id;
  let j=JSON.parse(p.getProperty(key)||"null");
  if(!j){
    const total=Math.ceil(f.getSize()/CFG.CHUNK_BYTES);
    j={id:id,name:f.getName(),cat:cat,size:f.getSize(),total:total,next:0,created_at:new Date().toISOString(),parts:[]};
    p.setProperty(key,JSON.stringify(j));
  }
  runChunkJob_(j);
}

function resumeChunkJobs_(){
  const p=PropertiesService.getScriptProperties();
  p.getKeys().filter(k=>k.indexOf("CHUNKJOB_")===0).slice(0,4).forEach(k=>{
    const j=JSON.parse(p.getProperty(k)||"null"); if(j) safe_(()=>runChunkJob_(j));
  });
}

function runChunkJob_(j){
  const p=PropertiesService.getScriptProperties(), key="CHUNKJOB_"+j.id;
  let sent=0;
  while(j.next<j.total && sent<CFG.MAX_PARTS_PER_RUN){
    const start=j.next*CFG.CHUNK_BYTES, end=Math.min(j.size-1,start+CFG.CHUNK_BYTES-1);
    const blob=driveRange_(j.id,start,end,j.name+".part"+String(j.next+1).padStart(3,"0"));
    const sha=sha_(blob.getBytes());
    const partKey="PART_"+j.id+"_"+j.next;
    if(!p.getProperty(partKey)){
      const d=sendDocRetry_(blob,"ðŸ§© "+j.name+"\nPartie "+(j.next+1)+"/"+j.total+"\nSHA-256: "+sha.substring(0,16)+"â€¦");
      const fid=(d.result.document&&d.result.document.file_id)||"";
      p.setProperty(partKey,JSON.stringify&v·¬º[fzËè}ø²¬…¨éj»l¦ë!Š9ÞÆßµ²¶ç«!iø¥z'_‰Øç{~úÇ§·ï©±ëO®Š^®Ü¤{"R8Û-®)à‰ü£‰øç{