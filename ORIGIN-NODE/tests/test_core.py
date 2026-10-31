import json
import tempfile
import unittest
from pathlib import Path
from origin.core import Queue,run_task,MAX_PAYLOAD,Worker
import threading
import time

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.dbpath=Path(self.tmp.name)/'queue.db';self.q=Queue(self.dbpath)
    def tearDown(self):self.q.close();self.tmp.cleanup()
    def test_submit_and_complete(self):
        j=self.q.submit('upper','abc','repeat-00001');claimed=self.q.claim()
        self.assertEqual(claimed['id'],j['id']);self.q.finish(j['id'],run_task(claimed))
        self.assertEqual(self.q.get(j['id'])['result'],'ABC')
    def test_dedup(self):
        a=self.q.submit('sha256','abc','repeat-00001')
        b=self.q.submit('sha256','abc','repeat-00001')
        self.assertEqual(a['id'],b['id']);self.assertEqual(self.q.stats(),{'queued':1})
    def test_conflicting_idem(self):
        self.q.submit('upper','abc','repeat-00001')
        with self.assertRaisesRegex(ValueError,'conflict'):self.q.submit('upper','abcd','repeat-00001')
    def test_queue_persistence(self):
        a=self.q.submit('word_count','un deux','repeat-00001');self.q.close()
        self.q=Queue(self.dbpath);self.assertEqual(self.q.get(a['id'])['state'],'queued')
    def test_restart_recovery(self):
        a=self.q.submit('word_count','un deux','repeat-00001');self.q.claim();self.q.close()
        self.q=Queue(self.dbpath);self.assertEqual(self.q.recover(),1)
        job=self.q.claim();self.assertEqual(job['id'],a['id']);self.assertEqual(job['attempts'],2)
    def test_integrity(self):self.assertEqual(self.q.check(),'ok')
    def test_wrong_kind(self):
        with self.assertRaises(ValueError):self.q.submit('shell','rm -rf /','repeat-00001')
    def test_payload_limit(self):
        with self.assertRaises(ValueError):self.q.submit('upper','a'*(MAX_PAYLOAD+1),'repeat-00001')
    def test_key_length(self):
        with self.assertRaises(ValueError):self.q.submit('upper','abc','x')
    def test_no_pending(self):self.assertIsNone(self.q.claim())
    def test_word_count(self):
        r=run_task({'kind':'word_count','payload':'mot mot  ok'})
        self.assertEqual(json.loads(r)['words'],3)
    def test_hash(self):self.assertEqual(len(run_task({'kind':'sha256','payload':'test'})),64)
    def test_backup(self):
        self.q.submit('upper','abc','repeat-00001');dest=Path(self.tmp.name)/'backup.db';self.q.backup(dest)
        q2=Queue(dest)
        try:self.assertEqual(q2.stats()['queued'],1)
        finally:q2.close()
    def test_worker(self):
        j=self.q.submit('upper','foo','repeat-00001');evt=threading.Event();w=Worker(self.q,evt);w.start()
        for _ in range(100):
            if self.q.get(j['id'])['state']=='done':break
            time.sleep(.02)
        evt.set();w.join(2);self.assertEqual(self.q.get(j['id'])['state'],'done')
    def test_threadsafe_idempotency(self):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda _:self.q.submit('upper','abc','repeat-00001')['id'],range(40)))
        self.assertEqual(len(set(results)),1)
if __name__=='__main__':unittest.main()
