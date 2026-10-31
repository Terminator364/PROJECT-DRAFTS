import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from origin.core import Queue, Worker
from origin.server import AppServer

class APITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.q=Queue(Path(self.temp.name)/'jobs.db')
        self.stop=threading.Event();self.worker=Worker(self.q,self.stop);self.worker.start()
        self.app=AppServer(('127.0.0.1',0),self.q,'A'*40)
        self.port=self.app.server_address[1]
        self.thread=threading.Thread(target=self.app.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.app.shutdown();self.app.server_close();self.stop.set();self.worker.join(2);self.thread.join(2);self.q.close();self.temp.cleanup()
    def send(self,method,path,data=None,auth=True):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        headers={'Content-Type':'application/json'}
        if auth:headers['Authorization']='Bearer '+'A'*40
        body=json.dumps(data) if data is not None else None
        conn.request(method,path,body=body,headers=headers)
        r=conn.getresponse();body=r.read();conn.close()
        return r.status,json.loads(body)
    def job(self):return {'kind':'upper','payload':'essai','idempotency_key':'http-test-00001'}
    def test_unauthorized(self):
        s,data=self.send('GET','/health',auth=False);self.assertEqual(s,401)
    def test_health(self):
        s,data=self.send('GET','/health');self.assertEqual(s,200);self.assertEqual(data['integrity'],'ok')
    def test_create_and_get(self):
        s,data=self.send('POST','/jobs',self.job());self.assertEqual(s,202);i=data['id']
        for _ in range(100):
            s,status=self.send('GET',f'/jobs/{i}')
            if status['state']=='done':break
            time.sleep(.01)
        self.assertEqual(status['result'],'ESSAI')
    def test_duplicate(self):
        a=self.send('POST','/jobs',self.job())[1];b=self.send('POST','/jobs',self.job())[1]
        self.assertEqual(a['id'],b['id'])
    def test_reject_arbitrary_commands(self):
        j=self.job();j['kind']='shell';s,_=self.send('POST','/jobs',j)
        self.assertEqual(s,400)
    def test_idempotency_conflict(self):
        self.send('POST','/jobs',self.job())
        j=self.job();j['payload']='other';s,body=self.send('POST','/jobs',j)
        self.assertEqual(s,400);self.assertIn('conflict',body['error'])
    def test_missing_route(self):
        self.assertEqual(self.send('GET','/admin')[0],404)
    def test_get_unknown(self):
        self.assertEqual(self.send('GET','/jobs/999999')[0],404)
    def test_delete_disabled(self):
        self.assertEqual(self.send('DELETE','/jobs/1')[0],405)
if __name__=='__main__':unittest.main()
