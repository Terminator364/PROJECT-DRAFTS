"""JDK->Windows-agent interoperability test; runs local HTTP only."""
import pathlib
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'windows'))
from bridge_agent import Bridge, handler_factory

class JavaClientProtocolTests(unittest.TestCase):
    def test_real_java_client_can_authenticate_against_python_server(self):
        if not shutil.which('javac') or not shutil.which('java'):
            self.skipTest('Java JDK unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)
            key='ab'*32
            agent=Bridge(path/'state',path/'sandbox',key)
            server=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(agent))
            thread=threading.Thread(target=lambda: server.serve_forever(poll_interval=0.02),daemon=True);thread.start()
            try:
                subprocess.run(['javac','-encoding','UTF-8','-d',tmp,
                    str(ROOT/'android/app/src/main/java/com/blessing/rescuebridge/BridgeProtocol.java'),
                    str(ROOT/'tests/BridgeInteropCli.java')],check=True,capture_output=True,text=True,timeout=30)
                result=subprocess.run(['java','-cp',tmp,'BridgeInteropCli','127.0.0.1',str(server.server_port),key],
                    check=True,capture_output=True,text=True,timeout=15)
                self.assertIn('INTEROP_OK',result.stdout)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)
if __name__=='__main__':unittest.main()