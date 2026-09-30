import http from 'node:http';
import { mkdirSync, readFileSync, readdirSync, writeFileSync, renameSync } from 'node:fs';
import { homedir, freemem, totalmem, cpus, networkInterfaces, setPriority, constants as osConstants } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';
import { execFileSync, execFile, spawn } from 'node:child_process';
import { randomBytes, createHash, timingSafeEqual } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..');
const dataDir = process.env.TLIB_DATA_DIR || join(process.env.LOCALAPPDATA || homedir(), 'TLIB-PC');
mkdirSync(dataDir, { recursive: true });
const APP_BUILD = '2026.09.30-v0.12.0-retrieval-quality';
const STARTED_AT = new Date().toISOString();
function deploymentCommit() {
  try {
    const meta=JSON.parse(readFileSync(join(ROOT,'deployment.json'),'utf8'));
    if(meta && typeof meta.commit==='string' && /^[0-9a-f]{40}$/i.test(meta.commit)) return meta.commit;
  } catch {}
  try {
    const env=String(process.env.TLIB_DEPLOYMENT_COMMIT||'').trim();
    if(/^[0-9a-f]{40}$/i.test(env)) return env;
  } catch {}
  try { return String(execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8',windowsHide:true,stdio:['ignore','pipe','ignore'],timeout:3000})||'').trim(); }
  catch { return 'UNKNOWN'; }
}
const APP_COMMIT = deploymentCommit();
function writeRuntimeMarker() {
  try {
    writeFileSync(join(dataDir,'runtime.json'),JSON.stringify({
      pid:process.pid,build:APP_BUILD,commit:APP_COMMIT,started_at:STARTED_AT,root:ROOT,port:Number(process.env.TLIB_DASHBOARD_PORT||8787)
    },null,2));
  } catch {}
}
const dbPath = join(dataDir, 'tlib-worker.sqlite3');
const db = new DatabaseSync(dbPath);
db.exec(`
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=-4096;
PRAGMA busy_timeout=3000;
CREATE TABLE IF NOT EXISTS jobs(
  entity_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'PENDING',
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS results(
  entity_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  http_status INTEGER,
  github_id TEXT,
  node_id TEXT,
  description TEXT,
  archived INTEGER,
  fork INTEGER,
  stars INTEGER,
  language TEXT,
  license TEXT,
  topics_json TEXT,
  updated_at_github TEXT,
  pushed_at TEXT,
  default_branch TEXT,
  size_kb INTEGER,
  open_issues INTEGER,
  rate_remaining INTEGER,
  fetched_at TEXT NOT NULL,
  raw_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  level TEXT NOT NULL,
  event TEXT NOT NULL,
  detail TEXT
);
CREATE TABLE IF NOT EXISTS l2_profiles(
  entity_id TEXT PRIMARY KEY,
  human_summary TEXT,
  capabilities_json TEXT,
  use_cases_json TEXT,
  limitations_json TEXT,
  confidence REAL,
  source TEXT,
  updated_at TEXT NOT NULL
);
`);

function ensureResultColumn(name, type) {
  const cols = db.prepare('PRAGMA table_info(results)').all().map(r => String(r.name));
  if (!cols.includes(name)) db.exec('ALTER TABLE results ADD COLUMN ' + name + ' ' + type);
}
ensureResultColumn('resource_kind','TEXT');
ensureResultColumn('technology','TEXT');
ensureResultColumn('content_mode','TEXT');
ensureResultColumn('activity_status','TEXT');
ensureResultColumn('activity_days','INTEGER');
ensureResultColumn('l1_quality','TEXT');
ensureResultColumn('homepage','TEXT');
ensureResultColumn('forks_count','INTEGER');
ensureResultColumn('watchers_count','INTEGER');
ensureResultColumn('created_at_github','TEXT');
ensureResultColumn('visibility','TEXT');
ensureResultColumn('disabled','INTEGER');
ensureResultColumn('has_wiki','INTEGER');
ensureResultColumn('has_pages','INTEGER');
ensureResultColumn('has_discussions','INTEGER');
ensureResultColumn('l1_score','INTEGER');
ensureResultColumn('owner_login','TEXT');
ensureResultColumn('owner_type','TEXT');
ensureResultColumn('html_url','TEXT');
ensureResultColumn('clone_url','TEXT');
ensureResultColumn('license_name','TEXT');
ensureResultColumn('subscribers_count','INTEGER');
ensureResultColumn('network_count','INTEGER');
ensureResultColumn('has_issues','INTEGER');
ensureResultColumn('has_projects','INTEGER');
ensureResultColumn('has_downloads','INTEGER');
ensureResultColumn('is_template','INTEGER');
ensureResultColumn('l1_summary','TEXT');
ensureResultColumn('l1_stage','TEXT');
ensureResultColumn('deep_status','TEXT');
ensureResultColumn('languages_json','TEXT');
ensureResultColumn('latest_release_tag','TEXT');
ensureResultColumn('latest_release_at','TEXT');
ensureResultColumn('community_health','INTEGER');
ensureResultColumn('readme_present','INTEGER');
ensureResultColumn('primary_theme','TEXT');
ensureResultColumn('theme_path','TEXT');
ensureResultColumn('theme_tags_json','TEXT');
ensureResultColumn('theme_confidence','REAL');
ensureResultColumn('taxonomy_version','TEXT');

function ensureL2Column(name,type){
  const cols=db.prepare('PRAGMA table_info(l2_profiles)').all().map(r=>String(r.name));
  if(!cols.includes(name)) db.exec('ALTER TABLE l2_profiles ADD COLUMN '+name+' '+type);
}
ensureL2Column('stage','TEXT');
ensureL2Column('deep_status','TEXT');
ensureL2Column('score','INTEGER');
ensureL2Column('evidence_json','TEXT');
ensureL2Column('readme_signals_json','TEXT');
ensureL2Column('attempts','INTEGER');
ensureL2Column('last_error','TEXT');
ensureL2Column('source_version','TEXT');
ensureL2Column('dossier_json','TEXT');
ensureL2Column('comprehension_score','INTEGER');
ensureL2Column('l3_ready','INTEGER');
ensureL2Column('language_ui','TEXT');
ensureL2Column('deep_sources_json','TEXT');
ensureL2Column('retrieval_text','TEXT');
db.prepare("UPDATE l2_profiles SET stage=coalesce(stage,'BASE'),deep_status=coalesce(deep_status,CASE WHEN source='fixture' THEN 'NOT_APPLICABLE' ELSE 'PENDING' END),attempts=coalesce(attempts,0),source_version=coalesce(source_version,CASE WHEN source='fixture' THEN 'fixture-v1' ELSE 'legacy' END),language_ui=coalesce(language_ui,'fr'),comprehension_score=coalesce(comprehension_score,score,0),l3_ready=coalesce(l3_ready,0)").run();

db.exec(`
CREATE INDEX IF NOT EXISTS idx_jobs_status_updated ON jobs(status,updated_at);
CREATE INDEX IF NOT EXISTS idx_results_deep_fetched ON results(resource_kind,deep_status,fetched_at);
CREATE INDEX IF NOT EXISTS idx_results_stage ON results(l1_stage);
CREATE INDEX IF NOT EXISTS idx_results_fetched ON results(fetched_at);
CREATE INDEX IF NOT EXISTS idx_events_level_at ON events(level,at);
CREATE INDEX IF NOT EXISTS idx_l2_stage_status ON l2_profiles(stage,deep_status,updated_at);
CREATE INDEX IF NOT EXISTS idx_l2_score ON l2_profiles(score);
CREATE TABLE IF NOT EXISTS l3_actions(entity_id TEXT PRIMARY KEY,action_json TEXT NOT NULL,source_l2_version TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_l3_updated ON l3_actions(updated_at);
CREATE TABLE IF NOT EXISTS search_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(entity_id UNINDEXED,title,l1,l2,l3,hidden,tokenize='unicode61 remove_diacritics 2');
`);

const now = () => new Date().toISOString();
const event = (level, name, detail='') => {
  db.prepare('INSERT INTO events(at,level,event,detail) VALUES(?,?,?,?)').run(now(), level, name, String(detail).slice(0,2000));
};

function argValue(prefix, fallback) {
  const a = process.argv.find(x => x.startsWith(prefix + '='));
  return a ? a.slice(prefix.length + 1) : fallback;
}

let ghTokenCache;
let githubAuthMode = 'UNKNOWN';
function githubToken() {
  if (ghTokenCache !== undefined) return ghTokenCache;
  const fromEnv = String(process.env.GH_TOKEN || '').trim();
  if (fromEnv.length > 20) {
    ghTokenCache = fromEnv;
    githubAuthMode = 'ENV_SECURE';
    return ghTokenCache;
  }
  try {
    const t = String(execFileSync('gh',['auth','token'],{
      encoding:'utf8',windowsHide:true,stdio:['ignore','pipe','ignore'],timeout:15000
    }) || '').trim();
    if (t.length > 20) {
      ghTokenCache = t;
      githubAuthMode = 'GH_KEYRING';
      return ghTokenCache;
    }
  } catch {}
  ghTokenCache = '';
  githubAuthMode = 'PUBLIC';
  return '';
}

function warmGitHubToken() {
  if (ghTokenCache !== undefined) return Promise.resolve(ghTokenCache);
  const fromEnv=String(process.env.GH_TOKEN||'').trim();
  if(fromEnv.length>20){ghTokenCache=fromEnv;githubAuthMode='ENV_SECURE';return Promise.resolve(ghTokenCache);}
  return new Promise(resolve=>{
    execFile('gh',['auth','token'],{encoding:'utf8',windowsHide:true,timeout:15000},(err,stdout)=>{
      const t=err?'':String(stdout||'').trim();
      if(t.length>20){ghTokenCache=t;githubAuthMode='GH_KEYRING';}
      else {ghTokenCache='';githubAuthMode='PUBLIC';}
      resolve(ghTokenCache);
    });
  });
}

function nextGitHubDelay(remaining, resetSeconds) {
  if (!githubToken()) return 75000;
  const floor = 1200;
  const rem = Number(remaining);
  const resetMs = Number(resetSeconds || 0) * 1000;
  if (Number.isFinite(rem) && rem <= floor && resetMs > Date.now()) {
    return Math.max(60000, resetMs - Date.now() + 15000);
  }
  if (Number.isFinite(rem) && rem > floor && resetMs > Date.now()) {
    const spread = Math.ceil((resetMs - Date.now()) / Math.max(1, rem - floor));
    return Math.max(800, Math.min(5000, spread));
  }
  return 900;
}

function entityId(fullName) {
  return 'ghpath:' + fullName.toLowerCase();
}

const TAXONOMY_VERSION='2026.09-v2-functional';
const THEME_RULES=[
  ['Développement/Outils IA & Agents', /coding agent|code agent|agent orchestrator|orchestrat(?:e|or).*agent|parallel agents?|agentic coding|worktree.*agent|ide for.*agent|ai orchestrator/],
  ['Réseau & IoT/Accès distant', /remote desktop|remote access|remote control|screen sharing|teamviewer|\brdp\b|\bvnc\b|zero[- ]trust access/],
  ['Automatisation & Outils/Workflow', /workflow automation|workflow engine|automation platform|low[- ]code automation|orchestration platform/],
  ['Développement/API & Tests', /api client|api testing|api development|http client|rest client|graphql.*rest|alternative to postman/],
  ['Données & IA/Moteurs IA locaux', /local ai|localai|local llm|self[- ]hosted llm|llm inference|openai[- ]compatible.*local|run any model/],
  ['Données & IA/Outils API & agents', /model context protocol|\bmcp server\b|agent tools?|tool calling/],
  ['Données & IA/Bases de données & GUI', /database gui|database editor|redis gui|sql client|database client/],
  ['Sauvegarde & Résilience/Sauvegarde', /backup|snapshot|restore|disaster recovery|volume backup/],
  ['Observabilité & Supervision/Monitoring', /uptime monitor|monitoring platform|observability|telemetry|metrics platform/],
  ['Développement/Langages/Python', /\bpython\b|django|flask|pytorch|numpy|pandas/],
  ['Développement/Langages/JavaScript & TypeScript', /javascript|typescript|node\.?js|npm|deno|bun\b/],
  ['Développement/Langages/JVM', /\bjava\b|kotlin|scala|groovy|clojure/],
  ['Développement/Langages/Rust', /\brust\b|cargo/],
  ['Développement/Langages/Go', /\bgolang\b|\bgo\b/],
  ['Développement/Langages/.NET', /dotnet|\.net|csharp|c#|fsharp|f#/],
  ['Développement/Langages/C & C++', /c\+\+|\bcpp\b|cmake|\bc language\b/],
  ['Développement/Mobile/Android', /android|jetpack|gradle|kotlin/],
  ['Développement/Mobile/iOS', /\bios\b|swift|watchos|xcode/],
  ['Développement/Mobile/Hybride', /react[- ]native|flutter|cordova|capacitor|ionic/],
  ['Développement/Web/Frontend', /frontend|front-end|react\b|vue\b|angular|svelte|css|html5|webcomponents?/],
  ['Développement/Desktop', /electron|tauri|desktop|windows|macos|gtk|qt\b/],
  ['Cloud & DevOps/AWS', /\baws\b|amazon web services/],
  ['Cloud & DevOps/Cloud', /azure|gcp|google cloud|cloudflare|digitalocean|heroku|firebase/],
  ['Cloud & DevOps/Containers', /docker|kubernetes|\bk8s\b|container|helm/],
  ['Cloud & DevOps/Infrastructure as Code', /terraform|opentofu|ansible|pulumi/],
  ['Cloud & DevOps/CI-CD', /github actions|gitlab ci|jenkins|ci[- ]?cd|continuous integration/],
  ['Données & IA/IA & Machine Learning', /machine learning|deep learning|artificial intelligence|generative ai|llm|transformer/],
  ['Données & IA/Data Science', /data science|analytics|pandas|numpy|jupyter|visualization/],
  ['Données & IA/Bases de données', /database|postgres|mysql|sqlite|mongodb|redis|nosql/],
  ['Réseau & IoT/IoT', /\biot\b|mqtt|arduino|raspberry pi|esp32|esp8266|adafruit|home assistant/],
  ['Réseau & IoT/Réseau', /network|networking|dns|tcp|udp|snmp|vpn|wifi|wireless/],
  ['Sécurité/Cybersécurité', /security|cyber|appsec|malware|pentest|ctf|forensic|vulnerability/],
  ['Automatisation & Outils/CLI & Scripts', /command line|\bcli\b|powershell|shell|bash|automation|scripting/],
  ['Automatisation & Outils/Productivité développeur', /developer tools|devtools|workflow|productivity|git\b|github/],
  ['Documentation & Apprentissage/Guides', /tutorial|learning|guide|roadmap|book|course|cheat[- ]?sheet|reference|documentation/],
  ['Catalogues & Curations/Awesome Lists', /awesome[- ]?list|curated list|collection of .*resources|\bawesome\b/]
];

function classifyThemes(x,q){
  const topics=Array.isArray(x.topics)?x.topics.map(v=>String(v).toLowerCase()):[];
  const bag=[x.name,x.full_name,x.description,q.technology,q.kind,...topics].filter(Boolean).join(' ').toLowerCase();
  const matches=[];
  for(const [path,rx] of THEME_RULES) if(rx.test(bag)) matches.push(path);
  if(q.kind==='Catalogue de ressources' && !matches.includes('Catalogues & Curations/Awesome Lists')) matches.push('Catalogues & Curations/Awesome Lists');
  if(q.kind==='Guide / documentation' && !matches.includes('Documentation & Apprentissage/Guides')) matches.push('Documentation & Apprentissage/Guides');
  const uniq=[...new Set(matches)];
  const priority=(p)=>{
    if(/^Catalogues & Curations\//.test(p))return 120;
    if(/^Documentation & Apprentissage\//.test(p))return 115;
    if(/^Développement\/Outils IA & Agents/.test(p))return 112;
    if(/^Réseau & IoT\/Accès distant/.test(p))return 111;
    if(/^Sécurité\//.test(p))return 110;
    if(/^Données & IA\/(Moteurs IA locaux|Bases de données & GUI|Outils API & agents)/.test(p))return 109;
    if(/^Développement\/API & Tests/.test(p))return 108;
    if(/^Sauvegarde & Résilience\//.test(p))return 108;
    if(/^Observabilité & Supervision\//.test(p))return 107;
    if(/^Données & IA\//.test(p))return 105;
    if(/^Réseau & IoT\//.test(p))return 100;
    if(/^Cloud & DevOps\//.test(p))return 95;
    if(/^Automatisation & Outils\//.test(p))return 90;
    if(/^Développement\/(Mobile|Web|Desktop)/.test(p))return 80;
    if(/^Développement\/Langages\//.test(p))return 30;
    return 60;
  };
  const ranked=uniq.map((p,i)=>({p,i,w:priority(p)})).sort((a,b)=>b.w-a.w||a.i-b.i);
  const primary=ranked[0]?.p || (q.technology && q.technology!=='Domaine à préciser' ? 'Autres/'+q.technology : 'Autres/À classifier');
  const tags=[...new Set([
    ...uniq.flatMap(p=>p.split('/').slice(-2)),
    q.technology!=='Domaine à préciser'?q.technology:'',
    q.kind,
    ...topics.slice(0,12)
  ].filter(Boolean))].slice(0,24);
  const confidence=Math.min(0.99, uniq.length?0.74+Math.min(0.23,uniq.length*0.05):(q.technology!=='Domaine à préciser'?0.55:0.35));
  return {primary:primary.split('/')[0],path:primary,tags,confidence};
}

function classifyL1(x) {
  const full = String(x.full_name || '');
  const name = String(x.name || full.split('/').pop() || '').toLowerCase();
  const desc = String(x.description || '').toLowerCase();
  const topics = Array.isArray(x.topics) ? x.topics.map(v => String(v).toLowerCase()) : [];
  const bag = [name, desc, ...topics].join(' ');

  const isCatalogue = name.startsWith('awesome') || topics.includes('awesome-list') || topics.includes('list') ||
    /curated list|collection of (useful |awesome |interesting )?(resources|tools|projects|libraries|packages)|awesome resources|aggregation of tooling|aggregation of tools|list of .*tools/.test(desc);
  const isGuide = /(^|[-_])(tips?|guides?|tutorials?|learning|books?|courses?|roadmaps?|cheat[-_]?sheet|references?|papers?|docs?|documentation)([-_]|$)/.test(name) ||
    /tips|tutorial|learning material|learning resources|guide|reference|documentation|bookmarks|must[- ]watch/.test(desc);
  const isDataset = /dataset|data set|public data/.test(bag);

  let kind = isCatalogue ? 'Catalogue de ressources' :
    isDataset ? 'Jeu de données / ressources' :
    isGuide ? 'Guide / documentation' :
    x.is_template ? 'Modèle / template' :
    'Projet logiciel';

  const techRules = [
    ['react native', /react[- ]native/], ['nodejs', /node\.js|nodejs|node-js/], ['javascript', /javascript|\bjs\b/],
    ['typescript', /typescript/], ['python', /python/], ['rust', /\brust\b/], ['golang', /golang|\bgo\b/],
    ['c++', /c\+\+|\bcpp\b/], ['c# / .NET', /dotnet|\.net|csharp|c#/], ['swift', /swift/], ['ios', /\bios\b/],
    ['android', /android/], ['electron', /electron/], ['cordova', /cordova|phonegap/], ['flutter', /flutter/],
    ['firebase', /firebase/], ['cloudflare', /cloudflare/], ['aws', /\baws\b|amazon web services/],
    ['windows', /windows|powertoys/], ['linux', /linux/], ['macOS', /macos|mac os|\bmac\b/],
    ['kubernetes', /kubernetes|\bk8s\b/], ['docker', /docker|container/], ['terraform', /terraform|opentofu/],
    ['home assistant', /home assistant/], ['iot', /\biot\b|esp8266|esp32|adafruit/], ['ebpf', /ebpf/],
    ['nix', /\bnix\b/], ['deno', /\bdeno\b/], ['scala', /scala/], ['ruby', /ruby/], ['clojure', /clojure/],
    ['elixir', /elixir/], ['erlang', /erlang/], ['elm', /\belm\b/], ['haskell', /haskell/], ['lua', /\blua\b/],
    ['R', /(^|[^a-z])r([^a-z]|$)|rstats/], ['julia', /julia/], ['capacitor', /capacitor/],
    ['frontend', /frontend|front-end/], ['web', /webextensions?|web components?|html5|css/],
    ['network', /network|mqtt|snmp|rtc/], ['security', /security|cyber|malware|ctf|appsec/],
    ['machine learning / AI', /machine learning|deep learning|artificial intelligence|generative ai|\bai\b/]
  ];
  let technology = '';
  if (name.startsWith('awesome-')) {
    const suffix=name.slice(8).replace(/-/g,' ').trim();
    const aliases={
      'fsharp':'F#','f sharp':'F#','cpp':'C++','c plus plus':'C++','dotnet':'.NET','dotnet core':'.NET',
      'cl':'Common Lisp','common lisp':'Common Lisp','d':'D','r':'R','go':'Go','golang':'Go','java':'Java',
      'rxjava':'RxJava / Java','python':'Python','nodejs':'Node.js','node js':'Node.js','swift':'Swift',
      'rust':'Rust','haskell':'Haskell','purescript':'PureScript','scala':'Scala','scala native':'Scala Native',
      'ruby':'Ruby','clojure':'Clojure','clojurescript':'ClojureScript','elixir':'Elixir','elm':'Elm',
      'erlang':'Erlang','lua':'Lua','kotlin':'Kotlin','dart':'Dart','groovy':'Groovy','perl':'Perl',
      'vba':'VBA','autohotkey':'AutoHotkey','autoit':'AutoIt','cmake':'CMake','ada':'Ada','coq':'Coq'
    };
    if(suffix && !/^(list|resources?|things)$/.test(suffix)) technology=aliases[suffix]||suffix;
  }
  if (!technology && kind==='Projet logiciel' && x.language) {
    const strongName=[name].join(' ');
    const strongRules=techRules.filter(function(z){return ['react native','android','ios','electron','cordova','flutter','firebase','windows','kubernetes','terraform','home assistant'].includes(z[0]);});
    for (const [label, rx] of strongRules) if (rx.test(strongName)) { technology = label; break; }
    if(!technology) technology=String(x.language);
  }
  if (!technology) {
    const topicBag=[name,...topics].join(' ');
    for (const [label, rx] of techRules) if (rx.test(topicBag)) { technology = label; break; }
  }
  if (!technology) for (const [label, rx] of techRules) if (rx.test(desc)) { technology = label; break; }

  const genericTopics = new Set([
    'awesome','awesome-list','list','lists','resources','resource','open-source','opensource','github',
    'collection','curated','agpl','agplv3','gpl','gplv3','mit','apache-2','hacktoberfest','community'
  ]);
  const candidates = topics.filter(t => !genericTopics.has(t) && !/license|licence|agpl|gpl|mit-license/.test(t));
  if (!technology && name === 'awesome') technology = 'Multi-thèmes';
  if (!technology && name.startsWith('awesome-')) {
    const n = name.slice(8).replace(/-/g,' ').trim();
    if (n && !/^(list|resources?)$/.test(n)) technology = n;
  }
  if (!technology && candidates.length) technology = candidates[0];
  if (!technology && x.language) technology = String(x.language);
  if (!technology) technology = 'Domaine à préciser';

  const contentMode = isCatalogue ? 'Catalogue / documentation / liens' :
    isGuide ? 'Documentation / apprentissage' :
    isDataset ? 'Données / documentation' :
    (x.language ? 'Projet logiciel (' + x.language + ')' : 'Projet / contenu à préciser');

  let activityDays = null, activityStatus = 'Activité inconnue';
  const pushed = Date.parse(String(x.pushed_at || ''));
  if (Number.isFinite(pushed)) {
    activityDays = Math.max(0, Math.floor((Date.now() - pushed) / 86400000));
    activityStatus = x.archived ? 'Archivé' :
      x.disabled ? 'Désactivé' :
      activityDays <= 180 ? 'Actif récemment' :
      activityDays <= 730 ? 'Activité modérée' : 'Peu actif / ancien';
  } else if (x.archived) activityStatus = 'Archivé';

  const quality = x.id && full ? 'Identité GitHub vérifiée' : 'Vérification partielle';
  let score = 30;
  if (x.id && full) score += 20;
  if (x.description) score += 8;
  if (topics.length) score += 7;
  if (x.license) score += 7;
  if (x.pushed_at) score += 7;
  if (x.created_at) score += 5;
  if (x.default_branch) score += 5;
  if (technology && technology !== 'Domaine à préciser') score += 5;
  if (kind) score += 3;
  if (x.homepage) score += 3;
  score = Math.min(100, score);
  const tech = technology && technology !== 'Domaine à préciser' ? technology : 'un domaine encore à préciser';
  const summary = kind === 'Catalogue de ressources'
    ? 'Catalogue de ressources consacré à ' + tech + '. ' + activityStatus + '.'
    : kind === 'Guide / documentation'
      ? 'Guide ou documentation consacré à ' + tech + '. ' + activityStatus + '.'
      : kind === 'Jeu de données / ressources'
        ? 'Ressource de données consacrée à ' + tech + '. ' + activityStatus + '.'
        : 'Projet logiciel lié à ' + tech + (x.language ? ', principalement en ' + x.language : '') + '. ' + activityStatus + '.';
  const deepStatus = kind === 'Projet logiciel' ? 'PENDING' : 'NOT_APPLICABLE';
  const l1Stage = kind === 'Projet logiciel' ? 'CORE_VERIFIED_DEEP_PENDING' : 'L1_COMPLETE';
  const theme=classifyThemes(x,{kind,technology});
  return {kind, technology, contentMode, activityStatus, activityDays, quality, score, summary, deepStatus, l1Stage, theme};
}

function applyExtendedL1(entityIdValue, x, q) {
  db.prepare(`UPDATE results SET
    owner_login=?,owner_type=?,html_url=?,clone_url=?,license_name=?,subscribers_count=?,network_count=?,
    has_issues=?,has_projects=?,has_downloads=?,is_template=?,l1_summary=?,
    l1_stage=CASE WHEN coalesce(deep_status,'')='DONE' OR coalesce(l1_stage,'')='L1_COMPLETE' THEN 'L1_COMPLETE' ELSE ? END,
    deep_status=CASE WHEN coalesce(deep_status,'')='DONE' THEN 'DONE' ELSE coalesce(deep_status,?) END
    WHERE entity_id=?`).run(
      String(x.owner?.login ?? ''), String(x.owner?.type ?? ''), String(x.html_url ?? ''),
      String(x.clone_url ?? ''), String(x.license?.name ?? ''), Number(x.subscribers_count ?? 0),
      Number(x.network_count ?? 0), x.has_issues ? 1 : 0, x.has_projects ? 1 : 0,
      x.has_downloads ? 1 : 0, x.is_template ? 1 : 0, q.summary, q.l1Stage, q.deepStatus, entityIdValue
    );
  const t=q.theme||classifyThemes(x,q);
  db.prepare(`UPDATE results SET primary_theme=?,theme_path=?,theme_tags_json=?,theme_confidence=?,taxonomy_version=? WHERE entity_id=?`)
    .run(t.primary,t.path,JSON.stringify(t.tags),Number(t.confidence||0),TAXONOMY_VERSION,entityIdValue);
}

function reclassifyExisting() {
  const rows=db.prepare(`SELECT entity_id,raw_json FROM results
                         WHERE coalesce(taxonomy_version,'')<>?
                            OR coalesce(l1_summary,'')=''
                            OR coalesce(l1_stage,'')=''`).all(TAXONOMY_VERSION);
  const upd=db.prepare(`UPDATE results SET resource_kind=?,technology=?,content_mode=?,activity_status=?,activity_days=?,l1_quality=?,l1_score=? WHERE entity_id=?`);
  let changed=0;
  for(const r of rows){
    try{
      const x=JSON.parse(r.raw_json||'{}'), q=classifyL1(x);
      upd.run(q.kind,q.technology,q.contentMode,q.activityStatus,q.activityDays,q.quality,q.score,r.entity_id);
      applyExtendedL1(r.entity_id,x,q);
      changed++;
    }catch{}
  }
  if(changed){
    event('INFO','L1_RECLASSIFY','rows='+changed);
    rebuildSearchIndex();
  }
  return changed;
}

function seed() {
  const seeds = JSON.parse(readFileSync(join(ROOT, 'config', 'canary-seeds.json'), 'utf8'));
  const stmt = db.prepare(`INSERT OR IGNORE INTO jobs(entity_id,full_name,status,attempts,updated_at)
                           VALUES(?,?,'PENDING',0,?)`);
  let added = 0;
  for (const fullName of seeds) {
    const r = stmt.run(entityId(fullName), fullName, now());
    added += Number(r.changes || 0);
  }
  event('INFO', 'SEED', `added=${added}; total=${seeds.length}`);
  console.log(JSON.stringify({ ok: true, added, configured: seeds.length, dbPath }, null, 2));
}

function selftest() {
  const ver = process.versions.node.split('.').map(Number);
  if (ver[0] < 24) throw new Error('NODE_24_REQUIRED');
  const testName = 'selftest/example';
  db.prepare(`INSERT OR REPLACE INTO jobs(entity_id,full_name,status,attempts,updated_at)
              VALUES(?,?,'TEST',0,?)`).run(entityId(testName), testName, now());
  const row = db.prepare('SELECT full_name FROM jobs WHERE entity_id=?').get(entityId(testName));
  db.prepare('DELETE FROM jobs WHERE entity_id=?').run(entityId(testName));
  if (!row || row.full_name !== testName) throw new Error('SQLITE_READBACK_FAILED');

  const roleCases=[
    [{full_name:'stablyai/orca',description:'Orca is the ADE for working with a fleet of parallel agents. Run any coding agent with your own subscription. Available on desktop, mobile and remote runtime.',topics_json:'["ai-agents","parallel-agents","worktrees"]',theme_path:'Développement/Outils IA & Agents'},{identity_excerpt:'Run coding agents in parallel worktrees and manage terminals.'},'coding-agent-orchestrator'],
    [{full_name:'mudler/LocalAI',description:'LocalAI is the open-source AI engine. Run any model - LLMs, vision, voice, image, video - on any hardware. No GPU required.',topics_json:'["ai","llm","api"]',theme_path:'Données & IA/Moteurs IA locaux'},{identity_excerpt:'Run models locally with an OpenAI compatible API.'},'local-ai-engine'],
    [{full_name:'firezone/firezone',description:'Blazing-fast remote access',topics_json:'["network-security","security","vpn","wireguard","wireguard-vpn"]',theme_path:'Réseau & IoT/Accès distant',theme_tags_json:'["Accès distant","Cybersécurité"]'},{identity_excerpt:'Connect users to private apps and infrastructure securely.'},'secure-remote-access'],
    [{full_name:'rustdesk/rustdesk',description:'An open-source remote desktop application designed for self-hosting, as an alternative to TeamViewer.',topics_json:'["remote-control","remote-desktop","rdp","vnc"]',theme_path:'Réseau & IoT/Accès distant'},{identity_excerpt:'Remote desktop control across multiple platforms.'},'remote-desktop'],
    [{full_name:'getinsomnia/insomnia',description:'The open-source, cross-platform API client for GraphQL, REST, WebSockets, SSE and gRPC.',topics_json:'["api","api-client","graphql","rest-api"]',theme_path:'Développement/API & Tests'},{identity_excerpt:'API client for designing and testing APIs.'},'api-client'],
    [{full_name:'mobile-next/mobile-mcp',description:'Mobile MCP server for iOS and Android automation.'},{identity_excerpt:'Automate mobile applications and devices.'},'mobile-automation-mcp'],
    [{full_name:'offen/docker-volume-backup',description:'Backup Docker volumes locally or to S3-compatible storage.'},{identity_excerpt:'Automated backup and restore for Docker volumes.'},'backup']
  ];
  for(const [r,sig,expected] of roleCases){
    const got=l2PrimaryRole(r,sig,l2Signals((r.description||'')+' '+(sig.identity_excerpt||''))).id;
    if(got!==expected)throw new Error('SEMANTIC_ROLE_FAIL '+r.full_name+' expected='+expected+' got='+got);
  }
  const themeCases=[
    [{full_name:'stablyai/orca',name:'orca',description:'AI agent orchestrator for coding agents and parallel worktrees',language:'TypeScript',topics:['ai','agents']},{kind:'Projet logiciel',technology:'TypeScript'},'Développement/Outils IA & Agents'],
    [{full_name:'firezone/firezone',name:'firezone',description:'Blazing-fast remote access',language:'Elixir',topics:['wireguard','security','vpn']},{kind:'Projet logiciel',technology:'Elixir'},'Réseau & IoT/Accès distant'],
    [{full_name:'mudler/LocalAI',name:'LocalAI',description:'Local AI engine and self-hosted LLM inference',language:'Go',topics:['llm','ai']},{kind:'Projet logiciel',technology:'Go'},'Données & IA/Moteurs IA locaux'],
    [{full_name:'getinsomnia/insomnia',name:'insomnia',description:'Cross-platform API client for GraphQL, REST, WebSockets and gRPC',language:'TypeScript',topics:['api','api-client','graphql','rest-api']},{kind:'Projet logiciel',technology:'TypeScript'},'Développement/API & Tests']
  ];
  for(const [x,q,expected] of themeCases){
    const got=classifyThemes(x,q).path;
    if(got!==expected)throw new Error('SEMANTIC_THEME_FAIL '+x.full_name+' expected='+expected+' got='+got);
  }
  const noisy=l2PurposeSignals('remote-desktop',['Ligne de commande / automatisation','Réseau / communication','Application mobile']);
  if(noisy.includes('Ligne de commande / automatisation')||!noisy.includes('Réseau / communication'))throw new Error('SEMANTIC_PURPOSE_FILTER_FAIL');
  const concepts=searchConceptGroups('android remote control');
  if(concepts.length<3||!searchFtsQuery('android remote control','broad').includes(' OR '))throw new Error('SEARCH_CONCEPT_SELFTEST_FAIL');
  if(searchTextHasTerm('maikub/flutter_local_notifications','ai')||!searchTextHasTerm('local AI engine','ai')||searchFtsTerm('gui')!=='gui')throw new Error('SEARCH_TOKEN_BOUNDARY_SELFTEST_FAIL');
  const frConcepts=searchConceptGroups('je veux contrôler un téléphone Android à distance');if(frConcepts.length<3)throw new Error('SEARCH_FRENCH_CONCEPT_SELFTEST_FAIL');

  event('INFO', 'SELFTEST_PASS', `node=${process.versions.node}; semantic=7; themes=4; search=PASS`);
  console.log(JSON.stringify({ ok:true,node:process.versions.node,sqlite:true,semantic_roles:7,semantic_themes:4,search_concepts:true,dbPath }, null, 2));
}

async function fetchRepo(fullName) {
  const headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'TLIB-PC-Agent/0.1'
  };
  const token = githubToken();
  if (token) headers.Authorization = 'Bearer ' + token;
  const url = 'https://api.github.com/repos/' + fullName;
  const res = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
  const text = await res.text();
  let body = {};
  try { body = text ? JSON.parse(text) : {}; } catch { body = { message: text.slice(0,500) }; }
  const remaining = Number(res.headers.get('x-ratelimit-remaining') || -1);
  const reset = Number(res.headers.get('x-ratelimit-reset') || 0);

  if (res.status === 403 && remaining === 0) {
    const e = new Error('GITHUB_RATE_LIMIT');
    e.code = 'RATE_LIMIT';
    e.reset = reset;
    throw e;
  }
  if (res.status === 404) return { status: 404, body, remaining, reset };
  if (!res.ok) {
    const e = new Error('GITHUB_HTTP_' + res.status + ' ' + String(body.message || '').slice(0,300));
    e.code = res.status >= 500 ? 'RETRY' : 'HTTP';
    throw e;
  }
  return { status: res.status, body, remaining, reset };
}

async function canary(limit=10) {
  seed();
  const jobs = db.prepare(`SELECT entity_id,full_name,attempts FROM jobs
                           WHERE status IN ('PENDING','RETRY')
                           ORDER BY rowid LIMIT ?`).all(limit);
  let done=0, missing=0, errors=0, paused=false;
  for (const job of jobs) {
    db.prepare(`UPDATE jobs SET status='RUNNING', attempts=attempts+1, updated_at=? WHERE entity_id=?`).run(now(), job.entity_id);
    try {
      const r = await fetchRepo(job.full_name);
      if (r.status === 404) {
        db.prepare(`UPDATE jobs SET status='NOT_FOUND', last_error='HTTP_404', updated_at=? WHERE entity_id=?`).run(now(), job.entity_id);
        event('WARN','NOT_FOUND',job.full_name);
        missing++;
        continue;
      }
      const x = r.body;
      const topics = Array.isArray(x.topics) ? x.topics : [];
      const q = classifyL1(x);
      db.prepare(`INSERT OR REPLACE INTO results(
        entity_id,full_name,http_status,github_id,node_id,description,archived,fork,stars,language,license,
        topics_json,updated_at_github,pushed_at,default_branch,size_kb,open_issues,rate_remaining,fetched_at,raw_json,
        resource_kind,technology,content_mode,activity_status,activity_days,l1_quality
      ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(
        job.entity_id, job.full_name, r.status, String(x.id ?? ''), String(x.node_id ?? ''), String(x.description ?? ''),
        x.archived ? 1 : 0, x.fork ? 1 : 0, Number(x.stargazers_count ?? 0), String(x.language ?? ''),
        String(x.license?.spdx_id ?? x.license?.name ?? ''), JSON.stringify(topics), String(x.updated_at ?? ''),
        String(x.pushed_at ?? ''), String(x.default_branch ?? ''), Number(x.size ?? 0), Number(x.open_issues_count ?? 0),
        r.remaining, now(), JSON.stringify(x), q.kind, q.technology, q.contentMode, q.activityStatus, q.activityDays, q.quality
      );
      applyExtendedL1(job.entity_id,x,q);
      db.prepare(`UPDATE jobs SET status='DONE', last_error=NULL, updated_at=? WHERE entity_id=?`).run(now(), job.entity_id);
      event('INFO','L1_OK',job.full_name);
      done++;
    } catch (e) {
      if (e.code === 'RATE_LIMIT') {
        db.prepare(`UPDATE jobs SET status='RETRY', last_error=?, updated_at=? WHERE entity_id=?`).run(String(e.message), now(), job.entity_id);
        event('WARN','RATE_LIMIT',`reset=${e.reset || 0}`);
        paused=true;
        break;
      }
      const attempts = Number(job.attempts || 0) + 1;
      const retry = attempts < 3;
      db.prepare(`UPDATE jobs SET status=?, last_error=?, updated_at=? WHERE entity_id=?`).run(retry?'RETRY':'FAILED', String(e.message).slice(0,500), now(), job.entity_id);
      event('ERROR','L1_ERROR',job.full_name + ' :: ' + e.message);
      errors++;
    }
  }
  const summary = statusSnapshot();
  console.log(JSON.stringify({ ok: !paused, paused, processed: jobs.length, done, missing, errors, summary }, null, 2));
}

function fixtureFiles() {
  try {
    return readdirSync(join(ROOT,'config')).filter(n => /^l1-(fixture|batch).*\.json$/i.test(n)).sort();
  } catch { return []; }
}

let fixtureCorpusCache=null;
function fixtureCorpus() {
  if(fixtureCorpusCache) return fixtureCorpusCache;
  const byName = new Map();
  for (const file of fixtureFiles()) {
    try {
      const rows = JSON.parse(readFileSync(join(ROOT,'config',file),'utf8'));
      for (const x of rows) if (x && x.full_name) byName.set(String(x.full_name).toLowerCase(), x);
    } catch {}
  }
  fixtureCorpusCache=[...byName.values()];
  return fixtureCorpusCache;
}

function stagedNames() {
  const out=[], seen=new Set();
  const add = (rows) => {
    for(const n of rows || []){
      const full=String(n||'').trim();
      if(full && !seen.has(full.toLowerCase())){seen.add(full.toLowerCase());out.push(full);}
    }
  };
  try {
    for(const file of readdirSync(join(ROOT,'config')).filter(n=>/^l1-names-.*\.json$/i.test(n)).sort()){
      try{ add(JSON.parse(readFileSync(join(ROOT,'config',file),'utf8'))); }catch{}
    }
  }catch{}
  try {
    for(const file of readdirSync(dataDir).filter(n=>/^queue-full-\d+\.json$/i.test(n)).sort()){
      try{ add(JSON.parse(readFileSync(join(dataDir,file),'utf8'))); }catch{}
    }
  }catch{}
  return out;
}

let stagedNameCount = 0;
function stageNamedQueue() {
  const existing=Number(db.prepare('SELECT COUNT(*) AS n FROM jobs').get().n);
  // Fast boot: a full corpus is already durable in SQLite. Do not reread/parse
  // queue-full JSON files on every startup just to rediscover the same names.
  if(existing>=50000){
    stagedNameCount=existing;
    event('INFO','L1_NAME_STAGE_SKIP','existing='+existing+'; reason=durable_queue_already_loaded');
    return {added:0,staged:existing,skipped:true};
  }
  const rows=stagedNames();
  stagedNameCount=rows.length;
  if(existing>=rows.length){
    event('INFO','L1_NAME_STAGE_SKIP','existing='+existing+'; staged_names='+rows.length);
    return {added:0,staged:rows.length,skipped:true};
  }
  const stmt=db.prepare(`INSERT OR IGNORE INTO jobs(entity_id,full_name,status,attempts,updated_at)
                         VALUES(?,?,'PENDING',0,?)`);
  let added=0;
  db.exec('BEGIN IMMEDIATE');
  try {
    const at=now();
    for(const fullName of rows) added += Number(stmt.run(entityId(fullName),fullName,at).changes||0);
    db.exec('COMMIT');
  } catch(e) {
    try{db.exec('ROLLBACK')}catch{}
    throw e;
  }
  if(added) event('INFO','L1_NAME_STAGE','added='+added+'; staged_names='+rows.length);
  return {added,staged:rows.length,skipped:false};
}

function stageFixtureJobs() {
  const rows = fixtureCorpus();
  const stmt = db.prepare(`INSERT OR IGNORE INTO jobs(entity_id,full_name,status,attempts,updated_at)
                           VALUES(?,?,'PENDING',0,?)`);
  let added=0;
  for (const x of rows) added += Number(stmt.run(entityId(x.full_name),String(x.full_name),now()).changes||0);
  if (added) event('INFO','L1_STAGE','added='+added+'; staged='+rows.length);
  return {added,staged:rows.length};
}

function upsertFixtureResult(x) {
  const fullName=String(x.full_name||''); if(!fullName) return false;
  const id=entityId(fullName), topics=Array.isArray(x.topics)?x.topics:[], q=classifyL1(x);
  db.prepare(`INSERT OR REPLACE INTO results(
    entity_id,full_name,http_status,github_id,node_id,description,archived,fork,stars,language,license,
    topics_json,updated_at_github,pushed_at,default_branch,size_kb,open_issues,rate_remaining,fetched_at,raw_json,
    resource_kind,technology,content_mode,activity_status,activity_days,l1_quality,homepage,forks_count,watchers_count,
    created_at_github,visibility,disabled,has_wiki,has_pages,has_discussions,l1_score
  ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(
    id,fullName,200,String(x.id??''),String(x.node_id??''),String(x.description??''),x.archived?1:0,x.fork?1:0,
    Number(x.stargazers_count??0),String(x.language??''),String(x.license?.spdx_id??x.license?.name??''),JSON.stringify(topics),
    String(x.updated_at??''),String(x.pushed_at??''),String(x.default_branch??''),Number(x.size??0),Number(x.open_issues_count??0),
    -1,now(),JSON.stringify(x),q.kind,q.technology,q.contentMode,q.activityStatus,q.activityDays,q.quality,
    String(x.homepage??''),Number(x.forks_count??0),Number(x.watchers_count??0),String(x.created_at??''),String(x.visibility??''),
    x.disabled?1:0,x.has_wiki?1:0,x.has_pages?1:0,x.has_discussions?1:0,q.score
  );
  applyExtendedL1(id,x,q);
  syncSearchEntity(id);
  db.prepare(`UPDATE jobs SET status='DONE', last_error=NULL, updated_at=? WHERE entity_id=?`).run(now(),id);
  return true;
}

let fixtureAutopilotExhausted=false;
function autopilotFixtureStep(limit=2) {
  if(fixtureAutopilotExhausted) return 0;
  const corpus=fixtureCorpus(), pending=[];
  for(const x of corpus){
    const id=entityId(x.full_name);
    const done=db.prepare('SELECT 1 AS ok FROM results WHERE entity_id=?').get(id);
    if(!done) pending.push(x);
    if(pending.length>=limit) break;
  }
  if(!pending.length){
    fixtureAutopilotExhausted=true;
    event('INFO','L1_FIXTURE_EXHAUSTED','cached='+corpus.length);
    return 0;
  }
  let done=0;
  for(const x of pending) if(upsertFixtureResult(x)) done++;
  if(done) event('INFO','L1_AUTOPILOT','+'+done+' fiche(s)');
  return done;
}

let publicNextAttemptAt = 0;
let publicRateRemaining = null;
let publicRateReset = null;
let coreSinceDeep = 0;
let deepNextAttemptAt = 0;

async function githubGet(path, allow404=false) {
  const headers={'Accept':'application/vnd.github+json','User-Agent':'TLIB-PC-Agent/0.2'};
  const token=githubToken(); if(token) headers.Authorization='Bearer '+token;
  const res=await fetch('https://api.github.com'+path,{headers,signal:AbortSignal.timeout(15000)});
  const text=await res.text();
  let body={}; try{body=text?JSON.parse(text):{}}catch{body={message:text.slice(0,500)}}
  const remaining=Number(res.headers.get('x-ratelimit-remaining')||-1);
  const reset=Number(res.headers.get('x-ratelimit-reset')||0);
  publicRateRemaining=remaining; publicRateReset=reset;
  if(res.status===404 && allow404) return {status:404,body:{},remaining,reset};
  if(res.status===403 && remaining===0){const e=new Error('GITHUB_RATE_LIMIT');e.code='RATE_LIMIT';e.reset=reset;throw e}
  if(!res.ok){const e=new Error('GITHUB_HTTP_'+res.status+' '+String(body.message||'').slice(0,300));e.code=res.status>=500?'RETRY':'HTTP';throw e}
  return {status:res.status,body,remaining,reset};
}

const UI_ACTIVITY_FILE=join(dataDir,'ui-active.txt');
const BG_WORKER_FILE=join(dataDir,'background-worker.json');
let lastCpuTimes=null;
let lastInteractiveRequestAt=Date.now();
let lastExplicitInteractionAt=0;
let governorState={mode:'STARTING',delay_ms:2500,free_mb:0,free_pct:0,cpu_pct:null,rss_mb:0,reason:'boot'};

function systemCpuPercent() {
  try{
    const list=cpus();
    let idle=0,total=0;
    for(const cpu of list){
      idle+=cpu.times.idle;
      total+=cpu.times.user+cpu.times.nice+cpu.times.sys+cpu.times.idle+cpu.times.irq;
    }
    const cur={idle,total};
    if(!lastCpuTimes){lastCpuTimes=cur;return null}
    const dIdle=cur.idle-lastCpuTimes.idle,dTotal=cur.total-lastCpuTimes.total;
    lastCpuTimes=cur;
    if(dTotal<=0)return null;
    return Math.max(0,Math.min(100,100*(1-dIdle/dTotal)));
  }catch{return null}
}
let pressureStreak=0;
let reliefStreak=0;
function resourceGovernor() {
  const free=freemem(), total=totalmem();
  const totalMB=Math.round(total/1048576), freeMB=Math.round(free/1048576), freePct=total?100*free/total:0;
  const usedPct=100-freePct;
  const rssMB=Math.round(process.memoryUsage().rss/1048576);
  const cpu=systemCpuPercent();
  let sharedActivity=lastInteractiveRequestAt;
  try{sharedActivity=Math.max(sharedActivity,Number(readFileSync(UI_ACTIVITY_FILE,'utf8'))||0)}catch{}
  const userActive=(Date.now()-sharedActivity)<30000;

  // 4–6 Go : 80–95 % de RAM utilisée est un état courant sous Windows.
  // On ne pénalise donc jamais TLIB sur la seule RAM système utilisée.
  const lowRamProfile=totalMB<=6144;
  const profile=lowRamProfile?'LOW_RAM_4_6GB':'STANDARD';

  const workerSoft=lowRamProfile?110:180;
  const workerHard=lowRamProfile?180:260;
  const freeCritical=lowRamProfile?70:220;
  const freeSoft=lowRamProfile?110:420;
  const cpuSoft=lowRamProfile?88:82;
  const cpuHard=lowRamProfile?97:95;

  const memoryCritical=(freeMB<freeCritical && rssMB>workerSoft) || rssMB>workerHard;
  const memorySoft=(freeMB<freeSoft && rssMB>workerSoft) || rssMB>workerSoft;
  const cpuCritical=cpu!==null && cpu>cpuHard;
  const cpuSoftHit=cpu!==null && cpu>cpuSoft;
  const pressureHit=memoryCritical || cpuCritical || (memorySoft && cpuSoftHit);

  if(pressureHit){pressureStreak=Math.min(20,pressureStreak+1);reliefStreak=0}
  else {reliefStreak=Math.min(20,reliefStreak+1);if(reliefStreak>=2)pressureStreak=Math.max(0,pressureStreak-1)}

  let mode='NORMAL',delay=lowRamProfile?2200:1800,reason='resources-ok';
  if(pressureStreak>=3 && (memoryCritical || cpuCritical)){
    mode='PAUSED'; delay=12000;
    reason=memoryCritical?'combined-memory-pressure':'sustained-high-cpu';
  }else if(pressureStreak>=2 && (memorySoft || cpuSoftHit)){
    mode='THROTTLED'; delay=lowRamProfile?5500:4500;
    reason=memorySoft?'combined-memory-headroom':'cpu-headroom';
  }else if(userActive){
    mode='USER_ACTIVE'; delay=lowRamProfile?3800:3000;
    reason='interactive-use';
  }

  const pressureScore=Math.min(100,
    Math.round(
      (rssMB/Math.max(1,workerHard))*45 +
      (cpu===null?0:(cpu/100)*35) +
      (freeMB<freeCritical?20:freeMB<freeSoft?10:0)
    )
  );

  governorState={
    mode,profile,delay_ms:delay,total_mb:totalMB,free_mb:freeMB,
    used_pct:Number(usedPct.toFixed(1)),free_pct:Number(freePct.toFixed(1)),
    cpu_pct:cpu===null?null:Number(cpu.toFixed(1)),rss_mb:rssMB,
    pressure_score:pressureScore,pressure_streak:pressureStreak,
    reason,
    note:lowRamProfile?'80–95% system RAM usage is treated as normal unless TLIB itself adds measurable pressure':'standard memory profile'
  };
  return governorState;
}
function markInteractiveRequest(pathname) {
  const quiet=new Set(['/api/health','/api/version','/api/update/status']);
  if(pathname==='/api/interaction') lastExplicitInteractionAt=Date.now();
  if(!quiet.has(pathname)){
    lastInteractiveRequestAt=Date.now();
    try{writeFileSync(UI_ACTIVITY_FILE,String(lastInteractiveRequestAt),'utf8')}catch{}
  }
}

function deepBacklogCount() {
  return Number(db.prepare(`SELECT COUNT(*) AS n FROM results
                            WHERE resource_kind='Projet logiciel'
                              AND coalesce(deep_status,'PENDING') IN ('PENDING','RETRY')`).get().n);
}
function l1SchedulerMode() {
  const backlog=deepBacklogCount();
  if(backlog>100 && (publicRateRemaining===null || publicRateRemaining>=2000)) return 'DEEP_CATCHUP';
  if(backlog>25) return 'BALANCED_DEEP_FIRST';
  return 'CORE_EXPANSION';
}
function schedulerMode(){
  const l2=l2Stats();
  if(l2.base_pending>0 || l2.deep_pending>0) return 'PARALLEL_L1_L2';
  return 'L1_'+l1SchedulerMode();
}

async function deepL1Step() {
  if(Date.now()<deepNextAttemptAt) return {done:0,state:'WAIT'};
  if(!githubToken()) return {done:0,state:'NO_AUTH'};
  if(publicRateRemaining !== null && publicRateRemaining < 1800) return {done:0,state:'RESERVE_RATE'};
  const row=db.prepare(`SELECT entity_id,full_name,default_branch FROM results
                        WHERE resource_kind='Projet logiciel'
                          AND coalesce(deep_status,'PENDING') IN ('PENDING','RETRY')
                        ORDER BY fetched_at LIMIT 1`).get();
  if(!row) return {done:0,state:'EMPTY'};
  try{
    const enc=row.full_name.split('/').map(encodeURIComponent).join('/');
    const langs=await githubGet('/repos/'+enc+'/languages',true);
    const rel=await githubGet('/repos/'+enc+'/releases/latest',true);
    const community=await githubGet('/repos/'+enc+'/community/profile',true);
    const langJson=langs.status===404?'{}':JSON.stringify(langs.body||{});
    const releaseTag=rel.status===404?'':String(rel.body?.tag_name||'');
    const releaseAt=rel.status===404?'':String(rel.body?.published_at||rel.body?.created_at||'');
    const health=community.status===404?null:Number(community.body?.health_percentage ?? 0);
    const readme=community.status!==404 && Boolean(community.body?.files?.readme);
    db.prepare(`UPDATE results SET languages_json=?,latest_release_tag=?,latest_release_at=?,
                community_health=?,readme_present=?,deep_status='DONE',l1_stage='L1_COMPLETE'
                WHERE entity_id=?`).run(langJson,releaseTag,releaseAt,health,readme?1:0,row.entity_id);
    syncSearchEntity(row.entity_id);
    event('INFO','L1_DEEP_OK',row.full_name);
    deepNextAttemptAt=Date.now()+2500;
    return {done:1,state:'OK'};
  }catch(e){
    if(e.code==='RATE_LIMIT'){
      publicRateReset=Number(e.reset||0);
      publicNextAttemptAt=Math.max(Date.now()+60000,publicRateReset*1000+15000);
      event('WARN','L1_DEEP_RATE_LIMIT','reset='+publicRateReset);
      deepNextAttemptAt=publicNextAttemptAt;
      return {done:0,state:'RATE_LIMIT'};
    }
    db.prepare(`UPDATE results SET deep_status='RETRY' WHERE entity_id=?`).run(row.entity_id);
    event('ERROR','L1_DEEP_ERROR',row.full_name+' :: '+String(e.message||e));
    deepNextAttemptAt=Date.now()+5000;
    return {done:0,state:'ERROR'};
  }
}

function saveLiveResult(job, r) {
  const x=r.body, topics=Array.isArray(x.topics)?x.topics:[], q=classifyL1(x);
  db.prepare(`INSERT OR REPLACE INTO results(
    entity_id,full_name,http_status,github_id,node_id,description,archived,fork,stars,language,license,
    topics_json,updated_at_github,pushed_at,default_branch,size_kb,open_issues,rate_remaining,fetched_at,raw_json,
    resource_kind,technology,content_mode,activity_status,activity_days,l1_quality,homepage,forks_count,watchers_count,
    created_at_github,visibility,disabled,has_wiki,has_pages,has_discussions,l1_score
  ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(
    job.entity_id,job.full_name,r.status,String(x.id??''),String(x.node_id??''),String(x.description??''),x.archived?1:0,x.fork?1:0,
    Number(x.stargazers_count??0),String(x.language??''),String(x.license?.spdx_id??x.license?.name??''),JSON.stringify(topics),
    String(x.updated_at??''),String(x.pushed_at??''),String(x.default_branch??''),Number(x.size??0),Number(x.open_issues_count??0),
    Number(r.remaining??-1),now(),JSON.stringify(x),q.kind,q.technology,q.contentMode,q.activityStatus,q.activityDays,q.quality,
    String(x.homepage??''),Number(x.forks_count??0),Number(x.watchers_count??0),String(x.created_at??''),String(x.visibility??''),
    x.disabled?1:0,x.has_wiki?1:0,x.has_pages?1:0,x.has_discussions?1:0,q.score
  );
  applyExtendedL1(job.entity_id,x,q);
  syncSearchEntity(job.entity_id);
  db.prepare(`UPDATE jobs SET status='DONE', last_error=NULL, updated_at=? WHERE entity_id=?`).run(now(),job.entity_id);
}

async function autopilotPublicStep() {
  if (Date.now() < publicNextAttemptAt) return {done:0,state:'WAIT'};
  const job=db.prepare(`SELECT j.entity_id,j.full_name,j.attempts
                        FROM jobs j LEFT JOIN results r ON r.entity_id=j.entity_id
                        WHERE r.entity_id IS NULL AND j.status IN ('PENDING','RETRY')
                        ORDER BY j.rowid LIMIT 1`).get();
  if(!job) return {done:0,state:'EMPTY'};
  db.prepare(`UPDATE jobs SET status='RUNNING',attempts=attempts+1,updated_at=? WHERE entity_id=?`).run(now(),job.entity_id);
  try{
    const r=await fetchRepo(job.full_name);
    publicRateRemaining=Number(r.remaining??-1);
    if(r.status===404){
      db.prepare(`UPDATE jobs SET status='NOT_FOUND',last_error='HTTP_404',updated_at=? WHERE entity_id=?`).run(now(),job.entity_id);
      event('WARN','L1_PUBLIC_NOT_FOUND',job.full_name);
    }else{
      saveLiveResult(job,r);
      event('INFO','L1_PUBLIC_OK',job.full_name+'; remaining='+publicRateRemaining);
    }
    publicRateReset=Number(r.reset||0);
    publicNextAttemptAt=Date.now()+nextGitHubDelay(publicRateRemaining,publicRateReset);
    if(r.status!==404) coreSinceDeep++;
    return {done:r.status===404?0:1,state:'OK'};
  }catch(e){
    if(e.code==='RATE_LIMIT'){
      publicRateReset=Number(e.reset||0);
      publicNextAttemptAt=Math.max(Date.now()+60000,(publicRateReset*1000)+15000);
      db.prepare(`UPDATE jobs SET status='RETRY',last_error=?,updated_at=? WHERE entity_id=?`).run('GITHUB_RATE_LIMIT',now(),job.entity_id);
      event('WARN','L1_PUBLIC_RATE_LIMIT','reset='+publicRateReset);
      return {done:0,state:'RATE_LIMIT'};
    }
    const attempts=Number(job.attempts||0)+1,retry=attempts<3;
    db.prepare(`UPDATE jobs SET status=?,last_error=?,updated_at=? WHERE entity_id=?`).run(retry?'RETRY':'FAILED',String(e.message||e).slice(0,500),now(),job.entity_id);
    publicNextAttemptAt=Date.now()+120000;
    event('ERROR','L1_PUBLIC_ERROR',job.full_name+' :: '+String(e.message||e));
    return {done:0,state:'ERROR'};
  }
}

function fixtureCanary() {
  seed();
  stageFixtureJobs();
  const fixture = fixtureCorpus();
  let done = 0;
  for (const x of fixture) {
    const fullName = String(x.full_name || '');
    const id = entityId(fullName);
    db.prepare(`INSERT OR IGNORE INTO jobs(entity_id,full_name,status,attempts,updated_at)
                VALUES(?,?,'PENDING',0,?)`).run(id, fullName, now());
    if (upsertFixtureResult(x)) done++;
  }
  event('INFO','FIXTURE_CANARY_PASS','done=' + done + '; corpus=' + fixture.length);
  console.log(JSON.stringify({ ok:true, mode:'fixture', done, summary:statusSnapshot() }, null, 2));
}

function fixtureL2Canary() {
  const profiles = JSON.parse(readFileSync(join(ROOT, 'config', 'l2-fixture-10.json'), 'utf8'));
  let done = 0;
  const stmt = db.prepare(`INSERT OR REPLACE INTO l2_profiles(
    entity_id,human_summary,capabilities_json,use_cases_json,limitations_json,confidence,source,updated_at,
    stage,deep_status,score,evidence_json,readme_signals_json,attempts,last_error,source_version
  ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`);
  for (const p of profiles) {
    const id = entityId(p.full_name);
    const exists = db.prepare('SELECT entity_id FROM results WHERE entity_id=?').get(id);
    if (!exists) continue;
    stmt.run(id,String(p.summary||''),JSON.stringify(p.capabilities||[]),JSON.stringify(p.use_cases||[]),
      JSON.stringify(p.limitations||[]),Number(p.confidence||0),String(p.source||'fixture'),now(),
      'BASE','NOT_APPLICABLE',Math.round(Number(p.confidence||0)*100),JSON.stringify(['fixture contrôlée']),'{}',0,null,'fixture-v1');
    done++;
  }
  event('INFO','L2_FIXTURE_PASS','done=' + done);
  console.log(JSON.stringify({ok:true,mode:'l2-fixture',done,summary:statusSnapshot()},null,2));
}

const L2_RULESET_VERSION='2026.09-v4-semantic';
const SEARCH_INDEX_VERSION='2026.09-v3-semantic-with-legacy-fallback';
const L2_MIN_L1_SCORE=65;
const L2_README_RATE_RESERVE=2800;
const L2_RAW_FILE_MAX=262144;
let l2DeepNextAttemptAt=0;
let pipelineCycle=0;
let l1Cycle=0;

function jsonArray(v){try{const x=JSON.parse(v||'[]');return Array.isArray(x)?x:[]}catch{return[]}}
function jsonObject(v){try{const x=JSON.parse(v||'{}');return x&&typeof x==='object'&&!Array.isArray(x)?x:{} }catch{return{}}}
function uniqText(xs,max=16){return [...new Set(xs.map(x=>String(x||'').trim()).filter(Boolean))].slice(0,max)}
function frJoin(xs){xs=uniqText(xs,8);return xs.length<2?(xs[0]||''):xs.slice(0,-1).join(', ')+' et '+xs[xs.length-1]}
function sentence(v){v=String(v||'').trim();return v?v.replace(/\s+/g,' ').replace(/[.;:,\s]+$/,'')+'.':''}

const SEARCH_STOPWORDS=new Set(['a','au','aux','avec','ce','ces','dans','de','des','du','elle','en','et','eux','il','je','la','le','les','leur','lui','ma','mais','me','meme','mes','moi','mon','ne','nos','notre','nous','on','ou','par','pas','pour','qu','que','qui','sa','se','ses','son','sur','ta','te','tes','toi','ton','tu','un','une','vos','votre','vous','the','of','and','or','to','for','with','from','in','on','is','are','cherche','chercher','trouve','trouver','besoin','veux','voudrais','permet','permettre','faire','utiliser','usage','solution','projet','projets','outil','outils','logiciel','logiciels']);
function searchNormalize(v){return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
function searchConceptGroups(q){
  let x=searchNormalize(q).replace(/c\+\+/g,' cpp ').replace(/c#/g,' csharp ');
  const groups=[];
  const phrases=[
    [/base(?:s)? de donnees?/g,['database','sql','postgres','mysql','sqlite','redis']],
    [/intelligence artificielle/g,['ai','llm','artificial','intelligence']],
    [/ia locale/g,['local','ai','llm','localai','ollama']],
    [/a distance/g,['remote','distance']],
    [/auto[- ]?heberg(?:e|ee|er)/g,['selfhosted','self','hosted']],
    [/ligne de commande/g,['cli','terminal','command']],
    [/sauvegard(?:e|es)/g,['backup','snapshot','restore']],
    [/supervision/g,['monitoring','observability','monitor']],
    [/automatisation/g,['automation','workflow','automate']],
    [/controle/g,['control','remote','pilotage']],
    [/telephone/g,['mobile','android','ios']],
    [/ordinateur/g,['desktop','pc','computer']],
    [/hors ligne/g,['offline','local']],
    [/sans internet/g,['offline','local']],
    [/open source/g,['open','source','opensource']]
  ];
  for(const [rx,alts] of phrases){
    if(rx.test(x)){groups.push(alts);x=x.replace(rx,' ');}
  }
  for(const token of x.split(/[^a-z0-9_.+#-]+/).map(t=>t.replace(/^[-_.]+|[-_.]+$/g,'')).filter(t=>t.length>1&&!SEARCH_STOPWORDS.has(t))){
    const map={distance:['distance','remote'],distant:['remote','distance'],distante:['remote','distance'],sauvegarde:['backup','snapshot','restore'],sauvegarder:['backup','snapshot','restore'],monitoring:['monitoring','observability','monitor'],supervision:['monitoring','observability','monitor'],android:['android'],mobile:['mobile','android','ios'],telegram:['telegram'],docker:['docker','container'],offline:['offline','local'],local:['local','localai'],locale:['local','localai'],ia:['ai','llm','artificial'],agent:['agent','agents'],agents:['agent','agents'],workflow:['workflow','automation'],automatiser:['automation','workflow','automate'],automation:['automation','workflow','automate'],backup:['backup','snapshot','restore'],remote:['remote','distance'],database:['database','sql','postgres','mysql','sqlite'],donnees:['data','database'],gui:['gui','interface'],graphique:['gui','interface','ui'],interface:['interface','gui','ui'],leger:['lightweight','light','lowresource'],legere:['lightweight','light','lowresource'],reseau:['network','tcp','udp','wifi','lan'],securite:['security','secure'],securise:['secure','security','zerotrust'],securisee:['secure','security','zerotrust']};
    groups.push(map[token]||[token]);
  }
  return groups.slice(0,8);
}
function searchFtsTerm(term){
  const t=String(term||'').replace(/[^a-z0-9_]/g,'');
  return !t?'':(t.length<=3?t:t+'*');
}
function searchTextHasTerm(text,term){
  const t=searchNormalize(term).replace(/[^a-z0-9_]/g,'');if(!t)return false;
  const tokens=searchNormalize(text).split(/[^a-z0-9_]+/).filter(Boolean);
  if(t.length<=3)return tokens.includes(t);
  return tokens.some(x=>x===t||x.startsWith(t));
}
function searchFtsQuery(q,mode='broad'){
  const groups=searchConceptGroups(q);
  if(!groups.length)return '';
  const parts=groups.map(g=>'('+uniqText(g,8).map(searchFtsTerm).filter(Boolean).join(' OR ')+')').filter(x=>x!=='()');
  return parts.join(mode==='strict'?' AND ':' OR ');
}
function resolveSearchMatch(q){
  const groups=searchConceptGroups(q),strict=searchFtsQuery(q,'strict'),broad=searchFtsQuery(q,'broad');
  if(!broad)return {match:'',mode:'EMPTY',groups};
  let strictHits=0;
  try{if(strict)strictHits=Number(db.prepare('SELECT COUNT(*) AS n FROM search_fts WHERE search_fts MATCH ?').get(strict).n||0)}catch{}
  return {match:broad,mode:strictHits>0?'ALL_CONCEPTS_AVAILABLE':'RELAXED_CONCEPTS',strict_hits:strictHits,groups};
}
const searchResultCache=new Map();
function searchRanked(q){
  q=String(q||'').trim();
  const key=searchNormalize(q),cached=searchResultCache.get(key);
  if(cached&&Date.now()-cached.at<5000)return cached.value;
  const resolved=resolveSearchMatch(q),groups=resolved.groups||[],match=resolved.match;
  if(!groups.length||!match)return {items:[],total:0,groups:[],mode:'EMPTY'};
  const sql="SELECT r.entity_id,r.full_name,r.description,r.stars,r.language,r.license,r.topics_json,r.archived,r.fork,"+
    "r.updated_at_github,r.pushed_at,r.default_branch,r.size_kb,r.open_issues,r.fetched_at,"+
    "r.resource_kind,r.technology,r.content_mode,r.activity_status,r.activity_days,r.l1_quality,r.l1_score,"+
    "r.primary_theme,r.theme_path,r.theme_tags_json,r.theme_confidence,"+
    "l.human_summary,l.stage AS l2_stage,l.comprehension_score AS l2_score,l.l3_ready,"+
    "search_fts.title AS _title,search_fts.l1 AS _l1,search_fts.l2 AS _l2,search_fts.l3 AS _l3,search_fts.hidden AS _hidden,"+
    "bm25(search_fts,0.0,10.0,4.0,9.0,7.0,3.0) AS _bm25 "+
    "FROM search_fts JOIN results r ON r.entity_id=search_fts.entity_id "+
    "LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version=? "+
    "WHERE search_fts MATCH ? ORDER BY _bm25 ASC LIMIT 700";
  const candidates=db.prepare(sql).all(L2_RULESET_VERSION,match);
  const fieldWeights=[['_title',11],['_l2',10],['_l3',8],['_l1',6],['_hidden',4]];
  const phrase=searchNormalize(q),scored=[];
  for(const r of candidates){
    const fields=fieldWeights.map(([k,w])=>[searchNormalize(r[k]),w]);
    let hits=0,semantic=0;const matched=[];
    for(const group of groups){
      let best=0,bestTerm='';
      for(const term of group){
        const t=searchNormalize(term);
        for(const [txt,w] of fields){if(searchTextHasTerm(txt,t)&&w>best){best=w;bestTerm=t}}
      }
      if(best){hits++;semantic+=best;matched.push(bestTerm)}
    }
    const coverage=hits/groups.length,minCoverage=resolved.strict_hits>0?1:(groups.length<=2?0.5:groups.length<=4?0.5:0.4);
    if(coverage<minCoverage)continue;
    const title=searchNormalize(r.full_name),exactTitle=title===phrase?40:title.includes(phrase)?18:0;
    const depthBonus=r.l2_stage==='DEEP'?12:r.l2_stage==='BASE'?4:0;
    const readyBonus=Number(r.l3_ready||0)?5:0;
    const qualityBonus=Math.min(10,Number(r.l2_score||0)/12)+Math.min(6,Number(r.l1_score||0)/18);
    const referenceIntent=/(awesome|catalog|catalogue|guide|documentation|reference|liste|ressource)/.test(phrase);
    const kind=String(r.resource_kind||'');
    const kindBonus=kind==='Projet logiciel'?10:(!referenceIntent&&kind==='Catalogue de ressources'?-18:!referenceIntent&&kind==='Guide / documentation'?-10:0);
    const score=coverage*180+semantic*3+exactTitle+depthBonus+readyBonus+qualityBonus+kindBonus;
    scored.push({...r,search_score:Number(score.toFixed(2)),search_coverage:Number(coverage.toFixed(3)),search_hits:hits,search_groups:groups.length,search_terms:matched,search_mode:resolved.mode});
  }
  scored.sort((x,y)=>y.search_score-x.search_score||Number(y.l2_score||0)-Number(x.l2_score||0)||Number(y.l1_score||0)-Number(x.l1_score||0)||Number(y.stars||0)-Number(x.stars||0));
  const value={items:scored,total:scored.length,groups,mode:resolved.mode};
  searchResultCache.set(key,{at:Date.now(),value});
  if(searchResultCache.size>50){const first=searchResultCache.keys().next().value;searchResultCache.delete(first)}
  return value;
}
function syncSearchEntity(entityIdValue){
  try{
    const r=db.prepare(`SELECT r.entity_id,r.full_name,r.description,r.language,r.license,r.topics_json,r.resource_kind,r.technology,r.content_mode,r.activity_status,r.primary_theme,r.theme_path,r.theme_tags_json,r.l1_summary,
      l.human_summary,l.capabilities_json,l.use_cases_json,l.limitations_json,l.dossier_json,l.retrieval_text,
      lx.human_summary AS legacy_summary,lx.dossier_json AS legacy_dossier,lx.source_version AS legacy_l2_version,
      a.action_json,ax.action_json AS legacy_action,ax.source_l2_version AS legacy_l3_version
      FROM results r
      LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version=?
      LEFT JOIN l2_profiles lx ON lx.entity_id=r.entity_id
      LEFT JOIN l3_actions a ON a.entity_id=r.entity_id AND a.source_l2_version=?
      LEFT JOIN l3_actions ax ON ax.entity_id=r.entity_id
      WHERE r.entity_id=?`).get(L2_RULESET_VERSION,L2_RULESET_VERSION,entityIdValue);
    db.prepare('DELETE FROM search_fts WHERE entity_id=?').run(entityIdValue);
    if(!r)return;
    const l1=[r.description,r.language,r.license,r.topics_json,r.resource_kind,r.technology,r.content_mode,r.activity_status,r.primary_theme,r.theme_path,r.theme_tags_json,r.l1_summary].filter(Boolean).join(' ');
    const l2=[r.human_summary,r.capabilities_json,r.use_cases_json,r.limitations_json,r.dossier_json].filter(Boolean).join(' ');
    const legacyL2=r.legacy_l2_version&&r.legacy_l2_version!==L2_RULESET_VERSION?[r.legacy_summary,r.legacy_dossier].filter(Boolean).join(' '):'';
    const legacyL3=r.legacy_l3_version&&r.legacy_l3_version!==L2_RULESET_VERSION?String(r.legacy_action||''):'';
    const hidden=[r.retrieval_text,legacyL2,legacyL3].filter(Boolean).join(' ');
    db.prepare('INSERT INTO search_fts(entity_id,title,l1,l2,l3,hidden) VALUES(?,?,?,?,?,?)').run(r.entity_id,r.full_name||'',l1,l2,r.action_json||'',hidden);
    searchResultCache.clear();
  }catch(e){try{event('WARN','SEARCH_SYNC_ERROR',String(entityIdValue)+' :: '+String(e.message||e).slice(0,240))}catch{}}
}
function rebuildSearchIndex(){
  const started=Date.now();
  try{
    db.exec('BEGIN IMMEDIATE');
    db.exec('DELETE FROM search_fts');
    db.prepare(`INSERT INTO search_fts(entity_id,title,l1,l2,l3,hidden)
      SELECT r.entity_id,
             coalesce(r.full_name,''),
             trim(coalesce(r.description,'')||' '||coalesce(r.language,'')||' '||coalesce(r.license,'')||' '||coalesce(r.topics_json,'')||' '||coalesce(r.resource_kind,'')||' '||coalesce(r.technology,'')||' '||coalesce(r.content_mode,'')||' '||coalesce(r.activity_status,'')||' '||coalesce(r.primary_theme,'')||' '||coalesce(r.theme_path,'')||' '||coalesce(r.theme_tags_json,'')||' '||coalesce(r.l1_summary,'')),
             trim(coalesce(l.human_summary,'')||' '||coalesce(l.capabilities_json,'')||' '||coalesce(l.use_cases_json,'')||' '||coalesce(l.limitations_json,'')||' '||coalesce(l.dossier_json,'')),
             coalesce(a.action_json,''),
             trim(coalesce(l.retrieval_text,'')||' '||CASE WHEN lx.source_version<>? THEN coalesce(lx.human_summary,'')||' '||coalesce(lx.dossier_json,'') ELSE '' END||' '||CASE WHEN ax.source_l2_version<>? THEN coalesce(ax.action_json,'') ELSE '' END)
      FROM results r
      LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version=?
      LEFT JOIN l2_profiles lx ON lx.entity_id=r.entity_id
      LEFT JOIN l3_actions a ON a.entity_id=r.entity_id AND a.source_l2_version=?
      LEFT JOIN l3_actions ax ON ax.entity_id=r.entity_id`).run(L2_RULESET_VERSION,L2_RULESET_VERSION,L2_RULESET_VERSION,L2_RULESET_VERSION);
    const total=Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n||0);
    db.prepare("INSERT INTO search_meta(key,value) VALUES('index_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value").run(SEARCH_INDEX_VERSION);
    db.prepare("INSERT INTO search_meta(key,value) VALUES('indexed_count',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value").run(String(total));
    db.exec('COMMIT');
    searchResultCache.clear();
    event('INFO','SEARCH_INDEX_REBUILT','rows='+total+'; ms='+(Date.now()-started));
    return total;
  }catch(e){
    try{db.exec('ROLLBACK')}catch{}
    event('ERROR','SEARCH_INDEX_REBUILD_ERROR',String(e.message||e));
    throw e;
  }
}
function ensureSearchIndex(force=false){
  try{
    const v=db.prepare("SELECT value FROM search_meta WHERE key='index_version'").get()?.value||'';
    const indexed=Number(db.prepare('SELECT COUNT(*) AS n FROM search_fts').get().n||0);
    const total=Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n||0);
    if(v===SEARCH_INDEX_VERSION&&indexed===total)return indexed;
    if(force||process.env.TLIB_BACKGROUND_WORKER==='1')return rebuildSearchIndex();
    return indexed;
  }catch{
    if(force||process.env.TLIB_BACKGROUND_WORKER==='1')return rebuildSearchIndex();
    return 0;
  }
}

const L2_SIGNAL_RULES=[
  ['API / intégration',/\bapi\b|rest|graphql|webhook|sdk|integration/],
  ['Ligne de commande / automatisation',/\bcli\b|command[- ]line|terminal|shell|powershell|automation|script/],
  ['Bibliothèque / SDK',/library|framework|sdk|package|module|dependency/],
  ['Application web',/web app|frontend|backend|server|browser|http|website|next\.js|react|vue|angular/],
  ['Application mobile',/android|ios|mobile|flutter|react native|capacitor|expo/],
  ['Données / stockage',/database|sqlite|postgres|mysql|mongodb|redis|dataset|storage|vector/],
  ['IA / apprentissage automatique',/machine learning|deep learning|\bllm\b|artificial intelligence|generative ai|neural|transformer/],
  ['Réseau / communication',/network|tcp|udp|dns|wifi|mqtt|websocket|telegram|messag/],
  ['Cloud / DevOps',/docker|kubernetes|terraform|ci[- ]?cd|github actions|cloud|deployment|container/],
  ['Sécurité / authentification',/security|auth|oauth|encrypt|crypt|vulnerability|pentest|malware|jwt/],
  ['Observabilité / supervision',/monitor|metrics|logging|telemetry|tracing|observability/],
  ['Documentation / apprentissage',/documentation|tutorial|guide|course|learning|reference|awesome/]
];
const L2_PURPOSE_MAP={
  'API / intégration':'S’intégrer à d’autres applications ou exposer des fonctions programmatiques.',
  'Ligne de commande / automatisation':'Automatiser des tâches techniques depuis un terminal ou un script.',
  'Bibliothèque / SDK':'Être réutilisé comme composant logiciel dans un autre projet.',
  'Application web':'Fournir ou soutenir une interface ou un service accessible sur le Web.',
  'Application mobile':'Construire, exécuter ou accompagner une expérience sur téléphone ou tablette.',
  'Données / stockage':'Lire, transformer, indexer, conserver ou servir des données.',
  'IA / apprentissage automatique':'Exécuter ou intégrer des fonctions liées à l’intelligence artificielle ou à l’apprentissage automatique.',
  'Réseau / communication':'Échanger des données entre appareils, services ou utilisateurs.',
  'Cloud / DevOps':'Construire, déployer, conteneuriser ou automatiser une infrastructure.',
  'Sécurité / authentification':'Gérer des contrôles de sécurité, d’identité ou de protection des données.',
  'Observabilité / supervision':'Mesurer, journaliser ou superviser le comportement d’un système.',
  'Documentation / apprentissage':'Servir de référence, de guide ou de corpus d’apprentissage.'
};
const L2_AUDIENCE_MAP={
  'API / intégration':'développeurs qui intègrent des services ou des API',
  'Ligne de commande / automatisation':'développeurs, administrateurs et utilisateurs techniques',
  'Bibliothèque / SDK':'développeurs qui réutilisent des bibliothèques',
  'Application web':'développeurs web et équipes produit',
  'Application mobile':'développeurs mobile et équipes produit',
  'Données / stockage':'développeurs data, backend et opérateurs de bases',
  'IA / apprentissage automatique':'développeurs IA, data scientists et intégrateurs',
  'Réseau / communication':'développeurs réseau, backend et systèmes',
  'Cloud / DevOps':'équipes DevOps, SRE et administrateurs',
  'Sécurité / authentification':'développeurs sécurité et administrateurs',
  'Observabilité / supervision':'équipes exploitation, SRE et développeurs',
  'Documentation / apprentissage':'apprenants, mainteneurs et développeurs'
};

const L2_ROLE_RULES=[
  {id:'coding-agent-orchestrator',rx:/coding agents?|agent orchestrator|orchestrat(?:e|or).*agents?|parallel agents?|agentic coding|worktrees?.*agents?|agents?.*worktrees?|ai orchestrator/,nature:'orchestrateur d’agents de développement',purpose:'Orchestrer plusieurs agents de code, isoler leurs travaux et comparer ou piloter leurs résultats.',audience:'développeurs qui travaillent avec plusieurs agents de code',operation:'Il coordonne plusieurs agents de développement et leurs espaces de travail, puis centralise leur suivi et leurs actions.'},
  {id:'local-ai-engine',rx:/open[- ]source ai engine|localai|local ai engine|local llm|self[- ]hosted llm|llm inference|run any model|openai[- ]compatible.*(?:local|inference)/,nature:'moteur d’intelligence artificielle local et auto-hébergeable',purpose:'Exécuter et exposer localement des modèles d’IA sans dépendre obligatoirement d’un service cloud.',audience:'développeurs et équipes qui veulent exécuter ou intégrer des modèles d’IA localement',operation:'Il exécute des modèles sur la machine ou l’infrastructure de l’utilisateur et les expose via des interfaces programmatiques ou des outils locaux.'},
  {id:'remote-desktop',rx:/remote desktop|alternative to teamviewer|screen sharing|desktop remote control|remote desktop application/,nature:'solution de bureau à distance',purpose:'Accéder à un ordinateur distant, afficher son écran et le contrôler à travers le réseau.',audience:'utilisateurs et administrateurs qui ont besoin de contrôler des machines à distance',operation:'Il relie un client à une machine distante afin d’afficher et contrôler sa session, avec des composants réseau et clients multiplateformes.'},
  {id:'secure-remote-access',rx:/secure remote access|zero[- ]trust access|vpn replacement|wireguard.*access|remote access.*(?:security|vpn|wireguard)|(?:security|vpn|wireguard).*remote access|connectivity to apps.*infrastructure/,nature:'plateforme d’accès distant sécurisé',purpose:'Donner un accès distant contrôlé à des applications, appareils ou infrastructures sans exposer directement les ressources.',audience:'équipes réseau, sécurité et exploitation qui gèrent des accès distants',operation:'Il établit des chemins d’accès réseau authentifiés entre utilisateurs, appareils et ressources protégées.'},
  {id:'mobile-automation-mcp',rx:/mcp server.*mobile|mobile automation|automating.*(?:ios|android)|ios.*android.*automation|mobile development and automation/,nature:'serveur d’automatisation et de contrôle d’appareils mobiles',purpose:'Permettre à des agents ou scripts de piloter, tester et inspecter des applications iOS ou Android.',audience:'développeurs mobile, testeurs et intégrateurs d’agents IA',operation:'Il expose des outils structurés pour découvrir les appareils, lancer des applications, lire l’interface et exécuter des gestes ou saisies.'},
  {id:'workflow-automation',rx:/workflow automation|automation platform|workflow engine|low[- ]code automation|automate workflows|400\+ integrations/,nature:'plateforme d’automatisation de workflows',purpose:'Construire et exécuter des workflows reliant plusieurs services, données et actions.',audience:'équipes techniques et métiers qui automatisent des processus',operation:'Il enchaîne des déclencheurs, intégrations et étapes de traitement dans des workflows configurables.'},
  {id:'backup',rx:/backup docker volumes|backup tool|continuous backup|automatic backups?|snapshot and restore|disaster recovery/,nature:'outil de sauvegarde et de restauration',purpose:'Créer, conserver et restaurer des sauvegardes de données ou de volumes.',audience:'administrateurs et utilisateurs qui protègent des données ou services',operation:'Il copie les données vers un stockage cible selon une politique de sauvegarde et fournit un chemin de restauration.'},
  {id:'api-client',rx:/api development ecosystem|api client|alternative to postman|rest client/,nature:'outil de développement et de test d’API',purpose:'Construire, envoyer, inspecter et automatiser des requêtes vers des API.',audience:'développeurs et testeurs d’API',operation:'Il permet de définir des requêtes, gérer des environnements et examiner les réponses de services API.'},
  {id:'database-gui',rx:/database editor|database gui|redis gui|sql client|database management tool/,nature:'interface de gestion de bases de données',purpose:'Explorer, administrer ou modifier des bases de données à partir d’une interface dédiée.',audience:'développeurs et administrateurs de bases de données',operation:'Il se connecte à un moteur de données et fournit des vues ou commandes pour inspecter et modifier son contenu.'},
  {id:'monitoring',rx:/uptime monitor|monitoring platform|observability platform|network visibility|asset discovery|monitor websites|monitoring and performance/,nature:'outil de supervision et d’observabilité',purpose:'Surveiller l’état, les changements ou les performances d’un système et signaler les anomalies.',audience:'équipes exploitation, réseau, DevOps et SRE',operation:'Il collecte des signaux d’état ou de performance, les présente et permet de détecter les changements ou incidents.'},
  {id:'messaging-bot',rx:/telegram bot|discord bot|chat bot|messaging bot/,nature:'bot ou automatisation de messagerie',purpose:'Automatiser des commandes, notifications ou interactions depuis une plateforme de messagerie.',audience:'développeurs et utilisateurs qui automatisent des interactions de messagerie',operation:'Il reçoit des événements ou commandes depuis la messagerie, exécute une logique puis renvoie des réponses ou notifications.'}
];

function l2PrimaryRole(r,sig={},signals=[]){
  const desc=String(r.description||''),identity=String(sig.identity_excerpt||''),features=Array.isArray(sig.feature_lines)?sig.feature_lines.join(' '):'';
  const fullName=String(r.full_name||''),meta=[fullName,r.topics_json,r.theme_path,r.theme_tags_json].filter(Boolean).join(' ');
  const descBag=desc.toLowerCase(),readmeBag=(identity+' '+features).toLowerCase(),metaBag=meta.toLowerCase();
  const context=(meta+' '+desc+' '+identity+' '+features).toLowerCase();
  for(const role of L2_ROLE_RULES){
    if(!role.rx.test(context))continue;
    if(role.rx.test(descBag))return {...role,confidence:0.96,identity_source:'GITHUB_DESCRIPTION',identity_basis_fr:'Rôle principal reconnu directement dans la description GitHub du dépôt.'};
    if(role.rx.test(readmeBag))return {...role,confidence:0.94,identity_source:'README_IDENTITY',identity_basis_fr:'Rôle principal reconnu dans l’introduction ou les fonctionnalités structurantes du README.'};
    if(role.rx.test(metaBag))return {...role,confidence:0.82,identity_source:'L1_METADATA',identity_basis_fr:'Rôle principal déduit du nom, des topics et du classement fonctionnel L1 ; confirmation README recommandée.'};
  }
  if(r.resource_kind==='Catalogue de ressources')return {id:'catalogue',nature:'catalogue de ressources techniques',purpose:'Repérer, comparer et retrouver des ressources techniques dans un domaine donné.',audience:'développeurs et utilisateurs qui explorent un domaine technique',operation:'Il organise des liens et références afin de faciliter leur découverte.',confidence:0.88,identity_source:'L1_RESOURCE_KIND',identity_basis_fr:'Identité fondée sur le type de ressource vérifié en L1 : catalogue de ressources.'};
  if(r.resource_kind==='Guide / documentation')return {id:'documentation',nature:'guide ou documentation technique',purpose:'Expliquer une technologie ou une procédure et servir de référence.',audience:'apprenants, développeurs et mainteneurs',operation:'Il organise des explications, exemples et références autour d’un sujet technique.',confidence:0.88,identity_source:'L1_RESOURCE_KIND',identity_basis_fr:'Identité fondée sur le type de ressource vérifié en L1 : guide ou documentation.'};
  if(signals.includes('API / intégration'))return {id:'integration-software',nature:'projet logiciel orienté intégration',purpose:L2_PURPOSE_MAP['API / intégration'],audience:L2_AUDIENCE_MAP['API / intégration'],operation:'Il expose ou consomme des interfaces permettant de relier plusieurs composants logiciels.',confidence:0.62,identity_source:'SIGNAL_FALLBACK',identity_basis_fr:'Identité provisoire déduite de signaux fonctionnels ; le README doit encore confirmer la fonction principale.'};
  if(signals.includes('Bibliothèque / SDK'))return {id:'library',nature:'bibliothèque ou SDK réutilisable',purpose:L2_PURPOSE_MAP['Bibliothèque / SDK'],audience:L2_AUDIENCE_MAP['Bibliothèque / SDK'],operation:'Il fournit des composants logiciels destinés à être appelés depuis un autre projet.',confidence:0.60,identity_source:'SIGNAL_FALLBACK',identity_basis_fr:'Identité provisoire déduite de signaux de bibliothèque/SDK ; confirmation documentaire requise.'};
  if(signals.includes('Application web'))return {id:'web-app',nature:'application ou service Web',purpose:L2_PURPOSE_MAP['Application web'],audience:L2_AUDIENCE_MAP['Application web'],operation:'Il fournit une interface ou un service accessible à travers des technologies Web.',confidence:0.58,identity_source:'SIGNAL_FALLBACK',identity_basis_fr:'Identité provisoire déduite de signaux Web ; confirmation documentaire requise.'};
  if(signals.includes('Ligne de commande / automatisation'))return {id:'cli-tool',nature:'outil technique en ligne de commande ou d’automatisation',purpose:L2_PURPOSE_MAP['Ligne de commande / automatisation'],audience:L2_AUDIENCE_MAP['Ligne de commande / automatisation'],operation:'Il est piloté depuis un terminal ou un script pour automatiser une tâche technique.',confidence:0.58,identity_source:'SIGNAL_FALLBACK',identity_basis_fr:'Identité provisoire déduite de signaux CLI/automatisation ; confirmation documentaire requise.'};
  return {id:'generic-software',nature:String(r.resource_kind||'projet logiciel').toLowerCase(),purpose:'Fournir les fonctions décrites par le dépôt ; la finalité principale doit encore être confirmée par des preuves plus profondes.',audience:'utilisateurs techniques du domaine concerné',operation:'Son fonctionnement précis doit encore être confirmé par la documentation et la structure du dépôt.',confidence:0.42,identity_source:'INSUFFICIENT_EVIDENCE',identity_basis_fr:'Les preuves actuelles ne suffisent pas à déterminer une fonction principale fiable.'};
}
function l2PurposeSignals(roleId,signals){
  const allow={
    'coding-agent-orchestrator':['API / intégration','Ligne de commande / automatisation','Cloud / DevOps'],
    'local-ai-engine':['API / intégration','IA / apprentissage automatique','Données / stockage','Bibliothèque / SDK','Cloud / DevOps'],
    'remote-desktop':['Réseau / communication','Sécurité / authentification','Application mobile'],
    'secure-remote-access':['Réseau / communication','Sécurité / authentification','Cloud / DevOps'],
    'mobile-automation-mcp':['Application mobile','API / intégration','Ligne de commande / automatisation'],
    'workflow-automation':['Ligne de commande / automatisation','API / intégration','Données / stockage','Cloud / DevOps'],
    'backup':['Données / stockage','Cloud / DevOps'],
    'api-client':['API / intégration','Réseau / communication','Données / stockage'],
    'database-gui':['Données / stockage','Application web'],
    'monitoring':['Observabilité / supervision','Réseau / communication','Cloud / DevOps'],
    'messaging-bot':['Réseau / communication','API / intégration','Ligne de commande / automatisation']
  };
  const wanted=allow[roleId];return wanted?signals.filter(x=>wanted.includes(x)):signals;
}
function l2Signals(text){const bag=String(text||'').toLowerCase(),out=[];for(const [label,rx] of L2_SIGNAL_RULES)if(rx.test(bag))out.push(label);return uniqText(out,10)}
function cleanMarkdownText(text){return String(text||'').replace(/```[\s\S]*?```/g,' ').replace(/!\[[^\]]*\]\([^)]*\)/g,' ').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/<[^>]+>/g,' ').replace(/[\t ]+/g,' ').replace(/\r/g,'')}
function extractReadmeCommands(raw){
  const out=[],accept=(line)=>{
    const x=String(line||'').trim().replace(/^(?:\$|>|PS>)\s*/i,'');
    if(!x||x.length>200)return;
    if(/^(npm|pnpm|yarn|npx|node|bun|python|python3|pip|pip3|pipx|uv|poetry|conda|docker|docker-compose|podman|make|cmake|meson|cargo|go|dotnet|java|gradle|mvn|powershell|pwsh|git|curl|wget|helm|kubectl|brew|apt|apt-get|winget|choco|bash|sh)\b/i.test(x)||/^\.[\\/][^\s]+/.test(x))out.push(x);
  };
  for(const m of String(raw||'').matchAll(/```[^\n]*\n([\s\S]*?)```/g))for(const line of String(m[1]||'').split(/\r?\n/))accept(line);
  for(const m of String(raw||'').matchAll(/\x60([^\x60\n]{3,200})\x60/g))accept(m[1]);
  return uniqText(out,18);
}
function readmeSignals(text){
  const raw=String(text||'').slice(0,65536),clean=cleanMarkdownText(raw);
  const headings=uniqText([...raw.matchAll(/^#{1,3}\s+(.+)$/gm)].map(m=>m[1].replace(/[#*_`]/g,'').trim()),20);
  const lines=raw.split(/\r?\n/).map(x=>x.replace(/<[^>]+>/g,' ').replace(/!\[[^\]]*\]\([^)]*\)/g,' ').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/^[#>*+\-\s]+/,'').replace(/[`*_]/g,'').trim()).filter(x=>x.length>=28&&x.length<=360&&!/^https?:\/\//i.test(x)&&!/shields\.io|badge|license:|downloads|discord|follow us/i.test(x));
  const identityLines=uniqText(lines.slice(0,18),12);
  const featureLines=uniqText(lines.filter(x=>/feature|support|allows?|provides?|enables?|works with|run |build |monitor|control|backup|agent|api|automation|remote|local|self[- ]host/i.test(x)).slice(0,24),18);
  const identity_excerpt=identityLines.join(' ').slice(0,3200);
  const signals=l2Signals([headings.join(' '),identity_excerpt,featureLines.join(' '),clean.slice(0,18000)].join(' '));
  const commands=extractReadmeCommands(raw),h=headings.join(' ').toLowerCase();
  return {headings,signals,commands,chars:raw.length,identity_excerpt,feature_lines:featureLines,sections:{installation:/install|setup|getting started|quick start|prerequisite/.test(h),usage:/usage|how to use|example|tutorial|quick start/.test(h),configuration:/config|environment|settings|variables/.test(h),api:/\bapi\b|reference|sdk/.test(h),deployment:/deploy|docker|kubernetes|production|hosting/.test(h),architecture:/architecture|design|structure|internals/.test(h),contributing:/contribut|development/.test(h)}};
}
function repoApiBase(fullName){return '/repos/'+String(fullName||'').split('/').map(encodeURIComponent).join('/')}
async function githubRawText(fullName,branch,path,maxBytes=L2_RAW_FILE_MAX){const url='https://raw.githubusercontent.com/'+String(fullName).split('/').map(encodeURIComponent).join('/')+'/'+encodeURIComponent(String(branch||'main'))+'/'+String(path).split('/').map(encodeURIComponent).join('/');const res=await fetch(url,{headers:{'User-Agent':'TLIB-PC-Agent/0.3'},signal:AbortSignal.timeout(12000)});if(res.status===404)return null;if(!res.ok)throw new Error('RAW_HTTP_'+res.status+' '+path);const len=Number(res.headers.get('content-length')||0);if(len>maxBytes)return null;const txt=await res.text();return txt.length>maxBytes?txt.slice(0,maxBytes):txt}
async function rootInventory(fullName,branch){const rr=await githubGet(repoApiBase(fullName)+'/contents?ref='+encodeURIComponent(String(branch||'main')),true);if(rr.status===404||!Array.isArray(rr.body))return {names:[],files:[],dirs:[]};const files=rr.body.filter(x=>x&&x.type==='file').map(x=>String(x.name||''));const dirs=rr.body.filter(x=>x&&x.type==='dir').map(x=>String(x.name||''));return {names:files.concat(dirs),files,dirs}}
async function manifestFacts(r,inventory){
  const names=new Set((inventory.files||[]).map(x=>String(x).toLowerCase()));
  const candidates=['package.json','pyproject.toml','requirements.txt','dockerfile','docker-compose.yml','compose.yml','go.mod','cargo.toml'];
  const selected=candidates.filter(x=>names.has(x)).slice(0,6);
  const facts={files:selected,commands:[],dependencies:[],scripts:[],services:[],runtime:[],config_files:[],raw_detected:inventory.names||[]};
  const addDeps=(xs)=>{facts.dependencies=uniqText([...facts.dependencies,...(xs||[])],28)};
  const addCmd=(xs)=>{facts.commands=uniqText([...facts.commands,...(xs||[])],18)};
  for(const p of selected){
    try{
      const actual=(inventory.files||[]).find(x=>String(x).toLowerCase()===p)||p;
      const txt=await githubRawText(r.full_name,r.default_branch||'main',actual);if(!txt)continue;
      if(p==='package.json'){
        let j={};try{j=JSON.parse(txt)}catch{}
        const pm=names.has('pnpm-lock.yaml')?'pnpm':names.has('yarn.lock')?'yarn':(names.has('bun.lockb')||names.has('bun.lock'))?'bun':'npm';
        facts.scripts=uniqText(Object.keys(j.scripts||{}),18);
        addCmd([pm==='yarn'?'yarn install':pm+' install',...Object.keys(j.scripts||{}).map(k=>pm+' run '+k)]);
        addDeps([...Object.keys(j.dependencies||{}),...Object.keys(j.peerDependencies||{}),...Object.keys(j.optionalDependencies||{}),...Object.keys(j.devDependencies||{}).slice(0,12)]);
        facts.runtime.push(j.engines?'Node '+Object.entries(j.engines).map(([k,v])=>k+' '+v).join(', '):'Node.js / JavaScript');
      }else if(p==='requirements.txt'){
        addDeps(txt.split(/\r?\n/).map(x=>x.trim().split(/[<=>~!;\[]/)[0]).filter(x=>x&&!x.startsWith('#')&&!x.startsWith('-')));
        addCmd(['pip install -r requirements.txt']);facts.runtime.push('Python');
      }else if(p==='pyproject.toml'){
        facts.runtime.push('Python');
        const arr=txt.match(/(?:^|\n)\s*dependencies\s*=\s*\[([\s\S]*?)\]/i);
        if(arr)addDeps([...arr[1].matchAll(/["']([^"']+)["']/g)].map(m=>m[1].split(/[<=>~!;\[]/)[0].trim()));
        const poetry=txt.match(/\[tool\.poetry\.dependencies\]([\s\S]*?)(?=\n\[|$)/i);
        if(poetry)addDeps(poetry[1].split(/\r?\n/).map(x=>(x.match(/^\s*([A-Za-z0-9_.-]+)\s*=/)||[])[1]).filter(x=>x&&x.toLowerCase()!=='python'));
        const scripts=txt.match(/\[(?:project\.scripts|tool\.poetry\.scripts)\]([\s\S]*?)(?=\n\[|$)/i);
        if(scripts)facts.scripts=uniqText([...facts.scripts,...scripts[1].split(/\r?\n/).map(x=>(x.match(/^\s*([A-Za-z0-9_.-]+)\s*=/)||[])[1]).filter(Boolean)],18);
        addCmd(['pip install .',...facts.scripts.slice(0,8)]);
      }else if(p==='go.mod'){
        const mod=txt.match(/^module\s+(.+)$/m);facts.runtime.push(mod?'Go · module '+mod[1].trim():'Go');
        const block=txt.match(/require\s*\(([\s\S]*?)\)/m),single=[...txt.matchAll(/^require\s+([^\s]+)\s+/gm)].map(m=>m[1]);
        const req=block?block[1].split(/\r?\n/).map(x=>x.trim().split(/\s+/)[0]).filter(x=>x&&!x.startsWith('//')):[];
        addDeps([...req,...single]);addCmd(['go build ./...']);
      }else if(p==='cargo.toml'){
        facts.runtime.push('Rust / Cargo');
        const deps=[];
        for(const sec of txt.matchAll(/\[(?:dev-|build-)?dependencies(?:\.[^\]]+)?\]([\s\S]*?)(?=\n\[|$)/gi)){deps.push(...sec[1].split(/\r?\n/).map(x=>(x.match(/^\s*([A-Za-z0-9_-]+)\s*=/)||[])[1]).filter(Boolean))}
        addDeps(deps);addCmd(['cargo build']);
      }else if(p==='dockerfile'){
        const images=[...txt.matchAll(/^\s*FROM\s+([^\s]+).*$/gim)].map(m=>m[1]);
        facts.runtime.push(images.length?'Docker · images '+uniqText(images,4).join(', '):'Docker');addCmd(['docker build .']);
      }else if(/compose/.test(p)){
        facts.runtime.push('Docker Compose');addCmd(['docker compose up']);
        const after=(txt.match(/(?:^|\n)services:\s*\n([\s\S]*?)(?=\n\S|$)/i)||[])[1]||'';
        facts.services=uniqText([...facts.services,...after.split(/\r?\n/).map(x=>(x.match(/^\s{2,}([A-Za-z0-9_.-]+):\s*(?:#.*)?$/)||[])[1]).filter(Boolean)],16);
      }
    }catch(e){event('WARN','L2_MANIFEST_READ_FAIL',r.full_name+' '+p+' '+String(e.message||e).slice(0,180))}
  }
  facts.config_files=uniqText((inventory.files||[]).filter(x=>/^(?:\.env|config|settings|.*\.ya?ml$|.*\.toml$)/i.test(x)),12);
  facts.runtime=uniqText(facts.runtime,10);facts.commands=uniqText(facts.commands,18);facts.dependencies=uniqText(facts.dependencies,28);facts.services=uniqText(facts.services,16);
  return facts;
}
function l2Nature(r,signals,role){return role&&role.nature?role.nature:String(r.resource_kind||'projet logiciel').toLowerCase()}
function l2FrenchDossier(r,sig={signals:[],commands:[],sections:{}},inventory={names:[],files:[],dirs:[]},facts={files:[],commands:[],dependencies:[],scripts:[],services:[],runtime:[],config_files:[]}){
  const topics=jsonArray(r.topics_json),tags=jsonArray(r.theme_tags_json),langs=Object.keys(jsonObject(r.languages_json));
  const baseText=[r.full_name,r.description,r.l1_summary,r.resource_kind,r.technology,r.content_mode,r.primary_theme,r.theme_path,r.language,topics.join(' '),tags.join(' '),langs.join(' ')].filter(Boolean).join(' ');
  const signals=uniqText([...l2Signals(baseText),...(Array.isArray(sig.signals)?sig.signals:[])],12);
  const role=l2PrimaryRole(r,sig,signals);
  const tech=r.technology||r.language||langs[0]||'technologie principale non déterminée',nature=l2Nature(r,signals,role);
  const purposeSignals=l2PurposeSignals(role.id,signals);
  const purposes=uniqText([role.purpose,...purposeSignals.map(x=>L2_PURPOSE_MAP[x]).filter(Boolean)],7);
  const audiences=uniqText([role.audience,...signals.map(x=>L2_AUDIENCE_MAP[x]).filter(Boolean)],9);
  const interfaces=uniqText([signals.includes('Ligne de commande / automatisation')?'Ligne de commande / scripts':'',signals.includes('API / intégration')?'API ou interface d’intégration':'',signals.includes('Application web')?'Interface ou service Web':'',signals.includes('Application mobile')?'Interface ou composant mobile':'',signals.includes('Bibliothèque / SDK')?'Bibliothèque / SDK':''],8);
  const commands=uniqText([...(Array.isArray(sig.commands)?sig.commands:[]),...(facts.commands||[])],14);
  const architecture=uniqText(['Technologie principale : '+tech,langs.length?'Langages détectés : '+frJoin(langs.slice(0,6)):'',(facts.runtime||[]).length?'Environnement d’exécution : '+frJoin(facts.runtime):'',(inventory.dirs||[]).length?'Répertoires racine observés : '+frJoin(inventory.dirs.slice(0,10)):'',(facts.files||[]).length?'Fichiers techniques détectés : '+frJoin(facts.files):'',(facts.services||[]).length?'Services déclarés : '+frJoin(facts.services):''],12);
  const setup=uniqText([commands.length?'Commandes documentées ou déduites : '+commands.slice(0,6).join(' ; '):'',sig.sections&&sig.sections.installation?'Le README contient une section d’installation ou de démarrage rapide.':'',(facts.config_files||[]).length?'Configuration repérée : '+frJoin(facts.config_files):''],10);
  const integrations=uniqText([signals.includes('Données / stockage')?'Stockage ou base de données détecté dans les signaux du projet.':'',signals.includes('Réseau / communication')?'Communication réseau ou messagerie détectée.':'',signals.includes('Cloud / DevOps')?'Déploiement ou infrastructure automatisée détecté.':'',signals.includes('Sécurité / authentification')?'Mécanisme de sécurité ou d’authentification détecté.':'',...(facts.services||[]).map(x=>'Service déclaré : '+x)],10);
  const dependencies=uniqText(facts.dependencies||[],20);
  const deployment=uniqText([(facts.runtime||[]).some(x=>/Docker/.test(x))?'Exécution ou déploiement conteneurisé prévu ou documenté.':'',signals.includes('Cloud / DevOps')?'Le projet comporte des signaux de déploiement, CI/CD ou infrastructure.':'',signals.includes('Application mobile')?'Une cible ou un compagnon mobile est détecté ; cela ne signifie pas nécessairement que le mobile est la fonction principale.':'',sig.sections&&sig.sections.deployment?'Le README possède une section de déploiement ou de production.':''],8);
  const limits=uniqText([Number(r.archived||0)?'Le dépôt est archivé : ne pas le choisir pour un nouveau projet sans justification.':'',Number(r.disabled||0)?'Le dépôt est désactivé.':'',!r.license&&!r.license_name?'La licence n’est pas déterminée : vérifier les droits d’utilisation avant intégration.':'',Number(r.activity_days||0)>730?'L’activité récente paraît faible ou ancienne.':'',!commands.length?'Aucune commande exploitable n’a encore été confirmée automatiquement.':'',!(facts.files||[]).length?'Aucun manifeste technique racine n’a encore été analysé.':'','La compréhension L2 est fondée sur des preuves du dépôt ; elle ne remplace pas un audit ligne par ligne du code source.'],10);
  const unknowns=uniqText([role.confidence<0.7?'identité fonctionnelle principale encore à confirmer':'',!commands.length?'commande exacte d’installation ou de lancement':'',!dependencies.length?'dépendances techniques détaillées':'',!interfaces.length?'interface principale réellement exposée':'',!(sig.sections&&sig.sections.architecture)?'architecture interne explicitement documentée':'',!r.latest_release_tag?'cycle de release récent':''],10);
  const evidence=uniqText([r.l1_summary?'Fiche L1 complète':'',r.description?'Description GitHub':'',topics.length?'Topics GitHub':'',langs.length?'Langages détaillés':'',r.latest_release_tag?'Release '+r.latest_release_tag:'',sig.identity_excerpt?'Début du README analysé pour identifier la fonction principale':'',sig.chars?'README analysé ('+sig.chars+' caractères)':'',(inventory.names||[]).length?'Structure racine analysée ('+inventory.names.length+' entrées)':'',(facts.files||[]).length?'Manifestes analysés : '+frJoin(facts.files):''],18);
  const score=Math.max(30,Math.min(100,Math.round(Math.min(20,Number(r.l1_score||0)/5)+role.confidence*20+(sig.chars?15:0)+((inventory.names||[]).length?10:0)+((facts.files||[]).length?10:0)+(commands.length?10:0)+(dependencies.length?7:0)+(interfaces.length?4:0)+(evidence.length>=4?4:0))));
  const l3Ready=score>=82&&role.confidence>=0.75&&Boolean(sig.chars)&&Boolean((inventory.names||[]).length)&&Boolean(commands.length||dependencies.length||(facts.runtime||[]).length);
  const definition='« '+String(r.full_name||'Ce projet')+' » est '+nature+' centré sur '+tech+'. '+role.purpose;
  const how=role.operation+' '+(interfaces.length?'Interfaces observées : '+frJoin(interfaces)+'. ':'')+(architecture.length?'Éléments techniques : '+architecture.slice(0,3).join(' ; ')+'.':'');
  const dossier={schema:4,interpretation_version:2,language:'fr',project:String(r.full_name||''),role_id:role.id,role_fr:role.nature,identity_confidence:Number(role.confidence.toFixed(2)),identity_source:role.identity_source,identity_basis_fr:role.identity_basis_fr,definition_fr:sentence(definition),nature_fr:nature,finalites_fr:purposes,audiences_fr:audiences,interfaces_fr:interfaces,fonctionnement_fr:sentence(how),installation_lancement_fr:setup,commandes:commands,architecture_fr:architecture,dependances:dependencies,integrations_fr:integrations,deploiement_fr:deployment,cas_usage_fr:purposes.slice(0,9),limites_fr:limits,preuves_fr:evidence,a_verifier_fr:unknowns,handoff_l3:{pret:Boolean(l3Ready),score,utilisable_des_l2:score>=55,ce_quon_peut_deja_faire:uniqText([purposes[0]?'Évaluer le projet pour ce besoin : '+purposes[0]:'',commands.length?'Préparer un test local à partir des commandes confirmées.':'',dependencies.length?'Évaluer les dépendances principales avant intégration.':'',interfaces.length?'Choisir une stratégie d’intégration via '+frJoin(interfaces):''],8),blocages:unknowns}};
  const caps=uniqText([role.purpose,...interfaces.map(x=>'Interface : '+x),...architecture.slice(0,5)],12);
  const hiddenParts=[r.description,sig.identity_excerpt,...(Array.isArray(sig.feature_lines)?sig.feature_lines:[]),...(Array.isArray(sig.headings)?sig.headings:[]),...commands,...dependencies];
  return {dossier,human_summary:dossier.definition_fr+' '+dossier.fonctionnement_fr,capabilities:caps,use_cases:purposes,limitations:limits,confidence:Math.min(0.99,Math.max(0.35,score/100)),score,evidence,deep_status:(r.resource_kind==='Projet logiciel'&&Number(r.readme_present||0)===1)?'PENDING':'NOT_APPLICABLE',l3_ready:l3Ready?1:0,retrieval_hidden:uniqText(hiddenParts,80).join(' \n ')};
}
function l2EligibilitySql(alias='r'){
  return alias+".l1_stage='L1_COMPLETE' AND coalesce("+alias+".l1_score,0)>="+L2_MIN_L1_SCORE+" AND coalesce("+alias+".archived,0)=0 AND coalesce("+alias+".disabled,0)=0";
}
function l2Stats(){
  const eligible=Number(db.prepare('SELECT COUNT(*) AS n FROM results r WHERE '+l2EligibilitySql('r')).get().n);
  const total=Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=?').get(L2_RULESET_VERSION).n);
  const base=Number(db.prepare("SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND coalesce(stage,'BASE')='BASE'").get(L2_RULESET_VERSION).n);
  const deep=Number(db.prepare("SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND stage='DEEP'").get(L2_RULESET_VERSION).n);
  const legacyRemaining=Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles l JOIN results r ON r.entity_id=l.entity_id WHERE '+l2EligibilitySql('r')+" AND coalesce(l.source_version,'')<>?").get(L2_RULESET_VERSION).n);
  const neverProfiled=Number(db.prepare('SELECT COUNT(*) AS n FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id WHERE '+l2EligibilitySql('r')+' AND l.entity_id IS NULL').get().n);
  const basePending=legacyRemaining+neverProfiled;
  const deepPending=Number(db.prepare("SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND deep_status IN ('PENDING','RETRY')").get(L2_RULESET_VERSION).n);
  const l3Ready=Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND l3_ready=1').get(L2_RULESET_VERSION).n);
  const fiveAgo=new Date(Date.now()-5*60*1000).toISOString();
  const last5=Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND updated_at>=?').get(L2_RULESET_VERSION,fiveAgo).n);
  const avg=Number(db.prepare('SELECT coalesce(avg(comprehension_score),0) AS n FROM l2_profiles WHERE source_version=?').get(L2_RULESET_VERSION).n||0);
  return {eligible,total,base_done:base,deep_done:deep,base_pending:basePending,legacy_remaining:legacyRemaining,never_profiled:neverProfiled,deep_pending:deepPending,l3_ready:l3Ready,throughput_per_hour:last5*12,comprehension_avg:Number(avg.toFixed(1)),progress_percent:eligible?Number((Math.min(total,eligible)*100/eligible).toFixed(2)):0,version:L2_RULESET_VERSION};
}
function l2QueueRows(limit=60){
  limit=Math.max(1,Math.min(Number(limit||60),200));
  const base=db.prepare("SELECT 'BASE_V4' AS queue,r.entity_id,r.full_name,r.technology,r.resource_kind,r.l1_score,r.stars,r.activity_status,r.fetched_at FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id WHERE "+l2EligibilitySql('r')+" AND (l.entity_id IS NULL OR coalesce(l.source_version,'')<>?) ORDER BY r.l1_score DESC,r.stars DESC,r.fetched_at ASC LIMIT ?").all(L2_RULESET_VERSION,limit);
  if(base.length>=limit)return base;
  const deep=db.prepare("SELECT 'DEEP_V4' AS queue,r.entity_id,r.full_name,r.technology,r.resource_kind,r.l1_score,r.stars,r.activity_status,l.updated_at AS fetched_at FROM l2_profiles l JOIN results r ON r.entity_id=l.entity_id WHERE l.source_version=? AND l.deep_status IN ('PENDING','RETRY') ORDER BY l.comprehension_score DESC,l.updated_at ASC LIMIT ?").all(L2_RULESET_VERSION,limit-base.length);
  return base.concat(deep);
}
function l2BaseStep(limit=3){
  limit=Math.max(1,Math.min(Number(limit||3),6));
  const rows=db.prepare('SELECT r.* FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id WHERE '+l2EligibilitySql('r')+" AND (l.entity_id IS NULL OR coalesce(l.source_version,'')<>?) ORDER BY r.l1_score DESC,r.stars DESC,r.fetched_at ASC LIMIT ?").all(L2_RULESET_VERSION,limit);
  if(!rows.length)return {done:0,state:'EMPTY'};
  const sql="INSERT INTO l2_profiles(entity_id,human_summary,capabilities_json,use_cases_json,limitations_json,confidence,source,updated_at,stage,deep_status,score,evidence_json,readme_signals_json,attempts,last_error,source_version,dossier_json,comprehension_score,l3_ready,language_ui,deep_sources_json,retrieval_text) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(entity_id) DO UPDATE SET human_summary=excluded.human_summary,capabilities_json=excluded.capabilities_json,use_cases_json=excluded.use_cases_json,limitations_json=excluded.limitations_json,confidence=excluded.confidence,source=excluded.source,updated_at=excluded.updated_at,stage=excluded.stage,deep_status=excluded.deep_status,score=excluded.score,evidence_json=excluded.evidence_json,readme_signals_json=excluded.readme_signals_json,attempts=excluded.attempts,last_error=excluded.last_error,source_version=excluded.source_version,dossier_json=excluded.dossier_json,comprehension_score=excluded.comprehension_score,l3_ready=excluded.l3_ready,language_ui=excluded.language_ui,deep_sources_json=excluded.deep_sources_json,retrieval_text=excluded.retrieval_text";
  const stmt=db.prepare(sql);let done=0;
  for(const r of rows){try{const p=l2FrenchDossier(r);stmt.run(r.entity_id,p.human_summary,JSON.stringify(p.capabilities),JSON.stringify(p.use_cases),JSON.stringify(p.limitations),p.confidence,'L1_DOSSIER_FR_V4',now(),'BASE',p.deep_status,p.score,JSON.stringify(p.evidence),'{}',0,null,L2_RULESET_VERSION,JSON.stringify(p.dossier),p.score,p.l3_ready,'fr','[]',p.retrieval_hidden||'');syncSearchEntity(r.entity_id);done++;}catch(e){event('ERROR','L2_BASE_V4_ERROR',String(r.full_name||r.entity_id)+' :: '+String(e.message||e))}}
  if(done)event('INFO','L2_BASE_V4_OK','+'+done+' dossier(s)');return {done,state:done?'OK':'ERROR'};
}
async function l2DeepStep(){
  if(Date.now()<l2DeepNextAttemptAt)return {done:0,state:'WAIT'};if(!githubToken())return {done:0,state:'NO_AUTH'};if(publicRateRemaining!==null&&publicRateRemaining<L2_README_RATE_RESERVE)return {done:0,state:'RESERVE_RATE'};
  const row=db.prepare("SELECT l.entity_id AS l2_entity_id,l.*,r.* FROM l2_profiles l JOIN results r ON r.entity_id=l.entity_id WHERE l.source_version=? AND l.deep_status IN ('PENDING','RETRY') ORDER BY l.comprehension_score DESC,l.updated_at ASC LIMIT 1").get(L2_RULESET_VERSION);
  if(!row)return {done:0,state:'EMPTY'};
  try{
    const enc=String(row.full_name).split('/').map(encodeURIComponent).join('/');
    const rr=await githubGet('/repos/'+enc+'/readme',true);let decoded='';
    if(rr.status!==404&&rr.body&&rr.body.content)decoded=Buffer.from(String(rr.body.content||'').replace(/\s/g,''),String(rr.body.encoding||'base64')).toString('utf8').slice(0,65536);
    const sig=readmeSignals(decoded),inventory=await rootInventory(row.full_name,row.default_branch||'main'),facts=await manifestFacts(row,inventory),p=l2FrenchDossier(row,sig,inventory,facts);
    const deepSources=uniqText([decoded?'README':'',inventory.names.length?'Structure racine':'',...facts.files.map(x=>'Fichier '+x)],12);
    const sql="UPDATE l2_profiles SET human_summary=?,capabilities_json=?,use_cases_json=?,limitations_json=?,confidence=?,source='L2_V4_README_STRUCTURE_MANIFESTS',updated_at=?,stage='DEEP',deep_status='DONE',score=?,evidence_json=?,readme_signals_json=?,attempts=coalesce(attempts,0)+1,last_error=NULL,source_version=?,dossier_json=?,comprehension_score=?,l3_ready=?,language_ui='fr',deep_sources_json=?,retrieval_text=? WHERE entity_id=?";
    db.prepare(sql).run(p.human_summary,JSON.stringify(p.capabilities),JSON.stringify(p.use_cases),JSON.stringify(p.limitations),p.confidence,now(),p.score,JSON.stringify(p.evidence),JSON.stringify(sig),L2_RULESET_VERSION,JSON.stringify(p.dossier),p.score,p.l3_ready,JSON.stringify(deepSources),p.retrieval_hidden||'',row.entity_id);
    syncSearchEntity(row.entity_id);
    event('INFO','L2_DEEP_V4_OK',row.full_name+'; score='+p.score+'; l3='+p.l3_ready+'; role='+String(p.dossier?.role_id||'')+'; sources='+deepSources.length);l2DeepNextAttemptAt=Date.now()+4500;return {done:1,state:'OK'};
  }catch(e){if(e.code==='RATE_LIMIT'){l2DeepNextAttemptAt=Math.max(Date.now()+60000,Number(e.reset||0)*1000+15000);event('WARN','L2_DEEP_V4_RATE_LIMIT','reset='+Number(e.reset||0));return {done:0,state:'RATE_LIMIT'}}db.prepare("UPDATE l2_profiles SET deep_status='RETRY',attempts=coalesce(attempts,0)+1,last_error=?,updated_at=? WHERE entity_id=?").run(String(e.message||e).slice(0,400),now(),row.entity_id);l2DeepNextAttemptAt=Date.now()+15000;event('ERROR','L2_DEEP_V4_ERROR',row.full_name+' :: '+String(e.message||e));return {done:0,state:'ERROR'}}
}
function l3ActionPackFromDossier(entityId,dossier){
  dossier=dossier&&typeof dossier==='object'?dossier:{};const h=dossier.handoff_l3||{};
  const commands=Array.isArray(dossier.commandes)?dossier.commandes:[],deps=Array.isArray(dossier.dependances)?dossier.dependances:[],interfaces=Array.isArray(dossier.interfaces_fr)?dossier.interfaces_fr:[],unknowns=Array.isArray(dossier.a_verifier_fr)?dossier.a_verifier_fr:[],limits=Array.isArray(dossier.limites_fr)?dossier.limites_fr:[],uses=Array.isArray(dossier.cas_usage_fr)?dossier.cas_usage_fr:[],evidence=Array.isArray(dossier.preuves_fr)?dossier.preuves_fr:[],audiences=Array.isArray(dossier.audiences_fr)?dossier.audiences_fr:[];
  const role=String(dossier.role_fr||dossier.nature_fr||'projet logiciel'),definition=String(dossier.definition_fr||''),confidence=Number(dossier.identity_confidence||0);
  const first=uniqText([...(Array.isArray(h.ce_quon_peut_deja_faire)?h.ce_quon_peut_deja_faire:[]),commands[0]?'Exécuter un test contrôlé avec : '+commands[0]:'',deps.length?'Vérifier la compatibilité des dépendances clés : '+deps.slice(0,5).join(', '):''],8);
  const testPlan=uniqText([commands.length?'Lancer le projet avec une commande documentée dans un environnement isolé.':'Préparer un environnement isolé avant toute exécution.',interfaces.length?'Tester l’interface principale : '+interfaces.join(', '):'',uses[0]?'Vérifier le cas d’usage prioritaire : '+uses[0]:'','Mesurer succès, erreurs, latence et consommation de ressources.','Comparer le résultat avec au moins une alternative retenue par la recherche TLIB.'],8);
  const integration=uniqText([interfaces.length?'Point d’intégration probable : '+interfaces.join(', '):'',deps.length?'Dépendances à provisionner : '+deps.slice(0,8).join(', '):'','Conserver un mécanisme de rollback avant intégration durable.'],8);
  const risks=uniqText([...limits,...unknowns.map(x=>'À confirmer : '+x)],12);
  const bestFor=uniqText([uses[0]||'',uses[1]||'',audiences[0]?'Public pertinent : '+audiences[0]:''],6);
  const strengths=uniqText([definition,confidence>=0.9?'Identité fonctionnelle fortement confirmée par les preuves du dépôt.':'',commands.length?'Commandes de test ou de lancement disponibles.':'',deps.length?'Dépendances techniques identifiées.':'',interfaces.length?'Interfaces identifiées : '+interfaces.join(', '):'',evidence.length?'Preuves disponibles : '+evidence.slice(-4).join(' ; '):''],8);
  const selectionChecks=uniqText([unknowns.length?'Lever les inconnues critiques : '+unknowns.slice(0,5).join(', '):'',limits.length?'Vérifier les limites : '+limits.slice(0,4).join(' ; '):'',commands.length?'Confirmer que les commandes sont compatibles avec l’environnement cible.':'Confirmer une procédure de lancement reproductible.',deps.length?'Confirmer que les dépendances sont acceptables pour le projet cible.':''],8);
  const readiness=commands.length&&confidence>=0.8?(unknowns.length<=1?'TESTABLE':'TESTABLE_AVEC_VERIFICATIONS'):'REVUE_REQUISE';
  const researchTerms=uniqText([role,dossier.role_id||'',...uses,...interfaces,...audiences,...deps.slice(0,8)],24);
  return {
    schema:2,entity_id:entityId,
    objective:'Passer de la compréhension L2 à la sélection, au test puis à une intégration contrôlée.',
    relevance_summary:definition,
    best_for:bestFor,
    strengths,
    selection_checks:selectionChecks,
    readiness,
    research_terms:researchTerms,
    first_actions:first,
    test_plan:testPlan,
    integration_plan:integration,
    risks,
    blockers:unknowns,
    source_score:Number(h.score||0),
    source_identity_confidence:confidence,
    source_ready:Boolean(h.pret)
  };
}
function l3Step(limit=2){
  limit=Math.max(1,Math.min(Number(limit||2),5));
  const rows=db.prepare("SELECT l.entity_id,l.dossier_json FROM l2_profiles l LEFT JOIN l3_actions a ON a.entity_id=l.entity_id WHERE l.source_version=? AND l.l3_ready=1 AND (a.entity_id IS NULL OR a.source_l2_version<>?) ORDER BY l.comprehension_score DESC,l.updated_at ASC LIMIT ?").all(L2_RULESET_VERSION,L2_RULESET_VERSION,limit);
  if(!rows.length)return {done:0,state:'EMPTY'};const stmt=db.prepare("INSERT INTO l3_actions(entity_id,action_json,source_l2_version,updated_at) VALUES(?,?,?,?) ON CONFLICT(entity_id) DO UPDATE SET action_json=excluded.action_json,source_l2_version=excluded.source_l2_version,updated_at=excluded.updated_at");let done=0;
  for(const r of rows){try{const d=jsonObject(r.dossier_json),pack=l3ActionPackFromDossier(r.entity_id,d);stmt.run(r.entity_id,JSON.stringify(pack),L2_RULESET_VERSION,now());syncSearchEntity(r.entity_id);done++}catch(e){event('ERROR','L3_ACTION_ERROR',r.entity_id+' :: '+String(e.message||e))}}
  if(done)event('INFO','L3_ACTION_OK','+'+done+' pack(s)');return {done,state:done?'OK':'ERROR'};
}
function l3Stats(){
  const ready=Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles WHERE source_version=? AND l3_ready=1').get(L2_RULESET_VERSION).n);
  const total=Number(db.prepare('SELECT COUNT(*) AS n FROM l3_actions WHERE source_l2_version=?').get(L2_RULESET_VERSION).n);
  return {ready,total,pending:Math.max(0,ready-total),progress_percent:ready?Number((total*100/ready).toFixed(1)):0};
}
function l3Rows(limit=100){
  limit=Math.max(1,Math.min(Number(limit||100),200));return db.prepare("SELECT a.entity_id,a.action_json,a.updated_at,r.full_name,r.resource_kind,r.technology,l.comprehension_score FROM l3_actions a JOIN results r ON r.entity_id=a.entity_id JOIN l2_profiles l ON l.entity_id=a.entity_id WHERE a.source_l2_version=? ORDER BY l.comprehension_score DESC,a.updated_at DESC LIMIT ?").all(L2_RULESET_VERSION,limit).map(x=>({...x,action:jsonObject(x.action_json)}));
}
async function scheduledL1Step(){
  const mode=l1SchedulerMode();l1Cycle++;
  if(mode==='DEEP_CATCHUP'){
    if(l1Cycle%4!==0){const deep=await deepL1Step();if(deep.done||!['EMPTY','NO_AUTH','RESERVE_RATE'].includes(deep.state))return deep;}
    return await autopilotPublicStep();
  }
  if(mode==='BALANCED_DEEP_FIRST'){
    if(l1Cycle%3===0){const deep=await deepL1Step();if(deep.done||!['EMPTY','NO_AUTH','RESERVE_RATE'].includes(deep.state))return deep;}
    return await autopilotPublicStep();
  }
  const core=await autopilotPublicStep();if(core.done&&l1Cycle%20===0)await deepL1Step();return core;
}
async function scheduledPipelineStep(){
  pipelineCycle++;const l2=l2Stats(),l3=l3Stats();
  if(l3.pending>0&&pipelineCycle%20===9){const a=l3Step(2);if(a.done)return a;}
  if(l2.deep_pending>0&&pipelineCycle%12===6){const d=await l2DeepStep();if(d.done||!['EMPTY','NO_AUTH','RESERVE_RATE','WAIT'].includes(d.state))return d;}
  if(l2.base_pending>0&&pipelineCycle%4===0)return l2BaseStep(4);
  return await scheduledL1Step();
}

function loadControlSnapshot() {
  try { return JSON.parse(readFileSync(join(ROOT, 'config', 'control-snapshot.json'), 'utf8')); }
  catch { return { engine:{}, product:{} }; }
}

function libraryRows(q='', limit=100, offset=0, sort='stars') {
  q=String(q||'').trim();
  limit=Math.max(1,Math.min(Number(limit||100),500));
  offset=Math.max(0,Number(offset||0));
  const orders={stars:'r.stars DESC',recent:'r.pushed_at DESC',verified:'r.fetched_at DESC',complete:'r.l1_score DESC',name:'r.full_name ASC'};
  const order=orders[String(sort||'stars')]||orders.stars;
  if(!q){
    return db.prepare(`SELECT r.entity_id,r.full_name,r.description,r.stars,r.language,r.license,r.topics_json,r.archived,r.fork,
      r.updated_at_github,r.pushed_at,r.default_branch,r.size_kb,r.open_issues,r.fetched_at,
      r.resource_kind,r.technology,r.content_mode,r.activity_status,r.activity_days,r.l1_quality,r.l1_score,
      r.primary_theme,r.theme_path,r.theme_tags_json,r.theme_confidence,
      l.human_summary,l.stage AS l2_stage,l.comprehension_score AS l2_score,l.l3_ready
      FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version=?
      ORDER BY ${order} LIMIT ? OFFSET ?`).all(L2_RULESET_VERSION,limit,offset);
  }
  ensureSearchIndex();
  const ranked=searchRanked(q).items;
  let rows=ranked;
  if(sort==='recent')rows=[...ranked].sort((a,b)=>b.search_score-a.search_score||String(b.pushed_at||'').localeCompare(String(a.pushed_at||'')));
  else if(sort==='name')rows=[...ranked].sort((a,b)=>b.search_score-a.search_score||String(a.full_name).localeCompare(String(b.full_name)));
  else if(sort==='stars')rows=[...ranked].sort((a,b)=>b.search_score-a.search_score||Number(b.stars||0)-Number(a.stars||0));
  return rows.slice(offset,offset+limit).map(({_title,_l1,_l2,_l3,_hidden,_bm25,...x})=>x);
}

function libraryCount(q='') {
  q=String(q||'').trim();
  if(!q)return Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n);
  ensureSearchIndex();
  return searchRanked(q).total;
}
function l2Rows(limit=100) {
  limit=Math.max(1,Math.min(Number(limit||100),500));
  return db.prepare(`SELECT r.entity_id,r.full_name,r.resource_kind,r.technology,r.activity_status,r.stars,
                            l.human_summary,l.capabilities_json,l.use_cases_json,l.limitations_json,l.confidence,l.updated_at,
                            l.stage,l.deep_status,l.comprehension_score,l.l3_ready,l.language_ui,l.source_version
                     FROM l2_profiles l JOIN results r ON r.entity_id=l.entity_id
                     WHERE l.source_version=?
                     ORDER BY l.comprehension_score DESC,l.updated_at DESC LIMIT ?`).all(L2_RULESET_VERSION,limit).map(x=>{
    const parse=v=>{try{return JSON.parse(v||'[]')}catch{return[]}};
    return {...x,capabilities:parse(x.capabilities_json),use_cases:parse(x.use_cases_json),limitations:parse(x.limitations_json)};
  });
}

function l1Stats() {
  const control=loadControlSnapshot();
  const target=Number(control.engine?.entity_count||120694);
  const core=Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n);
  const complete=Number(db.prepare(`SELECT COUNT(*) AS n FROM results WHERE l1_stage='L1_COMPLETE'`).get().n);
  const deepDone=Number(db.prepare(`SELECT COUNT(*) AS n FROM results WHERE deep_status='DONE'`).get().n);
  const deepPending=Number(db.prepare(`SELECT COUNT(*) AS n FROM results WHERE deep_status IN ('PENDING','RETRY')`).get().n);
  const fiveAgo=new Date(Date.now()-5*60*1000).toISOString();
  const last5=Number(db.prepare('SELECT COUNT(*) AS n FROM results WHERE fetched_at>=?').get(fiveAgo).n);
  const perHour=last5*12;
  const errors24=Number(db.prepare(`SELECT COUNT(*) AS n FROM events WHERE level='ERROR' AND at>=?`).get(new Date(Date.now()-86400000).toISOString()).n);
  return {target,core,complete,deep_done:deepDone,deep_pending:deepPending,pending:Math.max(0,target-core),
    core_percent:target?Number((core*100/target).toFixed(3)):0,complete_percent:target?Number((complete*100/target).toFixed(3)):0,
    throughput_per_hour:perHour,errors_24h:errors24};
}

function loadL0Sources() {
  try {
    const rows=JSON.parse(readFileSync(join(dataDir,'l0-sources.json'),'utf8'));
    return Array.isArray(rows)?rows:[];
  } catch { return []; }
}
function l0SourcesSnapshot(params={}) {
  const all=loadL0Sources();
  const q=String(params.q||'').trim().toLowerCase();
  const status=String(params.status||'').trim().toUpperCase();
  const depth=String(params.depth??'').trim();
  const limit=Math.max(1,Math.min(Number(params.limit||100),500));
  const offset=Math.max(0,Number(params.offset||0));
  const filtered=all.filter(r=>{
    if(status && String(r.status||'').toUpperCase()!==status) return false;
    if(depth!=='' && String(r.depth??'')!==depth) return false;
    if(q){
      const bag=[r.source_id,r.owner,r.repo,r.raw_url,r.discovered_from,r.status,r.depth].join(' ').toLowerCase();
      if(!bag.includes(q)) return false;
    }
    return true;
  });
  const byStatus={},byDepth={};
  for(const r of all){
    const s=String(r.status||'UNKNOWN'),d=String(r.depth??'—');
    byStatus[s]=(byStatus[s]||0)+1;
    byDepth[d]=(byDepth[d]||0)+1;
  }
  return {total:all.length,filtered_total:filtered.length,offset,limit,items:filtered.slice(offset,offset+limit),by_status:byStatus,by_depth:byDepth};
}
function l1InsightsSnapshot() {
  const group=(col,limit=30)=>db.prepare(`SELECT coalesce(${col},'—') AS value, COUNT(*) AS n
    FROM results GROUP BY ${col} ORDER BY n DESC, value ASC LIMIT ?`).all(limit);
  const scoreBuckets=db.prepare(`SELECT
    SUM(CASE WHEN coalesce(l1_score,0)>=90 THEN 1 ELSE 0 END) AS s90,
    SUM(CASE WHEN coalesce(l1_score,0)>=75 AND coalesce(l1_score,0)<90 THEN 1 ELSE 0 END) AS s75,
    SUM(CASE WHEN coalesce(l1_score,0)>=50 AND coalesce(l1_score,0)<75 THEN 1 ELSE 0 END) AS s50,
    SUM(CASE WHEN coalesce(l1_score,0)<50 THEN 1 ELSE 0 END) AS slow
    FROM results`).get();
  return {
    total:Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n),
    by_type:group('resource_kind',20), by_theme:group('primary_theme',30), by_path:group('theme_path',40),
    by_technology:group('technology',40), by_language:group('language',30), by_license:group('license',30),
    by_activity:group('activity_status',20), by_stage:group('l1_stage',20), by_deep:group('deep_status',20),
    score_buckets:{'90-100':Number(scoreBuckets.s90||0),'75-89':Number(scoreBuckets.s75||0),'50-74':Number(scoreBuckets.s50||0),'<50':Number(scoreBuckets.slow||0)}
  };
}

function facetsSnapshot() {
  const technologies=db.prepare(`SELECT technology AS value, COUNT(*) AS n FROM results
                                 WHERE coalesce(technology,'')<>'' GROUP BY technology
                                 ORDER BY n DESC, value ASC LIMIT 30`).all();
  const types=db.prepare(`SELECT resource_kind AS value, COUNT(*) AS n FROM results
                          WHERE coalesce(resource_kind,'')<>'' GROUP BY resource_kind
                          ORDER BY n DESC, value ASC`).all();
  const activities=db.prepare(`SELECT activity_status AS value, COUNT(*) AS n FROM results
                               WHERE coalesce(activity_status,'')<>'' GROUP BY activity_status
                               ORDER BY n DESC, value ASC`).all();
  const themes=db.prepare(`SELECT primary_theme AS value, COUNT(*) AS n FROM results
                           WHERE coalesce(primary_theme,'')<>'' GROUP BY primary_theme
                           ORDER BY n DESC, value ASC`).all();
  const paths=db.prepare(`SELECT theme_path AS value, COUNT(*) AS n FROM results
                          WHERE coalesce(theme_path,'')<>'' GROUP BY theme_path
                          ORDER BY n DESC, value ASC LIMIT 40`).all();
  return {technologies,types,activities,themes,paths,taxonomy_version:TAXONOMY_VERSION};
}

function drillLike(q){return '%'+String(q||'').trim().toLowerCase()+'%'}
function l1Drilldown(kind='verified',q='',limit=50,offset=0,sort='score',band=''){
  kind=String(kind||'verified');q=String(q||'').trim().toLowerCase();
  limit=Math.max(1,Math.min(Number(limit||50),100));offset=Math.max(0,Number(offset||0));
  const allowed=new Set(['verified','complete','deep_done','deep_pending','l2_eligible']);if(!allowed.has(kind))kind='verified';
  const whereMap={
    verified:'1=1',
    complete:"r.l1_stage='L1_COMPLETE'",
    deep_done:"r.deep_status='DONE'",
    deep_pending:"r.resource_kind='Projet logiciel' AND coalesce(r.deep_status,'PENDING') IN ('PENDING','RETRY')",
    l2_eligible:l2EligibilitySql('r')
  };
  let where=whereMap[kind],params=[];
  band=String(band||'');const bandMap={'90-100':'coalesce(r.l1_score,0)>=90','75-89':'coalesce(r.l1_score,0)>=75 AND coalesce(r.l1_score,0)<90','50-74':'coalesce(r.l1_score,0)>=50 AND coalesce(r.l1_score,0)<75','<50':'coalesce(r.l1_score,0)<50'};
  if(bandMap[band])where+=' AND '+bandMap[band];
  if(q){where+=' AND (lower(r.full_name) LIKE ? OR lower(coalesce(r.description,\'\')) LIKE ? OR lower(coalesce(r.technology,\'\')) LIKE ? OR lower(coalesce(r.resource_kind,\'\')) LIKE ? OR lower(coalesce(r.theme_path,\'\')) LIKE ?)';const like=drillLike(q);params.push(like,like,like,like,like);}
  const orderMap={score:'r.l1_score DESC,r.stars DESC',recent:'r.fetched_at DESC',stars:'r.stars DESC,r.l1_score DESC',name:'r.full_name ASC'};
  const order=orderMap[String(sort||'score')]||orderMap.score;
  const total=Number(db.prepare('SELECT COUNT(*) AS n FROM results r WHERE '+where).get(...params).n);
  const items=db.prepare(`SELECT r.entity_id,r.full_name,r.description,r.resource_kind,r.technology,r.activity_status,r.l1_score,r.l1_stage,r.deep_status,r.stars,r.fetched_at,r.primary_theme,r.theme_path,
    EXISTS(SELECT 1 FROM l2_profiles l WHERE l.entity_id=r.entity_id) AS has_l2
    FROM results r WHERE ${where} ORDER BY ${order} LIMIT ? OFFSET ?`).all(...params,limit,offset);
  return {kind,q,sort,band,total,limit,offset,items};
}
function l2Drilldown(kind='profiles',q='',limit=50,offset=0,sort='score'){
  kind=String(kind||'profiles');q=String(q||'').trim().toLowerCase();limit=Math.max(1,Math.min(Number(limit||50),100));offset=Math.max(0,Number(offset||0));
  const allowed=new Set(['profiles','eligible','base_pending','base_done','deep_pending','deep_done','l3_ready']);if(!allowed.has(kind))kind='profiles';
  const maps={
    profiles:{from:'l2_profiles l JOIN results r ON r.entity_id=l.entity_id',where:'l.source_version=?',pre:[L2_RULESET_VERSION]},
    eligible:{from:"results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version='"+L2_RULESET_VERSION+"'",where:l2EligibilitySql('r'),pre:[]},
    base_pending:{from:"results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version='"+L2_RULESET_VERSION+"'",where:l2EligibilitySql('r')+' AND l.entity_id IS NULL',pre:[]},
    base_done:{from:'l2_profiles l JOIN results r ON r.entity_id=l.entity_id',where:"l.source_version=? AND coalesce(l.stage,'BASE')='BASE'",pre:[L2_RULESET_VERSION]},
    deep_pending:{from:'l2_profiles l JOIN results r ON r.entity_id=l.entity_id',where:"l.source_version=? AND l.deep_status IN ('PENDING','RETRY')",pre:[L2_RULESET_VERSION]},
    deep_done:{from:'l2_profiles l JOIN results r ON r.entity_id=l.entity_id',where:"l.source_version=? AND l.stage='DEEP'",pre:[L2_RULESET_VERSION]},
    l3_ready:{from:'l2_profiles l JOIN results r ON r.entity_id=l.entity_id',where:'l.source_version=? AND l.l3_ready=1',pre:[L2_RULESET_VERSION]}
  };
  const cfg=maps[kind];let where=cfg.where,params=[...(cfg.pre||[])];
  if(q){where+=" AND (lower(r.full_name) LIKE ? OR lower(coalesce(r.description,'')) LIKE ? OR lower(coalesce(r.technology,'')) LIKE ? OR lower(coalesce(r.resource_kind,'')) LIKE ? OR lower(coalesce(l.human_summary,'')) LIKE ?)";const like=drillLike(q);params.push(like,like,like,like,like)}
  const orderMap={score:'coalesce(l.comprehension_score,l.score,r.l1_score,0) DESC,r.stars DESC',recent:'coalesce(l.updated_at,r.fetched_at) DESC',stars:'r.stars DESC',name:'r.full_name ASC'};const order=orderMap[String(sort||'score')]||orderMap.score;
  const total=Number(db.prepare('SELECT COUNT(*) AS n FROM '+cfg.from+' WHERE '+where).get(...params).n);
  const items=db.prepare('SELECT r.entity_id,r.full_name,r.description,r.resource_kind,r.technology,r.activity_status,r.l1_score,r.stars,l.stage AS l2_stage,l.deep_status AS l2_deep_status,l.comprehension_score AS l2_score,l.confidence,l.updated_at AS l2_updated_at,l.human_summary,l.l3_ready,l.language_ui FROM '+cfg.from+' WHERE '+where+' ORDER BY '+order+' LIMIT ? OFFSET ?').all(...params,limit,offset);
  return {kind,q,sort,total,limit,offset,items,version:L2_RULESET_VERSION};
}
function chatSearch(q,limit=8){
  q=String(q||'').trim();limit=Math.max(1,Math.min(Number(limit||8),12));
  if(!q)return {q,items:[],total:0,concepts:[],search_mode:'EMPTY',engine:'FTS5_CONCEPT_RERANK'};
  ensureSearchIndex();
  const ranked=searchRanked(q);
  const items=ranked.items.slice(0,limit).map(({_title,_l1,_l2,_l3,_hidden,_bm25,...x})=>x);
  return {q,total:ranked.total,items,concepts:ranked.groups,mode:ranked.mode,search_mode:ranked.mode,engine:'FTS5_CONCEPT_RERANK_L1_L2_L3'};
}
async function searchAuditSnapshot(){
  ensureSearchIndex(true);
  const queries=['android remote control','secure remote access','local ai','coding agent orchestrator','api client','docker backup','typescript automation','database gui','offline first','websocket remote','self hosted monitoring','telegram automation'];
  const results={};
  for(const q of queries){
    const r=searchRanked(q);
    results[q]={mode:r.mode,total:r.total,top:r.items.slice(0,8).map(x=>({full_name:x.full_name,coverage:x.search_coverage,score:x.search_score,l1:x.l1_score,l2:x.l2_score,stage:x.l2_stage,l3_ready:Boolean(x.l3_ready),theme:x.theme_path,summary:String(x.human_summary||x.description||'').slice(0,220)}))};
  }
  const semanticNames=['stablyai/orca','mudler/LocalAI','firezone/firezone','rustdesk/rustdesk','getinsomnia/insomnia','offen/docker-volume-backup','mobile-next/mobile-mcp'];
  const samples=[];
  for(const name of semanticNames){
    const r=db.prepare('SELECT * FROM results WHERE lower(full_name)=lower(?)').get(name);
    if(!r){samples.push({full_name:name,missing:true});continue}
    const stored=db.prepare('SELECT stage,comprehension_score,dossier_json FROM l2_profiles WHERE entity_id=? AND source_version=?').get(r.entity_id,L2_RULESET_VERSION)||null;
    const d=stored?jsonObject(stored.dossier_json):{};
    let probe=null;
    try{
      const enc=String(r.full_name).split('/').map(encodeURIComponent).join('/');
      const rr=await githubGet('/repos/'+enc+'/readme',true);
      let decoded='';if(rr.status!==404&&rr.body&&rr.body.content)decoded=Buffer.from(String(rr.body.content||'').replace(/\s/g,''),String(rr.body.encoding||'base64')).toString('utf8').slice(0,65536);
      const sig=readmeSignals(decoded),p=l2FrenchDossier(r,sig,{names:[],files:[],dirs:[]},{files:[],commands:[],dependencies:[],scripts:[],services:[],runtime:[],config_files:[]});
      probe={role:p.dossier.role_id,role_fr:p.dossier.role_fr,definition:p.dossier.definition_fr,identity_confidence:p.dossier.identity_confidence,finalites:p.dossier.finalites_fr.slice(0,4),readme_chars:sig.chars};
    }catch(e){probe={error:String(e.message||e)}}
    samples.push({full_name:r.full_name,theme:r.theme_path,l1_score:r.l1_score,l2_stage:stored?.stage||null,l2_score:stored?.comprehension_score||null,stored_role:d.role_id||null,stored_definition:d.definition_fr||null,live_readme_probe:probe});
  }
  return {build:APP_BUILD,l2_version:L2_RULESET_VERSION,taxonomy:TAXONOMY_VERSION,search_index:SEARCH_INDEX_VERSION,indexed:Number(db.prepare('SELECT COUNT(*) AS n FROM search_fts').get().n||0),results,samples};
}
function resourceById(id) {
  const r = db.prepare(`SELECT * FROM results WHERE entity_id=? OR lower(full_name)=lower(?)`).get(String(id||''), String(id||''));
  if (!r) return null;
  let topics=[]; try { topics=JSON.parse(r.topics_json||'[]'); } catch {}
  const l2raw = db.prepare('SELECT * FROM l2_profiles WHERE entity_id=? AND source_version=?').get(r.entity_id,L2_RULESET_VERSION) || null;
  let l2 = null;
  if (l2raw) {
    const parse = (v) => { try { return JSON.parse(v || '[]'); } catch { return []; } };
    l2 = {...l2raw, capabilities:parse(l2raw.capabilities_json), use_cases:parse(l2raw.use_cases_json), limitations:parse(l2raw.limitations_json), evidence:parse(l2raw.evidence_json), readme_signals:parse(l2raw.readme_signals_json), dossier:parse(l2raw.dossier_json), deep_sources:parse(l2raw.deep_sources_json)};
  }
  const l3raw=db.prepare('SELECT action_json,updated_at,source_l2_version FROM l3_actions WHERE entity_id=?').get(r.entity_id)||null;
  const l3=l3raw?{...l3raw,action:jsonObject(l3raw.action_json)}:null;
  return {...r, topics, l2, l3};
}


const PHONE_STATE_FILE=join(dataDir,'phone-share.json');
const PHONE_COOKIE='tlib_m';
const phoneClaimAttempts=new Map();

function privateLanIpv4(){
  try{
    const found=[];
    for(const [name,rows] of Object.entries(networkInterfaces())){
      for(const x of rows||[]){
        if(!x||x.family!=='IPv4'||x.internal) continue;
        const a=String(x.address||'');
        const priv=/^10\./.test(a)||/^192\.168\./.test(a)||/^172\.(1[6-9]|2\d|3[01])\./.test(a);
        if(priv) found.push({name,address:a,score:/wi-?fi|wireless|wlan/i.test(name)?3:/ethernet/i.test(name)?2:1});
      }
    }
    found.sort((a,b)=>b.score-a.score||a.address.localeCompare(b.address));
    return found[0]?.address||null;
  }catch{return null}
}
function tokenHash(v){return createHash('sha256').update(String(v||''),'utf8').digest('hex')}
function phoneCodeFromBytes(buf){
  const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let n=BigInt('0x'+buf.toString('hex')),out='';
  for(let i=0;i<10;i++){out=alphabet[Number(n%BigInt(alphabet.length))]+out;n/=BigInt(alphabet.length)}
  return out;
}
function cleanPhoneState(state){
  const nowMs=Date.now(),s=state&&typeof state==='object'?state:{};
  const sessions=Array.isArray(s.sessions)?s.sessions.filter(x=>Number(x.expires_at||0)>nowMs).map((x,i)=>({...x,id:String(x.id||('legacy-'+i)),duration_minutes:Number(x.duration_minutes||Math.max(1,Math.round((Number(x.expires_at||0)-Number(x.created_at||nowMs))/60000))) })):[];
  const p=s.pair_offer&&typeof s.pair_offer==='object'?s.pair_offer:null;
  const pair_offer=p&&!p.used&&Number(p.offer_expires_at||0)>nowMs?p:null;
  return {schema:2,sessions,pair_offer};
}
function loadPhoneState(){
  try{return cleanPhoneState(JSON.parse(readFileSync(PHONE_STATE_FILE,'utf8')))}
  catch{return {schema:2,sessions:[],pair_offer:null}}
}
function savePhoneState(state){try{writeFileSync(PHONE_STATE_FILE,JSON.stringify(cleanPhoneState(state),null,2),'utf8')}catch{}}
function phoneState(){const st=loadPhoneState();savePhoneState(st);return st}
function normalizePhoneMinutes(v){const n=Number(v||30);return [30,180,360].includes(n)?n:30}
function createPhonePair(minutes=30){
  const lanIp=privateLanIpv4();if(!lanIp)return {ok:false,error:'NO_PRIVATE_LAN_IP'};
  minutes=normalizePhoneMinutes(minutes);const secret=randomBytes(24).toString('base64url'),code=phoneCodeFromBytes(randomBytes(7)),nowMs=Date.now(),state=phoneState();
  state.pair_offer={secret,code,minutes,created_at:nowMs,offer_expires_at:nowMs+5*60*1000,lan_ip:lanIp,used:false};savePhoneState(state);
  event('INFO','PHONE_PAIR_CREATED','duration='+minutes+'m; ip='+lanIp);return phoneStatus();
}
function activePhoneOffer(){return phoneState().pair_offer||null}
function phoneStatus(){
  const state=phoneState(),offer=state.pair_offer,lanIp=privateLanIpv4(),port=Number(process.env.TLIB_DASHBOARD_PORT||8787),base=lanIp?'http://'+lanIp+':'+port:null,nowMs=Date.now();
  return {ok:true,enabled:Boolean(offer||state.sessions.length),lan_ip:lanIp,port,base_url:base,access_qr_url:state.sessions.length&&base?base:null,
    pair:offer?{code:offer.code,minutes:offer.minutes,offer_expires_at:new Date(offer.offer_expires_at).toISOString(),session_expires_at:new Date(offer.created_at+offer.minutes*60*1000).toISOString(),qr_url:'http://'+offer.lan_ip+':'+port+'/pair#t='+encodeURIComponent(offer.secret)}:null,
    sessions:state.sessions.map(x=>({id:String(x.id),duration_minutes:Number(x.duration_minutes||0),created_at:new Date(x.created_at).toISOString(),expires_at:new Date(x.expires_at).toISOString(),remaining_seconds:Math.max(0,Math.floor((Number(x.expires_at)-nowMs)/1000)),last_seen:x.last_seen?new Date(x.last_seen).toISOString():null,state:Number(x.expires_at)>nowMs?'ACTIVE':'EXPIRED'})),
    session_count:state.sessions.length,read_only:true};
}
function revokePhoneSession(id){
  const state=phoneState(),before=state.sessions.length;state.sessions=state.sessions.filter(x=>String(x.id)!==String(id||''));savePhoneState(state);
  event('INFO','PHONE_SESSION_REVOKED','id='+String(id||'')+'; removed='+(before-state.sessions.length));return phoneStatus();
}
function parseCookies(req){
  const out={};
  for(const p of String(req.headers.cookie||'').split(';')){
    const i=p.indexOf('=');if(i<1)continue;
    const k=p.slice(0,i).trim(),v=p.slice(i+1).trim();
    try{out[k]=decodeURIComponent(v)}catch{out[k]=v}
  }
  return out;
}
function safeEqualText(a,b){
  const aa=Buffer.from(String(a||'')),bb=Buffer.from(String(b||''));
  return aa.length===bb.length&&timingSafeEqual(aa,bb);
}
function isLoopbackRequest(req){
  const a=String(req.socket?.remoteAddress||'').replace(/^::ffff:/,'');
  return a==='127.0.0.1'||a==='::1'||a==='localhost';
}
function remoteAddress(req){return String(req.socket?.remoteAddress||'').replace(/^::ffff:/,'')}
function validPhoneSession(req){
  const raw=parseCookies(req)[PHONE_COOKIE];
  if(!raw) return null;
  const hash=tokenHash(raw),state=phoneState(),nowMs=Date.now();
  const found=state.sessions.find(x=>x.hash===hash&&Number(x.expires_at)>nowMs);
  if(!found)return null;
  if(!found.last_seen||nowMs-Number(found.last_seen)>60000){
    found.last_seen=nowMs; savePhoneState(state);
  }
  return found;
}
function phoneClaimAllowed(req){
  const ip=remoteAddress(req),nowMs=Date.now();
  let x=phoneClaimAttempts.get(ip);
  if(!x||nowMs-x.start>60000)x={start:nowMs,count:0};
  x.count++;phoneClaimAttempts.set(ip,x);
  return x.count<=10;
}
function readJsonBody(req,max=4096){
  return new Promise((resolve,reject)=>{
    let size=0,parts=[];
    req.on('data',d=>{size+=d.length;if(size>max){reject(new Error('BODY_TOO_LARGE'));req.destroy();return}parts.push(d)});
    req.on('end',()=>{try{resolve(parts.length?JSON.parse(Buffer.concat(parts).toString('utf8')):{})}catch(e){reject(new Error('INVALID_JSON'))}});
    req.on('error',reject);
  });
}
function pairPage(){
  return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
    '<meta name="referrer" content="no-referrer"><title>TLIB · Connexion téléphone</title><style>'+
    'body{font-family:Segoe UI,Arial,sans-serif;background:#0c111b;color:#edf2ff;margin:0;min-height:100vh;display:grid;place-items:center;padding:20px}'+
    '.box{width:min(420px,100%);background:#131b2a;border:1px solid #2a3850;border-radius:20px;padding:22px;box-shadow:0 18px 60px #0007}'+
    'h1{font-size:22px;margin:0 0 8px}p{color:#9fb0ca;line-height:1.45}input,button{box-sizing:border-box;width:100%;padding:13px 14px;border-radius:11px;border:1px solid #354661;background:#0b1220;color:#fff;font-size:16px}'+
    'button{margin-top:10px;background:#4777ff;border:0;font-weight:700}#state{margin-top:14px;font-size:14px;color:#9fb0ca}.ok{color:#67d391}.bad{color:#ff7f8c}</style></head><body><div class="box">'+
    '<h1>📱 TLIB sur téléphone</h1><p>Scanne le QR depuis le PC, ou saisis le code temporaire affiché dans Manager.</p>'+
    '<form id="f"><input id="code" autocomplete="one-time-code" placeholder="Code TLIB"><button>Se connecter</button></form><div id="state">Connexion locale sécurisée par session temporaire.</div>'+
    '<script>(function(){var st=document.getElementById("state"),f=document.getElementById("f"),inp=document.getElementById("code");'+
    'async function claim(v,k){st.textContent="Vérification…";try{var r=await fetch("/api/mobile/claim",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(k==="token"?{token:v}:{code:v})});var j=await r.json();if(!r.ok)throw new Error(j.error||"PAIR_FAILED");history.replaceState(null,"","/pair");st.className="ok";st.textContent="Connecté. Ouverture de TLIB…";setTimeout(function(){location.replace("/")},250)}catch(e){st.className="bad";st.textContent="Connexion refusée : "+e.message}}'+
    'var h=location.hash||"";if(h.indexOf("#t=")===0){var t=decodeURIComponent(h.slice(3));location.hash="";claim(t,"token")}'+
    'f.onsubmit=function(e){e.preventDefault();var c=inp.value.trim().toUpperCase();if(c)claim(c,"code")}})();</script></div></body></html>';
}
function revokePhoneSessions(){savePhoneState({schema:2,sessions:[],pair_offer:null});event('INFO','PHONE_SESSIONS_REVOKED','all');return phoneStatus();}

function readJsonSafe(path, fallback=null) {
  try { return JSON.parse(readFileSync(path,'utf8')); } catch { return fallback; }
}
const AUTO_UPDATE_INTERVAL_MS=10*60*1000;
const AUTO_UPDATE_FIRST_DELAY_MS=45*1000;
const AUTO_UPDATE_IDLE_GUARD_MS=120*1000;
const LAST_GOOD_SOAK_MS=15*60*1000;
let autoUpdateRunning=false;
let autoUpdateTimer=null;
let autoUpdateNextAt=0;
let autoUpdateLastAt=0;
let autoUpdateLastResult='NOT_RUN';

function updateStatusSnapshot() {
  const pending=readJsonSafe(join(dataDir,'pending-deployment.json'),null);
  const lastGood=readJsonSafe(join(dataDir,'last-good-deployment.json'),null);
  const current=readJsonSafe(join(dataDir,'current-deployment.json'),null);
  const runtime=readJsonSafe(join(dataDir,'runtime.json'),null);
  const progress=readJsonSafe(join(dataDir,'slot-update-progress.json'),null);
  let audit=[];
  try{
    const lines=readFileSync(join(dataDir,'slot-update-audit.jsonl'),'utf8').split(/\r?\n/).filter(Boolean).slice(-25);
    audit=lines.map(x=>{try{return JSON.parse(x)}catch{return {at:'',event:'UNPARSEABLE',status:'WARN',detail:x.slice(0,300)}}});
  }catch{}
  return {
    scheme:'SLOT_V1',
    active:{build:APP_BUILD,commit:APP_COMMIT,pid:process.pid,started_at:STARTED_AT},
    current,
    runtime,
    pending,
    last_good:lastGood,
    pending_available:!!(pending&&pending.verified),
    progress,
    automatic_update:{
      enabled:true,
      channel:'release/tlib-hybrid-v2-stable',
      interval_minutes:10,
      first_check_seconds:45,
      idle_guard_seconds:120,
      running:autoUpdateRunning,
      last_check_at:autoUpdateLastAt?new Date(autoUpdateLastAt).toISOString():null,
      next_check_at:autoUpdateNextAt?new Date(autoUpdateNextAt).toISOString():null,
      last_result:autoUpdateLastResult
    },
    audit
  };
}
function runUpdaterStage() {
  const script=join(ROOT,'scripts','slot-update.mjs');
  return new Promise((resolve,reject)=>{
    execFile(process.execPath,[script,'stage'],{cwd:ROOT,windowsHide:true,timeout:180000,maxBuffer:1024*1024},(err,stdout,stderr)=>{
      if(err)return reject(new Error('AUTO_STAGE_FAILED '+String(stderr||err.message||err).slice(0,500)));
      resolve(String(stdout||''));
    });
  });
}
function spawnUpdaterApply() {
  const script=join(ROOT,'scripts','slot-update.mjs');
  const child=spawn(process.execPath,[script,'apply'],{cwd:ROOT,windowsHide:true,detached:true,stdio:'ignore'});
  child.unref();
  event('INFO','AUTO_UPDATE_APPLY_TRIGGERED','pid='+child.pid);
  return child.pid;
}
function scheduleAutoUpdate(delayMs=AUTO_UPDATE_INTERVAL_MS){
  try{if(autoUpdateTimer)clearTimeout(autoUpdateTimer)}catch{}
  autoUpdateNextAt=Date.now()+Math.max(1000,Number(delayMs||AUTO_UPDATE_INTERVAL_MS));
  autoUpdateTimer=setTimeout(autoUpdateTick,Math.max(1000,Number(delayMs||AUTO_UPDATE_INTERVAL_MS)));
  try{autoUpdateTimer.unref()}catch{}
}
async function autoUpdateTick(){
  if(autoUpdateRunning){scheduleAutoUpdate(5*60*1000);return}
  autoUpdateRunning=true;autoUpdateLastAt=Date.now();autoUpdateNextAt=0;
  try{
    const explicitAge=lastExplicitInteractionAt?Date.now()-lastExplicitInteractionAt:Infinity;
    const guard=resourceGovernor();
    if(explicitAge<AUTO_UPDATE_IDLE_GUARD_MS){
      autoUpdateLastResult='DEFER_USER_ACTIVE';
      event('INFO','AUTO_UPDATE_DEFER','user-active');
      scheduleAutoUpdate(5*60*1000);return;
    }
    if(guard.mode==='PAUSED'){
      autoUpdateLastResult='DEFER_RESOURCE_PRESSURE';
      event('INFO','AUTO_UPDATE_DEFER',guard.reason||'resource-pressure');
      scheduleAutoUpdate(10*60*1000);return;
    }
    event('INFO','AUTO_UPDATE_CHECK_BEGIN','channel=release/tlib-hybrid-v2-stable');
    let pending=readJsonSafe(join(dataDir,'pending-deployment.json'),null);
    if(!(pending&&pending.verified)){
      await runUpdaterStage();
      pending=readJsonSafe(join(dataDir,'pending-deployment.json'),null);
    }else{
      event('INFO','AUTO_UPDATE_REUSE_PENDING',String(pending.commit||''));
    }
    if(!pending?.verified){
      autoUpdateLastResult='NO_UPDATE';
      event('INFO','AUTO_UPDATE_NO_UPDATE',APP_COMMIT);
      scheduleAutoUpdate(AUTO_UPDATE_INTERVAL_MS);return;
    }
    const ageAfterStage=lastExplicitInteractionAt?Date.now()-lastExplicitInteractionAt:Infinity;
    if(ageAfterStage<AUTO_UPDATE_IDLE_GUARD_MS){
      autoUpdateLastResult='STAGED_WAITING_FOR_IDLE';
      event('INFO','AUTO_UPDATE_STAGED_WAIT_IDLE',String(pending.commit||''));
      scheduleAutoUpdate(5*60*1000);return;
    }
    const guardAfter=resourceGovernor();
    if(guardAfter.mode==='PAUSED'){
      autoUpdateLastResult='STAGED_WAITING_FOR_RESOURCES';
      event('INFO','AUTO_UPDATE_STAGED_WAIT_RESOURCES',guardAfter.reason||'resource-pressure');
      scheduleAutoUpdate(10*60*1000);return;
    }
    autoUpdateLastResult='APPLY_TRIGGERED';
    spawnUpdaterApply();
    scheduleAutoUpdate(10*60*1000);
  }catch(e){
    autoUpdateLastResult='ERROR';
    event('WARN','AUTO_UPDATE_ERROR',String(e.message||e).slice(0,500));
    scheduleAutoUpdate(30*60*1000);
  }finally{autoUpdateRunning=false}
}
function promoteCurrentToLastGoodAfterSoak(){
  const timer=setTimeout(()=>{
    try{
      const current=readJsonSafe(join(dataDir,'current-deployment.json'),null);
      if(!current||current.commit!==APP_COMMIT)return;
      const value={...current,build:APP_BUILD,pid:process.pid,promoted_at:new Date().toISOString(),soak_minutes:15};
      const dest=join(dataDir,'last-good-deployment.json'),tmp=dest+'.tmp-'+process.pid;
      writeFileSync(tmp,JSON.stringify(value,null,2)+'\n','utf8');
      try{renameSync(tmp,dest)}catch{writeFileSync(dest,JSON.stringify(value,null,2)+'\n','utf8')}
      event('INFO','LAST_GOOD_PROMOTED','commit='+APP_COMMIT+' soak=15m');
    }catch(e){event('WARN','LAST_GOOD_PROMOTE_FAIL',String(e.message||e).slice(0,300))}
  },LAST_GOOD_SOAK_MS);
  try{timer.unref()}catch{}
}
function startAutonomousUpdates(){
  event('INFO','AUTO_UPDATE_ARMED','first=45s interval=10m channel=release/tlib-hybrid-v2-stable');
  scheduleAutoUpdate(AUTO_UPDATE_FIRST_DELAY_MS);
}

function spawnUpdater(mode) {
  const map={Stage:'stage',Apply:'apply',Repair:'repair'};
  const chosen=map[mode];
  if(!chosen) throw new Error('INVALID_UPDATE_MODE');
  const script=join(ROOT,'scripts','slot-update.mjs');
  const child=spawn(process.execPath,[script,chosen],{windowsHide:true,detached:true,stdio:'ignore'});
  child.unref();
  event('INFO','SLOT_UPDATE_TRIGGERED',chosen);
  return true;
}

let statusCacheValue=null;
let statusCacheAt=0;
function statusSnapshot(force=false) {
  const nowMs=Date.now();
  if(!force && statusCacheValue && nowMs-statusCacheAt<30000){
    const cached=JSON.parse(JSON.stringify(statusCacheValue));
    if(cached.pc_worker&&cached.pc_worker.runtime){
      cached.pc_worker.runtime.uptime_seconds=Math.round(process.uptime());
      cached.pc_worker.runtime.rss_mb=Math.round(process.memoryUsage().rss/1048576);
    }
    if(cached.pc_worker) cached.pc_worker.resource_governor=governorState;
    return cached;
  }
  const counts = {};
  for (const r of db.prepare('SELECT status, COUNT(*) AS n FROM jobs GROUP BY status').all()) counts[r.status] = Number(r.n);
  const totalResults = Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n);
  const l2stat=l2Stats(),l3stat=l3Stats();
  const l2Count = Number(l2stat.total||0);
  const recent = db.prepare(`SELECT r.full_name,r.description,r.stars,r.language,r.archived,r.fork,r.rate_remaining,r.fetched_at,
                                    r.resource_kind,r.technology,r.content_mode,r.activity_status,r.l1_quality,l.human_summary
                             FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id AND l.source_version='${L2_RULESET_VERSION}'
                             ORDER BY r.fetched_at DESC LIMIT 12`).all();
  const events = db.prepare('SELECT at,level,event,detail FROM events ORDER BY id DESC LIMIT 12').all();
  const control = loadControlSnapshot();
  const levels = JSON.parse(JSON.stringify(control.product || {}));
  if (levels.l1) { levels.l1.count = totalResults; if (totalResults > 0) levels.l1.state = 'CANARY'; }
  if (levels.l2) { levels.l2.count = l2Count; if (l2Count > 0) levels.l2.state = l2Count>10?'RUNNING':'CANARY'; }
  if (levels.l3) { levels.l3.count = l3stat.total; levels.l3.state = l3stat.total>0?'RUNNING':'DESIGNED'; }
  const out={
    product: 'TLIB',
    build: APP_BUILD,
    commit: APP_COMMIT,
    started_at: STARTED_AT,
    mode: 'HYBRID_V2_LAB',
    pc_worker: { online:true, database:dbPath, local_l1_results:totalResults, local_l2_profiles:l2Count, queue:counts,
      runtime:{node:process.versions.node,pid:process.pid,uptime_seconds:Math.round(process.uptime()),rss_mb:Math.round(process.memoryUsage().rss/1048576)},
      staged_l1:fixtureCorpus().length, staged_names:stagedNameCount, autopilot:true,
      github_auth_mode: githubAuthMode, l1_stats:l1Stats(),
      public_next_attempt_at: publicNextAttemptAt ? new Date(publicNextAttemptAt).toISOString() : null,
      public_rate_remaining: publicRateRemaining, public_rate_reset: publicRateReset,
      scheduler_mode:schedulerMode(), l1_scheduler_mode:l1SchedulerMode(), deep_backlog:deepBacklogCount(), l2_stats:l2stat, l3_stats:l3stat, resource_governor:governorState },
    apps_script: control.engine || {},
    levels,
    recent,
    events
  };
  statusCacheValue=out;
  statusCacheAt=nowMs;
  return JSON.parse(JSON.stringify(out));
}

function deepQueueRows(limit=50, state='pending') {
  limit=Math.max(1,Math.min(Number(limit||50),200));
  const states=state==='done'?['DONE']:['PENDING','RETRY'];
  const marks=states.map(()=>'?').join(',');
  return db.prepare(`SELECT entity_id,full_name,technology,activity_status,l1_score,deep_status,fetched_at
                     FROM results
                     WHERE resource_kind='Projet logiciel' AND coalesce(deep_status,'PENDING') IN (${marks})
                     ORDER BY fetched_at ASC LIMIT ?`).all(...states,limit);
}

function reportLines(type='manager') {
  const s=statusSnapshot(), q=s.pc_worker.queue||{}, st=s.pc_worker.l1_stats||{}, a=s.apps_script||{}, rt=s.pc_worker.runtime||{};
  const head=[
    'TLIB - Rapport '+String(type).toUpperCase(),
    'Genere: '+new Date().toISOString(),
    ''
  ];
  const common=[
    'L0 ressources: '+Number(a.entity_count||0).toLocaleString('fr-FR'),
    'L1 verifiees: '+Number(st.core||0).toLocaleString('fr-FR'),
    'L1 completes: '+Number(st.complete||0).toLocaleString('fr-FR'),
    'L1 profondes: '+Number(st.deep_done||0).toLocaleString('fr-FR'),
    'Approfondissements en attente: '+Number(st.deep_pending||0).toLocaleString('fr-FR'),
    'Mode ordonnanceur: '+String(s.pc_worker.scheduler_mode||''),
    'Cadence recente: '+Number(st.throughput_per_hour||0).toLocaleString('fr-FR')+' fiches/h',
    ''
  ];
  if(type==='l0') return head.concat([
    'Etat L0: '+String(a.status||''),
    'Sources explorees: '+Number(a.source_count||0).toLocaleString('fr-FR'),
    'Sources terminees: '+Number(a.source_done||0).toLocaleString('fr-FR'),
    'Sources epuisees: '+Number(a.source_failed||0).toLocaleString('fr-FR'),
    'Sources en attente: '+Number(a.source_pending||0).toLocaleString('fr-FR'),
    '',
    'Objet: decouverte, normalisation et deduplication des ressources.'
  ]);
  if(type==='l1') return head.concat(common,[
    'Queue DONE: '+Number(q.DONE||0).toLocaleString('fr-FR'),
    'Queue PENDING: '+Number(q.PENDING||0).toLocaleString('fr-FR'),
    'Queue RUNNING: '+Number(q.RUNNING||0).toLocaleString('fr-FR'),
    'Erreurs 24h: '+Number(st.errors_24h||0).toLocaleString('fr-FR'),
    '',
    'Strategie: resorber la dette d approfondissement avant expansion rapide.'
  ]);
  if(type==='technical') return head.concat([
    'Node: '+String(rt.node||''),
    'PID: '+String(rt.pid||''),
    'Uptime: '+Number(rt.uptime_seconds||0).toLocaleString('fr-FR')+' s',
    'RAM worker: '+Number(rt.rss_mb||0).toLocaleString('fr-FR')+' Mo',
    'GitHub auth: '+String(s.pc_worker.github_auth_mode||''),
    'Quota GitHub restant: '+Number(s.pc_worker.public_rate_remaining||0).toLocaleString('fr-FR'),
    'SQLite: '+String(s.pc_worker.database||'')
  ]);
  return head.concat(common,[
    'Worker: EN LIGNE',
    'GitHub auth: '+String(s.pc_worker.github_auth_mode||''),
    'Quota restant: '+Number(s.pc_worker.public_rate_remaining||0).toLocaleString('fr-FR'),
    'RAM worker: '+Number(rt.rss_mb||0).toLocaleString('fr-FR')+' Mo'
  ]);
}

function pdfEscape(s) {
  return String(s).replace(/\\/g,'\\\\').replace(/\(/g,'\\(').replace(/\)/g,'\\)');
}
function latin1(s) {
  return Buffer.from(String(s).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^\x20-\xFF]/g,'?'),'latin1');
}
function simplePdf(title, lines) {
  const perPage=46, pages=[];
  for(let i=0;i<lines.length;i+=perPage) pages.push(lines.slice(i,i+perPage));
  if(!pages.length) pages.push([]);
  const objects=[null];
  const fontId=1; objects.push('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
  const pageIds=[], contentIds=[];
  const pagesId=2; objects.push('');
  for(const rows of pages){
    const pageId=objects.length; pageIds.push(pageId); objects.push('');
    const contentId=objects.length; contentIds.push(contentId);
    let body='BT\n/F1 11 Tf\n50 790 Td\n14 TL\n';
    const all=[title,'',...rows];
    for(let i=0;i<all.length;i++){
      const line=pdfEscape(String(all[i]).slice(0,110));
      if(i===0) body+='/F1 16 Tf\n('+line+') Tj\n/F1 11 Tf\n';
      else body+='T*\n('+line+') Tj\n';
    }
    body+='ET\n';
    const bytes=latin1(body);
    objects.push(Buffer.concat([Buffer.from('<< /Length '+bytes.length+' >>\nstream\n','ascii'),bytes,Buffer.from('endstream','ascii')]));
  }
  objects[pagesId]='<< /Type /Pages /Count '+pageIds.length+' /Kids ['+pageIds.map(id=>id+' 0 R').join(' ')+'] >>';
  for(let i=0;i<pageIds.length;i++) objects[pageIds[i]]='<< /Type /Page /Parent '+pagesId+' 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 '+fontId+' 0 R >> >> /Contents '+contentIds[i]+' 0 R >>';
  const catalogId=objects.length; objects.push('<< /Type /Catalog /Pages '+pagesId+' 0 R >>');
  const chunks=[Buffer.from('%PDF-1.4\n%TLIB\n','ascii')], offsets=[0];
  let pos=chunks[0].length;
  for(let i=1;i<objects.length;i++){
    offsets[i]=pos;
    const head=Buffer.from(i+' 0 obj\n','ascii');
    const body=Buffer.isBuffer(objects[i])?objects[i]:latin1(objects[i]);
    const tail=Buffer.from('\nendobj\n','ascii');
    chunks.push(head,body,tail); pos+=head.length+body.length+tail.length;
  }
  const xrefPos=pos;
  let xref='xref\n0 '+objects.length+'\n0000000000 65535 f \n';
  for(let i=1;i<objects.length;i++) xref+=String(offsets[i]).padStart(10,'0')+' 00000 n \n';
  xref+='trailer\n<< /Size '+objects.length+' /Root '+catalogId+' 0 R >>\nstartxref\n'+xrefPos+'\n%%EOF';
  chunks.push(Buffer.from(xref,'ascii'));
  return Buffer.concat(chunks);
}
function sendPdf(res, type) {
  const lines=reportLines(type), pdf=simplePdf('TLIB - '+String(type).toUpperCase(),lines);
  res.writeHead(200, {'content-type':'application/pdf','content-disposition':'attachment; filename="TLIB_'+String(type).toUpperCase()+'_'+new Date().toISOString().slice(0,10)+'.pdf"','cache-control':'no-store','content-length':pdf.length});
  res.end(pdf);
}

function sendJson(res, code, value) {
  res.writeHead(code, {'content-type':'application/json; charset=utf-8','cache-control':'no-store'});
  res.end(JSON.stringify(value));
}

async function startDashboard() {
  const port = Number(process.env.TLIB_DASHBOARD_PORT || 8787);
  const dashboardPage = readFileSync(join(ROOT,'public','index.html'),'utf8').replaceAll('__TLIB_BUILD__',APP_BUILD).replaceAll('__TLIB_COMMIT__',APP_COMMIT);
  const qrCodeJs = readFileSync(join(ROOT,'public','vendor','qrcode.min.js'),'utf8');
  let busy = false;
  const server = http.createServer(async (req,res) => {
    const u = new URL(req.url || '/', 'http://127.0.0.1');
    const local=isLoopbackRequest(req);
    const phoneSession=local?null:validPhoneSession(req);
    markInteractiveRequest(u.pathname);
    try {
      res.setHeader('Referrer-Policy','no-referrer');
      res.setHeader('X-Content-Type-Options','nosniff');

      if(u.pathname==='/pair'&&!local){
        if(!activePhoneOffer()) return sendJson(res,403,{error:'PAIRING_NOT_ACTIVE'});
        const html=pairPage();
        res.writeHead(200,{'content-type':'text/html; charset=utf-8','cache-control':'no-store','content-length':Buffer.byteLength(html)});
        return res.end(html);
      }
      if(u.pathname==='/api/mobile/claim'&&req.method==='POST'&&!local){
        if(!phoneClaimAllowed(req)) return sendJson(res,429,{error:'PAIR_RATE_LIMIT'});
        const offer=activePhoneOffer();if(!offer)return sendJson(res,410,{error:'PAIR_EXPIRED'});
        const body=await readJsonBody(req).catch(e=>null);if(!body)return sendJson(res,400,{error:'INVALID_BODY'});
        const ok=(body.token&&safeEqualText(body.token,offer.secret))||(body.code&&safeEqualText(String(body.code).trim().toUpperCase(),offer.code));
        if(!ok)return sendJson(res,403,{error:'PAIR_CODE_INVALID'});
        const raw=randomBytes(32).toString('base64url'),state=phoneState(),nowMs=Date.now(),expiresAt=nowMs+offer.minutes*60*1000,id=randomBytes(6).toString('hex');
        state.sessions.push({id,hash:tokenHash(raw),duration_minutes:offer.minutes,created_at:nowMs,expires_at:expiresAt,last_seen:nowMs});
        state.pair_offer=null;savePhoneState(state);
        res.setHeader('Set-Cookie',PHONE_COOKIE+'='+encodeURIComponent(raw)+'; HttpOnly; SameSite=Strict; Path=/; Max-Age='+Math.floor(offer.minutes*60));
        event('INFO','PHONE_PAIR_CLAIMED','duration='+offer.minutes+'m; remote='+remoteAddress(req));
        return sendJson(res,200,{ok:true,expires_at:new Date(expiresAt).toISOString(),read_only:true});
      }

      if(!local&&!phoneSession) return sendJson(res,401,{error:'PHONE_AUTH_REQUIRED'});
      if(!local&&req.method!=='GET'&&u.pathname!=='/api/interaction') return sendJson(res,403,{error:'PHONE_READ_ONLY'});

      if(u.pathname==='/vendor/qrcode.min.js'){
        res.writeHead(200,{'content-type':'application/javascript; charset=utf-8','cache-control':'public, max-age=86400','content-length':Buffer.byteLength(qrCodeJs)});
        return res.end(qrCodeJs);
      }
      if(u.pathname==='/api/mobile/status'){
        if(!local)return sendJson(res,403,{error:'LOCAL_ONLY'});
        return sendJson(res,200,phoneStatus());
      }
      if(u.pathname==='/api/mobile/pair'&&req.method==='POST'){
        if(!local)return sendJson(res,403,{error:'LOCAL_ONLY'});
        const out=createPhonePair(u.searchParams.get('minutes')||30);
        return sendJson(res,out.ok===false?409:200,out);
      }
      if(u.pathname==='/api/mobile/revoke'&&req.method==='POST'){
        if(!local)return sendJson(res,403,{error:'LOCAL_ONLY'});
        return sendJson(res,200,revokePhoneSessions());
      }
      if(u.pathname==='/api/mobile/session/revoke'&&req.method==='POST'){
        if(!local)return sendJson(res,403,{error:'LOCAL_ONLY'});
        return sendJson(res,200,revokePhoneSession(u.searchParams.get('id')||''));
      }
      if (u.pathname === '/api/interaction' && req.method === 'POST') return sendJson(res,200,{ok:true});
      if (u.pathname === '/api/status') return sendJson(res,200,statusSnapshot());
      if (u.pathname === '/api/version') return sendJson(res,200,{product:'TLIB',build:APP_BUILD,pid:process.pid,node:process.versions.node});
      if (u.pathname === '/api/library') {
        const q=u.searchParams.get('q')||'', limit=u.searchParams.get('limit')||100,
              offset=u.searchParams.get('offset')||0, sort=u.searchParams.get('sort')||'stars';
        const searchInfo=q?resolveSearchMatch(q):{mode:'BROWSE',match:''};
        return sendJson(res,200,{items:libraryRows(q,limit,offset,sort),total:libraryCount(q),limit:Number(limit),offset:Number(offset),sort:q?'relevance':sort,search_mode:searchInfo.mode,search_engine:q?'FTS5_L1_L2_L3':'BROWSE'});
      }
      if (u.pathname === '/api/update/status' && req.method === 'GET') return sendJson(res,200,updateStatusSnapshot());
      if (u.pathname === '/api/update/action' && req.method === 'POST') {
        const requested=String(u.searchParams.get('mode')||'Stage');
        if(!['Stage','Apply','Repair'].includes(requested)) return sendJson(res,400,{ok:false,error:'INVALID_UPDATE_MODE'});
        sendJson(res,202,{ok:true,accepted:requested});
        setTimeout(()=>{try{spawnUpdater(requested)}catch(e){event('ERROR','UPDATE_TRIGGER_FAILED',String(e.message||e))}},250);
        return;
      }
      if (u.pathname === '/api/l0/sources') return sendJson(res,200,l0SourcesSnapshot({
        q:u.searchParams.get('q')||'', status:u.searchParams.get('status')||'', depth:u.searchParams.get('depth')??'',
        limit:u.searchParams.get('limit')||100, offset:u.searchParams.get('offset')||0
      }));
      if (u.pathname === '/api/l1/insights') return sendJson(res,200,l1InsightsSnapshot());
      if (u.pathname === '/api/l1/drilldown') return sendJson(res,200,l1Drilldown(u.searchParams.get('kind')||'verified',u.searchParams.get('q')||'',u.searchParams.get('limit')||50,u.searchParams.get('offset')||0,u.searchParams.get('sort')||'score',u.searchParams.get('band')||''));
      if (u.pathname === '/api/l2/drilldown') return sendJson(res,200,l2Drilldown(u.searchParams.get('kind')||'profiles',u.searchParams.get('q')||'',u.searchParams.get('limit')||50,u.searchParams.get('offset')||0,u.searchParams.get('sort')||'score'));
      if (u.pathname === '/api/chat/search') return sendJson(res,200,chatSearch(u.searchParams.get('q')||'',u.searchParams.get('limit')||8));
      if (u.pathname === '/api/facets') return sendJson(res,200,facetsSnapshot());
      if (u.pathname === '/api/l1/stats') return sendJson(res,200,l1Stats());
      if (u.pathname === '/api/l2/list') return sendJson(res,200,{items:l2Rows(u.searchParams.get('limit')||100),stats:l2Stats()});
      if (u.pathname === '/api/l2/queue') return sendJson(res,200,{items:l2QueueRows(u.searchParams.get('limit')||60),stats:l2Stats()});
      if (u.pathname === '/api/l3/list') return sendJson(res,200,{items:l3Rows(u.searchParams.get('limit')||100),stats:l3Stats()});
      if (u.pathname === '/api/resource') {
        const item=resourceById(u.searchParams.get('id')||'');
        return item ? sendJson(res,200,item) : sendJson(res,404,{error:'NOT_FOUND'});
      }
      if (u.pathname === '/api/l1/deep' && req.method === 'GET') {
        return sendJson(res,200,{state:u.searchParams.get('state')||'pending',items:deepQueueRows(u.searchParams.get('limit')||50,u.searchParams.get('state')||'pending')});
      }
      if (u.pathname === '/api/report' && req.method === 'GET') {
        const type=['manager','l0','l1','technical'].includes(u.searchParams.get('type'))?u.searchParams.get('type'):'manager';
        return sendPdf(res,type);
      }
      if (u.pathname === '/api/events') {
        const items=db.prepare('SELECT at,level,event,detail FROM events ORDER BY id DESC LIMIT 100').all();
        return sendJson(res,200,{items});
      }
      if (u.pathname === '/api/action/fixture-canary' && req.method === 'POST') {
        if (busy) return sendJson(res,409,{ok:false,message:'Un test est déjà en cours.'});
        busy=true;
        try { fixtureCanary(); return sendJson(res,200,{ok:true,message:'Test L1 local terminé.',status:statusSnapshot()}); }
        finally { busy=false; }
      }
      if (u.pathname === '/api/action/fixture-l2' && req.method === 'POST') {
        if (busy) return sendJson(res,409,{ok:false,message:'Un test est déjà en cours.'});
        busy=true;
        try { fixtureL2Canary(); return sendJson(res,200,{ok:true,message:'10 profils L2 de démonstration chargés.',status:statusSnapshot()}); }
        finally { busy=false; }
      }
      if (u.pathname === '/api/health') return sendJson(res,200,{ok:true,at:now(),build:APP_BUILD,commit:APP_COMMIT,pid:process.pid,started_at:STARTED_AT});
      if (u.pathname === '/api/version') return sendJson(res,200,{product:'TLIB',build:APP_BUILD,commit:APP_COMMIT,pid:process.pid,started_at:STARTED_AT,root:ROOT});
      res.writeHead(200, {'content-type':'text/html; charset=utf-8','cache-control':'no-store','content-length':Buffer.byteLength(dashboardPage)});
      res.end(dashboardPage);
    } catch (e) {
      event('ERROR','HTTP_ERROR',e.message || String(e));
      sendJson(res,500,{error:'LOCAL_SERVER_ERROR',message:String(e.message||e)});
    }
  });
  server.on('error', (e) => {
    event('ERROR','DASHBOARD_BIND_ERROR',String(e.code||'')+' '+String(e.message||e));
    console.error('TLIB dashboard bind failed:',e);
    // A worker that cannot own the dashboard port is useless and must not
    // remain resident as a RAM-consuming ghost process.
    setTimeout(()=>process.exit(2),50);
  });
  server.listen(port, '0.0.0.0', () => {
    writeRuntimeMarker();
    const lan=privateLanIpv4();
    event('INFO','DASHBOARD_STARTED','0.0.0.0:' + port + '; lan='+(lan||'none')+'; build=' + APP_BUILD + '; commit=' + APP_COMMIT);
    console.log('TLIB dashboard: http://127.0.0.1:' + port + ' [' + APP_BUILD + ']');
  });
  return server;
}

function pidAlive(pid){
  try{process.kill(Number(pid),0);return true}catch{return false}
}
function readBackgroundWorker(){
  try{return JSON.parse(readFileSync(BG_WORKER_FILE,'utf8'))}catch{return null}
}
function writeBackgroundWorker(extra){
  try{writeFileSync(BG_WORKER_FILE,JSON.stringify({
    pid:process.pid,build:APP_BUILD,commit:APP_COMMIT,started_at:STARTED_AT,...extra
  },null,2),'utf8')}catch{}
}
function ensureBackgroundWorker(){
  const existing=readBackgroundWorker();
  if(existing&&existing.pid&&pidAlive(existing.pid)){
    if(existing.commit===APP_COMMIT && existing.build===APP_BUILD) return existing;
    try{process.kill(Number(existing.pid),'SIGTERM')}catch{}
  }
  const child=spawn(process.execPath,[fileURLToPath(import.meta.url),'worker'],{
    cwd:ROOT,detached:true,windowsHide:true,stdio:'ignore',
    env:{...process.env,TLIB_DATA_DIR:dataDir,TLIB_DEPLOYMENT_COMMIT:APP_COMMIT,TLIB_BACKGROUND_WORKER:'1'}
  });
  child.unref();
  const state={pid:child.pid,build:APP_BUILD,commit:APP_COMMIT,spawned_at:now(),state:'SPAWNED'};
  try{writeFileSync(BG_WORKER_FILE,JSON.stringify(state,null,2),'utf8')}catch{}
  event('INFO','BACKGROUND_WORKER_SPAWN','pid='+child.pid);
  return state;
}
function startWorkerLoop(){
  try { setPriority(process.pid, osConstants.priority?.PRIORITY_BELOW_NORMAL ?? 10); } catch {}
  writeBackgroundWorker({state:'RUNNING'});
  process.on('exit',()=>writeBackgroundWorker({state:'STOPPED',stopped_at:now()}));
  setTimeout(async () => {
    try {
      stageFixtureJobs();
      stageNamedQueue();
      warmGitHubToken().catch(e=>event('WARN','TOKEN_WARMUP_FAILED',e.message||String(e)));
    } catch(e) {
      event('ERROR','BOOTSTRAP_LIGHT_ERROR',e.message||String(e));
    }
  }, 2500);

  let running=false, timer=null;
  const schedule=(ms)=>{ clearTimeout(timer); timer=setTimeout(tick,Math.max(1000,Number(ms||3000))); };
  const tick=async()=>{
    if(running){schedule(3000);return}
    const guard=resourceGovernor();
    writeBackgroundWorker({state:guard.mode,governor:guard});
    if(guard.mode==='PAUSED'||guard.mode==='USER_ACTIVE'){
      if(guard.mode==='PAUSED')event('INFO','ECO_PAUSE',guard.reason+'; free='+guard.free_mb+'MB; cpu='+(guard.cpu_pct??'n/a'));
      schedule(guard.delay_ms);
      return;
    }
    running=true;
    try {
      const stagedDone=autopilotFixtureStep(Number(process.env.TLIB_STAGE_STEP || 1));
      if(!stagedDone) {
        await scheduledPipelineStep();
      }
    } catch(e){
      event('ERROR','L1_AUTOPILOT_ERROR',e.message||String(e));
    } finally {
      running=false;
      const next=resourceGovernor();
      schedule(Number(process.env.TLIB_STAGE_INTERVAL_MS || next.delay_ms));
    }
  };
  resourceGovernor();
  schedule(3000);
}

async function main() {
  const cmd = process.argv[2] || 'selftest';
  if (cmd === 'selftest') return selftest();
  if (cmd === 'seed') return seed();
  if (cmd === 'reclassify') { console.log(JSON.stringify({ok:true,rows:reclassifyExisting()},null,2)); return; }
  if (cmd === 'search-audit') { reclassifyExisting(); console.log(JSON.stringify(await searchAuditSnapshot(),null,2)); return; }
  if (cmd === 'canary') return canary(Number(argValue('--limit', '10')));
  if (cmd === 'fixture-canary') return fixtureCanary();
  if (cmd === 'fixture-l2') return fixtureL2Canary();
  if (cmd === 'dashboard') return startDashboard();
  if (cmd === 'worker') {
    selftest();
    seed();
    reclassifyExisting();
    ensureSearchIndex(true);
    startWorkerLoop();
    return;
  }
  if (cmd === 'agent') {
    // UI/server stays at normal OS priority. Background enrichment runs in a
    // separate below-normal process so SQLite/GitHub work cannot block 8787.
    selftest();
    seed();
    startDashboard();
    ensureBackgroundWorker();
    startAutonomousUpdates();
    promoteCurrentToLastGoodAfterSoak();
    return;
  }
  throw new Error('UNKNOWN_COMMAND ' + cmd);
}

main().catch(e => {
  try { event('FATAL','PROCESS_ERROR',e.stack || e.message); } catch {}
  console.error(e.stack || e.message);
  process.exitCode = 1;
});
