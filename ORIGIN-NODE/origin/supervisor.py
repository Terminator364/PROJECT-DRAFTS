"""Termux-compatible crash-safe supervisor using fcntl.flock, not mkdir locks."""
import argparse
import fcntl
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

class AlreadyRunning(RuntimeError):pass

def take_lock(path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_CREAT|os.O_RDWR,0o600)
    try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd);raise AlreadyRunning('supervisor already active')
    os.ftruncate(fd,0)
    os.write(fd,str(os.getpid()).encode())
    return fd

def rotate_log(path,max_bytes=2*1024*1024):
    p=Path(path)
    if p.is_file() and p.stat().st_size>max_bytes:
        old=p.with_suffix(p.suffix+'.1')
        p.replace(old)

def serve_forever(port=8789,root=None,delay=10):
    base=Path(root) if root else Path.home()/'.origin-node'
    base.mkdir(parents=True,exist_ok=True)
    lock=take_lock(base/'supervisor.lock')
    stopping=False
    child=None
    def on_signal(signum,frame):
        nonlocal stopping
        stopping=True
        if child is not None and child.poll() is None:
            child.terminate()
    old_term=signal.signal(signal.SIGTERM,on_signal)
    old_int=signal.signal(signal.SIGINT,on_signal)
    try:
        while not stopping:
            logfile=base/'supervisor.log'
            rotate_log(logfile)
            with open(logfile,'a',encoding='utf-8') as stream:
                argv=[sys.executable,'-m','origin.server','--port',str(port),
                      '--db',str(base/'jobs.sqlite3'),'--token-file',str(base/'token')]
                child=subprocess.Popen(argv,stdout=stream,stderr=subprocess.STDOUT)
                while not stopping and child.poll() is None:
                    time.sleep(.2)
                if stopping:
                    if child.poll() is None:
                        child.terminate()
                        try:child.wait(timeout=4)
                        except subprocess.TimeoutExpired:child.kill();child.wait(timeout=4)
                    break
                stream.write(f'RESTART child exit code={child.returncode}\n');stream.flush()
            for _ in range(max(1,int(delay*5))):
                if stopping:break
                time.sleep(.2)
    finally:
        signal.signal(signal.SIGTERM,old_term)
        signal.signal(signal.SIGINT,old_int)
        os.close(lock)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--port',type=int,default=8789)
    ap.add_argument('--root')
    ap.add_argument('--delay',type=float,default=10)
    args=ap.parse_args()
    if not 1024<=args.port<=65535:ap.error('invalid port')
    if not 1<=args.delay<=300:ap.error('restart delay must be 1..300 seconds')
    try:serve_forever(port=args.port,root=args.root,delay=args.delay)
    except AlreadyRunning as exc:print(str(exc),file=sys.stderr);sys.exit(3)
if __name__=='__main__':main()
