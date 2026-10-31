"""Fault injection exercises software-level state continuity, not phone reliability."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from origin.core import Queue, run_task

class Chaos(unittest.TestCase):
    def test_sigkill_recovery(self):
        with tempfile.TemporaryDirectory() as t:
            db=str(Path(t)/'powercut.db')
            q=Queue(db);j=q.submit('upper','resume','chaos-run-001');q.close()
            code="from origin.core import Queue;import sys,time;q=Queue(sys.argv[1]);j=q.claim();print('CLAIMED',flush=True);time.sleep(100)"
            p=subprocess.Popen([sys.executable,'-c',code,db],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                self.assertEqual(p.stdout.readline().strip(),'CLAIMED')
                p.kill();p.wait(timeout=5)
                q=Queue(db)
                self.assertEqual(q.get(j['id'])['state'],'running')
                self.assertEqual(q.recover(),1)
                job=q.claim();self.assertEqual(job['id'],j['id'])
                q.finish(j['id'],run_task(job));self.assertEqual(q.get(j['id'])['result'],'RESUME')
                self.assertEqual(q.check(),'ok');q.close()
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=5)
                p.stdout.close();p.stderr.close()
    def test_burst_300_jobs(self):
        with tempfile.TemporaryDirectory() as t:
            q=Queue(Path(t)/'burst.db')
            try:
                for i in range(300):q.submit('word_count',f'num {i}',f'burst-test-{i:05d}')
                for i in range(300):
                    job=q.claim();self.assertIsNotNone(job)
                    q.finish(job['id'],run_task(job))
                self.assertEqual(q.stats()['done'],300)
                self.assertEqual(q.check(),'ok')
            finally:q.close()
