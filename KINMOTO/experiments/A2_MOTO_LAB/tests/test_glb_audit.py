import unittest,struct,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_glb import inspect_glb

def make_glb(*,triangles=2,textured=False,external=False,animated=True):
    doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':36}],
         'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':36}],
         'accessors':[{'bufferView':0,'componentType':5126,'type':'VEC3','count':3}],
         'meshes':[{'name':'motorcycle','primitives':[{'attributes':{'POSITION':0},'mode':4} for _ in range(triangles)]}],
         'nodes':[{'name':'front_wheel'},{'name':'rear_wheel'}],
         'scenes':[{'nodes':[0,1]}], 'scene':0}
    if animated:doc['animations']=[{'name':'wheel-roll'}]
    if textured:
        doc['images']=[{'bufferView':0,'mimeType':'image/png'}]
        doc['materials']=[{'pbrMetallicRoughness':{'baseColorTexture':{'index':0}}}]
        for mesh in doc['meshes']:
            for p in mesh['primitives']:p['material']=0
    if external:doc['buffers'][0]['uri']='https://example.invalid/model.bin'
    js=json.dumps(doc,separators=(',',':')).encode('utf-8')
    js+=b' ' *(-len(js)%4)
    binary=b'\x00'*36
    return struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary

class GLBAudit(unittest.TestCase):
    def test_simple_glb_passes(self):
        s=inspect_glb(make_glb());self.assertEqual(s['technical_status'],'PASS_TECHNICAL');self.assertEqual(s['triangles'],2)
    def test_external_buffers_rejected(self):
        s=inspect_glb(make_glb(external=True));self.assertEqual(s['technical_status'],'REJECTED')
    def test_oversized_triangle_budget_rejected(self):
        s=inspect_glb(make_glb(triangles=12001));self.assertEqual(s['technical_status'],'REJECTED')
    def test_texture_dependency_is_reported_not_hidden(self):
        s=inspect_glb(make_glb(textured=True));self.assertTrue(s['requires_textured_gltf_renderer'])
    def test_corrupt_length_rejected(self):
        x=make_glb()[:-4];self.assertEqual(inspect_glb(x)['technical_status'],'REJECTED')
    def test_named_wheels_and_animations_recorded(self):
        s=inspect_glb(make_glb());self.assertEqual(s['front_wheel_nodes'],['front_wheel']);self.assertEqual(s['rear_wheel_nodes'],['rear_wheel']);self.assertEqual(s['animations'],['wheel-roll'])
    def test_license_never_automatically_approved(self):
        s=inspect_glb(make_glb());self.assertEqual(s['legal_status'],'UNVERIFIED')
if __name__=='__main__':unittest.main()
