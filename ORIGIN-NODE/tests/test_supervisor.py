import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from origin.supervisor import take_lock,AlreadyRunning,rotate_log

class Supervisor(unittest.TestCase):
    def test_duplicate_supervisor_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'lock';fd=take_lock(p)
            try:
                with self.assertRaises(AlreadyRunning):take_lock(p)
            finally:os.close(fd)
    def test_lock_released_on_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'lock';fd=take_lock(p);os.close(fd)
            new=take_lock(p);os.close(new)
    def test_lock_released_after_sigkill(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'lock'
            code='import sys,time;from origin.supervisor import take_lock;f=take_lock(sys.argv[1]);print("READY",flush=True);time.sleep(30)'
            child=subprocess.Popen([sys.executable,'-c',code,str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                self.assertEqual(child.stdout.readline().strip(),'READY')
                with self.assertRaises(AlreadyRunning):take_lock(p)
                child.kill();child.wait(timeout=4)
                fd=take_lock(p);os.close(fd)
            finally:
                if child.poll() is None:child.kill();child.wait()
                child.stdout.close();child.stderr.close()
    def test_log_rotation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.log';p.write_text('a'*120)
            rotate_log(p,max_bytes=100)
            self.assertFalse(p.exists());self.assertTrue((Path(tmp)/'a.log.1').exists())
if __name__=='__main__':unittest.main()
