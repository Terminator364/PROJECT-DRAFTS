'use strict';
/* Wi-Fi networks measured by the WINDOWS HP, never inferred from Android.
   Safe boundaries: known saved profiles only, no password access, no shell. */
const os=require('node:os');
const path=require('node:path');
const {execFile}=require('node:child_process');
const NETSH=process.platform==='win32'?path.join(process.env.SystemRoot||'C:\\Windows','System32','netsh.exe'):'netsh';
const clean=s=>String(s||'').trim();
const safeName=s=>typeof s==='string' && s.length>0 && s.length<=128 && !/[\x00-\x1f]/.test(s);
function parseProfiles(raw){
  const names=new Set();
  for(const line of String(raw).split(/\r?\n/)){
    const m=line.match(/^\s*(?:All User Profile|Current User Profile|Profil\s+(?:Tous les utilisateurs|utilisateur actuel|tous les utilisateurs|Utilisateur actuel))\s*:\s*(.+?)\s*$/i);
    if(m && safeName(m[1].trim()))names.add(m[1].trim());
  }
  return names;
}
function getBand(value){
  const s=String(value).replace(',','.').trim().toLowerCase();
  if(/(?:^|\s)5\s*(?:ghz|g)/.test(s))return '5 GHz';
  if(/2\.4\s*(?:ghz|g)/.test(s))return '2,4 GHz';
  if(/6\s*(?:ghz|g)/.test(s))return '6 GHz';
  const channel=Number.parseInt(s,10);
  if(channel>=1&&channel<=14)return '2,4 GHz';
  if(channel>=32&&channel<=177)return '5 GHz';
  return null;
}
function parseNetworks(raw){
  const items=new Map();let current=null;
  function ensure(name){if(!items.has(name))items.set(name,{ssid:name,bands:new Set(),signal:0});return items.get(name)}
  for(const line of String(raw).split(/\r?\n/)){
    const ssid=line.match(/^\s*SSID\s+\d+\s*:\s*(.*)$/i);
    if(ssid){current=safeName(ssid[1])?ensure(ssid[1].trim()):null;continue}
    if(!current)continue;
    const band=line.match(/^\s*(?:Band|Bande)\s*:\s*(.+)$/i);
    const channel=line.match(/^\s*(?:Channel|Canal)\s*:\s*(\d+)\s*$/i);
    const signal=line.match(/^\s*Signal\s*:\s*(\d+)\s*%/i);
    const b=band?getBand(band[1]):channel?getBand(channel[1]):null;
    if(b)current.bands.add(b);
    if(signal)current.signal=Math.max(current.signal,Math.min(100,+signal[1]));
  }
  return [...items.values()].map(x=>({...x,bands:[...x.bands]}));
}
function parseCurrent(raw){
  let ssid=null,band=null;
  for(const line of String(raw).split(/\r?\n/)){
    let m=line.match(/^\s*SSID\s*:\s*(.+?)\s*$/i);
    if(m&&safeName(m[1]))ssid=m[1].trim();
    m=line.match(/^\s*(?:Band|Bande|Channel|Canal)\s*:\s*(.+?)\s*$/i);
    if(m)band=getBand(m[1])||band;
  }
  return {ssid,band};
}
function preference(item){
  const name=String(item.ssid||'').toLowerCase().replace(',','.');
  if(!name.includes('starlink'))return 9;
  // A 2.4-labelled extender can broadcast on 5 GHz: prefer primary SSID,
  // not the actual frequency of an unrelated extender.
  if(/(?:^|[\s_-])ext(?:$|[\s_-])|extender/.test(name))return 6;
  if(/(?:^|[\s_-])5\s*(?:ghz|g)(?:$|[\s_-])/.test(name))return 0;
  if(/(?:^|[\s_-])2\.?4\s*(?:ghz|g)(?:$|[\s_-])/.test(name))return 1;
  if(item.bands.length===1 && item.bands.includes('5 GHz'))return 2;
  if(item.bands.length===1 && item.bands.includes('2,4 GHz'))return 3;
  return 4;
}
function assemble({networks,profiles,current}){
  const known=profiles instanceof Set?profiles:new Set(profiles);
  return networks.map(x=>({
    ssid:x.ssid,bands:x.bands,signal:x.signal,
    saved:known.has(x.ssid),current:current.ssid===x.ssid,
    priority:preference(x),
    // Same SSID on both bands: Windows adapter decides the exact AP/band.
    band_control:x.bands.length===1?'BY_SSID':'ADAPTER_DECIDES'
  })).sort((a,b)=>Number(b.current)-Number(a.current)||a.priority-b.priority||Number(b.saved)-Number(a.saved)||b.signal-a.signal||a.ssid.localeCompare(b.ssid));
}
function createWifiManager({run}={}){
  const exec=run||((args)=>new Promise((resolve,reject)=>{
    execFile(NETSH,['wlan',...args],{windowsHide:true,timeout:8500,maxBuffer:400000,shell:false},(err,stdout)=>err?reject(err):resolve(stdout));
  }));
  let switching=false;
  async function list(){
    let results;
    try{results=await Promise.all([
      exec(['show','networks','mode=bssid']),exec(['show','profiles']),exec(['show','interfaces'])
    ])}catch(e){return {available:false,reason:'WINDOWS_WIFI_UNAVAILABLE',networks:[],current:null}}
    const current=parseCurrent(results[2]);
    const networks=assemble({networks:parseNetworks(results[0]),profiles:parseProfiles(results[1]),current});
    return {available:true,host:os.hostname().slice(0,60),current:current.ssid,current_band:current.band,networks};
  }
  async function connect(ssid){
    if(switching)return {state:'BUSY'};
    if(!safeName(ssid))return {state:'INVALID_SSID'};
    const info=await list();
    if(!info.available)return {state:'WINDOWS_WIFI_UNAVAILABLE'};
    const target=info.networks.find(n=>n.ssid===ssid);
    if(!target)return {state:'NETWORK_NOT_VISIBLE'};
    if(!target.saved)return {state:'CONFIGURE_ON_HP'};
    if(target.current)return {state:'ALREADY_CONNECTED',ssid};
    switching=true;
    try{
      // Only the exact profile returned by Windows may be used. No passwords exposed.
      await exec(['connect',`name=${ssid}`,`ssid=${ssid}`]);
      return {state:'SWITCH_REQUESTED',ssid};
    }catch(e){return {state:'CONNECT_FAILED',reason:'WINDOWS_REJECTED_CONNECTION'}}
    finally{switching=false}
  }
  function best(info){
    // Only the two explicitly named PRIMARY Starlink bands are automatic.
    // Never auto-switch to an extender or another person's network.
    return info.networks.filter(x=>x.saved&&x.priority<=1&&x.signal>=35)
      .sort((a,b)=>a.priority-b.priority||b.signal-a.signal)[0]||null;
  }
  return {list,connect,best};
}
module.exports={createWifiManager,parseNetworks,parseProfiles,parseCurrent,preference,assemble,getBand,safeName};
