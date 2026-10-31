"""Durable, bounded, idempotent job queue. No dynamic shell/code execution."""
from __future__ import annotations
import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path

MAX_JOBS=1000
MAX_HISTORY=20000
MAX_PAYLOAD=4096
KINDS={'sha256','word_count','upper'}

class Queue:
    def __init__(self,path):
        self.path=str(path)
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        self.guard=threading.RLock()
        self.db=sqlite3.connect(self.path,timeout=20,check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA busy_timeout=10000')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS jobs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          idem TEXT UNIQUE NOT NULL,
          kind TEXT NOT NULL,
          payload TEXT NOT NULL,
          state TEXT NOT NULL,
          attempts INTEGER NOT NULL DEFAULT 0,
          result TEXT,
          error TEXT,
          created REAL NOT NULL,
          touched REAL NOT NULL,
          lease_until REAL
        )''')
        columns={r[1] for r in self.db.execute('PRAGMA table_info(jobs)')}
        if 'lease_until' not in columns:
            self.db.execute('ALTER TABLE jobs ADD COLUMN lease_until REAL')
        self.db.execute('CREATE INDEX IF NOT EXISTS ix_jobs_state_id ON jobs(state,id)')
        self.db.commit()
    def close(self):
        with self.guard:self.db.close()
    def submit(self,kind,payload,idem):
        if kind not in KINDS: raise ValueError('unknown kind')
        if not isinstance(payload,str) or len(payload.encode())>MAX_PAYLOAD: raise ValueError('payload limit 4096 bytes')
        if not isinstance(idem,str) or not (8<=len(idem)<=128):raise ValueError('idempotency key length 8..128')
        with self.guard:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                row=self.db.execute('SELECT * FROM jobs WHERE idem=?',(idem,)).fetchone()
                if row:
                    if row['kind']!=kind or row['payload']!=payload:
                        raise ValueError('idempotency conflict')
                else:
                    count=self.db.execute("SELECT count(*) FROM jobs WHERE state IN ('queued','running')").fetchone()[0]
                    total=self.db.execute('SELECT count(*) FROM jobs').fetchone()[0]
                    if count>=MAX_JOBS: raise OverflowError('queue saturated')
                    if total>=MAX_HISTORY: raise OverflowError('history full; export and archive required')
                    now=time.time()
                    self.db.execute("INSERT INTO jobs(idem,kind,payload,state,created,touched) VALUES(?,?,?,'queued',?,?)",(idem,kind,payload,now,now))
                    row=self.db.execute('SELECT * FROM jobs WHERE idem=?',(idem,)).fetchone()
                self.db.commit()
                return dict(row)
            except Exception:
                self.db.rollback()
                raise
    def claim(self, lease_seconds=30):
        with self.guard:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                row=self.db.execute("SELECT * FROM jobs WHERE state='queued' ORDER BY id LIMIT 1").fetchone()
                if row:
                    now=time.time()
                    self.db.execute("UPDATE jobs SET state='running',attempts=attempts+1,touched=?,lease_until=? WHERE id=?",(now,now+lease_seconds,row['id']))
                    row=self.db.execute('SELECT * FROM jobs WHERE id=?',(row['id'],)).fetchone()
                self.db.commit()
                return dict(row) if row else None
            except Exception:
                self.db.rollback();raise
    def finish(self,jobid,result=None,error=None,expected_attempt=None):
        state='failed' if error else 'done'
        with self.guard:
            if expected_attempt is None:
                query="UPDATE jobs SET state=?,result=?,error=?,touched=?,lease_until=NULL WHERE id=? AND state='running'"
                values=(state,result,error,time.time(),jobid)
            else:
                query="UPDATE jobs SET state=?,result=?,error=?,touched=?,lease_until=NULL WHERE id=? AND state='running' AND attempts=?"
                values=(state,result,error,time.time(),jobid,expected_attempt)
            cur=self.db.execute(query,values)
            self.db.commit()
            return cur.rowcount==1
    def requeue_expired(self, now=None):
        # Safe for built-in PURE handlers. Never use automatic retries for external side effects.
        now=time.time() if now is None else now
        with self.guard:
            cur=self.db.execute("UPDATE jobs SET state='queued',touched=?,lease_until=NULL WHERE state='running' AND lease_until IS NOT NULL AND lease_until<=?",(now,now))
            self.db.commit()
            return cur.rowcount
    def recover(self):
        # Exactly-once external side effects are NOT guaranteed. Handlers here are pure.
        with self.guard:
            r=self.db.execute("UPDATE jobs SET state='queued',touched=?,lease_until=NULL WHERE state='running'",(time.time(),))
            self.db.commit()
            return r.rowcount
    def get(self,jobid):
        with self.guard:
            r=self.db.execute('SELECT id,kind,state,attempts,result,error,created,touched FROM jobs WHERE id=?',(jobid,)).fetchone()
            return dict(r) if r else None
    def stats(self):
        with self.guard:
            rows=self.db.execute('SELECT state,count(*) AS n FROM jobs GROUP BY state').fetchall()
            return {r['state']:r['n'] for r in rows}
    def check(self):
        with self.guard:return self.db.execute('PRAGMA quick_check').fetchone()[0]
    def backup(self, outpath):
        with self.guard:
            d=sqlite3.connect(str(outpath))
            try:self.db.backup(d)
            finally:d.close()

def run_task(job):
    value=job['payload']
    if job['kind']=='sha256':return hashlib.sha256(value.encode()).hexdigest()
    if job['kind']=='word_count':return json.dumps({'words':len(value.split()),'bytes':len(value.encode())})
    if job['kind']=='upper':return value.upper()
    raise ValueError('invalid job kind')

class Worker(threading.Thread):
    def __init__(self,queue,stop_event):
        super().__init__(daemon=True)
        self.queue=queue;self.stop_event=stop_event
    def run(self):
        while not self.stop_event.is_set():
            self.queue.requeue_expired()
            j=self.queue.claim()
            if j is None:
                self.stop_event.wait(.25)
                continue
            try:self.queue.finish(j['id'],result=run_task(j),expected_attempt=j['attempts'])
            except Exception as exc:self.queue.finish(j['id'],error=str(exc)[:500],expected_attempt=j['attempts'])
