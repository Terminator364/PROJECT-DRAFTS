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

def mutate_glb(change):
    body=make_glb()
    length,kind=struct.unpack_from('<II',body,12)
    doc=json.loads(body[20:20+length].decode('utf-8').rstrip(' '))
    change(doc)
    js=json.dumps(doc,separators=(',',':')).encode('utf-8')
    js+=b' '*(-len(js)%4)
    binary=b'\x00'*36
    return (struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))
            +struct.pack('<II',len(js),0x4e4f534a)+js
            +struct.pack('<II',len(binary),0x004e4942)+binary)

class GLBMalformationQA(unittest.TestCase):
    def test_negative_position_accessor_rejected(self):
        b=mutate_glb(lambda d:d['meshes'][0]['primitives'][0]['attributes'].update(POSITION=-1))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_negative_index_accessor_rejected(self):
        b=mutate_glb(lambda d:d['meshes'][0]['primitives'][0].update(indices=-1))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_binary_view_overrun_rejected(self):
        b=mutate_glb(lambda d:d['bufferViews'][0].update(byteOffset=35,byteLength=36))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_negative_vertex_count_rejected(self):
        b=mutate_glb(lambda d:d['accessors'][0].update(count=-10))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_null_meshes_array_rejected_without_parser_exception(self):
        b=mutate_glb(lambda d:d.update(meshes=None))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_invalid_mesh_primitive_structure_rejected(self):
        b=mutate_glb(lambda d:d['meshes'][0].update(primitives=None))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_invalid_primitive_attributes_rejected(self):
        b=mutate_glb(lambda d:d['meshes'][0]['primitives'][0].update(attributes=None))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_invalid_images_array_rejected(self):
        b=mutate_glb(lambda d:d.update(images=[None]))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_invalid_animations_array_rejected(self):
        b=mutate_glb(lambda d:d.update(animations='not-a-list'))
        self.assertEqual(inspect_glb(b)['technical_status'],'REJECTED')
    def test_oversized_binary_rejected_before_json_parse(self):
        b=b'glTF'+b'\x00'*2_000_100
        s=inspect_glb(b)
        self.assertEqual(s['technical_status'],'REJECTED')
        self.assertTrue(any('File budget exceeded' in e for e in s['errors']))


class GLBBinPaddingQA(unittest.TestCase):
    def test_surplus_binary_chunk_over_3_bytes_is_rejected(self):
        blob=bytearray(make_glb())
        json_length=struct.unpack_from('<I',blob,12)[0]
        bin_header=20+json_length
        bin_length=struct.unpack_from('<I',blob,bin_header)[0]
        assert bin_length==36
        struct.pack_into('<I',blob,bin_header,40)
        blob.extend(b'\x00'*4)
        struct.pack_into('<I',blob,8,len(blob))
        self.assertEqual(inspect_glb(bytes(blob))['technical_status'],'REJECTED')

    def test_3_bytes_zero_bin_padding_allowed(self):
        blob=bytearray(make_glb())
        json_length=struct.unpack_from('<I',blob,12)[0]
        doc=json.loads(blob[20:20+json_length].decode('utf-8').rstrip(' '))
        doc['buffers'][0]['byteLength']=37
        js=json.dumps(doc,separators=(',',':')).encode('utf-8')
        js+=b' '*(-len(js)%4)
        binary=b'\x00'*40
        packed=(struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))
                +struct.pack('<II',len(js),0x4e4f534a)+js
                +struct.pack('<II',len(binary),0x004e4942)+binary)
        self.assertEqual(inspect_glb(packed)['technical_status'],'PASS_TECHNICAL')

    def test_nonzero_padding_bytes_are_rejected(self):
        blob=bytearray(make_glb())
        json_length=struct.unpack_from('<I',blob,12)[0]
        doc=json.loads(blob[20:20+json_length].decode('utf-8').rstrip(' '))
        doc['buffers'][0]['byteLength']=37
        js=json.dumps(doc,separators=(',',':')).encode('utf-8')
        js+=b' '*(-len(js)%4)
        binary=b'\x00'*37+b'abc'
        packed=(struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))
                +struct.pack('<II',len(js),0x4e4f534a)+js
                +struct.pack('<II',len(binary),0x004e4942)+binary)
        self.assertEqual(inspect_glb(packed)['technical_status'],'REJECTED')

if __name__=='__main__':unittest.main()
