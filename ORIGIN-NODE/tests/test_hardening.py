"""Adversarial non-device tests for ORIGIN 0.2."""
import concurrent.futures
import http.client
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from origin.core import Queue, MAX_JOBS
from origin.server import AppServer

class Hardening(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'data.db'
        self.q=Queue(self.path)
    def tearDown(self):
        self.q.close();self.temp.cleanup()
    def test_attempt_fence_does_not_overwrite_recovered_result(self):
        j=self.q.submit('upper','alpha','fence-test-0001')
        old=self.q.claim()
        self.assertEqual(old['attempts'],1)
        self.assertEqual(self.q.requeue_expired(old['lease_until']+1),1)
        new=self.q.claim()
        self.assertEqual(new['attempts'],2)
        self.assertFalse(self.q.finish(j['id'],result='STALE',expected_attempt=1))
        self.assertTrue(self.q.finish(j['id'],result='FRESH',expected_attempt=2))
        self.assertEqual(self.q.get(j['id'])['result'],'FRESH')
    def test_expiry_does_not_requeue_healthy_claim(self):
        self.q.submit('upper','alpha','lease-test-0001')
        job=self.q.claim(lease_seconds=60)
        self.assertEqual(self.q.requeue_expired(job['lease_until']-1),0)
        self.assertEqual(self.q.get(job['id'])['state'],'running')
    def test_expiry_then_reclaim(self):
        self.q.submit('upper','alpha','lease-test-0001')
        old=self.q.claim(lease_seconds=0.01)
        self.assertEqual(self.q.requeue_expired(old['lease_until']+1),1)
        self.assertEqual(self.q.claim()['attempts'],2)
    def test_recovery_does_not_recover_completed(self):
        job=self.q.submit('upper','alpha','lease-test-0001');old=self.q.claim()
        self.q.finish(job['id'],result='ALPHA',expected_attempt=old['attempts'])
        self.assertEqual(self.q.recover(),0)
        self.assertEqual(self.q.get(job['id'])['result'],'ALPHA')
    def test_sql_injection_remains_literal(self):
        evil="'); DROP TABLE jobs; --"
        self.q.submit('upper',evil,'safe-key-0001')
        self.assertEqual(self.q.check(),'ok')
        self.assertEqual(self.q.stats()['queued'],1)
    def test_parallel_distinct_submits(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            rows=list(pool.map(lambda i:self.q.submit('upper',str(i),f'parallel-{i:05d}'),range(200)))
        self.assertEqual(len({x['id'] for x in rows}),200)
    def test_queue_capacity_rejection_and_readable_db(self):
        for i in range(MAX_JOBS):self.q.submit('sha256','x',f'capacity-{i:05d}')
        with self.assertRaises(OverflowError):self.q.submit('sha256','x','capacity-over')
        self.assertEqual(self.q.check(),'ok')
    def test_non_destructive_upgrade_legacy_schema(self):
        self.q.close();self.path.unlink()
        db=sqlite3.connect(str(self.path))
        db.execute('''CREATE TABLE jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,idem TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL,state TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,result TEXT,error TEXT,created REAL NOT NULL,touched REAL NOT NULL)''')
        db.execute('''INSERT INTO jobs(idem,kind,payload,state,created,touched) VALUES('old-item-001','upper','preserved','queued',1,1)''')
        db.commit();db.close();self.q=Queue(self.path)
        self.assertEqual(self.q.get(1)['state'],'queued')
        self.assertIn('lease_until',{r[1] for r in self.q.db.execute('PRAGMA table_info(jobs)')})
    def test_backup_keeps_completed_results(self):
        j=self.q.submit('upper','test','backup-test-001');a=self.q.claim();self.q.finish(j['id'],result='TEST',expected_attempt=a['attempts'])
        outfile=Path(self.temp.name)/'safe-copy.db';self.q.backup(outfile)
        db=sqlite3.connect(outfile)
        self.assertEqual(db.execute('SELECT result FROM jobs WHERE id=?',(j['id'],)).fetchone()[0],'TEST');db.close()
    def test_loopback_binding(self):
        srv=AppServer(('127.0.0.1',0),self.q,'X'*48)
        try:self.assertEqual(srv.server_address[0],'127.0.0.1')
        finally:srv.server_close()
    def test_unknown_verb_no_shell(self):
        srv=AppServer(('127.0.0.1',0),self.q,'X'*48)
        thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
        try:
            conn=http.client.HTTPConnection('127.0.0.1',srv.server_address[1],timeout=2)
            conn.request('PUT','/jobs',body='{}',headers={'Authorization':'Bearer '+'X'*48})
            response=conn.getresponse();self.assertIn(response.status,(405,501));conn.close()
        finally:srv.shutdown();srv.server_close();thread.join()
if __name__=='__main__':unittest.main()
