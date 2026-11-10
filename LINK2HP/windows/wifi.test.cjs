'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');
const {parseProfiles,parseNetworks,parseCurrent,createWifiManager}=require('./wifi.cjs');
const scan=`SSID 1 : Starlink_2.4G\n    Signal : 81%\n    Band : 2.4 GHz\n    Channel : 6\nSSID 2 : Starlink_5G\n    Signal : 95%\n    Bande : 5 GHz\n    Canal : 44\nSSID 3 : Famille\n    Signal : 50%\n    Canal : 11`;
const prof=`    All User Profile     : Starlink_5G\n    Profil Tous les utilisateurs : Starlink_2.4G`;
test('parse HP scan: 5 GHz, 2.4 GHz, unknown network',()=>{
  const n=parseNetworks(scan);assert.equal(n.length,3);assert.deepEqual(n[1].bands,['5 GHz']);assert.deepEqual(n[0].bands,['2,4 GHz']);
});
test('saved profiles French and English; do not leak keys',()=>{
  assert.deepEqual([...parseProfiles(prof)].sort(),['Starlink_2.4G','Starlink_5G']);
});
test('connect only Windows-saved profiles, and fall back',async()=>{
  const commands=[];const run=async args=>{commands.push(args);if(args[0]==='show'&&args[1]==='networks')return scan;if(args[0]==='show'&&args[1]==='profiles')return prof;if(args[0]==='show')return 'SSID : Starlink_2.4G';return 'Connection request completed successfully';};
  const wifi=createWifiManager({run});const list=await wifi.list();assert.equal(list.networks.find(x=>x.ssid==='Starlink_5G').priority,0);
  assert.equal(wifi.best(list).ssid,'Starlink_5G');
  assert.equal((await wifi.connect('Famille')).state,'CONFIGURE_ON_HP');
  assert.equal((await wifi.connect('Starlink_5G')).state,'SWITCH_REQUESTED');
  assert.equal(commands.filter(x=>x[0]==='connect').length,1);
});
test('reject commands and invisible networks',async()=>{
  const wifi=createWifiManager({run:async x=>x[0]==='show'&&x[1]==='networks'?scan:x[0]==='show'&&x[1]==='profiles'?prof:'SSID : Starlink_2.4G'});
  assert.equal((await wifi.connect('Starlink_5G\r\nnetsh wlan delete')).state,'INVALID_SSID');
  assert.equal((await wifi.connect('123-nonexistent')).state,'NETWORK_NOT_VISIBLE');
  assert.equal(parseCurrent('SSID : Starlink_5G\nBand : 5 GHz').band,'5 GHz');
});
