import http from 'node:http';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { homedir, freemem, totalmem, cpus, networkInterfaces, setPriority, constants as osConstants } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';
import { execFileSync, execFile, spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..');
const dataDir = process.env.TLIB_DATA_DIR || join(process.env.LOCALAPPDATA || homedir(), 'TLIB-PC');
mkdirSync(dataDir, { recursive: true });
const APP_BUILD = '2026.09.28-v0.6.8-phone-lan';
const STARTED_AT = new Date().toISOString();
const DASHBOARD_PORT = Number(process.env.TLIB_DASHBOARD_PORT || 8787);
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

db.exec(`
CREATE INDEX IF NOT EXISTS idx_jobs_status_updated ON jobs(status,updated_at);
CREATE INDEX IF NOT EXISTS idx_results_deep_fetched ON results(resource_kind,deep_status,fetched_at);
CREATE INDEX IF NOT EXISTS idx_results_stage ON results(l1_stage);
CREATE INDEX IF NOT EXISTS idx_results_fetched ON results(fetched_at);
CREATE INDEX IF NOT EXISTS idx_events_level_at ON events(level,at);
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

const TAXONOMY_VERSION='2026.09-v1';
const THEME_RULES=[
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
  const primary=uniq[0] || (q.technology && q.technology!=='Domaine à préciser' ? 'Autres/'+q.technology : 'Autres/À classifier');
  const tags=[...new Set([
    ...uniq.flatMap(p=>p.split('/').slice(-2)),
    q.technology!=='Domaine à préciser'?q.technology:'',
    q.kind,
    ...topics.slice(0,12)
  ].filter(Boolean))].slice(0,24);
  const confidence=Math.min(0.99, uniq.length?0.72+Math.min(0.24,uniq.length*0.06):(q.technology!=='Domaine à préciser'?0.55:0.35));
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
    has_issues=?,has_projects=?,has_downloads=?,is_template=?,l1_summary=?,l1_stage=?,
    deep_status=coalesce(deep_status,?)
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
  if(changed) event('INFO','L1_RECLASSIFY','rows='+changed);
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
  event('INFO', 'SELFTEST_PASS', `node=${process.versions.node}`);
  console.log(JSON.stringify({ ok: true, node: process.versions.node, sqlite: true, dbPath }, null, 2));
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
function schedulerMode() {
  const backlog=deepBacklogCount();
  if(backlog>100 && (publicRateRemaining===null || publicRateRemaining>=2000)) return 'DEEP_CATCHUP';
  if(backlog>25) return 'BALANCED_DEEP_FIRST';
  return 'CORE_EXPANSION';
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
    entity_id,human_summary,capabilities_json,use_cases_json,limitations_json,confidence,source,updated_at
  ) VALUES(?,?,?,?,?,?,?,?)`);
  for (const p of profiles) {
    const id = entityId(p.full_name);
    const exists = db.prepare('SELECT entity_id FROM results WHERE entity_id=?').get(id);
    if (!exists) continue;
    stmt.run(id,String(p.summary||''),JSON.stringify(p.capabilities||[]),JSON.stringify(p.use_cases||[]),
      JSON.stringify(p.limitations||[]),Number(p.confidence||0),String(p.source||'fixture'),now());
    done++;
  }
  event('INFO','L2_FIXTURE_PASS','done=' + done);
  console.log(JSON.stringify({ok:true,mode:'l2-fixture',done,summary:statusSnapshot()},null,2));
}

function loadControlSnapshot() {
  try { return JSON.parse(readFileSync(join(ROOT, 'config', 'control-snapshot.json'), 'utf8')); }
  catch { return { engine:{}, product:{} }; }
}

function libraryRows(q='', limit=100, offset=0, sort='stars') {
  q = String(q || '').trim().toLowerCase();
  limit = Math.max(1, Math.min(Number(limit || 100), 500));
  offset = Math.max(0, Number(offset || 0));
  const orders={stars:'r.stars DESC',recent:'r.pushed_at DESC',verified:'r.fetched_at DESC',complete:'r.l1_score DESC',name:'r.full_name ASC'};
  const order=orders[String(sort||'stars')]||orders.stars;
  if (!q) {
    return db.prepare(`SELECT r.entity_id,r.full_name,r.description,r.stars,r.language,r.license,r.topics_json,r.archived,r.fork,
                              r.updated_at_github,r.pushed_at,r.default_branch,r.size_kb,r.open_issues,r.fetched_at,
                              r.resource_kind,r.technology,r.content_mode,r.activity_status,r.activity_days,r.l1_quality,r.l1_score,
                              r.primary_theme,r.theme_path,r.theme_tags_json,r.theme_confidence,
                              l.human_summary
                       FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id
                       ORDER BY ${order} LIMIT ? OFFSET ?`).all(limit,offset);
  }
  const like = '%' + q + '%';
  return db.prepare(`SELECT r.entity_id,r.full_name,r.description,r.stars,r.language,r.license,r.topics_json,r.archived,r.fork,
                            r.updated_at_github,r.pushed_at,r.default_branch,r.size_kb,r.open_issues,r.fetched_at,
                            r.resource_kind,r.technology,r.content_mode,r.activity_status,r.activity_days,r.l1_quality,r.l1_score,
                            r.primary_theme,r.theme_path,r.theme_tags_json,r.theme_confidence,
                            l.human_summary
                     FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id
                     WHERE lower(r.full_name) LIKE ? OR lower(r.description) LIKE ? OR lower(r.language) LIKE ?
                        OR lower(r.license) LIKE ? OR lower(r.topics_json) LIKE ? OR lower(coalesce(l.human_summary,'')) LIKE ?
                        OR lower(coalesce(r.technology,'')) LIKE ? OR lower(coalesce(r.resource_kind,'')) LIKE ?
                        OR lower(coalesce(r.activity_status,'')) LIKE ? OR lower(coalesce(r.content_mode,'')) LIKE ?
                        OR lower(coalesce(r.primary_theme,'')) LIKE ? OR lower(coalesce(r.theme_path,'')) LIKE ?
                        OR lower(coalesce(r.theme_tags_json,'')) LIKE ?
                     ORDER BY ${order} LIMIT ? OFFSET ?`).all(like,like,like,like,like,like,like,like,like,like,like,like,like,limit,offset);
}

function libraryCount(q='') {
  q=String(q||'').trim().toLowerCase();
  if(!q) return Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n);
  const like='%'+q+'%';
  return Number(db.prepare(`SELECT COUNT(*) AS n
    FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id
    WHERE lower(r.full_name) LIKE ? OR lower(r.description) LIKE ? OR lower(r.language) LIKE ?
       OR lower(r.license) LIKE ? OR lower(r.topics_json) LIKE ? OR lower(coalesce(l.human_summary,'')) LIKE ?
       OR lower(coalesce(r.technology,'')) LIKE ? OR lower(coalesce(r.resource_kind,'')) LIKE ?
       OR lower(coalesce(r.activity_status,'')) LIKE ? OR lower(coalesce(r.content_mode,'')) LIKE ?
       OR lower(coalesce(r.primary_theme,'')) LIKE ? OR lower(coalesce(r.theme_path,'')) LIKE ?
       OR lower(coalesce(r.theme_tags_json,'')) LIKE ?`)
    .get(like,like,like,like,like,like,like,like,like,like,like,like,like).n);
}

function l2Rows(limit=100) {
  limit=Math.max(1,Math.min(Number(limit||100),500));
  return db.prepare(`SELECT r.entity_id,r.full_name,r.resource_kind,r.technology,r.activity_status,r.stars,
                            l.human_summary,l.capabilities_json,l.use_cases_json,l.limitations_json,l.confidence,l.updated_at
                     FROM l2_profiles l JOIN results r ON r.entity_id=l.entity_id
                     ORDER BY l.updated_at DESC LIMIT ?`).all(limit).map(x=>{
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

function resourceById(id) {
  const r = db.prepare(`SELECT * FROM results WHERE entity_id=? OR lower(full_name)=lower(?)`).get(String(id||''), String(id||''));
  if (!r) return null;
  let topics=[]; try { topics=JSON.parse(r.topics_json||'[]'); } catch {}
  const l2raw = db.prepare('SELECT * FROM l2_profiles WHERE entity_id=?').get(r.entity_id) || null;
  let l2 = null;
  if (l2raw) {
    const parse = (v) => { try { return JSON.parse(v || '[]'); } catch { return []; } };
    l2 = {...l2raw, capabilities:parse(l2raw.capabilities_json), use_cases:parse(l2raw.use_cases_json), limitations:parse(l2raw.limitations_json)};
  }
  return {...r, topics, l2};
}

function readJsonSafe(path, fallback=null) {
  try { return JSON.parse(readFileSync(path,'utf8')); } catch { return fallback; }
}
function updateStatusSnapshot() {
  const pending=readJsonSafe(join(dataDir,'pending-deployment.json'),null);
  const lastGood=readJsonSafe(join(dataDir,'last-good-deployment.json'),null);
  const current=readJsonSafe(join(dataDir,'current-deployment.json'),null);
  const runtime=readJsonSafe(join(dataDir,'runtime.json'),null);
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
    audit
  };
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
  if(!force && statusCacheValue && nowMs-statusCacheAt<8000){
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
  const l2Count = Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles').get().n);
  const recent = db.prepare(`SELECT r.full_name,r.description,r.stars,r.language,r.archived,r.fork,r.rate_remaining,r.fetched_at,
                                    r.resource_kind,r.technology,r.content_mode,r.activity_status,r.l1_quality,l.human_summary
                             FROM results r LEFT JOIN l2_profiles l ON l.entity_id=r.entity_id
                             ORDER BY r.fetched_at DESC LIMIT 12`).all();
  const events = db.prepare('SELECT at,level,event,detail FROM events ORDER BY id DESC LIMIT 12').all();
  const control = loadControlSnapshot();
  const levels = JSON.parse(JSON.stringify(control.product || {}));
  if (levels.l1) { levels.l1.count = totalResults; if (totalResults > 0) levels.l1.state = 'CANARY'; }
  if (levels.l2) { levels.l2.count = l2Count; if (l2Count > 0) levels.l2.state = 'CANARY'; }
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
      scheduler_mode:schedulerMode(), deep_backlog:deepBacklogCount(), resource_governor:governorState },
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


const phoneShare={
  server:null,token:null,pairCode:null,startedAt:0,expiresAt:0,durationMinutes:0,
  generation:0,lanAddress:null,baseUrl:null,url:null,port:0,timer:null,monitor:null,
  devices:new Map(),failures:new Map()
};
function lanIpv4(){
  const nets=networkInterfaces(),rows=[];
  const private4=a=>/^10\.|^192\.168\.|^172\.(1[6-9]|2\d|3[01])\./.test(a);
  for(const [name,list] of Object.entries(nets)){
    for(const row of list||[]){
      if(row.family!=='IPv4'||row.internal||!row.address||row.address.startsWith('169.254.'))continue;
      const virtual=/tailscale|vpn|virtual|vethernet|docker|wsl|hyper-v|loopback/i.test(name);
      let score=virtual?100:0;
      score+=private4(row.address)?0:30;
      score+=/wi-?fi|wireless|wlan/i.test(name)?0:/ethernet/i.test(name)?5:20;
      rows.push({address:row.address,name,score});
    }
  }
  rows.sort((a,b)=>a.score-b.score);
  return rows[0]||null;
}
function cookieValue(req,name){
  const raw=String(req.headers.cookie||'');
  for(const part of raw.split(';')){
    const i=part.indexOf('=');
    if(i>0&&part.slice(0,i).trim()===name)return decodeURIComponent(part.slice(i+1).trim());
  }
  return null;
}
function normalizePhoneDuration(v){return [30,90,180].includes(Number(v))?Number(v):90}
function newPairCode(){return String(randomBytes(4).readUInt32BE(0)%100000000).padStart(8,'0')}
function phoneShareFile(){return join(dataDir,'phone_share.json')}
function persistPhoneShareState(){
  const obj={
    version:1,active:!!phoneShare.server,base_url:phoneShare.baseUrl,pair_code:phoneShare.pairCode,
    started_at:phoneShare.startedAt||null,expires_at:phoneShare.expiresAt||null,
    duration_minutes:phoneShare.durationMinutes,generation:phoneShare.generation,
    lan_address:phoneShare.lanAddress,port:phoneShare.port,same_wifi_required:true,
    devices:[...phoneShare.devices.values()].map(x=>({label:x.label,ip:x.ip,last_seen:x.last_seen})).slice(0,12),
    updated_at:now()
  };
  try{writeFileSync(phoneShareFile(),JSON.stringify(obj,null,2),'utf8')}catch{}
}
function refreshPhoneAddress(write=true){
  const lan=lanIpv4();
  if(!phoneShare.server||!phoneShare.token)return lan;
  if(!lan){
    const changed=!!phoneShare.url;
    phoneShare.url=null;phoneShare.baseUrl=null;phoneShare.lanAddress=null;
    if(changed&&write)persistPhoneShareState();
    return null;
  }
  const base='http://'+lan.address+':'+phoneShare.port+'/';
  const next=base+'?pair='+encodeURIComponent(phoneShare.token);
  const changed=next!==phoneShare.url;
  phoneShare.lanAddress=lan.address;phoneShare.baseUrl=base;phoneShare.url=next;
  if(changed&&write)persistPhoneShareState();
  return lan;
}
function phoneStatus(){
  const lan=refreshPhoneAddress(false)||lanIpv4();
  const remaining=phoneShare.expiresAt?Math.max(0,phoneShare.expiresAt-Date.now()):0;
  return {
    ok:true,active:!!phoneShare.server,url:phoneShare.url,base_url:phoneShare.baseUrl,
    pair_code:phoneShare.pairCode,port:phoneShare.port,started_at:phoneShare.startedAt||null,
    expires_at:phoneShare.expiresAt||null,remaining_ms:remaining,duration_minutes:phoneShare.durationMinutes,
    generation:phoneShare.generation,same_wifi_required:true,
    lan:lan?{address:lan.address,adapter:lan.name}:null,
    devices:[...phoneShare.devices.values()].sort((a,b)=>b.last_seen-a.last_seen).slice(0,12)
  };
}
function clearPhoneTimers(){
  if(phoneShare.timer){clearTimeout(phoneShare.timer);phoneShare.timer=null}
  if(phoneShare.monitor){clearInterval(phoneShare.monitor);phoneShare.monitor=null}
}
function stopPhoneShare(){
  clearPhoneTimers();
  const srv=phoneShare.server;
  phoneShare.server=null;phoneShare.token=null;phoneShare.pairCode=null;
  phoneShare.startedAt=0;phoneShare.expiresAt=0;phoneShare.url=null;phoneShare.baseUrl=null;
  phoneShare.lanAddress=null;phoneShare.port=0;phoneShare.devices.clear();phoneShare.failures.clear();
  if(srv){try{srv.close()}catch{}}
  persistPhoneShareState();
  return phoneStatus();
}
function resetPhoneExpiry(minutes){
  phoneShare.durationMinutes=normalizePhoneDuration(minutes);
  phoneShare.expiresAt=Date.now()+phoneShare.durationMinutes*60000;
  if(phoneShare.timer)clearTimeout(phoneShare.timer);
  phoneShare.timer=setTimeout(()=>stopPhoneShare(),Math.max(1000,phoneShare.expiresAt-Date.now()));
  phoneShare.timer.unref?.();
}
function phoneRateLimited(ip){
  const t=Date.now(),old=phoneShare.failures.get(ip)||[],recent=old.filter(x=>t-x<300000);
  phoneShare.failures.set(ip,recent);
  return recent.length>=6;
}
function phoneFailCode(ip){
  const x=phoneShare.failures.get(ip)||[];
  x.push(Date.now());phoneShare.failures.set(ip,x.slice(-8));
}
function phoneRelayHandler(req,res){
  if(!phoneShare.server||Date.now()>=phoneShare.expiresAt){
    res.writeHead(410,{'content-type':'text/plain; charset=utf-8','cache-control':'no-store'});
    return res.end('Session TLIB expirée');
  }
  refreshPhoneAddress(false);
  const u=new URL(req.url||'/',phoneShare.baseUrl||'http://127.0.0.1/');
  const ip=String(req.socket.remoteAddress||'').replace(/^::ffff:/,'');
  const supplied=u.searchParams.get('pair');
  const code=String(u.searchParams.get('code')||'').trim();
  const paired=cookieValue(req,'tlib_pair');
  const validToken=supplied&&supplied===phoneShare.token;
  const validCode=code&&code===phoneShare.pairCode;
  if(validToken||validCode){
    phoneShare.failures.delete(ip);
    res.writeHead(302,{
      'set-cookie':'tlib_pair='+encodeURIComponent(phoneShare.token)+'; Path=/; HttpOnly; SameSite=Strict',
      'location':'/','cache-control':'no-store','referrer-policy':'no-referrer','x-frame-options':'DENY'
    });
    return res.end();
  }
  if(paired!==phoneShare.token){
    if(code&&!validCode)phoneFailCode(ip);
    if(phoneRateLimited(ip)){
      res.writeHead(429,{'content-type':'text/plain; charset=utf-8','cache-control':'no-store'});
      return res.end('Trop de tentatives. Réessaie dans quelques minutes.');
    }
    res.writeHead(401,{
      'content-type':'text/html; charset=utf-8','cache-control':'no-store',
      'referrer-policy':'no-referrer','x-frame-options':'DENY'
    });
    return res.end('<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font:16px system-ui;background:#08111f;color:#eef3fb;display:grid;place-items:center;min-height:100vh;margin:0}.c{width:min(420px,calc(100vw - 28px));padding:24px;border:1px solid #263956;border-radius:18px;background:#101b2d;box-sizing:border-box}h1{font-size:22px;margin:0 0 8px}p{color:#9fb0c8;line-height:1.5}input,button{width:100%;height:46px;border-radius:10px;box-sizing:border-box;font:inherit}input{padding:0 12px;border:1px solid #344967;background:#091321;color:white;margin:8px 0}button{border:0;background:#5b8cff;color:white;font-weight:700}</style><div class="c"><h1>TLIB</h1><p>Scanne le QR affiché sur le PC, ou saisis le code temporaire. Le téléphone et le PC doivent être sur le même réseau local.</p><form><input name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="Code temporaire"><button>Ouvrir TLIB</button></form></div>');
  }
  const ua=String(req.headers['user-agent']||'Appareil');
  phoneShare.devices.set(ip,{
    id:ip,label:/Android/i.test(ua)?'Téléphone Android':/iPhone|iPad/i.test(ua)?'iPhone / iPad':'Navigateur',
    ip,last_seen:Date.now(),user_agent:ua.slice(0,180)
  });
  const headers={...req.headers,host:'127.0.0.1:'+DASHBOARD_PORT};
  delete headers['accept-encoding'];delete headers.cookie;
  const proxy=http.request({hostname:'127.0.0.1',port:DASHBOARD_PORT,path:req.url||'/',method:req.method,headers},up=>{
    const out={...up.headers};
    delete out['content-security-policy'];
    res.writeHead(up.statusCode||502,out);up.pipe(res);
  });
  proxy.on('error',()=>{
    if(!res.headersSent)res.writeHead(502,{'content-type':'text/plain; charset=utf-8'});
    res.end('TLIB local indisponible');
  });
  req.pipe(proxy);
}
async function listenPhoneRelay(){
  for(let port=8831;port<=8835;port++){
    const relay=http.createServer(phoneRelayHandler);
    const result=await new Promise(resolve=>{
      const onError=e=>resolve({ok:false,error:e});
      relay.once('error',onError);
      relay.listen(port,'0.0.0.0',()=>{
        relay.off('error',onError);resolve({ok:true,relay,port});
      });
    });
    if(result.ok)return result;
    try{relay.close()}catch{}
    if(result.error?.code!=='EADDRINUSE')return result;
  }
  return {ok:false,error:new Error('NO_TLIB_PHONE_PORT_AVAILABLE')};
}
async function startPhoneShare(minutes=90){
  if(phoneShare.server)stopPhoneShare();
  const lan=lanIpv4();
  if(!lan)return {ok:false,state:'NO_LAN_IPV4'};
  phoneShare.token=randomBytes(12).toString('base64url');
  phoneShare.pairCode=newPairCode();phoneShare.startedAt=Date.now();phoneShare.generation++;
  const listened=await listenPhoneRelay();
  if(!listened.ok){
    stopPhoneShare();
    return {ok:false,state:'PHONE_PORT_UNAVAILABLE',error:String(listened.error?.message||listened.error)};
  }
  phoneShare.server=listened.relay;phoneShare.port=listened.port;
  resetPhoneExpiry(minutes);refreshPhoneAddress(false);
  phoneShare.server.on('error',()=>stopPhoneShare());
  phoneShare.monitor=setInterval(()=>refreshPhoneAddress(true),10000);
  phoneShare.monitor.unref?.();
  persistPhoneShareState();
  event('INFO','PHONE_SHARE_ACTIVE','port='+phoneShare.port+'; minutes='+phoneShare.durationMinutes);
  return {ok:true,state:'PHONE_SHARE_ACTIVE',...phoneStatus()};
}
function extendPhoneShare(minutes){
  if(!phoneShare.server)return {ok:false,state:'PHONE_SHARE_INACTIVE'};
  resetPhoneExpiry(minutes);persistPhoneShareState();
  event('INFO','PHONE_SHARE_EXTENDED','minutes='+phoneShare.durationMinutes);
  return {ok:true,state:'PHONE_SHARE_EXTENDED',...phoneStatus()};
}
function rotatePhoneShare(){
  if(!phoneShare.server)return {ok:false,state:'PHONE_SHARE_INACTIVE'};
  phoneShare.token=randomBytes(12).toString('base64url');
  phoneShare.pairCode=newPairCode();phoneShare.generation++;
  phoneShare.devices.clear();phoneShare.failures.clear();refreshPhoneAddress(false);persistPhoneShareState();
  event('INFO','PHONE_SHARE_ROTATED','generation='+phoneShare.generation);
  return {ok:true,state:'PHONE_SHARE_ROTATED',...phoneStatus()};
}
function readJsonBody(req,max=16384){
  return new Promise((resolveBody,rejectBody)=>{
    let raw='';
    req.setEncoding('utf8');
    req.on('data',chunk=>{
      raw+=chunk;
      if(raw.length>max){rejectBody(new Error('BODY_TOO_LARGE'));try{req.destroy()}catch{}}
    });
    req.on('end',()=>{
      if(!raw)return resolveBody({});
      try{resolveBody(JSON.parse(raw))}catch{rejectBody(new Error('INVALID_JSON'))}
    });
    req.on('error',rejectBody);
  });
}

function sendJson(res, code, value) {
  res.writeHead(code, {'content-type':'application/json; charset=utf-8','cache-control':'no-store'});
  res.end(JSON.stringify(value));
}

async function startDashboard() {
  const port = DASHBOARD_PORT;
  let busy = false;
  const server = http.createServer(async (req,res) => {
    const u = new URL(req.url || '/', 'http://127.0.0.1');
    markInteractiveRequest(u.pathname);
    try {
      if (u.pathname === '/api/interaction' && req.method === 'POST') return sendJson(res,200,{ok:true});
      if (u.pathname === '/api/phone/share' && req.method === 'GET') return sendJson(res,200,phoneStatus());
      if (u.pathname === '/api/phone/share' && req.method === 'POST') {
        const body=await readJsonBody(req);
        const action=String(body.action||'status');
        let out;
        if(action==='start') out=await startPhoneShare(body.minutes);
        else if(action==='extend') out=extendPhoneShare(body.minutes);
        else if(action==='rotate') out=rotatePhoneShare();
        else if(action==='stop') out={ok:true,state:'PHONE_SHARE_STOPPED',...stopPhoneShare()};
        else out=phoneStatus();
        return sendJson(res,out.ok===false?409:200,out);
      }
      if (u.pathname === '/api/status') return sendJson(res,200,statusSnapshot());
      if (u.pathname === '/api/version') return sendJson(res,200,{product:'TLIB',build:APP_BUILD,pid:process.pid,node:process.versions.node});
      if (u.pathname === '/api/library') {
        const q=u.searchParams.get('q')||'', limit=u.searchParams.get('limit')||100,
              offset=u.searchParams.get('offset')||0, sort=u.searchParams.get('sort')||'stars';
        return sendJson(res,200,{items:libraryRows(q,limit,offset,sort),total:libraryCount(q),limit:Number(limit),offset:Number(offset),sort});
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
      if (u.pathname === '/api/facets') return sendJson(res,200,facetsSnapshot());
      if (u.pathname === '/api/l1/stats') return sendJson(res,200,l1Stats());
      if (u.pathname === '/api/l2/list') return sendJson(res,200,{items:l2Rows(u.searchParams.get('limit')||100)});
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
      if (u.pathname === '/vendor-qrcode.min.js') {
        const qr=readFileSync(join(ROOT,'public','vendor-qrcode.min.js'));
        res.writeHead(200,{'content-type':'application/javascript; charset=utf-8','cache-control':'public, max-age=86400'});
        return res.end(qr);
      }
      const page = readFileSync(join(ROOT,'public','index.html'),'utf8');
      res.writeHead(200, {'content-type':'text/html; charset=utf-8','cache-control':'no-store'});
      res.end(page);
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
  server.listen(port, '127.0.0.1', () => {
    writeRuntimeMarker();
    event('INFO','DASHBOARD_STARTED','127.0.0.1:' + port + '; build=' + APP_BUILD + '; commit=' + APP_COMMIT);
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
        const mode=schedulerMode();
        if(mode==='DEEP_CATCHUP'){
          const deep=await deepL1Step();
          if(!deep.done && (deep.state==='EMPTY' || deep.state==='NO_AUTH')) await autopilotPublicStep();
        }else if(mode==='BALANCED_DEEP_FIRST'){
          if(coreSinceDeep>=4){
            coreSinceDeep=0;
            const deep=await deepL1Step();
            if(!deep.done && deep.state!=='RESERVE_RATE') await autopilotPublicStep();
          }else{
            await autopilotPublicStep();
          }
        }else{
          const core=await autopilotPublicStep();
          if(core.done && coreSinceDeep>=20){coreSinceDeep=0;await deepL1Step();}
        }
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
  if (cmd === 'canary') return canary(Number(argValue('--limit', '10')));
  if (cmd === 'fixture-canary') return fixtureCanary();
  if (cmd === 'fixture-l2') return fixtureL2Canary();
  if (cmd === 'dashboard') return startDashboard();
  if (cmd === 'worker') {
    selftest();
    seed();
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
    return;
  }
  throw new Error('UNKNOWN_COMMAND ' + cmd);
}

main().catch(e => {
  try { event('FATAL','PROCESS_ERROR',e.stack || e.message); } catch {}
  console.error(e.stack || e.message);
  process.exitCode = 1;
});
