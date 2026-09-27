import http from 'node:http';
import { mkdirSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..');
const dataDir = process.env.TLIB_DATA_DIR || join(process.env.LOCALAPPDATA || homedir(), 'TLIB-PC');
mkdirSync(dataDir, { recursive: true });
const dbPath = join(dataDir, 'tlib-worker.sqlite3');
const db = new DatabaseSync(dbPath);
db.exec(`
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
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

const now = () => new Date().toISOString();
const event = (level, name, detail='') => {
  db.prepare('INSERT INTO events(at,level,event,detail) VALUES(?,?,?,?)').run(now(), level, name, String(detail).slice(0,2000));
};

function argValue(prefix, fallback) {
  const a = process.argv.find(x => x.startsWith(prefix + '='));
  return a ? a.slice(prefix.length + 1) : fallback;
}

function entityId(fullName) {
  return 'ghpath:' + fullName.toLowerCase();
}

function classifyL1(x) {
  const full = String(x.full_name || '');
  const name = String(x.name || full.split('/').pop() || '').toLowerCase();
  const desc = String(x.description || '').toLowerCase();
  const topics = Array.isArray(x.topics) ? x.topics.map(v => String(v).toLowerCase()) : [];
  const isList = name.startsWith('awesome') || topics.includes('awesome-list') || topics.includes('list') ||
    /curated list|collection of resources|resources for|bookmarks/.test(desc);
  let kind = isList ? 'Catalogue de ressources' : (x.fork ? 'Fork de projet' : 'Projet logiciel');

  const candidates = topics.filter(t => !['awesome','awesome-list','list','lists','resources'].includes(t));
  let technology = '';
  const preferred = ['electron','android-development','android-library','android','ios','react-native','react','nodejs','node','cordova','frontend','iot','swift'];
  for (const p of preferred) if (candidates.includes(p)) { technology = p; break; }
  if (!technology && name === 'awesome') technology = 'Multi-thèmes';
  if (!technology && name.startsWith('awesome-')) technology = name.slice(8).replace(/-/g,' ');
  if (!technology && candidates.length && !candidates.includes('unicorns')) technology = candidates[0];
  if (!technology && x.language) technology = String(x.language);

  const contentMode = isList && !x.language ? 'Documentation / liens' :
    (x.language ? 'Code + documentation (' + x.language + ')' : 'Contenu à préciser');

  let activityDays = null, activityStatus = 'Activité inconnue';
  const pushed = Date.parse(String(x.pushed_at || ''));
  if (Number.isFinite(pushed)) {
    activityDays = Math.max(0, Math.floor((Date.now() - pushed) / 86400000));
    activityStatus = activityDays <= 180 ? 'Actif récemment' :
      activityDays <= 730 ? 'Activité modérée' : 'Peu actif / ancien';
  }
  const quality = x.id && full ? 'Identité GitHub vérifiée' : 'Vérification partielle';
  return {kind, technology, contentMode, activityStatus, activityDays, quality};
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
  if (process.env.GH_TOKEN) headers.Authorization = 'Bearer ' + process.env.GH_TOKEN;
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
  if (res.status === 404) return { status: 404, body, remaining };
  if (!res.ok) {
    const e = new Error('GITHUB_HTTP_' + res.status + ' ' + String(body.message || '').slice(0,300));
    e.code = res.status >= 500 ? 'RETRY' : 'HTTP';
    throw e;
  }
  return { status: res.status, body, remaining };
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

function fixtureCanary() {
  seed();
  const files = ['l1-fixture-10.json','l1-batch-a.json','l1-batch-b.json','l1-batch-c.json','l1-batch-d.json','l1-batch-e.json'];
  const byName = new Map();
  for (const file of files) {
    try {
      const rows = JSON.parse(readFileSync(join(ROOT, 'config', file), 'utf8'));
      for (const x of rows) if (x && x.full_name) byName.set(String(x.full_name).toLowerCase(), x);
    } catch {}
  }
  const fixture = [...byName.values()];
  let done = 0;
  for (const x of fixture) {
    const fullName = String(x.full_name || '');
    const id = entityId(fullName);
    db.prepare(`INSERT OR IGNORE INTO jobs(entity_id,full_name,status,attempts,updated_at)
                VALUES(?,?,'PENDING',0,?)`).run(id, fullName, now());
    const topics = Array.isArray(x.topics) ? x.topics : [];
    const q = classifyL1(x);
    db.prepare(`INSERT OR REPLACE INTO results(
      entity_id,full_name,http_status,github_id,node_id,description,archived,fork,stars,language,license,
      topics_json,updated_at_github,pushed_at,default_branch,size_kb,open_issues,rate_remaining,fetched_at,raw_json,
      resource_kind,technology,content_mode,activity_status,activity_days,l1_quality
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).run(
      id, fullName, 200, String(x.id ?? ''), String(x.node_id ?? ''), String(x.description ?? ''),
      x.archived ? 1 : 0, x.fork ? 1 : 0, Number(x.stargazers_count ?? 0), String(x.language ?? ''),
      String(x.license?.spdx_id ?? x.license?.name ?? ''), JSON.stringify(topics), String(x.updated_at ?? ''),
      String(x.pushed_at ?? ''), String(x.default_branch ?? ''), Number(x.size ?? 0), Number(x.open_issues_count ?? 0),
      -1, now(), JSON.stringify(x), q.kind, q.technology, q.contentMode, q.activityStatus, q.activityDays, q.quality
    );
    db.prepare(`UPDATE jobs SET status='DONE', last_error=NULL, updated_at=? WHERE entity_id=?`).run(now(), id);
    done++;
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

function libraryRows(q='', limit=100) {
  q = String(q || '').trim().toLowerCase();
  limit = Math.max(1, Math.min(Number(limit || 100), 500));
  if (!q) {
    return db.prepare(`SELECT entity_id,full_name,description,stars,language,license,topics_json,archived,fork,
                              updated_at_github,pushed_at,default_branch,size_kb,open_issues,fetched_at,
                              resource_kind,technology,content_mode,activity_status,activity_days,l1_quality
                       FROM results ORDER BY stars DESC LIMIT ?`).all(limit);
  }
  const like = '%' + q + '%';
  return db.prepare(`SELECT entity_id,full_name,description,stars,language,license,topics_json,archived,fork,
                            updated_at_github,pushed_at,default_branch,size_kb,open_issues,fetched_at,
                            resource_kind,technology,content_mode,activity_status,activity_days,l1_quality
                     FROM results
                     WHERE lower(full_name) LIKE ? OR lower(description) LIKE ? OR lower(language) LIKE ?
                        OR lower(license) LIKE ? OR lower(topics_json) LIKE ?
                     ORDER BY stars DESC LIMIT ?`).all(like,like,like,like,like,limit);
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

function statusSnapshot() {
  const counts = {};
  for (const r of db.prepare('SELECT status, COUNT(*) AS n FROM jobs GROUP BY status').all()) counts[r.status] = Number(r.n);
  const totalResults = Number(db.prepare('SELECT COUNT(*) AS n FROM results').get().n);
  const l2Count = Number(db.prepare('SELECT COUNT(*) AS n FROM l2_profiles').get().n);
  const recent = db.prepare(`SELECT full_name,description,stars,language,archived,fork,rate_remaining,fetched_at,
                                    resource_kind,technology,content_mode,activity_status,l1_quality
                             FROM results ORDER BY fetched_at DESC LIMIT 12`).all();
  const events = db.prepare('SELECT at,level,event,detail FROM events ORDER BY id DESC LIMIT 12').all();
  const control = loadControlSnapshot();
  const levels = JSON.parse(JSON.stringify(control.product || {}));
  if (levels.l1) { levels.l1.count = totalResults; if (totalResults > 0) levels.l1.state = 'CANARY'; }
  if (levels.l2) { levels.l2.count = l2Count; if (l2Count > 0) levels.l2.state = 'CANARY'; }
  return {
    product: 'TLIB',
    mode: 'HYBRID_V2_LAB',
    pc_worker: { online:true, database:dbPath, local_l1_results:totalResults, local_l2_profiles:l2Count, queue:counts },
    apps_script: control.engine || {},
    levels,
    recent,
    events
  };
}

function sendJson(res, code, value) {
  res.writeHead(code, {'content-type':'application/json; charset=utf-8','cache-control':'no-store'});
  res.end(JSON.stringify(value));
}

async function startDashboard() {
  const port = Number(process.env.TLIB_DASHBOARD_PORT || 8787);
  let busy = false;
  const server = http.createServer(async (req,res) => {
    const u = new URL(req.url || '/', 'http://127.0.0.1');
    try {
      if (u.pathname === '/api/status') return sendJson(res,200,statusSnapshot());
      if (u.pathname === '/api/library') return sendJson(res,200,{items:libraryRows(u.searchParams.get('q')||'',u.searchParams.get('limit')||100)});
      if (u.pathname === '/api/resource') {
        const item=resourceById(u.searchParams.get('id')||'');
        return item ? sendJson(res,200,item) : sendJson(res,404,{error:'NOT_FOUND'});
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
      if (u.pathname === '/api/health') return sendJson(res,200,{ok:true,at:now()});
      const page = readFileSync(join(ROOT,'public','index.html'),'utf8');
      res.writeHead(200, {'content-type':'text/html; charset=utf-8','cache-control':'no-store'});
      res.end(page);
    } catch (e) {
      event('ERROR','HTTP_ERROR',e.message || String(e));
      sendJson(res,500,{error:'LOCAL_SERVER_ERROR',message:String(e.message||e)});
    }
  });
  server.listen(port, '127.0.0.1', () => {
    event('INFO','DASHBOARD_STARTED','127.0.0.1:' + port);
    console.log('TLIB dashboard: http://127.0.0.1:' + port);
  });
  return server;
}

async function main() {
  const cmd = process.argv[2] || 'selftest';
  if (cmd === 'selftest') return selftest();
  if (cmd === 'seed') return seed();
  if (cmd === 'canary') return canary(Number(argValue('--limit', '10')));
  if (cmd === 'fixture-canary') return fixtureCanary();
  if (cmd === 'fixture-l2') return fixtureL2Canary();
  if (cmd === 'dashboard') return startDashboard();
  if (cmd === 'agent') {
    selftest();
    seed();
    startDashboard();
    if (process.env.TLIB_AUTO_WORK === '1') await canary(Number(process.env.TLIB_AUTO_LIMIT || 10));
    return;
  }
  throw new Error('UNKNOWN_COMMAND ' + cmd);
}

main().catch(e => {
  try { event('FATAL','PROCESS_ERROR',e.stack || e.message); } catch {}
  console.error(e.stack || e.message);
  process.exitCode = 1;
});
