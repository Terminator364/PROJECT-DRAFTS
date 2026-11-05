"""Deterministic, bounded malformed-GLB regression tests; no network or external tools."""
import copy
import json
import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_glb import inspect_glb
from test_glb_audit import make_glb


def encode_glb(doc):
    source = json.dumps(doc, separators=(',', ':')).encode('utf-8')
    source += b' ' * (-len(source) % 4)
    binary = b'\x00' * 36
    total = 12 + 8 + len(source) + 8 + len(binary)
    return (struct.pack('<4sII', b'glTF', 2, total)
            + struct.pack('<II', len(source), 0x4e4f534a) + source
            + struct.pack('<II', len(binary), 0x004e4942) + binary)


class MalformedGLBFuzzQA(unittest.TestCase):
    def test_1500_random_binary_corruptions_do_not_crash_parser(self):
        rng = random.Random(20261105)
        original = make_glb()
        for case in range(1500):
            payload = bytearray(original)
            for _ in range(rng.randint(1, 9)):
                offset = rng.randrange(len(payload))
                payload[offset] = rng.randrange(256)
            if rng.random() < 0.2:
                payload = payload[:rng.randrange(len(payload))]
            with self.subTest(case=case):
                result = inspect_glb(bytes(payload))
                self.assertIn(result['technical_status'], ('REJECTED', 'PASS_TECHNICAL'))
                self.assertEqual(result['legal_status'], 'UNVERIFIED')

    def test_1500_malformed_json_structures_do_not_crash_parser(self):
        rng = random.Random(20261105)
        original = make_glb(textured=True)
        length = struct.unpack_from('<I', original, 12)[0]
        base = json.loads(original[20:20+length].decode('utf-8').rstrip(' '))
        fields = ('asset', 'buffers', 'bufferViews', 'accessors', 'meshes', 'nodes',
                  'materials', 'images', 'animations', 'extensionsUsed', 'scenes', 'scene')
        candidates = (None, False, True, 0, -1, 1, 1_000_000, 1.0, -3.4,
                      'oops', '', [], {}, [None], [1], [{}], {'uri': None})
        for case in range(1500):
            doc = copy.deepcopy(base)
            for _ in range(rng.randint(1, 4)):
                key = rng.choice(fields)
                value = copy.deepcopy(rng.choice(candidates))
                if rng.random() < 0.65:
                    doc[key] = value
                elif isinstance(doc.get(key), list) and doc[key]:
                    doc[key][rng.randrange(len(doc[key]))] = value
                else:
                    doc[key] = value
            with self.subTest(case=case):
                result = inspect_glb(encode_glb(doc))
                self.assertIn(result['technical_status'], ('REJECTED', 'PASS_TECHNICAL'))
                self.assertEqual(result['legal_status'], 'UNVERIFIED')

if __name__ == '__main__':
    unittest.main()
