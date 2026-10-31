"""Minimal loopback HTTP control plane. No Internet listener or shell execution."""
import argparse
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .core import Queue,Worker

class Handler(BaseHTTPRequestHandler):
    server_version='OriginNode/0.2'
    def log_message(self,fmt,*args):return
    def reply(self,status,obj):
        payload=json.dumps(obj,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers();self.wfile.write(payload)
    def authorized(self):
        token=self.headers.get('Authorization','')
        if not secrets.compare_digest(token,'Bearer '+self.server.token):
            self.reply(401,{'error':'unauthorized'});return False
        return True
    def do_GET(self):
        if not self.authorized():return
        if self.path=='/health':return self.reply(200,{'status':'ok','queue':self.server.queue.stats(),'integrity':self.server.queue.check()})
        if self.path.startswith('/jobs/') and self.path[6:].isdigit():
            value=self.server.queue.get(int(self.path[6:]))
            return self.reply(200 if value else 404,value if value else {'error':'not_found'})
        self.reply(404,{'error':'not_found'})
    def do_POST(self):
        if not self.authorized():return
        if self.path!='/jobs':return self.reply(404,{'error':'not_found'})
        length=self.headers.get('Content-Length','')
        if not length.isdigit() or int(length)>8192:
            return self.reply(413,{'error':'invalid or oversized request'})
        try:
            data=json.loads(self.rfile.read(int(length)))
            job=self.server.queue.submit(data['kind'],data['payload'],data['idempotency_key'])
            self.reply(202,{'id':job['id'],'state':job['state']})
        except (KeyError,ValueError,TypeError,OverflowError,json.JSONDecodeError) as exc:
            self.reply(400,{'error':str(exc)[:180]})
    def do_DELETE(self):self.reply(405,{'error':'method_disabled'})

class AppServer(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=True
    def __init__(self,address,queue,token):
        super().__init__(address,Handler)
        self.queue=queue;self.token=token

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8789)
    parser.add_argument('--db',default=str(Path.home()/'.origin-node'/'jobs.sqlite3'))
    parser.add_argument('--token-file',default=str(Path.home()/'.origin-node'/'token'))
    args=parser.parse_args(argv)
    if not 1024<=args.port<=65535:parser.error('port must be between 1024 and 65535')
    tf=Path(args.token_file);tf.parent.mkdir(parents=True,exist_ok=True)
    if not tf.exists():
        fd=os.open(str(tf),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as out:out.write(secrets.token_urlsafe(32))
    os.chmod(tf,0o600)
    token=tf.read_text().strip()
    if len(token)<32:raise RuntimeError('weak authentication token')
    queue=Queue(args.db);queue.recover()
    stop=threading.Event();worker=Worker(queue,stop);worker.start()
    httpd=AppServer(('127.0.0.1',args.port),queue,token)
    print(f'ORIGIN localhost HTTP ready at 127.0.0.1:{args.port}',flush=True)
    try:httpd.serve_forever(poll_interval=.25)
    except KeyboardInterrupt:pass
    finally:
        httpd.server_close();stop.set();worker.join(4);queue.close()
if __name__=='__main__':main()
