import { readFileSync, existsSync } from 'node:fs';
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

try{
  const psFiles=['bootstrap-tlib.ps1','install-windows.ps1','launch-tlib.ps1','update-tlib.ps1'].map(name=>join(APP,'scripts',name));
  const full=process.argv.includes('--full')||process.env.TLIB_VERIFY_FULL==='1';
  if(full){
    const q=s=>"'"+String(s).replace(/'/g,"''")+"'";
    const cmd=[
      "$ErrorActionPreference='Stop'",
      "$files=@("+psFiles.map(q).join(',')+")",
      "$bad=@()",
      "foreach($p in $files){$tokens=$null;$errs=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errs);if($errs.Count -gt 0){$bad += ($p+' :: '+(($errs|ForEach-Object {$_.Message}) -join ' | '))}}",
      "if($bad.Count -gt 0){$bad|ForEach-Object {Write-Error $_};exit 1}"
    ].join(';');
    execFileSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',cmd],{stdio:'pipe',windowsHide:true,timeout:60000});
    ok('powershell-syntax-batch',psFiles.length+' scripts · full');
  }else{
    const bad=psFiles.filter(p=>!existsSync(p)||readFileSync(p,'utf8').length<40);
    if(bad.length)throw new Error('POWERSHELL_FILE_INVALID '+bad.join(','));
    ok('powershell-syntax-batch',psFiles.length+' scripts · fast staging mode; full parser available with --full');
  }
}catch(e){fail('powershell-syntax-batch',String(e.stderr||e.message||e).slice(0,1000));}

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

  for(const [tab,pane] of [['l0','l0'],['l1','l1'],['l2','l2'],['l3','l3'],['manager','manager'],['tech','tech']]){
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
    "bindPaneTabs('#l3Subnav [data-l3-tab]','[data-l3-pane]','l3Tab','l3Pane'",
    "bindPaneTabs('#managerSubnav [data-manager-tab]','[data-manager-pane]','managerTab','managerPane'",
    "bindPaneTabs('#techSubnav [data-tech-tab]','[data-tech-pane]','techTab','techPane'"
  ];
  const missingBindings=expectedBindings.filter(x=>!js.includes(x));
  missingBindings.length?fail('ui-router-contract',missingBindings.join(' || ')):ok('ui-router-contract','explicit button/pane keys for all workspaces');

  const legacyBindings=[
    "bindPaneTabs('#l0Subnav [data-l0-tab]','[data-l0-pane]','l0Tab');",
    "bindPaneTabs('#l1Subnav [data-l1-tab]','[data-l1-pane]','l1Tab');",
    "bindPaneTabs('#l2Subnav [data-l2-tab]','[data-l2-pane]','l2Tab');",
    "bindPaneTabs('#managerSubnav [data-manager-tab]','[data-manager-pane]','managerTab');",
    "bindPaneTabs('#techSubnav [data-tech-tab]','[data-tech-pane]','techTab');"
  ];
  const legacyFound=legacyBindings.filter(x=>js.includes(x));
  legacyFound.length?fail('ui-router-no-legacy',legacyFound.join(' || ')):ok('ui-router-no-legacy');

  const essentials=['navBack','commandOpen','homeSearchBtn','librarySearchBtn','chatSend','refreshDeepQueue','refreshL2Queue','refreshL3','runUiAuditBtn','drawerClose','phoneCreateBtn','phoneRefreshBtn','phoneRevokeBtn','phoneQr','phoneSessionList','phoneRemainingMax','phonePairState','mgrPhoneShortcut','mgrPhoneCard','mgrBuildBadge','updateAutoMode','updateAutoDetail','updateProgressBar','updateProgressText','l2ProgressBar','l2QueueTable','l2L3Ready','l2Comprehension','l1DrillSearchBtn','l1DrillPrev','l1DrillNext','l1DrillResults','l2ProfileSearchBtn','l2ProfilePrev','l2ProfileNext','l2Results','l3Ready','l3Total','l3Pending','l3ProgressBar','l3Results'];

  // Global actionability contract: no visible control may ship dead.
  const declarativeButtonAttrs=['data-view','data-go','data-action','data-l0-tab','data-l1-tab','data-l2-tab','data-l3-tab','data-manager-tab','data-tech-tab','data-detail-tab','data-l2mini-tab','data-chat','data-phone-minutes','data-event-filter','data-l0-jump','data-depth-filter','data-filter','data-tag','data-drawer-go','data-manager-node','data-manager-tab-jump','data-cmd-index','data-mobile-view','data-l1-drill-open','data-l1-drill','data-l2-drill-open','data-l2-kind','data-l2-jump','data-l3-jump','data-score-band','data-chat-resource','data-manager-jump','data-tech-jump','data-l1-jump'];
  const buttonAttrs=[...markup.matchAll(/<button\b([^>]*)>/g)].map(m=>m[1]);
  const deadButtons=[];
  for(const attrs of buttonAttrs){
    if(declarativeButtonAttrs.some(a=>attrs.includes(a+'=')))continue;
    const id=(attrs.match(/\bid="([^"]+)"/)||[])[1]||'';
    if(!id){deadButtons.push('(sans id)');continue}
    const direct=js.includes("el('#"+id+"').onclick")||js.includes('el("#'+id+'").onclick')||js.includes("el('#"+id+"').onchange")||js.includes("el('#"+id+"').oninput")||js.includes("el('#"+id+"').addEventListener");
    if(!direct)deadButtons.push(id);
  }
  deadButtons.length?fail('ui-all-buttons-actionable',deadButtons.join(',')):ok('ui-all-buttons-actionable',buttonAttrs.length+' buttons');

  const fieldAttrs=[...markup.matchAll(/<(?:input|select)\b([^>]*)>/g)].map(m=>m[1]);
  const deadFields=[];
  for(const attrs of fieldAttrs){
    const id=(attrs.match(/\bid="([^"]+)"/)||[])[1]||'';
    if(!id||!js.includes("el('#"+id+"')"))deadFields.push(id||'(sans id)');
  }
  deadFields.length?fail('ui-all-fields-actionable',deadFields.join(',')):ok('ui-all-fields-actionable',fieldAttrs.length+' fields');
  const absent=essentials.filter(id=>!markup.includes('id="'+id+'"'));
  absent.length?fail('ui-essential-controls',absent.join(',')):ok('ui-essential-controls',essentials.length+' controls');

  const phoneDurations=[30,180,360].filter(n=>markup.includes('data-phone-minutes="'+n+'"'));
  phoneDurations.length===3?ok('phone-ui-durations','30/180/360'):fail('phone-ui-durations',phoneDurations.join(','));
  markup.includes('data-manager-tab="phone"')&&markup.includes('data-manager-pane="phone"')?ok('phone-ui-workspace','Manager > Téléphone / QR'):fail('phone-ui-workspace');
  markup.includes('data-manager-tab="phone">📱 Téléphone / QR</button>')?ok('phone-ui-label','explicit QR entry'):fail('phone-ui-label');
  html.includes('<script src="/vendor/qrcode.min.js"></script>')?ok('phone-ui-qr-loader'):fail('phone-ui-qr-loader');
  (js.includes("if(v==='phone')loadPhoneStatus()")||js.includes("if(v==='phone')return loadPhoneStatus()"))?ok('phone-ui-lazy-load'):fail('phone-ui-lazy-load');
  js.includes("el('#mgrPhoneShortcut').onclick=openManagerPhone")&&js.includes("el('#mgrPhoneCard').onclick=openManagerPhone")?ok('phone-ui-discoverability','header + overview card'):fail('phone-ui-discoverability');
  js.includes('startUpdatePolling()')&&js.includes("#updateProgressBar")?ok('update-ui-progress','live polling + bar'):fail('update-ui-progress');
  markup.includes('id="mobileMenuToggle"')&&markup.includes('id="mobileBottomNav"')&&markup.includes('id="mobileBackdrop"')?ok('mobile-ui-shell','off-canvas + bottom-nav'):fail('mobile-ui-shell');
  html.includes('.side.mobile-open')&&html.includes('.mobile-bottom-nav')&&html.includes('@media(max-width:760px)')?ok('mobile-ui-responsive-css'):fail('mobile-ui-responsive-css');
  js.includes('openMobileMenu')&&js.includes('closeMobileMenu')&&js.includes('syncMobileNav')?ok('mobile-ui-navigation-js'):fail('mobile-ui-navigation-js');
  markup.includes('id="globalActivity"')&&html.includes('.subpane.pane-loading')?ok('ui-global-loading-contract'):fail('ui-global-loading-contract');
  js.includes("attempts=method==='GET'?3:1")?ok('ui-read-retry-contract'):fail('ui-read-retry-contract');
  js.includes('UPDATE_EXPECT_RESTART')&&js.includes('reconnexion automatique')&&js.includes('location.reload()')?ok('ui-update-reconnect-contract'):fail('ui-update-reconnect-contract');
  markup.includes('id="projectFeedbackCard"')&&markup.includes('id="projectSyncBadge"')?ok('ui-project-feedback-panel'):fail('ui-project-feedback-panel');
  js.includes('ensureUiRuntimeSync')&&js.includes('PAGE_BUILD')?ok('ui-runtime-autosync'):fail('ui-runtime-autosync');
  markup.includes('data-l1-pane="drill"')&&markup.includes('id="l1DrillResults"')&&markup.includes('id="l1DrillSearch"')?ok('l1-ui-real-drilldown'):fail('l1-ui-real-drilldown');
  js.includes('function openL1Drill')&&js.includes("/api/l1/drilldown")&&js.includes("openL1Drill('complete')")?ok('l1-ui-drilldown-routing'):fail('l1-ui-drilldown-routing');
  markup.includes('id="l2ProfileNav"')&&markup.includes('id="l2ProfileSearch"')&&markup.includes('id="l2Results"')?ok('l2-ui-real-drilldown'):fail('l2-ui-real-drilldown');
  js.includes('function openL2Drill')&&js.includes("/api/l2/drilldown")&&js.includes("openL2Drill('profiles')")?ok('l2-ui-drilldown-routing'):fail('l2-ui-drilldown-routing');
  js.includes('function sendChatQuery')&&js.includes("/api/chat/search")&&!js.includes("var items=await loadLibrary(q)")?ok('chat-dedicated-search'):fail('chat-dedicated-search');
  markup.includes('data-l1-drill-open="complete"')&&markup.includes('data-l2-drill-open="eligible"')?ok('overview-metrics-actionable'):fail('overview-metrics-actionable');
  markup.includes('data-action="l1-taxonomy"')?ok('l1-taxonomy-actionable'):fail('l1-taxonomy-actionable');
  markup.includes('id="projectFeedbackCard"')&&markup.includes('data-manager-jump="updates"')&&markup.includes('data-tech-jump="events"')?ok('manager-project-feedback-actionable'):fail('manager-project-feedback-actionable');
  markup.includes('data-l1-jump="deep"')&&markup.includes('data-manager-jump="pipeline"')?ok('manager-resource-indicators-actionable'):fail('manager-resource-indicators-actionable');
  markup.includes('data-l2-tab="pipeline"')&&markup.includes('data-l2-pane="pipeline"')?ok('l2-ui-pipeline-pane'):fail('l2-ui-pipeline-pane');
  markup.includes('id="l2BasePending"')&&markup.includes('id="l2DeepDone"')&&markup.includes('id="l2ProgressBar"')?ok('l2-ui-metrics'):fail('l2-ui-metrics');
  js.includes('loadL2Queue')&&js.includes("if(v==='pipeline')return loadL2Queue()")?ok('l2-ui-lazy-queue'):fail('l2-ui-lazy-queue');
  const l2tabs=[...new Set([...markup.matchAll(/data-l2-tab="([^"]+)"/g)].map(m=>m[1]))];
  l2tabs.length===5?ok('l2-ui-five-subpages',l2tabs.join(',')):fail('l2-ui-five-subpages',String(l2tabs.length));
  markup.includes('id="l2L3Ready"')&&markup.includes('id="l2Comprehension"')&&markup.includes('V4 sémantique')?ok('l2-v4-dashboard'):fail('l2-v4-dashboard');
  markup.includes('id="l2MigrationLegacy"')&&markup.includes('id="l2NeverProfiled"')&&js.includes('legacy_remaining')&&js.includes('never_profiled')?ok('l2-v4-migration-transparency'):fail('l2-v4-migration-transparency');
  js.includes('data-l2mini-tab="understand"')&&js.includes('data-l2mini-tab="use"')&&js.includes('data-l2mini-tab="architecture"')&&js.includes('data-l2mini-tab="proof"')?ok('l2-v4-nested-dossier-tabs'):fail('l2-v4-nested-dossier-tabs');
  js.includes('dossier.definition_fr')&&js.includes('installation_lancement_fr')&&js.includes('a_verifier_fr')?ok('l2-v4-french-dossier-render'):fail('l2-v4-french-dossier-render');
  markup.includes('V4 sémantique')&&js.includes('identity_confidence')&&js.includes('role_fr')?ok('l2-v4-semantic-identity-ui'):fail('l2-v4-semantic-identity-ui');
  js.includes('identity_basis_fr')&&js.includes('identity_source')&&js.includes('Pourquoi ce rôle ?')?ok('l2-v4-identity-trace-ui'):fail('l2-v4-identity-trace-ui');
  markup.includes('Recherche locale multiterme dans L1 + L2 V4 + L3')&&js.includes('RELAXED_CONCEPTS')&&js.includes('search_coverage')&&js.includes('pertinence ')?ok('semantic-search-ui'):fail('semantic-search-ui');
  js.includes('l3pack.best_for')&&js.includes('l3pack.strengths')&&js.includes('l3pack.selection_checks')&&js.includes('l3pack.readiness')?ok('l3-decision-ui'):fail('l3-decision-ui');
  markup.includes('<section id="l3" class="section">')&&markup.includes('id="l3Results"')&&markup.includes('data-l3-tab="packs"')?ok('l3-real-workspace'):fail('l3-real-workspace');
  js.includes('async function loadL3')&&js.includes('/api/l3/list')?ok('l3-ui-data'):fail('l3-ui-data');
  markup.includes('id="phoneSessionList"')&&markup.includes('id="phoneRemainingMax"')&&markup.includes('id="phoneQrType"')?ok('phone-session-dashboard'):fail('phone-session-dashboard');
  js.includes('phoneRemainingLabel')&&js.includes('setInterval(renderPhoneCountdowns,1000)')?ok('phone-live-countdown'):fail('phone-live-countdown');
  js.includes('/api/mobile/session/revoke')&&js.includes('data-revoke-phone-session')?ok('phone-individual-revoke'):fail('phone-individual-revoke');
  js.includes('access_qr_url')&&js.includes("qrType=pair?'PAIRAGE':hasSession?'ACCÈS':'AUCUN'")?ok('phone-access-qr'):fail('phone-access-qr');
}

try{
  const qr=readFileSync(join(APP,'public','vendor','qrcode.min.js'),'utf8');
  qr.includes('QRCode')?ok('phone-qr-asset',qr.length+' bytes'):fail('phone-qr-asset','unexpected content');
}catch(e){fail('phone-qr-asset',e.message)}

existsSync(join(APP,'public','vendor-qrcode.min.js'))?fail('phone-qr-no-legacy-duplicate','legacy duplicate present'):ok('phone-qr-no-legacy-duplicate');

try{
  const src=readFileSync(join(APP,'src','tlib.mjs'),'utf8');
  const autoChecks=[
    ['dashboard-build-injection',src.includes("replaceAll('__TLIB_BUILD__',APP_BUILD)")&&src.includes("replaceAll('__TLIB_COMMIT__',APP_COMMIT)")],
    ['last-good-soak',src.includes('LAST_GOOD_SOAK_MS=15*60*1000')&&src.includes('promoteCurrentToLastGoodAfterSoak')],
    ['auto-update-arm',src.includes('startAutonomousUpdates()')],
    ['auto-update-stage',src.includes('runUpdaterStage')],
    ['auto-update-idle-guard',src.includes('AUTO_UPDATE_IDLE_GUARD_MS')],
    ['auto-update-interval',src.includes('AUTO_UPDATE_INTERVAL_MS=10*60*1000')],
    ['auto-update-first-check',src.includes('AUTO_UPDATE_FIRST_DELAY_MS=45*1000')],
    ['auto-update-channel',src.includes("channel:'release/tlib-hybrid-v2-stable'")],
    ['l2-continuous-base-v4',src.includes('function l2BaseStep')&&src.includes("'L1_DOSSIER_FR_V4'")&&src.includes('dossier_json')&&src.includes('retrieval_text')],
    ['l2-continuous-deep',src.includes('async function l2DeepStep')&&src.includes('L2_README_RATE_RESERVE=2800')],
    ['l2-continuous-scheduler',src.includes('async function scheduledPipelineStep')&&src.includes("return 'PARALLEL_L1_L2'")],
    ['l2-l1-parallel-safe',src.includes('pipelineCycle%4===0')&&src.includes('pipelineCycle%12===6')],
    ['scheduler-no-overlap',src.indexOf('pipelineCycle%20===9')<src.indexOf('pipelineCycle%12===6')&&src.indexOf('pipelineCycle%12===6')<src.indexOf('pipelineCycle%4===0')],
    ['l2-queue-api',src.includes("/api/l2/queue")],
    ['l2-entry-quality-gate',src.includes('const L2_MIN_L1_SCORE=65')],
    ['l1-drilldown-api',src.includes('function l1Drilldown')&&src.includes("/api/l1/drilldown")],
    ['l2-drilldown-api',src.includes('function l2Drilldown')&&src.includes("/api/l2/drilldown")],
    ['chat-search-api',src.includes('function chatSearch')&&src.includes("/api/chat/search")],
    ['resource-l2-evidence',src.includes('evidence:parse(l2raw.evidence_json)')&&src.includes('readme_signals:parse(l2raw.readme_signals_json)')],
    ['l2-v4-ruleset',src.includes("L2_RULESET_VERSION='2026.09-v4-semantic'")],
    ['l2-v4-french-fields',src.includes('definition_fr')&&src.includes('fonctionnement_fr')&&src.includes('installation_lancement_fr')&&src.includes('preuves_fr')&&src.includes('handoff_l3')],
    ['l2-v4-deep-sources',src.includes('rootInventory')&&src.includes('manifestFacts')&&src.includes('L2_V4_README_STRUCTURE_MANIFESTS')],
    ['l2-v4-legacy-rebuild',src.includes("coalesce(l.source_version,'')<>?")&&src.includes('L2_RULESET_VERSION')],
    ['l2-v4-drill-current-only',src.includes("eligible:{from:")&&src.includes("base_pending:{from:")&&src.includes("AND l.source_version='")&&src.includes("l.entity_id IS NULL")],
    ['l2-v4-french-ui-data',src.includes("language_ui='fr'")||src.includes("'fr','[]'")],
    ['l3-engine',src.includes('function l3Step')&&src.includes('function l3ActionPackFromDossier')&&src.includes('CREATE TABLE IF NOT EXISTS l3_actions')],
    ['l1-functional-taxonomy',src.includes("TAXONOMY_VERSION='2026.09-v2-functional'")&&src.includes('Développement/Outils IA & Agents')&&src.includes('Réseau & IoT/Accès distant')&&src.includes('priority=(p)=>')],
    ['l1-reclassify-no-downgrade',src.includes("coalesce(deep_status,'')='DONE'")&&src.includes("coalesce(l1_stage,'')='L1_COMPLETE'")&&src.includes("THEN 'L1_COMPLETE'")],
    ['l2-primary-role-engine',src.includes('const L2_ROLE_RULES=')&&src.includes('function l2PrimaryRole')&&src.includes('identity_confidence')&&src.includes('role_id')],
    ['l2-identity-evidence-trace',src.includes('identity_source')&&src.includes('identity_basis_fr')&&src.includes("README_IDENTITY")&&src.includes("GITHUB_DESCRIPTION")&&src.includes("SIGNAL_FALLBACK")],
    ['l2-role-before-capabilities',src.includes('const role=l2PrimaryRole(r,sig,signals)')&&src.includes("const purposes=uniqText([role.purpose")],
    ['l2-quality-readiness',src.includes('role.confidence>=0.75')&&src.includes('score>=82')&&src.includes('interpretation_version:2')],
    ['l2-v4-migration-stats',src.includes('legacy_remaining:legacyRemaining')&&src.includes('never_profiled:neverProfiled')&&src.includes('const basePending=legacyRemaining+neverProfiled')],
    ['l2-purpose-role-filter',src.includes('function l2PurposeSignals')&&src.includes("'remote-desktop':['Réseau / communication','Sécurité / authentification','Application mobile']")],
    ['semantic-real-witnesses',src.includes("description:'Blazing-fast remote access'")&&src.includes("'getinsomnia/insomnia'")&&src.includes("'stablyai/orca'")&&src.includes("'rustdesk/rustdesk'")],
    ['l1-api-testing-theme',src.includes("'Développement/API & Tests'")&&src.includes('api client|api testing|api development|http client|rest client')&&src.includes("if(/^Développement\\/API & Tests/.test(p))return 108")],
    ['search-fts-schema',src.includes('CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5')&&src.includes('SEARCH_INDEX_VERSION')],
    ['search-fts-ranking',src.includes('bm25(search_fts')&&src.includes('resolveSearchMatch')&&src.includes('ALL_CONCEPTS_AVAILABLE')&&src.includes('RELAXED_CONCEPTS')&&src.includes('searchRanked')&&src.includes('search_coverage')],
    ['search-concept-coverage-gate',src.includes('resolved.strict_hits>0?1')&&src.includes('coverage*180')],
    ['search-legacy-fallback',src.includes('legacy_summary')&&src.includes('legacy_dossier')&&src.includes('legacy_action')&&src.includes('SEARCH_INDEX_VERSION=\'2026.09-v3-semantic-with-legacy-fallback\'')],
    ['semantic-selftest',src.includes('SEMANTIC_ROLE_FAIL')&&src.includes('SEMANTIC_THEME_FAIL')&&src.includes('SEARCH_CONCEPT_SELFTEST_FAIL')&&src.includes('SEARCH_TOKEN_BOUNDARY_SELFTEST_FAIL')&&src.includes('SEARCH_FRENCH_CONCEPT_SELFTEST_FAIL')],
    ['semantic-purpose-selftest',src.includes('SEMANTIC_PURPOSE_FILTER_FAIL')&&src.includes('semantic_roles:7')&&src.includes('semantic_themes:4')],
    ['search-short-token-boundary',src.includes('function searchFtsTerm')&&src.includes('function searchTextHasTerm')&&src.includes("searchFtsTerm('gui')!=='gui'")],
    ['search-software-priority',src.includes("kind==='Projet logiciel'?10")&&src.includes("Catalogue de ressources'?-18")],
    ['search-audit-cli',src.includes("cmd === 'search-audit'")&&src.includes('searchAuditSnapshot')&&src.includes('live_readme_probe')],
    ['search-agent-fast-start',src.includes("if (cmd === 'agent')")&&src.includes('startDashboard();')&&!src.slice(src.indexOf("if (cmd === 'agent')"),src.indexOf("throw new Error('UNKNOWN_COMMAND",src.indexOf("if (cmd === 'agent')"))).includes('ensureSearchIndex(')],
    ['search-l1-l2-l3-index',src.includes('syncSearchEntity')&&src.includes('l.dossier_json')&&src.includes('a.action_json')&&src.includes('l.retrieval_text')],
    ['search-bilingual-concepts',src.includes('searchConceptGroups')&&src.includes("['database','sql','postgres','mysql','sqlite','redis']")&&src.includes("['local','ai','llm','localai','ollama']")],
    ['search-background-index',src.includes("if (cmd === 'worker')")&&src.includes('reclassifyExisting();')&&src.includes('ensureSearchIndex(true);')],
    ['manifest-depth-extraction',src.includes("p==='cargo.toml'")&&src.includes("p==='go.mod'")&&src.includes("p==='pyproject.toml'")&&src.includes("docker compose up")&&src.includes("pip install -r requirements.txt")],
    ['readme-command-depth',src.includes('pipx|uv|poetry|conda')&&src.includes('helm|kubectl')&&src.includes('matchAll(/\\x60')],
    ['l3-decision-support',src.includes('relevance_summary')&&src.includes('best_for')&&src.includes('selection_checks')&&src.includes('readiness')&&src.includes('research_terms')],
    ['l3-api',src.includes("/api/l3/list")&&src.includes('l3Stats()')]
  ];
  for(const [id,pass] of autoChecks) pass?ok(id):fail(id);
  const phoneChecks=[
    ['phone-server-durations',src.includes('[30,180,360]')],
    ['phone-server-pair-code',src.includes('phoneCodeFromBytes')],
    ['phone-server-state',src.includes('phone-share.json')],
    ['phone-server-cookie',src.includes("PHONE_COOKIE='tlib_m'")],
    ['phone-server-lan-bind',src.includes("server.listen(port, '0.0.0.0'")],
    ['phone-server-rate-limit',src.includes('phoneClaimAllowed')],
    ['phone-server-pair-api',src.includes("/api/mobile/pair")],
    ['phone-server-claim-api',src.includes("/api/mobile/claim")],
    ['phone-server-revoke-api',src.includes("/api/mobile/revoke")],
    ['phone-server-read-only',src.includes('PHONE_READ_ONLY')],
    ['phone-server-fragment-pair',src.includes("/pair#t=")],
    ['phone-server-persistent-pair',src.includes('pair_offer')&&src.includes('schema:2')],
    ['phone-server-session-id',src.includes('duration_minutes')&&src.includes('remaining_seconds')],
    ['phone-server-session-revoke',src.includes('/api/mobile/session/revoke')&&src.includes('revokePhoneSession')],
    ['phone-server-access-qr',src.includes('access_qr_url')]
  ];
  for(const [id,pass] of phoneChecks) pass?ok(id):fail(id);
}catch(e){fail('phone-server-contract',e.message)}

try{
  const updater=readFileSync(join(APP,'scripts','slot-update.mjs'),'utf8');
  updater.includes("const UPDATE_CHANNEL='release/tlib-hybrid-v2-stable'")?ok('update-stable-channel'):fail('update-stable-channel');
  updater.includes("branches/'+encodeURIComponent(UPDATE_CHANNEL)")?ok('update-stable-lookup'):fail('update-stable-lookup');
  updater.includes('STALE_UPDATE_LOCK_REMOVED')?ok('update-stale-lock-recovery'):fail('update-stale-lock-recovery');
  updater.includes('freePreflightPort')?ok('update-dynamic-preflight-port'):fail('update-dynamic-preflight-port');
  updater.includes('BOOTSTRAP_SYNC')?ok('update-bootstrap-self-refresh'):fail('update-bootstrap-self-refresh');
  updater.includes("reason:'pre-activation-last-good'")&&!updater.includes('writeJson(CURRENT,active);writeJson(LASTGOOD,active)')?ok('update-delayed-last-good'):fail('update-delayed-last-good');
  updater.includes('MANIFEST_PATH_UNSAFE')&&updater.includes('MAX_TOTAL_BYTES')?ok('update-manifest-safety'):fail('update-manifest-safety');
  updater.includes('FETCH_TIMEOUT_MS=45000')?ok('update-slow-network-profile'):fail('update-slow-network-profile');
  updater.includes("taskkill.exe',['/PID',String(n),'/F']")&&!updater.includes("taskkill.exe',['/PID',String(n),'/T','/F']")?ok('update-self-survival-no-tree-kill'):fail('update-self-survival-no-tree-kill');
  updater.includes('stopBackgroundWorker()')&&updater.includes('UPDATER_SURVIVED_STOP')?ok('update-self-survival-contract'):fail('update-self-survival-contract');
  updater.includes("const PROGRESS=join(DATA,'slot-update-progress.json')")&&updater.includes("progress('DOWNLOAD'")&&updater.includes("progress('DONE'")?ok('update-progress-contract'):fail('update-progress-contract');
}catch(e){fail('update-stable-contract',e.message)}

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
