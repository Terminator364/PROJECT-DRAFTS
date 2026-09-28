import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const HERE=dirname(fileURLToPath(import.meta.url));
const APP=resolve(HERE,'..');
const errors=[];
const ok=(name,detail='')=>console.log('PASS '+name+(detail?' :: '+detail:''));
const fail=(name,detail='')=>{errors.push(name+(detail?' :: '+detail:''));console.error('FAIL '+name+(detail?' :: '+detail:''));};

try{
  execFileSync(process.execPath,['--check',join(APP,'src','tlib.mjs')],{stdio:'pipe'});
  ok('node-syntax');
}catch(e){fail('node-syntax',String(e.stderr||e.message||e).slice(0,500));}

try{
  execFileSync(process.execPath,['--check',join(APP,'scripts','slot-update.mjs')],{stdio:'pipe'});
  ok('slot-updater-syntax');
}catch(e){fail('slot-updater-syntax',String(e.stderr||e.message||e).slice(0,500));}

for(const name of ['bootstrap-tlib.ps1','install-windows.ps1','launch-tlib.ps1','update-tlib.ps1']){
  try{
    const p=join(APP,'scripts',name);
    const cmd='[ScriptBlock]::Create((Get-Content -LiteralPath "'+p.replace(/"/g,'""')+'" -Raw)) | Out-Null';
    execFileSync('powershell.exe',['-NoProfile','-Command',cmd],{stdio:'pipe',windowsHide:true,timeout:10000});
    ok('powershell-syntax-'+name);
  }catch(e){fail('powershell-syntax-'+name,String(e.stderr||e.message||e).slice(0,500));}
}

let html='';
try{html=readFileSync(join(APP,'public','index.html'),'utf8');ok('ui-readable',html.length+' bytes');}
catch(e){fail('ui-readable',e.message);}

if(html){
  const s=html.indexOf('<script>'),e=html.lastIndexOf('</script>');
  const markup=s>=0?html.slice(0,s):html;
  if(s<0||e<=s) fail('ui-script-present');
  else{
    const js=html.slice(s+8,e);
    try{new Function(js);ok('ui-javascript-syntax');}catch(err){fail('ui-javascript-syntax',err.message);}
  }

  const ids=[...markup.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
  const dup=[...new Set(ids.filter((x,i)=>ids.indexOf(x)!==i))];
  dup.length?fail('ui-unique-ids',dup.join(',')):ok('ui-unique-ids',ids.length+' ids');

  const views=[...new Set([...markup.matchAll(/data-view="([^"]+)"/g)].map(m=>m[1]))];
  const missingViews=views.filter(v=>!markup.includes('<section id="'+v+'" class="section'));
  missingViews.length?fail('ui-main-views',missingViews.join(',')):ok('ui-main-views',views.join(','));

  const gos=[...new Set([...markup.matchAll(/data-go="([^"]+)"/g)].map(m=>m[1]))];
  const missingGo=gos.filter(v=>!markup.includes('<section id="'+v+'" class="section'));
  missingGo.length?fail('ui-go-targets',missingGo.join(',')):ok('ui-go-targets',gos.length+' targets');

  for(const [tab,pane] of [['l0','l0'],['l1','l1'],['l2','l2'],['phone','phone'],['manager','manager'],['tech','tech']]){
    const tabs=[...new Set([...markup.matchAll(new RegExp('data-'+tab+'-tab="([^"]+)"','g'))].map(m=>m[1]))];
    const panes=[...new Set([...markup.matchAll(new RegExp('data-'+pane+'-pane="([^"]+)"','g'))].map(m=>m[1]))];
    const miss=tabs.filter(x=>!panes.includes(x));
    const orphan=panes.filter(x=>!tabs.includes(x));
    if(miss.length||orphan.length) fail('ui-subpages-'+tab,'missing='+miss.join('|')+' orphan='+orphan.join('|'));
    else ok('ui-subpages-'+tab,tabs.length+' exact pairs');
  }

  const js=s>=0&&e>s?html.slice(s+8,e):'';
  const expectedBindings=[
    "bindPaneTabs('#l0Subnav [data-l0-tab]','[data-l0-pane]','l0Tab','l0Pane'",
    "bindPaneTabs('#l1Subnav [data-l1-tab]','[data-l1-pane]','l1Tab','l1Pane'",
    "bindPaneTabs('#l2Subnav [data-l2-tab]','[data-l2-pane]','l2Tab','l2Pane'",
    "bindPaneTabs('#phoneSubnav [data-phone-tab]','[data-phone-pane]','phoneTab','phonePane'",
    "bindPaneTabs('#managerSubnav [data-manager-tab]','[data-manager-pane]','managerTab','managerPane'",
    "bindPaneTabs('#techSubnav [data-tech-tab]','[data-tech-pane]','techTab','techPane'"
  ];
  const missingBindings=expectedBindings.filter(x=>!js.includes(x));
  missingBindings.length?fail('ui-router-contract',missingBindings.join(' || ')):ok('ui-router-contract','explicit button/pane keys for all workspaces');

  const legacyBindings=[
    "bindPaneTabs('#l0Subnav [data-l0-tab]','[data-l0-pane]','l0Tab');",
    "bindPaneTabs('#l1Subnav [data-l1-tab]','[data-l1-pane]','l1Tab');",
    "bindPaneTabs('#l2Subnav [data-l2-tab]','[data-l2-pane]','l2Tab');",
    "bindPaneTabs('#phoneSubnav [data-phone-tab]','[data-phone-pane]','phoneTab');",
    "bindPaneTabs('#managerSubnav [data-manager-tab]','[data-manager-pane]','managerTab');",
    "bindPaneTabs('#techSubnav [data-tech-tab]','[data-tech-pane]','techTab');"
  ];
  const legacyFound=legacyBindings.filter(x=>js.includes(x));
  legacyFound.length?fail('ui-router-no-legacy',legacyFound.join(' || ')):ok('ui-router-no-legacy');

  const essentials=['navBack','commandOpen','homeSearchBtn','librarySearchBtn','chatSend','refreshDeepQueue','runUiAuditBtn','drawerClose','phoneRefresh','phoneExtend','phoneRotate','phoneStop','phoneCopy'];
  const absent=essentials.filter(id=>!markup.includes('id="'+id+'"'));
  absent.length?fail('ui-essential-controls',absent.join(',')):ok('ui-essential-controls',essentials.length+' controls');

  const phoneDurations=[30,90,180].filter(n=>markup.includes('data-phone-minutes="'+n+'"'));
  phoneDurations.length===3?ok('phone-ui-durations','30/90/180'):fail('phone-ui-durations',phoneDurations.join(','));
  markup.includes('data-view="phone"')&&markup.includes('id="phone"')?ok('phone-ui-workspace'):fail('phone-ui-workspace');
  js.includes("s.src='/vendor-qrcode.min.js'")?ok('phone-ui-qr-loader'):fail('phone-ui-qr-loader');
}

try{
  const qr=readFileSync(join(APP,'public','vendor-qrcode.min.js'),'utf8');
  qr.includes('QRCode=function')?ok('phone-qr-asset',qr.length+' bytes'):fail('phone-qr-asset','unexpected content');
}catch(e){fail('phone-qr-asset',e.message)}

try{
  const src=readFileSync(join(APP,'src','tlib.mjs'),'utf8');
  const phoneChecks=[
    ['phone-server-durations',src.includes('[30,90,180]')],
    ['phone-server-pair-code',src.includes('pair_code')],
    ['phone-server-state',src.includes('phone_share.json')],
    ['phone-server-cookie',src.includes('tlib_pair')],
    ['phone-server-ports',src.includes('port=8831')&&src.includes('port<=8835')],
    ['phone-server-rate-limit',src.includes('phoneRateLimited')],
    ['phone-server-api',src.includes("/api/phone/share")],
    ['phone-server-rotate',src.includes('PHONE_SHARE_ROTATED')]
  ];
  for(const [id,pass] of phoneChecks) pass?ok(id):fail(id);
}catch(e){fail('phone-server-contract',e.message)}

try{
  const src=readFileSync(join(APP,'src','tlib.mjs'),'utf8');
  const m=src.match(/const APP_BUILD = '([^']+)'/);
  if(m)ok('build-id',m[1]); else fail('build-id','APP_BUILD missing');
}catch(e){fail('build-id',e.message);}

if(errors.length){
  console.error(JSON.stringify({ok:false,errors},null,2));
  process.exit(1);
}
console.log(JSON.stringify({ok:true,checked_at:new Date().toISOString()},null,2));
