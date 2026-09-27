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

  for(const [tab,pane] of [['l0','l0'],['l1','l1'],['l2','l2'],['manager','manager'],['tech','tech']]){
    const tabs=[...new Set([...markup.matchAll(new RegExp('data-'+tab+'-tab="([^"]+)"','g'))].map(m=>m[1]))];
    const panes=[...new Set([...markup.matchAll(new RegExp('data-'+pane+'-pane="([^"]+)"','g'))].map(m=>m[1]))];
    const miss=tabs.filter(x=>!panes.includes(x));
    miss.length?fail('ui-subpages-'+tab,miss.join(',')):ok('ui-subpages-'+tab,tabs.length+' tabs');
  }

  const essentials=['navBack','commandOpen','homeSearchBtn','librarySearchBtn','chatSend','refreshDeepQueue','runUiAuditBtn','drawerClose'];
  const absent=essentials.filter(id=>!markup.includes('id="'+id+'"'));
  absent.length?fail('ui-essential-controls',absent.join(',')):ok('ui-essential-controls',essentials.length+' controls');
}

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
