import hashlib, json, tempfile, time, threading, unittest, http.client, secrets
from pathlib import Path
from http.server import ThreadingHTTPServer
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"windows"))
from bridge_agent import Bridge, compact, handler_factory

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.b=Bridge(root/'state',root/'work','ab'*32)
        self.http=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(self.b))
        self.t=threading.Thread(target=lambda: self.http.serve_forever(poll_interval=0.02),daemon=True);self.t.start()
    def tearDown(self):
        self.http.shutdown();self.http.server_close();self.t.join(timeout=2);self.tmp.cleanup()
    def request(self, path='/v1/status',payload=None,nonce=None,sign=True,age=0, bad_mac=False):
        body=compact(payload or {})
        ts=str(int(time.time())+age)
        nonce=nonce or secrets.token_hex(12)
        digest=hashlib.sha256(body).hexdigest()
        sig=self.b.sig(f'POST\n{path}\n{ts}\n{nonce}\n{digest}') if sign else ''
        if bad_mac: sig='f'*64
        con=http.client.HTTPConnection('127.0.0.1',self.http.server_port,timeout=4)
        con.request('POST',path,body,{'Content-Type':'application/json','X-Bridge-Time':ts,
                     'X-Bridge-Nonce':nonce,'X-Bridge-Signature':sig})
        res=con.getresponse();raw=res.read(); signature=res.getheader('X-Bridge-Signature');status=res.status;con.close()
        self.assertEqual(signature,self.b.sig(f'{nonce}\n{status}\n{hashlib.sha256(raw).hexdigest()}'))
        return status,json.loads(raw)
    def test_status(self):
        code,r=self.request();self.assertEqual(code,200);self.assertEqual('BCP_USB_RESCUE_R1',r['result']['agent'])
    def test_diagnostics(self):
        code,r=self.request('/v1/diagnostics');self.assertEqual(code,200);self.assertTrue(r['result']['workspace_exists'])
    def test_invalid_key(self): self.assertEqual(401,self.request(bad_mac=True)[0])
    def test_stale_request(self): self.assertEqual('STALE_TIMESTAMP',self.request(age=-1000)[1]['reason'])
    def test_replay_persists_after_restart(self):
        nonce=secrets.token_hex(12)
        self.assertEqual(200,self.request(nonce=nonce)[0])
        self.assertEqual('REPLAY',self.request(nonce=nonce)[1]['reason'])
        b2=Bridge(self.b.state_dir,self.b.workspace,'ab'*32)
        self.assertEqual('REPLAY',b2.authenticate('POST','/v1/status',str(int(time.time())),nonce,
                      b2.sig(f'POST\n/v1/status\n{int(time.time())}\n{nonce}\n{hashlib.sha256(compact({})).hexdigest()}'),compact({})))
    def test_files_within_workspace(self):
        self.assertEqual([],self.request('/v1/files')[1]['result']['items'])
        status,r=self.request('/v1/write',{'path':'a.txt','content':'hello','approved':True})
        self.assertEqual(200,status)
        self.assertEqual('hello',self.request('/v1/read',{'path':'a.txt'})[1]['result']['content'])
        self.assertEqual(1,len(self.request('/v1/files')[1]['result']['items']))
    def test_write_requires_explicit_approval(self):
        self.assertEqual('APPROVAL_REQUIRED',self.request('/v1/write',{'path':'a.txt','content':'oops'})[1]['reason'])
        self.assertFalse((self.b.workspace/'a.txt').exists())
    def test_traversal_blocked(self):
        self.assertEqual('OUTSIDE_WORKSPACE',self.request('/v1/write',{'path':'../pwn.txt','content':'X','approved':True})[1]['reason'])
    def test_no_arbitrary_shell(self):
        self.assertEqual(404,self.request('/v1/shell',{'command':'whoami'})[0])
    def test_backup(self):
        self.request('/v1/write',{'path':'x.txt','content':'before','approved':True})
        result=self.request('/v1/write',{'path':'x.txt','content':'after','approved':True})[1]['result']
        self.assertTrue((self.b.state_dir/result['backup_name']).exists())
        self.assertEqual('before',(self.b.state_dir/result['backup_name']).read_text())
    def test_audit(self):
        self.request()
        self.assertTrue(self.request('/v1/audit')[1]['result']['events'])
    def test_bad_size_limit(self):
        self.assertEqual('CONTENT_INVALID_OR_TOO_LARGE',self.request('/v1/write',{'path':'x.txt','content':'x'*65537,'approved':True})[1]['reason'])
    def test_symlink_escape(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir()
        try: (self.b.workspace/'link').symlink_to(outside,target_is_directory=True)
        except OSError: self.skipTest('symlink unavailable')
        self.assertEqual('OUTSIDE_WORKSPACE',self.request('/v1/write',{'path':'link/oops.txt','content':'X','approved':True})[1]['reason'])
    def test_public_health_without_pairing(self):
        con=http.client.HTTPConnection('127.0.0.1',self.http.server_port)
        con.request('GET','/health');res=con.getresponse();data=json.loads(res.read());con.close()
        self.assertEqual(200,res.status);self.assertTrue(data['ok'])

if __name__=='__main__':unittest.main()