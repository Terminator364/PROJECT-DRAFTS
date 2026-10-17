"""Adversarial transport tests against a REAL loopback HTTP server (not Windows hardware)."""
from pathlib import Path
import sys,tempfile,threading,http.client,hashlib,hmac,time,json,secrets,unittest
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'windows'))
from bridge_agent import Bridge,handler_factory,compact

KEY='a'*64
class BoundedHTTPServer(ThreadingHTTPServer):
    request_queue_size = 32
    daemon_threads = False
    block_on_close = True

class FaultCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.agent=Bridge(root/'state',root/'workspace',KEY)
        self.server=BoundedHTTPServer(('127.0.0.1',0),handler_factory(self.agent))
        self.worker=threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.02),daemon=True);self.worker.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.worker.join(2);self.tmp.cleanup()
    def req(self,path='/v1/status',payload=None,nonce=None,key=KEY,ts=None,body=None):
        raw=body if body is not None else compact(payload or {})
        nonce=nonce or secrets.token_hex(16);ts=ts or str(int(time.time()))
        content=f'POST\n{path}\n{ts}\n{nonce}\n{hashlib.sha256(raw).hexdigest()}'.encode()
        sig=hmac.new(key.encode(),content,'sha256').hexdigest()
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=12)
        try:
            conn.request('POST',path,raw,headers={'X-Bridge-Time':ts,'X-Bridge-Nonce':nonce,'X-Bridge-Signature':sig})
            r=conn.getresponse();data=r.read();v=json.loads(data);headers=dict(r.getheaders());status=r.status
        finally:
            conn.close()
        expected=hmac.new(KEY.encode(),f'{nonce}\n{status}\n{hashlib.sha256(data).hexdigest()}'.encode(),'sha256').hexdigest()
        self.assertEqual(expected,headers['X-Bridge-Signature'])
        return status,v
    def test_50_signed_status_roundtrips(self):
        for i in range(50):
            code,v=self.req();self.assertEqual(200,code,v);self.assertEqual('BCP_USB_RESCUE_R1',v['result']['agent'])
    def test_20_unicode_roundtrips_and_backups(self):
        for i in range(20):
            msg='Épreuve-'+str(i)+' ; 🩺 🛠 ✅ ✓'
            code,v=self.req('/v1/write',{'path':'unicode.txt','content':msg,'approved':True});self.assertEqual(200,code,v)
            code,v=self.req('/v1/read',{'path':'unicode.txt'});self.assertEqual(200,code,v);self.assertEqual(msg,v['result']['content'])
    def test_auth_failure_storm_never_runs_action(self):
        for i in range(20):
            code,v=self.req('/v1/write',{'path':'bad.txt','content':str(i),'approved':True},key='bad'*22)
            self.assertEqual(401,code,v)
        self.assertFalse((self.agent.workspace/'bad.txt').exists())
    def test_spoofed_command_path_cannot_be_called(self):
        for path in ('/v1/shell','/v1/run','/v1/terminal','/v1/write/../../danger'):
            code,v=self.req(path);self.assertEqual(404,code)
    def test_concurrent_signed_clients(self):
        errors=[]
        def worker():
            for _ in range(5):
                try:
                    if self.req()[0]!=200: errors.append('not 200')
                except Exception as e: errors.append(str(e))
        ts=[threading.Thread(target=worker) for _ in range(4)]
        for t in ts:t.start()
        for t in ts:t.join()
        self.assertFalse(errors,errors)

if __name__=='__main__':unittest.main()