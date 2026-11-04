#!/usr/bin/env python3
"""KIN MOTO: inspect a supplied GLB offline; no API, no downloader, no licenses guessed.

Run: python tools/audit_glb.py path/to/asset.glb --out docs/ASSET_AUDIT.json
The validator is intentionally conservative. Technical checks do NOT confer copyright permission.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys
from pathlib import Path

MAX_FILE_BYTES=2_000_000
MAX_TRIANGLES=12_000
CHUNK_JSON=0x4e4f534a
CHUNK_BIN=0x004e4942

def inspect_glb(blob: bytes, filename: str = '<memory>') -> dict:
    result={"filename":filename,"bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest(),"format":"glb2",
            "technical_status":"REJECTED","legal_status":"UNVERIFIED","errors":[],"warnings":[]}
    fail=result["errors"].append
    if len(blob)<20 or blob[:4]!=b'glTF':
        fail('Not a glTF 2.0 binary file');return result
    magic,version,declared=struct.unpack_from('<4sII',blob,0)
    if version!=2 or declared!=len(blob):
        fail('GLB version/length mismatch');return result
    pos=12;chunks=[]
    while pos<len(blob):
        if pos+8>len(blob):fail('Incomplete GLB chunk header');return result
        size,kind=struct.unpack_from('<II',blob,pos);pos+=8
        if pos+size>len(blob):fail('GLB chunk exceeds file length');return result
        chunks.append((kind,blob[pos:pos+size]));pos+=size
    if not chunks or chunks[0][0]!=CHUNK_JSON:
        fail('First GLB chunk must contain JSON');return result
    try:doc=json.loads(chunks[0][1].rstrip(b'\0 \n\r\t').decode('utf-8'))
    except (ValueError,UnicodeDecodeError) as ex:fail('Invalid glTF JSON: '+str(ex));return result
    if doc.get('asset',{}).get('version')!='2.0':
        fail('Invalid glTF asset version');return result
    binary=next((c for k,c in chunks[1:] if k==CHUNK_BIN),b'')
    external=[]
    for b in doc.get('buffers',[]):
        if b.get('uri'):external.append('buffer:'+str(b['uri'])[:60])
        if not b.get('uri') and b.get('byteLength',0)>len(binary):fail('Embedded buffer length exceeds BIN chunk')
    for image in doc.get('images',[]):
        if image.get('uri'):external.append('image:'+str(image['uri'])[:60])
    if external:fail('External URLs or separate files forbidden for offline-first import: '+', '.join(external))
    triangles=0;verts=0;meshes=[];textured=False
    acc=doc.get('accessors',[])
    for mesh in doc.get('meshes',[]):
        tc=0
        for prim in mesh.get('primitives',[]):
            if prim.get('mode',4)!=4:
                result['warnings'].append('Primitive is not TRIANGLES; converter needed')
                continue
            idx=prim.get('indices');attrib=prim.get('attributes',{}).get('POSITION');
            if attrib is None or not isinstance(attrib,int) or attrib>=len(acc):
                fail('Missing/invalid POSITION accessor');continue
            verts+=acc[attrib].get('count',0)
            count=acc[idx].get('count',0) if isinstance(idx,int) and 0<=idx<len(acc) else acc[attrib].get('count',0)
            tc+=count//3;triangles+=count//3
            mi=prim.get('material')
            if mi is not None and 0<=mi<len(doc.get('materials',[])):
                m=doc['materials'][mi];pbr=m.get('pbrMetallicRoughness',{})
                if any(k in pbr for k in ('baseColorTexture','metallicRoughnessTexture')) or any(k in m for k in ('normalTexture','occlusionTexture','emissiveTexture')):textured=True
        meshes.append({'name':mesh.get('name','unnamed'), 'triangles':tc})
    if not meshes or triangles==0:fail('No renderable triangle mesh')
    if triangles>MAX_TRIANGLES:fail(f'Triangle budget exceeded: {triangles} > {MAX_TRIANGLES}')
    if len(blob)>MAX_FILE_BYTES:fail(f'File budget exceeded: {len(blob)} > {MAX_FILE_BYTES}')
    nodes=[str(n.get('name','')) for n in doc.get('nodes',[])]
    front=[n for n in nodes if any(w in n.lower() for w in ('front_wheel','wheel_front','frontwheel'))]
    rear=[n for n in nodes if any(w in n.lower() for w in ('rear_wheel','wheel_rear','rearwheel'))]
    anim=[a.get('name',f'clip_{i}') for i,a in enumerate(doc.get('animations',[]))]
    result.update({"triangles":triangles,"vertex_accessors_total":verts,"meshes":meshes,
                   "node_count":len(nodes),"front_wheel_nodes":front,"rear_wheel_nodes":rear,
                   "animations":anim,"materials":len(doc.get('materials',[])),"embedded_textures":len(doc.get('images',[])),
                   "requires_textured_gltf_renderer":textured,"extensions_used":doc.get('extensionsUsed',[]),
                   "technical_status":"PASS_TECHNICAL" if not result['errors'] else 'REJECTED'})
    if not front or not rear:result['warnings'].append('Named wheel nodes absent: separate wheel rotation needs preparation')
    if textured:result['warnings'].append('Current custom WebGL renderer cannot preserve GLB textures; do not silently flatten a detailed model')
    if not anim:result['warnings'].append('No animation clips, extra wheel/steering rig needed')
    result['warnings'].append('Source-page license assertion is NOT legal approval of this downloaded file')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('asset',type=Path);parser.add_argument('--out',type=Path)
    parser.add_argument('--sha256',help='expected checksum from independently recorded inventory')
    args=parser.parse_args();body=args.asset.read_bytes();report=inspect_glb(body,str(args.asset))
    if args.sha256 and report['sha256']!=args.sha256.lower():
        report['errors'].append('SHA256 mismatch against approved inventory');report['technical_status']='REJECTED'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    else:print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['technical_status']=='PASS_TECHNICAL' else 2
if __name__=='__main__':sys.exit(main())
