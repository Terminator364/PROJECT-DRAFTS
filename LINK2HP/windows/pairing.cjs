'use strict';
/* Local-only peer discovery and explicit one-click Windows approval. Never broadcast secrets. */
const dgram=require('node:dgram');
const crypto=require('node:crypto');
const os=require('node:os');
function privateIPv4(ip){
 const a=String(ip).replace(/^::ffff:/,'').split('.').map(Number);
 return a.length===4&&a.every(n=>Number.isInteger(n)&&n>=0&&n<=255) &&
 (a[0]===10||(a[0]===172&&a[1]>=16&&a[1]<=31)||(a[0]===192&&a[1]===168));
}
function safeDeviceLabel(s){return typeof s==='string' ? s.trim().slice(0,56).replace(/[<>"'&]/g,'') : 'Téléphone Android';}
function newTicket(){return crypto.randomBytes(24).toString('hex')}
function createPairing({certificatePin,port=17642,config,writeConfig,now=()=>Date.now()}){
 const pending=new Map(); const deadline=120000;
 function prune(){for(const [id,v] of pending)if(now()-v.created>deadline)pending.delete(id)}
 function begin(req){
  prune(); if(!privateIPv4(req.socket.remoteAddress))throw Error('LOCAL_NETWORK_ONLY');
  const deviceId=String(req.body.device_id||'');
  if(!/^[0-9a-f-]{36}$/i.test(deviceId))throw Error('BAD_DEVICE_ID');
  if(pending.size>=8)throw Error('TOO_MANY_PENDING');
  const id=newTicket(),label=safeDeviceLabel(req.body.label);
  pending.set(id,{deviceId,label,address:req.socket.remoteAddress,created:now(),approved:false,token:null});
  return {pair_id:id,waiting:true,ttl_seconds:120};
 }
 function poll(req,id,deviceId){
  prune();const p=pending.get(id);
  if(!p||p.deviceId!==deviceId||p.address!==req.socket.remoteAddress)return {state:'EXPIRED'};
  if(!p.approved)return {state:'WAITING'};
  pending.delete(id);
  return {state:'APPROVED',token:p.token,certPin:certificatePin,port};
 }
 function approve(id){prune();const p=pending.get(id);if(!p||p.approved)return false;
  const token=crypto.randomBytes(32).toString('hex');
  const peers=Array.isArray(config.devices)?config.devices:[];
  const filtered=peers.filter(x=>x.deviceId!==p.deviceId);
  filtered.push({deviceId:p.deviceId,label:p.label,token,approvedAt:new Date().toISOString()});
  config.devices=filtered.slice(-16);writeConfig(config);
  p.token=token;p.approved=true;return true;
 }
 function list(){prune();return [...pending].filter(([,p])=>!p.approved).map(([id,p])=>({id,label:p.label,created:p.created,address:p.address}));}
 function authorized(token){
  if(!/^[a-f0-9]{64}$/i.test(token||''))return false;
  const peers=(config.devices||[]).map(p=>p.token).filter(Boolean);
  return peers.some(x=>x.length===token.length&&crypto.timingSafeEqual(Buffer.from(x),Buffer.from(token)));
 }
 return {begin,poll,approve,list,authorized,privateIPv4};
}
function createDiscovery({pin,port=17642,discoverPort=17644}){
 const sock=dgram.createSocket({type:'udp4',reuseAddr:true});
 sock.on('message',(bytes,rinfo)=>{
  if(!privateIPv4(rinfo.address)||bytes.toString()!=='LINK2HP_DISCOVER_V2')return;
  const packet=Buffer.from(JSON.stringify({magic:'LINK2HP_HERE_V2',port,pin,name:os.hostname().slice(0,48)}));
  sock.send(packet,rinfo.port,rinfo.address,()=>{});
 });
 return {start:()=>new Promise((resolve,reject)=>{sock.once('error',reject);sock.bind(discoverPort,'0.0.0.0',resolve)}),close:()=>new Promise(r=>sock.close(r))};
}
module.exports={privateIPv4,createPairing,createDiscovery};
