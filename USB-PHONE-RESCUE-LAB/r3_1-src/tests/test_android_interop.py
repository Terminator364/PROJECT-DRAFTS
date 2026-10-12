"""Test Android Java *syntax* and pure-JDK protocol without Android SDK.
These tests do NOT claim an APK was compiled or Android device tested.
"""
import hashlib
import hmac
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'windows'))
from bridge_agent import Bridge

class JavaInteropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=tempfile.TemporaryDirectory(prefix='bcp-interop-')
        cls.out=Path(cls.root.name)
        src=ROOT/'android/app/src/main/java/com/blessing/rescuebridge/BridgeProtocol.java'
        helpers=[ROOT/'tests/java/ProtocolProbe.java',ROOT/'tests/java/ParseAndroidJava.java']
        subprocess.run(['javac','-encoding','UTF-8','-d',str(cls.out),str(src),*(str(p) for p in helpers)],check=True,timeout=25)
    @classmethod
    def tearDownClass(cls):cls.root.cleanup()
    def test_request_hmac_matches_python_agent(self):
        key='cafe'*16;ts=str(int(time.time()));nonce='11111111222222223333333344444444'
        body='{"content":"café","approved":true}';b=body.encode()
        got=subprocess.check_output(['java','-cp',str(self.out),'ProtocolProbe',key,'/v1/write',ts,nonce,body],text=True,timeout=15).splitlines()
        digest=hashlib.sha256(b).hexdigest()
        req=hmac.new(key.encode(),f'POST\n/v1/write\n{ts}\n{nonce}\n{digest}'.encode(),'sha256').hexdigest()
        resp=hmac.new(key.encode(),f'{nonce}\n200\n{digest}'.encode(),'sha256').hexdigest()
        self.assertEqual([req,resp,digest,'true','false','"hello\\n\\"x\\""'],got)
        with tempfile.TemporaryDirectory() as temp:
            agent=Bridge(Path(temp)/'state',Path(temp)/'work',key)
            self.assertIsNone(agent.authenticate('POST','/v1/write',ts,nonce,got[0],b))
            self.assertEqual('REPLAY',agent.authenticate('POST','/v1/write',ts,nonce,got[0],b))
    def test_android_sources_parse_with_jdk(self):
        sources=list((ROOT/'android/app/src/main/java/com/blessing/rescuebridge').glob('*.java'))
        self.assertEqual(7,len(sources))
        r=subprocess.run(['java','-cp',str(self.out),'ParseAndroidJava',*(str(p) for p in sources)],capture_output=True,text=True,timeout=20)
        self.assertEqual(0,r.returncode,r.stderr)
        self.assertEqual(len(sources),r.stdout.count('PARSED'))
    def test_android_activity_namespace_matches_manifest(self):
        gradle=(ROOT/'android/app/build.gradle').read_text()
        java=(ROOT/'android/app/src/main/java/com/blessing/rescuebridge/MainActivity.java').read_text()
        manifest=(ROOT/'android/app/src/main/AndroidManifest.xml').read_text()
        self.assertIn("namespace 'com.blessing.rescuebridge'",gradle)
        self.assertIn("applicationId 'com.blessing.rescuebridge'",gradle)
        self.assertIn('package com.blessing.rescuebridge;',java)
        self.assertIn('android:name=".MainActivity"',manifest)
    def test_bridge_client_jdk_compiles_with_json_stub(self):
        pkg=self.out/'org/json';pkg.mkdir(parents=True,exist_ok=True)
        stub=pkg/'JSONObject.java'
        stub.write_text('package org.json; public class JSONObject {public JSONObject(){} public JSONObject(String s){} public String toString(){return "{}";}}')
        client=ROOT/'android/app/src/main/java/com/blessing/rescuebridge/BridgeClient.java'
        r=subprocess.run(['javac','-d',str(self.out),'-cp',str(self.out),str(stub),str(client)],capture_output=True,text=True,timeout=20)
        self.assertEqual(0,r.returncode,r.stderr)
if __name__=='__main__':unittest.main()