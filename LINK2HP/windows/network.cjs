'use strict';
const http=require('node:http'),https=require('node:https'),dns=require('node:dns').promises,net=require('node:net');
const banned=['.local','.localhost','.internal','.test','.invalid','.onion'];
function isPublicIPv4(ip){if(net.isIP(ip)!==4)return false;const a=ip.split('.').map(Number);
 if([0,10,127].includes(a[0])||a[0]>=224||a[0]===169&&a[1]===254||a[0]===172&&a[1]>=16&&a[1]<=31||a[0]===192&&a[1]===168||a[0]===100&&a[1]>=64&&a[1]<=127||a[0]===198&&[18,19].includes(a[1])||a[0]===192&&a[1]===0||a[0]===192&&a[1]===88||a[0]===198&&a[1]===51||a[0]===203&&a[1]===0&&a[2]===113||a[0]===192&&a[1]===0&&a[2]===2)return false;
 return true;
}
function classify(raw){if(typeof raw!=='string'||!raw.trim()||raw.length>4096)throw Error('INVALID_LINK');const v=raw.trim();
 if(v.startsWith('magnet:')){const u=new URL(v);if(!/^urn:btih:([a-f\d]{40}|[a-z2-7]{32})$/i.test(u.searchParams.get('xt')||''))throw Error('INVALID_MAGNET');return{kind:'magnet',canonical:v}}
 let url;try{url=new URL(v)}catch{throw Error('INVALID_URL')}
 if(!['http:','https:'].includes(url.protocol))throw Error('INVALID_SCHEME');if(url.username||url.password)throw Error('URL_AUTH_NOT_ALLOWED');
 const host=url.hostname.toLowerCase().replace(/^\[|\]$/g,'');if(!host.includes('.')||banned.some(s=>host.endsWith(s))||net.isIP(host)===6||net.isIP(host)===4&&!isPublicIPv4(host))throw Error('UNSAFE_HOST');
 url.hash='';return{kind:/\.torrent$/i.test(url.pathname)?'torrent_url':'url',canonical:url.toString()};
}
async function secureGet(url,{maxBytes=1024*1024,timeoutMs=15000,maxRedirects=4,onChunk=null,streamOnly=false,probeOnly=false}={}){
 let current=classify(url).canonical;if(current.startsWith('magnet:'))throw Error('NOT_HTTP');
 for(let count=0;count<=maxRedirects;count++){
  const parsed=new URL(current);const h=parsed.hostname;let ip;
  if(net.isIP(h)){if(!isPublicIPv4(h))throw Error('UNSAFE_IP');ip=h}
  else{const addresses=await dns.lookup(h,{family:4,all:true});if(!addresses.length||addresses.some(a=>!isPublicIPv4(a.address)))throw Error('UNSAFE_DNS');ip=addresses[0].address}
  const transport=parsed.protocol==='https:'?https:http;
  const out=await new Promise((resolve,reject)=>{
   const req=transport.get(current,{timeout:timeoutMs,lookup:(_h,_opt,cb)=>cb(null,ip,4),headers:{'User-Agent':'LINK2HP/1.0','Accept':'*/*','Accept-Encoding':'identity'},maxHeaderSize:16384},res=>{
    const code=res.statusCode||0;
    if([301,302,303,307,308].includes(code)){res.resume();return resolve({redirect:res.headers.location||''})}
    if(code<200||code>=300){res.resume();return reject(Error('HTTP_'+code))}
    const size=Number(res.headers['content-length']||0);if(size>maxBytes && (!probeOnly || /text\/html/i.test(res.headers['content-type']||''))){res.destroy();return reject(Error('TOO_LARGE'))}
    if(probeOnly && !/text\/html/i.test(res.headers['content-type']||'') && !/\.torrent([?#]|$)/i.test(current)){res.destroy();return resolve({headers:res.headers,body:Buffer.alloc(0),finalUrl:current})}
    let total=0,parts=[];res.on('data',chunk=>{try{total+=chunk.length;if(total>maxBytes)throw Error('TOO_LARGE');if(onChunk)onChunk(chunk);else if(!streamOnly)parts.push(chunk)}catch(e){res.destroy(e)}});
    res.on('error',reject);res.on('end',()=>resolve({headers:res.headers,body:Buffer.concat(parts),finalUrl:current}));
   });req.on('timeout',()=>req.destroy(Error('TIMEOUT')));req.on('error',reject);
  });
  if(out.redirect){if(count===maxRedirects)throw Error('REDIRECT_LIMIT');current=classify(new URL(out.redirect,current).toString()).canonical;continue}
  return out;
 }
 throw Error('REDIRECT_LIMIT');
}
function parseCandidates(html,base){const out=[],seen=new Set();const re=/href\s*=\s*["']([^"']{1,2048})["']/gi;let m;
 while((m=re.exec(html))&&out.length<12){let link=m[1].replace(/&amp;/g,'&');if(link.startsWith('magnet:')){}else{try{link=new URL(link,base).toString()}catch{continue}}
 let item;try{item=classify(link)}catch{continue};if(item.kind!=='magnet'&&!/\.(torrent|pdf|zip|iso|mp4|mp3|mkv)(\?|$)/i.test(link))continue;
 if(seen.has(link))continue;seen.add(link);out.push({url:link.length>512?link.slice(0,512):link,label:item.kind==='magnet'?'Magnet':new URL(link).hostname.slice(0,70),kind:item.kind});
 }return out;
}
module.exports={classify,isPublicIPv4,secureGet,parseCandidates};
